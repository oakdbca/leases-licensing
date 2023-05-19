import hashlib
import os

import confy
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
confy.read_environment_file(BASE_DIR + "/.env")
os.environ.setdefault("BASE_DIR", BASE_DIR)

from ledger_api_client.settings_base import *  # noqa: F403

if DEBUG:
    ADMINS = [
        ("Oak McIlwain", "oak.mcilwain@dbca.wa.gov.au"),
        ("Karsten Prehn", "karsten.prehn@dbca.wa.gov.au"),
    ]
else:
    ADMINS = [
        ("ASI", "asi@dpaw.wa.gov.au"),
    ]

ROOT_URLCONF = "leaseslicensing.urls"
SITE_ID = 1
DEPT_DOMAINS = env("DEPT_DOMAINS", ["dpaw.wa.gov.au", "dbca.wa.gov.au"])
SYSTEM_MAINTENANCE_WARNING = env("SYSTEM_MAINTENANCE_WARNING", 24)  # hours
DISABLE_EMAIL = env("DISABLE_EMAIL", False)
SHOW_TESTS_URL = env("SHOW_TESTS_URL", False)
SHOW_DEBUG_TOOLBAR = env("SHOW_DEBUG_TOOLBAR", False)
BUILD_TAG = env(
    "BUILD_TAG", hashlib.md5(os.urandom(32)).hexdigest()
)  # URL of the Dev app.js served by webpack & express
TIME_ZONE = "Australia/Perth"

SILENCE_SYSTEM_CHECKS = env("SILENCE_SYSTEM_CHECKS", False)
if SILENCE_SYSTEM_CHECKS:
    SILENCED_SYSTEM_CHECKS = ["fields.W903", "fields.W904", "debug_toolbar.W004"]


STATIC_URL = "/static/"


INSTALLED_APPS += [
    "reversion",
    "reversion_compare",
    # 'bootstrap3',
    "webtemplate_dbca",
    "leaseslicensing",
    "leaseslicensing.components.main",
    "leaseslicensing.components.organisations",
    "leaseslicensing.components.users",
    "leaseslicensing.components.proposals",
    "leaseslicensing.components.approvals",
    "leaseslicensing.components.compliances",
    "leaseslicensing.components.bookings",
    "leaseslicensing.components.competitive_processes",
    "leaseslicensing.components.invoicing",
    "leaseslicensing.components.tenure",
    "rest_framework",
    "rest_framework_datatables",
    "rest_framework_gis",
    "ledger_api_client",
]

ADD_REVERSION_ADMIN = True

# maximum number of days allowed for a booking
WSGI_APPLICATION = "leaseslicensing.wsgi.application"

"""REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'leaseslicensing.perms.OfficerPermission',
    )
}"""

# REST_FRAMEWORK = {
#    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
#    #'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
#        'PAGE_SIZE': 5
# }

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
        "rest_framework_datatables.renderers.DatatablesRenderer",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "rest_framework_datatables.filters.DatatablesFilterBackend",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework_datatables.pagination.DatatablesPageNumberPagination",
    "PAGE_SIZE": 20,
}


