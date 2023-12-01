from django.db import models

# Create your models here.


def meta_fields():
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    return created_at, updated_at


class DhlApiKey(models.Model):
    created, updated = meta_fields()
    key = models.CharField(max_length=1024)
    exhausted = models.BooleanField(default=False)

    async def can_make_request(self):
        return self.exhausted


class DhlKeyUsage(models.Model):
    created, updated = meta_fields()

    key = models.ForeignKey(to=DhlApiKey, on_delete=models.CASCADE)


class GoogleKeyUsage(models.Model):
    created, updated = meta_fields()


class DhlPackage(models.Model):
    created, updated = meta_fields()

    number = models.CharField(max_length=1024, unique=True)
    discovered = models.DateTimeField(auto_now_add=True)
    origin = models.CharField(max_length=1024)
    location = models.CharField(max_length=1024)
    current_status = models.CharField(max_length=512)
    became_pre_transit = models.DateTimeField(null=True)
    became_transit = models.DateTimeField(null=True)
    became_delivered = models.DateTimeField(null=True)
