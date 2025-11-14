from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Size)
admin.site.register(Address)
admin.site.register(PaymentMethod)
admin.site.register(Order)
admin.site.register(Product)
admin.site.register(SizeProduct)
admin.site.register(Cart)
admin.site.register(CartItem)

def save_model(self, request, obj, form, change):
    ###Пересчитываем сумму при сохранении в админке
    obj.total_price = obj.calculate_total()
    super().save_model(request, obj, form, change)