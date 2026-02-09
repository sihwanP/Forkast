from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db.models import Sum
from .models import Transaction, TransactionItem, InventoryMovement, Inventory, DailySales, Order

@receiver(post_save, sender=Transaction)
def handle_transaction_confirmation(sender, instance, created, **kwargs):
    """
    Core Logic:
    1. If Transaction confirmed -> Create InventoryMovement -> Update Stock
    2. Update DailySales (Simple Aggregation)
    """
    if instance.status == 'CONFIRMED':
        # Check if movements already exist to avoid double counting
        # (Naive check: if any movement references this transaction)
        if InventoryMovement.objects.filter(ref_transaction=instance).exists():
            return

        # Process Items
        for item in instance.items.all():
            product = item.product
            qty = item.quantity
            
            # Determine Movement Type & Direction
            if instance.type == 'SALE':
                move_type = 'OUT'
                reason = f"매출 확정 (#{instance.id})"
                change = -qty
            elif instance.type == 'PURCHASE':
                move_type = 'IN'
                reason = f"매입 입고 (#{instance.id})"
                change = qty
            elif instance.type == 'REFUND':
                move_type = 'IN' # Return is IN
                reason = f"반품 입고 (#{instance.id})"
                change = qty
            else:
                continue

            # 1. Create Log
            InventoryMovement.objects.create(
                product=product,
                type=move_type,
                quantity=qty, # Log absolute quantity usually, but context matters
                ref_transaction=instance,
                reason=reason
            )

            # 2. Update Master Stock
            product.current_stock += change
            product.save()

        # 3. Update Daily Sales (If Sale)
        if instance.type == 'SALE':
            update_daily_sales(instance.transaction_date.date())

def update_daily_sales(target_date):
    """
    Aggregates all CONFIRMED SALES for the day and updates DailySales.
    """
    # 1. Total Daily Revenue
    daily_total = Transaction.objects.filter(
        type='SALE',
        status='CONFIRMED', 
        transaction_date__date=target_date
    ).aggregate(Sum('final_amount'))['final_amount__sum'] or 0

    # Update 'All' Item (General Total)
    ds, _ = DailySales.objects.get_or_create(date=target_date, item_name='All', defaults={'revenue': 0, 'predicted_revenue': 0})
    ds.revenue = daily_total
    ds.save()
@receiver(post_save, sender=Order)
def handle_order_movement(sender, instance, created, **kwargs):
    """
    Tracks Order status changes to create InventoryMovement records.
    Store Inbound (Procurement) = HQ Outbound (Logistics)
    """
    if instance.status == 'COMPLETED':
        # Prevent duplicate logs
        if InventoryMovement.objects.filter(reason__icontains=f"수주 완료 (#{instance.id})").exists():
            return
            
        InventoryMovement.objects.create(
            product=instance.item,
            type='IN',
            quantity=instance.quantity,
            reason=f"수주 입고 완료 (#{instance.id})"
        )
