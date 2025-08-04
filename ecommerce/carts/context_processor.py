from .models import CartItem
from .views import _getCartId
def getQuantity(request):
    try:
       cartObject = CartItem.objects.filter(cart__cart_id = _getCartId(request))
       quantity = 0
       for item in cartObject:
           quantity += item.quantity
    except cartObject.DoesNotExist:
        quantity = 0

    return {'quantity':quantity}
    
