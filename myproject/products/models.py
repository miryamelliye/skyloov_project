from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

User = get_user_model()

class Product(models.Model):
    category = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.FloatField()
    image = models.ImageField(upload_to='product_images/', default='',blank=True,null=True)  # Add the image field

    # Add any other fields relevant to your product model

    def __str__(self):
        return self.category + ' - ' + self.brand

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    # Add any additional fields you need
