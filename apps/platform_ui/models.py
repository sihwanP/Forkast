from django.db import models
from django.utils import timezone
import json

# ==========================================
# 1. CORE MASTER DATA (Partner, Product, Tax)
# ==========================================

class TaxCode(models.Model):
    name = models.CharField(max_length=50, verbose_name="세금 명칭")
    rate = models.DecimalField(max_digits=5, decimal_places=4, default=0.10, verbose_name="세율 (0.1=10%)")
    
    class Meta:
        verbose_name = "세금/과세 설정"
        verbose_name_plural = "세금 관리"

    def __str__(self):
        return f"{self.name} ({self.rate*100}%)"

class Partner(models.Model):
    TYPE_CHOICES = [('CUSTOMER', '고객'), ('SUPPLIER', '공급사'), ('BOTH', '모두')]
    name = models.CharField(max_length=100, verbose_name="거래처명")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='CUSTOMER', verbose_name="구분")
    contact_info = models.TextField(blank=True, verbose_name="연락처/비고")
    balance = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="미수/미지급금")
    
    class Meta:
        verbose_name = "거래처"
        verbose_name_plural = "거래처 관리"

    def __str__(self):
        return f"[{self.get_type_display()}] {self.name}"

class Inventory(models.Model):
    # This acts as the "Product" master
    category = models.CharField(max_length=50, default='General', verbose_name="카테고리")
    item_name = models.CharField(max_length=100, verbose_name="상품명")
    code = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="상품코드")
    
    # Stock
    current_stock = models.IntegerField(verbose_name="현재 재고")
    optimal_stock = models.IntegerField(verbose_name="적정 재고")
    status = models.CharField(max_length=50, choices=[('GOOD', '적정'), ('LOW', '부족'), ('OVER', '과잉')], default='GOOD', verbose_name="재고 상태")
    
    # Visuals
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="상품 이미지")
    
    sale_status = models.CharField(
        max_length=20, 
        choices=[('ON_SALE', '판매중'), ('STOPPED', '판매중지'), ('OUT_OF_STOCK', '품절')], 
        default='ON_SALE', 
        verbose_name="판매 상태"
    )
    is_managed = models.BooleanField(default=True, verbose_name="재고 관리 여부")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="최종 수정일")

    # Financials
    cost = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name="매입 단가")
    price = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name="판매 단가")
    tax_code = models.ForeignKey(TaxCode, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="과세 구분")

    class Meta:
        verbose_name = "상품/자재"
        verbose_name_plural = "상품 및 재고 관리"

    def __str__(self):
        return f"{self.item_name} (재고: {self.current_stock})"

# ==========================================
# 2. POS INTEGRATION & RAW DATA
# ==========================================

class PosRawSales(models.Model):
    STATUS_CHOICES = [('RECEIVED', '수신됨'), ('PROCESSED', '처리완료'), ('FAILED', '처리실패')]
    
    received_at = models.DateTimeField(auto_now_add=True, verbose_name="수신 일시")
    payload = models.JSONField(verbose_name="원본 데이터")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='RECEIVED', verbose_name="처리 상태")
    error_log = models.TextField(blank=True, verbose_name="에러 로그")
    
    class Meta:
        verbose_name = "POS 원천 데이터"
        verbose_name_plural = "POS 수신 로그"

    def __str__(self):
        return f"LOG #{self.id} - {self.status}"

class PosItemMap(models.Model):
    pos_code = models.CharField(max_length=100, unique=True, verbose_name="POS 상품코드")
    internal_product = models.ForeignKey(Inventory, on_delete=models.CASCADE, verbose_name="내부 상품 매핑")
    product_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="상품명")
    
    class Meta:
        verbose_name = "POS 상품 매핑"
        verbose_name_plural = "매핑 관리"

    def save(self, *args, **kwargs):
        if self.internal_product and not self.product_name:
            self.product_name = self.internal_product.item_name
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.pos_code} -> {self.product_name or self.internal_product.item_name}"

# ==========================================
# 3. TRANSACTIONS & MOVEMENTS
# ==========================================

