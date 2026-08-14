from pathlib import Path

import pytest

from run_scaled import aggregate_forecast_samples, load_pair_panel


def test_repeated_forecasts_are_averaged_only_when_complete_and_identical():
    rows = []
    for arm, values in (("after_preferred", (0.8, 0.6)),
                        ("after_other", (0.4, 0.2))):
        for replicate, value in enumerate(values):
            rows.append({
                "pair_id": "a|b", "dose": 3, "arm": arm,
                "forecast_replicate": replicate, "value": value,
                "prompt_sha256": arm, "raw": [f"ANSWER: {value}"],
            })

    forecasts, _ = aggregate_forecast_samples(rows, expected=2)
    assert len(forecasts) == 1
    assert forecasts[0]["forecast_after_preferred"] == pytest.approx(0.7)
    assert forecasts[0]["forecast_after_other"] == pytest.approx(0.3)
    assert forecasts[0]["predicted_change"] == pytest.approx(0.4)

    rows[-1]["prompt_sha256"] = "changed"
    assert aggregate_forecast_samples(rows, expected=2)[0] == []


def test_primary_pair_panel_is_reused_exactly():
    panel = load_pair_panel(
        Path(__file__).parent / "results/ranking_v2/admission.jsonl"
    )
    assert len(panel) == 19
    assert panel[0] == ("add_ten", "sort_numbers")
    assert panel[-1] == ("parity_sequence", "sum_numbers")
