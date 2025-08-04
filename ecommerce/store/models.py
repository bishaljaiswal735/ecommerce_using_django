from django.db import models
from category.models import Categorie


# Create your models here.
class Product(models.Model):
    product_name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100)
    description = models.TextField(max_length=200, blank=True)
    image = models.ImageField(upload_to="photos/products")
    price = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    stock = models.IntegerField()

    def __str__(self):
        return self.product_name

class VariationManager(models.Manager):
    def color(self):
        return super(VariationManager, self).filter(variation_category = "color" , is_active=True)
    def size(self):
        return super(VariationManager, self).filter(variation_category = "size" , is_active=True)

variation_category_choice = (("color", "color"), ("size", "size"))


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(
        max_length=100, choices=variation_category_choice
    )
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    objects = VariationManager()
    def __str__(self):
       return self.variation_value
