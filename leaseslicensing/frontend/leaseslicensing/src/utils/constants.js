module.exports = {
    APPLICATION_TYPES: {
        REGISTRATION_OF_INTEREST: 'registration_of_interest',
        LEASE_LICENCE: 'lease_licence',
    },
    ROLES: {
        GROUP_NAME_ASSESSOR: { ID: 'proposal_assessor_group', TEXT: 'Proposal Assessor Group' },
        GROUP_NAME_APPROVER: { ID: 'proposal_approver_group', TEXT: 'Proposal Approver Group' },
        COMPETITIVE_PROCESS_EDITOR: { ID: 'competitive_process_editor', TEXT: 'Competitive Process Editor' },
        FINANCE: { ID: 'finance', TEXT: 'Finance' },
        REFERRAL: { ID: 'referral', TEXT: 'Referral' },
    },
    PROPOSAL_STATUS: {
        DRAFT: { ID: 'draft', TEXT: 'Draft' },
        AMENDMENT_REQUIRED: { ID: 'amendment_required', TEXT: 'Amendment Required' },
        WITH_ASSESSOR: { ID: 'with_assessor', TEXT: 'With Assessor' },
        WITH_ASSESSOR_CONDITIONS: { ID: 'with_assessor_conditions', TEXT: 'With Assessor (Conditions)' },
        WITH_APPROVER: { ID: 'with_approver', TEXT: 'With Approver' },
        WITH_REFERRAL: { ID: 'with_referral', TEXT: 'With Referral' },
        WITH_REFERRAL_CONDITIONS: { ID: 'with_referral_conditions', TEXT: 'With Referral (Conditions)' },
        APPROVED_APPLICATION: { ID: 'approved_application', TEXT: 'Approved (Application)' },
        APPROVED_COMPETITIVE_PROCESS: { ID: 'approved_competitive_process', TEXT: 'Approved (Competitive Process)' },
        APPROVED_EDITING_INVOICING: { ID: 'approved_editing_invoicing', TEXT: 'Approved (Editing Invoicing)' },
        APPROVED: { ID: 'approved', TEXT: 'Approved' },
        DECLINED: { ID: 'declined', TEXT: 'Declined' },
        DISCARDED: { ID: 'discarded', TEXT: 'Discarded' },
    },
    COMPETITIVE_PROCESS_STATUS: {
        IN_PROGRESS: { ID: 'in_progress', TEXT: 'In Progress' },
        DISCARDED: { ID: 'discarded', TEXT: 'Discarded' },
        COMPLETED_APPLICATION: { ID: 'completed_application', TEXT: 'Completed (Application)' },
        COMPLETED_DECLINED: { ID: 'completed_declined', TEXT: 'Completed (Declined)' },
    },
    COMPLIANCE_PROCESSING_STATUS: {
        DUE: { ID: 'due', TEXT: 'Due' },
        FUTURE: { ID: 'future', TEXT: 'Future' },
        WITH_ASSESSOR: { ID: 'with_assessor', TEXT: 'With Assessor' },
        APPROVED: { ID: 'approved', TEXT: 'Approved' },
        DISCARDED: { ID: 'discarded', TEXT: 'Discarded' },
        OVERDUE: { ID: 'overdue', TEXT: 'Overdue' },
    },
    APPROVAL_STATUS: {
        CURRENT: { ID: 'current', TEXT: 'Current' },
        CURRENT_BASE_FEE_REVIEW: { ID: 'current_base_fee_review', TEXT: 'Current (base fee review)' },
        APPROVAL_STATUS_CURRENT_PENDING_RENEWAL_REVIEW: { ID: 'current_pending_renewal_review', TEXT: 'Current (Pending Renewal Review)' },
        CURRENT_EDITING_INVOICING: { ID: 'current_editing_invoicing', TEXT: 'Current (Editing Invoicing)' },
        CANCELLED: { ID: 'cancelled', TEXT: 'Cancelled' },
        SURRENDERED: { ID: 'surrendered', TEXT: 'Surrendered' },
        SUSPENDED: { ID: 'suspended', TEXT: 'Suspended' },
        HOLD_OVER_LEASE_DEED_OF_LICENCE: { ID: 'hold_over_lease_deed_of_licence', TEXT: 'Hold-over (lease, deed of licence)' },
        HOLD_OVER_BASE_FEE_REVIEW: { ID: 'hold_over_base_fee_review', TEXT: 'Hold-over (base fee review)' },
        EXTENDED_LEASE_DEED_OF_LICENCE: { ID: 'extended_lease_deed_of_licence', TEXT: 'Extended (lease, deed of licence)' },
        EXTENDED_BASE_FEE_REVIEW: { ID: 'extended_base_fee_review', TEXT: 'Extended (base fee review)' },
        EXPIRED_LICENCE: { ID: 'expired_licence', TEXT: 'Expired (licence)' },
    },
    REFERRAL_STATUS: {
        PROCESSING_STATUS_WITH_REFERRAL: { ID: 'pending', TEXT: 'Pending' },
        PROCESSING_STATUS_RECALLED: { ID: 'recalled', TEXT: 'Recalled' },
        PROCESSING_STATUS_COMPLETED: { ID: 'completed', TEXT: 'Completed' },
    },

    DATATABLE_PROCESSING_HTML: '<div class="d-flex justify-content-center"><div class="d-flex spinner-border text-primary my-4" role="status"><span class="visually-hidden">Loading...</span></div></div>',

    ERRORS: {
        NETWORK_ERROR: 'NETWORK ERROR: Please check your internet connection and try again. If the problem persists contact us at: ?.?@dbca.wa.gov.au',
        API_ERROR: 'API ERROR: An error has occured accessing the Leases and Licenses System API. Please try again \
            in an hour and if the problem persists contact us at: ?.?@dbca.wa.gov.au',
        API_ERROR_INTERNAL: 'API ERROR: An error has occured accessing the Leases and Licenses System API. Please try again \
            in an hour and if the problem persists contact the IT Service Desk.',
    }

};
