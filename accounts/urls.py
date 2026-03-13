from django.urls import path
from .views import LoginView,RegisterView,UserDetailView,Logout,MeView,RefreshView

urlpatterns=[
    path('login/',LoginView.as_view()),
    path('register/',RegisterView.as_view()),
    path("refresh/", RefreshView.as_view()),
    path("users/<int:id>/", UserDetailView.as_view()),
    path("logout/", Logout.as_view()),
    path("me/", MeView.as_view()),

]