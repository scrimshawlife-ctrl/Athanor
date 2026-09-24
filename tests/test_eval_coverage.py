from athanor.eval_coverage import compute_coverage

def test_eval_coverage_flags_unsupported_family():
    families = {"iching_daoist": 48, "enochian": 34}
    report = compute_coverage(families, min_support=50)
    assert report["status"] == "INCOMPLETE"
    assert "iching_daoist" in report["unsupported"]
