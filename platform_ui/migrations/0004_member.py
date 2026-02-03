from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('platform_ui', '0003_adminconfig_master_key'),
    ]

    operations = [
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='회원명')),
                ('master_key', models.CharField(max_length=50, unique=True, verbose_name='마스터 키')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
