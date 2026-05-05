from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from marketplace.models import Product, ProductCategory


class Command(BaseCommand):
    help = 'Populates the database with sample products for SkillMarket'

    def handle(self, *args, **options):
        # Create a sample seller if not exists
        if not User.objects.filter(username='seller').exists():
            seller = User.objects.create_user(
                username='seller',
                password='seller123',
                email='seller@example.com'
            )
            self.stdout.write('Created seller user: seller / seller123')
        else:
            seller = User.objects.get(username='seller')

        # Ensure seller has provider role
        seller.profile.role = 'provider'
        seller.profile.save()
        self.stdout.write(f'Set seller role to: Provider')

        # Create categories
        categories_data = [
            'Electronics',
            'Clothing & Fashion',
            'Home & Garden',
            'Sports & Outdoors',
            'Books & Media',
        ]

        categories = {}
        for cat_name in categories_data:
            category, created = ProductCategory.objects.get_or_create(name=cat_name)
            categories[cat_name] = category
            if created:
                self.stdout.write(f'Created category: {cat_name}')

        # Sample products
        products_data = [
            {
                'name': 'Wireless Bluetooth Headphones',
                'category': 'Electronics',
                'description': 'Premium wireless headphones with noise cancellation, 30-hour battery life, and comfortable over-ear design.',
                'price': '89.99',
                'stock': 50,
            },
            {
                'name': 'Smart Fitness Watch',
                'category': 'Electronics',
                'description': 'Track your workouts, heart rate, and sleep patterns with this advanced smartwatch.',
                'price': '199.99',
                'stock': 30,
            },
            {
                'name': 'Men\'s Casual T-Shirt',
                'category': 'Clothing & Fashion',
                'description': 'Comfortable cotton t-shirt available in multiple colors and sizes.',
                'price': '24.99',
                'stock': 100,
            },
            {
                'name': 'Women\'s Running Shoes',
                'category': 'Sports & Outdoors',
                'description': 'Lightweight running shoes with cushioned soles for maximum comfort.',
                'price': '79.99',
                'stock': 45,
            },
            {
                'name': 'Gardening Tool Set',
                'category': 'Home & Garden',
                'description': 'Complete set of essential gardening tools including spade, trowel, pruners, and gloves.',
                'price': '49.99',
                'stock': 25,
            },
            {
                'name': 'Bestselling Novel Collection',
                'category': 'Books & Media',
                'description': 'Set of 5 bestselling novels from renowned authors. Perfect for book lovers.',
                'price': '34.99',
                'stock': 60,
            },
            {
                'name': 'Portable Bluetooth Speaker',
                'category': 'Electronics',
                'description': 'Compact and waterproof Bluetooth speaker with 12 hours of playtime.',
                'price': '59.99',
                'stock': 40,
            },
            {
                'name': 'Yoga Mat Premium',
                'category': 'Sports & Outdoors',
                'description': 'Eco-friendly TPE yoga mat with non-slip surface, includes carrying strap.',
                'price': '39.99',
                'stock': 35,
            },
        ]

        created_count = 0
        for data in products_data:
            product, created = Product.objects.get_or_create(
                name=data['name'],
                defaults={
                    'category': categories[data['category']],
                    'description': data['description'],
                    'price': data['price'],
                    'stock': data['stock'],
                    'seller': seller,
                }
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} sample products')
        )
