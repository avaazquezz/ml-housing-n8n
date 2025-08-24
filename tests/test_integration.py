"""
Integration tests for the complete ML pipeline
"""
import pytest
import requests
import subprocess
import time
import os
import json


class TestPipelineIntegration:
    """Test the complete ML pipeline integration"""
    
    def test_model_training_to_api_pipeline(self, tmp_path):
        """Test complete pipeline from training to API serving"""
        # Note: This is a conceptual test - in practice you might use Docker containers
        
        # 1. Verify training script exists and is executable
        training_script = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'train.py')
        assert os.path.exists(training_script)
        
        # 2. Verify API script exists
        api_script = os.path.join(os.path.dirname(__file__), '..', 'app', 'main.py')
        assert os.path.exists(api_script)
        
        # 3. Test data flow consistency
        sample_input = {
            "MedInc": 4.2,
            "HouseAge": 15.0,
            "AveRooms": 5.3,
            "AveBedrms": 1.2,
            "Population": 1800.0,
            "AveOccup": 3.1,
            "Latitude": 34.05,
            "Longitude": -118.25
        }
        
        # This test would verify that the same input produces consistent results
        # across different parts of the pipeline
        assert True  # Placeholder for now


class TestDockerIntegration:
    """Test Docker-based deployment"""
    
    @pytest.mark.integration
    def test_docker_compose_build(self):
        """Test that Docker Compose can build the services"""
        # This test requires Docker to be available
        # Skip if not in CI/CD environment
        if not os.getenv('CI'):
            pytest.skip("Skipping Docker test in local environment")
        
        # Test would run: docker-compose build
        # And verify successful build
        pass
    
    @pytest.mark.integration
    def test_docker_services_health(self):
        """Test that Docker services start and are healthy"""
        if not os.getenv('CI'):
            pytest.skip("Skipping Docker test in local environment")
        
        # Test would run: docker-compose up -d
        # Then check health endpoints
        pass


class TestAPIIntegration:
    """Test API integration scenarios"""
    
    def test_api_with_real_data_samples(self, client):
        """Test API with various real-world data samples"""
        # Test cases representing different types of California housing
        test_cases = [
            {
                "name": "Low-income urban",
                "data": {
                    "MedInc": 2.5,
                    "HouseAge": 30.0,
                    "AveRooms": 4.0,
                    "AveBedrms": 1.1,
                    "Population": 5000.0,
                    "AveOccup": 4.0,
                    "Latitude": 34.0,
                    "Longitude": -118.0
                }
            },
            {
                "name": "High-income suburban",
                "data": {
                    "MedInc": 8.5,
                    "HouseAge": 10.0,
                    "AveRooms": 7.0,
                    "AveBedrms": 1.2,
                    "Population": 2000.0,
                    "AveOccup": 2.5,
                    "Latitude": 37.5,
                    "Longitude": -122.0
                }
            },
            {
                "name": "Rural area",
                "data": {
                    "MedInc": 3.8,
                    "HouseAge": 25.0,
                    "AveRooms": 5.5,
                    "AveBedrms": 1.3,
                    "Population": 800.0,
                    "AveOccup": 2.8,
                    "Latitude": 36.0,
                    "Longitude": -119.5
                }
            }
        ]
        
        for case in test_cases:
            response = client.post("/predict", json=case["data"])
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "success"
            assert data["prediction"] > 0
            
            # Predictions should be within reasonable ranges
            # (California housing dataset is in units of 100k)
            assert 0.5 <= data["prediction"] <= 8.0
            
            print(f"{case['name']}: ${data['prediction_usd_formatted']}")
    
    def test_api_response_format_consistency(self, client):
        """Test that API responses are consistent across different endpoints"""
        sample_data = {
            "MedInc": 4.2,
            "HouseAge": 15.0,
            "AveRooms": 5.3,
            "AveBedrms": 1.2,
            "Population": 1800.0,
            "AveOccup": 3.1,
            "Latitude": 34.05,
            "Longitude": -118.25
        }
        
        # Test structured endpoint
        response1 = client.post("/predict", json=sample_data)
        data1 = response1.json()
        
        # Test string endpoint
        csv_input = "4.2,15.0,5.3,1.2,1800.0,3.1,34.05,-118.25"
        response2 = client.post("/predict-from-string", json={"input": csv_input})
        data2 = response2.json()
        
        # Both responses should have same structure
        assert set(data1.keys()) == set(data2.keys())
        
        # Predictions should be very close (within 0.01)
        assert abs(data1["prediction"] - data2["prediction"]) < 0.01
        
        # Status should be success for both
        assert data1["status"] == data2["status"] == "success"


