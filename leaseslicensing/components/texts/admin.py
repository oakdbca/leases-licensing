from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib import admin

from leaseslicensing.components.texts.models import DetailsText


class DetailsTextForm(forms.ModelForm):
    body = forms.CharField(widget=CKEditorWidget(config_name="toolbar_minimal"))
    target = forms.CharField(widget=forms.TextInput(attrs={"readonly": True}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields[
            "target"
        ].help_text = "The HTML target id of this text's detail text field"
        self.fields["target"].widget.attrs["style"] = "width:400px; height:20px;"
        self.fields[
            "body"
        ].help_text = "The standard text to be used on an empty text field"
        self.fields["body"].widget.attrs["style"] = "width:400px; height:200px;"


@admin.register(DetailsText)
class DetailsTextsAdmin(admin.ModelAdmin):
    fields = (
        "target",
        "body",
    )
    list_display = ("target", "body")

    form = DetailsTextForm
