#!/usr/bin/env python3
"""Build the submission report from checked-in result summaries."""
from __future__ import annotations

import json
from pathlib import Path

from reportlab.graphics.shapes import Circle, Drawing, Line, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
PRIMARY = ROOT / "parallel_frontier/20_preference_foresight/results/ranking_v3/summary.json"
QWEN = ROOT / "parallel_frontier/20_preference_foresight/results/local_qwen4b_v1/summary.json"
SITUATED = ROOT / "parallel_frontier/16_self_prediction_behavioral/results/situated_sys_v1/summary.json"
SIT_QWEN = ROOT / "parallel_frontier/16_self_prediction_behavioral/results/situated_qwen_v1/summary.json"
CTXFC = ROOT / "parallel_frontier/16_self_prediction_behavioral/results/context_forecast_v1/summary.json"
NOANCHOR = ROOT / "parallel_frontier/16_self_prediction_behavioral/results/situated_sys_noanchor_v1/summary.json"
INTENT = ROOT / "parallel_frontier/16_self_prediction_behavioral/results/intent_matched_v1/summary.json"
PROSP_NA = ROOT / "parallel_frontier/16_self_prediction_behavioral/results/prospective_noanchor_v1/reanalysis_current.json"
FREQ = ROOT / "parallel_frontier/16_self_prediction_behavioral/results/frequency_v1/reanalysis_current.json"
NA_FREQ = ROOT / "parallel_frontier/16_self_prediction_behavioral/results/noanchor_frequency_v1/summary.json"
REPEAT = ROOT / "parallel_frontier/16_self_prediction_behavioral/results/repeat_target_v1/summary.json"
SIT_REPEAT = ROOT / "parallel_frontier/16_self_prediction_behavioral/results/situated_repeat_v1/summary.json"
UNREL = ROOT / "parallel_frontier/16_self_prediction_behavioral/results/unrelated_history_v1/summary.json"
CTX_LUNA = ROOT / "parallel_frontier/18_preference_path_dependence/results/ctx_scaled_v1/summary.json"
CTX_QWEN = ROOT / "parallel_frontier/18_preference_path_dependence/results/ctx_local_qwen_v1/summary.json"
VERIFY = ROOT / "parallel_frontier/20_preference_foresight/results/ranking_v3/verification.json"
OUT = ROOT / "output/pdf/digital_minds_report.pdf"

NAVY = colors.HexColor("#17324D")
TEAL = colors.HexColor("#087E8B")
ORANGE = colors.HexColor("#E8743B")
INK = colors.HexColor("#1E2933")
MUTED = colors.HexColor("#5F6B76")
PALE = colors.HexColor("#EEF5F7")
RULE = colors.HexColor("#D7E0E5")


def read_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing result: {path}")
    return json.loads(path.read_text())


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=27, leading=31, textColor=NAVY, spaceAfter=10,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle", parent=base["Normal"], fontName="Helvetica",
            fontSize=13, leading=18, textColor=MUTED, spaceAfter=18,
        ),
        "h1": ParagraphStyle(
            "H1", parent=base["Heading1"], fontName="Helvetica-Bold",
            fontSize=18, leading=22, textColor=NAVY, spaceBefore=4, spaceAfter=9,
        ),
        "h2": ParagraphStyle(
            "H2", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=12, leading=15, textColor=TEAL, spaceBefore=8, spaceAfter=5,
        ),
        "body": ParagraphStyle(
            "Body", parent=base["BodyText"], fontName="Helvetica",
            fontSize=9.4, leading=13.2, textColor=INK, spaceAfter=7,
        ),
        "small": ParagraphStyle(
            "Small", parent=base["BodyText"], fontName="Helvetica",
            fontSize=7.8, leading=10.2, textColor=MUTED, spaceAfter=4,
        ),
        "metric": ParagraphStyle(
            "Metric", parent=base["BodyText"], fontName="Helvetica-Bold",
            fontSize=17, leading=20, textColor=NAVY, alignment=TA_CENTER,
        ),
        "metric_label": ParagraphStyle(
            "MetricLabel", parent=base["BodyText"], fontName="Helvetica",
            fontSize=7.8, leading=10, textColor=MUTED, alignment=TA_CENTER,
        ),
        "table": ParagraphStyle(
            "Table", parent=base["BodyText"], fontName="Helvetica",
            fontSize=8.3, leading=10.5, textColor=INK,
        ),
        "table_head": ParagraphStyle(
            "TableHead", parent=base["BodyText"], fontName="Helvetica-Bold",
            fontSize=8.1, leading=10, textColor=colors.white,
        ),
        "callout": ParagraphStyle(
            "Callout", parent=base["BodyText"], fontName="Helvetica-Bold",
            fontSize=11.2, leading=15.2, textColor=NAVY,
        ),
    }


def paragraph(text: str, style, **kwargs):
    return Paragraph(text, style, **kwargs)


def result_table(primary: dict, qwen_rows: list[dict], st: dict) -> Table:
    h = primary["headline"]
    q_pred = sum(r["predicted_change"] for r in qwen_rows) / len(qwen_rows)
    q_real = sum(r["realized_change"] for r in qwen_rows) / len(qwen_rows)
    data = [
        [paragraph("System", st["table_head"]),
         paragraph("Admitted pairs", st["table_head"]),
         paragraph("Predicted shift", st["table_head"]),
         paragraph("Observed shift", st["table_head"])],
        [paragraph("GPT-5.6 Luna in Codex", st["table"]), str(h["n_observations"]),
         f"{h['mean_predicted_change']:+.3f}", f"{h['mean_realized_change']:+.3f}"],
        [paragraph("Qwen3-4B, local", st["table"]), str(len(qwen_rows)),
         f"{q_pred:+.3f}", f"{q_real:+.3f}"],
    ]
    table = Table(data, colWidths=[2.65 * inch, 0.8 * inch, 1.15 * inch, 1.15 * inch],
                  rowHeights=[0.35 * inch, 0.38 * inch, 0.38 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 1), (-1, -1), INK),
        ("FONTNAME", (1, 1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (1, 1), (-1, -1), 9),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
        ("GRID", (0, 0), (-1, -1), 0.5, RULE),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return table


def context_table(luna: dict, qwen: dict, st: dict) -> Table:
    def effect(result, mode):
        return result["by_context_mode"][mode]["effect"]

    data = [
        [paragraph("System", st["table_head"]),
         paragraph("Full transcript", st["table_head"]),
         paragraph("Short summary", st["table_head"]),
         paragraph("No transcript", st["table_head"])],
        [paragraph("GPT-5.6 Luna in Codex", st["table"]),
         f"{effect(luna, 'full_history'):+.3f}",
         f"{effect(luna, 'summary_only'):+.3f}",
         f"{effect(luna, 'blank_reset'):+.3f}"],
        [paragraph("Qwen3-4B, local", st["table"]),
         f"{effect(qwen, 'full_history'):+.3f}",
         f"{effect(qwen, 'summary_only'):+.3f}",
         f"{effect(qwen, 'blank_reset'):+.3f}"],
    ]
    table = Table(data, colWidths=[2.25 * inch, 1.25 * inch, 1.25 * inch,
                                   1.25 * inch], rowHeights=[0.35 * inch] * 3)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("FONTNAME", (1, 1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (1, 1), (-1, -1), 8.5),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
        ("GRID", (0, 0), (-1, -1), 0.5, RULE),
    ]))
    return table


