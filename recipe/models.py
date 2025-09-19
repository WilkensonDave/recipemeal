from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import MinLengthValidator
import uuid
from django.utils.text import slugify

# Create your models here.

class recipemeal(models.Model):
    title = models.CharField(max_length=150, unique=False)
    date = models.CharField(max_length=50)
    content = models.TextField(max_length=250, validators=[MinLengthValidator(20)], default="content")
    slug = models.SlugField(db_index=True, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    
    def __str__(self):
        return f"{self.title}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            count = 1
            while recipemeal.objects.filter(slug=slug).exists():
                slug = f"{base_slug} -{count}"
                count += 1
            
            self.slug = slug
        
        super().save(*args, **kwargs)
        
    def get_absolute_url(self):
        return reverse("recipe-details", kwargs={"slug": self.slug})

class resetpassword(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reset_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_when = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Password reset for {self.user.username} at {self.created_when}"

