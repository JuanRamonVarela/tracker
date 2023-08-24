from django.contrib import admin
from .models import Categories, Books, Delivery, DeliveryProspect

# Register your models here.
admin.site.register(Categories)
admin.site.register(Books)
admin.site.register(Delivery)
admin.site.register(DeliveryProspect)