import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from platform_ui.models import Weather, Inventory, LocalEvent

class Command(BaseCommand):
    help = 'Generates environment data (Weather, Inventory, Events)'

    def handle(self, *args, **kwargs):
        self.stdout.write("Generating environment data...")
        
        # 1. Weather (Today)
        today = timezone.now().date()
        Weather.objects.filter(date=today).delete()
        Weather.objects.create(
            date=today,
            condition=random.choice(["맑음", "약간 흐림", "비", "눈"]),
            temperature=random.uniform(5.0, 25.0)
        )
        
        # 2. Inventory (Reset & Randomize)
        Inventory.objects.all().delete()
        items = [
            ("A세트 (시그니처)", 50, 60), 
            ("B세트 (프리미엄)", 10, 30), # Low stock
            ("C세트 (가성비)", 100, 80), # Over stock
            ("단품 메뉴", 40, 40), 
            ("음료", 200, 200)
        ]
        for name, current, optimal in items:
            status = 'GOOD'
            if current < optimal * 0.5: status = 'LOW'
            elif current > optimal * 1.2: status = 'OVER'
            
            Inventory.objects.create(
                item_name=name,
                current_stock=current,
                optimal_stock=optimal,
                status=status
            )
            
        # 3. Local Events
        LocalEvent.objects.all().delete()
        if random.random() > 0.3: # 70% chance of event
            LocalEvent.objects.create(
                name="지역 벚꽃 축제",
                date=today,
                impact_level="HIGH"
            )
            
        self.stdout.write(self.style.SUCCESS('Successfully generated environment data'))