MIDDLEWARE_CLASSES += [
    # 'leaseslicensing.middleware.BookingTimerMiddleware',
    # 'leaseslicensing.middleware.FirstTimeNagScreenMiddleware',
    # 'leaseslicensing.middleware.RevisionOverrideMiddleware',
    "leaseslicensing.middleware.CacheControlMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]
MIDDLEWARE = MIDDLEWARE_CLASSES
MIDDLEWARE_CLASSES = None

if SHOW_DEBUG_TOOLBAR:

    def show_toolbar(request):
        if request:
            return True

    MIDDLEWARE += [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]
    INSTALLED_APPS += ("debug_toolbar",)
    # INTERNAL_IPS = ('127.0.0.1', 'localhost', get_ip())
    INTERNAL_IPS = ("127.0.0.1", "localhost")

    # this dict removes check to dtermine if toolbar should display --> works for rks docker container
    DEBUG_TOOLBAR_CONFIG = {
        # "SHOW_TOOLBAR_CALLBACK": show_toolbar,
        "INTERCEPT_REDIRECTS": False,
    }

TEMPLATES[0]["DIRS"].append(os.path.join(BASE_DIR, "leaseslicensing", "templates"))
TEMPLATES[0]["DIRS"].append(
    os.path.join(
        BASE_DIR, "leaseslicensing", "components", "organisations", "templates"
    )
)
TEMPLATES[0]["DIRS"].append(
    os.path.join(BASE_DIR, "leaseslicensing", "components", "emails", "templates")
)
TEMPLATES[0]["OPTIONS"]["context_processors"].append(
    "leaseslicensing.context_processors.leaseslicensing_url"
)

USE_DUMMY_CACHE = env("USE_DUMMY_CACHE", False)
if USE_DUMMY_CACHE:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        },
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
            "LOCATION": os.path.join(BASE_DIR, "leaseslicensing", "cache"),
        },
    }

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles_ll")
STATICFILES_DIRS.extend(
    [
        os.path.join(os.path.join(BASE_DIR, "leaseslicensing", "static")),
    ]
)
DEV_STATIC = env("DEV_STATIC", False)
DEV_STATIC_URL = env("DEV_STATIC_URL")
if DEV_STATIC and not DEV_STATIC_URL:
    raise ImproperlyConfigured("If running in DEV_STATIC, DEV_STATIC_URL has to be set")
DATA_UPLOAD_MAX_NUMBER_FIELDS = None

# Department details
SYSTEM_NAME = env("SYSTEM_NAME", "Leases and Licensing")
SYSTEM_NAME_SHORT = env("SYSTEM_NAME_SHORT", "LALS")
SITE_PREFIX = env("SITE_PREFIX")
SITE_DOMAIN = env("SITE_DOMAIN")
SUPPORT_EMAIL = env("SUPPORT_EMAIL", "licensing@" + SITE_DOMAIN).lower()
SUPPORT_EMAIL_FILMING = env("SUPPORT_EMAIL_FILMING", "filming@" + SITE_DOMAIN).lower()
DEP_URL = env("DEP_URL", "www." + SITE_DOMAIN)
DEP_PHONE = env("DEP_PHONE", "(08) 9219 9978")
DEP_PHONE_FILMING = env("DEP_PHONE_FILMING", "(08) 9219 8411")
DEP_PHONE_SUPPORT = env("DEP_PHONE_SUPPORT", "(08) 9219 9000")
DEP_FAX = env("DEP_FAX", "(08) 9423 8242")
DEP_POSTAL = env(
    "DEP_POSTAL", "Locked Bag 104, Bentley Delivery Centre, Western Australia 6983"
)
DEP_NAME = env("DEP_NAME", "Department of Biodiversity, Conservation and Attractions")
DEP_NAME_SHORT = env("DEP_NAME_SHORT", "DBCA")
BRANCH_NAME = env("BRANCH_NAME", "Leases and Licensing Branch")
DEP_ADDRESS = env("DEP_ADDRESS", "17 Dick Perry Avenue, Kensington WA 6151")
SITE_URL = env("SITE_URL", "https://" + SITE_PREFIX + "." + SITE_DOMAIN)
PUBLIC_URL = env("PUBLIC_URL", SITE_URL)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", "no-reply@" + SITE_DOMAIN).lower()
MEDIA_APP_DIR = env("MEDIA_APP_DIR", "leaseslicensing")
ADMIN_GROUP = env("ADMIN_GROUP", "LALS Admin")
CRON_RUN_AT_TIMES = env("CRON_RUN_AT_TIMES", "04:05")
CRON_EMAIL = env("CRON_EMAIL", "cron@" + SITE_DOMAIN).lower()
# for ORACLE Job Notification - override settings_base.py
EMAIL_FROM = DEFAULT_FROM_EMAIL
OTHER_PAYMENT_ALLOWED = env("OTHER_PAYMENT_ALLOWED", False)  # Cash/Cheque

