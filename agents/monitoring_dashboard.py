"""
Real-Time Monitoring Dashboard for EvoFold-Discovery-Agent.
Live visualization of key performance indicators with automated alerting for threshold breaches.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import json
import time


class AlertSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass
class KPIMetric:
    """Key Performance Indicator metric."""
    name: str
    value: float
    unit: str
    threshold_min: Optional[float] = None
    threshold_max: Optional[float] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def is_breached(self) -> bool:
        if self.threshold_max is not None and self.value > self.threshold_max:
            return True
        if self.threshold_min is not None and self.value < self.threshold_min:
            return True
        return False


@dataclass
class Alert:
    """Dashboard alert for threshold breach."""
    alert_id: str
    metric_name: str
    severity: AlertSeverity
    message: str
    current_value: float
    threshold_value: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    acknowledged: bool = False


class MonitoringDashboard:
    """
    Real-time monitoring dashboard for drug discovery pipeline KPIs.
    Tracks folding accuracy, docking scores, ADMET compliance, and pipeline throughput.
    """

    # Default KPI thresholds
    DEFAULT_THRESHOLDS = {
        "folding_confidence": {"min": 0.7, "max": None, "unit": "score"},
        "docking_score": {"min": None, "max": -5.0, "unit": "kcal/mol"},
        "lipinski_pass_rate": {"min": 0.6, "max": None, "unit": "ratio"},
        "pipeline_throughput": {"min": 10, "max": None, "unit": "molecules/hr"},
        "admet_bbb_pass": {"min": 0.3, "max": None, "unit": "ratio"},
        "qed_mean": {"min": 0.4, "max": None, "unit": "score"},
    }

    def __init__(self):
        self.metrics_history: Dict[str, List[KPIMetric]] = {}
        self.alerts: List[Alert] = []
        self.alert_counter = 0
        self._subscribers: List[callable] = []

    def record_metric(self, name: str, value: float, unit: str = "",
                      threshold_min: Optional[float] = None,
                      threshold_max: Optional[float] = None) -> KPIMetric:
        """Record a new KPI metric value and check thresholds."""
        thresholds = self.DEFAULT_THRESHOLDS.get(name, {})
        t_min = threshold_min if threshold_min is not None else thresholds.get("min")
        t_max = threshold_max if threshold_max is not None else thresholds.get("max")
        u = unit or thresholds.get("unit", "")

        metric = KPIMetric(name=name, value=value, unit=u,
                           threshold_min=t_min, threshold_max=t_max)

        if name not in self.metrics_history:
            self.metrics_history[name] = []
        self.metrics_history[name].append(metric)

        if metric.is_breached():
            self._generate_alert(metric)

        return metric

    def _generate_alert(self, metric: KPIMetric):
        """Generate an alert for a threshold breach."""
        self.alert_counter += 1
        if metric.threshold_max is not None and metric.value > metric.threshold_max:
            severity = AlertSeverity.CRITICAL if (metric.value - metric.threshold_max) > 0.5 * max(abs(metric.threshold_max), 1e-9) else AlertSeverity.WARNING
            msg = f"{metric.name} = {metric.value} exceeds max threshold {metric.threshold_max}"
            threshold = metric.threshold_max
        else:
            severity = AlertSeverity.WARNING
            msg = f"{metric.name} = {metric.value} below min threshold {metric.threshold_min}"
            threshold = metric.threshold_min

        alert = Alert(
            alert_id=f"ALERT-{self.alert_counter:06d}",
            metric_name=metric.name,
            severity=severity,
            message=msg,
            current_value=metric.value,
            threshold_value=threshold,
        )
        self.alerts.append(alert)
        self._notify_subscribers(alert)

    def _notify_subscribers(self, alert: Alert):
        """Notify all subscribers of new alerts."""
        for callback in self._subscribers:
            try:
                callback(alert)
            except Exception:
                pass

    def subscribe(self, callback: callable):
        """Subscribe to alert notifications."""
        self._subscribers.append(callback)

    def get_dashboard_summary(self) -> dict:
        """Get current dashboard summary with latest KPIs and active alerts."""
        latest_metrics = {}
        for name, history in self.metrics_history.items():
            if history:
                latest = history[-1]
                latest_metrics[name] = {
                    "value": latest.value,
                    "unit": latest.unit,
                    "breached": latest.is_breached(),
                    "trend": self._compute_trend(history),
                }

        active_alerts = [a for a in self.alerts if not a.acknowledged]
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": latest_metrics,
            "active_alert_count": len(active_alerts),
            "alerts": [
                {
                    "id": a.alert_id,
                    "severity": a.severity.value,
                    "message": a.message,
                    "metric": a.metric_name,
                    "timestamp": a.timestamp,
                }
                for a in active_alerts[-10:]
            ],
        }

    def _compute_trend(self, history: List[KPIMetric]) -> str:
        """Compute simple trend direction from recent history."""
        if len(history) < 2:
            return "STABLE"
        recent = history[-5:]
        if len(recent) < 2:
            return "STABLE"
        diffs = [recent[i + 1].value - recent[i].value for i in range(len(recent) - 1)]
        avg_diff = sum(diffs) / len(diffs)
        if avg_diff > 0.01:
            return "RISING"
        elif avg_diff < -0.01:
            return "FALLING"
        return "STABLE"

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert by ID."""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                return True
        return False

    def get_metric_history(self, name: str, limit: int = 100) -> List[dict]:
        """Get historical values for a specific metric."""
        if limit <= 0:
            return []
        history = self.metrics_history.get(name, [])
        return [
            {"value": m.value, "unit": m.unit, "timestamp": m.timestamp, "breached": m.is_breached()}
            for m in history[-limit:]
        ]

    def export_dashboard_json(self) -> str:
        """Export full dashboard state as JSON."""
        return json.dumps(self.get_dashboard_summary(), indent=2, default=str)
