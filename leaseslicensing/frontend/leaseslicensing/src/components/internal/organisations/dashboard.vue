<template>
    <div class="container" id="organisationRequestsDash">
        <FormSection :formCollapse="false" label="Organisation Access Requests" Index="organisationRequests">
            <OrganisationRequestsTable level="internal" />
        </FormSection>
    </div>
</template>

<script>
import FormSection from "@/components/forms/section_toggle.vue"
import OrganisationRequestsTable from "@/components/common/table_organisation_requests.vue"
export default {
    name: 'InternalOrganisationRequestsDashboard',
    components: {
        FormSection,
        OrganisationRequestsTable,
    },
}
</script>
