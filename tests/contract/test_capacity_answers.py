"""Coldline — Task 1.5.

===================

File:              tests/contract/test_capacity_answers.py
Component:         Contract — Capacity answers
Purpose:           Check submitted capacity-math answers against the shipped fixture, with
                    tolerance.
Interacts With:    submission.yaml, docs/student/task-1-4-reference-metrics.yaml
Sprint/Task:       Sprint 1 — Project 1 / Task 1.5
Concepts:          Tolerance-based automated grading
Tools:             Python 3.12, pytest, PyYAML
"""

import re
from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.runtime

TOLERANCE = 0.05


def _load_submission() -> dict:
    with Path("submission.yaml").open() as handle:
        return yaml.safe_load(handle)


def _load_fixture() -> dict:
    with Path("docs/student/task-1-4-reference-metrics.yaml").open() as handle:
        return yaml.safe_load(handle)


def _contains_number_within_tolerance(text: str, target: float, tolerance: float) -> bool:
    """Return True if a number in text falls within the tolerance band around target.

    A correct answer also states the duration and arrival-rate inputs it started from, and
    usually ends with the margin-rounded worker count - so the raw calculated value the fixture
    checks for is rarely the first or the last number in the string. Accepting a match anywhere
    avoids penalizing a correctly-computed answer for showing its work.
    """
    lower = target * (1 - tolerance)
    upper = target * (1 + tolerance)
    numbers = re.findall(r"[-+]?\d*\.?\d+", text)
    assert numbers, f"no number found in answer text: {text!r}"
    return any(lower <= float(match) <= upper for match in numbers)


def test_worker_count_calculation_within_tolerance() -> None:
    """The submitted worker count must fall within tolerance of the fixture-derived value."""
    submission = _load_submission()
    fixture = _load_fixture()

    duration = fixture["worker_task_duration_seconds"]
    arrival = fixture["peak_exception_arrival_at_10x_jobs_per_sec"]
    expected_workers = (duration * arrival) * 1.3  # 30% safety margin, per the lesson

    answer_text = submission["answers"]["worker_count_calc"]
    assert _contains_number_within_tolerance(answer_text, expected_workers, TOLERANCE), (
        f"worker_count_calc does not contain a number within +/-{TOLERANCE:.0%} of the expected "
        f"{expected_workers:.2f} (duration={duration} x arrival={arrival} x 1.3): {answer_text!r}"
    )
