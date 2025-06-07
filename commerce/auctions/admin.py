from django.contrib import admin
from .models import Listing, Comment, Bid, User
# Register your models here.

class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "description", "initial_bid", "image_url",
                    "category", "owner_user", "active")

admin.site.register(Listing, ListingAdmin)
admin.site.register(Comment)
admin.site.register(Bid)
admin.site.register(User)
