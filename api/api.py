from fastapi import FastAPI
import pandas as pd

# Create FastAPI app
app = FastAPI()

# Load CSV file
df = pd.read_csv("../data/all_state_forecasts.csv")

# Print column names in terminal
print(df.columns)

# Home Route
@app.get("/")
def home():
    return {
        "message": "Sales Forecasting REST API Running"
    }

# Get all states
@app.get("/states")
def get_states():

    states = df["State"].unique().tolist()

    return {
        "states": states
    }

# Get forecast by state
@app.get("/forecast/{state_name}")
def get_forecast(state_name: str):

    state_data = df[
        df["State"].str.lower() == state_name.lower()
    ]

    if state_data.empty:
        return {
            "error": "State not found"
        }

    result = state_data.to_dict(orient="records")

    return {
        "state": state_name,
        "forecast": result
    }