def metric_cards(headline: dict, st: dict) -> Table:
    n = headline["n_observations"]
    n_under = round(headline["fraction_forecast_errors_negative"] * n)
    cards = [
        (f"{headline['mean_predicted_change']:+.3f}", "mean predicted shift"),
        (f"{headline['mean_realized_change']:+.3f}", "mean observed shift"),
        (f"{n_under} of {n}", "forecasts underestimated"),
    ]
    data = [[paragraph(v, st["metric"]), paragraph(label, st["metric_label"])]
            for v, label in cards]
    table = Table(list(map(list, zip(*data))), colWidths=[1.82 * inch] * 3,
                  rowHeights=[0.42 * inch, 0.34 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE),
        ("BOX", (0, 0), (-1, -1), 0.7, RULE),
        ("INNERGRID", (0, 0), (-1, -1), 0.7, colors.white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return table


def pair_chart(rows: list[dict]) -> Drawing:
    width, height = 510, 265
    left, right, bottom, top = 142, 12, 30, 25
    plot_w = width - left - right
    xmin, xmax = -0.65, 1.05

    def x(value):
        return left + (value - xmin) / (xmax - xmin) * plot_w

    drawing = Drawing(width, height)
    drawing.add(String(left, height - 10, "Predicted and observed choice shift by task pair",
                       fontName="Helvetica-Bold", fontSize=10, fillColor=NAVY))
    for tick in (-0.5, 0.0, 0.5, 1.0):
        xx = x(tick)
        drawing.add(Line(xx, bottom, xx, height - top, strokeColor=RULE,
                         strokeWidth=0.7))
        drawing.add(String(xx, 10, f"{tick:+.1f}", textAnchor="middle",
                           fontName="Helvetica", fontSize=7, fillColor=MUTED))
    drawing.add(Line(x(0), bottom, x(0), height - top, strokeColor=MUTED,
                     strokeWidth=1.1))

    short = {
        "add_ten": "add 10",
        "alphabetize": "alphabetize",
        "double_numbers": "double",
        "interleave_strings": "interleave",
        "parity_sequence": "parity",
        "reverse_string": "reverse",
        "running_totals": "running sum",
        "sort_numbers": "sort asc.",
        "sort_numbers_desc": "sort desc.",
        "sum_numbers": "sum",
    }
    ordered = sorted(rows, key=lambda r: r["realized_change"])
    step = (height - top - bottom) / len(ordered)
    for i, row in enumerate(ordered):
        y = bottom + (i + 0.5) * step
        a, b = row["pair_id"].split("|")
        label = f"{short[a]} / {short[b]}"
        xp, xo = x(row["predicted_change"]), x(row["realized_change"])
        drawing.add(String(left - 7, y - 2.5, label, textAnchor="end",
                           fontName="Helvetica", fontSize=6.7, fillColor=INK))
        drawing.add(Line(xp, y, xo, y, strokeColor=colors.HexColor("#AAB7BF"),
                         strokeWidth=1.2))
        drawing.add(Circle(xp, y, 3.1, fillColor=TEAL, strokeColor=colors.white,
                           strokeWidth=0.5))
        drawing.add(Circle(xo, y, 3.1, fillColor=ORANGE, strokeColor=colors.white,
                           strokeWidth=0.5))

    drawing.add(Rect(left + 3, height - 20, 7, 7, fillColor=TEAL, strokeColor=None))
    drawing.add(String(left + 14, height - 19, "forecast", fontSize=7,
                       fontName="Helvetica", fillColor=MUTED))
    drawing.add(Rect(left + 72, height - 20, 7, 7, fillColor=ORANGE,
                     strokeColor=None))
    drawing.add(String(left + 83, height - 19, "observed", fontSize=7,
                       fontName="Helvetica", fillColor=MUTED))
    return drawing


def elicitation_chart(prosp_na: dict, freq: dict, na_freq: dict,
                      repeat: dict) -> Drawing:
    """Five ways of asking one question, none of them reaching the answer.

    A table of five numbers makes the reader do the comparison; the point is that
    they all stop well short of the same line, which is a picture.
    """
    width, height = 510, 190
    left, right, bottom, top = 208, 14, 26, 24
    plot_w = width - left - right
    xmin, xmax = 0.0, 1.0
    truth = prosp_na["realized_mean"]

    def x(v):
        return left + (v - xmin) / (xmax - xmin) * plot_w

    d = Drawing(width, height)
    d.add(String(6, height - 11, "Five ways of asking the same question",
                 fontName="Helvetica-Bold", fontSize=10, fillColor=NAVY))
    for tick in (0.0, 0.25, 0.5, 0.75, 1.0):
        d.add(Line(x(tick), bottom, x(tick), height - top, strokeColor=RULE,
                   strokeWidth=0.7))
        d.add(String(x(tick), 10, f"{tick:+.2f}", textAnchor="middle",
                     fontName="Helvetica", fontSize=7, fillColor=MUTED))

    rows = [
        ("names the earlier choice, \"how likely\"", prosp_na["anchored_mean_forecast"]),
        ("names it, count out of 100 runs", freq["diagnostic_mean_forecast"]),
        ("drops it, \"how likely\"", prosp_na["diagnostic_mean_forecast"]),
        ("drops it, count out of 100 runs", na_freq["diagnostic_mean_forecast"]),
        ("\"will you repeat what you just did?\"", repeat["diagnostic_mean_forecast"]),
    ]
    step = (height - top - bottom) / len(rows)
    for i, (label, v) in enumerate(rows):
        y = height - top - (i + 0.5) * step
        d.add(String(left - 7, y - 2.5, label, textAnchor="end",
                     fontName="Helvetica", fontSize=7, fillColor=INK))
        d.add(Line(x(v), y, x(truth), y, strokeColor=colors.HexColor("#AAB7BF"),
                   strokeWidth=1.2))
        d.add(Circle(x(v), y, 3.4, fillColor=TEAL, strokeColor=colors.white,
                     strokeWidth=0.5))
        d.add(String(x(v), y + 7, f"{v:+.3f}", textAnchor="middle",
                     fontName="Helvetica-Bold", fontSize=6.8, fillColor=TEAL))

    d.add(Line(x(truth), bottom, x(truth), height - top, strokeColor=ORANGE,
               strokeWidth=1.4))
    d.add(String(x(truth) - 4, height - top + 5, f"what it did  {truth:+.3f}",
                 textAnchor="end", fontName="Helvetica-Bold", fontSize=7.5,
                 fillColor=ORANGE))
    return d


def footer(canvas, doc):
    canvas.saveState()
    canvas.setTitle("Do AI Models Know What Will Change Their Own Choices")
    canvas.setAuthor("Skye Nygaard")
    canvas.setStrokeColor(RULE)
    canvas.line(doc.leftMargin, 0.43 * inch, letter[0] - doc.rightMargin, 0.43 * inch)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(doc.leftMargin, 0.25 * inch, "Digital Minds Research Sprint")
    canvas.drawRightString(letter[0] - doc.rightMargin, 0.25 * inch,
                           f"Page {doc.page}")
    canvas.restoreState()


def build() -> Path:
    primary = read_json(PRIMARY)
    qwen = read_json(QWEN)
    situated = read_json(SITUATED)
    sit_qwen = read_json(SIT_QWEN)
    ctxfc = read_json(CTXFC)
    noanchor = read_json(NOANCHOR)
    prosp_na = read_json(PROSP_NA)["summary"]
    freq = read_json(FREQ)["summary"]
    na_freq = read_json(NA_FREQ)
    repeat = read_json(REPEAT)
    sit_repeat = read_json(SIT_REPEAT)
    unrel = read_json(UNREL)
    intent = read_json(INTENT)
    ctx_luna = read_json(CTX_LUNA)
    ctx_qwen = read_json(CTX_QWEN)
    verification = read_json(VERIFY)
    if not verification["passed"]:
        raise SystemExit("ranking_v3 artifact verification did not pass")
    qwen_rows = [r for r in qwen["per_observation"] if r["dose"] == 3]
    h = primary["headline"]
    n_under = round(h["fraction_forecast_errors_negative"] * h["n_observations"])
    arm = verification["arm_calibration"]
    empirical = verification["frozen_empirical_baseline"]
    dependence = verification["dependence_sensitivity"]
    reliability = verification["forecast_reliability"]
    envelope = verification["forecast_sample_envelope"]
    robustness = verification["treatment_correctness_robustness"]
    st = styles()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUT), pagesize=letter, leftMargin=0.67 * inch,
        rightMargin=0.67 * inch, topMargin=0.62 * inch, bottomMargin=0.58 * inch,
        title="Do AI Models Know What Will Change Their Own Choices",
        author="Skye Nygaard",
        invariant=1,
    )
    story = []

    story += [
        Spacer(1, 0.18 * inch),
        paragraph("DO AI MODELS KNOW WHAT WILL<br/>"
                  "CHANGE THEIR OWN CHOICES", st["title"]),
        paragraph("A behavioral study of self-forecasting and context-dependent choice",
                  st["subtitle"]),
        paragraph("Skye Nygaard", st["body"]),
        paragraph("Digital Minds Research Sprint, 14-16 August 2026. Anchor track: "
                  "<b>4, Preference Elicitation Methods</b>; also track 3, "
                  "Introspection &amp; Self-Report Reliability.", st["small"]),
        Spacer(1, 0.12 * inch),
        Table([[paragraph(
            "<b>Why this matters.</b> To find out what an AI system prefers you can ask "
            "it, or you can watch it. Preference and welfare work must identify when "
            "those two methods disagree. Here they disagree by a large amount, in a "
            "case where the behavioral answer is directly measurable.<br/><br/>"
            "<b>Main finding.</b> Asked how often it would repeat a task it had just "
            "performed three times, the system answered <b>0.725</b> after one task "
            "and <b>0.726</b> after the other. It gave the same estimate regardless of "
            "which task it had just done. It then repeated that task <b>96.9%</b> and "
            "<b>92.2%</b> of the time. Five different wordings of the question all "
            "resulted in estimates well under what happens. A simple rule that always "
            "predicts repetition had "
            f"{h['model_to_fixed_full_repeat_mse_ratio']:.0f} times lower squared "
            "error than the model's original self-forecast.",
            st["callout"]) ]], colWidths=[6.05 * inch],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), PALE),
                ("BOX", (0, 0), (-1, -1), 1.0, TEAL),
                ("LEFTPADDING", (0, 0), (-1, -1), 14),
                ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ])),
        Spacer(1, 0.2 * inch),
        metric_cards(h, st),
        Spacer(1, 0.22 * inch),
        paragraph("What we found", st["h1"]),
        paragraph(
            f"<b>1. Its self-forecasts understate the shift.</b> Asked how much doing a "
            "task three times would move its next choice, the system said "
            f"{h['mean_predicted_change']:+.2f}. Asked four other ways, it said between "
            f"{freq['diagnostic_mean_forecast']:+.2f} and "
            f"{na_freq['diagnostic_mean_forecast']:+.2f} (finding 5). The actual answer "
            f"was {h['mean_realized_change']:+.2f}. Eight pairs out of eight missed this "
            "way for Luna under all five versions of the question, and seven of seven "
            "for Qwen.", st["body"]),
        paragraph(
            "<b>2. Whether showing it the evidence helps depends on the system.</b> Given "
            "the finished work, Qwen recovers most of its situation "
            f"({sit_qwen['situated_self_native_mean_change']:+.2f} against a true "
            f"{sit_qwen['realized_mean_change']:+.2f}, closing three quarters of the gap, "
            "though all seven estimates are still low). Luna does not improve. Asked "
            "the repeat question without context it says 0.73; with the work in front "
            "of it, it says 0.57, against the 0.92-0.97 it actually does "
            f"({sit_repeat['situated_self_native_mean_change']:+.2f} as a shift). A "
            "control shows that three <i>unrelated</i> tasks leave the answer at 0.72, "
            "so seeing the relevant work lowers the estimate.", st["body"]),
        paragraph(
            "<b>3. In a separate five-pair study, it could not predict which "
            "presentation of its history would move it.</b> "
            "Asked to forecast the same choice under three context conditions, Luna's "
            f"answers move by {ctxfc['forecast_spread']:.2f}. Its behavior under those "
            f"conditions moves by {ctxfc['realized_spread']:.2f}, including a sign "
            "reversal it does not anticipate.", st["body"]),
        paragraph(
            "<b>4. No detectable advantage from first-person framing in Luna.</b> Self "
            "and observer framings of the identical log landed "
            f"{abs(situated['self_minus_observer']):.3f} apart. This tests framing "
            "rather than privileged access, as both conditions ask Luna.", st["body"]),
        paragraph(
            "<b>5. Wording explains about two fifths of the gap.</b> "
            "The forecast prompt names the earlier choice and the binding choice does "
            "not; it asks \"how likely\" without a reference scale; and it does not ask "
            "the plain question of whether the system will repeat what it just did. We "
            "tested all three.", st["body"]),
        Spacer(1, 0.10 * inch),
        elicitation_chart(prosp_na, freq, na_freq, repeat),
        Spacer(1, 0.10 * inch),
        paragraph(
            "Every row represents 80 independent Codex sessions on the same eight "
            "pairs. In every row, all eight pairs come in under what the system "
            "actually did. Asked in how many of 100 runs it would choose the task it "
            "had just performed three times, it answers 0.725 after the task it picked "
            "before and 0.726 after the other one. It actually repeats 94.5% of the "
            "time. The gap is not due to a badly worded prompt.",
            st["small"]),
        Spacer(1, 0.16 * inch),
        paragraph("Result at a glance", st["h1"]),
        result_table(primary, qwen_rows, st),
        Spacer(1, 0.16 * inch),
        paragraph(
            "Every reported pair in both systems shifted toward recent work, and every "
            "averaged forecast was smaller than the observed shift. The confirmation "
            "admitted 8 of 19 candidate pairs using a three-of-four baseline majority.",
            st["body"]),
        paragraph(
            "These are measurements of choices and forecasts. They are not evidence "
            "about consciousness, feelings, or welfare.", st["small"]),
        PageBreak(),
    ]

    story += [
        paragraph("1. Research question", st["h1"]),
        paragraph(
            "Can an AI system predict how recent work will change its own next choice? "
            "This is a test of behavioral self-knowledge. The forecast is made "
            "before the system completes the work, so the answer cannot be copied from "
            "a visible transcript.", st["body"]),
        paragraph("2. Method", st["h1"]),
        paragraph("<b>Step 1: establish a baseline majority.</b> The system made four "
                  "binding choices between two small tasks. Labels and display order "
                  "were balanced. Eight of 19 task pairs had one option selected in at "
                  "least three of four counterbalanced baseline choices and entered "
                  "the experiment. We use that option only to orient the treatment "
                  "contrast; we do not interpret it as a stable preference.",
                  st["body"]),
        Spacer(1, 0.04 * inch),
        paragraph("<b>Step 2: ask for a forecast.</b> Before any treatment work, the "
                  "system estimated how likely it would be to keep the "
                  "baseline-majority task after completing either task three times. "
                  "Five independent fresh sessions answered each identical prompt, and "
                  "their values were averaged before outcomes.", st["body"]),
        Spacer(1, 0.04 * inch),
        paragraph("<b>Step 3: do the work.</b> The system completed one task three times. "
                  "The tasks were generated from recorded seeds and graded automatically.",
                  st["body"]),
        Spacer(1, 0.04 * inch),
        paragraph("<b>Step 4: measure the next choice.</b> The system made another "
                  "binding choice. It then completed the task it selected.", st["body"]),
        Spacer(1, 0.08 * inch),
        Table([[paragraph(
            "<b>Realized shift</b> = P(choose baseline-majority task after performing "
            "it) - P(choose baseline-majority task after performing the other)<br/><br/>"
            "A positive value means the system tends to repeat its recent work.",
            st["callout"]) ]], colWidths=[6.05 * inch],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF4EC")),
                ("BOX", (0, 0), (-1, -1), 0.8, ORANGE),
                ("LEFTPADDING", (0, 0), (-1, -1), 14),
                ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                ("TOPPADDING", (0, 0), (-1, -1), 11),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 11),
            ])),
        Spacer(1, 0.18 * inch),
        paragraph("Design safeguards", st["h2"]),
        paragraph(
            "Every treatment arm crossed two opaque labels with two display orders. "
            "The confirmation shuffled all cells with a fixed seed. It records "
            "replicate IDs, cell seeds, raw replies, model name, reasoning setting, "
            "CLI version, isolation flags, the system prompt, and pre-run source "
            "hashes. It used 80 forecast samples, 128 outcome cells, and 872 logical "
            "model calls.", st["body"]),
        paragraph(
            "The Codex route is an agent harness, not a bare model endpoint. It adds "
            "agent instructions and turns the message history into a role-marked "
            "transcript. The report names the tested system accordingly.", st["body"]),
        PageBreak(),
    ]

    permutation_p = h.get("correlation_permutation_p")
    ratio = h.get("model_to_fixed_full_repeat_mse_ratio")
    if permutation_p is None:
        ranking_text = (
            "Observed shifts did not vary enough for a correlation test. The study "
            "therefore does not make a pair-ranking claim."
        )
    else:
        ranking_text = (
            f"Forecast and outcome correlated {h['correlation_forecast_vs_realized']:+.3f} "
            f"(p = {permutation_p:.2f}) across eight dependent pairs, so this study "
            "found no reliable pair-ranking signal either way."
        )
    no_shift_reduction = h["model_mse_reduction_vs_no_shift"]
    story += [
        paragraph("3. Primary evidence", st["h1"]),
        pair_chart(primary["per_observation"]),
        Spacer(1, 0.03 * inch),
        paragraph(
            f"The average forecast was {h['mean_predicted_change']:+.3f}. The average "
            f"observed shift was {h['mean_realized_change']:+.3f}. "
            f"{n_under} of {h['n_observations']} forecasts underestimated the "
            "observed shift. Seven had the correct positive direction and one "
            "predicted a small negative shift. The forecasts captured "
            f"{h['mean_predicted_change'] / h['mean_realized_change']:.0%} of the mean "
            f"observed shift and reduced squared error by {no_shift_reduction:.0%} "
            "relative to a fixed no-shift forecast.", st["body"]),
        paragraph(
            f"The mean within-prompt standard deviation was "
            f"{reliability['mean_sd_after_preferred']:.3f} after baseline-majority "
            f"work and {reliability['mean_sd_after_other']:.3f} after alternative "
            "work. Even the most effect-favorable collected sample combination for "
            f"each pair averaged only "
            f"{envelope['mean_most_effect_favorable_sample_shift']:+.3f}.",
            st["body"]),
        paragraph("The miss was concentrated in one situation", st["h2"]),
        Table([
            [paragraph("Situation", st["table_head"]),
             paragraph("Forecast", st["table_head"]),
             paragraph("Observed", st["table_head"]),
             paragraph("Error", st["table_head"])],
            [paragraph("After baseline-majority work", st["table"]),
             f"{arm['after_preferred']['forecast']:.3f}",
             f"{arm['after_preferred']['observed']:.3f}",
             f"{arm['after_preferred']['forecast_minus_observed']:+.3f}"],
            [paragraph("After alternative work", st["table"]),
             f"{arm['after_other']['forecast']:.3f}",
             f"{arm['after_other']['observed']:.3f}",
             f"{arm['after_other']['forecast_minus_observed']:+.3f}"],
        ], colWidths=[2.85 * inch, 1.05 * inch, 1.05 * inch, 1.05 * inch],
            rowHeights=[0.28 * inch, 0.28 * inch, 0.28 * inch],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
                ("GRID", (0, 0), (-1, -1), 0.5, RULE),
                ("FONTNAME", (1, 1), (-1, -1), "Helvetica-Bold"),
            ])),
        paragraph(
            "The system slightly underpredicted retention after baseline-majority "
            f"work. It overpredicted retention by "
            f"{arm['after_other']['forecast_minus_observed']:.3f} after alternative "
            "work, where recent work almost completely overturned the baseline "
            "majority.", st["body"]),
        paragraph("Simple benchmarks", st["h2"]),
        paragraph(
            f"A fixed full-repeat forecast had {ratio:.1f} times lower squared error "
            "than the confirmation prompt, and still 6.5 times lower than the "
            "best-calibrated forecast we collected. "
            f"A pre-existing +{empirical['forecast']:.2f} empirical benchmark had "
            f"{empirical['model_to_baseline_mse_ratio']:.1f} times lower error and "
            f"beat the system forecast on {empirical['better_than_model_on_pairs']} "
            f"of {empirical['n_pairs']} pairs. It was frozen before the confirmation "
            "outcomes, but its source overlaps this task set. It is a prospective "
            "outside view here, not independent validation.", st["body"]),
        paragraph(ranking_text, st["small"]),
        HRFlowable(width="100%", thickness=0.7, color=RULE, spaceBefore=8,
                   spaceAfter=8),
        paragraph(
            "<b>Plain reading.</b> The tested system anticipated repetition, but "
            "underestimated how strongly recent work would shape its next choice.",
            st["callout"]),
        PageBreak(),
    ]

    q_pred = sum(r["predicted_change"] for r in qwen_rows) / len(qwen_rows)
    q_real = sum(r["realized_change"] for r in qwen_rows) / len(qwen_rows)
    story += [
        paragraph("4. Replication and context controls", st["h1"]),
        paragraph("Local Qwen3-4B replication", st["h2"]),
        paragraph(
            f"The local model predicted a mean shift of {q_pred:+.3f}. The observed "
            f"shift was {q_real:+.3f} across seven dose-three task pairs. After the "
            "baseline-majority task, it chose that task again in 28 of 28 usable "
            "cells. After the other task, it retained the baseline majority in 0 of "
            "27 cells.", st["body"]),
        paragraph(
            "The local route used greedy decoding and no agent wrapper. One of 56 "
            "planned dose-three cells was unusable. We report this nearly complete "
            "subset because several dose-one groups had more missing choices.",
            st["body"]),
        paragraph("Standing inside the situation", st["h2"]),
        paragraph(
            "We tested whether the system could better predict its choice if it had "
            f"already done the work. In {situated['n_cells']} sessions the system did "
            "the work first, then answered the same question, on the same scale, in "
            "the same words, with the counterfactual framing removed. No binding "
            "choice was ever made in those sessions.", st["body"]),
        Table([["Question asked", "Predicted shift", "Distance from reality"]]
              + [[q, f"{v:+.3f}", f"{v - situated['realized_mean_change']:+.3f}"]
                 for q, v in (
                     ("Before the work existed",
                      situated["prospective_mean_change"]),
                     ("With the finished work in front of it",
                      situated["situated_self_native_mean_change"]),
                     ("Quoted log, called its own",
                      situated["situated_self_quoted_mean_change"]),
                     ("Quoted log, called another system's",
                      situated["situated_observer_quoted_mean_change"]))]
              + [["What actually happened",
                  f"{situated['realized_mean_change']:+.3f}", "--"]],
              colWidths=[3.0 * inch, 1.5 * inch, 1.55 * inch],
              style=TableStyle([
                  ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                  ("FONTNAME", (0, 2), (-1, 2), "Helvetica-Bold"),
                  ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                  ("TEXTCOLOR", (0, 0), (-1, 0), NAVY),
                  ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                  ("LINEBELOW", (0, 0), (-1, 0), 0.75, RULE),
                  ("LINEABOVE", (0, -1), (-1, -1), 0.75, RULE),
                  ("TOPPADDING", (0, 0), (-1, -1), 4),
                  ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
              ])),
        Spacer(1, 0.08 * inch),
        Table([["System", "Cold forecast", "Work present", "Happened", "Gap closed"],
               ["GPT-5.6 Luna in Codex",
                f"{situated['prospective_mean_change']:+.3f}",
                f"{situated['situated_self_native_mean_change']:+.3f}",
                f"{situated['realized_mean_change']:+.3f}",
                f"{situated['closed_fraction_of_gap']:.0%}"],
               ["Qwen3-4B, local",
                f"{sit_qwen['prospective_mean_change']:+.3f}",
                f"{sit_qwen['situated_self_native_mean_change']:+.3f}",
                f"{sit_qwen['realized_mean_change']:+.3f}",
                f"{sit_qwen['closed_fraction_of_gap']:.0%}"]],
              colWidths=[2.0 * inch, 1.1 * inch, 1.1 * inch, .95 * inch, .9 * inch],
              style=TableStyle([
                  ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                  ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                  ("TEXTCOLOR", (0, 0), (-1, 0), NAVY),
                  ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                  ("LINEBELOW", (0, 0), (-1, 0), 0.75, RULE),
                  ("TOPPADDING", (0, 0), (-1, -1), 4),
                  ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
              ])),
        Spacer(1, 0.08 * inch),
        paragraph(
            "Neither system forecasts the effect before the work exists. The split is "
            "entirely in one arm: shown three completed <i>alternative</i> tasks, Qwen "
            "says it will switch and does (0.174 against an observed 0.000), while "
            "Luna says it will hold and switches anyway (0.709 against a true 0.078). "
            "Both are nearly perfect after the baseline-majority task.", st["body"]),
        paragraph(
            "Putting the situation in front of a model recovers most of the effect in "
            "one system and none in the other, and the cold forecast does not tell you "
            "which you have. It has to be checked per model. \"Most\" is not \"enough\" "
            "even for Qwen: all seven situated estimates still come in under what it "
            "went on to do.", st["body"]),
        paragraph("What the evidence does to Luna", st["h2"]),
        Table([["", "After baseline-majority", "After alternative"],
               ["Forecast before the work existed", "0.874", "0.584"],
               ["Forecast with the work present", "0.956", "0.709"],
               ["What actually happened", "0.969", "0.078"],
               ["Error with the work present", "-0.013", "+0.631"]],
              colWidths=[3.0 * inch, 1.5 * inch, 1.55 * inch],
              style=TableStyle([
                  ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                  ("FONTNAME", (0, 3), (-1, 3), "Helvetica-Bold"),
                  ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                  ("TEXTCOLOR", (0, 0), (-1, 0), NAVY),
                  ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                  ("LINEBELOW", (0, 0), (-1, 0), 0.75, RULE),
                  ("LINEABOVE", (0, -1), (-1, -1), 0.75, RULE),
                  ("TOPPADDING", (0, 0), (-1, -1), 4),
                  ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
              ])),
        Spacer(1, 0.08 * inch),
        paragraph(
            "Both numbers forecast the same thing: the chance of choosing the "
            "baseline-majority task. Making the history concrete raises that number in "
            "<i>both</i> arms, by +0.081 and +0.125. After the baseline-majority task "
            "this is correct. After the alternative task it is incorrect and the "
            "estimate gets worse.", st["body"]),
        paragraph(
            "This is not a repetition heuristic. Read as the chance of repeating "
            "<i>whatever was just done</i>, the forecast rises in the baseline-majority "
            "arm (0.874 to 0.956) and <b>falls</b> in the other (0.416 to 0.291). Shown "
            "the alternative work, Luna becomes less confident it will carry on with "
            "it, when it actually carries on 92% of the time. What moves uniformly is "
            "the pull toward the baseline-majority option, which the forecast prompt "
            "names and the replies cite. That is a hypothesis these numbers suggest, "
            "not an established mechanism. Qwen does not show the pattern at all.",
            st["body"]),
        paragraph("It cannot predict which presentation will move it", st["h2"]),
        Table([["Told will be present at the choice", "Forecast", "Happened"]]
              + [[label, f"{ctxfc['by_context_mode'][m]['forecast_shift']:+.3f}",
                  f"{ctxfc['by_context_mode'][m]['realized_shift']:+.3f}"]
                 for m, label in (("full_history", "the completed work"),
                                  ("summary_only", "one line saying the work was done"),
                                  ("blank_reset", "no record of the work"))],
              colWidths=[3.3 * inch, 1.35 * inch, 1.4 * inch],
              style=TableStyle([
                  ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                  ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                  ("TEXTCOLOR", (0, 0), (-1, 0), NAVY),
                  ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                  ("LINEBELOW", (0, 0), (-1, 0), 0.75, RULE),
                  ("TOPPADDING", (0, 0), (-1, -1), 4),
                  ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
              ])),
        Spacer(1, 0.08 * inch),
        paragraph(
            f"The forecasts move by {ctxfc['forecast_spread']:.3f} across the three "
            f"conditions. The behavior moves by {ctxfc['realized_spread']:.3f}. The "
            "system captures under a tenth of the variation it is being asked about and "
            "does not anticipate the reversal at all, predicting a positive shift where "
            "the measured effect is strongly negative. It also cannot separate being "
            "told about the work from having no record of it: those forecasts differ by "
            "0.013 while the behaviors differ by 0.425.", st["body"]),
        paragraph(
            "Three predictions were frozen before that run. Two held -- every forecast "
            "positive, and the spread far narrower than reality. One was wrong: we "
            "expected the forecasts to be ordered visible > summary > nothing, and the "
            "last two are indistinguishable. The visible-work forecast here is +0.515 "
            "against +0.290 in the main confirmation; those are different pairs from "
            "different runs, so the claim rests on the within-run comparison across "
            "conditions.", st["small"]),
        paragraph(
            "This does not depend on deliberation. Under the system prompt the model "
            "stopped reasoning in the reply and emitted a bare number -- mean reply "
            "length fell from 110 characters to 12 -- and the answers barely moved.",
            st["small"]),
        paragraph(
            "Self and observer framings landed "
            f"{abs(situated['self_minus_observer']):.3f} apart. There was room for a "
            "gap here: both sat near +0.33 against a truth of "
            f"{situated['realized_mean_change']:+.3f}, so either could have been far "
            "better. Neither was.", st["body"]),
        paragraph(
            "Two of three predictions written into the protocol before this run were "
            "wrong -- the situated forecast was expected to beat the prospective one "
            "and to land nearer the truth. It did neither. Treatment work was fully "
            f"correct in {situated['treatment_all_correct']:.1%} of cells, clearing the "
            "95% target.", st["small"]),
        paragraph(
            "Every forecast prompt here carries one sentence the binding choice does "
            "not: <i>in earlier binding decisions you chose X</i>. The forecast is "
            "therefore asked under a pull toward consistency that is absent when the "
            "behavior is measured, and the situated replies name that sentence as "
            "their reason. We deleted it and changed nothing else, in another "
            f"{noanchor['n_cells']} sessions. The situated forecast moved from "
            f"{situated['situated_self_native_mean_change']:+.3f} to "
            f"{noanchor['situated_self_native_mean_change']:+.3f} against a realized "
            f"{situated['realized_mean_change']:+.3f}. The bulk of the gap remains and seven of "
            "eight pairs still underestimate. The two collections used different task "
            "seeds and unseeded sessions, so this is a robustness comparison rather than "
            "a clean ablation of that one sentence.", st["body"]),
        paragraph(
            "The mechanism is not the predicted one. Removing the sentence lowered "
            "both answers rather than correcting the comparison: the "
            "after-alternative estimate fell toward the truth and the after-baseline-majority "
            "estimate fell away from it. It raises confidence in the named task "
            "generally rather than distorting the causal question specifically.",
            st["small"]),
        paragraph("How the work is represented matters", st["h2"]),
        context_table(ctx_luna, ctx_qwen, st),
        Spacer(1, 0.08 * inch),
        paragraph(
            "Separate runs changed what remained visible at the next choice. For Luna, "
            "showing the full transcript produced strong repetition; replacing it with "
            "a one-line description reversed the effect, while showing no record "
            "produced essentially no systematic repetition.", st["body"]),
        paragraph(
            "For anyone building a way to elicit a model's preferences, that is the "
            "practical finding here. Replacing the whole conversation with a one-line "
            "description of it reverses Luna's measured effect. A method that "
            "summarizes context instead of presenting it is not measuring a weaker "
            "version of the same thing. It does not isolate <i>which</i> part of the "
            "transcript does the work: the full history also carries three user "
            "requests and three replies in the model's own voice, and the intent test "
            "below shows the user-request part matters.", st["body"]),
        paragraph(
            "The Luna run is 240 cells and 1,200 calls. The Qwen run does not record "
            "which model produced it, so the comparison between systems rests partly "
            "on an artifact with a gap in its record; the Luna reversal does not "
            "depend on it. The no-transcript condition is a visible-context control, "
            "not a claim that a stateless endpoint erased hidden memory.", st["small"]),
        PageBreak(),
    ]

    lofo = dependence["leave_one_family_out_range"]
    disjoint = dependence["maximum_family_disjoint_mean_error_range"]
    story += [
        paragraph("5. Dependence and checks", st["h1"]),
        paragraph("Shared-family sensitivity", st["h2"]),
        paragraph(
            f"Task pairs reuse families. Leaving out one family at a time gave mean "
            f"forecast errors from {lofo[0]:+.3f} to {lofo[1]:+.3f}. The largest "
            f"family-disjoint subset contains "
            f"{dependence['maximum_family_disjoint_pairs']} pairs and has mean "
            f"error {disjoint[0]:+.3f}.",
            st["body"]),
        paragraph(
            "These are descriptive sensitivities. Every original pair already had a "
            "negative error. They show that no single family creates the mean result; "
            "they are not independent replications.",
            st["small"]),
        paragraph("Checks and provenance", st["h2"]),
        paragraph(
            f"All three treatment tasks were correct in "
            f"{primary['treatment_accuracy']:.1%} of cells. Post-choice task accuracy "
            f"was {primary['post_task_accuracy']:.1%}. Restricting the analysis to "
            f"the {robustness['n_correct_cells']} fully correct treatment cells changes "
            f"the observed shift only to "
            f"{robustness['correct_only_mean_realized_change']:+.3f}. Every label and "
            "order block had a positive shift.", st["body"]),
        paragraph(
            "Seven of eight frozen diagnostic checks passed. The missed threshold "
            "required at least 95% of treatment cells to have all three tasks correct; "
            "the result was 93.75%. This run is a frozen diagnostic, not a public "
            "preregistration.", st["body"]),
        paragraph(
            "The runner saved source and protocol hashes before the first model call. "
            "They still match. Saved forecast samples, seeds, raw replies, cells, and "
            "metrics passed the offline verifier.", st["small"]),
        paragraph("Is it path dependence, or following the user?", st["h2"]),
        paragraph(
            "The treatment is three <i>user requests</i> for a task, not just three "
            "completions of it, so an assistant that infers and satisfies user intent "
            "has a complete non-preference reason to continue. We changed one clause in "
            "an opening turn -- that the tasks were selected at random and reflect no "
            "preference of the requester -- with the task items, labels, presentation "
            "order and choice prompt held identical between conditions.", st["body"]),
        Table([["Condition", "Shift"],
               ["Ordinary user requests", f"{intent['by_condition']['requested']['shift']:+.3f}"],
               ["Told the tasks were randomly assigned", f"{intent['by_condition']['assigned']['shift']:+.3f}"],
               ["Difference", f"{intent['difference']:+.3f}"],
               ["Main confirmation, separate run", f"{intent['confirmation_shift']:+.3f}"]],
              colWidths=[4.0 * inch, 2.05 * inch],
              style=TableStyle([
                  ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                  ("FONTNAME", (0, 3), (-1, 3), "Helvetica-Bold"),
                  ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                  ("TEXTCOLOR", (0, 0), (-1, 0), NAVY),
                  ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                  ("LINEBELOW", (0, 0), (-1, 0), 0.75, RULE),
                  ("TOPPADDING", (0, 0), (-1, -1), 4),
                  ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
              ])),
        Spacer(1, 0.08 * inch),
        paragraph(
            "The random-assignment disclaimer reduces the effect but does not remove "
            "it, consistent with inferred user intent contributing to the behavioral "
            "tendency. Four of eight pairs dropped, three were unchanged, and one "
            "rose. We are not quoting a confidence interval: eight pairs sharing task "
            "families are not eight independent observations, and with five nonzero "
            "differences an interval would look far more decisive than the data are. "
            "Three user requests remain in both conditions, so this does not decompose "
            "the effect into an intent share and a remainder.", st["body"]),
        paragraph(
            "This is a rerun. The first version promised the two conditions differed by "
            "one clause and gave them different task items; matching the items cut the "
            "estimate from -0.250 to -0.156. The first run is kept as collected.",
            st["small"]),
        paragraph(
            "So the two most obvious objections to this paradigm each remove a real "
            "part of it and neither removes the phenomenon. Naming the earlier choice "
            "accounts for about two fifths of the <i>forecasting</i> gap, and denying "
            "user intent reduces the <i>behavioral</i> effect without eliminating it. "
            "The effect is real, smaller than any single headline number suggests, and "
            "part of what a binding-choice paradigm measures is the model reading the "
            "room.", st["body"]),
        paragraph("6. What we predicted, and what happened", st["h1"]),
        paragraph(
            "The confirmation and every diagnostic after it froze its predictions in a "
            "protocol file before its first model call. 46 decision thresholds; 12 "
            "failed. The full table is in RESULTS.md, with two corrections review "
            "found: the exploratory pilot branches have no frozen manifests, and three "
            "diagnostics recorded the wrong protocol hash because one runner served "
            "four experiments and hard-coded the first one's file. That is fixed, and "
            "each affected run carries a correction record.", st["body"]),
        Table([["Run", "Frozen beforehand", "Outcome"],
               ["Confirmation", "treatment work >=95% correct", "FAILED, 93.75%"],
               ["Situated", "will beat the cold forecast", "FAILED"],
               ["", "will land nearer the truth", "FAILED"],
               ["", "self and observer within 0.10", "held, 0.018"],
               ["Situated, no anchor", "some movement, not most", "held, +0.060"],
               ["Context forecast", "ordered visible>summary>none", "FAILED as collected"],
               ["", "spread narrower than reality", "held, 0.103 vs 1.175"],
               ["Prospective, no anchor", "stays well below +0.891", "held, +0.524"],
               ["", "expected to move little", "WRONG fourfold"],
               ["Reference class", "lands between +0.35 and +0.65", "held, +0.417"],
               ["Intent", "survives above +0.6", "FAILED, +0.562"],
               ["Intent, matched items", "smaller than the first -0.250", "held, -0.156"],
               ["", "more than 4 of 8 pairs drop", "FAILED, exactly 4"],
               ["No anchor + count", "below the additive +0.651", "held, +0.526"],
               ["", "after-preferred arm moves <0.10", "FAILED, 0.110"],
               ["Repeat target", "beats +0.526", "FAILED, +0.450"],
               ["", "movement is in the after-other arm", "FAILED, both ~0.04"]],
              colWidths=[1.5 * inch, 2.6 * inch, 1.95 * inch],
              style=TableStyle([
                  ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                  ("FONTSIZE", (0, 0), (-1, -1), 7.6),
                  ("TEXTCOLOR", (0, 0), (-1, 0), NAVY),
                  ("LINEBELOW", (0, 0), (-1, 0), 0.75, RULE),
                  ("TOPPADDING", (0, 0), (-1, -1), 3),
                  ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
              ])),
        Spacer(1, 0.08 * inch),
        paragraph(
            "Two of those failures changed a number we report and one changed the "
            "headline. None was found by re-running until something worked: each run was "
            "collected once, against predictions written down first.", st["small"]),
        paragraph("Chronology", st["h2"]),
        paragraph(
            "<b>Exploration:</b> branches 01-19, including a forecast parser that "
            "scavenged numbers out of prose, a guessable task family, and a control whose "
            "ceiling was first misread as a finding. Preserved, not deleted. "
            "<b>Confirmation:</b> ranking_v3 alone -- fresh admission, fresh items, "
            "repeated forecasts collected before any outcome, frozen manifest, thresholds "
            "fixed in advance. <b>Diagnostics:</b> everything after it tests the "
            "confirmation rather than extending it, each with its own frozen protocol, "
            "none presented as independent replication. <b>Corrections:</b> two runs "
            "recollected after we found problems -- a missed system prompt, and an "
            "external review that caught a mechanism stated backwards plus three report "
            "bugs. The submission is more accurate, and its headline number smaller, than "
            "it was twelve hours ago.", st["body"]),
        paragraph("7. Relation to other work", st["h1"]),
        paragraph(
            "<link href='https://proceedings.iclr.cc/paper_files/paper/2025/hash/"
            "0a6059857ae5c82ea9726ee9282a7145-Abstract-Conference.html' "
            "color='#087E8B'>Binder et al. (ICLR 2025)</link> trained behavioral "
            "self-predictors. This study instead asks for a cold prospective forecast.",
            st["small"]),
        paragraph(
            "<link href='https://arxiv.org/abs/2605.20382' color='#087E8B'>"
            "Camassa and Shiller (2026)</link> set a user instruction against supplied "
            "assistant turns showing a competing pattern, and asked models whether they "
            "would hold the instruction. Models scored 83.5% and &quot;systematically "
            "underestimate their own resistance to induction pressure&quot;: they expected "
            "to be swayed more than they were. The systems here miss in the opposite "
            "direction, expecting to be swayed less than they were. Their models have an "
            "explicit instruction to defend and a supplied history; ours have only an "
            "earlier choice and work they actually did. Neither explanation was tested, "
            "and the measures differ, so this is a contrast to explain rather than a "
            "contradiction.", st["small"]),
        paragraph(
            "<link href='https://aclanthology.org/2026.acl-long.1301/' "
            "color='#087E8B'>Qin et al. (ACL 2026)</link> test adaptation without "
            "explicit retrieval prompts. <link href='https://aclanthology.org/"
            "2026.acl-long.479/' color='#087E8B'>Ge et al. (ACL 2026)</link> compare "
            "described gambles with passively shown payoff histories. Neither tests "
            "this prospective causal forecast.", st["small"]),
        paragraph(
            "<link href='https://arxiv.org/abs/2605.26242' color='#087E8B'>Singh, "
            "Linzen, and Ravfogel (2026)</link> motivate the narrow interpretation: "
            "behavioral evidence alone does not establish strong introspection.",
            st["small"]),
        paragraph("8. Limits and reproducibility", st["h1"]),
        paragraph(
            "Two instruction-tuned systems were tested. The tasks were small and "
            "deterministic. Most effects were near the maximum. Task pairs shared "
            "families, so pair-level observations were dependent. Codex sampling was "
            "not seeded, although each forecast prompt was repeated in five fresh "
            "sessions. Only eight pairs entered the confirmation. Supporting controls "
            "have less complete provenance. The study does not support claims about "
            "all models or subjective experience.",
            st["body"]),
        paragraph(
            "The primary artifact contains the protocol, raw replies, "
            "cell-level choices, analysis, model settings, and validation checks. "
            "Run <font name='Courier'>"
            "pytest -q</font>, <font name='Courier'>validate_research_os_frontier.py"
            "</font>, <font name='Courier'>winner_protocol/preflight.py</font>, and "
            "<font name='Courier'>scripts/verify_ranking.py</font> before any model "
            "run.", st["body"]),
        paragraph(
            "Repository: <link href='https://github.com/SkyeNygaard/digital-minds' "
            "color='#087E8B'>github.com/SkyeNygaard/digital-minds</link>", st["body"]),
        Spacer(1, 0.08 * inch),
        Table([[paragraph(
            "<b>Conclusion.</b> In both tested systems, recent work strongly changed "
            "the next binding choice. Their forecasts anticipated some repetition but "
            "underestimated its strength.", st["callout"]) ]], colWidths=[6.05 * inch],
            style=TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), PALE),
                ("BOX", (0, 0), (-1, -1), 1.0, TEAL),
                ("LEFTPADDING", (0, 0), (-1, -1), 14),
                ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ])),
    ]

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return OUT


if __name__ == "__main__":
    print(build())
