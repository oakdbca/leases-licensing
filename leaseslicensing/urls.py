from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.urls import path
from django_media_serv.urls import urlpatterns as media_serv_patterns
from ledger_api_client.urls import urlpatterns as ledger_patterns
from rest_framework import routers

from leaseslicensing import views
from leaseslicensing.admin import admin
from leaseslicensing.components.approvals import api as approval_api
from leaseslicensing.components.bookings import api as booking_api
from leaseslicensing.components.competitive_processes import (
    api as competitive_process_api,
)
from leaseslicensing.components.compliances import api as compliances_api
from leaseslicensing.components.main import api as main_api
from leaseslicensing.components.organisations import api as org_api
from leaseslicensing.components.proposals import api as proposal_api
from leaseslicensing.components.proposals import views as proposal_views
from leaseslicensing.components.tenure import api as tenure_api
from leaseslicensing.components.users import api as users_api
from leaseslicensing.management.default_data_manager import DefaultDataManager
from leaseslicensing.utils import are_migrations_running

# API patterns
router = routers.DefaultRouter()
router.register(r"organisations", org_api.OrganisationViewSet, basename="organisations")
router.register(r"proposal", proposal_api.ProposalViewSet, basename="proposal")
router.register(r"acts", tenure_api.ActViewSet, basename="acts")
router.register(r"tenures", tenure_api.TenureViewSet, basename="tenures")
router.register(r"categories", tenure_api.CategoryViewSet, basename="categories")
router.register(r"regions", tenure_api.RegionViewSet, basename="regions")
router.register(r"districts", tenure_api.DistrictViewSet, basename="districts")
router.register(r"lgas", tenure_api.LGAViewSet, basename="lgas")
router.register(r"groups", tenure_api.GroupViewSet, basename="groups")
router.register(
    r"proposal_submit", proposal_api.ProposalSubmitViewSet, basename="proposal_submit"
)
router.register(
    r"proposal_paginated",
    proposal_api.ProposalPaginatedViewSet,
    basename="proposal_paginated",
)
router.register(r"approval_paginated", approval_api.ApprovalPaginatedViewSet)
router.register(
    r"competitive_process", competitive_process_api.CompetitiveProcessViewSet
)
router.register(r"booking_paginated", booking_api.BookingPaginatedViewSet)
router.register(r"compliance_paginated", compliances_api.CompliancePaginatedViewSet)
router.register(r"referrals", proposal_api.ReferralViewSet)
router.register(r"approvals", approval_api.ApprovalViewSet)
router.register(r"bookings", booking_api.BookingViewSet)
router.register(r"overdue_invoices", booking_api.OverdueBookingInvoiceViewSet)
router.register(r"compliances", compliances_api.ComplianceViewSet)
router.register(r"proposal_requirements", proposal_api.ProposalRequirementViewSet)
router.register(
    r"proposal_standard_requirements", proposal_api.ProposalStandardRequirementViewSet
)
router.register(
    r"organisation_requests_paginated",
    org_api.OrganisationRequestPaginatedViewSet,
    basename="organisation_requests_paginated",
)
router.register(r"organisation_requests", org_api.OrganisationRequestsViewSet)
router.register(r"organisation_contacts", org_api.OrganisationContactViewSet)
router.register(r"my_organisations", org_api.MyOrganisationsViewSet)
router.register(r"users", users_api.UserViewSet)
router.register(r"amendment_request", proposal_api.AmendmentRequestViewSet)
router.register(
    r"compliance_amendment_request", compliances_api.ComplianceAmendmentRequestViewSet
)
router.register(r"global_settings", main_api.GlobalSettingsViewSet)
router.register(r"application_types", main_api.ApplicationTypeViewSet)
router.register(r"assessments", proposal_api.ProposalAssessmentViewSet)
router.register(r"required_documents", main_api.RequiredDocumentViewSet)
router.register(r"questions", main_api.QuestionViewSet)
router.register(r"map_layers", main_api.MapLayerViewSet)
# router.register(r'payment', main_api.PaymentViewSet)
router.register(r"temporary_document", main_api.TemporaryDocumentCollectionViewSet)

