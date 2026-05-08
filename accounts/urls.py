from django.urls import path
from .views import GoogleLoginView, LoginView,RegisterView,UserDetailView,Logout,MeView,RefreshView,ProfileUpdateView

urlpatterns=[
    path("google/", GoogleLoginView.as_view()),
    path('login/',LoginView.as_view()),
    path('register/',RegisterView.as_view()),
    path("refresh/", RefreshView.as_view()),
    path("users/",UserDetailView .as_view()),
    path("users/<int:id>/", UserDetailView.as_view()),
    path("logout/", Logout.as_view()),
    path("me/", MeView.as_view()),
    path("profileupdate/", ProfileUpdateView.as_view()),
    

]