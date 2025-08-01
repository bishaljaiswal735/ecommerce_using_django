from .models import Categorie
def menu_list(request):
    category_objects = Categorie.objects.all()
    return {'category_object':category_objects }