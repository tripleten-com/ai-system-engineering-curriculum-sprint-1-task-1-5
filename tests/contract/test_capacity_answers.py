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
from jsonschema import Draft202012Validator

from tests.contract.submission_validation import _load_one_document, _validate_values

pytestmark = pytest.mark.runtime


def test_capacity_calculations_have_explicit_structured_fields() -> None:
    """Validate Step 2 independently; final `answers` still checks the whole sheet."""
    validate_calculation_fields(Path("submission.yaml"))


def validate_calculation_fields(submission: Path) -> None:
    """Use the same field schemas without requiring answers from later steps."""
    data = _load_one_document(submission)
    schema = json.loads(Path("docs/contracts/submission.schema.json").read_text())
    fields = ("ingestion_rate_calc", "exception_rate_calc", "storage_calc", "worker_count_calc")
    answers = data.get("answers", {})
    selected = {name: answers.get(name) for name in fields}
    _validate_values(selected, "answers")
    focused = {
        **schema,
        "type": "object",
        "properties": {
            name: schema["properties"]["answers"]["properties"][name] for name in fields
        },
        "required": list(fields),
        "additionalProperties": False,
    }
    Draft202012Validator(focused).validate(selected)


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
