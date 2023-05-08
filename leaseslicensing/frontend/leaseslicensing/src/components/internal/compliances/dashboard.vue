<template>
    <div class="container" id="compliancesDash">
        <FormSection :formCollapse="false" label="Compliances" index="compliances">
            <CompliancesTable level="internal" />
        </FormSection>
        <FormSection :formCollapse="false" label="Compliances Referred to Me" index="compliances-referred-to-me">
            <CompliancesTable level="internal" />
        </FormSection>
    </div>
</template>

<script>
import CompliancesTable from "@/components/common/table_compliances.vue"
export default {
    name: 'InternalCompliancesDashboard',
    components: {
        CompliancesTable,
    },
}
</script>