api_patterns = [
    url(
        r"^api/account/$",
        users_api.GetLedgerAccount.as_view(),
        name="get-ledger-account",
    ),
    url(
        r"^api/request_user_id/$",
        users_api.GetRequestUserID.as_view(),
        name="get-request-user-id",
    ),
    url(r"^api/profile$", users_api.GetProfile.as_view(), name="get-profile"),
    url(r"^api/countries$", users_api.GetCountries.as_view(), name="get-countries"),
    url(
        r"^api/charge_methods$",
        users_api.GetChargeMethods.as_view(),
        name="get-charge-methods",
    ),
    url(
        r"^api/repetition_types$",
        users_api.GetRepetitionTypes.as_view(),
        name="get-repetition-types",
    ),
    # url(
    #     r"^api/department_users$",
    #     users_api.DepartmentUserList.as_view(),
    #     name="department-users-list",
    # ),
    url(
        r"^api/filtered_users$",
        users_api.UserListFilterView.as_view(),
        name="filtered_users",
    ),
    # url(r'^api/filtered_organisations$', org_api.OrganisationListFilterView.as_view(), name='filtered_organisations'),
    url(
        r"^api/filtered_payments$",
        approval_api.ApprovalPaymentFilterViewSet.as_view(),
        name="filtered_payments",
    ),
    url(
        r"^api/proposal_type$",
        proposal_api.GetProposalType.as_view(),
        name="get-proposal-type",
    ),
    url(
        r"^api/empty_list$", proposal_api.GetEmptyList.as_view(), name="get-empty-list"
    ),
    url(
        r"^api/organisation_access_group_members",
        org_api.OrganisationAccessGroupMembers.as_view(),
        name="organisation-access-group-members",
    ),
    url(r"^api/", include(router.urls)),
    url(
        r"^api/amendment_request_reason_choices",
        proposal_api.AmendmentRequestReasonChoicesView.as_view(),
        name="amendment_request_reason_choices",
    ),
    url(
        r"^api/compliance_amendment_reason_choices",
        compliances_api.ComplianceAmendmentReasonChoicesView.as_view(),
        name="amendment_request_reason_choices",
    ),
    url(
        r"^api/search_keywords",
        proposal_api.SearchKeywordsView.as_view(),
        name="search_keywords",
    ),
    url(
        r"^api/search_reference",
        proposal_api.SearchReferenceView.as_view(),
        name="search_reference",
    ),
    # url(r'^api/applicants_dict$', proposal_api.GetApplicantsDict.as_view(),
    # name='get-applicants-dict'),
    # url(r'^api/oracle_job$',main_api.OracleJob.as_view(), name='get-oracle'),
    # url(r'^api/reports/booking_settlements$', main_api.BookingSettlementReportView.as_view(),
    # name='booking-settlements-report'),
]

