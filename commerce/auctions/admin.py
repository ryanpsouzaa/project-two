from django.contrib import admin
from django.core.management import CommandError

from .models import Listing, Comment, Bid, User
# Register your models here.

class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "description", "initial_bid", "image_url",
                    "category", "owner_user", "active")

class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "value", "user", "listing")

class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "message", "user", "listing")

admin.site.register(Listing, ListingAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(User)
