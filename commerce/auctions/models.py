from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watch_list = models.ManyToManyField('Listing', blank=True, related_name="watchlisted_by")


class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    initial_bid = models.FloatField()
    image_url = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=64, null=True, blank=True)
    owner_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} - initial_bid: {self.initial_bid}, active: {self.active}"

class Bid(models.Model):
    value = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")

class Comment(models.Model):
    message = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
