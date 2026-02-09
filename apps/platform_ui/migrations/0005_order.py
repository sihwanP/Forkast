from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('platform_ui', '0004_member'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(verbose_name='발주 수량')),
                ('status', models.CharField(choices=[('PENDING', '대기'), ('COMPLETED', '완료'), ('CANCELLED', '취소')], default='PENDING', max_length=20, verbose_name='상태')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='발주 일시')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='platform_ui.inventory', verbose_name='발주 상품')),
            ],
        ),
    ]
