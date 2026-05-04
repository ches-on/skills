from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from marketplace.models import Listing, Profile


class Command(BaseCommand):
    help = 'Populates the database with sample listings for SkillMarket'

    def handle(self, *args, **options):
        # Create a sample provider user if not exists
        if not User.objects.filter(username='provider').exists():
            provider = User.objects.create_user(
                username='provider',
                password='provider123',
                email='provider@example.com'
            )
            self.stdout.write('Created provider user: provider / provider123')
        else:
            provider = User.objects.get(username='provider')

        # Ensure provider has a profile with provider role
        profile, created = Profile.objects.get_or_create(
            user=provider,
            defaults={'role': 'provider'}
        )
        if not created and profile.role != 'provider':
            profile.role = 'provider'
            profile.save()
        self.stdout.write(f'Set provider role to: Provider (profile {"created" if created else "updated"})')

        # Sample listings data
        sample_listings = [
            {
                'title': 'House Deep Cleaning Service',
                'category': 'housekeeping',
                'skill_name': 'Deep Cleaning',
                'description': 'Professional deep cleaning for your home. We cover all rooms, bathrooms, kitchen, and windows. Eco-friendly products used.',
                'contact': '555-0101',
                'location': 'New York, NY',
            },
            {
                'title': 'Hair Styling & Coloring',
                'category': 'salon',
                'skill_name': 'Hair Styling',
                'description': 'Full hair services including cut, style, coloring, and treatments. Certified stylists with 10+ years experience.',
                'contact': '555-0102',
                'location': 'Los Angeles, CA',
            },
            {
                'title': 'Fresh Organic Vegetables',
                'category': 'sales',
                'skill_name': 'Organic Produce Sales',
                'description': 'Farm-fresh organic vegetables delivered to your door. Seasonal produce from local farms. Minimum order $20.',
                'contact': '555-0103',
                'location': 'Austin, TX',
            },
            {
                'title': 'Lawn Mowing & Landscaping',
                'category': 'housekeeping',
                'skill_name': 'Lawn Care',
                'description': 'Complete lawn care service including mowing, edging, trimming, and debris cleanup. Weekly and bi-weekly plans available.',
                'contact': '555-0104',
                'location': 'Chicago, IL',
            },
            {
                'title': 'Manicure & Pedicure at Home',
                'category': 'salon',
                'skill_name': 'Nail Care',
                'description': 'Professional nail care in the comfort of your home. Gel, acrylic, and regular polish options available.',
                'contact': '555-0105',
                'location': 'Miami, FL',
            },
            {
                'title': 'Handmade Jewelry Collection',
                'category': 'sales',
                'skill_name': 'Jewelry Making',
                'description': 'Unique handcrafted jewelry pieces including necklaces, bracelets, and earrings. Perfect for gifts or personal use.',
                'contact': '555-0106',
                'location': 'Seattle, WA',
            },
            {
                'title': 'Apartment Move-In Cleaning',
                'category': 'housekeeping',
                'skill_name': 'Move-In Cleaning',
                'description': 'Thorough cleaning service for apartments before move-in. Includes sanitizing all surfaces, floors, and appliances.',
                'contact': '555-0107',
                'location': 'Boston, MA',
            },
            {
                'title': 'Bridal Makeup & Hair',
                'category': 'salon',
                'skill_name': 'Bridal Makeup',
                'description': 'Complete bridal beauty package including makeup, hair styling, and touch-ups. Trial session included.',
                'contact': '555-0108',
                'location': 'Houston, TX',
            },
            {
                'title': 'Vintage Electronics & Gadgets',
                'category': 'sales',
                'skill_name': 'Electronics Repair',
                'description': 'Carefully restored vintage electronics including radios, cameras, and gaming consoles. Fully tested and working.',
                'contact': '555-0109',
                'location': 'Portland, OR',
            },
            {
                'title': 'Personal Chef Service',
                'category': 'cooking',
                'skill_name': 'Personal Chef',
                'description': 'In-home personal chef for meal prep, dinner parties, or special occasions. Custom menus to fit dietary needs.',
                'contact': '555-0110',
                'location': 'San Francisco, CA',
            },
            {
                'title': 'Pool Cleaning & Maintenance',
                'category': 'housekeeping',
                'skill_name': 'Pool Maintenance',
                'description': 'Regular pool cleaning, chemical balancing, and equipment inspection. Keep your pool sparkling clean all year round.',
                'contact': '555-0111',
                'location': 'Phoenix, AZ',
            },
            {
                'title': 'Mobile Massage Therapy',
                'category': 'fitness',
                'skill_name': 'Massage Therapy',
                'description': 'Relaxing massage therapy in your home or office. Swedish, deep tissue, and sports massage available.',
                'contact': '555-0112',
                'location': 'Denver, CO',
            },
        ]

        # Create listings
        created_count = 0
        for data in sample_listings:
            listing, created = Listing.objects.get_or_create(
                title=data['title'],
                defaults={
                    'category': data['category'],
                    'skill_name': data['skill_name'],
                    'description': data['description'],
                    'contact': data['contact'],
                    'location': data['location'],
                    'created_by': provider,
                }
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} sample listings')
        )
