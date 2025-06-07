from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db.models import Max
from django import forms

from .models import User, Listing, Bid, Comment

#@login_required(login_url="login") -> decorator para verificar a autenticacao dos users

#todo: construir Django forms e colocar decorator
class ListingForm(forms.Form):
    title = forms.CharField(label="Title", max_length=64)
    description = forms.Textarea()
    initial_bid = forms.DecimalField()
    image_url = forms.Textarea()
    category = forms.CharField()

def index(request):
    listings_active = Listing.objects.filter(active=True).all()
    return render(request, "auctions/index.html", {
        "listings_active" : listings_active
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def create_announce(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            title = request.POST["title"]
            description = request.POST["description"]
            initial_bid = request.POST["bid"]

            category = request.POST["category"]
            image_url = request.POST["image"]

            user = request.user
            if not category.strip() and not image_url.strip():
                listing = Listing(title=title, description=description, initial_bid=initial_bid,
                owner_user=user)

            else:
                listing = Listing(title=title, description=description, initial_bid=initial_bid,
                image_url=image_url, category=category, owner_user=user)

            if Listing.objects.filter(title=title, owner_user=user).exists():
                return render(request, "auctions/create-announce.html", {
                    "error" : "You already have this title created"
                })
            else:    
                listing.save()
                return render(request, "auctions/announce-details.html", get_context_listing(listing, {
                    "notification" : f"Announce: {listing.title} created"
                }))
                
        else:
            return render(request, "auctions/create-announce.html")
    else:
        return redirect("login")

def get_announce(request, listing_id):
    if request.user.is_authenticated:
        listing = Listing.objects.get(pk=listing_id)
        current_bid = None
        if len(listing.bids.all()) >= 1:
            current_bid = listing.bids.aggregate(Max("value"))["value__max"]
        if len(listing.comments.all()) > 0:
            all_comments = listing.comments.all()
        return render(request, "auctions/announce-details.html", get_context_listing(listing))
    else:
        return redirect("login")

def insert_bid(request, listing_id):
    if not request.user.is_authenticated:
        return redirect("login")
    else:
        if request.method == "POST":
            listing = Listing.objects.get(pk=listing_id)
            user = request.user
            value_bid = float(request.POST["value"])
            if len(listing.bids.all()) > 0:
                highest_bid = listing.bids.aggregate(Max("value"))["value__max"]
                if value_bid <= highest_bid:
                    return render(request, "auctions/announce-details.html", get_context_listing(listing, {
                        "error" : "Bid must be higher than current bid"
                    }))
            else:
                if value_bid < listing.initial_bid:
                    return render(request, "auctions/announce-details.html", get_context_listing(listing, {
                        "error" : "Bid must be higher or equal than the initial bid"
                    }))
            bid = Bid(value=value_bid, user=user, listing=listing)
            bid.save()
            return render(request, "auctions/announce-details.html", get_context_listing(listing, {
                "notification" : f"Bid: {bid.value} added"
            }))

        else:
            return redirect("get_announce", listing_id=listing_id)


def insert_comment(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    if not request.user.is_authenticated:
        return redirect("login")

    message = request.POST["message"]
    if not message.strip():
        return render(request, "auctions/announce-details.html", get_context_listing(listing, {
            "error" : "Message is blank"
        }))
    comment = Comment(message=message, user=request.user, listing=listing)
    comment.save()
    return render(request, "auctions/announce-details.html", get_context_listing(listing, {
        "notification" : "Comment added"
    }))

def get_context_listing(listing, extra_content=None):
    context = {
        "listing" : listing,
        "current_bid": listing.bids.aggregate(Max("value"))["value__max"],
        "comments" : listing.comments.all(),
    }
    if extra_content:
        context.update(extra_content)
    return context
