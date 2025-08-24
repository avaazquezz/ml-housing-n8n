"""
Tests for the Machine Learning model
"""
import pytest
import numpy as np
import pandas as pd
import joblib
import os
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.model_selection import cross_val_score
import tempfile


class TestModelTraining:
    """Test model training functionality"""
    
    def test_model_creation_and_fitting(self, california_housing_data):
        """Test that model can be created and fitted"""
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import StandardScaler
        from sklearn.ensemble import RandomForestRegressor
        
        data = california_housing_data
        X = data.data.head(1000)  # Use subset for faster testing
        y = data.target.head(1000)
        
        # Create pipeline
        pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("rf", RandomForestRegressor(n_estimators=10, random_state=42, n_jobs=1)),
        ])
        
        # Fit the model
        pipeline.fit(X, y)
        
        # Check that model components are fitted
        assert hasattr(pipeline.named_steps['scaler'], 'mean_')
        assert hasattr(pipeline.named_steps['rf'], 'feature_importances_')
    
    def test_model_prediction_shape(self, test_model, california_housing_data):
        """Test that model predictions have correct shape"""
        data = california_housing_data
        X_test = data.data.head(10)
        
        predictions = test_model.predict(X_test)
        
        assert len(predictions) == len(X_test)
        assert isinstance(predictions, np.ndarray)
        assert predictions.dtype in [np.float64, np.float32]
    
    def test_model_prediction_values(self, test_model, california_housing_data):
        """Test that model predictions are reasonable"""
        data = california_housing_data
        X_test = data.data.head(100)
        
        predictions = test_model.predict(X_test)
        
        # Predictions should be positive (housing prices)
        assert all(pred > 0 for pred in predictions)
        
        # Predictions should be within reasonable range for California housing
        # (dataset is in units of 100k, so 0.5-5.0 represents 50k-500k)
        assert all(0.1 <= pred <= 10.0 for pred in predictions)
    
    def test_model_performance_metrics(self, test_model, california_housing_data):
        """Test that model achieves reasonable performance"""
        data = california_housing_data
        X = data.data.head(1000)
        y = data.target.head(1000)
        
        predictions = test_model.predict(X)
        
        # Calculate metrics
        mse = mean_squared_error(y, predictions)
        r2 = r2_score(y, predictions)
        mae = mean_absolute_error(y, predictions)
        
        # Model should achieve reasonable performance
        assert r2 > 0.5  # R² should be above 0.5
        assert mse < 2.0  # MSE should be reasonable
        assert mae < 1.0  # MAE should be reasonable
        
        print(f"Model Performance - R²: {r2:.3f}, MSE: {mse:.3f}, MAE: {mae:.3f}")


class TestModelSerialization:
    """Test model saving and loading"""
    
    def test_model_save_and_load(self, test_model):
        """Test that model can be saved and loaded correctly"""
        with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
            # Save model
            joblib.dump(test_model, f.name)
            
            # Load model
            loaded_model = joblib.load(f.name)
            
            # Test that loaded model works
            sample_data = pd.DataFrame({
                'MedInc': [4.2],
                'HouseAge': [15.0],
                'AveRooms': [5.3],
                'AveBedrms': [1.2],
                'Population': [1800.0],
                'AveOccup': [3.1],
                'Latitude': [34.05],
                'Longitude': [-118.25]
            })
            
            original_pred = test_model.predict(sample_data)
            loaded_pred = loaded_model.predict(sample_data)
            
            # Predictions should be identical
            np.testing.assert_array_almost_equal(original_pred, loaded_pred)
        
        # Cleanup
        os.unlink(f.name)
    
    def test_model_file_integrity(self, test_model_file):
        """Test that saved model file is valid"""
        # Check file exists and has content
        assert os.path.exists(test_model_file)
        assert os.path.getsize(test_model_file) > 0
        
        # Load and verify it's a valid model
        loaded_model = joblib.load(test_model_file)
        assert hasattr(loaded_model, 'predict')
        assert hasattr(loaded_model, 'named_steps')


class TestModelInputValidation:
    """Test model input validation and edge cases"""
    
    def test_model_with_single_sample(self, test_model):
        """Test model prediction with single sample"""
        sample = pd.DataFrame({
            'MedInc': [4.2],
            'HouseAge': [15.0],
            'AveRooms': [5.3],
            'AveBedrms': [1.2],
            'Population': [1800.0],
            'AveOccup': [3.1],
            'Latitude': [34.05],
            'Longitude': [-118.25]
        })
        
        prediction = test_model.predict(sample)
        assert len(prediction) == 1
        assert prediction[0] > 0
    
    def test_model_with_multiple_samples(self, test_model):
        """Test model prediction with multiple samples"""
        samples = pd.DataFrame({
            'MedInc': [4.2, 3.5, 5.1],
            'HouseAge': [15.0, 25.0, 10.0],
            'AveRooms': [5.3, 4.8, 6.2],
            'AveBedrms': [1.2, 1.1, 1.3],
            'Population': [1800.0, 2500.0, 1200.0],
            'AveOccup': [3.1, 2.8, 3.5],
            'Latitude': [34.05, 35.0, 33.5],
            'Longitude': [-118.25, -119.0, -117.5]
        })
        
        predictions = test_model.predict(samples)
        assert len(predictions) == 3
        assert all(pred > 0 for pred in predictions)
    
    def test_model_with_edge_case_values(self, test_model):
        """Test model with edge case input values"""
        edge_cases = pd.DataFrame({
            'MedInc': [0.5, 15.0],  # Very low and high income
            'HouseAge': [1.0, 52.0],  # Very new and old houses
            'AveRooms': [2.0, 15.0],  # Few and many rooms
            'AveBedrms': [0.8, 3.0],  # Few and many bedrooms
            'Population': [100.0, 10000.0],  # Low and high population
            'AveOccup': [1.5, 8.0],  # Low and high occupancy
            'Latitude': [32.0, 42.0],  # Southern and northern California
            'Longitude': [-124.0, -114.0]  # Western and eastern California
        })
        
        predictions = test_model.predict(edge_cases)
        assert len(predictions) == 2
        assert all(pred > 0 for pred in predictions)
    
    def test_model_feature_importance(self, test_model):
        """Test that model has learned meaningful feature importances"""
        feature_names = ['MedInc', 'HouseAge', 'AveRooms', 'AveBedrms', 
                        'Population', 'AveOccup', 'Latitude', 'Longitude']
        
        # Get feature importances from the RandomForest
        rf_model = test_model.named_steps['rf']
        importances = rf_model.feature_importances_
        
        # Check that we have importance for each feature
        assert len(importances) == len(feature_names)
        
        # All importances should be non-negative
        assert all(imp >= 0 for imp in importances)
        
        # Importances should sum to 1
        assert abs(sum(importances) - 1.0) < 1e-6
        
        # MedInc (median income) should typically be important for housing prices
        medinc_importance = importances[0]  # MedInc is first feature
        assert medinc_importance > 0.1  # Should have at least 10% importance


