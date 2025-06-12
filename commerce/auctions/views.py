from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
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
    title = forms.CharField(label="Title", max_length=64, error_messages={"required":"Enter the title"})
    description = forms.CharField(widget=forms.Textarea)
    initial_bid = forms.DecimalField(label="Initial Bid", min_value=0.00, decimal_places=2)
    image_url = forms.URLField(label="image URL", required=False)
    category = forms.ChoiceField(choices=[
        ("eletronics", "Eletronics"),
        ("home_appliances", "Home Appliances"),
        ("furniture", "Furniture"),
        ("vehicles", "Vehicles"),
        ("fashion_and_acessories", "Fashion & Acessories"),
        ("books_and_education", "Books & Education"),
        ("musical_instruments", "Musical Instruments"),
        ("toys", "Toys"),
        ("games", "Games"),
        ("tools_and_construction", "Tools & Construction"),
        ("pets", "Pets & Pets Supplies")
    ])

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

@login_required()
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


@login_required()
def create_announce(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():

            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            initial_bid = form.cleaned_data["initial_bid"]
            category = form.cleaned_data["category"]
            image_url = form.cleaned_data["image_url"]

            user = request.user

            if not category.strip() and not image_url.strip():
                listing = Listing(title=title, description=description, initial_bid=initial_bid,
                owner_user=user)

            else:
                listing = Listing(title=title, description=description, initial_bid=initial_bid,
                image_url=image_url, category=category, owner_user=user)

            if Listing.objects.filter(title=title, owner_user=user).exists():
                return render(request, "auctions/create-announce.html", {
                    "form" : form,
                    "error" : "You already have this title created"
                })
            else:
                listing.save()
                return render(request, "auctions/announce-details.html", get_context_listing(listing, {
                    "notification" : f"Announce: {listing.title} created"
                }))
        else:
            return render(request, "auctions/create-announce.html", {
                "form" : form,
                "error" : "Form invalid"
            })

    else:
        form = ListingForm()
        return render(request, "auctions/create-announce.html", {
            "form" : form
        })

@login_required()
def get_listing_active(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    return render(request, "auctions/announce-details.html", get_context_listing(listing))

@login_required()
def insert_bid(request, listing_id):
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
        return redirect("get_listing_active", listing_id=listing_id)

@login_required()
def insert_comment(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
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

@login_required()
def get_watchlist(request):
    if request.user.watch_list.filter(active=True).exists():
        return render(request, "auctions/watchlist-details.html", {
            "watchlist" : request.user.watch_list.all()
        })
    else:
        return render(request, "auctions/watchlist-details.html", {
            "message" : "There is no listing in your Watch List"
        })

@login_required()
def add_watchlist(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    user = request.user
    user.watch_list.add(listing)
    return render(request, "auctions/announce-details.html", get_context_listing(listing,{
        "notification" : "Listing added to your Watch List"
    }))

@login_required()
def remove_watchlist(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    user = request.user
    user.watch_list.remove(listing)
    return render(request, "auctions/announce-details.html", get_context_listing(listing, {
        "notification" : "Listing removed to Watch List"
    }))

@login_required()
def remove_listing_active(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    if not listing.active:
        return render(request, "auctions/user-page.html", {
            "error" : f"Listing {listing.title} is already inactive"
        })
    if listing.bids.exists() > 0:
        bid_winner = listing.bids.order_by("-value").first()

        user_won = bid_winner.user
        user_won.listings_won.add(listing)
        listing.winner_bid = bid_winner.value

        notification = f"{listing.title} Removed from advertisement, buyed for {bid_winner.user.username}"
    else:
        notification = f"{listing.title} Removed from advertisement"

    listing.active = False
    listing.save()
    return render(request, "auctions/listing-inactive-details.html", {
        "notification" : notification,
        "listing" : listing,
        "comments" : listing.comments.all()
    })

@login_required()
def get_user(request, user_id):
    user = User.objects.get(pk=user_id)
    listings_created = user.listings.all()
    listings_won = user.listings_won.all()

    return render(request, "auctions/user-page.html", {
        "user" : user,
        "listings_created" : listings_created,
        "listings_won" : listings_won
    })

@login_required()
def view_get_listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    if not listing.active:
        return redirect("get_listing_inactive", listing_id=listing_id)
    else:
        return redirect("get_listing_active", listing_id=listing_id)

#todo: fazer a pagina de error
@login_required()
def get_listing_inactive(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    verification_user = verify_owner_buyer(request, listing)
    if not verification_user:
        return render(request, "auctions/error.html", {
            "error" : "You dont have permission to do this"
        })

    return render(request, "auctions/listing-inactive-details.html", {
        "listing" : listing,
        "listing_winner" : listing.winner_user,
        "comments" : listing.comments.all()
    })


def verify_owner_buyer(request, listing):
    user = request.user
    if user == listing.owner_user or user == listing.winner_user:
        return True

    return False



