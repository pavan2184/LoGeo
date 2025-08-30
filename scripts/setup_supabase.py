#!/usr/bin/env python3
"""
Supabase SQL Setup for Geo-Compliance System

This script outputs the SQL commands needed to set up your Supabase database.
Copy and paste these commands into your Supabase SQL Editor.

Required tables:
- geo_rules: Store feature access rules by country
- access_logs: Log all access attempts for audit trail  
- classification_results: Store all feature classification data

Usage:
    python scripts/setup_supabase.py
"""

def setup_supabase():
    """Output SQL commands for Supabase setup."""
    
    print("🚀 Geo-Compliance Supabase Setup")
    print("=" * 40)
    print("\n📋 Copy and paste these SQL commands into your Supabase SQL Editor:")
    print("🌐 Dashboard: https://app.supabase.com/project/<your-project-id>/sql")
    print("=" * 60)
    
    print("""
-- Create geo_rules table
CREATE TABLE IF NOT EXISTS geo_rules (
    feature_name TEXT PRIMARY KEY,
    allowed_countries TEXT[] DEFAULT '{}',
    blocked_countries TEXT[] DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create access_logs table
CREATE TABLE IF NOT EXISTS access_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    feature_name TEXT NOT NULL,
    country TEXT NOT NULL,
    access_granted BOOLEAN NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Create classification_results table for storing all classification data
CREATE TABLE IF NOT EXISTS classification_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    needs_geo_logic BOOLEAN NOT NULL,
    confidence FLOAT NOT NULL,
    reasoning TEXT NOT NULL,
    regulations TEXT[] DEFAULT '{}',
    risk_level TEXT NOT NULL,
    specific_requirements TEXT[] DEFAULT '{}',
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Insert sample geo-compliance rules
INSERT INTO geo_rules (feature_name, allowed_countries, blocked_countries) VALUES
('user_registration', '{"US","CA","UK","AU","EU"}', '{"CN","RU","KP"}'),
('age_verification', '{"US","CA","UK","EU"}', '{}'),
('data_analytics', '{"US","CA"}', '{"EU","UK"}'),
('content_moderation', '{}', '{"CN","KP"}'),
('social_features', '{"US","CA","UK","AU"}', '{"CN","RU","EU"}'),
('payment_processing', '{"US","CA","UK","AU","EU"}', '{"CN","RU","KP","IR"}')
ON CONFLICT (feature_name) DO NOTHING;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_access_logs_timestamp ON access_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_access_logs_user_id ON access_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_access_logs_feature ON access_logs(feature_name);
CREATE INDEX IF NOT EXISTS idx_classification_results_timestamp ON classification_results(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_classification_results_risk_level ON classification_results(risk_level);
CREATE INDEX IF NOT EXISTS idx_classification_results_needs_geo_logic ON classification_results(needs_geo_logic);
    """)
    
    print("=" * 60)
    print("\n✅ Setup Instructions:")
    print("1. Go to your Supabase dashboard")
    print("2. Navigate to SQL Editor")
    print("3. Copy and paste the SQL commands above")
    print("4. Click 'RUN' to execute")
    print("5. Verify tables are created in the Table Editor")
    print("\n🎯 After setup, your system will store:")
    print("• All classification results in Supabase") 
    print("• Geographic access logs")
    print("• Geo-compliance rules")
    print("• Complete audit trail for compliance")

if __name__ == "__main__":
    setup_supabase()