class TestModelCrossValidation:
    """Test model performance with cross-validation"""
    
    def test_cross_validation_performance(self, california_housing_data):
        """Test model performance using cross-validation"""
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import StandardScaler
        from sklearn.ensemble import RandomForestRegressor
        
        data = california_housing_data
        X = data.data.head(2000)  # Use subset for faster testing
        y = data.target.head(2000)
        
        # Create pipeline
        pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("rf", RandomForestRegressor(n_estimators=20, random_state=42, n_jobs=1)),
        ])
        
        # Perform cross-validation
        cv_scores = cross_val_score(pipeline, X, y, cv=3, scoring='r2')
        
        # Check that CV scores are reasonable
        assert len(cv_scores) == 3
        assert all(score > 0.3 for score in cv_scores)  # All folds should have R² > 0.3
        assert cv_scores.mean() > 0.5  # Average R² should be > 0.5
        
        print(f"Cross-validation R² scores: {cv_scores}")
        print(f"Mean CV R²: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")


class TestModelRobustness:
    """Test model robustness and stability"""
    
    def test_prediction_consistency(self, test_model):
        """Test that model gives consistent predictions for same input"""
        sample = pd.DataFrame({
            'MedInc': [4.2],
            'HouseAge': [15.0],
            'AveRooms': [5.3],
            'AveBedrms': [1.2],
            'Population': [1800.0],
            'AveOccup': [3.1],
            'Latitude': [34.05],
            'Longitude': [-118.25]
        })
        
        # Make multiple predictions
        pred1 = test_model.predict(sample)
        pred2 = test_model.predict(sample)
        pred3 = test_model.predict(sample)
        
        # All predictions should be identical
        np.testing.assert_array_equal(pred1, pred2)
        np.testing.assert_array_equal(pred1, pred3)
    
    def test_model_stability_across_random_seeds(self, california_housing_data):
        """Test that model training is reasonably stable across different random seeds"""
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import StandardScaler
        from sklearn.ensemble import RandomForestRegressor
        
        data = california_housing_data
        X = data.data.head(1000)
        y = data.target.head(1000)
        
        sample = X.head(1)
        predictions = []
        
        # Train models with different random seeds
        for seed in [42, 123, 456]:
            pipeline = Pipeline([
                ("scaler", StandardScaler()),
                ("rf", RandomForestRegressor(n_estimators=20, random_state=seed, n_jobs=1)),
            ])
            pipeline.fit(X, y)
            pred = pipeline.predict(sample)[0]
            predictions.append(pred)
        
        # Predictions should be reasonably similar (coefficient of variation < 20%)
        mean_pred = np.mean(predictions)
        std_pred = np.std(predictions)
        cv = std_pred / mean_pred
        
        assert cv < 0.2, f"Model predictions too variable across seeds: CV = {cv:.3f}"


class TestTrainingScript:
    """Test the training script functionality"""
    
    def test_training_script_execution(self, tmp_path):
        """Test that training script can be executed successfully"""
        # This would be an integration test that actually runs the training script
        # For now, we'll test the core logic
        
        # Import training logic
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
        
        # Test would go here - for now, we'll just check imports work
        try:
            from sklearn.datasets import fetch_california_housing
            from sklearn.model_selection import train_test_split
            from sklearn.pipeline import Pipeline
            from sklearn.preprocessing import StandardScaler
            from sklearn.ensemble import RandomForestRegressor
            import joblib
            
            # If we get here, all required imports work
            assert True
        except ImportError as e:
            pytest.fail(f"Training script dependencies not available: {e}")
    
    def test_model_directory_creation(self, tmp_path):
        """Test that model directory can be created"""
        model_dir = tmp_path / "test_model"
        model_dir.mkdir(exist_ok=True)
        
        assert model_dir.exists()
        assert model_dir.is_dir()
    
    def test_model_save_path(self, tmp_path, test_model):
        """Test model saving to specific path"""
        model_dir = tmp_path / "model"
        model_dir.mkdir(exist_ok=True)
        
        model_path = model_dir / "test_model.joblib"
        
        # Save model
        joblib.dump(test_model, model_path)
        
        # Verify file was created
        assert model_path.exists()
        assert model_path.stat().st_size > 0
        
        # Verify model can be loaded
        loaded_model = joblib.load(model_path)
        assert hasattr(loaded_model, 'predict')