OSCAR_BASKET_COOKIE_OPEN = "cols_basket"
PAYMENT_SYSTEM_ID = env("PAYMENT_SYSTEM_ID", "S675")
PAYMENT_SYSTEM_PREFIX = env(
    "PAYMENT_SYSTEM_PREFIX", PAYMENT_SYSTEM_ID.replace("S", "0")
)  # '0675'
os.environ[
    "LEDGER_PRODUCT_CUSTOM_FIELDS"
] = "('ledger_description','quantity','price_incl_tax','price_excl_tax','oracle_code')"
CRON_NOTIFICATION_EMAIL = env("CRON_NOTIFICATION_EMAIL", NOTIFICATION_EMAIL).lower()

if not VALID_SYSTEMS:
    VALID_SYSTEMS = [PAYMENT_SYSTEM_ID]

CRON_CLASSES = [
    "leaseslicensing.cron.OracleIntegrationCronJob",
]

PROTECTED_MEDIA_ROOT = env(
    "PROTECTED_MEDIA_ROOT", os.path.join(BASE_DIR, "protected_media")
)
SECURE_FILE_API_BASE_PATH = "/api/main/secure_file/"
SECURE_DOCUMENT_API_BASE_PATH = "/api/main/secure_document/"

BASE_URL = env("BASE_URL")

CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "full",
        "height": 300,
        # 'width': 300,
        "width": "100%",
    },
    "awesome_ckeditor": {
        "toolbar": "Basic",
    },
}


CONSOLE_EMAIL_BACKEND = env("CONSOLE_EMAIL_BACKEND", False)
if CONSOLE_EMAIL_BACKEND:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# Add a debug level logger for development
if DEBUG:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "verbose": {
                "format": "%(levelname)s %(asctime)s %(name)s [Line:%(lineno)s][%(funcName)s] %(message)s"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
            },
            "leaseslicensing_rotating_file": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(BASE_DIR, "logs", "leaseslicensing.log"),
                "formatter": "verbose",
                "maxBytes": 5242880,
            },
            "mail_admins": {
                "level": "ERROR",
                "class": "django.utils.log.AdminEmailHandler",
                "include_html": True,
            },
        },
        "loggers": {
            "leaseslicensing": {
                "handlers": ["console", "leaseslicensing_rotating_file", "mail_admins"],
                "level": "DEBUG",
                "propagate": False,
            },
        },
    }
else:
    # Additional logging for leaseslicensing
    LOGGING["handlers"]["payment_checkout"] = {
        "level": "INFO",
        "class": "logging.handlers.RotatingFileHandler",
        "filename": os.path.join(
            BASE_DIR, "logs", "leaseslicensing_payment_checkout.log"
        ),
        "formatter": "verbose",
        "maxBytes": 5242880,
    }
    LOGGING["loggers"]["payment_checkout"] = {
        "handlers": ["payment_checkout"],
        "level": "INFO",
    }
    # Add a handler
    LOGGING["handlers"]["file_leaseslicensing"] = {
        "level": "INFO",
        "class": "logging.handlers.RotatingFileHandler",
        "filename": os.path.join(BASE_DIR, "logs", "leaseslicensing.log"),
        "formatter": "verbose",
        "maxBytes": 5242880,
    }
    LOGGING["loggers"]["leaseslicensing"] = {
        "handlers": ["file_leaseslicensing"],
        "level": "INFO",
    }

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
DEV_APP_BUILD_URL = env(
    "DEV_APP_BUILD_URL"
)  # URL of the Dev app.js served by webpack & express

