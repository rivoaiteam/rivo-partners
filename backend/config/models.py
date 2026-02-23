from django.db import models


class AppConfig(models.Model):
    """Admin-configurable key-value store. All monetary values, bonus amounts,
    and display copy come from here and update across the app."""
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True, default='')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'app_config'
        ordering = ['key']

    def __str__(self):
        return f'{self.key} = {self.value}'

    @classmethod
    def get_value(cls, key, default=None):
        try:
            config = cls.objects.get(key=key)
            return cls._parse_value(config.value)
        except cls.DoesNotExist:
            return default

    @classmethod
    def get_all_config(cls):
        configs = cls.objects.all()
        return {c.key: cls._parse_value(c.value) for c in configs}

    @staticmethod
    def _parse_value(value):
        import json
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value


class HomeBanner(models.Model):
    """Configurable banner carousel items for home screen."""
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=500, blank=True, default='')
    icon = models.CharField(max_length=100, blank=True, default='')
    thumbnail = models.URLField(blank=True, default='')
    cta_text = models.CharField(max_length=100, blank=True, default='')
    cta_link = models.URLField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'home_banners'
        ordering = ['order']

    def __str__(self):
        return self.title
