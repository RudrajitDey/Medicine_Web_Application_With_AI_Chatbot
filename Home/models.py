from django.db import models
from django.utils.text import slugify


# Create models.

# Category_Model
class Category(models.Model):
    category_name = models.CharField(max_length=100)
    category_image = models.ImageField(upload_to="categories/")

    def __str__(self):
        return self.category_name
    

# Category_Wise_Subcategory_Model
class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="subcategories/")
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            count = 1

            while SubCategory.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)
    def __str__(self):
        return self.name
    

class Product(models.Model):
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='products')
    product_name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100, blank=True, null=True)
    product_image = models.ImageField(upload_to="products/")
    slug = models.SlugField(blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    stock = models.IntegerField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    discount_price = models.FloatField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)

    unit_type = models.CharField(max_length=20,
    choices=[
        ('tablet', 'Tablet'),
        ('capsule', 'Capsule'),
        ('ml', 'ML'),
        ('gm', 'Gram'),
    ],
    default='tablet'
    )
    is_available = models.BooleanField(default=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.product_name)
            slug = base_slug
            count = 1

            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.product_name
    
class ProductContents(models.Model):
    SECTION_CHOICES = [
        ('uses', 'Uses'),
        ('dosage', 'Dosage'),
        ('side_effects', 'Side Effects'),
        ('warnings', 'Warnings'),
        ('precautions', 'Precautions'),
        ('interactions', 'Interactions'),
        ('storage', 'Storage'),
        ('quick_tips', 'Quick Tips'),
        ('faq', 'FAQs'),
        ('lifestyle', 'Lifestyle Recommendation'),
    ]

    product_s = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='contents')
    section_type = models.CharField(max_length=50, choices=SECTION_CHOICES)
    title = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField()

    def __str__(self):
        return f"{self.product_s} - {self.section_type}"
    


class ProductPoints(models.Model):
    content = models.ForeignKey(ProductContents, on_delete=models.CASCADE, related_name='points')
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text

# FAQS Model
class faq(models.Model):
    faq_question = models.CharField(max_length=300)
    faq_answer = models.TextField(blank=True)

    def __str__(self):
        return self.faq_question
    
class AdBanner(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='banners/')

    def __str__(self):
        return self.name
    
    

