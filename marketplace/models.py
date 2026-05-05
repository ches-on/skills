from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

CATEGORY_CHOICES = [
    ('housekeeping', 'Housekeeping'),
    ('salon', 'Salon & Beauty'),
    ('sales', 'Sales'),
    ('tutoring', 'Tutoring'),
    ('repair', 'Repair & Maintenance'),
    ('fitness', 'Fitness & Wellness'),
    ('pet_care', 'Pet Care'),
    ('events', 'Event Planning'),
    ('delivery', 'Delivery'),
    ('cooking', 'Cooking'),
    ('photography', 'Photography'),
    ('other', 'Other'),
]

ROLE_CHOICES = [
    ('customer', 'Customer'),
    ('provider', 'Provider'),
    ('merchant', 'Merchant'),
]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=200, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} - {self.get_role_display()}'

    @property
    def is_provider(self):
        return self.role == 'provider'

    @property
    def is_merchant(self):
        return self.role == 'merchant'

    @property
    def is_customer(self):
        return self.role == 'customer'


class Listing(models.Model):
    title = models.CharField(max_length=200)
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='other'
    )
    skill_name = models.CharField(max_length=200, default='General Service', help_text="Specific skill or service offered")
    description = models.TextField()
    image = models.ImageField(upload_to='listings/', blank=True, null=True)
    contact = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='listings'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class ServicePortfolioImage(models.Model):
    service = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='portfolio_images'
    )
    image = models.ImageField(upload_to='services/portfolio/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Portfolio image for {self.service.title}'

    class Meta:
        ordering = ['uploaded_at']


# ========== PRODUCTS MARKETPLACE ==========

class ProductCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Product Categories'


class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name='products'
    )
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='products'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def in_stock(self):
        return self.stock > 0

    @property
    def primary_image(self):
        """Return the primary image, or the first available image"""
        primary = self.images.filter(is_primary=True).first()
        if not primary:
            primary = self.images.first()
        return primary

    @property
    def primary_image_url(self):
        """Return the URL of the primary image, or None"""
        primary = self.primary_image
        if primary:
            return primary.image.url
        return None

    class Meta:
        ordering = ['-created_at']


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='products/')
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Image for {self.product.name}'

    class Meta:
        ordering = ['-is_primary', 'uploaded_at']


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Cart"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'

    @property
    def total_price(self):
        return self.quantity * self.product.price

    class Meta:
        unique_together = ('cart', 'product')


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order #{self.id} - {self.user.username}'

    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'

    @property
    def total_price(self):
        return self.quantity * self.price


# ========== SIGNALS ==========

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


@receiver(post_save, sender=User)
def create_user_cart(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)
