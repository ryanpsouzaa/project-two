from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_announce, name="create_announce"),
    path("listing/active/<int:listing_id>", views.get_listing_active, name="get_listing_active"),
    path("bid/<int:listing_id>", views.insert_bid, name="add_bid"),
    path("comment/<int:listing_id>", views.insert_comment, name="add_comment"),
    path("watchlist/", views.get_watchlist, name="get_watchlist"),
    path("watchlist/add/<int:listing_id>", views.add_watchlist, name="add_watchlist"),
    path("watchlist/remove/<int:listing_id>", views.remove_watchlist, name="remove_watchlist"),
    path("listing/remove/<int:listing_id>", views.remove_listing_active, name="remove_listing"),
    path("listing/inactive/<int:listing_id>", views.get_listing_inactive, name="get_listing_inactive"),
    path("user/<int:user_id>", views.get_user, name="get_user"),
    path("listing/<int:listing_id>", views.view_get_listing, name="get_listing")
]
