from django.db import migrations, models
import django.core.validators
import django.db.models.deletion
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_rebuild_cart'),
    ]

    operations = [
        migrations.RunSQL("DROP TABLE IF EXISTS shop_product;"),
        migrations.RunSQL("DROP TABLE IF EXISTS shop_category;"),
        migrations.RunSQL("DROP TABLE IF EXISTS shop_manufacturer;"),
        
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('название', models.CharField(max_length=100)),
                ('описание', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Категория товара',
                'verbose_name_plural': 'Категории товаров',
            },
        ),
        
        migrations.CreateModel(
            name='Manufacturer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('название', models.CharField(max_length=100)),
                ('страна', models.CharField(max_length=100)),
                ('описание', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Производитель',
                'verbose_name_plural': 'Производители',
            },
        ),
        
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('название', models.CharField(max_length=200)),
                ('описание', models.TextField()),
                ('фото_товара', models.ImageField(blank=True, null=True, upload_to='products/')),
                ('цена', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('количество_на_складе', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('категория', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.category')),
                ('производитель', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.manufacturer')),
            ],
            options={
                'verbose_name': 'Товар',
                'verbose_name_plural': 'Товары',
            },
        ),
    ]