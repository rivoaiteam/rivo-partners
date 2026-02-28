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
        from django.core.cache import cache
        cache_key = f'appconfig:{key}'
        value = cache.get(cache_key)
        if value is not None:
            return value
        try:
            config = cls.objects.get(key=key)
            value = cls._parse_value(config.value)
            cache.set(cache_key, value, 3600)
            return value
        except cls.DoesNotExist:
            return default

    @classmethod
    def get_all_config(cls):
        from django.core.cache import cache
        cache_key = 'appconfig:all'
        configs = cache.get(cache_key)
        if configs is not None:
            return configs
        configs = {c.key: cls._parse_value(c.value) for c in cls.objects.all()}
        cache.set(cache_key, configs, 3600)
        return configs

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from django.core.cache import cache
        cache.delete(f'appconfig:{self.key}')
        cache.delete('appconfig:all')

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
