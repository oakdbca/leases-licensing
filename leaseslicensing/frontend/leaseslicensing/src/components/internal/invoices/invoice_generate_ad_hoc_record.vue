<template>
    <div id="raiseAdHocInvoice">
        <modal
            transition="modal fade"
            title="Generate Ad Hoc Invoice Record"
            ok-text="Generate Invoice Record"
            cancel-text="Cancel"
            large
            @ok="validateForm"
        >
            <div class="container">
                <div class="row">
                    <div class="col">
                        <form
                            id="generate-ad-hoc-invoice-record-form"
                            class="needs-validation"
                            novalidate
                        >
                            <div class="row mt-3 mb-3">
                                <label
                                    for="approval"
                                    class="col-sm-4 col-form-label"
                                    >Approval</label
                                >
                                <div class="col-sm-8">
                                    <Multiselect
                                        v-model="invoice.approval"
                                        label="lodgement_number"
                                        track-by="id"
                                        placeholder="Select Approval"
                                        :options="approvals"
                                        :hide-selected="true"
                                        :multiple="false"
                                        :searchable="true"
                                        :loading="loadingApprovals"
                                        required
                                    />
                                    <div class="invalid-feedback">
                                        Please select an approval to raise the
                                        invoice against.
                                    </div>
                                </div>
                            </div>
                            <div class="row mt-3 mb-3">
                                <label
                                    for="amount"
                                    class="col-sm-4 col-form-label"
                                    >Amount</label
                                >
                                <div class="col-sm-8">
                                    <input
                                        id="amount"
                                        type="number"
                                        class="form-control"
                                        step="0.01"
                                        required
                                    />
                                    <div class="invalid-feedback">
                                        Please enter the amount.
                                    </div>
                                </div>
                            </div>
                            <div class="row mt-3 mb-3">
                                <label
                                    for="description"
                                    class="col-sm-4 col-form-label"
                                    >Description</label
                                >
                                <div class="col-sm-8">
                                    <textarea
                                        id="description"
                                        class="form-control"
                                        required
                                    ></textarea>
                                    <div class="invalid-feedback">
                                        Please enter the description.
                                    </div>
                                </div>
                            </div>
                            <div class="row mt-3 mb-3">
                                <label
                                    for="issue-date"
                                    class="col-sm-4 col-form-label"
                                    >Issue Date</label
                                >
                                <div class="col-sm-8">
                                    <input
                                        id="issue-date"
                                        class="form-control"
                                        type="date"
                                        required
                                    />
                                    <div class="invalid-feedback">
                                        Please enter an issue date.
                                    </div>
                                </div>
                            </div>
                            <div class="row mt-3 mb-3">
                                <label
                                    for="issue-date"
                                    class="col-sm-4 col-form-label"
                                    >Due Date</label
                                >
                                <div class="col-sm-8">
                                    <input
                                        id="issue-date"
                                        class="form-control"
                                        type="date"
                                        required
                                    />
                                    <div class="invalid-feedback">
                                        Please enter an issue date.
                                    </div>
                                </div>
                            </div>
                            <div class="row mt-3 mb-3">
                                <label
                                    for="oracle-invoice-number"
                                    class="col-sm-4 col-form-label"
                                    >Oracle Invoice Number</label
                                >
                                <div class="col-sm-8">
                                    <input
                                        id="oracle-invoice-number"
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
                                        id="oracle-invoice"
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
import Multiselect from 'vue-multiselect';

export default {
    name: 'InvoiceRaiseAdHoc',
    components: {
        modal,
        Multiselect,
    },
    emits: ['oracleInvoiceNumberUploaded'],
    data: function () {
        return {
            isModalOpen: false,
            invoice: {},
            loadingApprovals: false,
            approvals: [],
        };
    },
    watch: {
        isModalOpen: function (val) {
            if (val) {
                this.$nextTick(() => {
                    $('#generate-ad-hoc-invoice-record-form')
                        .find('input')
                        .first()
                        .focus();
                });
            }
        },
    },
    created: async function () {
        this.fetchApprovals();
    },
    methods: {
        close: function () {
            this.isModalOpen = false;
        },
        confirmUpload: function () {
            Swal.fire({
                title: 'Confirm Ad Hoc Invoice Record Generation',
                text: `You are about to generate an invoice record with the details entered. A payment request will be sent to the proponent immediately.`,
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
            var form = document.getElementById(
                'generate-ad-hoc-invoice-record-form'
            );

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
                vm.generateAdHocInvoiceRecord();
            } else {
                form.classList.add('was-validated');
                $('#oracle-invoice-number-form')
                    .find(':invalid')
                    .first()
                    .focus();
            }

            return false;
        },
        generateAdHocInvoiceRecord: function () {},
        fetchApprovals: async function () {
            let vm = this;
            vm.loadingApprovals = true;

            fetch(api_endpoints.approvals + 'key-value-list/')
                .then(async (response) => {
                    const data = await response.json();
                    if (!response.ok) {
                        const error =
                            (data && data.message) || response.statusText;
                        console.log(error);
                        Promise.reject(error);
                    }
                    vm.approvals = data;
                })
                .catch((error) => {
                    console.error('There was an error!', error);
                    Promise.reject(error);
                })
                .finally(() => {
                    vm.loadingApprovals = false;
                });
        },
    },
};
</script>
