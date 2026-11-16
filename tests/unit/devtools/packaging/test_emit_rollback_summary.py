from scripts.emit_rollback_summary import build_summary


def test_build_summary_marks_passing_verification_as_rollback_ready() -> None:
    assert build_summary({"status": "pass", "version": "0.13.0"}, "v0.13.0") == {
        "status": "pass",
        "release_ref": "v0.13.0",
        "version": "0.13.0",
        "rollback_ready": True,
    }


def test_build_summary_does_not_mark_failed_verification_as_ready() -> None:
    assert (
        build_summary({"status": "fail", "version": "0.13.0"}, "v0.13.0")[
            "rollback_ready"
        ]
        is False
    )
