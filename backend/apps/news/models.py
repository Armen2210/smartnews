from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Source(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class News(models.Model):
    class SummaryStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        DONE = "done", "Done"
        FAILED = "failed", "Failed"

    title = models.CharField(max_length=500)
    url = models.URLField(unique=True)

    source = models.ForeignKey(
        Source, on_delete=models.CASCADE, related_name="news"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="news"
    )

    published_at = models.DateTimeField(db_index=True)
    original_text = models.TextField()
    summary_text = models.TextField(null=True, blank=True)

    summary_status = models.CharField(
        max_length=20,
        choices=SummaryStatus.choices,
        default=SummaryStatus.PENDING,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-published_at"]
        indexes = [
            models.Index(fields=["-published_at"]),
        ]

    def __str__(self):
        return self.title[:80]
