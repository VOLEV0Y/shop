from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def link_addresses_to_auth_users(apps, schema_editor):
    Address = apps.get_model('shop_app', 'Address')
    Order = apps.get_model('shop_app', 'Order')
    ShopUser = apps.get_model('shop_app', 'User')
    AuthUser = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))
    fallback = AuthUser.objects.filter(is_superuser=True).order_by('id').first() or AuthUser.objects.order_by('id').first()
    for address in Address.objects.all():
        owner_id = None
        order = Order.objects.filter(address_id=address.pk).first()
        if order:
            owner_id = order.user_id
        if owner_id is None:
            shop_user = ShopUser.objects.filter(pk=address.user_id).first()
            if shop_user:
                match = AuthUser.objects.filter(username__iexact=shop_user.nickname).first()
                if match:
                    owner_id = match.pk
        if owner_id is None and fallback:
            owner_id = fallback.pk
        if owner_id is None:
            address.delete()
        else:
            Address.objects.filter(pk=address.pk).update(user_id=owner_id)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shop_app', '0007_userprofile_apartment_userprofile_city_and_more'),
    ]

    operations = [
        migrations.RunPython(link_addresses_to_auth_users, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='address',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses',
                                    to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
    ]
