"""Run experiments through subscription-authenticated agent CLIs.

Use this route when the target is the model inside the Codex or Claude Code
agent environment. Label that condition explicitly; it is not a bare model
endpoint. The CLI flattens message history into a role-marked prompt and does
not expose a sampling seed.

Use `local_provider` for work that needs local weights or activations. Use a
pinned API route when the claim requires a bare endpoint or controlled sampling.
All three providers implement the same `complete(messages)` contract.
"""
from __future__ import annotations

import json
import subprocess

CODEX_DEFAULT_MODEL = "gpt-5.6-luna"
CODEX_REASONING_EFFORT = "low"

HARNESS_WARNING = (
    "CLI harness condition: the model is wrapped in agent system instructions "
    "and the message list is flattened to one prompt"
)


def flatten(messages, system: str | None = None) -> str:
    """Role-marked transcript. The last user turn is the live question."""
    parts = []
    if system:
        parts.append(f"[instructions]\n{system}")
    for m in messages:
        parts.append(f"[{m['role']}]\n{m['content']}")
    return "\n\n".join(parts)


def _run(cmd, stdin_text: str, timeout_s: float) -> str:
    p = subprocess.run(cmd, input=stdin_text, capture_output=True, text=True,
                       timeout=timeout_s)
    if p.returncode != 0:
        raise RuntimeError(f"{cmd[0]} exited {p.returncode}: {p.stderr[-400:]}")
    return p.stdout


def _codex_command(model: str) -> list[str]:
    return [
        "codex", "exec", "--json", "--ephemeral", "--skip-git-repo-check",
        "--sandbox", "read-only", "--ignore-user-config", "--ignore-rules",
        "-c", "project_doc_max_bytes=0",
        "-c", f'model_reasoning_effort="{CODEX_REASONING_EFFORT}"',
        "--disable", "plugins", "--disable", "apps", "--disable", "hooks",
        "--disable", "memories", "--disable", "skill_search",
        "--disable", "multi_agent", "-m", model, "-",
    ]


def _codex_final(stdout: str) -> str:
    """Last agent message from `codex exec --json` JSONL.

    The payload is `{"type": "item.completed", "item": {"type":
    "agent_message", "text": ...}}`. The event type alone is not enough -- a
    tool call is also an `item.completed` -- so the inner item type is what
    selects the message. Older builds nest the same thing under `msg`.
    """
    text = ""
    for line in stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        for payload in (ev.get("item"), ev.get("msg"), ev):
            if not isinstance(payload, dict):
                continue
            if payload.get("type") not in ("agent_message", "assistant_message"):
                continue
            for key in ("text", "message", "content"):
                v = payload.get(key)
                if isinstance(v, str) and v.strip():
                    text = v
    if not text:
        raise RuntimeError(f"no agent_message in codex output: {stdout[-300:]!r}")
    return text


def _claude_final(stdout: str) -> str:
    """`claude -p --output-format json` returns one object with `result`.

    An error is reported in that same `result` field with `is_error: true`, so
    "Not logged in - Please run /login" arrives looking exactly like a model
    reply. Raise on it: a harness failure that reaches the analysis as a datum is
    worse than a crash.
    """
    try:
        d = json.loads(stdout)
    except json.JSONDecodeError:
        return stdout.strip()
    if isinstance(d, dict):
        if d.get("is_error"):
            raise RuntimeError(f"claude harness error: {d.get('result')!r}")
        for key in ("result", "text", "content"):
            v = d.get(key)
            if isinstance(v, str):
                return v
    return stdout.strip()


