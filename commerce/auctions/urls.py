from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_announce, name="create_announce"),
    path("/announce?a=<int:listing_id>", views.get_announce, name="get_announce"),
    path("bid/<int:listing_id>", views.insert_bid, name="bid")
]
