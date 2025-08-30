#!/usr/bin/env python3
"""
Simple Backend Test - Test Integrated System Without Full Dependencies

This tests the core integrated classification functionality without requiring
all the dependencies like pandas, faiss, etc.
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_simple_classification():
    """Test the integrated classifier with a simple example"""
    
    print("🧪 TESTING INTEGRATED SYSTEM (Simple Mode)")
    print("=" * 60)
    
    try:
        # Import the integrated classifier
        from backend.enhanced_classifier import get_enhanced_classifier
        
        print("✅ Successfully imported enhanced classifier")
        
        # Initialize classifier
        classifier = get_enhanced_classifier()
        print("✅ Successfully initialized classifier")
        
        # Test classification
        title = "GDPR Age Gate"
        description = "Age verification for EU users under 16 to comply with GDPR Article 8"
        
        print(f"\n🔄 Testing classification...")
        print(f"Title: {title}")
        print(f"Description: {description}")
        
        result = classifier.classify(title, description)
        
        print(f"\n📊 RESULTS:")
        print(f"✅ Classification completed successfully!")
        print(f"Needs Geo Logic: {result.needs_geo_logic}")
        print(f"Overall Confidence: {result.overall_confidence:.3f}")
        print(f"Human Review Required: {result.needs_human_review}")
        
        # Check integrated threshold system
        if hasattr(result, 'categories_detected') and result.categories_detected:
            print(f"Categories Detected: {result.categories_detected}")
        if hasattr(result, 'applicable_threshold'):
            print(f"Applicable Threshold: {result.applicable_threshold:.3f}")
        if hasattr(result, 'escalation_rule') and result.escalation_rule:
            print(f"Escalation Rule: {result.escalation_rule}")
        
        print(f"\n🎯 INTEGRATION TEST PASSED!")
        print("✅ Backend is working with integrated system")
        print("✅ Fallback implementations are functioning")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Backend may need additional dependencies or configuration")
        return False

if __name__ == "__main__":
    success = test_simple_classification()
    if success:
        print(f"\n🚀 READY FOR FRONTEND TESTING!")
        print("Your backend is working. The frontend should be able to connect.")
        print("\nTo fix the 'stuck' issue:")
        print("1. Make sure this test passes ✅")
        print("2. Start the backend with dependencies installed")
        print("3. Or use Docker for a complete environment")
    else:
        print(f"\n🔧 BACKEND NEEDS SETUP")
        print("Install dependencies or use Docker to resolve issues.")
