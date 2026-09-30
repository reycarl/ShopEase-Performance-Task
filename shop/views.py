from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db import transaction
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from . import cart
from .forms import OrderForm, ProductForm
from .models import Category, Order, OrderItem, Product


def is_staff(user):
    return user.is_authenticated and user.is_staff


def htmx(request):
    return request.headers.get("HX-Request") == "true"


def product_list(request):
    products = Product.objects.filter(is_active=True).select_related("category")
    categories = Category.objects.all()

    q = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    sort = request.GET.get("sort", "newest")

    if q:
        products = products.filter(Q(name__icontains=q) | Q(description__icontains=q))
    if category:
        products = products.filter(category__slug=category)

    sort_map = {
        "price_low": "price",
        "price_high": "-price",
        "newest": "-date_created",
    }
    products = products.order_by(sort_map.get(sort, "-date_created"))

    from django.core.paginator import Paginator
    paginator = Paginator(products, 6)
    page_obj = paginator.get_page(request.GET.get("page", 1))

    context = {
        "page_obj": page_obj,
        "products": page_obj.object_list,
        "categories": categories,
        "selected_category": category,
        "q": q,
        "sort": sort,
        "cart_count": cart.count(request),
    }

    if htmx(request):
        return render(request, "partials/_product_grid.html", context)
    return render(request, "product_list.html", context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    error = None
    if request.method == "POST":
        try:
            quantity = int(request.POST.get("quantity", "1"))
        except ValueError:
            quantity = 0
        if quantity < 1:
            error = "Quantity must be at least 1."
        elif quantity > product.stock:
            error = f"Only {product.stock} unit(s) are available."
        else:
            cart.add(request, product, quantity)
            messages.success(request, f"{product.name} added to cart.")
            return redirect("product_detail", pk=pk)
    return render(request, "product_detail.html", {"product": product, "error": error})


def product_manage(request):
    products = Product.objects.select_related("category").all()
    q = request.GET.get("q", "").strip()
    if q:
        products = products.filter(Q(name__icontains=q) | Q(description__icontains=q))
    context = {"products": products, "q": q}
    if htmx(request):
        return render(request, "partials/_product_manage_table.html", context)
    return render(request, "product_manage.html", context)


@user_passes_test(is_staff, login_url="/admin/login/")
def product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        product = form.save()
        messages.success(request, f"{product.name} created successfully.")
        if htmx(request):
            response = HttpResponse(status=204)
            response["HX-Redirect"] = reverse("product_manage")
            return response
        return redirect("product_manage")
    return render(request, "product_form.html", {"form": form, "title": "Add Product"})


@user_passes_test(is_staff, login_url="/admin/login/")
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"{product.name} updated successfully.")
        if htmx(request):
            response = HttpResponse(status=204)
            response["HX-Redirect"] = reverse("product_manage")
            return response
        return redirect("product_manage")
    return render(request, "product_form.html", {"form": form, "title": "Edit Product", "product": product})


@user_passes_test(is_staff, login_url="/admin/login/")
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method != "DELETE" and request.method != "POST":
        raise Http404
    name = product.name
    product.delete()
    if htmx(request):
        return HttpResponse("")
    messages.success(request, f"{name} deleted.")
    return redirect("product_manage")


def cart_add(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    try:
        quantity = int(request.POST.get("quantity", "1"))
    except ValueError:
        quantity = 0

    current = int(cart.get_cart(request).get(str(pk), 0))
    if quantity < 1:
        return HttpResponse("Quantity must be at least 1.", status=400)
    if current + quantity > product.stock:
        return HttpResponse(f"Only {product.stock} unit(s) are available.", status=400)

    cart.add(request, product, quantity)
    if htmx(request):
        return render(request, "partials/_cart_badge.html", {"cart_count": cart.count(request)})
    return redirect("cart")


def cart_view(request):
    items = cart.get_items(request)
    context = {
        "items": items,
        "subtotal": cart.subtotal(request),
        "shipping": cart.shipping_cost(request),
        "total": cart.total(request),
    }
    return render(request, "cart.html", context)


def cart_update(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    try:
        quantity = int(request.POST.get("quantity", "0"))
    except ValueError:
        quantity = 0

    if quantity < 1:
        return HttpResponse("Quantity must be at least 1.", status=400)
    if quantity > product.stock:
        return HttpResponse(f"Only {product.stock} unit(s) are available.", status=400)

    cart.set_quantity(request, product, quantity)
    context = {
        "items": cart.get_items(request),
        "subtotal": cart.subtotal(request),
        "shipping": cart.shipping_cost(request),
        "total": cart.total(request),
    }
    if htmx(request):
        return render(request, "partials/_cart_container.html", context)
    return redirect("cart")


def cart_remove(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method not in ("DELETE", "POST"):
        raise Http404
    cart.remove(request, pk)
    if htmx(request):
        return render(request, "partials/_cart_container.html", {
            "items": cart.get_items(request),
            "subtotal": cart.subtotal(request),
            "shipping": cart.shipping_cost(request),
            "total": cart.total(request),
        })
    return redirect("cart")


def checkout(request):
    items = cart.get_items(request)
    if not items:
        messages.warning(request, "Your cart is empty.")
        return redirect("cart")

    form = OrderForm(request.POST or None)
    context = {
        "form": form,
        "items": items,
        "subtotal": cart.subtotal(request),
        "shipping": cart.shipping_cost(request, request.POST.get("shipping_method", "standard")),
        "total": cart.total(request, request.POST.get("shipping_method", "standard")),
    }

    if request.method == "POST":
        if form.is_valid():
            with transaction.atomic():
                # Lock products and validate stock again at checkout.
                locked = {}
                for item in items:
                    product = Product.objects.select_for_update().get(pk=item["product"].pk)
                    qty = item["quantity"]
                    if qty > product.stock:
                        form.add_error(None, f"{product.name} no longer has enough stock. Available: {product.stock}.")
                        break
                    locked[product.pk] = product
                else:
                    order = form.save(commit=False)
                    order.total = cart.total(request, order.shipping_method)
                    order.save()

                    for item in items:
                        product = locked[item["product"].pk]
                        qty = item["quantity"]
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=qty,
                            unit_price=product.price,
                        )
                        product.stock -= qty
                        product.save(update_fields=["stock"])

                    cart.clear(request)
                    if htmx(request):
                        response = HttpResponse(status=204)
                        response["HX-Redirect"] = reverse("order_confirmation", args=[order.pk])
                        return response
                    return redirect("order_confirmation", pk=order.pk)

        if htmx(request):
            return render(request, "partials/_checkout_form.html", context)

    return render(request, "checkout.html", context)


def checkout_summary(request):
    method = request.GET.get("shipping_method", "standard")
    context = {
        "subtotal": cart.subtotal(request),
        "shipping": cart.shipping_cost(request, method),
        "total": cart.total(request, method),
    }
    if htmx(request):
        return render(request, "partials/_order_summary.html", context)
    return redirect("checkout")


def order_confirmation(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related("items__product"), pk=pk)
    return render(request, "order_success.html", {"order": order})
