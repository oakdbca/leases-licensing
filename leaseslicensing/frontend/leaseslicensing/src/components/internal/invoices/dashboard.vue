<template>
    <div class="container" id="invoicesDash">
        <FormSection :formCollapse="false" label="Invoices" Index="invoices">
            <InvoicesTable
                level="internal"
            />
        </FormSection>
    </div>
</template>

<script>
import FormSection from "@/components/forms/section_toggle.vue"
import InvoicesTable from "@/components/common/table_invoices.vue"
export default {
    name: 'InternalInvoicesDashboard',
    data() {
        let vm = this;
        return {

        }
    },
    components:{
        FormSection,
        InvoicesTable,
    },
    methods: {

    },
}
</script>
