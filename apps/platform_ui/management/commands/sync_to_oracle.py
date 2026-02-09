"""
SQLite -> Oracle DB (ADMIN 스키마) 전체 동기화 커맨드
사용법: python manage.py sync_to_oracle [--user USER] [--password PASSWORD] [--schema SCHEMA]

DBeaver 등 Oracle 클라이언트에서 데이터를 확인할 수 있도록,
SQLite에 저장된 모든 모델 데이터를 Oracle DB ADMIN 스키마에 MERGE(upsert) 합니다.
"""
import oracledb
from django.core.management.base import BaseCommand
from apps.platform_ui.models import (
    Inventory, Order, Delivery, InventoryMovement,
    DailySales, Member,
)


class Command(BaseCommand):
    help = 'SQLite의 모든 데이터를 Oracle DB ADMIN 스키마에 동기화합니다.'

    def add_arguments(self, parser):
        parser.add_argument('--user', type=str, default='master', help='Oracle 사용자명')
        parser.add_argument('--password', type=str, default='master1234', help='Oracle 비밀번호')
        parser.add_argument('--host', type=str, default='localhost', help='Oracle 호스트')
        parser.add_argument('--port', type=int, default=1521, help='Oracle 포트')
        parser.add_argument('--service', type=str, default='xe', help='Oracle 서비스명')
        parser.add_argument('--schema', type=str, default='ADMIN', help='대상 Oracle 스키마')

    def handle(self, *args, **options):
        user = options['user']
        password = options['password']
        host = options['host']
        port = options['port']
        service = options['service']
        self.schema = options['schema']

        self.stdout.write(f'Oracle DB 연결 중... ({user}@{host}:{port}/{service}, 스키마: {self.schema})')

        try:
            conn = oracledb.connect(
                user=user, password=password,
                host=host, port=port, service_name=service
            )
            cursor = conn.cursor()
            self.stdout.write(self.style.SUCCESS('Oracle DB 연결 성공!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Oracle DB 연결 실패: {e}'))
            return

        try:
            self.sync_inventory(cursor)
            self.sync_orders(cursor)
            self.sync_movements(cursor)
            self.sync_daily_sales(cursor)
            self.sync_members(cursor)

            conn.commit()
            self.stdout.write(self.style.SUCCESS('\n✅ Oracle DB 동기화 완료!'))

        except Exception as e:
            conn.rollback()
            self.stdout.write(self.style.ERROR(f'\n❌ 동기화 중 오류: {e}'))
            import traceback
            traceback.print_exc()
        finally:
            cursor.close()
            conn.close()

    def sync_inventory(self, cursor):
        """[Inventory] 상품/자재 마스터 → ADMIN.PLATFORM_UI_INVENTORY"""
        self.stdout.write('\n📦 Inventory 동기화...')
        items = Inventory.objects.all()
        count = 0
        for item in items:
            try:
                cursor.execute(f'''
                    MERGE INTO {self.schema}.PLATFORM_UI_INVENTORY t
                    USING (SELECT :id AS ID FROM DUAL) s
                    ON (t.ID = s.ID)
                    WHEN MATCHED THEN UPDATE SET
                        ITEM_NAME = :name, CODE = :code, CATEGORY = :cat,
                        CURRENT_STOCK = :stock, OPTIMAL_STOCK = :opt,
                        STATUS = :stat, COST = :cost, PRICE = :price
                    WHEN NOT MATCHED THEN INSERT
                        (ID, ITEM_NAME, CODE, CATEGORY, CURRENT_STOCK, OPTIMAL_STOCK, STATUS, COST, PRICE)
                    VALUES (:id, :name, :code, :cat, :stock, :opt, :stat, :cost, :price)
                ''', {
                    'id': item.id, 'name': item.item_name,
                    'code': item.code or '', 'cat': item.category,
                    'stock': item.current_stock, 'opt': item.optimal_stock,
                    'stat': item.status,
                    'cost': int(item.cost), 'price': int(item.price),
                })
                count += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  ⚠ #{item.id} ({item.item_name}): {e}'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ {count}/{items.count()}건'))

    def sync_orders(self, cursor):
        """[Order] 수주/발주 → ADMIN.PLATFORM_UI_ORDER"""
        self.stdout.write('\n📋 Order 동기화...')
        orders = Order.objects.all()
        count = 0
        for o in orders:
            try:
                cursor.execute(f'''
                    MERGE INTO {self.schema}.PLATFORM_UI_ORDER t
                    USING (SELECT :id AS ID FROM DUAL) s
                    ON (t.ID = s.ID)
                    WHEN MATCHED THEN UPDATE SET
                        ITEM_ID = :item_id, QUANTITY = :qty, STATUS = :stat
                    WHEN NOT MATCHED THEN INSERT
                        (ID, ITEM_ID, QUANTITY, STATUS, CREATED_AT)
                    VALUES (:id, :item_id, :qty, :stat, :created)
                ''', {
                    'id': o.id, 'item_id': o.item_id,
                    'qty': o.quantity, 'stat': o.status,
                    'created': o.created_at,
                })
                count += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  ⚠ Order #{o.id}: {e}'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ {count}/{orders.count()}건'))

    def sync_movements(self, cursor):
        """[InventoryMovement] 입출고 이력 → ADMIN.PLATFORM_UI_INVENTORYMOVEMENT"""
        self.stdout.write('\n📊 InventoryMovement 동기화...')
        moves = InventoryMovement.objects.all()
        count = 0
        for m in moves:
            try:
                cursor.execute(f'''
                    MERGE INTO {self.schema}.PLATFORM_UI_INVENTORYMOVEMENT t
                    USING (SELECT :id AS ID FROM DUAL) s
                    ON (t.ID = s.ID)
                    WHEN MATCHED THEN UPDATE SET
                        PRODUCT_ID = :pid, TYPE = :type, QUANTITY = :qty, REASON = :reason
                    WHEN NOT MATCHED THEN INSERT
                        (ID, PRODUCT_ID, TYPE, QUANTITY, REASON, CREATED_AT)
                    VALUES (:id, :pid, :type, :qty, :reason, :created)
                ''', {
                    'id': m.id, 'pid': m.product_id, 'type': m.type,
                    'qty': m.quantity, 'reason': m.reason, 'created': m.created_at,
                })
                count += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  ⚠ #{m.id}: {e}'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ {count}/{moves.count()}건'))

    def sync_daily_sales(self, cursor):
        """[DailySales] 일일 매출 → ADMIN.PLATFORM_UI_DAILYSALES"""
        self.stdout.write('\n💰 DailySales 동기화...')
        sales = DailySales.objects.all()
        count = 0
        errors = 0
        for s in sales:
            try:
                cursor.execute(f'''
                    MERGE INTO {self.schema}.PLATFORM_UI_DAILYSALES t
                    USING (SELECT :id AS ID FROM DUAL) s
                    ON (t.ID = s.ID)
                    WHEN MATCHED THEN UPDATE SET
                        "DATE" = :dt, ITEM_NAME = :name,
                        REVENUE = :rev, PREDICTED_REVENUE = :pred
                    WHEN NOT MATCHED THEN INSERT
                        (ID, "DATE", ITEM_NAME, REVENUE, PREDICTED_REVENUE)
                    VALUES (:id, :dt, :name, :rev, :pred)
                ''', {
                    'id': s.id, 'dt': s.date, 'name': s.item_name,
                    'rev': int(s.revenue),
                    'pred': int(s.predicted_revenue) if s.predicted_revenue else 0,
                })
                count += 1
            except Exception as e:
                errors += 1
                if errors <= 3:
                    self.stdout.write(self.style.WARNING(f'  ⚠ #{s.id}: {e}'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ {count}/{sales.count()}건 (에러: {errors}건)'))

    def sync_members(self, cursor):
        """[Member] 지점/사용자 → ADMIN.PLATFORM_UI_MEMBER"""
        self.stdout.write('\n👥 Member 동기화...')
        members = Member.objects.all()
        count = 0
        for m in members:
            try:
                cursor.execute(f'''
                    MERGE INTO {self.schema}.PLATFORM_UI_MEMBER t
                    USING (SELECT :id AS ID FROM DUAL) s
                    ON (t.ID = s.ID)
                    WHEN MATCHED THEN UPDATE SET
                        NAME = :name, MASTER_KEY = :key, IS_APPROVED = :approved
                    WHEN NOT MATCHED THEN INSERT
                        (ID, NAME, MASTER_KEY, IS_APPROVED, CREATED_AT)
                    VALUES (:id, :name, :key, :approved, :created)
                ''', {
                    'id': m.id, 'name': m.name, 'key': m.master_key,
                    'approved': 1 if m.is_approved else 0,
                    'created': m.created_at,
                })
                count += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  ⚠ #{m.id}: {e}'))
        self.stdout.write(self.style.SUCCESS(f'  ✓ {count}/{members.count()}건'))
