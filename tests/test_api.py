import pytest
import os
import shutil
from fastapi.testclient import TestClient
from kestrel_returns.api import app, ARTIFACTS_DIR

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_predict_success(client):
    payload = {
        "family": "Air Fryer",
        "sales_channel": "app",
        "payment_mode": "prepaid_upi",
        "is_gift": "N",
        "shield_member": "Y",
        "discount_pct": 10.5,
        "promised_delivery_days": 3,
        "customer_prior_orders": 2,
        "customer_prior_returns": 0,
        "order_id": "TEST1234",
        "sku": "ignore_me"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "score" in data
    assert "recommend_call" in data
    assert "reasons" in data
    assert "ignored_fields" in data
    assert "sku" in data["ignored_fields"]
    assert data["order_id"] == "TEST1234"
    assert len(data["reasons"]) > 0

    # Deterministic API response
    response2 = client.post("/predict", json=payload)
    assert response.json() == response2.json()

def test_invalid_enum(client):
    payload = {
        "family": "Invalid Family",
        "sales_channel": "app",
        "payment_mode": "prepaid_upi",
        "is_gift": "N",
        "shield_member": "Y",
        "discount_pct": 10.5,
        "promised_delivery_days": 3,
        "customer_prior_orders": 2,
        "customer_prior_returns": 0
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422

def test_prior_returns_greater_than_orders(client):
    payload = {
        "family": "Air Fryer",
        "sales_channel": "app",
        "payment_mode": "prepaid_upi",
        "is_gift": "N",
        "shield_member": "Y",
        "discount_pct": 10.5,
        "promised_delivery_days": 3,
        "customer_prior_orders": 2,
        "customer_prior_returns": 5
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422
    assert "greater" in response.text

def test_missing_field(client):
    payload = {
        "sales_channel": "app"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422

def test_invalid_numeric_bounds(client):
    payload = {
        "family": "Air Fryer",
        "sales_channel": "app",
        "payment_mode": "prepaid_upi",
        "is_gift": "N",
        "shield_member": "Y",
        "discount_pct": 150, # Invalid (>100)
        "promised_delivery_days": 3,
        "customer_prior_orders": 2,
        "customer_prior_returns": 0
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422
    assert "discount_pct" in response.text

    payload["discount_pct"] = -10 # Invalid (<0)
    response = client.post("/predict", json=payload)
    assert response.status_code == 422

    payload["discount_pct"] = 10
    payload["promised_delivery_days"] = -5 # Invalid (<0)
    response = client.post("/predict", json=payload)
    assert response.status_code == 422

def test_missing_artifact_503():
    # We move artifacts to a temp dir, test, and put them back
    temp_dir = ARTIFACTS_DIR.parent / "temp_artifacts"
    if ARTIFACTS_DIR.exists():
        shutil.move(str(ARTIFACTS_DIR), str(temp_dir))

    try:
        import kestrel_returns.api as api_module

        # Reset globals to simulate cold start
        old_pipeline = api_module.pipeline
        old_meta = api_module.model_meta
        api_module.pipeline = None
        api_module.model_meta = None

        with TestClient(api_module.app) as temp_client:
            health = temp_client.get("/health")
            assert health.status_code == 200 # health returns 200 with unhealthy status
            assert health.json()["status"] == "unhealthy"

            payload = {
                "family": "Air Fryer", "sales_channel": "app", "payment_mode": "prepaid_upi",
                "is_gift": "N", "shield_member": "Y", "discount_pct": 10.5,
                "promised_delivery_days": 3, "customer_prior_orders": 2, "customer_prior_returns": 0
            }
            pred = temp_client.post("/predict", json=payload)
            assert pred.status_code == 503

        # Restore globals
        api_module.pipeline = old_pipeline
        api_module.model_meta = old_meta
    finally:
        if temp_dir.exists():
            if ARTIFACTS_DIR.exists():
                shutil.rmtree(ARTIFACTS_DIR)
            shutil.move(str(temp_dir), str(ARTIFACTS_DIR))
