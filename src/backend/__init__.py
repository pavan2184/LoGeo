"""
Backend package for Geo-Compliance Detection System

This package contains all the core backend modules for the geo-compliance detection system,
including decision engines, classifiers, and supporting utilities.
"""

# Package version
__version__ = "1.0.0"

# Re-export from submodules for backward compatibility
try:
    from src.backend.compliance.enhanced_decision_engine import EnhancedDecisionEngine
    from src.backend.core.llm_classifier import LLMClassifier, get_classifier, RegulatoryAnalysisResult
    from src.backend.core.enhanced_classifier import EnhancedClassifier, get_enhanced_classifier, EnhancedClassificationResult
    from src.backend.knowledge.rag_loader import RegulationRAG, get_rag_instance
    from src.backend.compliance.geo_compliance import GeoComplianceEngine, get_geo_engine
    from src.backend.infrastructure.supabase_client import get_supabase_client
    from src.backend.infrastructure.feedback_system import get_feedback_processor, FeedbackType, InterventionPriority
    from src.backend.core.preprocessing import get_preprocessor
    from src.backend.core.confidence_scoring import ConfidenceScorer
    from src.backend.knowledge.glossary import get_glossary
    from src.backend.compliance.ambiguity_handler import get_ambiguity_handler
except ImportError:
    # Handle import errors gracefully during development
    pass
