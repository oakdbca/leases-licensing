from io import BytesIO
import os
import re
import logging
from django.core.files import File
from django.conf import settings
from django.db import IntegrityError, transaction

from docx import Document

from leaseslicensing.components.approvals.models import (
    ApprovalDocument,
)
from leaseslicensing.components.main.decorators import basic_exception_handler

logger = logging.getLogger(__name__)


class ApprovalDocumentGenerator:

    # Test template property. May be overwritten.
    _license_template = f"{settings.BASE_DIR}/leaseslicensing/templates/doc/leases_licence_template.docx"

    def _docx_replace_regex(
        self,
        doc_obj,
        regex,
        replace,
        key,
        bold=False,
        italic=False,
        underline=False,
        **kwargs,
    ):
        """
        Replaces occurrences of `key` in document paragraphs with value `replace`
        """

        for p in doc_obj.paragraphs:
            if regex.search(p.text):
                # Replace the pattern with itself. This causes the entire paragraph to be the run
                # allowing to sub-replace the pattern, but removing any formatting of that paragraph
                # Adding placeholder to table cells in the template preserves the formatting in cells
                p.text = regex.sub(regex.pattern, p.text)
                # TODO Alternatively, can add sophisticated code to split the paragraph into runs
                # first and `add_run` combine the pieces while preserving any formatting and adding
                # inline formatting to the keys. Such code would need to take handle keys that span
                # multiple runs, e.g. `{{key}}` may translate to three runs `{{`, `key`, and `}}`
                inline = p.runs
                # Loop added to work with runs (strings with same style)
                for i in range(len(inline)):
                    if regex.search(inline[i].text):
                        text = regex.sub(replace, inline[i].text)
                        inline[i].text = text
                        inline[i].bold = bold
                        inline[i].italic = italic
                        inline[i].underline = underline

        for table in doc_obj.tables:
            for row in table.rows:
                for cell in row.cells:
                    self._docx_replace_regex(
                        cell, regex, replace, key, bold, italic, underline
                    )

    @transaction.atomic
    def _approval_document_for_filename(self, approval, filename):
        """
        Gets or creates an ApprovalDocument for the given approval
        """

        try:
            document, created = ApprovalDocument.objects.get_or_create(
                approval=approval, name=filename
            )
        except IntegrityError as e:
            logger.exception(e)
            raise e
        except Exception as e:
            logger.exception(e)
            raise e
        else:
            return document, created

    @basic_exception_handler
    def _filepath_to_buffer(self, filepath):
        try:
            with open(filepath, "rb") as f:
                buffer = f.read()
        except IOError as e:
            logger.exception(f"Can not open file {filepath}")
            raise e
        else:
            return BytesIO(buffer)

    @property
    def license_template(self):
        return self._license_template

    @license_template.setter
    def license_template(self, value):
        self._license_template = value

    @basic_exception_handler
    def approval_buffer(self, approval):
        """
        Test function to create a very basic Approval document from the test template
        """

        doc = Document(self._license_template)

        proposal = approval.current_proposal

        key = "{{applicant_name}}"
        # Licensee example bold (table cell)
        self._docx_replace_regex(
            doc,
            re.compile(rf"{key}"),
            f"{proposal.applicant_name}",
            key,
            True,
            False,
            False,
        )
        # Licence number example italic  (table cell)
        key = "{{lodgement_number}}"
        self._docx_replace_regex(
            doc,
            re.compile(rf"{key}"),
            f"{approval.lodgement_number}",
            key,
            False,
            True,
            False,
        )
        # Start/End date examples underlined (no table, inline replacement)
        key = "{{start_date}}"
        start_date = approval.start_date.strftime("%a %d %b %Y, %I:%M %p")
        self._docx_replace_regex(
            doc, re.compile(rf"{key}"), f"{start_date}", key, False, False, True
        )
        key = "{{expiry_date}}"
        expiry_date = approval.expiry_date.strftime("%a %d %b %Y, %I:%M %p")
        self._docx_replace_regex(
            doc, re.compile(rf"{key}"), f"{expiry_date}", key, False, False, True
        )
        # Issue date example no formatting (no table, inline replacement)
        key = "{{issue_date}}"
        issue_date = approval.issue_date.strftime("%m/%d/%Y, %H:%M:%S")
        self._docx_replace_regex(
            doc, re.compile(rf"{key}"), f"{issue_date}", key, False
        )

        temp_directory = f"{settings.BASE_DIR}/tmp"

        try:
            os.stat(temp_directory)
        except:
            os.mkdir(temp_directory)
        new_doc_file = f"{temp_directory}/licence_{str(approval.lodgement_number)}.docx"
        new_pdf_file = f"{temp_directory}/licence_{str(approval.lodgement_number)}.pdf"
        doc.save(new_doc_file)
        os.system(
            "libreoffice --headless --convert-to pdf "
            + new_doc_file
            + " --outdir "
            + temp_directory
        )

        approval_buffer = self._filepath_to_buffer(new_pdf_file)

        os.remove(new_doc_file)
        os.remove(new_pdf_file)

        return approval_buffer

    @basic_exception_handler
    def update_approval_document_file(self, approval, buffer, filename, **kwargs):
        """
        Updates the ApprovalDocument file identified by filename with buffer
        Args:
            approval:
                Approval object
            buffer:
                File buffer object
            filename:
                Name of the ApprovalDocument file
            reason:
                Reason for creating the document. Must be one of the choices in ApprovalDocument.REASON_CHOICES
        Returns:
            ApprovalDocument object
        """

        file = File(buffer)

        reason = kwargs.get("reason", "new").lower()

        # Validate reason
        reasons = {r[0]: r[1] for r in ApprovalDocument.REASON_CHOICES}
        if reason not in reasons.keys():
            raise AttributeError(
                f"Invalid reason `{reason}` for approval document not in {reasons.keys()}."
            )

        # Get the current or create a new approval document
        document, created = self._approval_document_for_filename(approval, filename)

        version_comment = f"{reasons[reason]} Approval document: {document.name}"
        logger.info(version_comment)

        if not created:
            # If the document already exists, update the reason unless it is 'new'
            if reason == "new":
                raise AttributeError(
                    f"Reason cannot be 'new'. ApprovalDocument {document.name} already exists."
                )
            document.reason = reason

        document._file.save(filename, file, save=True)
        document.save(version_comment=version_comment)

        return document

    def create_license_document(self, approval, filepath=None, filename=None, **kwargs):
        if filepath is None:
            buffer = self.approval_buffer(approval)
        else:
            buffer = self._filepath_to_buffer(filepath)

        if filename is None:
            filename = "Approval-{}.pdf".format(approval.lodgement_number)

        document = self.update_approval_document_file(
            approval, buffer, filename, **kwargs
        )
        buffer.close()
        # Attach the document to the approval
        approval.licence_document = document

        return document

    def create_cover_letter(self, approval, filepath=None, filename=None, **kwargs):
        if filepath is None:
            raise NotImplementedError(
                "Please specify a filepath. Creating cover letters from templates is not implemented yet."
            )
        else:
            buffer = self._filepath_to_buffer(filepath)

        if filename is None:
            filename = "CoverLetter-{}.pdf".format(approval.lodgement_number)

        document = self.update_approval_document_file(
            approval, buffer, filename, **kwargs
        )
        buffer.close()
        # Attach the document to the approval
        approval.cover_letter_document = document

        return document
