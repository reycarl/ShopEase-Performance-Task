import re
from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError

from .models import Order, Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "category", "description", "price", "stock", "image", "is_active"]
        labels = {
            "name": "Product name",
            "category": "Category",
            "description": "Description",
            "price": "Price (₱)",
            "stock": "Stock quantity",
            "image": "Product image",
            "is_active": "Active product",
        }
        help_texts = {
            "name": "Use a clear customer-facing product name.",
            "price": "Must be greater than ₱0.00.",
            "stock": "Use 0 when the product is out of stock.",
            "image": "Optional JPG/PNG/WebP image.",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "input", "placeholder": "e.g. Wireless Mouse"}),
            "category": forms.Select(attrs={"class": "input"}),
            "description": forms.Textarea(attrs={"class": "input", "rows": 5}),
            "price": forms.NumberInput(attrs={"class": "input", "step": "0.01", "min": "0.01"}),
            "stock": forms.NumberInput(attrs={"class": "input", "min": "0"}),
            "image": forms.ClearableFileInput(attrs={"class": "input", "accept": "image/*"}),
            "is_active": forms.CheckboxInput(attrs={"class": "checkbox"}),
        }

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price is None or price <= Decimal("0"):
            raise ValidationError("Price must be greater than 0.")
        return price

    def clean_stock(self):
        stock = self.cleaned_data.get("stock")
        if stock is None or stock < 0:
            raise ValidationError("Stock cannot be negative.")
        return stock


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "customer_name", "email", "phone", "address", "city",
            "shipping_method", "payment_method",
        ]
        labels = {
            "customer_name": "Full name",
            "email": "Email address",
            "phone": "Philippine mobile number",
            "address": "Complete address",
            "city": "City / Municipality",
            "shipping_method": "Shipping method",
            "payment_method": "Payment method",
        }
        help_texts = {
            "phone": "Format: 09XXXXXXXXX or +639XXXXXXXXX",
            "address": "Include house/building number and street.",
        }
        widgets = {
            "customer_name": forms.TextInput(attrs={"class": "input", "autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"class": "input", "autocomplete": "email"}),
            "phone": forms.TextInput(attrs={"class": "input", "placeholder": "09171234567"}),
            "address": forms.TextInput(attrs={"class": "input", "placeholder": "House/Building No., Street"}),
            "city": forms.TextInput(attrs={"class": "input", "placeholder": "City / Municipality"}),
            "shipping_method": forms.Select(attrs={"class": "input", "id": "id_shipping_method"}),
            "payment_method": forms.Select(attrs={"class": "input"}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if not re.fullmatch(r"(09\d{9}|\+639\d{9})", phone):
            raise ValidationError("Enter a valid Philippine mobile number: 09XXXXXXXXX or +639XXXXXXXXX.")
        return phone

    def clean(self):
        cleaned = super().clean()
        shipping = cleaned.get("shipping_method")
        address = (cleaned.get("address") or "").strip()
        city = (cleaned.get("city") or "").strip()

        if shipping == "express" and (len(address) < 8 or not city):
            raise ValidationError(
                "Express shipping requires a complete address and city/municipality."
            )
        return cleaned
