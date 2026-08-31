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


def _first_number(text: str) -> float:
    match = re.search(r"[-+]?\d*\.?\d+", text)
    assert match, f"no number found in answer text: {text!r}"
    return float(match.group())


def test_worker_count_calculation_within_tolerance() -> None:
    """The submitted worker count must fall within tolerance of the fixture-derived value."""
    submission = _load_submission()
    fixture = _load_fixture()

    duration = fixture["worker_task_duration_seconds"]
    arrival = fixture["peak_exception_arrival_at_10x_jobs_per_sec"]
    expected_workers = (duration * arrival) * 1.3  # 30% safety margin, per the lesson

    submitted = _first_number(submission["answers"]["worker_count_calc"])
    lower = expected_workers * (1 - TOLERANCE)
    upper = expected_workers * (1 + TOLERANCE)
    assert lower <= submitted <= upper, (
        f"worker_count_calc={submitted} is outside the ±{TOLERANCE:.0%} tolerance band around "
        f"the expected {expected_workers:.2f} (duration={duration} x arrival={arrival} x 1.3)"
    )
