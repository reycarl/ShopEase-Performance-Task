from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from shop.models import Category, Product


class Command(BaseCommand):
    help = "Create demo categories, products, and a staff user."

    def handle(self, *args, **options):
        categories = {
            "Electronics": "electronics",
            "Accessories": "accessories",
            "Home Office": "home-office",
        }
        category_objects = {}
        for name, slug in categories.items():
            category_objects[name], _ = Category.objects.get_or_create(
                slug=slug, defaults={"name": name}
            )

        products = [
            ("Wireless Mouse", "Electronics", "Comfortable wireless mouse for everyday work.", "650.00", 10),
            ("Mechanical Keyboard", "Electronics", "Tactile mechanical keyboard with RGB backlight.", "2500.00", 5),
            ("USB-C Hub", "Accessories", "Multi-port USB-C hub for laptops and tablets.", "1200.00", 8),
            ("Laptop Stand", "Home Office", "Adjustable aluminum laptop stand.", "900.00", 0),
            ("Webcam", "Electronics", "1080p webcam for online meetings and classes.", "1800.00", 6),
            ("Desk Mat", "Home Office", "Large anti-slip desk mat.", "550.00", 14),
        ]

        for name, category, description, price, stock in products:
            Product.objects.update_or_create(
                name=name,
                defaults={
                    "category": category_objects[category],
                    "description": description,
                    "price": price,
                    "stock": stock,
                    "is_active": True,
                },
            )

        User = get_user_model()
        user, created = User.objects.get_or_create(username="admin", defaults={"email": "admin@example.com"})
        user.is_staff = True
        user.is_superuser = True
        user.set_password("Admin12345!")
        user.save()

        self.stdout.write(self.style.SUCCESS("Demo data ready."))
        self.stdout.write("Staff login: admin / Admin12345!")
