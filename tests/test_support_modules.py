"""Focused validation for supplementary heuristic and monitoring modules."""
import pytest

from agents.monitoring_dashboard import MonitoringDashboard, AlertSeverity
from agents.predictive_analytics import PredictiveAnalyticsEngine


def test_negative_threshold_alert_severity_and_history_bounds():
    dashboard = MonitoringDashboard()
    dashboard.record_metric("docking_score", -4.9)
    assert dashboard.alerts[-1].severity == AlertSeverity.WARNING
    dashboard.record_metric("docking_score", 0.0)
    assert dashboard.alerts[-1].severity == AlertSeverity.CRITICAL
    assert dashboard.get_metric_history("docking_score", limit=0) == []


def test_predictive_placeholders_cannot_report_fake_validation():
    engine = PredictiveAnalyticsEngine()
    assert engine.models["binding_affinity_predictor"]["trained"] is False
    result = engine.predict("binding_affinity_predictor", {"molecular_weight": 100.0})
    assert result.predicted_outcome
    with pytest.raises(NotImplementedError):
        engine.validate_model("binding_affinity_predictor", [])
    with pytest.raises(NotImplementedError):
        engine.assess_clinical_utility("binding_affinity_predictor")


def test_extreme_heuristic_inputs_do_not_overflow_sigmoid():
    engine = PredictiveAnalyticsEngine()
    a = engine.predict("binding_affinity_predictor", {"molecular_weight": -1e300})
    b = engine.predict("admet_toxicity_classifier", {"mw": -1e300})
    assert a.probability == 0.0
    assert b.probability == 0.0
