from . import cart

def cart_context(request):
    return {"cart_count": cart.count(request)}
