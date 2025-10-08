from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Address) 
admin.site.register(PaymentMethod) 
admin.site.register(Delivery) 
admin.site.register(Order) 
admin.site.register(OrderItem) 
admin.site.register(Cart)  