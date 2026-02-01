#!/usr/bin/env python3
"""
Test script to verify HuggingFace NER works correctly in Docker environment
"""

import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_huggingface_ner():
    """Test HuggingFace NER installation and functionality"""
    try:
        from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
        import torch
        logger.info("✅ HuggingFace transformers successfully imported")
        
        # Test if CUDA is available
        if torch.cuda.is_available():
            logger.info(f"🚀 CUDA available: {torch.cuda.get_device_name(0)}")
            device = 0
        else:
            logger.info("💻 Using CPU for inference")
            device = -1
        
        # Try to load a lightweight NER model
        try:
            ner_pipeline = pipeline(
                "ner", 
                model="dslim/bert-base-NER",
                aggregation_strategy="simple",
                device=device
            )
            logger.info("✅ Successfully loaded HuggingFace NER model: dslim/bert-base-NER")
        except Exception as e:
            logger.warning(f"⚠️  Failed to load dslim/bert-base-NER: {e}")
            logger.info("Trying fallback model...")
            try:
                ner_pipeline = pipeline("ner", aggregation_strategy="simple", device=device)
                logger.info("✅ Successfully loaded default HuggingFace NER model")
            except Exception as e2:
                logger.error(f"❌ Failed to load any NER model: {e2}")
                return False
        
        # Test basic functionality
        test_text = "Users in California under 18 need age verification for GDPR compliance"
        logger.info(f"📝 Test text: {test_text}")
        
        try:
            entities = ner_pipeline(test_text)
            logger.info(f"🏷️  Entities detected: {len(entities)}")
            
            for entity in entities:
                logger.info(f"  - {entity.get('word', 'N/A')} ({entity.get('entity_group', entity.get('label', 'N/A'))}) - {entity.get('score', 0):.3f}")
            
        except Exception as e:
            logger.error(f"❌ Error during NER inference: {e}")
            return False
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Failed to import HuggingFace transformers: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error testing HuggingFace NER: {e}")
        return False

def test_enhanced_classifier():
    """Test the enhanced classifier with spaCy integration"""
    try:
        # Add current directory to path for imports
        sys.path.insert(0, "/app")
        
        from backend.preprocessing import get_preprocessor
        logger.info("✅ Successfully imported preprocessing module")
        
        preprocessor = get_preprocessor()
        logger.info("✅ Preprocessor initialized successfully")
        
        # Test preprocessing
        title = "California Teen Privacy Controls"
        description = "Default privacy settings for users under 18 in California to comply with SB976"
        
        result = preprocessor.process(title, description)
        logger.info(f"📊 Preprocessing result:")
        logger.info(f"   - Entities found: {len(result.entities)}")
        logger.info(f"   - Clear-cut classification: {result.clear_cut_classification}")
        logger.info(f"   - Confidence: {result.confidence_score:.3f}")
        logger.info(f"   - Needs further analysis: {result.needs_further_analysis}")
        
        # Show detected entities
        for entity in result.entities:
            logger.info(f"   - Entity: {entity.text} ({entity.entity_type}) - {entity.confidence:.3f}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing enhanced classifier: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    logger.info("🧪 Testing HuggingFace NER Integration in Docker")
    logger.info("=" * 50)
    
    # Test 1: HuggingFace NER installation
    logger.info("\n1. Testing HuggingFace NER Installation:")
    hf_ok = test_huggingface_ner()
    
    # Test 2: Enhanced classifier integration
    logger.info("\n2. Testing Enhanced Classifier Integration:")
    classifier_ok = test_enhanced_classifier()
    
    # Summary
    logger.info("\n📋 Test Summary:")
    logger.info(f"   HuggingFace NER: {'✅ PASS' if hf_ok else '❌ FAIL'}")
    logger.info(f"   Enhanced Classifier: {'✅ PASS' if classifier_ok else '❌ FAIL'}")
    
    if hf_ok and classifier_ok:
        logger.info("🎉 All tests passed! Docker setup is working correctly.")
        return 0
    else:
        logger.error("❌ Some tests failed. Check the logs above for details.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
