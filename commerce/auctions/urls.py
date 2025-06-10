from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_announce, name="create_announce"),
    path("/announce?a=<int:listing_id>", views.get_announce, name="get_announce"),
    path("bid/<int:listing_id>", views.insert_bid, name="add_bid"),
    path("comment/<int:listing_id>", views.insert_comment, name="add_comment"),
    path("watchlist/", views.get_watchlist, name="get_watchlist"),
    path("announce/w=<int:listing_id>", views.add_watchlist, name="add_watchlist"),
    path("announce/wr=<int:listing_id>", views.remove_watchlist, name="remove_watchlist"),
    path("announce/r=<int:listing_id>", views.remove_listing_active, name="remove_listing")
]
