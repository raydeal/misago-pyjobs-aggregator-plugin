from django import forms
from django.contrib import admin

from .models import AggregatorConfig, CollectionState, ImportedJob


class AggregatorConfigForm(forms.ModelForm):
    keywords = forms.CharField(
        help_text="Comma-separated keywords. Matching is case-insensitive and uses OR semantics."
    )

    class Meta:
        model = AggregatorConfig
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and isinstance(self.instance.keywords, list):
            self.initial["keywords"] = ", ".join(self.instance.keywords)

    def clean_keywords(self):
        value = self.cleaned_data["keywords"]
        result = [item.strip() for item in value.split(",") if item.strip()]
        if not result:
            raise forms.ValidationError("At least one keyword is required.")
        return result


@admin.register(AggregatorConfig)
class AggregatorConfigAdmin(admin.ModelAdmin):
    form = AggregatorConfigForm
    list_display = ("collection_enabled", "solid_division", "updated_at")


@admin.register(ImportedJob)
class ImportedJobAdmin(admin.ModelAdmin):
    list_display = ("source_id", "job_id", "thread_id", "last_published_at")
    search_fields = ("source_id", "job_id")
    readonly_fields = [field.name for field in ImportedJob._meta.fields]


@admin.register(CollectionState)
class CollectionStateAdmin(admin.ModelAdmin):
    readonly_fields = [field.name for field in CollectionState._meta.fields]
