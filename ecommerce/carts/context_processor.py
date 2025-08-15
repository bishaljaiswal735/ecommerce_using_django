from .models import CartItem
from .views import _getCartId
def getQuantity(request):
    try:
       if request.user.is_authenticated:
           cartObject = CartItem.objects.filter(user = request.user)
       else:   
            cartObject = CartItem.objects.filter(cart__cart_id = _getCartId(request))
       quantity = 0
       for item in cartObject:
           quantity += item.quantity
    except CartItem.DoesNotExist:
        quantity = 0

    return {'quantity':quantity}
    
