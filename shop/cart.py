from decimal import Decimal
from .models import Product

CART_SESSION_KEY = "shopease_cart"


def get_cart(request):
    return request.session.setdefault(CART_SESSION_KEY, {})


def save_cart(request, cart):
    request.session[CART_SESSION_KEY] = cart
    request.session.modified = True


def add(request, product, quantity):
    cart = get_cart(request)
    key = str(product.pk)
    cart[key] = int(cart.get(key, 0)) + int(quantity)
    save_cart(request, cart)


def set_quantity(request, product, quantity):
    cart = get_cart(request)
    key = str(product.pk)
    if quantity <= 0:
        cart.pop(key, None)
    else:
        cart[key] = int(quantity)
    save_cart(request, cart)


def remove(request, product_id):
    cart = get_cart(request)
    cart.pop(str(product_id), None)
    save_cart(request, cart)


def clear(request):
    request.session[CART_SESSION_KEY] = {}
    request.session.modified = True


def get_items(request):
    raw = get_cart(request)
    items = []
    stale = []
    for product_id, quantity in raw.items():
        try:
            product = Product.objects.get(pk=product_id, is_active=True)
        except Product.DoesNotExist:
            stale.append(product_id)
            continue
        items.append({
            "product": product,
            "quantity": int(quantity),
            "subtotal": product.price * int(quantity),
        })
    if stale:
        for key in stale:
            raw.pop(key, None)
        save_cart(request, raw)
    return items


def subtotal(request):
    return sum((item["subtotal"] for item in get_items(request)), Decimal("0.00"))


def count(request):
    return sum(item["quantity"] for item in get_items(request))


def shipping_cost(request, method="standard"):
    return Decimal("150.00") if method == "express" and count(request) else Decimal("0.00")


def total(request, method="standard"):
    return subtotal(request) + shipping_cost(request, method)
