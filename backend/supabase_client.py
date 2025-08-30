"""
Supabase client configuration and utilities for geo-compliance system.
"""

import os
from supabase import create_client, Client
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseClient:
    """Supabase client wrapper for geo-compliance operations."""
    
    def __init__(self):
        """Initialize Supabase client with environment variables."""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            logger.warning("Supabase credentials not found in environment variables")
            self.client = None
        else:
            try:
                self.client: Client = create_client(self.supabase_url, self.supabase_key)
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                self.client = None
    
    def is_connected(self) -> bool:
        """Check if Supabase client is properly connected."""
        return self.client is not None
    
    async def get_geo_rule(self, feature_name: str) -> Optional[Dict[str, Any]]:
        """
        Get geo-compliance rule for a specific feature.
        
        Args:
            feature_name: Name of the feature to check
            
        Returns:
            Dict containing allowed_countries and blocked_countries, or None if not found
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return None
            
        try:
            response = self.client.table("geo_rules").select("*").eq("feature_name", feature_name).execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error fetching geo rule for {feature_name}: {e}")
            return None
    
    async def log_access_attempt(
        self, 
        user_id: str, 
        feature_name: str, 
        country: str, 
        access_granted: bool
    ) -> bool:
        """
        Log an access attempt to the access_logs table.
        
        Args:
            user_id: ID of the user making the request
            feature_name: Name of the feature being accessed
            country: Country code of the user
            access_granted: Whether access was granted or denied
            
        Returns:
            True if logged successfully, False otherwise
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return False
            
        try:
            log_data = {
                "user_id": user_id,
                "feature_name": feature_name,
                "country": country,
                "access_granted": access_granted,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            response = self.client.table("access_logs").insert(log_data).execute()
            
            if response.data:
                logger.info(f"Access attempt logged for user {user_id}, feature {feature_name}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error logging access attempt: {e}")
            return False
    
    async def get_access_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve access logs from the database.
        
        Args:
            limit: Maximum number of logs to retrieve
            
        Returns:
            List of access log entries
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return []
            
        try:
            response = self.client.table("access_logs").select("*").order("timestamp", desc=True).limit(limit).execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"Error fetching access logs: {e}")
            return []
    
    async def create_geo_rule(
        self, 
        feature_name: str, 
        allowed_countries: List[str] = None, 
        blocked_countries: List[str] = None
    ) -> bool:
        """
        Create or update a geo-compliance rule.
        
        Args:
            feature_name: Name of the feature
            allowed_countries: List of allowed country codes
            blocked_countries: List of blocked country codes
            
        Returns:
            True if created/updated successfully, False otherwise
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return False
            
        try:
            rule_data = {
                "feature_name": feature_name,
                "allowed_countries": allowed_countries or [],
                "blocked_countries": blocked_countries or []
            }
            
            # Use upsert to create or update
            response = self.client.table("geo_rules").upsert(rule_data).execute()
            
            if response.data:
                logger.info(f"Geo rule created/updated for feature {feature_name}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error creating geo rule: {e}")
            return False
    
    async def log_classification_result(
        self,
        title: str,
        description: str,
        needs_geo_logic: bool,
        confidence: float,
        reasoning: str,
        regulations: List[str],
        risk_level: str,
        specific_requirements: List[str]
    ) -> bool:
        """
        Log a classification result to the classification_results table.
        
        Args:
            title: Feature title
            description: Feature description
            needs_geo_logic: Whether geo logic is needed
            confidence: Confidence score
            reasoning: Classification reasoning
            regulations: Applicable regulations
            risk_level: Risk level (low/medium/high)
            specific_requirements: List of specific requirements
            
        Returns:
            True if logged successfully, False otherwise
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return False
            
        try:
            classification_data = {
                "title": title,
                "description": description,
                "needs_geo_logic": needs_geo_logic,
                "confidence": confidence,
                "reasoning": reasoning,
                "regulations": regulations,
                "risk_level": risk_level,
                "specific_requirements": specific_requirements,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            response = self.client.table("classification_results").insert(classification_data).execute()
            
            if response.data:
                logger.info(f"Classification result logged for feature: {title}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error logging classification result: {e}")
            return False
    
    async def get_classification_results(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve classification results from the database.
        
        Args:
            limit: Maximum number of results to retrieve
            
        Returns:
            List of classification result entries
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return []
            
        try:
            response = self.client.table("classification_results").select("*").order("timestamp", desc=True).limit(limit).execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"Error fetching classification results: {e}")
            return []
    
    async def get_classification_statistics(self) -> Dict[str, Any]:
        """
        Get classification statistics from Supabase.
        
        Returns:
            Dictionary with classification statistics
        """
        if not self.client:
            logger.error("Supabase client not initialized")
            return {
                "total_classifications": 0,
                "compliance_required": 0,
                "no_compliance_needed": 0,
                "average_confidence": 0.0,
                "risk_levels": {"low": 0, "medium": 0, "high": 0}
            }
            
        try:
            # Get all classification results
            response = self.client.table("classification_results").select("*").execute()
            results = response.data if response.data else []
            
            if not results:
                return {
                    "total_classifications": 0,
                    "compliance_required": 0,
                    "no_compliance_needed": 0,
                    "average_confidence": 0.0,
                    "risk_levels": {"low": 0, "medium": 0, "high": 0}
                }
            
            total = len(results)
            compliance_required = len([r for r in results if r.get('needs_geo_logic') == True])
            no_compliance_needed = len([r for r in results if r.get('needs_geo_logic') == False])
            
            # Calculate average confidence
            confidences = [r.get('confidence', 0) for r in results if r.get('confidence') is not None]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            # Count risk levels
            risk_levels = {"low": 0, "medium": 0, "high": 0}
            for result in results:
                risk_level = result.get('risk_level', '').lower()
                if risk_level in risk_levels:
                    risk_levels[risk_level] += 1
            
            return {
                "total_classifications": total,
                "compliance_required": compliance_required,
                "no_compliance_needed": no_compliance_needed,
                "average_confidence": round(avg_confidence, 3),
                "risk_levels": risk_levels
            }
            
        except Exception as e:
            logger.error(f"Error fetching classification statistics: {e}")
            return {
                "total_classifications": 0,
                "compliance_required": 0,
                "no_compliance_needed": 0,
                "average_confidence": 0.0,
                "risk_levels": {"low": 0, "medium": 0, "high": 0}
            }

# Global instance
_supabase_client = None

def get_supabase_client() -> SupabaseClient:
    """Get or create the global Supabase client instance."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    return _supabase_client
