from django.urls import path
from . views import WishlistView,WishlistitemDelete





urlpatterns=[
    path("wishlist/",WishlistView.as_view()),
    path("wishlist/<int:id>/", WishlistitemDelete.as_view()),
]