# URL Patterns
urlpatterns = (
    [
        # url(r'^admin/', include(leaseslicensing_admin_site.urls)),
        # url(r'^admin/', leaseslicensing_admin_site.urls),
        path(r"admin/", admin.site.urls),
        # url(r'^login/', LoginView.as_view(),name='login'),
        # path('login/', login, name='login'),
        # url(r'^logout/$', LogoutView.as_view(), {'next_page': '/'}, name='logout'),
        url(r"", include(api_patterns)),
        url(r"^$", views.LeasesLicensingRoutingView.as_view(), name="home"),
        url(
            r"^contact/", views.LeasesLicensingContactView.as_view(), name="ds_contact"
        ),
        url(
            r"^further_info/",
            views.LeasesLicensingFurtherInformationView.as_view(),
            name="ds_further_info",
        ),
        url(r"^internal/", views.InternalView.as_view(), name="internal"),
        url(
            r"^internal/proposal/(?P<proposal_pk>\d+)/referral/(?P<referral_pk>\d+)/$",
            views.ReferralView.as_view(),
            name="internal-referral-detail",
        ),
        url(r"^external/", views.ExternalView.as_view(), name="external"),
        url(r"^firsttime/$", views.first_time, name="first_time"),
        url(r"^account/", views.ExternalView.as_view(), name="manage-account"),
        url(r"^profiles/", views.ExternalView.as_view(), name="manage-profiles"),
        url(
            r"^help/(?P<application_type>[^/]+)/(?P<help_type>[^/]+)/$",
            views.HelpView.as_view(),
            name="help",
        ),
        url(
            r"^mgt-commands/$",
            views.ManagementCommandsView.as_view(),
            name="mgt-commands",
        ),
        # url(r'test-emails/$', proposal_views.TestEmailView.as_view(), name='test-emails'),
        url(r"^proposal/$", proposal_views.ProposalView.as_view(), name="proposal"),
        url(
            r"^api/application_types$",
            proposal_api.GetApplicationTypeDescriptions.as_view(),
            name="get-application-type-descriptions",
        ),
        url(
            r"^api/application_types_dict$",
            proposal_api.GetApplicationTypeDict.as_view(),
            name="get-application-type-dict",
        ),
        url(
            r"^api/additional_document_types_dict$",
            proposal_api.GetAdditionalDocumentTypeDict.as_view(),
            name="get-additional-document-types-dict",
        ),
        url(
            r"^api/application_statuses_dict$",
            proposal_api.GetApplicationStatusesDict.as_view(),
            name="get-application-statuses-dict",
        ),
        url(
            r"^api/competitive_process_statuses_dict$",
            competitive_process_api.GetCompetitiveProcessStatusesDict.as_view(),
            name="get-competitive-process-statuses-dict",
        ),
        # Approval type should point to Approval.current_proposal.application_type
        # url(r'^api/approval_types_dict$', approval_api.GetApprovalTypeDict.as_view(),
        # name='get-approval-type-dict'),
        url(
            r"^api/approval_statuses_dict$",
            approval_api.GetApprovalStatusesDict.as_view(),
            name="get-approval-statuses-dict",
        ),
        url(
            r"^api/approval_types_dict$",
            approval_api.GetApprovalTypesDict.as_view(),
            name="get-approval-types-dict",
        ),
        url(
            r"^api/compliance_statuses_dict$",
            compliances_api.GetComplianceStatusesDict.as_view(),
            name="get-compliance-statuses-dict",
        ),
        url(
            r"^internal/proposal/(?P<proposal_pk>\d+)/$",
            views.InternalProposalView.as_view(),
            name="internal-proposal-detail",
        ),
        url(
            r"^internal/approval/(?P<approval_pk>\d+)/$",
            views.InternalApprovalView.as_view(),
            name="internal-approval-detail",
        ),
        url(
            r"^external/proposal/(?P<proposal_pk>\d+)/$",
            views.ExternalProposalView.as_view(),
            name="external-proposal-detail",
        ),
        url(
            r"^external/compliance/(?P<compliance_pk>\d+)/$",
            views.ExternalComplianceView.as_view(),
            name="external-compliance-detail",
        ),
        url(
            r"^internal/compliance/(?P<compliance_pk>\d+)/$",
            views.InternalComplianceView.as_view(),
            name="internal-compliance-detail",
        ),
        url(
            r"^internal/competitive_process/(?P<competitive_process_pk>\d+)/$",
            views.InternalCompetitiveProcessView.as_view(),
            name="internal-competitive-process-detail",
        ),
    ]
    + ledger_patterns
    + media_serv_patterns
)

if settings.DEBUG:  # Serve media locally in development.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    if "debug_toolbar" in settings.INSTALLED_APPS and settings.SHOW_DEBUG_TOOLBAR:
        urlpatterns += [
            # ...
            path("__debug__/", include("debug_toolbar.urls")),
        ]

if not are_migrations_running():
    DefaultDataManager()
