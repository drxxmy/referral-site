from django.urls import path

from . import views

urlpatterns = [
    path("auth/request-code/", views.RequestCodeView.as_view(), name="request-code"),
    path("auth/verify-code/", views.VerifyCodeView.as_view(), name="verify-code"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path(
        "profile/activate-invite/",
        views.ActivateInviteView.as_view(),
        name="activate-invite",
    ),
]
