from django.db import models
from django.utils import timezone

class DailySales(models.Model):
    date = models.DateField(default=timezone.now, verbose_name="날짜")
    item_name = models.CharField(max_length=200, default='General', verbose_name="상품명")
    revenue = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="실매출")
    predicted_revenue = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="예상매출")
    weather_impact = models.CharField(max_length=100, blank=True, verbose_name="날씨 영향")
    event_impact = models.CharField(max_length=100, blank=True, verbose_name="이벤트 영향")

    class Meta:
        verbose_name = "일일 매출"
        verbose_name_plural = "일일 매출 목록"
        unique_together = ('date', 'item_name')

    def __str__(self):
        return f"{self.date} - {self.item_name} - {self.revenue}"

class Inventory(models.Model):
    item_name = models.CharField(max_length=100, verbose_name="상품명")
    current_stock = models.IntegerField(verbose_name="현재 재고")
    optimal_stock = models.IntegerField(verbose_name="적정 재고")
    status = models.CharField(max_length=50, choices=[('GOOD', '적정'), ('LOW', '부족'), ('OVER', '과잉')], default='GOOD', verbose_name="상태")

    class Meta:
        verbose_name = "재고 항목"
        verbose_name_plural = "재고 관리 목록"

    def __str__(self):
        return self.item_name

class Weather(models.Model):
    date = models.DateField(default=timezone.now, verbose_name="날짜")
    condition = models.CharField(max_length=50, verbose_name="날씨 상태")
    temperature = models.FloatField(verbose_name="온도")

    class Meta:
        verbose_name = "날씨 정보"
        verbose_name_plural = "날씨 데이터 목록"

    def __str__(self):
        return f"{self.date}: {self.condition}"

class LocalEvent(models.Model):
    name = models.CharField(max_length=200, verbose_name="이벤트명")
    date = models.DateField(verbose_name="날짜")
    impact_level = models.CharField(max_length=50, verbose_name="매출 영향도")

    class Meta:
        verbose_name = "지역 이벤트"
        verbose_name_plural = "지역 이벤트 목록"

    def __str__(self):
        return self.name

class OwnerSentiment(models.Model):
    date = models.DateField(auto_now_add=True)
    mood_score = models.IntegerField(default=5, verbose_name="기분 점수 (1-10)")
    cheer_message = models.TextField(verbose_name="응원 메시지")

    class Meta:
        verbose_name = "점주 기분/심리"
        verbose_name_plural = "점주 심리 상태 목록"

    def __str__(self):
        return f"{self.date} - Score: {self.mood_score}"

class CommunityPost(models.Model):
    author = models.CharField(max_length=100, verbose_name="작성자")
    content = models.TextField(verbose_name="내용")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")

    class Meta:
        verbose_name = "커뮤니티 게시글"
        verbose_name_plural = "커뮤니티 게시판"

    def __str__(self):
        return f"{self.author}: {self.content[:20]}"

class Consultation(models.Model):
    question = models.TextField(verbose_name="질문")
    answer = models.TextField(verbose_name="AI 답변", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="접수일")

    class Meta:
        verbose_name = "AI 상담 내역"
        verbose_name_plural = "AI 상담 로그"

    def __str__(self):
        return self.question[:30]

class Member(models.Model):
    name = models.CharField(max_length=100, verbose_name="회원명")
    master_key = models.CharField(max_length=50, unique=True, verbose_name="마스터 키")
    is_approved = models.BooleanField(default=True, verbose_name="승인 상태")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="등록일")

    class Meta:
        verbose_name = "지점 파트너"
        verbose_name_plural = "지점 관리 목록"

    def __str__(self):
        return self.name

class AdminConfig(models.Model):
    key = models.CharField(max_length=50, default="admin", verbose_name="관리자 키")
    # master_key removed to rely on Memeber model and fix DB mismatch
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        verbose_name = "관리자 설정"
        verbose_name_plural = "관리자 설정 항목"

    def __str__(self):
        return "Admin Configuration"

class Order(models.Model):
    item = models.ForeignKey(Inventory, on_delete=models.CASCADE, verbose_name="발주 상품")
    quantity = models.IntegerField(verbose_name="수량")
    status = models.CharField(max_length=20, choices=[('PENDING', '대기'), ('COMPLETED', '완료'), ('CANCELLED', '취소')], default='PENDING', verbose_name="상태")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="주문 일시")

    class Meta:
        verbose_name = "수주/입고 내역"
        verbose_name_plural = "수주/입고 관리 목록"

    def __str__(self):
        return f"{self.item.item_name} - {self.quantity}개 ({self.status})"
