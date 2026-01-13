"""Test FastAPI server without models"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from api.src.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    print("✅ Root endpoint test passed")

def test_openapi_schema():
    """Test OpenAPI schema generation"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema
    print("✅ OpenAPI schema test passed")

def test_docs_endpoint():
    """Test docs endpoint"""
    response = client.get("/docs")
    assert response.status_code == 200
    print("✅ Docs endpoint test passed")

def test_models_endpoint():
    """Test models listing endpoint"""
    response = client.get("/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert "object" in data
    assert "data" in data
    assert len(data["data"]) > 0
    # Check for supertonic model
    model_ids = [m["id"] for m in data["data"]]
    assert "supertonic" in model_ids
    print("✅ Models endpoint test passed")

if __name__ == "__main__":
    print("Running FastAPI server tests...")
    print()
    
    try:
        test_root_endpoint()
        test_openapi_schema()
        test_docs_endpoint()
        test_models_endpoint()
        
        print()
        print("=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        print()
        print("Note: Full TTS functionality requires ONNX models")
        print("Download models: git clone https://huggingface.co/Supertone/supertonic-2 ../assets")
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
