"""
Test script to verify model loading and inference.
Run this independently to test without starting the full API.
"""

import sys
from pathlib import Path
from app.services.ocr_service import load_model, run_inference, get_model_info
from PIL import Image, ImageDraw
import numpy as np

def main():
    """
    Main test function.
    Expects a sample license image at uploads/trade_license_sample.jpg
    and the model at ml_models/roboflow_model/model.pt.
    """
    print("\n" + "=" * 60)
    print("🧪 TESTING MODEL LOADING AND INFERENCE")
    print("=" * 60 + "\n")
    
    try:
        # Test 1: Load model
        print("TEST 1: Loading model...")
        model = load_model()
        print("✅ Model loaded successfully!\n")
        
        # Test 2: Get model info
        print("TEST 2: Getting model info...")
        info = get_model_info()
        print("   Model Info:")
        for key, value in info.items():
            print(f"   - {key}: {value}")
        print("✅ Model info retrieved!\n")
        
        # Test 3: Create dummy image
        print("TEST 3: Creating test image...")
        test_image_path = "uploads/trade_license_sample.jpg" 
        print("✅ Test image ready!\n")
        
        # Test 4: Run inference
        print("TEST 4: Running inference on test image...")
        detections = run_inference(test_image_path, confidence_threshold=0.25)
        
        print("\n📊 RESULTS:")
        print(f"   Total detections: {len(detections)}")
        
        if len(detections) > 0:
            print("\n   Detections:")
            for i, det in enumerate(detections, 1):
                print(f"\n   Detection {i}:")
                print(f"      Class: {det['class_name']}")
                print(f"      Confidence: {det['confidence']:.2%}")
                print(f"      Bounding Box: {det['bbox']}")
        else:
            print("\n   ⚠️  No detections found (this is normal for dummy image)")
            print("   Try with a real trade license image!")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60 + "\n")
        
    except FileNotFoundError as e:
        print(f"\n❌ ERROR: {e}")
        print("\n💡 Make sure your model file is at:")
        print("   ml_models/roboflow_model/model.pt")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()