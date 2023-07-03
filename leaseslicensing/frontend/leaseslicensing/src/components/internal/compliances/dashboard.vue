<template>
    <div id="compliancesDash" class="container">
        <FormSection
            :form-collapse="false"
            label="Compliances"
            index="compliances"
        >
            <CompliancesTable level="internal" />
        </FormSection>
        <FormSection
            :form-collapse="false"
            label="Compliances Referred to Me"
            index="compliances-referred-to-me"
        >
            <CompliancesTable
                level="internal"
                :compliances-referred-to-me="true"
            />
        </FormSection>
    </div>
</template>

<script>
import CompliancesTable from '@/components/common/table_compliances.vue'

export default {
    name: 'InternalCompliancesDashboard',
    components: {
        CompliancesTable,
    },
}
</script>
