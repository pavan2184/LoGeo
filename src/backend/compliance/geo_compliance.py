"""
Geo-compliance logic for access control based on geographic rules.
"""

from typing import Dict, List, Tuple, Any
from src.backend.infrastructure.supabase_client import get_supabase_client
import logging

logger = logging.getLogger(__name__)

class GeoComplianceEngine:
    """Core engine for geo-compliance access control."""
    
    def __init__(self):
        """Initialize the geo-compliance engine."""
        self.supabase_client = get_supabase_client()
    
    async def check_access(
        self, 
        user_id: str, 
        feature_name: str, 
        country: str
    ) -> Tuple[bool, str]:
        """
        Check if access should be granted based on geo-compliance rules.
        
        Args:
            user_id: ID of the user requesting access
            feature_name: Name of the feature being accessed
            country: Country code of the user (e.g., 'US', 'EU', 'CA')
            
        Returns:
            Tuple of (access_granted, reason)
        """
        try:
            # Get geo rule for the feature
            geo_rule = await self.supabase_client.get_geo_rule(feature_name)
            
            if not geo_rule:
                # No rule found - default to deny access for security
                reason = f"No geo-compliance rule found for feature '{feature_name}'. Access denied by default."
                await self.supabase_client.log_access_attempt(user_id, feature_name, country, False)
                return False, reason
            
            allowed_countries = geo_rule.get("allowed_countries", [])
            blocked_countries = geo_rule.get("blocked_countries", [])
            
            # Check blocked countries first (highest priority)
            if country in blocked_countries:
                reason = f"Access denied: '{country}' is explicitly blocked for feature '{feature_name}'"
                await self.supabase_client.log_access_attempt(user_id, feature_name, country, False)
                return False, reason
            
            # Check allowed countries
            if allowed_countries and country in allowed_countries:
                reason = f"Access granted: '{country}' is allowed for feature '{feature_name}'"
                await self.supabase_client.log_access_attempt(user_id, feature_name, country, True)
                return True, reason
            
            # If allowed_countries list exists but country not in it, deny
            if allowed_countries:
                reason = f"Access denied: '{country}' is not in the allowed countries list for feature '{feature_name}'"
                await self.supabase_client.log_access_attempt(user_id, feature_name, country, False)
                return False, reason
            
            # No allowed_countries specified and not in blocked list - grant access
            reason = f"Access granted: No geographic restrictions for feature '{feature_name}'"
            await self.supabase_client.log_access_attempt(user_id, feature_name, country, True)
            return True, reason
            
        except Exception as e:
            logger.error(f"Error checking access for user {user_id}, feature {feature_name}: {e}")
            reason = f"Error checking geo-compliance rules: {str(e)}"
            await self.supabase_client.log_access_attempt(user_id, feature_name, country, False)
            return False, reason
    
    async def batch_check_access(
        self, 
        requests: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Check access for multiple requests in batch.
        
        Args:
            requests: List of dicts with keys: user_id, feature_name, country
            
        Returns:
            List of results with access_granted and reason for each request
        """
        results = []
        
        for request in requests:
            user_id = request.get("user_id")
            feature_name = request.get("feature_name")  
            country = request.get("country")
            
            if not all([user_id, feature_name, country]):
                result = {
                    "user_id": user_id,
                    "feature_name": feature_name,
                    "country": country,
                    "access_granted": False,
                    "reason": "Missing required fields: user_id, feature_name, or country"
                }
            else:
                access_granted, reason = await self.check_access(user_id, feature_name, country)
                result = {
                    "user_id": user_id,
                    "feature_name": feature_name,
                    "country": country,
                    "access_granted": access_granted,
                    "reason": reason
                }
            
            results.append(result)
        
        return results
    
    async def get_feature_rules(self) -> List[Dict[str, Any]]:
        """
        Get all geo-compliance rules.
        
        Returns:
            List of all geo rules in the system
        """
        try:
            if not self.supabase_client.is_connected():
                return []
            
            # This would need to be implemented in the supabase_client
            # For now, return empty list
            return []
            
        except Exception as e:
            logger.error(f"Error fetching feature rules: {e}")
            return []

# Default mock rules for testing when Supabase is not available
MOCK_GEO_RULES = {
    # MINOR PROTECTION FEATURES - High compliance risk
    "Curfew login blocker with ASL and GH for Utah minors": {
        "allowed_countries": ["UT"],  # Utah-specific law
        "blocked_countries": [],
        "compliance_note": "Utah Social Media Regulation Act - minors only"
    },
    "PF default toggle with NR enforcement for California teens": {
        "allowed_countries": ["CA"],  # California SB976
        "blocked_countries": [],
        "compliance_note": "California SB976 - teen personalization restrictions"
    },
    "Jellybean-based parental notifications for Florida regulation": {
        "allowed_countries": ["FL"],  # Florida's Online Protections for Minors law
        "blocked_countries": [],
        "compliance_note": "Florida Online Protections for Minors law"
    },
    "Age-specific notification controls with ASL": {
        "allowed_countries": ["US", "CA", "EU"],  # COPPA, GDPR age requirements
        "blocked_countries": ["CN", "RU"],  # Countries with restrictive policies
        "compliance_note": "Age verification required - COPPA/GDPR compliance"
    },
    "Minor-safe chat expansion via Jellybean": {
        "allowed_countries": ["US", "CA", "EU", "UK"],
        "blocked_countries": ["CN", "IN"],  # Countries with chat restrictions
        "compliance_note": "Minor protection chat features"
    },
    "Custom avatar system with identity checks": {
        "allowed_countries": ["US", "CA", "EU", "UK", "AU"],
        "blocked_countries": ["CN", "TR"],  # Countries with content restrictions
        "compliance_note": "Age verification for adult content blocking"
    },
    
    # CONTENT SAFETY & ABUSE PREVENTION
    "Child abuse content scanner using T5 and CDS triggers": {
        "allowed_countries": ["US"],  # US federal NCMEC requirement
        "blocked_countries": [],
        "compliance_note": "US NCMEC reporting requirement - federal law"
    },
    "Content visibility lock with NSP for EU DSA": {
        "allowed_countries": ["EU", "DE", "FR", "IT", "ES", "NL"],  # EU DSA countries
        "blocked_countries": [],
        "compliance_note": "EU Digital Services Act Article 16 compliance"
    },
    
    # DATA PRIVACY & TRACKING
    "Creator fund payout tracking in CDS": {
        "allowed_countries": ["US", "CA", "UK", "AU"],  # Non-GDPR countries for easier processing
        "blocked_countries": ["EU", "DE", "FR"],  # GDPR data localization restrictions
        "compliance_note": "GDPR data localization requirements"
    },
    "Unified retention control via DRT & CDS": {
        "allowed_countries": [],  # Universal feature
        "blocked_countries": ["CN", "RU", "IR"],  # Countries with data retention restrictions
        "compliance_note": "Regional data retention laws vary"
    },
    
    # REGIONAL TESTING FEATURES
    "Trial run of video replies in EU": {
        "allowed_countries": ["EU", "DE", "FR", "IT", "ES", "NL", "BE"],  # EEA only
        "blocked_countries": [],
        "compliance_note": "EU-only feature rollout"
    },
    "Regional trial of autoplay behavior": {
        "allowed_countries": ["US"],  # US-only testing
        "blocked_countries": [],
        "compliance_note": "US-only A/B testing"
    },
    "South Korea dark theme A/B experiment": {
        "allowed_countries": ["KR"],  # South Korea only
        "blocked_countries": [],
        "compliance_note": "South Korea accessibility testing"
    },
    "Canada-first PF variant test": {
        "allowed_countries": ["CA"],  # Canada only
        "blocked_countries": [],
        "compliance_note": "Canada-specific feature testing"
    },
    "Chat UI overhaul": {
        "allowed_countries": ["CA", "US", "BR", "ID"],  # Multi-region testing
        "blocked_countries": ["EU"],  # GDPR UI consent complications
        "compliance_note": "Multi-region UI testing - GDPR excluded"
    },
    
    # LOW-RISK FEATURES (No geographic restrictions)
    "Universal PF deactivation on guest mode": {
        "allowed_countries": [],  # Universal feature
        "blocked_countries": [],
        "compliance_note": "No geographic restrictions"
    },
    "Story resharing with content expiry": {
        "allowed_countries": [],  # Universal feature  
        "blocked_countries": ["CN"],  # Content sharing restrictions
        "compliance_note": "Content sharing restrictions in some regions"
    },
    "Leaderboard system for weekly creators": {
        "allowed_countries": [],  # Universal feature
        "blocked_countries": [],
        "compliance_note": "No geographic restrictions"
    },
    
    # LEGACY RULES FOR TESTING
    "user_registration": {
        "allowed_countries": ["US", "CA", "UK", "AU"],
        "blocked_countries": ["CN", "RU"]
    },
    "age_verification": {
        "allowed_countries": ["US", "CA", "EU", "UK"],
        "blocked_countries": []
    },
    "content_moderation": {
        "allowed_countries": [],  # Empty means all allowed
        "blocked_countries": ["CN", "KP"]
    },
    "data_analytics": {
        "allowed_countries": ["US", "CA"],
        "blocked_countries": ["EU", "UK"]  # GDPR restrictions
    }
}

class MockGeoComplianceEngine:
    """Mock geo-compliance engine for testing without Supabase."""
    
    def __init__(self):
        """Initialize mock engine with default rules."""
        self.rules = MOCK_GEO_RULES
    
    async def check_access(
        self, 
        user_id: str, 
        feature_name: str, 
        country: str
    ) -> Tuple[bool, str]:
        """Mock implementation of access checking."""
        
        if feature_name not in self.rules:
            return False, f"No geo-compliance rule found for feature '{feature_name}'"
        
        rule = self.rules[feature_name]
        allowed_countries = rule.get("allowed_countries", [])
        blocked_countries = rule.get("blocked_countries", [])
        
        # Check blocked first
        if country in blocked_countries:
            return False, f"Access denied: '{country}' is blocked for feature '{feature_name}'"
        
        # Check allowed
        if allowed_countries and country in allowed_countries:
            return True, f"Access granted: '{country}' is allowed for feature '{feature_name}'"
        
        if allowed_countries:
            return False, f"Access denied: '{country}' not in allowed list for feature '{feature_name}'"
        
        # No restrictions
        return True, f"Access granted: No geographic restrictions for feature '{feature_name}'"
    
    async def batch_check_access(
        self, 
        requests: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Mock implementation of batch access checking.
        """
        results = []
        
        for request in requests:
            user_id = request.get("user_id")
            feature_name = request.get("feature_name")  
            country = request.get("country")
            
            if not all([user_id, feature_name, country]):
                result = {
                    "user_id": user_id,
                    "feature_name": feature_name,
                    "country": country,
                    "access_granted": False,
                    "reason": "Missing required fields: user_id, feature_name, or country"
                }
            else:
                access_granted, reason = await self.check_access(user_id, feature_name, country)
                result = {
                    "user_id": user_id,
                    "feature_name": feature_name,
                    "country": country,
                    "access_granted": access_granted,
                    "reason": reason
                }
            
            results.append(result)
        
        return results

# Global instance
_geo_engine = None

def get_geo_engine() -> GeoComplianceEngine:
    """Get or create the global geo-compliance engine."""
    global _geo_engine
    if _geo_engine is None:
        supabase_client = get_supabase_client()
        if supabase_client.is_connected():
            _geo_engine = GeoComplianceEngine()
        else:
            logger.warning("Supabase not available, using mock geo-compliance engine")
            _geo_engine = MockGeoComplianceEngine()
    return _geo_engine
