from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.views.generic.base import TemplateView
from django.views import View
from django.http import HttpResponse, HttpResponseRedirect
from .forms import RecipeForm
from .models import recipemeal, resetpassword
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils import timezone
from .models import *
from django.views.generic.edit import DeleteView, UpdateView
from django.urls import reverse_lazy
# Create your views here.

class registerView(View):
    def get(self, request):
        return render(request, "register.html")

    def post(self, request):
        firstname = request.POST.get("firstname")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm-password")

        if User.objects.filter(email=email).exists():
            messages.error(request, "This email already exists. Try another one.")
            return render(request, "register.html")
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "This username already exists. Try another one.")
            return render(request, "register.html")
        
        
        if len(password) < 8:
            messages.error(request, "Password can not be less than 8 characters")
            
        
        if password != confirm_password:
            messages.error(request, "Password does not match.")
            return render(request, "register.html")
        
        user = User.objects.create(
            username=username,
            first_name=firstname,
            email=email,
            password=make_password(password)
            )
        
        if user is not None:
            messages.success(request, "You have been successfully register.")
            return redirect("login")
        
        else:
            messages.error(request, "sorry check if the data entered are correct.")
            return redirect("register")
    

class loginView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "login.html")
    
    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            next_url = request.GET.get("next")
            
            if next_url:
                return redirect(next_url)
            
            else:
                return redirect("home")

        else:
            messages.error(request, "Invalid credentials")
            return render(request, "login.html")

class logoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "You have been successfully logged out.......")
        return render(request, "login.html")


class homeView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            data = recipemeal.objects.filter(user=request.user).order_by("-id")[:10]
            context ={
                "form":RecipeForm(),
                "recipes":data
            }
            return render(request, "index.html", context)
        
        else:
            context ={
                "form":RecipeForm(),
            }
            return render(request, "index.html", context)
    
    @method_decorator(login_required, name='dispatch')
    def post(self, request):
        form = RecipeForm(request.POST)
        
        if request.user.is_authenticated:
            if form.is_valid():
                recipe_meal = form.save(commit=False)
                recipe_meal.user = request.user
                recipe_meal.save()   
                return redirect("home")
            
            data = recipemeal.objects.filter(user=request.user).order_by("-id")[:10]
            user = request.user
            context = {
                    "recipes": data,
                    "form": form,
                    "user":user
                }
            
            return render(request, "index.html", context)
        
        else:
            messages.error(request, "You need to login to access this page")
            return redirect("login")
        
        
class recipeView(LoginRequiredMixin, ListView):
    template_name = "recipe.html"
    model = recipemeal
    
    ordering = ["-id"]    
    context_object_name = "recipes"
    
    def get_queryset(self):
        return recipemeal.objects.filter(user=self.request.user).order_by("-id")[:10]


class forgetPassword(View):
    
    def get(self, request, *args, **kwargs):
        return render(request, "forgetpassword.html")

    def post(self, request, *args, **kwargs):
        email = request.POST.get("email")
        if not User.objects.filter(email=email).exists():
            return HttpResponse("This email does not exist in our database.")
        
        try:
            user = User.objects.get(email=email)
            new_reset_link = resetpassword(user=user)
            new_reset_link.save()
            password_reset_link = reverse('reset-password', kwargs={"reset_id": new_reset_link.reset_id})
            
            full_password_reset_url = f"{request.scheme}://{request.get_host()}{password_reset_link}"
            emal_body = f"Reset your password using the link below:\n\n\n{full_password_reset_url}"
            
            email_message = EmailMessage(
                "reset your password",
                emal_body, 
                settings.EMAIL_HOST_USER,
                [email]
            )
            
            email_message.fail_silently = True
            email_message.send()
            return redirect("resetpassword-link", reset_id=new_reset_link.reset_id)
        
        
        except User.DoesNotExist:
            messages.error(request, f"No user found with this email: '{email}'")
            return redirect("forgetpassword")
    
    
class linkToResetPassword(View):
    def get(self, request, reset_id, *args, **kwargs):
        if resetpassword.objects.filter(reset_id=reset_id).exists():
            return render(request, "resetpassword-link.html")
        
        else:
            messages.error(request, "Invalid reset id")
            return redirect("forgetpassword")


class resetPassword(View):
    def get(self, request, *args, **kwargs):
        return render(request, "password-reset-send.html")
    
    
    def post(self, request, reset_id, *args, **kwargs):
        
        try:
            password_reset_id = resetpassword.objects.get(reset_id=reset_id)
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")
            
            not_correct_password =False
            
            if password != confirm_password:
                not_correct_password = True
                messages.error(request, "The password you have entered are not match.")
            
            if len(password) < 8:
                not_correct_password = True
                messages.error(request, "password mut be at least 8 characters long.")
            
            expiration_time = password_reset_id.created_when +  timezone.timedelta(minutes=10)
            
            if timezone.now() > expiration_time:
                not_correct_password = True
                messages.error(request, "Sorry the reset link has been expired.")
                password_reset_id.delete()
            
            if not not_correct_password:
                user = password_reset_id.user
                user.set_password(password)
                user.save()
                password_reset_id.delete()
                messages.error(request, "Your password has been successfully reset. Try to login now.")
                return redirect("login")
            else:
                return redirect("reset-password", reset_id=reset_id)
        
        except resetpassword.DoesNotExist:
            messages.error(request, "Invalid reset id")
            return redirect("forgetpassword")


class UpdateData(LoginRequiredMixin, View):
    
    def get(self, request, pk, *args, **kwargs):
        current_recipe = get_object_or_404(recipemeal, id=pk)
        
        if request.user != current_recipe.user and not request.user.is_superuser:
            return redirect("unauthorize")
        
        form = RecipeForm(instance=current_recipe)
        return render(request, "updatedata.html", {"forms": form})
    
    def post(self, request, pk, *args, **kwargs):
        current_recipe = get_object_or_404(recipemeal, id=pk)
        form = RecipeForm(request.POST or None, instance=current_recipe)
        
        if form.is_valid():
            form.save()
            return redirect("home")


# class deletedata(LoginRequiredMixin, DeleteView):
#     model = recipemeal
#     success_url = "/"
#     template_name = "confirm-delete.html"

class deletedata(LoginRequiredMixin, View):
    
    def get(self, request, pk, *args, **kwargs):
        item_to_delete = get_object_or_404(recipemeal, id=pk)
        
        if request.user.is_authenticated:
            item_to_delete.delete()
            messages.success(request, "recipe has been successfully deleted.")
            return redirect("/")
        else:
            return redirect("Unauthorized")
    
         

