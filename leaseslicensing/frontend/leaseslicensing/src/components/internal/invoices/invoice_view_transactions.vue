<template>
    <div :id="'invoiceTransactions' + invoice_id">
        <modal transition="modal fade" :title="title" large>
            <div class="container">
                <div class="row">
                    Show Transactions Here.
                </div>
            </div>
        </modal>
    </div>
</template>

<script>
import modal from '@vue-utils/bootstrap-modal.vue'
import { utils } from "@/utils/hooks.js"

export default {
    name: 'InvoiceTransactions',
    components: {
        modal,
    },
    props: {
        invoice_id: {
            type: Number,
            default: null,
        },
        invoice_lodgement_number: {
            type: String,
            default: null,
        },
    },
    data: function () {
        let vm = this;
        return {
            isModalOpen: false,
            transactions: null,
        }
    },
    computed: {
        title: function () {
            return 'Transaction History for Invoice: ' + this.invoice_lodgement_number;
        },
    },
    methods: {

    },
    created: async function () {
        let vm = this;
        vm.transactions = await utils.fetchInvoiceTransactions(vm.invoice_id);
    },
}
</script>
