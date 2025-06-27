from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('создана', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('обновлена', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('пользователь', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='корзина', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Корзина',
                'verbose_name_plural': 'Корзины',
                'db_table': 'shop_cart',
            },
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('количество', models.PositiveIntegerField(verbose_name='Количество')),
                ('добавлен', models.DateTimeField(auto_now_add=True, verbose_name='Добавлен')),
                ('корзина', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='элементы', to='shop.cart', verbose_name='Корзина')),
                ('товар', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.product', verbose_name='Товар')),
            ],
            options={
                'verbose_name': 'Элемент корзины',
                'verbose_name_plural': 'Элементы корзины',
                'db_table': 'shop_cartitem',
            },
        ),
        migrations.AlterUniqueTogether(
            name='cartitem',
            unique_together={('корзина', 'товар')},
        ),
    ]