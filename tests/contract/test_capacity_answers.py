"""Coldline.

===================

File:              tests/contract/test_capacity_answers.py
Component:         Capacity calculation contract
Purpose:           Verify structured inputs and published calculation rules.
Interacts With:    submission.yaml and the supplied evidence pack
Sprint/Task:       Sprint 1 - Project 1 / Task 1.5
Concepts:          Units, arithmetic, margin and rounding
Tools:             Python 3.12, pytest

Public calculation structure; protected assessment checks semantic correctness.

Numbers embedded in prose are not calculation evidence. The public schema requires
named input, intermediate, unit and rounding fields without exposing an answer key.
"""

import json
import math
from pathlib import Path

import pytest
import yaml

from tests.contract.submission_validation import validate_submission

pytestmark = pytest.mark.runtime


def test_capacity_calculations_have_explicit_structured_fields() -> None:
    """Reject prose and incomplete calculation fields through the public schema."""
    validate_submission(
        Path("submission.yaml"),
        Path("docs/contracts/submission.schema.json"),
        sample_path=Path("submission-sample.yaml"),
    )


def test_capacity_arithmetic_is_internally_consistent() -> None:
    """Check visible formulas without publishing the protected completed answers."""
    test_capacity_calculations_have_explicit_structured_fields()
    answers = yaml.safe_load(Path("submission.yaml").read_text(encoding="utf-8"))["answers"]
    pack = json.loads(Path("docs/student/evidence-pack.json").read_text(encoding="utf-8"))
    units = pack["planning_inputs"]
    ingestion = answers["ingestion_rate_calc"]
    exceptions = answers["exception_rate_calc"]
    storage = answers["storage_calc"]
    workers = answers["worker_count_calc"]

    def equal(actual: float, expected: float, tolerance: float = 0.001) -> None:
        assert actual == pytest.approx(expected, rel=0, abs=tolerance)

    equal(
        ingestion["projected_readings_per_second"],
        ingestion["baseline_readings_per_second"] * ingestion["growth_factor"],
    )
    equal(
        ingestion["ingestion_bytes_per_second"],
        ingestion["projected_readings_per_second"] * ingestion["payload_bytes_per_reading"],
    )
    equal(
        ingestion["ingestion_mb_per_hour"],
        ingestion["ingestion_bytes_per_second"]
        * units["seconds_per_hour"]
        / units["bytes_per_decimal_mb"],
    )
    equal(exceptions["projected_readings_per_second"], ingestion["projected_readings_per_second"])
    equal(
        exceptions["arrival_jobs_per_second"],
        exceptions["projected_readings_per_second"] * exceptions["exception_fraction"],
    )
    equal(storage["ingestion_bytes_per_second"], ingestion["ingestion_bytes_per_second"])
    equal(storage["seconds_per_day"], units["seconds_per_day"])
    equal(
        storage["retained_bytes"],
        storage["ingestion_bytes_per_second"]
        * storage["seconds_per_day"]
        * storage["retention_days"],
    )
    equal(storage["retained_decimal_gb"], storage["retained_bytes"] / units["bytes_per_decimal_gb"])
    equal(workers["arrival_jobs_per_second"], exceptions["arrival_jobs_per_second"])
    equal(
        workers["unmargined_workers"],
        workers["arrival_jobs_per_second"] * workers["service_seconds_per_job"],
        0.0001,
    )
    equal(workers["margin_fraction"], units["margin_fraction"], 0.000001)
    equal(
        workers["with_margin_workers"],
        workers["unmargined_workers"] * (1 + workers["margin_fraction"]),
        0.0001,
    )
    assert workers["required_workers"] == math.ceil(workers["with_margin_workers"])
