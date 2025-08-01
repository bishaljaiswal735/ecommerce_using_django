from django.db import models
from category.models import Categorie

# Create your models here.
class Product(models.Model):
    product_name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100)
    description = models.TextField(max_length=200,blank=True)
    image = models.ImageField(upload_to='photos/products')
    price = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Categorie, on_delete= models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    stock = models.IntegerField()

    def __str__(self):
        return self.product_name
