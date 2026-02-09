from django.core.management.base import BaseCommand
from platform_ui.models import Inventory
import random

class Command(BaseCommand):
    help = 'Generates dummy inventory data'

    def handle(self, *args, **kwargs):
        items = [
            {"name": "염지 닭 (10호)", "optimal": 50},
            {"name": "치킨 파우더 (10kg)", "optimal": 10},
            {"name": "식용유 (18L)", "optimal": 5},
            {"name": "양념 소스 (10kg)", "optimal": 5},
            {"name": "치킨 무 (Box)", "optimal": 20},
            {"name": "콜라 1.25L", "optimal": 60},
            {"name": "포장용 박스", "optimal": 100},
            {"name": "나무 젓가락", "optimal": 200},
        ]

        self.stdout.write("Initializing Inventory Data...")
        
        # Clear existing data? Or just add if missing?
        # Let's clear to ensure clean slate for demo
        # [Inventory 테이블] 상품/자재 마스터 (상품명, 현재고, 적정재고, 상태)
        Inventory.objects.all().delete()
        
        for item in items:
            # Randomize current stock around optimal
            current = int(item["optimal"] * random.uniform(0.4, 1.2))
            
            # Determine status
            ratio = current / item["optimal"]
            if ratio < 0.3:
                status = 'LOW'
            elif ratio > 1.5:
                status = 'OVER'
            else:
                status = 'GOOD'
                
            # [Inventory 테이블] 상품/자재 마스터 (상품명, 현재고, 적정재고, 상태)
            Inventory.objects.create(
                item_name=item["name"],
                current_stock=current,
                optimal_stock=item["optimal"],
                status=status
            )
            
        self.stdout.write(self.style.SUCCESS(f'Successfully generated {len(items)} inventory items.'))
