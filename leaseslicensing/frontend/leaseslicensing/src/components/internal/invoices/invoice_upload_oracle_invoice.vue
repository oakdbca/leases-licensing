<template>
    <div :id="'invoiceEditOracleInvoiceNumber' + invoiceId" :key="invoiceId">
        <modal
            transition="modal fade"
            :title="title"
            ok-text="Upload Oracle Invoice"
            cancel-text="Cancel"
            large
            @ok="validateForm"
        >
            <div class="container">
                <div class="row">
                    <div class="col">
                        <form
                            id="oracle-invoice-number-form"
                            class="needs-validation"
                            novalidate
                        >
                            <div class="row mt-3 mb-3">
                                <label
                                    for="oracle-invoice-number"
                                    class="col-sm-4 col-form-label"
                                    >Oracle Invoice Number</label
                                >
                                <div class="col-sm-8">
                                    <input
                                        :id="
                                            'oracle-invoice-number' + invoiceId
                                        "
                                        v-model="oracleInvoiceNumber"
                                        type="text"
                                        class="form-control"
                                        required
                                        maxlength="50"
                                    />
                                    <div class="invalid-feedback">
                                        Please enter the oracle invoice number.
                                    </div>
                                </div>
                            </div>
                            <div class="row mb-3">
                                <label
                                    for="formFile"
                                    class="col-form-label col-sm-4"
                                    >Oracle Invoice</label
                                >
                                <div class="col-sm-8">
                                    <input
                                        :id="'oracle-invoice' + invoiceId"
                                        class="form-control"
                                        type="file"
                                        data-filetype="application/pdf"
                                        accepts=".pdf"
                                        required
                                    />
                                    <div class="invalid-feedback">
                                        Please select the oracle invoice file
                                        (.pdf)
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
import modal from '@vue-utils/bootstrap-modal.vue';
import { api_endpoints } from '@/utils/hooks.js';
import Swal from 'sweetalert2';

export default {
    name: 'InvoiceTransactions',
    components: {
        modal,
    },
    props: {
        invoiceId: {
            type: Number,
            default: null,
        },
        invoiceLodgementNumber: {
            type: String,
            default: null,
        },
        selectedOracleInvoiceNumber: {
            type: String,
            default: null,
        },
    },
    emits: ['oracleInvoiceNumberUploaded'],
    data: function () {
        return {
            isModalOpen: false,
            oracleInvoiceNumber: null,
        };
    },
    computed: {
        title: function () {
            return (
                'Upload Oracle Invoice for Invoice: ' +
                this.invoiceLodgementNumber
            );
        },
    },
    watch: {
        isModalOpen: function (newVal) {
            let vm = this;
            if (newVal) {
                vm.$nextTick(function () {
                    $('#oracle-invoice-number' + vm.invoiceId).focus();
                    if (this.selectedOracleInvoiceNumber) {
                        this.oracleInvoiceNumber =
                            this.selectedOracleInvoiceNumber;
                    }
                });
            }
        },
    },
    methods: {
        close: function () {
            this.isModalOpen = false;
            $('#oracle-invoice-number').val('');
        },
        confirmUpload: function () {
            Swal.fire({
                title: 'Confirm Oracle Invoice Upload',
                text: `You are about to upload the oracle invoice for invoice record: ${this.invoiceLodgementNumber}.\
                The system will notify the proponent that a new invoice has been raised.`,
                icon: 'warning',
                showCancelButton: true,
                reverseButtons: true,
                buttonsStyling: false,
                customClass: {
                    confirmButton: 'btn btn-primary',
                    cancelButton: 'btn btn-secondary',
                },
            }).then((result) => {
                if (result.isConfirmed) {
                    return this.validateForm();
                }
            });
        },
        validateForm: function () {
            let vm = this;
            var form = document.getElementById('oracle-invoice-number-form');

            let oracleInvoice = document.getElementById('oracle-invoice');
            if (
                !oracleInvoice.files[0] ||
                oracleInvoice.files[0].name.split('.').pop() != 'pdf'
            ) {
                oracleInvoice.setCustomValidity(
                    'The oracle invoice file must be a pdf file.'
                );
            } else {
                oracleInvoice.setCustomValidity('');
            }

            if (form.checkValidity()) {
                vm.updateOracleInvoiceNumber();
            } else {
                form.classList.add('was-validated');
                $('#oracle-invoice-number-form')
                    .find(':invalid')
                    .first()
                    .focus();
            }

            return false;
        },
        updateOracleInvoiceNumber: function () {
            let vm = this;
            let oracleInvoice = document.getElementById(
                'oracle-invoice' + vm.invoiceId
            );

            var data = new FormData();
            data.append('oracle_invoice_number', vm.oracleInvoiceNumber);
            data.append('invoice_pdf', oracleInvoice.files[0]);

            const requestOptions = {
                method: 'POST',
                body: data,
            };
            fetch(
                api_endpoints.invoices +
                    `${vm.invoiceId}/upload_oracle_invoice/`,
                requestOptions
            )
                .then(async (response) => {
                    const data = await response.json();
                    if (!response.ok) {
                        const error =
                            (data && data.message) || response.statusText;
                        console.error(error);
                        Swal.fire({
                            icon: 'error',
                            title: `Upload Failed`,
                            text: JSON.stringify(data.errors),
                            buttonsStyling: false,
                            customClass: {
                                confirmButton: 'btn btn-primary',
                            },
                        });
                        return;
                    }
                    Swal.fire({
                        icon: 'success',
                        title: `Upload Successful`,
                        text: `Oracle Invoice Number Uploaded for Invoice Record: ${vm.invoiceLodgementNumber}`,
                        buttonsStyling: false,
                        customClass: {
                            confirmButton: 'btn btn-primary',
                        },
                    });
                    vm.$emit('oracleInvoiceNumberUploaded');
                })
                .catch((error) => {
                    console.error('There was an error!', error);
                });
        },
    },
};
</script>
