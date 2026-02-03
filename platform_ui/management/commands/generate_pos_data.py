import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from platform_ui.models import DailySales

class Command(BaseCommand):
    help = 'Generates 30 days of dummy POS data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Generating dummy data...")
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=29)
        
        # Clear existing data for cleaner demo
        DailySales.objects.all().delete()
        
        for i in range(30):
            current_date = start_date + timedelta(days=i)
            is_weekend = current_date.weekday() >= 5
            
            # Base revenue: 800k ~ 1.2m
            base = random.randint(800000, 1200000)
            
            # Weekend boost (1.2x ~ 1.5x)
            if is_weekend:
                base = int(base * random.uniform(1.2, 1.5))
            
            # Random noise
            revenue = base + random.randint(-50000, 50000)
            
            # Predicted revenue (usually close to actual)
            predicted = int(revenue * random.uniform(0.9, 1.1))
            
            weather = random.choice(["맑음", "구름조금", "비", "흐림"])
            
            DailySales.objects.create(
                date=current_date,
                revenue=revenue,
                predicted_revenue=predicted,
                weather_impact=weather
            )
            
        self.stdout.write(self.style.SUCCESS(f"Successfully created 30 days of sales data from {start_date} to {end_date}"))
