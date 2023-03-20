""" Custom exceptions for the organisations component """
import logging

logger = logging.getLogger(__name__)


class UnableToRetrieveLedgerOrganisation(Exception):
    """The exception to be thrown if no ledger organisation can be retrieved from the ledger API"""
