from .models import CartItem, Cart
from .views import _getCartId
def getQuantity(request):
    quantity = 0

    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
    else:
        cart_id = _getCartId(request)
        try:
            cart = Cart.objects.get(cart_id=cart_id)
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        except Cart.DoesNotExist:
            cart_items = CartItem.objects.none()  # no cart → no items

    quantity = sum(item.quantity for item in cart_items)
    return {'quantity': quantity}
