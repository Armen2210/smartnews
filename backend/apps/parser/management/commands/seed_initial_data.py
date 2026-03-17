from django.core.management.base import BaseCommand

from apps.news.models import Category, Source


class Command(BaseCommand):
    help = "Create initial categories and RSS sources"

    def handle(self, *args, **options):
        self.stdout.write("Seeding initial data...")

        categories_data = [
            {"name": "tech", "slug": "tech"},
            {"name": "world", "slug": "world"},
            {"name": "business", "slug": "business"},
        ]

        created_categories = {}

        for item in categories_data:
            category, created = Category.objects.get_or_create(
                slug=item["slug"],
                defaults={"name": item["name"]},
            )
            created_categories[item["slug"]] = category

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created category: {category.slug}"))
            else:
                self.stdout.write(f"Category already exists: {category.slug}")

        sources_data = [
            {
                "name": "BBC Tech",
                "url": "https://feeds.bbci.co.uk/news/technology/rss.xml",
                "category_slug": "tech",
            },
            {
                "name": "Reuters World",
                "url": "https://www.reuters.com/rssFeed/worldNews",
                "category_slug": "world",
            },
        ]

        for item in sources_data:
            source, created = Source.objects.get_or_create(
                url=item["url"],
                defaults={
                    "name": item["name"],
                    "default_category": created_categories[item["category_slug"]],
                    "is_active": True,
                },
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created source: {source.name}"))
            else:
                self.stdout.write(f"Source already exists: {source.name}")

        self.stdout.write(self.style.SUCCESS("Seed completed successfully."))