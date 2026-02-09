"""
Django Management Command: run_forecast_batch
==============================================
Scheduled batch job for AI sales forecasting.

Usage:
    python manage.py run_forecast_batch
    python manage.py run_forecast_batch --horizon 14
    python manage.py run_forecast_batch --store S001 --channel DELIVERY

Schedule with cron:
    10 3 * * * cd /path/to/project && python manage.py run_forecast_batch >> /var/log/forecast.log 2>&1
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run AI sales forecast batch job'

    def add_arguments(self, parser):
        parser.add_argument(
            '--horizon',
            type=int,
            default=7,
            help='Forecast horizon in days (default: 7)'
        )
        parser.add_argument(
            '--store',
            type=str,
            default=None,
            help='Store ID filter (default: all stores)'
        )
        parser.add_argument(
            '--channel',
            type=str,
            default=None,
            help='Channel filter: STORE or DELIVERY (default: all)'
        )

    def handle(self, *args, **options):
        horizon = options['horizon']
        store_id = options['store']
        channel = options['channel']

        self.stdout.write(self.style.NOTICE(
            f"[{timezone.now()}] Starting forecast batch..."
        ))
        self.stdout.write(f"  Horizon: {horizon} days")
        self.stdout.write(f"  Store: {store_id or 'ALL'}")
        self.stdout.write(f"  Channel: {channel or 'ALL'}")

        try:
            # Import here to avoid circular imports
            from platform_ui.services.forecast_service import ForecastService

            # Step 1: Initialize service
            service = ForecastService(store_id=store_id, channel=channel)

            # Step 2: Run forecast
            self.stdout.write(self.style.NOTICE("  [1/4] Fetching historical data..."))
            result = service.run_forecast(horizon_days=horizon)

            # Step 3: Report results
            if result['status'] == 'SUCCESS':
                self.stdout.write(self.style.SUCCESS(
                    f"  [2/4] Forecast completed successfully!"
                ))
                self.stdout.write(f"  [3/4] Rows processed: {result['rows_processed']}")
                self.stdout.write(f"  [4/4] Model version: {result['model_version']}")
                self.stdout.write(self.style.SUCCESS(
                    f"\n✅ Batch completed: {result['run_id']}"
                ))
            else:
                self.stdout.write(self.style.ERROR(
                    f"  ❌ Forecast failed: {result.get('error', 'Unknown error')}"
                ))
                return

            # Step 4: Check for anomalies
            kpi = service.get_kpi_summary()
            if kpi['anomaly_count'] > 0:
                self.stdout.write(self.style.WARNING(
                    f"\n⚠️ ALERT: {kpi['anomaly_count']} anomalies detected (error > 15%)"
                ))
                # In production, this would trigger notifications
                # send_anomaly_alert(kpi['anomaly_count'])

        except Exception as e:
            logger.exception("Forecast batch failed")
            self.stdout.write(self.style.ERROR(f"Batch failed with error: {e}"))
            raise
