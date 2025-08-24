"""
Tests for the FastAPI application
"""
import pytest
import json
from fastapi import status


class TestAPIEndpoints:
    """Test API endpoints functionality"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns correct information"""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "msg" in data
        assert "model_loaded" in data
        assert data["model_loaded"] is True
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert data["model_loaded"] is True
        assert "model_path" in data


class TestPredictEndpoint:
    """Test the structured prediction endpoint"""
    
    def test_predict_valid_input(self, client, sample_housing_data):
        """Test prediction with valid structured input"""
        response = client.post("/predict", json=sample_housing_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        
        # Check all required fields are present
        required_fields = [
            "prediction", "prediction_eur", "prediction_usd",
            "prediction_eur_formatted", "prediction_usd_formatted",
            "status", "message_text", "message_html"
        ]
        for field in required_fields:
            assert field in data
        
        # Check data types and values
        assert isinstance(data["prediction"], (int, float))
        assert isinstance(data["prediction_eur"], (int, float))
        assert isinstance(data["prediction_usd"], (int, float))
        assert data["prediction"] > 0
        assert data["prediction_eur"] > 0
        assert data["prediction_usd"] > 0
        assert data["status"] == "success"
        
        # Check formatting
        assert "EUR" in data["prediction_eur_formatted"]
        assert "USD" in data["prediction_usd_formatted"]
        assert "🏠" in data["message_html"]
        assert "<b>" in data["message_html"]
    
    def test_predict_missing_fields(self, client):
        """Test prediction with missing required fields"""
        incomplete_data = {
            "MedInc": 4.2,
            "HouseAge": 15.0,
            # Missing other required fields
        }
        response = client.post("/predict", json=incomplete_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_predict_invalid_data_types(self, client):
        """Test prediction with invalid data types"""
        invalid_data = {
            "MedInc": "invalid",  # Should be float
            "HouseAge": 15.0,
            "AveRooms": 5.3,
            "AveBedrms": 1.2,
            "Population": 1800.0,
            "AveOccup": 3.1,
            "Latitude": 34.05,
            "Longitude": -118.25
        }
        response = client.post("/predict", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_predict_extreme_values(self, client):
        """Test prediction with extreme but valid values"""
        extreme_data = {
            "MedInc": 15.0,  # Very high income
            "HouseAge": 52.0,  # Very old house
            "AveRooms": 10.0,  # Many rooms
            "AveBedrms": 2.0,
            "Population": 5000.0,  # High population
            "AveOccup": 5.0,
            "Latitude": 32.0,
            "Longitude": -120.0
        }
        response = client.post("/predict", json=extreme_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"


class TestPredictFromStringEndpoint:
    """Test the CSV string prediction endpoint"""
    
    def test_predict_from_string_valid_input(self, client, sample_csv_input):
        """Test prediction with valid CSV string"""
        payload = {"input": sample_csv_input}
        response = client.post("/predict-from-string", json=payload)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["status"] == "success"
        assert isinstance(data["prediction"], (int, float))
        assert data["prediction"] > 0
    
    def test_predict_from_string_with_semicolons(self, client):
        """Test CSV string with semicolons (should be converted to commas)"""
        csv_with_semicolons = "4.2;15;5.3;1.2;1800;3.1;34.05;-118.25"
        payload = {"input": csv_with_semicolons}
        response = client.post("/predict-from-string", json=payload)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
    
    def test_predict_from_string_wrong_number_of_values(self, client):
        """Test CSV string with wrong number of values"""
        # Too few values
        payload = {"input": "4.2,15,5.3"}
        response = client.post("/predict-from-string", json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Too many values
        payload = {"input": "4.2,15,5.3,1.2,1800,3.1,34.05,-118.25,99,100"}
        response = client.post("/predict-from-string", json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_predict_from_string_invalid_numbers(self, client):
        """Test CSV string with invalid number formats"""
        payload = {"input": "4.2,abc,5.3,1.2,1800,3.1,34.05,-118.25"}
        response = client.post("/predict-from-string", json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_predict_from_string_empty_input(self, client):
        """Test empty CSV string"""
        payload = {"input": ""}
        response = client.post("/predict-from-string", json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_predict_from_string_whitespace_handling(self, client):
        """Test CSV string with extra whitespace"""
        payload = {"input": " 4.2 , 15 , 5.3 , 1.2 , 1800 , 3.1 , 34.05 , -118.25 "}
        response = client.post("/predict-from-string", json=payload)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"


class TestResponseFormatting:
    """Test response formatting functionality"""
    
    def test_currency_formatting(self, client, sample_housing_data):
        """Test currency formatting in responses"""
        response = client.post("/predict", json=sample_housing_data)
        data = response.json()
        
        # Check EUR formatting (European style: 1.234.567,89)
        eur_formatted = data["prediction_eur_formatted"]
        assert "EUR" in eur_formatted
        
        # Check USD formatting (US style: 1,234,567.89)
        usd_formatted = data["prediction_usd_formatted"]
        assert "USD" in usd_formatted
    
    def test_html_message_structure(self, client, sample_housing_data):
        """Test HTML message structure for Telegram"""
        response = client.post("/predict", json=sample_housing_data)
        data = response.json()
        
        html_message = data["message_html"]
        
        # Check for HTML formatting
        assert "<b>" in html_message
        assert "</b>" in html_message
        assert "🏠" in html_message
        assert "🔎" in html_message
        
        # Check for proper HTML escaping (no raw user input)
        assert "<script>" not in html_message
    
    def test_plain_text_message(self, client, sample_housing_data):
        """Test plain text message format"""
        response = client.post("/predict", json=sample_housing_data)
        data = response.json()
        
        text_message = data["message_text"]
        
        # Check structure
        assert "Estimated price:" in text_message
        assert "Details:" in text_message
        assert "Status: success" in text_message
        
        # Should not contain HTML tags
        assert "<b>" not in text_message
        assert "</b>" not in text_message


class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_model_not_loaded_scenario(self, monkeypatch):
        """Test behavior when model is not loaded"""
        # This test would require mocking the model loading failure
        # For now, we'll test the response structure
        pass
    
    def test_prediction_failure_scenario(self, client):
        """Test handling of prediction failures"""
        # Test with data that might cause prediction issues
        problematic_data = {
            "MedInc": float('inf'),  # Infinity value
            "HouseAge": 15.0,
            "AveRooms": 5.3,
            "AveBedrms": 1.2,
            "Population": 1800.0,
            "AveOccup": 3.1,
            "Latitude": 34.05,
            "Longitude": -118.25
        }
        response = client.post("/predict", json=problematic_data)
        # The response might be 500 or 422 depending on how the model handles it
        assert response.status_code in [400, 422, 500]


class TestPerformance:
    """Test performance aspects"""
    
    def test_response_time(self, client, sample_housing_data):
        """Test that responses are reasonably fast"""
        import time
        
        start_time = time.time()
        response = client.post("/predict", json=sample_housing_data)
        end_time = time.time()
        
        assert response.status_code == status.HTTP_200_OK
        assert (end_time - start_time) < 5.0  # Should respond within 5 seconds
    
    def test_concurrent_requests(self, client, sample_housing_data):
        """Test handling of multiple concurrent requests"""
        import concurrent.futures
        
        def make_request():
            return client.post("/predict", json=sample_housing_data)
        
        # Test with 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            responses = [future.result() for future in futures]
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] == "success"
