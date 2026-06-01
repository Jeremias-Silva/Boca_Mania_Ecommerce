from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


# 👤 CUSTOMER PROFILE (NO CHANGE)
class CustomerProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} Profile"


# 🛒 PRODUCT (PROFESSIONAL CORRECTED VERSION)
class Product(models.Model):

    # BASIC
    name = models.CharField(max_length=255)

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=300, blank=True)

    # PRICING
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # INVENTORY
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=100, blank=True)

    # MEDIA
    image = models.ImageField(upload_to='products/', null=True, blank=True)

    # SYSTEM (ADMIN CONTROL)
    is_published = models.BooleanField(default=False)  # LIVE / DRAFT
    is_featured = models.BooleanField(default=False)
    is_new = models.BooleanField(default=True)

    # SEO
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)

    # TIMESTAMPS
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # AUTO SLUG SAFE (NO CONFLICT)
    def save(self, *args, **kwargs):

        if not self.slug:

            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            # avoids UNIQUE error (YOUR ORIGINAL PROBLEM)
            while Product.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# 📦 ORDER (VERSION SUITABLE FOR ANONYMOUS CHECKOUT)
class Order(models.Model):

    # Modified to allow null in the database for guest purchases
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # FIELDS INJECTED TO MATCH THE VIEW AND AVOID TYPEERROR:
    status = models.CharField(max_length=50, default='Awaiting Payment')
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username if self.user else 'Guest'}"


# 🧾 ORDER ITEMS (NO CHANGE)
class OrderItem(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"