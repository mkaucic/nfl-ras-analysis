import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import os

# Make sure the analysis directory exists
os.makedirs('../../backend/analysis/advanced', exist_ok=True)

def perform_advanced_analysis():
    print("Performing advanced statistical analysis...")
    
    # Load the data
    try:
        df = pd.read_csv('../../backend/data/pro_bowlers_ras.csv')
        print(f"Loaded data for {len(df)} players")
    except Exception as e:
        print(f"Error loading data: {e}")
        return
    
    # Prepare the data
    # Convert RAS to numeric
    if 'RAS' in df.columns:
        df['RAS_numeric'] = pd.to_numeric(df['RAS'], errors='coerce')
    
    # Convert Pro Bowls to numeric
    pro_bowl_cols = ['Pro Bowls', 'ProBowls', 'Pro_Bowls']
    for col in pro_bowl_cols:
        if col in df.columns:
            df['Pro_Bowls_numeric'] = pd.to_numeric(df[col], errors='coerce')
            break
    
    # Handle position
    pos_col = None
    for col in ['Position', 'Pos']:
        if col in df.columns:
            pos_col = col
            break
    
    if pos_col:
        # Create dummy variables for positions
        position_dummies = pd.get_dummies(df[pos_col], prefix='pos')
        df = pd.concat([df, position_dummies], axis=1)
    
    # Handle draft information
    if 'Draft Year' in df.columns:
        # Extract draft round if possible
        try:
            df['draft_round'] = df['Draft Year'].str.extract(r'Round (\d+)').astype(float)
        except:
            print("Couldn't extract draft round from Draft Year column")
    
    # Multiple Regression Analysis
    print("\nPerforming multiple regression analysis...")
    
    # Drop missing values for regression
    regression_df = df.dropna(subset=['RAS_numeric', 'Pro_Bowls_numeric'])
    
    if len(regression_df) < 10:
        print("Not enough data for regression analysis")
        return
    
    # Basic model: Pro Bowls ~ RAS
    X = regression_df[['RAS_numeric']].astype(float)
    X = sm.add_constant(X)  # Add intercept
    y = regression_df['Pro_Bowls_numeric'].astype(float)
    
    model = sm.OLS(y, X).fit()
    print("\nBasic Regression Results (Pro Bowls ~ RAS):")
    print(model.summary().tables[1])
    
    # Save the results
    with open('../../backend/analysis/advanced/basic_regression.txt', 'w') as f:
        f.write(str(model.summary()))
    
    # Advanced model: Include position and draft round if available
    advanced_cols = ['RAS_numeric']
    
    # Add position dummies if available
    pos_dummy_cols = [col for col in regression_df.columns if col.startswith('pos_')]
    if pos_dummy_cols:
        # Take fewer dummy variables to avoid potential issues
        advanced_cols.extend(pos_dummy_cols[:min(5, len(pos_dummy_cols)-1)])  # Exclude one for the dummy variable trap
    
    # Add draft round if available
    if 'draft_round' in regression_df.columns:
        advanced_cols.append('draft_round')
    
    # Run advanced model if we have enough variables
    if len(advanced_cols) > 1:
        # Convert data to float to avoid the object dtype error
        try:
            X_adv = regression_df[advanced_cols].astype(float)
            X_adv = sm.add_constant(X_adv)
            y_adv = y.astype(float)
            
            advanced_model = sm.OLS(y_adv, X_adv).fit()
            print("\nAdvanced Regression Results (including position/draft):")
            print(advanced_model.summary().tables[1])
            
            with open('../../backend/analysis/advanced/advanced_regression.txt', 'w') as f:
                f.write(str(advanced_model.summary()))
        except Exception as e:
            print(f"Error in advanced regression: {e}")
            print("Skipping advanced regression analysis")
    
    # Machine Learning: Predict Pro Bowl Likelihood
    print("\nTraining machine learning models to predict Pro Bowl likelihood...")
    
    # Create a binary target: Did the player make multiple Pro Bowls?
    regression_df['multiple_pro_bowls'] = (regression_df['Pro_Bowls_numeric'] > 1).astype(int)
    
    # Features for prediction
    ml_features = ['RAS_numeric']
    
    # Add position dummies if available
    if pos_dummy_cols:
        # Limit the number of features to avoid issues
        ml_features.extend(pos_dummy_cols[:min(5, len(pos_dummy_cols))])
    
    # Add draft round if available
    if 'draft_round' in regression_df.columns and not regression_df['draft_round'].isna().all():
        ml_features.append('draft_round')
    
    # Ensure all features are numeric and handle missing values
    X_ml = regression_df[ml_features].fillna(0).astype(float)
    y_ml = regression_df['multiple_pro_bowls'].astype(int)
    
    # Split data
    try:
        X_train, X_test, y_train, y_test = train_test_split(X_ml, y_ml, test_size=0.25, random_state=42)
        
        # Logistic Regression
        log_reg = LogisticRegression(random_state=42, max_iter=1000)
        log_reg.fit(X_train, y_train)
        
        y_pred_lr = log_reg.predict(X_test)
        accuracy_lr = accuracy_score(y_test, y_pred_lr)
        
        print(f"\nLogistic Regression Accuracy: {accuracy_lr:.4f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred_lr))
        
        # Feature importance from logistic regression
        feature_importance_lr = pd.DataFrame({
            'Feature': X_ml.columns,
            'Importance': np.abs(log_reg.coef_[0])
        }).sort_values('Importance', ascending=False)
        
        print("\nFeature Importance (Logistic Regression):")
        print(feature_importance_lr)
        
        # Save results
        with open('../../backend/analysis/advanced/logistic_regression_results.txt', 'w') as f:
            f.write(f"Logistic Regression Accuracy: {accuracy_lr:.4f}\n\n")
            f.write("Classification Report:\n")
            f.write(classification_report(y_test, y_pred_lr))
            f.write("\nFeature Importance:\n")
            f.write(feature_importance_lr.to_string())
        
        # Random Forest for comparison
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(X_train, y_train)
        
        y_pred_rf = rf.predict(X_test)
        accuracy_rf = accuracy_score(y_test, y_pred_rf)
        
        print(f"\nRandom Forest Accuracy: {accuracy_rf:.4f}")
        
        # Feature importance from random forest
        feature_importance_rf = pd.DataFrame({
            'Feature': X_ml.columns,
            'Importance': rf.feature_importances_
        }).sort_values('Importance', ascending=False)
        
        print("\nFeature Importance (Random Forest):")
        print(feature_importance_rf)
        
        with open('../../backend/analysis/advanced/random_forest_results.txt', 'w') as f:
            f.write(f"Random Forest Accuracy: {accuracy_rf:.4f}\n\n")
            f.write("Classification Report:\n")
            f.write(classification_report(y_test, y_pred_rf))
            f.write("\nFeature Importance:\n")
            f.write(feature_importance_rf.to_string())
    
    except Exception as e:
        print(f"Error in classification models: {e}")
        print("Creating simplified models for visualization...")
        # Create simple models for visualization purposes
        log_reg = LogisticRegression(random_state=42, max_iter=1000)
        log_reg.fit(regression_df[['RAS_numeric']].fillna(0).astype(float), 
                   regression_df['multiple_pro_bowls'].astype(int))
        
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(regression_df[['RAS_numeric']].fillna(0).astype(float), 
              regression_df['multiple_pro_bowls'].astype(int))
    
    # Generate prediction dataset for frontend visualization
    # This creates a dataset with predictions for different RAS values by position
    
    print("\nGenerating prediction dataset for visualization...")
    
    # Get unique positions
    positions = df[pos_col].unique() if pos_col else ['All']
    
    predictions_data = []
    
    for position in positions:
        if position != 'DB':  # Skip DB position as requested earlier
            # Create a range of RAS values
            for ras in np.arange(1, 10.1, 0.1):
                # Create a sample player with this RAS and position
                sample_data = {'RAS_numeric': [ras]}
                
                # Add position dummies if needed
                if pos_dummy_cols and len(pos_dummy_cols) > 0:
                    for pos_dummy in pos_dummy_cols[:min(5, len(pos_dummy_cols))]:
                        if pos_dummy in X_ml.columns:  # Only add if it was used in training
                            pos_name = pos_dummy.split('_')[1]
                            sample_data[pos_dummy] = 1 if pos_name == position else 0
                
                # Add a middle-round draft pick if used in training
                if 'draft_round' in X_ml.columns:
                    sample_data['draft_round'] = 3
                
                # Create sample DataFrame with only columns used in training
                sample = pd.DataFrame(sample_data)
                for col in X_ml.columns:
                    if col not in sample.columns:
                        sample[col] = 0
                
                sample = sample[X_ml.columns].fillna(0).astype(float)
                
                # Make predictions
                try:
                    prob_lr = log_reg.predict_proba(sample)[0][1]
                except:
                    prob_lr = 0
                    
                try:
                    prob_rf = rf.predict_proba(sample)[0][1]
                except:
                    prob_rf = 0
                
                predictions_data.append({
                    'RAS': ras,
                    'Position': position,
                    'LogisticRegression_Prob': prob_lr,
                    'RandomForest_Prob': prob_rf
                })
    
    # Create a dataframe and save to JSON
    predictions_df = pd.DataFrame(predictions_data)
    
    # Ensure directory exists
    os.makedirs('../../frontend/public/data', exist_ok=True)
    
    predictions_df.to_json('../../frontend/public/data/ml_predictions.json', orient='records')
    
    print("Advanced analysis complete. Results saved to backend/analysis/advanced/ and frontend/public/data/")

if __name__ == "__main__":
    perform_advanced_analysis()