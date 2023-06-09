<template>
    <div :id="'invoiceEditOracleInvoiceNumber' + invoice_id">
        <modal transition="modal fade" :title="title" @ok="validateForm" okText="Update Oracle Invoice Number"
            cancelText="Cancel" large>
            <div class="container">
                <div class="row">
                    <div class="col">
                        <form id="oracle-invoice-number-form" class="needs-validation" novalidate>
                            <div class="row mt-3 mb-3">
                                <label for="oracle-invoice-number" class="col-sm-4 col-form-label">Oracle Invoice
                                    Number</label>
                                <div class="col-sm-8">
                                    <input type="text" class="form-control" id="oracle-invoice-number" required
                                        maxlength="50">
                                    <div class="invalid-feedback">
                                        Please enter the oracle invoice number.
                                    </div>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </modal>
    </div>
</template>

<script>
import modal from '@vue-utils/bootstrap-modal.vue'
import { api_endpoints } from "@/utils/hooks.js"
import Swal from 'sweetalert2'

export default {
    name: 'InvoiceTransactions',
    emits: ['oracleInvoiceNumberUpdated'],
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
        oracle_invoice_number: {
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
    watch: {
        isModalOpen: function (newVal, oldVal) {
            let vm = this;
            if (newVal) {
                vm.$nextTick(function () {
                    $('#oracle-invoice-number').focus();
                    if (this.oracle_invoice_number) {
                        console.log('oracle invoice number: ' + typeof (this.oracle_invoice_number))
                        $('#oracle-invoice-number').val(this.oracle_invoice_number);
                    }
                });
            }
        },
    },
    computed: {
        title: function () {
            return 'Edit Oracle Invoice Number for Invoice: ' + this.invoice_lodgement_number;
        },
    },
    methods: {
        close: function () {
            this.isModalOpen = false;
            $('#oracle-invoice-number').val('');
        },
        validateForm: function () {
            let vm = this;
            var form = document.getElementById('oracle-invoice-number-form')

            if (form.checkValidity()) {
                console.log('Form valid');
                vm.updateOracleInvoiceNumber();
            } else {
                form.classList.add('was-validated');
                $('#oracle-invoice-number-form').find(":invalid").first().focus();
            }

            return false;
        },
        updateOracleInvoiceNumber: function () {
            let vm = this;
            let oracleInvoiceNumber = $('#oracle-invoice-number').val();
            if (oracleInvoiceNumber) {
                const requestOptions = {
                    method: 'PATCH',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        invoice_id: vm.invoice_id,
                        oracle_invoice_number: oracleInvoiceNumber,
                    })
                };
                fetch(api_endpoints.invoices + `${vm.invoice_id}/edit_oracle_invoice_number/`, requestOptions)
                    .then(async (response) => {
                        const data = await response.json()
                        if (!response.ok) {
                            const error =
                                (data && data.message) || response.statusText
                            console.log(error)
                            Promise.reject(error)
                        }
                        console.log('oracle invoice number updated.')
                        Swal.fire({
                            icon: 'success',
                            title: `Update Successful`,
                            text: `Oracle Invoice Number Updated for Invoice: ${vm.invoice_lodgement_number}`,
                            buttonsStyling: false,
                            customClass: {
                                confirmButton: 'btn btn-primary',
                            },
                        })
                        vm.$emit('oracleInvoiceNumberUpdated')
                    })
                    .catch((error) => {
                        console.error('There was an error!', error)
                        Promise.reject(error)
                    })
            }
        },
    },
}
</script>