PROPOSAL_TYPE_NEW = "new"
PROPOSAL_TYPE_RENEWAL = "renewal"
PROPOSAL_TYPE_AMENDMENT = "amendment"
PROPOSAL_TYPES = [
    (PROPOSAL_TYPE_NEW, "New Application"),
    (PROPOSAL_TYPE_AMENDMENT, "Amendment"),
    (PROPOSAL_TYPE_RENEWAL, "Renewal"),
]

APPLICATION_TYPE_REGISTRATION_OF_INTEREST = "registration_of_interest"
APPLICATION_TYPE_LEASE_LICENCE = "lease_licence"
APPLICATION_TYPES = [
    (APPLICATION_TYPE_REGISTRATION_OF_INTEREST, "Registration of Interest"),
    (APPLICATION_TYPE_LEASE_LICENCE, "Lease Licence"),
]
KMI_SERVER_URL = env("KMI_SERVER_URL", "https://kmi.dbca.wa.gov.au")
KMI_AUTH_USERNAME = env("KMI_AUTH_USERNAME")
KMI_AUTH_PASSWORD = env("KMI_AUTH_PASSWORD")

APPROVAL_RENEWAL_DAYS_PRIOR_TO_EXPIRY = 90

template_title = "Leases and Licensing"
template_group = "parkswildlife"

LEDGER_TEMPLATE = "bootstrap5"
# LEDGER_UI_ACCOUNTS_MANAGEMENT = [
#    {'first_name': {'options': {'view': True, 'edit': True}}},
#    {'last_name': {'options': {'view': True, 'edit': True}}},
#    {'residential_address': {'options': {'view': True, 'edit': True}}},
#    {'phone_number': {'options': {'view': True, 'edit': True}}},
#    {'mobile_number': {'options': {'view': True, 'edit': True}}},
# ]

GROUP_NAME_ASSESSOR = "proposal_assessor_group"
GROUP_NAME_APPROVER = "proposal_approver_group"
GROUP_NAME_ORGANISATION_ACCESS = "organisation_access_group"
GROUP_REGISTRATION_OF_INTEREST_ASSESSOR = "registration_of_interest_assessor"
GROUP_REGISTRATION_OF_INTEREST_APPROVER = "registration_of_interest_approver"
GROUP_LEASE_LICENCE_ASSESSOR = "lease_licence_assessor"
GROUP_LEASE_LICENCE_APPROVER = "lease_licence_approver"
GROUP_COMPETITIVE_PROCESS_EDITOR = "competitive_process_editor"
GROUP_FINANCE = "finance"
GROUP_NAME_CHOICES = (
    (GROUP_NAME_ASSESSOR, "Proposal Assessor Group"),
    (GROUP_NAME_APPROVER, "Proposal Approver Group"),
    (GROUP_NAME_ORGANISATION_ACCESS, "Organisation Access Group"),
    (GROUP_REGISTRATION_OF_INTEREST_ASSESSOR, "Registration of Interest Assessor"),
    (GROUP_REGISTRATION_OF_INTEREST_APPROVER, "Registration of Interest Approver"),
    (GROUP_LEASE_LICENCE_ASSESSOR, "Lease Licence Assessor"),
    (GROUP_LEASE_LICENCE_APPROVER, "Lease Licence Approver"),
    (GROUP_COMPETITIVE_PROCESS_EDITOR, "Competitive Process Editor"),
    (GROUP_FINANCE, "Finance"),
)
CHARGE_METHOD_ONCE_OFF_CHARGE = "once_off_charge"
CHARGE_METHOD_BASE_FEE_PLUS_FIXED_ANNUAL_INCREMENT = (
    "base_fee_plus_fixed_annual_increment"
)
CHARGE_METHOD_BASE_FEE_PLUS_FIXED_ANNUAL_PERCENTAGE = (
    "base_fee_plus_fixed_annual_percentage"
)
CHARGE_METHOD_BASE_FEE_PLUS_ANNUAL_CPI = "base_fee_plus_annual_cpi"
CHARGE_METHOD_PERCENTAGE_OF_GROSS_TURNOVER = "percentage_of_gross_turnover"
CHARGE_METHOD_NO_RENT_OR_LICENCE_CHARGE = "no_rent_or_licence_charge"
CHARGE_METHODS = (
    (CHARGE_METHOD_ONCE_OFF_CHARGE, "Once-off charge"),
    (
        CHARGE_METHOD_BASE_FEE_PLUS_FIXED_ANNUAL_INCREMENT,
        "Base fee plus fixed annual increment",
    ),
    (
        CHARGE_METHOD_BASE_FEE_PLUS_FIXED_ANNUAL_PERCENTAGE,
        "Base fee plus fixed annual percentage",
    ),
    (CHARGE_METHOD_BASE_FEE_PLUS_ANNUAL_CPI, "Base fee plus annual CPI"),
    (CHARGE_METHOD_PERCENTAGE_OF_GROSS_TURNOVER, "Percentage of gross turnover"),
    (CHARGE_METHOD_NO_RENT_OR_LICENCE_CHARGE, "No rent or licence charge"),
)
REPETITION_TYPE_ANNUALLY = "annually"
REPETITION_TYPE_QUARTERLY = "quarterly"
REPETITION_TYPE_MONTHLY = "monthly"
REPETITION_TYPES = (
    (REPETITION_TYPE_ANNUALLY, "Annually"),
    (REPETITION_TYPE_QUARTERLY, "Quarterly"),
    (REPETITION_TYPE_MONTHLY, "Monthly"),
)

