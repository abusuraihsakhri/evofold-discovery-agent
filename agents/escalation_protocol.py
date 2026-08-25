"""
Automated Escalation Protocol for EvoFold-Discovery-Agent.
Rule-based escalation engine with role-appropriate notifications and response time tracking.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum
import json


class EscalationLevel(str, Enum):
    LEVEL_1 = "L1_ANALYST"
    LEVEL_2 = "L2_SENIOR_SCIENTIST"
    LEVEL_3 = "L3_PRINCIPAL_INVESTIGATOR"
    LEVEL_4 = "L4_HEAD_OF_DISCOVERY"


class NotificationMethod(str, Enum):
    EMAIL = "EMAIL"
    WEBHOOK = "WEBHOOK"
    DASHBOARD = "DASHBOARD"
    PAGER = "PAGER"


@dataclass
class EscalationRule:
    """Rule defining when and how to escalate."""
    rule_id: str
    name: str
    condition: str  # human-readable condition
    severity_threshold: str  # "WARNING", "CRITICAL"
    initial_level: EscalationLevel
    timeout_minutes: int  # escalate if no response within this time
    notification_methods: List[NotificationMethod]
    active: bool = True


@dataclass
class EscalationEvent:
    """Tracks an escalation event through its lifecycle."""
    event_id: str
    rule_id: str
    alert_id: str
    current_level: EscalationLevel
    created_at: str
    last_escalated_at: Optional[str] = None
    resolved_at: Optional[str] = None
    acknowledged_by: Optional[str] = None
    escalation_count: int = 0
    response_times: List[float] = field(default_factory=list)


@dataclass
class EscalationNotification:
    """Notification to be sent for an escalation."""
    notification_id: str
    event_id: str
    level: EscalationLevel
    method: NotificationMethod
    recipient: str
    message: str
    sent_at: str
    acknowledged: bool = False


class EscalationProtocolEngine:
    """
    Rule-based escalation engine that manages alert lifecycle from initial
    notification through multi-tier escalation with response time tracking.
    """

    LEVEL_ORDER = [
        EscalationLevel.LEVEL_1,
        EscalationLevel.LEVEL_2,
        EscalationLevel.LEVEL_3,
        EscalationLevel.LEVEL_4,
    ]

    DEFAULT_ROLES = {
        EscalationLevel.LEVEL_1: {"title": "Research Analyst", "timeout_min": 15},
        EscalationLevel.LEVEL_2: {"title": "Senior Scientist", "timeout_min": 30},
        EscalationLevel.LEVEL_3: {"title": "Principal Investigator", "timeout_min": 60},
        EscalationLevel.LEVEL_4: {"title": "Head of Discovery", "timeout_min": 120},
    }

    def __init__(self):
        self.rules: Dict[str, EscalationRule] = {}
        self.active_events: Dict[str, EscalationEvent] = {}
        self.notifications: List[EscalationNotification] = []
        self.event_counter = 0
        self.notif_counter = 0
        self._setup_default_rules()

    def _setup_default_rules(self):
        """Initialize default escalation rules for drug discovery pipeline."""
        self.add_rule(EscalationRule(
            rule_id="RULE-001",
            name="Low Folding Confidence",
            condition="folding_confidence < 0.5",
            severity_threshold="WARNING",
            initial_level=EscalationLevel.LEVEL_1,
            timeout_minutes=15,
            notification_methods=[NotificationMethod.DASHBOARD, NotificationMethod.EMAIL],
        ))
        self.add_rule(EscalationRule(
            rule_id="RULE-002",
            name="Failed Docking Campaign",
            condition="docking_success_rate < 0.1",
            severity_threshold="CRITICAL",
            initial_level=EscalationLevel.LEVEL_2,
            timeout_minutes=10,
            notification_methods=[NotificationMethod.EMAIL, NotificationMethod.WEBHOOK],
        ))
        self.add_rule(EscalationRule(
            rule_id="RULE-003",
            name="ADMET Safety Flag",
            condition="herg_inhibition > 0.5 OR hepatotoxicity_risk > 0.7",
            severity_threshold="CRITICAL",
            initial_level=EscalationLevel.LEVEL_2,
            timeout_minutes=10,
            notification_methods=[NotificationMethod.EMAIL, NotificationMethod.PAGER],
        ))
        self.add_rule(EscalationRule(
            rule_id="RULE-004",
            name="Pipeline Throughput Drop",
            condition="throughput < 5 molecules/hr for 30 min",
            severity_threshold="WARNING",
            initial_level=EscalationLevel.LEVEL_1,
            timeout_minutes=30,
            notification_methods=[NotificationMethod.DASHBOARD],
        ))

    def add_rule(self, rule: EscalationRule):
        """Add an escalation rule."""
        self.rules[rule.rule_id] = rule

    def trigger_escalation(self, alert_id: str, rule_id: str,
                           details: str = "") -> Optional[EscalationEvent]:
        """Trigger a new escalation event based on a rule."""
        rule = self.rules.get(rule_id)
        if not rule or not rule.active:
            return None

        self.event_counter += 1
        event = EscalationEvent(
            event_id=f"ESC-{self.event_counter:06d}",
            rule_id=rule_id,
            alert_id=alert_id,
            current_level=rule.initial_level,
            created_at=datetime.utcnow().isoformat(),
        )
        self.active_events[event.event_id] = event

        # Send initial notifications
        self._send_notifications(event, rule, details)
        return event

    def _send_notifications(self, event: EscalationEvent, rule: EscalationRule,
                            details: str = ""):
        """Send notifications for current escalation level."""
        role_info = self.DEFAULT_ROLES.get(event.current_level, {})
        for method in rule.notification_methods:
            self.notif_counter += 1
            notification = EscalationNotification(
                notification_id=f"NOTIF-{self.notif_counter:06d}",
                event_id=event.event_id,
                level=event.current_level,
                method=method,
                recipient=role_info.get("title", "Unknown"),
                message=f"[{rule.name}] Alert {event.alert_id}: {details}",
                sent_at=datetime.utcnow().isoformat(),
            )
            self.notifications.append(notification)

    def check_timeouts(self) -> List[EscalationEvent]:
        """Check for events that have timed out and need escalation."""
        escalated = []
        now = datetime.utcnow()

        for event_id, event in list(self.active_events.items()):
            if event.resolved_at or event.acknowledged_by:
                continue

            rule = self.rules.get(event.rule_id)
            if not rule:
                continue

            last_time_str = event.last_escalated_at or event.created_at
            last_time = datetime.fromisoformat(last_time_str)
            elapsed = (now - last_time).total_seconds() / 60

            if elapsed >= rule.timeout_minutes:
                next_level = self._get_next_level(event.current_level)
                if next_level:
                    event.current_level = next_level
                    event.escalation_count += 1
                    event.last_escalated_at = now.isoformat()
                    event.response_times.append(elapsed)
                    self._send_notifications(event, rule, f"Escalated to {next_level.value}")
                    escalated.append(event)
                else:
                    # Already at max level
                    event.response_times.append(elapsed)

        return escalated

    def _get_next_level(self, current: EscalationLevel) -> Optional[EscalationLevel]:
        """Get the next escalation level."""
        try:
            idx = self.LEVEL_ORDER.index(current)
            if idx + 1 < len(self.LEVEL_ORDER):
                return self.LEVEL_ORDER[idx + 1]
        except ValueError:
            pass
        return None

    def acknowledge_event(self, event_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an escalation event."""
        event = self.active_events.get(event_id)
        if event and not event.acknowledged_by:
            event.acknowledged_by = acknowledged_by
            return True
        return False

    def resolve_event(self, event_id: str) -> bool:
        """Resolve an escalation event."""
        event = self.active_events.get(event_id)
        if event and not event.resolved_at:
            event.resolved_at = datetime.utcnow().isoformat()
            return True
        return False

    def get_escalation_metrics(self) -> dict:
        """Compute escalation performance metrics."""
        all_events = list(self.active_events.values())
        resolved = [e for e in all_events if e.resolved_at]
        active = [e for e in all_events if not e.resolved_at]

        avg_response_times = []
        for event in resolved:
            if event.response_times:
                avg_response_times.append(sum(event.response_times) / len(event.response_times))

        return {
            "total_events": len(all_events),
            "active_events": len(active),
            "resolved_events": len(resolved),
            "avg_response_time_min": round(sum(avg_response_times) / len(avg_response_times), 1) if avg_response_times else 0,
            "max_escalation_level": max((e.escalation_count for e in all_events), default=0),
            "notifications_sent": len(self.notifications),
        }

    def export_metrics_json(self) -> str:
        """Export escalation metrics as JSON."""
        return json.dumps(self.get_escalation_metrics(), indent=2)