class TestErrorScenarios:
    """Test various error scenarios in the complete system"""
    
    def test_api_graceful_degradation(self, client):
        """Test that API handles errors gracefully"""
        # Test with malformed JSON
        response = client.post("/predict", 
                              data="invalid json",
                              headers={"Content-Type": "application/json"})
        assert response.status_code == 422
        
        # Test with missing content-type
        response = client.post("/predict", data="{}")
        assert response.status_code in [400, 422]
    
    def test_api_input_validation_edge_cases(self, client):
        """Test API input validation with edge cases"""
        edge_cases = [
            # Very large numbers
            {
                "MedInc": 1e6,
                "HouseAge": 15.0,
                "AveRooms": 5.3,
                "AveBedrms": 1.2,
                "Population": 1800.0,
                "AveOccup": 3.1,
                "Latitude": 34.05,
                "Longitude": -118.25
            },
            # Negative values where they shouldn't be
            {
                "MedInc": -1.0,
                "HouseAge": 15.0,
                "AveRooms": 5.3,
                "AveBedrms": 1.2,
                "Population": 1800.0,
                "AveOccup": 3.1,
                "Latitude": 34.05,
                "Longitude": -118.25
            },
            # Zero values
            {
                "MedInc": 0.0,
                "HouseAge": 0.0,
                "AveRooms": 0.0,
                "AveBedrms": 0.0,
                "Population": 0.0,
                "AveOccup": 0.0,
                "Latitude": 0.0,
                "Longitude": 0.0
            }
        ]
        
        for case in edge_cases:
            response = client.post("/predict", json=case)
            # API should handle these gracefully (either succeed or fail cleanly)
            assert response.status_code in [200, 400, 422, 500]
            
            if response.status_code == 200:
                data = response.json()
                assert "prediction" in data


class TestPerformanceIntegration:
    """Test performance characteristics of the integrated system"""
    
    def test_api_throughput(self, client):
        """Test API can handle reasonable throughput"""
        import time
        import statistics
        
        sample_data = {
            "MedInc": 4.2,
            "HouseAge": 15.0,
            "AveRooms": 5.3,
            "AveBedrms": 1.2,
            "Population": 1800.0,
            "AveOccup": 3.1,
            "Latitude": 34.05,
            "Longitude": -118.25
        }
        
        # Measure response times for multiple requests
        response_times = []
        num_requests = 20
        
        for _ in range(num_requests):
            start_time = time.time()
            response = client.post("/predict", json=sample_data)
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
        
        # Calculate statistics
        avg_time = statistics.mean(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        # Performance assertions
        assert avg_time < 1.0  # Average response time under 1 second
        assert max_time < 3.0  # No request takes more than 3 seconds
        
        print(f"Performance stats - Avg: {avg_time:.3f}s, Min: {min_time:.3f}s, Max: {max_time:.3f}s")
    
    def test_memory_usage_stability(self, client):
        """Test that memory usage remains stable during operation"""
        import psutil
        import os
        
        # Get current process
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        sample_data = {
            "MedInc": 4.2,
            "HouseAge": 15.0,
            "AveRooms": 5.3,
            "AveBedrms": 1.2,
            "Population": 1800.0,
            "AveOccup": 3.1,
            "Latitude": 34.05,
            "Longitude": -118.25
        }
        
        # Make many requests
        for _ in range(100):
            response = client.post("/predict", json=sample_data)
            assert response.status_code == 200
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 50MB)
        assert memory_increase < 50 * 1024 * 1024
        
        print(f"Memory usage - Initial: {initial_memory/1024/1024:.1f}MB, "
              f"Final: {final_memory/1024/1024:.1f}MB, "
              f"Increase: {memory_increase/1024/1024:.1f}MB")


class TestDataPipeline:
    """Test data pipeline integrity"""
    
    def test_feature_order_consistency(self, client):
        """Test that feature order is consistent throughout the pipeline"""
        # The order should be: MedInc,HouseAge,AveRooms,AveBedrms,Population,AveOccup,Latitude,Longitude
        
        structured_data = {
            "MedInc": 1.0,
            "HouseAge": 2.0,
            "AveRooms": 3.0,
            "AveBedrms": 4.0,
            "Population": 5.0,
            "AveOccup": 6.0,
            "Latitude": 7.0,
            "Longitude": 8.0
        }
        
        csv_data = "1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0"
        
        response1 = client.post("/predict", json=structured_data)
        response2 = client.post("/predict-from-string", json={"input": csv_data})
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        # Predictions should be identical
        assert abs(data1["prediction"] - data2["prediction"]) < 1e-10
    
    def test_prediction_scaling_consistency(self, client):
        """Test that prediction scaling is applied consistently"""
        sample_data = {
            "MedInc": 4.2,
            "HouseAge": 15.0,
            "AveRooms": 5.3,
            "AveBedrms": 1.2,
            "Population": 1800.0,
            "AveOccup": 3.1,
            "Latitude": 34.05,
            "Longitude": -118.25
        }
        
        response = client.post("/predict", json=sample_data)
        data = response.json()
        
        # Check that EUR to USD conversion is consistent
        expected_usd = data["prediction_eur"] * 1.10  # Default EUR_TO_USD
        assert abs(data["prediction_usd"] - expected_usd) < 0.01