# ---------- Identifier fields for logging ----------

""" Fields that the logging functions will check for on the instance
    and use to identify the instance in the logs. """
ACTION_LOGGING_IDENTIFIER_FIELDS = [
    "lodgement_number",
    "id",
]

# ---------- Cache Timeouts ----------

LOV_CACHE_TIMEOUT = 60 * 60 * 3  # 3 hours

CACHE_TIMEOUT_1_MINUTE = 60
CACHE_TIMEOUT_5_MINUTES = 60 * 5
CACHE_TIMEOUT_2_HOURS = 60 * 60 * 2
CACHE_TIMEOUT_24_HOURS = 60 * 60 * 24

# ---------- Cache Keys ----------

CACHE_KEY_LEDGER_EMAIL_USER = "ledger-emailuser-{}"
CACHE_KEY_LEDGER_ORGANISATION = "ledger-organisation-{}"
CACHE_KEY_ORGANISATION_IDS = "cache_organisation_ids"
CACHE_KEY_ORGANISATIONS = "cache_organisations"
CACHE_KEY_USER_IDS = "cache_user_ids"
CACHE_KEY_COUNTRY_LIST = "country_list"
CACHE_KEY_APPROVAL_STATUSES = "approval_statuses_dict"
CACHE_KEY_APPLICATION_TYPE_DICT_FOR_FILTER = "application_type_dict_for_filter"
CACHE_KEY_APPLICATION_TYPE_DICT = "application_type_dict"
CACHE_KEY_APPLICATION_STATUSES_DICT_INTERNAL = "application_internal_statuses_dict"
CACHE_KEY_APPLICATION_STATUSES_DICT_EXTERNAL = "application_external_statuses_dict"
CACHE_KEY_APPLICATION_STATUSES_DICT_FOR_FILTER = (
    "application_internal_statuses_dict_for_filter"
)
CACHE_KEY_DBCA_LEGISLATED_LANDS_AND_WATERS = "dbca_legislated_lands_and_waters"
CACHE_KEY_MAP_PROPOSALS = "map-proposals"

# ---------- User Log Actions ----------

ACTION_VIEW = "View {} {}"
ACTION_CREATE = "Create {} {}"
ACTION_UPDATE = "Update {} {}"
ACTION_DESTROY = "Destroy {} {}"
