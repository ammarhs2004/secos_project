graph TD
    A[Incoming POST: /api/v1/ml/predict] --> B[Data Parser]
    B --> C[Extract Weather: Temp, Humidity, Condition]
    B --> D[Extract Lags: Historical kWh & Multiplier]
    C --> E[Feature Engineering & Normalization]
    D --> E
    E --> F{Model Inference Routing}
    F -->|Basic Prediction| G[Linear Regression Model]
    F -->|Pattern Forecasting| H[Random Forest Model]
    G --> I[Result Aggregation]
    H --> I
    I --> J[Format Output: 7-14 Day Predicted kWh JSON]