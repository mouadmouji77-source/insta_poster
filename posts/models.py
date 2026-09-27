from django.conf import settings
from django.db import models

class Post(models.Model):
    image_url = models.URLField()
    caption = models.TextField()
    post_date = models.DateField()
    post_time = models.TimeField()
    is_published = models.BooleanField(default=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.caption