class Transaction(models.Model):
    TYPE_CHOICES = [('SALE', '매철'), ('PURCHASE', '매입'), ('REFUND', '반품/취소')]
    STATUS_CHOICES = [('PENDING', '대기'), ('CONFIRMED', '확정'), ('CANCELLED', '취소')]
    
    transaction_date = models.DateTimeField(default=timezone.now, verbose_name="거래 일시")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='SALE', verbose_name="거래 유형")
    partner = models.ForeignKey(Partner, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="거래처")
    
    total_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="총 공급가액")
    tax_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="총 세액")
    final_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="최종 합계")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name="진행 상태")
    raw_pos_ref = models.ForeignKey(PosRawSales, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="POS 연동 참조")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "거래 내역"
        verbose_name_plural = "거래 관리"

    def __str__(self):
        return f"#{self.id} [{self.get_type_display()}] {self.final_amount}원"

class TransactionItem(models.Model):
    transaction = models.ForeignKey(Transaction, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Inventory, on_delete=models.CASCADE, verbose_name="상품")
    product_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="상품명")
    quantity = models.IntegerField(verbose_name="수량")
    unit_price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="단가")
    line_total = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="라인 합계")

    def save(self, *args, **kwargs):
        if self.product and not self.product_name:
            self.product_name = self.product.item_name
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)

class InventoryMovement(models.Model):
    MOVE_TYPES = [('IN', '입고'), ('OUT', '출고'), ('ADJ', '조정')]
    
    product = models.ForeignKey(Inventory, on_delete=models.CASCADE, verbose_name="상품")
    product_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="상품명")
    type = models.CharField(max_length=10, choices=MOVE_TYPES, verbose_name="유형")
    quantity = models.IntegerField(verbose_name="수량 (변동분)")
    ref_transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="관련 거래")
    reason = models.CharField(max_length=200, verbose_name="사유")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="일시")

    class Meta:
        verbose_name = "재고 수불부"
        verbose_name_plural = "입출고 이력"

    def save(self, *args, **kwargs):
        if self.product and not self.product_name:
            self.product_name = self.product.item_name
        super().save(*args, **kwargs)

# ==========================================
# 4. ANALYTICS & AI
# ==========================================

class DailySales(models.Model):
    date = models.DateField(default=timezone.now, verbose_name="날짜")
    item_name = models.CharField(max_length=200, default='All', verbose_name="상품명/구분")
    revenue = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="실매출")
    predicted_revenue = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="예상매출")
    
    class Meta:
        verbose_name = "일일 매출 집계"
        verbose_name_plural = "매출 리포트"
        unique_together = ('date', 'item_name')

class ForecastRun(models.Model):
    run_date = models.DateTimeField(auto_now_add=True, verbose_name="실행 일시")
    model_name = models.CharField(max_length=100, default="Prophet-Ensemble", verbose_name="사용 모델")
    status = models.CharField(max_length=20, default='SUCCESS', verbose_name="상태")
    accuracy_metrics = models.JSONField(default=dict, verbose_name="정확도 지표 (MAPE 등)")
    
    class Meta:
        verbose_name = "예측 모델 실행 이력"
        verbose_name_plural = "AI 모델 관리"

# ==========================================
# 5. SETTINGS & LEGACY
# ==========================================

class Member(models.Model):
    name = models.CharField(max_length=100, verbose_name="지점명")
    master_key = models.CharField(max_length=50, unique=True, verbose_name="액세스 키")
    is_approved = models.BooleanField(default=True, verbose_name="승인 상태")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="등록일")

    class Meta:
        verbose_name = "지점/사용자"
        verbose_name_plural = "사용자 및 권한"

class AuditLog(models.Model):
    user = models.CharField(max_length=100, verbose_name="사용자")
    action = models.CharField(max_length=50, verbose_name="작업")
    target = models.CharField(max_length=200, verbose_name="대상")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="일시")
    details = models.TextField(blank=True, verbose_name="상세 내용")

    class Meta:
        verbose_name = "감사 로그"
        verbose_name_plural = "시스템 감사"

# Legacy/Simple models kep for compatibility or extensions
class Weather(models.Model):
    date = models.DateField(default=timezone.now, verbose_name="날짜")
    condition = models.CharField(max_length=50, verbose_name="기상 상태")
    temperature = models.FloatField(verbose_name="기온")

    class Meta:
        verbose_name = "날씨 정보"
        verbose_name_plural = "날씨 데이터"

class LocalEvent(models.Model):
    name = models.CharField(max_length=200, verbose_name="행사명")
    date = models.DateField(verbose_name="일시")
    impact_level = models.CharField(max_length=50, verbose_name="영향도")

    class Meta:
        verbose_name = "지역 행사 정보"
        verbose_name_plural = "지역 행사 및 이벤트"

