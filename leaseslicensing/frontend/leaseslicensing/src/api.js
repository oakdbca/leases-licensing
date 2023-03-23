
module.exports = {
    application_types: '/api/application_types/',
    application_types_dict: '/api/application_types_dict',
    application_statuses_dict: '/api/application_statuses_dict',
    competitive_process_statuses_dict: '/api/competitive_process_statuses_dict',
    applicants_dict: '/api/applicants_dict',
    person_lookup: '/api/users/person_lookup/',
    company_names: '/api/company_names',
    fee_configurations: '/api/fee_configurations',
    approval_types_dict: '/api/approval_types_dict',
    approval_sub_types_dict: '/api/approval_sub_types_dict',
    approval_statuses_dict: '/api/approval_statuses_dict',
    payment_system_id: '/api/payment_system_id',
    fee_seasons_dict: '/api/fee_seasons_dict',
    compliance_statuses_dict: '/api/compliance_statuses_dict',
    referrals: '/api/referrals.json',
    profile: '/api/profile',
    search_reference: '/api/search_reference/',
    submitter_profile: '/api/submitter_profile',
    organisations: '/api/organisations.json',
    organisation_lookup: '/api/organisations/organisation_lookup',
    filtered_organisations: '/api/filtered_organisations',
    organisation_requests_paginated: '/api/organisation_requests_paginated/',
    organisation_requests: '/api/organisation_requests.json',
    organisation_contacts: '/api/organisation_contacts.json',
    organisation_access_group_members: '/api/organisation_access_group_members',
    users_api: '/api/users/',
    users: '/api/users.json',
    filtered_users: '/api/filtered_users',
    countries: '/api/countries',
    proposals: '/api/proposal.json',
    proposals_paginated_list: '/api/proposal_paginated', // both for external and internal
    approvals_paginated_list: '/api/approval_paginated',
    competitive_process: '/api/competitive_process',
    compliances_paginated_external: '/api/compliance_paginated/list_external/',
    compliances: '/api/compliances.json',
    proposal: '/api/proposal/',
    approvals: '/api/approvals/',
    proposal_standard_requirements: '/api/proposal_standard_requirements/application_type_standard_requirements/',
    proposal_requirements: '/api/proposal_requirements.json',
    proposal_by_uuid: '/api/proposal_by_uuid/',
    temporary_document: '/api/temporary_document/',

    lookupApprovalDetails: function (id) {
        return `/api/approvals/${id}/lookup_approval.json`;
    },
    lookupApprovalHistory: function (id) {
        return `/api/approvals/${id}/approval_history?format=datatables`;
    },
    discard_proposal: function (id) {
        return `/api/proposal/${id}.json`;
    },
};
