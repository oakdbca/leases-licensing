<template>
    <div class="container" id="externalDash">
        <FormSection :formCollapse="false" label="Applications" subtitle="- View existing applications and lodge new ones"
            Index="applications">
            <ApplicationsTable level="external" />
        </FormSection>

        <FormSection :formCollapse="false" label="Leases and Licences"
            subtitle="- View existing licences / permits and renew them" Index="licences_and_permits">
            <ApprovalsTable level="external" :approvalTypeFilter="allApprovalTypeFilter" />
        </FormSection>

        <FormSection :formCollapse="false" label="Compliances" subtitle="- View submitted Compliances and submit new ones"
            Index="compliances">
            <CompliancesTable level="external" />
        </FormSection>
    </div>
</template>

<script>
import FormSection from "@/components/forms/section_toggle.vue"
import ApplicationsTable from "@/components/common/table_proposals"
import ApprovalsTable from "@/components/common/table_approvals"
import CompliancesTable from "@/components/common/table_compliances"
import { api_endpoints, helpers } from '@/utils/hooks'

export default {
    name: 'ExternalDashboard',
    data() {
        let vm = this;
        return {
            proposals_url: api_endpoints.proposals_paginated_external,
            approvals_url: api_endpoints.approvals_paginated_external,
            compliances_url: api_endpoints.compliances_paginated_external,
            allApprovalTypeFilter: ['ml', 'aap', 'aup'],
            wlaApprovalTypeFilter: ['wla',],
        }
    },
    components: {
        FormSection,
        ApplicationsTable,
        ApprovalsTable,
        CompliancesTable,
    },
    computed: {
        is_external: function () {
            return this.level == 'external'
        },
        is_internal: function () {
            return this.level == 'internal'
        },
    },
    mounted: function () {
        // must be at top level of every page with <FormSection> component
        chevron_toggle.init();
    },
}
</script>