class OwnerSentiment(models.Model):
    date = models.DateField(auto_now_add=True, verbose_name="기록일")
    mood_score = models.IntegerField(default=5, verbose_name="기분 점수")
    cheer_message = models.TextField(verbose_name="응원 메시지")

    class Meta:
        verbose_name = "점주 심리 상태"
        verbose_name_plural = "점주 심리 로그"

class CommunityPost(models.Model):
    author = models.CharField(max_length=100, verbose_name="작성자")
    content = models.TextField(verbose_name="내용")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")

    class Meta:
        verbose_name = "커뮤니티 게시글"
        verbose_name_plural = "커뮤니티 관리"

class Consultation(models.Model):
    question = models.TextField(verbose_name="질문 내용")
    answer = models.TextField(blank=True, verbose_name="AI 답변")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="접수일")

    class Meta:
        verbose_name = "AI 상담 내역"
        verbose_name_plural = "AI 상담 로그"

class AdminConfig(models.Model):
    key = models.CharField(max_length=50, default="admin", verbose_name="설정 키")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        verbose_name = "관리자 환경 설정"
        verbose_name_plural = "관리자 설정"

# Order is kept as "Inbound Order" (Procurement)
class Order(models.Model):
    """ Legacy Order model - mapped to Purchase Transactions eventually """
    ORDER_TYPES = [
        ('SALES', '가맹점수주'),
        ('PURCHASE', '공급사발주'),
    ]
    item = models.ForeignKey(Inventory, on_delete=models.CASCADE, verbose_name="대상 품목")
    product_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="상품명")
    quantity = models.IntegerField(verbose_name="수량")
    status = models.CharField(max_length=20, choices=[('PENDING', '대기'), ('COMPLETED', '완료'), ('CANCELLED', '취소')], default='PENDING', verbose_name="상태")
    type = models.CharField(max_length=10, choices=ORDER_TYPES, default='SALES', verbose_name="주문 유형")
    branch_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="지점명")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="접수 일시")

    class Meta:
        verbose_name = "수주/발주 요청"
        verbose_name_plural = "수주/발주 관리"

    def save(self, *args, **kwargs):
        if self.item and not self.product_name:
            self.product_name = self.item.item_name
        super().save(*args, **kwargs)

# ==========================================
# 6. DELIVERY & LOGISTICS FLOW
# ==========================================

class Delivery(models.Model):
    STATUS_CHOICES = [
        ('PENDING', '배차 대기'),
        ('SCHEDULED', '배송 예약'),
        ('IN_TRANSIT', '배송 중'),
        ('DELIVERED', '배송 완료'),
        ('CANCELLED', '취소됨')
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery', verbose_name="연관 주문")
    product_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="상품명")
    driver_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="배송원 성함")
    vehicle_info = models.CharField(max_length=100, blank=True, null=True, verbose_name="차량 정보")
    delivery_address = models.TextField(verbose_name="배송지")
    scheduled_at = models.DateTimeField(null=True, blank=True, verbose_name="배정/예약 시간")
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name="완료 시간")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name="배송 상태")
    
    class Meta:
        verbose_name = "배송 관리"
        verbose_name_plural = "배송/물류 관리"

    def save(self, *args, **kwargs):
        if self.order and self.order.item and not self.product_name:
            self.product_name = self.order.item.item_name
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Delivery for Order #{self.order.id} - {self.get_status_badge_text()}"

    def get_status_badge_text(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

# ==========================================
# 7. PROXY MODELS FOR DEDICATED ADMIN PAGES
# ==========================================

class SalesOrder(Order):
    class Meta:
        proxy = True
        verbose_name = "수주 관리 (Sales Order)"
        verbose_name_plural = "수주 관리"

class PurchaseOrder(Order):
    class Meta:
        proxy = True
        verbose_name = "발주 관리 (Purchase Order)"
        verbose_name_plural = "발주 관리"

class Inbound(InventoryMovement):
    class Meta:
        proxy = True
        verbose_name = "입고 관리 (Inbound)"
        verbose_name_plural = "입고 관리"

class Outbound(Delivery):
    class Meta:
        proxy = True
        verbose_name = "출고 관리 (Outbound)"
        verbose_name_plural = "출고 관리"
