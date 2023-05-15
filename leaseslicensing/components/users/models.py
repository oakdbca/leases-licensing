from django.conf import settings
from django.db import models
from ledger_api_client.ledger_models import EmailUserRO as EmailUser

from leaseslicensing.components.main.models import (
    CommunicationsLogEntry,
    Document,
    SecureFileField,
    UserAction,
)


class EmailUserLogEntry(CommunicationsLogEntry):
    email_user = models.IntegerField()

    def __str__(self):
        return f"Email User ID: {self.email_user} - {self.subject}"

    class Meta:
        app_label = "leaseslicensing"


def email_user_comms_log_document_upload_location(instance, filename):
    return "{}/email_user/{}/communications/{}".format(
        settings.MEDIA_APP_DIR, instance.log_entry.email_user, filename
    )


class EmailUserLogDocument(Document):
    log_entry = models.ForeignKey(
        EmailUserLogEntry, related_name="documents", on_delete=models.CASCADE
    )
    _file = SecureFileField(
        upload_to=email_user_comms_log_document_upload_location, max_length=512
    )

    class Meta:
        app_label = "leaseslicensing"


class EmailUserAction(UserAction):
    email_user = models.IntegerField()

    @classmethod
    def log_action(cls, email_user, action, request_user):
        return cls.objects.create(
            email_user=email_user.id,
            who=request_user.id,
            who_full_name=request_user.get_full_name(),
            what=str(action),
        )

    class Meta:
        app_label = "leaseslicensing"


def log_user_action(self, action, request):
    """As EmailUserRO is outside the leaseslicensing app,
    we need to monkey patch it to add the log_user_action method"""
    return EmailUserAction.log_action(self, action, request.user)


setattr(EmailUser, "log_user_action", log_user_action)