def load(harness: str, *, model: str | None = None, system: str | None = None,
         timeout_s: float = 180, log=print):
    """`harness` is 'codex' or 'claude'. Returns `(complete, close)`."""
    if harness not in ("codex", "claude"):
        raise ValueError(f"unknown harness {harness!r}")
    if harness == "codex":
        model = model or CODEX_DEFAULT_MODEL
        command = _codex_command(model)
        cli_version = subprocess.run(
            ["codex", "--version"], capture_output=True, text=True, check=True,
        ).stdout.strip()
    else:
        command = None
        cli_version = subprocess.run(
            ["claude", "--version"], capture_output=True, text=True, check=True,
        ).stdout.strip()
    log(f"[cli_provider] {HARNESS_WARNING}")
    state = {"n": 0, "failures": 0}

    def complete(messages):
        state["n"] += 1
        prompt = flatten(messages, system)
        if harness == "codex":
            # Isolation flags are not optional for a preference experiment. Without
            # them Codex reads ~/.codex/AGENTS.md, the project doc and the user's
            # rules into every trial, so the operator's standing instructions would
            # sit inside the context that the model's task choices are measured from.
            # `read-only` also stops a trial from touching the filesystem while
            # "doing the work".
            text = _codex_final(_run(command, prompt, timeout_s))
        else:
            # No --bare: it drops hooks and plugins, which would be welcome, but
            # it also never reads OAuth or the keychain, so every call comes back
            # "Not logged in". The harness scaffolding stays.
            cmd = ["claude", "-p", "--output-format", "json"]
            if model:
                cmd += ["--model", model]
            text = _claude_final(_run(cmd, prompt, timeout_s))
        if not text.strip():
            state["failures"] += 1
        return {"text": text, "model": model or "harness-default",
                "provider": f"{harness}-harness:{model or 'default'}",
                "agent_harness_condition": True}

    def close():
        log(f"[cli_provider] {state['n']} calls via {harness}, "
            f"{state['failures']} empty. {HARNESS_WARNING}")
        return dict(
            state,
            harness=harness,
            model=model or "harness-default",
            cli_version=cli_version,
            requested_reasoning_effort=(
                CODEX_REASONING_EFFORT if harness == "codex" else "low"),
            effective_reasoning_effort=(
                CODEX_REASONING_EFFORT if harness == "codex" else "unrecorded"),
            command=command,
            agent_harness_condition=True,
        )

    return complete, close


def demo():
    """Contract check without invoking either CLI."""
    msgs = [{"role": "user", "content": "pick one"},
            {"role": "assistant", "content": "Q"},
            {"role": "user", "content": "now do it"}]
    f = flatten(msgs, system="be brief")
    assert f.startswith("[instructions]\nbe brief"), f
    assert f.count("[user]") == 2 and "[assistant]" in f

    assert _claude_final('{"result": "ANSWER: 0.4"}') == "ANSWER: 0.4"
    assert _claude_final("not json") == "not json"
    # A harness error arrives in the same field a real answer would.
    try:
        _claude_final('{"is_error": true, "result": "Not logged in"}')
    except RuntimeError:
        pass
    else:
        raise AssertionError("harness error was returned as a model reply")
    jsonl = ('{"type": "thread.started", "thread_id": "x"}\n'
             '{"type": "item.completed", "item": {"type": "agent_message", '
             '"text": "first"}}\n'
             'noise\n'
             '{"type": "item.completed", "item": {"type": "command_execution", '
             '"text": "ls"}}\n'
             '{"type": "item.completed", "item": {"type": "agent_message", '
             '"text": "ANSWER: Q"}}\n')
    # The LAST agent message is the answer, and a tool call is also an
    # item.completed -- selecting on the event type alone returns "ls".
    assert _codex_final(jsonl) == "ANSWER: Q"
    cmd = _codex_command(CODEX_DEFAULT_MODEL)
    assert cmd[-3:] == ["-m", CODEX_DEFAULT_MODEL, "-"]
    assert f'model_reasoning_effort="{CODEX_REASONING_EFFORT}"' in cmd
    try:
        _codex_final('{"type": "turn.completed"}')
    except RuntimeError:
        pass
    else:
        raise AssertionError("codex output with no agent message was accepted")

    for bad in ("gpt", "anthropic"):
        try:
            load(bad)
        except ValueError:
            continue
        raise AssertionError(f"accepted harness {bad!r}")
    print("ok")


if __name__ == "__main__":
    demo()
