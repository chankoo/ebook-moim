from django.db import models


class SearchHistory(models.Model):
    q = models.CharField(max_length=200, default='')
    user_identifier = models.CharField(max_length=50, default='')

    dt_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-dt_created']
