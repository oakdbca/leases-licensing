<template>
    <div id="organisations-dashboard" class="container">
        <FormSection label="Organisations" index="organisations">
            <OrganisationsTable />
        </FormSection>
    </div>
</template>

<script>
import FormSection from '@/components/forms/section_toggle.vue';
import OrganisationsTable from '@/components/common/table_organisations.vue';
export default {
    name: 'InternalOrganisationRequestsDashboard',
    components: {
        FormSection,
        OrganisationsTable,
    },
};
</script>
