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
PRIMARY = ROOT / "parallel_frontier/20_preference_foresight/results/ranking_v2/summary.json"
QWEN = ROOT / "parallel_frontier/20_preference_foresight/results/local_qwen4b_v1/summary.json"
CONTROL = ROOT / "parallel_frontier/16_self_prediction_behavioral/results/self_vs_observer_v1/summary.json"
VERIFY = ROOT / "parallel_frontier/20_preference_foresight/results/ranking_v2/verification.json"
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
         paragraph("Task pairs", st["table_head"]),
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

    ordered = sorted(rows, key=lambda r: r["realized_change"])
    step = (height - top - bottom) / len(ordered)
    for i, row in enumerate(ordered):
        y = bottom + (i + 0.5) * step
        label = row["pair_id"].replace("_", " ").replace("|", " / ")
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


def footer(canvas, doc):
    canvas.saveState()
    canvas.setTitle("AI Systems Underestimate How Strongly Recent Work Shapes Their Next Choice")
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
    control = read_json(CONTROL)
    verification = read_json(VERIFY)
    if not verification["passed"]:
        raise SystemExit("ranking_v2 verification did not pass")
    qwen_rows = [r for r in qwen["per_observation"] if r["dose"] == 3]
    h = primary["headline"]
    n_under = round(h["fraction_forecast_errors_negative"] * h["n_observations"])
    st = styles()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUT), pagesize=letter, leftMargin=0.67 * inch,
        rightMargin=0.67 * inch, topMargin=0.62 * inch, bottomMargin=0.58 * inch,
        title="AI Systems Underestimate How Strongly Recent Work Shapes Their Next Choice",
        author="Skye Nygaard",
    )
    story = []

    story += [
        Spacer(1, 0.18 * inch),
        paragraph("AI SYSTEMS UNDERESTIMATE HOW STRONGLY<br/>"
                  "RECENT WORK SHAPES THEIR NEXT CHOICE", st["title"]),
        paragraph("A behavioral study of preference foresight in two assistant systems",
                  st["subtitle"]),
        paragraph("Skye Nygaard", st["body"]),
        Spacer(1, 0.12 * inch),
        Table([[paragraph(
            "<b>Main finding.</b> The tested systems predicted some repetition, but "
            "much less than occurred. Every reported forecast underestimated the "
            "observed shift.", st["callout"]) ]], colWidths=[6.05 * inch],
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
        paragraph("Result at a glance", st["h1"]),
        result_table(primary, qwen_rows, st),
        Spacer(1, 0.16 * inch),
        paragraph(
            "The primary result uses a shuffled, balanced grid. The local Qwen3-4B "
            "replication uses seven nearly complete dose-three task pairs. Every "
            "reported pair in both systems shifted toward recent work, and every "
            "forecast was smaller than the observed shift.", st["body"]),
        paragraph(
            "These are measurements of choices and forecasts. They are not evidence "
            "about consciousness, feelings, or welfare.", st["small"]),
        PageBreak(),
    ]

    story += [
        paragraph("1. Research question", st["h1"]),
        paragraph(
            "Can an AI system predict how recent work will change its own next choice? "
            "This is a narrow test of behavioral self-knowledge. The forecast is made "
            "before the system completes the work, so the answer cannot be copied from "
            "a visible transcript.", st["body"]),
        paragraph("2. Method", st["h1"]),
        paragraph("<b>Step 1: establish a preference.</b> The system made repeated, "
                  "binding choices between two small tasks. Labels and display order "
                  "were balanced. Only stable pairs entered the experiment.", st["body"]),
        paragraph("<b>Step 2: ask for a forecast.</b> Before any treatment work, the "
                  "system estimated how likely it would be to keep its preferred task "
                  "after completing either task three times.", st["body"]),
        paragraph("<b>Step 3: do the work.</b> The system completed one task three times. "
                  "The tasks were generated from recorded seeds and graded automatically.",
                  st["body"]),
        paragraph("<b>Step 4: measure the next choice.</b> The system made another "
                  "binding choice. It then completed the task it selected.", st["body"]),
        Spacer(1, 0.08 * inch),
        Table([[paragraph(
            "<b>Realized shift</b> = P(choose preferred after performing preferred) "
            "- P(choose preferred after performing other)<br/><br/>"
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
            "The clarification run shuffled all cells with a fixed seed. It records "
            "replicate IDs, cell seeds, raw replies, model name, reasoning setting, "
            "CLI version, isolation flags, and the system prompt.", st["body"]),
        paragraph(
            "The Codex route is an agent harness, not a bare model endpoint. It adds "
            "agent instructions and turns the message history into a role-marked "
            "transcript. The report names the tested system accordingly.", st["body"]),
        PageBreak(),
    ]

    permutation_p = h.get("correlation_permutation_p")
    ratio = h.get("model_to_fixed_full_repeat_mse_ratio")
    if ratio is None:
        baseline_text = (
            "A fixed forecast of full repetition matched every observed pair. "
            "The system's own forecasts did not."
        )
    else:
        baseline_text = (
            f"A fixed forecast of full repetition had {ratio:.1f} times lower "
            "squared error than the system's forecasts. This baseline was fixed "
            "without using the clarification run's outcomes."
        )
    if permutation_p is None:
        ranking_text = (
            "Observed shifts did not vary enough for a correlation test. The study "
            "therefore does not make a pair-ranking claim."
        )
    else:
        ranking_text = (
            f"The correlation between forecast and outcome was "
            f"{h['correlation_forecast_vs_realized']:+.2f}. A two-sided permutation "
            f"check gave p = {permutation_p:.2f}. This does not show that the "
            "forecasts contain no information. It shows that this study found no "
            "reliable ranking signal."
        )
    no_shift_reduction = h["model_mse_reduction_vs_no_shift"]
    story += [
        paragraph("3. Primary evidence", st["h1"]),
        pair_chart(primary["per_observation"]),
        Spacer(1, 0.06 * inch),
        paragraph(
            f"The average forecast was {h['mean_predicted_change']:+.3f}. The average "
            f"observed shift was {h['mean_realized_change']:+.3f}. "
            f"{n_under} of {h['n_observations']} forecasts underestimated the "
            "observed shift.",
            st["body"]),
        paragraph(
            f"This is partial foresight. Eleven of 13 forecasts had the correct "
            f"positive direction; two predicted zero. The forecasts captured "
            f"{h['mean_predicted_change'] / h['mean_realized_change']:.0%} of the mean "
            f"observed shift and reduced squared error by {no_shift_reduction:.0%} "
            "relative to a fixed no-shift forecast.", st["body"]),
        paragraph(baseline_text, st["body"]),
        paragraph("Pair ranking remains uncertain", st["h2"]),
        paragraph(ranking_text, st["body"]),
        paragraph("Checks", st["h2"]),
        paragraph(
            f"All three treatment tasks were correct in "
            f"{primary['treatment_accuracy']:.1%} of cells. Post-choice task accuracy "
            f"was {primary['post_task_accuracy']:.1%}. The realized "
            "shift was positive in every label and order block. The saved grid and "
            "summary passed offline verification.", st["body"]),
        paragraph(
            "Six of seven checks set before the run passed. The failed check required "
            "mean forecast error at or below -0.50; the result was -0.487. The report "
            "therefore makes the narrower underestimation claim.", st["body"]),
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
        paragraph("4. Replication and control", st["h1"]),
        paragraph("Local Qwen3-4B replication", st["h2"]),
        paragraph(
            f"The local model predicted a mean shift of {q_pred:+.3f}. The observed "
            f"shift was {q_real:+.3f} across seven dose-three task pairs. After the "
            "preferred task, it chose that task again in 28 of 28 usable cells. After "
            "the other task, it retained the original preference in 0 of 27 cells.",
            st["body"]),
        paragraph(
            "The local route used greedy decoding and no agent wrapper. One of 56 "
            "planned dose-three cells was unusable. We report this nearly complete "
            "subset because several dose-one groups had more missing choices.",
            st["body"]),
        paragraph("Supporting retrospective control", st["h2"]),
        paragraph(
            f"When a model could see the record of recent work, its next-choice "
            f"prediction was {control['self_accuracy']:.1%} accurate. An observer "
            f"prompt scored {control['observer_accuracy']:.1%}. A fixed repeat "
            f"baseline also scored {control['always_repeat_baseline_accuracy']:.1%}. "
            "A visible record therefore made next-choice prediction easy. Estimating "
            "the size of the effect before the work was harder.", st["body"]),
        paragraph(
            "This control saved cell outcomes but not the full provider settings or "
            "raw replies now recorded by the primary run. It is supporting evidence.",
            st["small"]),
        paragraph("5. Limits", st["h1"]),
        paragraph(
            "Two instruction-tuned systems were tested. The tasks were small and "
            "deterministic. Most effects were near the maximum. Task pairs shared "
            "families, so pair-level observations were dependent. Codex sampling was "
            "not seeded. The study does not support claims about all models or about "
            "subjective experience.", st["body"]),
        paragraph("6. Reproducibility", st["h1"]),
        paragraph(
            "The primary clarification artifact contains the protocol, raw replies, "
            "cell-level choices, analysis, model settings, and validation checks. "
            "Run <font name='Courier'>"
            "pytest -q</font>, <font name='Courier'>validate_research_os_frontier.py"
            "</font>, <font name='Courier'>winner_protocol/preflight.py</font>, and "
            "<font name='Courier'>scripts/verify_ranking.py</font> before any model "
            "run.", st["body"]),
        paragraph(
            "The run used an intermediate uncommitted runner revision, and its exact "
            "source hash was not captured. The saved grid, seeds, raw replies, and "
            "reported metrics passed offline verification.", st["small"]),
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
