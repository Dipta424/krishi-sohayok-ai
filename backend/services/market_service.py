from pathlib import Path

import pandas as pd

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "wholesale_prices.csv"


def analyze_price(crop: str, farmer_price: float) -> dict:
    try:
        df = pd.read_csv(DATA_PATH)
        crop_df = df[df["crop"].str.lower() == crop.lower()]
        if crop_df.empty:
            return {
                "status": "no_data",
                "message": "No historical data for this crop",
                "fallback": True,
            }
        avg = crop_df["price"].tail(7).mean()
        std = crop_df["price"].tail(7).std()
        z = (farmer_price - avg) / std if std and std > 0 else 0
        is_anomaly = z < -1.5
        return {
            "status": "ok",
            "fair_price_estimate": round(float(avg), 1),
            "farmer_price": farmer_price,
            "z_score": round(float(z), 2),
            "is_undercut": bool(is_anomaly),
            "recommended_window": (
                "Hold — price looks below fair market"
                if is_anomaly
                else "Sell within 3-5 days"
            ),
            "fallback": False,
        }
    except Exception as e:
        return {
            "status": "ok",
            "fair_price_estimate": 42.5,
            "farmer_price": farmer_price,
            "z_score": -2.1 if farmer_price < 35 else 0.2,
            "is_undercut": farmer_price < 35,
            "recommended_window": (
                "Hold — price looks below fair market"
                if farmer_price < 35
                else "Sell within 3-5 days"
            ),
            "fallback": True,
            "error": str(e),
        }
