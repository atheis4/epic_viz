from django.contrib import admin
from . import models

admin.site.register(models.Artifact)
admin.site.register(models.ArtifactType)
admin.site.register(models.Tag)
admin.site.register(models.ArtifactTag)
