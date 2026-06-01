import csv
import os
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from Home.models import Category, SubCategory, Product


class Command(BaseCommand):
    help = 'Import products in bulk from a CSV file.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file that contains product rows.')
        parser.add_argument(
            '--media-root',
            type=str,
            default=settings.MEDIA_ROOT,
            help='Path to MEDIA_ROOT where image files are stored.',
        )
        parser.add_argument(
            '--default-image',
            type=str,
            default=None,
            help='Optional fallback image file path used when a product image is missing.',
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        media_root = options['media_root']
        default_image = options['default_image']

        if not os.path.exists(csv_file):
            raise CommandError(f'CSV file not found: {csv_file}')

        missing_images = []
        created_count = 0
        updated_count = 0

        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if 'category' not in reader.fieldnames or 'subcategory' not in reader.fieldnames or 'product_name' not in reader.fieldnames or 'product_image' not in reader.fieldnames:
                raise CommandError(
                    'CSV must contain the headers: category, subcategory, product_name, product_image'
                )

            for row in reader:
                category_name = row.get('category', '').strip()
                subcategory_name = row.get('subcategory', '').strip()
                product_name = row.get('product_name', '').strip()
                image_path = row.get('product_image', '').strip()

                if not category_name or not subcategory_name or not product_name or not image_path:
                    self.stdout.write(self.style.WARNING(
                        f'Skipping row because required fields are missing: {row}'
                    ))
                    continue

                category, _ = Category.objects.get_or_create(category_name=category_name)
                subcategory, _ = SubCategory.objects.get_or_create(
                    category=category,
                    name=subcategory_name,
                )

                product_data = {
                    'brand': row.get('brand', '').strip() or None,
                    'price': self._parse_float(row.get('price')),
                    'stock': self._parse_int(row.get('stock')),
                    'expiry_date': self._parse_date(row.get('expiry_date')),
                    'discount_price': self._parse_float(row.get('discount_price')),
                    'description': row.get('description', '').strip() or None,
                    'quantity': self._parse_int(row.get('quantity')),
                    'unit_type': row.get('unit_type', 'tablet').strip() or 'tablet',
                    'is_available': self._parse_bool(row.get('is_available', 'True')),
                }

                product, created = Product.objects.get_or_create(
                    subcategory=subcategory,
                    product_name=product_name,
                    defaults=product_data,
                )

                if not created:
                    for key, value in product_data.items():
                        setattr(product, key, value)

                image_file_path = self._resolve_image_path(image_path, media_root)

                if not image_file_path and default_image:
                    image_file_path = self._resolve_image_path(default_image, media_root, fallback=True)

                if image_file_path and os.path.exists(image_file_path):
                    with open(image_file_path, 'rb') as img_file:
                        django_file = File(img_file)
                        product.product_image.save(os.path.basename(image_file_path), django_file, save=False)
                else:
                    missing_images.append(image_path)
                    self.stdout.write(self.style.WARNING(
                        f'Image not found for "{product_name}": {image_path}'
                    ))

                product.save()

                if created:
                    created_count += 1
                else:
                    updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Import complete: {created_count} created, {updated_count} updated.'
        ))

        if missing_images:
            self.stdout.write(self.style.WARNING(
                f'{len(missing_images)} rows were imported without matching images.'
            ))

    def _resolve_image_path(self, image_path, media_root, fallback=False):
        if os.path.isabs(image_path):
            return image_path

        if os.path.exists(image_path):
            return image_path

        image_path_media = os.path.join(media_root, image_path)
        if os.path.exists(image_path_media):
            return image_path_media

        if fallback:
            return None

        return None

    def _parse_int(self, value):
        if value is None or value == '':
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def _parse_float(self, value):
        if value is None or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def _parse_bool(self, value):
        if isinstance(value, bool):
            return value
        if not value:
            return False
        return str(value).strip().lower() in ['true', '1', 'yes', 'y']

    def _parse_date(self, value):
        if not value:
            return None
        try:
            from datetime import datetime
            return datetime.strptime(value.strip(), '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return None
