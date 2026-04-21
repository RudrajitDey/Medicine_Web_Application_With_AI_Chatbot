from django.db import models

# Create models.

# Category_Model
class Category(models.Model):
    category_name = models.CharField(max_length=100)
    category_image = models.ImageField(upload_to="categories/")

    def __str__(self):
        return self.category_name
    

# Category_Wise_Product_Model
class Product(models.Model):
    product_name = models.CharField(max_length=100)
    product_image = models.ImageField(upload_to="products/")
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.product_name

# FAQS Model
class faq(models.Model):
    faq_question = models.CharField(max_length=300)
    faq_answer = models.TextField(blank=True)

    def __str__(self):
        return self.faq_question
    
    

