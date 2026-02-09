"""
Forecast Service: AI Sales Prediction Logic Wrapper
====================================================
This module handles the forecasting logic using Prophet (or fallback to simple regression).
It interfaces with Oracle DB via Django ORM.

ORACLE DB ASSUMPTIONS:
- Sales data exists in existing tables (read-only access)
- Forecast results are stored in SALES_FORECAST_RESULT table
- Batch logs are stored in FORECAST_BATCH_LOG table
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import random

# Django imports
from django.db import connection
from django.utils import timezone


class ForecastService:
    """
    Service layer for AI sales forecasting.
    Wraps model execution, data retrieval, and result storage.
    """

    MODEL_VERSION = "v2.3.1"

    def __init__(self, store_id: Optional[str] = None, channel: Optional[str] = None):
        self.store_id = store_id
        self.channel = channel

    # =========================================
    # DATA RETRIEVAL (FROM ORACLE)
    # =========================================

    def get_daily_sales_aggregate(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Fetch aggregated daily sales from SALES_DAILY_AGG_MV.
        
        Args:
            start_date: YYYY-MM-DD format
            end_date: YYYY-MM-DD format
            
        Returns:
            List of dicts with: sale_date, total_sales, order_count, avg_ticket
        """
        # STUB: In production, this would query Oracle
        # Example SQL:
        # SELECT sale_date, total_sales, order_count, avg_ticket
        # FROM SALES_DAILY_AGG_MV
        # WHERE sale_date BETWEEN :start AND :end
        #   AND (:store_id IS NULL OR store_id = :store_id)
        #   AND (:channel IS NULL OR channel = :channel)
        # ORDER BY sale_date DESC
        
        # Dummy data for MVP
        result = []
        current = datetime.strptime(end_date, "%Y-%m-%d")
        for i in range(30):
            day = current - timedelta(days=i)
            result.append({
                'sale_date': day.strftime("%Y-%m-%d"),
                'total_sales': random.randint(1200, 2100) * 10000,  # 1200~2100만원
                'order_count': random.randint(80, 150),
                'avg_ticket': random.randint(15000, 25000),
            })
        return result

    def get_forecast_results(self, horizon_days: int = 7) -> List[Dict]:
        """
        Fetch stored forecast results from SALES_FORECAST_RESULT.
        
        Args:
            horizon_days: Prediction horizon (7, 14, or 30)
            
        Returns:
            List of dicts with: forecast_date, predicted_sales, lower_bound, upper_bound, actual_sales, error_rate
        """
        # STUB: In production, this would query Oracle
        # Example SQL:
        # SELECT f.forecast_date, f.predicted_sales, f.lower_bound, f.upper_bound,
        #        a.total_sales AS actual_sales,
        #        CASE WHEN a.total_sales IS NOT NULL 
        #             THEN ROUND((f.predicted_sales - a.total_sales) / a.total_sales * 100, 1)
        #             ELSE NULL END AS error_rate
        # FROM SALES_FORECAST_RESULT f
        # LEFT JOIN SALES_DAILY_AGG_MV a ON f.forecast_date = a.sale_date
        # WHERE f.horizon_days = :horizon AND f.store_id = :store_id
        # ORDER BY f.forecast_date DESC
        
        # Dummy data for MVP
        result = []
        today = datetime.now()
        
        for i in range(-3, horizon_days):  # 과거 3일 + 미래 horizon일
            day = today + timedelta(days=i)
            predicted = random.randint(1400, 2000) * 10000
            
            if i < 0:  # 과거 데이터 (실제값 있음)
                actual = predicted + random.randint(-300, 300) * 10000
                error = round((predicted - actual) / actual * 100, 1)
            else:  # 미래 데이터 (실제값 없음)
                actual = None
                error = None
            
            result.append({
                'forecast_date': day.strftime("%Y-%m-%d"),
                'predicted_sales': predicted,
                'lower_bound': int(predicted * 0.85),
                'upper_bound': int(predicted * 1.15),
                'actual_sales': actual,
                'error_rate': error,
            })
        
        return sorted(result, key=lambda x: x['forecast_date'], reverse=True)

    # =========================================
    # FORECAST EXECUTION
    # =========================================

    def run_forecast(self, horizon_days: int = 7) -> Dict:
        """
        Execute forecast model and store results.
        
        This is the main entry point for batch jobs.
        
        Args:
            horizon_days: Number of days to predict
            
        Returns:
            Dict with: run_id, status, rows_processed, model_version
        """
        run_id = str(uuid.uuid4())
        started_at = datetime.now()
        
        try:
            # Step 1: Get historical data
            historical = self.get_daily_sales_aggregate(
                start_date=(datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d"),
                end_date=datetime.now().strftime("%Y-%m-%d")
            )
            
            # Step 2: Run prediction (simplified linear regression for MVP)
            predictions = self._simple_forecast(historical, horizon_days)
            
            # Step 3: Store results (would use MERGE INTO in production)
            rows_processed = len(predictions)
            
            # Step 4: Log batch execution
            self._log_batch(run_id, started_at, 'SUCCESS', rows_processed, None)
            
            return {
                'run_id': run_id,
                'status': 'SUCCESS',
                'rows_processed': rows_processed,
                'model_version': self.MODEL_VERSION,
            }
            
        except Exception as e:
            self._log_batch(run_id, started_at, 'FAILED', 0, str(e))
            return {
                'run_id': run_id,
                'status': 'FAILED',
                'rows_processed': 0,
                'error': str(e),
            }

    def _simple_forecast(self, historical: List[Dict], horizon: int) -> List[Dict]:
        """
        Simple moving average forecast (MVP).
        In production, replace with Prophet or ARIMA.
        """
        if not historical:
            return []
        
        # Calculate 7-day moving average
        recent_sales = [h['total_sales'] for h in historical[:7]]
        avg_sales = sum(recent_sales) / len(recent_sales) if recent_sales else 0
        
        predictions = []
        for i in range(1, horizon + 1):
            pred_date = datetime.now() + timedelta(days=i)
            # Add some randomness for demo
            predicted = avg_sales * (1 + random.uniform(-0.1, 0.1))
            
            predictions.append({
                'forecast_date': pred_date.strftime("%Y-%m-%d"),
                'store_id': self.store_id,
                'channel': self.channel,
                'horizon_days': horizon,
                'predicted_sales': predicted,
                'lower_bound': predicted * 0.85,
                'upper_bound': predicted * 1.15,
                'model_version': self.MODEL_VERSION,
            })
        
        return predictions

    def _log_batch(self, run_id: str, started_at: datetime, status: str, 
                   rows: int, error_msg: Optional[str]):
        """
        Log batch execution to FORECAST_BATCH_LOG.
        In production, this would INSERT/UPDATE to Oracle.
        """
        # STUB: Would execute SQL like:
        # INSERT INTO FORECAST_BATCH_LOG (run_id, started_at, ended_at, status, rows_processed, model_version, error_message)
        # VALUES (:run_id, :started_at, SYSTIMESTAMP, :status, :rows, :model_ver, :error)
        pass

    # =========================================
    # KPI CALCULATIONS
    # =========================================

    def get_kpi_summary(self) -> Dict:
        """
        Calculate KPI metrics for the dashboard.
        
        Returns:
            Dict with: expected_sales, week_over_week_change, target_achievement, anomaly_count
        """
        forecasts = self.get_forecast_results(7)
        future_forecasts = [f for f in forecasts if f['actual_sales'] is None]
        past_forecasts = [f for f in forecasts if f['actual_sales'] is not None]
        
        # Expected sales (next 7 days)
        expected_sales = sum(f['predicted_sales'] for f in future_forecasts)
        
        # Week over week change
        historical = self.get_daily_sales_aggregate(
            start_date=(datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d"),
            end_date=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        )
        last_week_sales = sum(h['total_sales'] for h in historical[:7])
        wow_change = ((expected_sales - last_week_sales) / last_week_sales * 100) if last_week_sales else 0
        
        # Target achievement (assuming 13200만원 target)
        target = 132000000
        achievement = (expected_sales / target * 100) if target else 0
        
        # Anomaly count (error > 15%)
        anomalies = len([f for f in past_forecasts if f['error_rate'] and abs(f['error_rate']) > 15])
        
        return {
            'expected_sales': expected_sales,
            'week_over_week_change': round(wow_change, 1),
            'target_achievement': round(achievement, 1),
            'anomaly_count': anomalies,
        }


# =========================================
# API INTERFACE (for views.py)
# =========================================

def get_forecast_dashboard_data(store_id=None, channel=None, horizon=7):
    """
    Main API function to get all data needed for the forecast dashboard.
    Called by sales_forecast_view.
    """
    service = ForecastService(store_id=store_id, channel=channel)
    
    return {
        'kpi': service.get_kpi_summary(),
        'forecasts': service.get_forecast_results(horizon),
        'historical': service.get_daily_sales_aggregate(
            start_date=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
            end_date=datetime.now().strftime("%Y-%m-%d")
        ),
        'model_version': service.MODEL_VERSION,
    }


def trigger_forecast_batch(horizon=7):
    """
    Manually trigger a forecast batch run.
    Called when user clicks "배치실행" button.
    """
    service = ForecastService()
    return service.run_forecast(horizon_days=horizon)
