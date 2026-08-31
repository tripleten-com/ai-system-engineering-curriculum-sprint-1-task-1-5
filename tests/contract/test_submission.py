"""Coldline — Task 1.5.

===================

File:              tests/contract/test_submission.py
Component:         Contract tests — Test Submission
Purpose:           Tests for the public answer and path checks for this Task's submission.
Interacts With:    Published interfaces and repository boundaries
Sprint/Task:       Sprint 1 — Project 1 / Task 1.5
Concepts:          Compatibility, ownership, export safety
Tools:             Python 3.12, pytest
"""

from pathlib import Path

import pytest
import yaml

from tests.contract.submission_validation import (
    SubmissionError,
    main,
    validate_changed_paths,
    validate_submission,
)

ROOT = Path(__file__).parents[2]


def valid_answers() -> dict[str, object]:
    """Return a complete fictional answer sheet unrelated to Coldline outcomes."""
    return {
        "answers": {
            "claim_audit": (
                "Fictional Claim 1 (Factual): the fictional worker consumes messages from "
                "fictional Redis Streams. Marked Supported after checking the fictional queue "
                "adapter code. Fictional Claim 2 (Calculated): fictional 10x ingestion reaches "
                "18,000,000 fictional MB per hour. Marked Calculation Error: the fictional draft "
                "multiplied fictional bytes per second by fictional seconds per hour without "
                "converting bytes to megabytes first. Fictional Claim 3 (Judgment): migrate to a "
                "fictional multi-region Kubernetes cluster. Marked Unsupported Assumption: the "
                "fictional load test evidence points only to fictional worker concurrency."
            ),
            "ingestion_rate_calc": (
                "At fictional 10x scale, ingestion is 10 fictional readings/sec x 500 fictional "
                "bytes/reading = 5,000 fictional bytes/sec, or 18 fictional MB/hour."
            ),
            "exception_rate_calc": (
                "Fictional baseline exception rate is 5 percent of 2 fictional shipments/sec = "
                "0.1 fictional jobs/sec. At fictional 10x scale, arrival is 1.0 fictional jobs/sec."
            ),
            "worker_count_calc": (
                "Using a fictional worker task duration of 0.35 fictional sec/job and a fictional "
                "peak arrival of 10 fictional jobs/sec: 0.35 x 10 x 1.3 = 4.55 fictional workers, "
                "rounded up to 5 fictional worker processes."
            ),
            "scaling_recommendation": (
                "Scale the fictional exception worker pool from 2 to 5 fictional processes rather "
                "than adopting the fictional draft's fictional multi-region Kubernetes migration, "
                "which is not supported by any fictional measured bottleneck."
            ),
            "adr": (
                "Context: fictional leadership approved a fictional 10x shipment expansion. "
                "Decision: scale the fictional exception worker pool from 2 to 5 fictional "
                "processes. Consequences: fictional infrastructure cost rises modestly. "
                "Alternatives Considered: a fictional multi-region Kubernetes migration was "
                "rejected as unsupported. Action Trigger: scale up when the fictional queue "
                "backlog exceeds 50 fictional messages for 2 fictional minutes. Rollback "
                "Condition: revert if fictional database CPU exceeds 85 percent. Next "
                "Measurement: monitor fictional worker queue backlog after the change."
            ),
        }
    }


def test_complete_answer_shape_passes_public_validation(tmp_path: Path) -> None:
    """A complete direct-answer mapping must pass syntax and schema validation."""
    submission = tmp_path / "submission.yaml"
    submission.write_text(yaml.safe_dump(valid_answers()), encoding="utf-8")

    validate_submission(submission, ROOT / "docs/contracts/submission.schema.json")


def test_blank_template_fails_with_field_address(tmp_path: Path) -> None:
    """An untouched answer sheet must identify an incomplete field."""
    submission = tmp_path / "submission.yaml"
    submission.write_text((ROOT / "submission.yaml").read_text(encoding="utf-8"), encoding="utf-8")

    with pytest.raises(SubmissionError, match="answers.claim_audit"):
        validate_submission(submission, ROOT / "docs/contracts/submission.schema.json")


def test_malformed_yaml_is_rejected(tmp_path: Path) -> None:
    """A syntactically invalid answer sheet must fail safely."""
    submission = tmp_path / "submission.yaml"
    submission.write_text("answers: [unterminated", encoding="utf-8")

    with pytest.raises(SubmissionError, match="valid YAML"):
        validate_submission(submission, ROOT / "docs/contracts/submission.schema.json")


def test_unexpected_answer_field_is_rejected(tmp_path: Path) -> None:
    """Fields outside the published direct-answer schema must fail validation."""
    answers = valid_answers()
    answer_mapping = answers["answers"]
    assert isinstance(answer_mapping, dict)
    answer_mapping["repair_hint"] = "not part of this Task's schema"
    submission = tmp_path / "submission.yaml"
    submission.write_text(yaml.safe_dump(answers), encoding="utf-8")

    with pytest.raises(SubmissionError, match="Additional properties"):
        validate_submission(submission, ROOT / "docs/contracts/submission.schema.json")


def test_exact_sample_copy_is_rejected(tmp_path: Path) -> None:
    """The fictional sample must not be accepted as a student submission."""
    submission = tmp_path / "submission.yaml"
    submission.write_text(
        (ROOT / "submission-sample.yaml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    with pytest.raises(SubmissionError, match="fictional sample"):
        validate_submission(
            submission,
            ROOT / "docs/contracts/submission.schema.json",
            sample_path=ROOT / "submission-sample.yaml",
        )


def test_only_student_editable_paths_are_permitted() -> None:
    """The advisory path gate must accept this Task's editable paths and reject others."""
    validate_changed_paths(["submission.yaml"])

    with pytest.raises(SubmissionError, match="src/api"):
        validate_changed_paths(["src/api/routes.py"])

    with pytest.raises(SubmissionError, match="loadtest"):
        validate_changed_paths(["loadtest/model_provider_latency.py"])


def test_public_entrypoint_reports_an_incomplete_answer_sheet(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Catch a verifier entrypoint that skips the real submission contract."""
    (tmp_path / "docs/contracts").mkdir(parents=True)
    (tmp_path / "submission.yaml").write_text(
        (ROOT / "submission.yaml").read_text(encoding="utf-8"), encoding="utf-8"
    )
    (tmp_path / "submission-sample.yaml").write_text(
        (ROOT / "submission-sample.yaml").read_text(encoding="utf-8"), encoding="utf-8"
    )
    (tmp_path / "docs/contracts/submission.schema.json").write_text(
        (ROOT / "docs/contracts/submission.schema.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    assert main(tmp_path, changed_paths=[]) == 1
    assert "answers.claim_audit is incomplete" in capsys.readouterr().err
