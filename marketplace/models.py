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


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
