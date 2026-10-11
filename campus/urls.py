from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("portal/<slug:slug>/", views.module, name="module"),
    path("portal/<slug:slug>/new/", views.module, {"action":"create"}, name="module_create"),
    path("portal/<slug:slug>/<int:pk>/edit/", views.module, {"action":"edit"}, name="module_edit"),
    path("portal/<slug:slug>/<int:pk>/delete/", views.module, {"action":"delete"}, name="module_delete"),
    path("notices/publish/", views.quick_notice, name="quick_notice"),
    path("materials/<int:pk>/download/", views.download_material, name="download_material"),
    path("password-reset/", auth_views.PasswordResetView.as_view(template_name="registration/password_reset.html",success_url="/password-reset/done/"),name="password_reset"),
    path("password-reset/done/",auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"),name="password_reset_done"),
]
