from django.urls import path
from . import views

urlpatterns = [
    path('', views.homeView.as_view(), name="home"),
    path("recipe/", views.recipeView.as_view(), name="recipe"),
    path("register/", views.registerView.as_view(), name="register"),
    path("login/", views.loginView.as_view(), name="login"),
    path("logout/", views.loginView.as_view(), name="logout"),
    path("forgetpassword/", views.forgetPassword.as_view(), name="forgetpassword"),
    path("resetpassword-link/<str:reset_id>", views.linkToResetPassword.as_view(), name="resetpassword-link"),
    path("resetpassword/<str:reset_id>", views.resetPassword.as_view(), name="reset-password"),
    path("updatedata/<int:pk>", views.UpdateData.as_view(), name="update-data"),
    path("delete/<int:pk>", views.deletedata.as_view(), name="deletedata")
]
