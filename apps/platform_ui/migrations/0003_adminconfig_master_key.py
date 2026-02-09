from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('platform_ui', '0002_adminconfig'),
    ]

    operations = [
        migrations.AddField(
            model_name='adminconfig',
            name='master_key',
            field=models.CharField(default='master', max_length=50, verbose_name='마스터 키'),
        ),
    ]
