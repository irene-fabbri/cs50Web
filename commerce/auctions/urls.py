from django.urls import path

from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new", views.new_listing, name="newlisting"),
    path("listing/<int:listing_id>/", views.listing, name='listing'),
    path("close_auction/<int:listing_id>/", views.close_auction, name='close_auction'),
    path("watchlist/<int:user_id>/<int:listing_id>/", views.watchlist_add, name='watchlist_add'),
    path("watchlist/<int:user_id>/<int:listing_id>/rm", views.watchlist_remove, name='watchlist_remove'),
    path("watchlist/<int:user_id>/", views.watchlist, name='watchlist'),
    path("my_bids/<int:user_id>/", views.my_bids, name='my_bids'),
    path("<str:category>/", views.category, name='category')
]
