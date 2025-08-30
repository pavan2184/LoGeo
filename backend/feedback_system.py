"""
Self-Evolution Feedback System for Geo-Compliance Classification

This module implements the self-evolution capability through human feedback loops:
1. Human intervention alerts and tracking
2. Feedback collection and processing
3. Glossary updates based on corrections
4. LLM prompt improvement
5. Model performance monitoring
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import os
from enum import Enum

from backend.glossary import get_glossary
from backend.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

class FeedbackType(Enum):
    CLASSIFICATION_CORRECTION = "classification_correction"
    ENTITY_CORRECTION = "entity_correction"
    CONFIDENCE_ADJUSTMENT = "confidence_adjustment"
    NEW_PATTERN = "new_pattern"
    REGULATORY_UPDATE = "regulatory_update"

class InterventionPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class HumanFeedback:
    """Structure for human feedback on classification results"""
    feedback_id: str
    timestamp: str
    reviewer_id: str
    original_classification: Dict[str, Any]
    corrected_classification: Dict[str, Any]
    feedback_type: str
    confidence_correction: Optional[float]
    reasoning: str
    additional_notes: str
    processing_status: str  # "pending", "processed", "applied"

@dataclass
class InterventionAlert:
    """Structure for human intervention alerts"""
    alert_id: str
    timestamp: str
    feature_title: str
    feature_description: str
    classification_result: Dict[str, Any]
    intervention_reason: str
    priority: str
    status: str  # "pending", "under_review", "resolved"
    assigned_reviewer: Optional[str]
    resolution_notes: Optional[str]
    resolved_timestamp: Optional[str]

class FeedbackProcessor:
    """
    Processes human feedback to improve system performance.
    Implements the self-evolution aspect of the feature flow.
    """
    
    def __init__(self):
        self.glossary = get_glossary()
        self.supabase_client = get_supabase_client()
        self.feedback_file = "backend/feedback_data.json"
        self.alerts_file = "backend/intervention_alerts.json"
        self.performance_file = "backend/performance_metrics.json"
        
        # Performance tracking
        self.performance_metrics = {
            "total_classifications": 0,
            "correct_classifications": 0,
            "false_positives": 0,
            "false_negatives": 0,
            "human_interventions": 0,
            "feedback_applied": 0,
            "accuracy_trend": [],
            "confidence_trend": [],
            "last_updated": datetime.now().isoformat()
        }
        
        self._load_performance_metrics()
    
    def create_intervention_alert(self, 
                                feature_title: str,
                                feature_description: str,
                                classification_result: Dict[str, Any],
                                intervention_reason: str,
                                priority: InterventionPriority) -> str:
        """
        Create a human intervention alert for review.
        Returns the alert ID for tracking.
        """
        
        alert_id = f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(feature_title) % 10000}"
        
        alert = InterventionAlert(
            alert_id=alert_id,
            timestamp=datetime.now().isoformat(),
            feature_title=feature_title,
            feature_description=feature_description,
            classification_result=classification_result,
            intervention_reason=intervention_reason,
            priority=priority.value,
            status="pending",
            assigned_reviewer=None,
            resolution_notes=None,
            resolved_timestamp=None
        )
        
        # Save alert
        self._save_alert(alert)
        
        # Log for immediate notification
        logger.warning(f"Human intervention alert created: {alert_id} - Priority: {priority.value} - Reason: {intervention_reason}")
        
        # Update metrics
        self.performance_metrics["human_interventions"] += 1
        self._save_performance_metrics()
        
        return alert_id
    
    def submit_feedback(self,
                       feedback_type: FeedbackType,
                       reviewer_id: str,
                       original_classification: Dict[str, Any],
                       corrections: Dict[str, Any],
                       reasoning: str,
                       additional_notes: str = "") -> str:
        """
        Submit human feedback for processing.
        Returns feedback ID for tracking.
        """
        
        feedback_id = f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(reviewer_id) % 10000}"
        
        # Extract confidence correction if provided
        confidence_correction = None
        if "confidence" in corrections:
            confidence_correction = corrections["confidence"]
        
        feedback = HumanFeedback(
            feedback_id=feedback_id,
            timestamp=datetime.now().isoformat(),
            reviewer_id=reviewer_id,
            original_classification=original_classification,
            corrected_classification=corrections,
            feedback_type=feedback_type.value,
            confidence_correction=confidence_correction,
            reasoning=reasoning,
            additional_notes=additional_notes,
            processing_status="pending"
        )
        
        # Save feedback
        self._save_feedback(feedback)
        
        # Process feedback immediately for critical updates
        if feedback_type in [FeedbackType.CLASSIFICATION_CORRECTION, FeedbackType.ENTITY_CORRECTION]:
            self._process_feedback_immediately(feedback)
        
        logger.info(f"Feedback submitted: {feedback_id} by {reviewer_id}")
        return feedback_id
    
    def _process_feedback_immediately(self, feedback: HumanFeedback):
        """Process critical feedback immediately for system improvement"""
        
        try:
            if feedback.feedback_type == FeedbackType.CLASSIFICATION_CORRECTION.value:
                self._apply_classification_correction(feedback)
            
            elif feedback.feedback_type == FeedbackType.ENTITY_CORRECTION.value:
                self._apply_entity_correction(feedback)
            
            # Update processing status
            feedback.processing_status = "processed"
            self._save_feedback(feedback)
            
            # Update performance metrics
            self.performance_metrics["feedback_applied"] += 1
            self._calculate_accuracy_update(feedback)
            self._save_performance_metrics()
            
            logger.info(f"Feedback processed immediately: {feedback.feedback_id}")
            
        except Exception as e:
            logger.error(f"Failed to process feedback {feedback.feedback_id}: {e}")
            feedback.processing_status = "error"
            self._save_feedback(feedback)
    
    def _apply_classification_correction(self, feedback: HumanFeedback):
        """Apply classification corrections to improve future performance"""
        
        original = feedback.original_classification
        corrected = feedback.corrected_classification
        
        # Extract corrected entities for glossary updates
        if "entities" in corrected:
            for entity_correction in corrected["entities"]:
                if entity_correction.get("type") == "misclassified":
                    # Update glossary with correct mapping
                    self.glossary.update_from_feedback({
                        "type": entity_correction.get("entity_type", "").lower(),
                        "original_text": entity_correction.get("original_text", ""),
                        "correct_mapping": entity_correction.get("correct_form", ""),
                        "confidence": entity_correction.get("confidence", 1.0),
                        "feedback_source": feedback.reviewer_id
                    })
        
        # Log pattern for future improvement
        pattern_data = {
            "feature_text": f"{original.get('title', '')} {original.get('description', '')}",
            "original_classification": original.get("needs_geo_logic"),
            "corrected_classification": corrected.get("needs_geo_logic"),
            "correction_reason": feedback.reasoning,
            "timestamp": feedback.timestamp
        }
        
        self._log_classification_pattern(pattern_data)
    
    def _apply_entity_correction(self, feedback: HumanFeedback):
        """Apply entity extraction corrections to improve glossary"""
        
        corrections = feedback.corrected_classification
        
        # Process entity corrections
        for entity_type in ["location", "age", "terminology"]:
            if entity_type in corrections:
                entity_corrections = corrections[entity_type]
                
                for correction in entity_corrections:
                    self.glossary.update_from_feedback({
                        "type": entity_type,
                        "original_text": correction.get("original_text", ""),
                        "correct_mapping": correction.get("correct_mapping", ""),
                        "confidence": correction.get("confidence", 1.0),
                        "feedback_source": feedback.reviewer_id
                    })
    
    def _calculate_accuracy_update(self, feedback: HumanFeedback):
        """Update accuracy metrics based on feedback"""
        
        original_classification = feedback.original_classification.get("needs_geo_logic")
        corrected_classification = feedback.corrected_classification.get("needs_geo_logic")
        
        self.performance_metrics["total_classifications"] += 1
        
        if original_classification == corrected_classification:
            self.performance_metrics["correct_classifications"] += 1
        else:
            # Determine if it was false positive or false negative
            if original_classification and not corrected_classification:
                self.performance_metrics["false_positives"] += 1
            elif not original_classification and corrected_classification:
                self.performance_metrics["false_negatives"] += 1
        
        # Calculate current accuracy
        total = self.performance_metrics["total_classifications"]
        correct = self.performance_metrics["correct_classifications"]
        current_accuracy = correct / total if total > 0 else 0.0
        
        # Add to trend
        self.performance_metrics["accuracy_trend"].append({
            "timestamp": datetime.now().isoformat(),
            "accuracy": current_accuracy,
            "total_samples": total
        })
        
        # Keep only last 100 data points
        if len(self.performance_metrics["accuracy_trend"]) > 100:
            self.performance_metrics["accuracy_trend"] = self.performance_metrics["accuracy_trend"][-100:]
    
    def _log_classification_pattern(self, pattern_data: Dict[str, Any]):
        """Log classification patterns for future model improvement"""
        
        patterns_file = "backend/classification_patterns.json"
        
        try:
            # Load existing patterns
            patterns = []
            if os.path.exists(patterns_file):
                with open(patterns_file, 'r') as f:
                    patterns = json.load(f)
            
            # Add new pattern
            patterns.append(pattern_data)
            
            # Keep only last 1000 patterns
            if len(patterns) > 1000:
                patterns = patterns[-1000:]
            
            # Save updated patterns
            with open(patterns_file, 'w') as f:
                json.dump(patterns, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to log classification pattern: {e}")
    
    def get_pending_alerts(self, priority_filter: Optional[str] = None) -> List[InterventionAlert]:
        """Get pending intervention alerts, optionally filtered by priority"""
        
        alerts = self._load_alerts()
        pending_alerts = [alert for alert in alerts if alert.status == "pending"]
        
        if priority_filter:
            pending_alerts = [alert for alert in pending_alerts if alert.priority == priority_filter]
        
        # Sort by priority and timestamp
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        pending_alerts.sort(key=lambda x: (priority_order.get(x.priority, 4), x.timestamp))
        
        return pending_alerts
    
    def resolve_alert(self, alert_id: str, reviewer_id: str, resolution_notes: str):
        """Mark an intervention alert as resolved"""
        
        alerts = self._load_alerts()
        
        for alert in alerts:
            if alert.alert_id == alert_id:
                alert.status = "resolved"
                alert.assigned_reviewer = reviewer_id
                alert.resolution_notes = resolution_notes
                alert.resolved_timestamp = datetime.now().isoformat()
                break
        
        self._save_alerts(alerts)
        logger.info(f"Alert resolved: {alert_id} by {reviewer_id}")
    
    def get_performance_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get performance summary for the last N days"""
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Filter recent accuracy trend
        recent_trend = [
            point for point in self.performance_metrics["accuracy_trend"]
            if datetime.fromisoformat(point["timestamp"]) > cutoff_date
        ]
        
        # Calculate recent accuracy
        recent_accuracy = recent_trend[-1]["accuracy"] if recent_trend else 0.0
        
        # Calculate trend direction
        trend_direction = "stable"
        if len(recent_trend) >= 2:
            first_accuracy = recent_trend[0]["accuracy"]
            last_accuracy = recent_trend[-1]["accuracy"]
            
            if last_accuracy > first_accuracy + 0.05:
                trend_direction = "improving"
            elif last_accuracy < first_accuracy - 0.05:
                trend_direction = "declining"
        
        # Get pending alerts summary
        pending_alerts = self.get_pending_alerts()
        alert_summary = {
            "critical": len([a for a in pending_alerts if a.priority == "critical"]),
            "high": len([a for a in pending_alerts if a.priority == "high"]),
            "medium": len([a for a in pending_alerts if a.priority == "medium"]),
            "low": len([a for a in pending_alerts if a.priority == "low"])
        }
        
        return {
            "period_days": days,
            "current_accuracy": recent_accuracy,
            "trend_direction": trend_direction,
            "total_classifications": self.performance_metrics["total_classifications"],
            "total_interventions": self.performance_metrics["human_interventions"],
            "feedback_applied": self.performance_metrics["feedback_applied"],
            "pending_alerts": alert_summary,
            "false_positive_rate": self.performance_metrics["false_positives"] / max(self.performance_metrics["total_classifications"], 1),
            "false_negative_rate": self.performance_metrics["false_negatives"] / max(self.performance_metrics["total_classifications"], 1),
            "last_updated": self.performance_metrics["last_updated"]
        }
    
    def _save_alert(self, alert: InterventionAlert):
        """Save individual alert"""
        alerts = self._load_alerts()
        alerts.append(alert)
        self._save_alerts(alerts)
    
    def _load_alerts(self) -> List[InterventionAlert]:
        """Load all alerts from file"""
        try:
            if os.path.exists(self.alerts_file):
                with open(self.alerts_file, 'r') as f:
                    alerts_data = json.load(f)
                return [InterventionAlert(**alert) for alert in alerts_data]
        except Exception as e:
            logger.error(f"Failed to load alerts: {e}")
        return []
    
    def _save_alerts(self, alerts: List[InterventionAlert]):
        """Save all alerts to file"""
        try:
            alerts_data = [asdict(alert) for alert in alerts]
            with open(self.alerts_file, 'w') as f:
                json.dump(alerts_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save alerts: {e}")
    
    def _save_feedback(self, feedback: HumanFeedback):
        """Save feedback to file"""
        try:
            feedbacks = []
            if os.path.exists(self.feedback_file):
                with open(self.feedback_file, 'r') as f:
                    feedbacks = json.load(f)
            
            # Update existing or add new
            updated = False
            for i, existing in enumerate(feedbacks):
                if existing.get("feedback_id") == feedback.feedback_id:
                    feedbacks[i] = asdict(feedback)
                    updated = True
                    break
            
            if not updated:
                feedbacks.append(asdict(feedback))
            
            with open(self.feedback_file, 'w') as f:
                json.dump(feedbacks, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save feedback: {e}")
    
    def _load_performance_metrics(self):
        """Load performance metrics from file"""
        try:
            if os.path.exists(self.performance_file):
                with open(self.performance_file, 'r') as f:
                    saved_metrics = json.load(f)
                self.performance_metrics.update(saved_metrics)
        except Exception as e:
            logger.error(f"Failed to load performance metrics: {e}")
    
    def _save_performance_metrics(self):
        """Save performance metrics to file"""
        try:
            self.performance_metrics["last_updated"] = datetime.now().isoformat()
            with open(self.performance_file, 'w') as f:
                json.dump(self.performance_metrics, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save performance metrics: {e}")

# Global feedback processor instance
_feedback_processor_instance = None

def get_feedback_processor() -> FeedbackProcessor:
    """Get singleton feedback processor instance"""
    global _feedback_processor_instance
    if _feedback_processor_instance is None:
        _feedback_processor_instance = FeedbackProcessor()
    return _feedback_processor_instance

if __name__ == "__main__":
    # Test the feedback system
    processor = FeedbackProcessor()
    
    # Simulate an intervention alert
    alert_id = processor.create_intervention_alert(
        "Test Feature",
        "Test description",
        {"needs_geo_logic": True, "confidence": 0.6},
        "Low confidence for high-risk category",
        InterventionPriority.HIGH
    )
    
    print(f"Created alert: {alert_id}")
    
    # Get pending alerts
    pending = processor.get_pending_alerts()
    print(f"Pending alerts: {len(pending)}")
    
    # Get performance summary
    summary = processor.get_performance_summary()
    print(f"Performance summary: {json.dumps(summary, indent=2)}")
