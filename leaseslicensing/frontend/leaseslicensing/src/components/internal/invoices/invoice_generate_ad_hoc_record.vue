<template>
    <div id="raiseAdHocInvoice">
        <modal
            transition="modal fade"
            title="Generate Ad Hoc Invoice Record"
            ok-text="Generate Invoice Record"
            :ok-disabled="generatingAdHocInvoiceRecord"
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
                            <BootstrapAlert
                                v-if="errors"
                                class="alert alert-danger mb-0"
                                role="alert"
                                icon="exclamation-triangle-fill"
                            >
                                <ErrorRenderer :errors="errors" />
                            </BootstrapAlert>
                            <div class="row mt-3 mb-3">
                                <label
                                    for="approval"
                                    class="col-sm-4 col-form-label"
                                    >Approval</label
                                >
                                <div class="col-sm-8">
                                    <Multiselect
                                        v-if="approvals"
                                        ref="approval"
                                        v-model="invoice.approval"
                                        :custom-label="
                                            (opt) =>
                                                approvals.find(
                                                    (x) => x.id == opt
                                                ).lodgement_number
                                        "
                                        placeholder="Select Approval"
                                        :min-chars="2"
                                        :options="
                                            approvals.map(
                                                (approval) => approval.id
                                            )
                                        "
                                        :allow-empty="false"
                                        :hide-selected="true"
                                        :multiple="false"
                                        :searchable="true"
                                        :loading="loadingApprovals"
                                        :required="true"
                                        @change="updateFieldRequired"
                                    />
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
                                        v-model="invoice.amount"
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
                                        v-model="invoice.description"
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
                                        v-model="invoice.date_issued"
                                        class="form-control"
                                        type="date"
                                        required
                                        @change="updateDueDate"
                                    />
                                    <div class="invalid-feedback">
                                        Please enter an issue date.
                                    </div>
                                </div>
                            </div>
                            <div class="row mt-3 mb-3">
                                <label
                                    for="due-date"
                                    class="col-sm-4 col-form-label"
                                    >Due Date</label
                                >
                                <div class="col-sm-8">
                                    <input
                                        id="due-date"
                                        v-model="invoice.date_due"
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
                                        v-model="invoice.oracle_invoice_number"
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
                                <div
                                    v-if="generatingAdHocInvoiceRecord"
                                    class="col-sm-8"
                                >
                                    <BootstrapSpinner
                                        class="text-primary"
                                        :center-of-screen="false"
                                    />
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
import ErrorRenderer from '@common-utils/ErrorRenderer.vue';

export default {
    name: 'InvoiceRaiseAdHoc',
    components: {
        ErrorRenderer,
        modal,
        Multiselect,
    },
    emits: ['adHocInvoiceRecordGenerated'],
    data: function () {
        return {
            isModalOpen: false,
            invoice: {},
            loadingApprovals: false,
            generatingAdHocInvoiceRecord: false,
            approvals: [],
            errors: null,
        };
    },
    watch: {
        isModalOpen: function (val) {
            if (val) {
                this.$nextTick(() => {
                    this.focusFirstField();
                });
            }
        },
    },
    created: async function () {
        this.fetchApprovals();
    },
    methods: {
        focusFirstField: function () {
            $('#generate-ad-hoc-invoice-record-form')
                .find('input')
                .first()
                .focus();
        },
        updateDueDate: function () {
            if (this.invoice.date_due) {
                return;
            }
            let date_issued = new Date(this.invoice.date_issued);
            let date_due = date_issued.setDate(date_issued.getDate() + 30);
            this.invoice.date_due = new Date(date_due)
                .toISOString()
                .split('T')[0];
        },
        resetInvoice: function () {
            this.invoice = {
                approval: null,
                amount: null,
                description: null,
                date_issued: null,
                date_due: null,
                oracle_invoice_number: null,
            };
        },
        close: function () {
            var form = document.getElementById(
                'generate-ad-hoc-invoice-record-form'
            );
            form.classList.remove('was-validated');
            this.errors = null;
            this.isModalOpen = false;
        },
        updateFieldRequired() {
            this.$nextTick(() => {
                const required =
                    this.required &&
                    (this.option == null ||
                        (Array.isArray(this.option) &&
                            this.option.length == 0 &&
                            this.options.length > 0));
                this.$refs.approval.$el.querySelector('input').required =
                    required;
            });
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

            if (!this.invoice.approval) {
                this.focusFirstField();
                return;
            }

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
        generateAdHocInvoiceRecord: function () {
            let vm = this;
            let oracleInvoice = $('#oracle-invoice').prop('files')[0];
            const formData = new FormData();
            for (let key in this.invoice) {
                formData.append(key, this.invoice[key]);
            }
            formData.append('invoice_pdf', oracleInvoice);
            const requestOptions = {
                method: 'POST',
                body: formData,
            };
            vm.generatingAdHocInvoiceRecord = true;
            fetch(
                api_endpoints.invoices + 'generate_ad_hoc_invoice/',
                requestOptions
            )
                .then(async (response) => {
                    const data = await response.json();
                    if (!response.ok) {
                        const error =
                            (data && data.message) || response.statusText;
                        console.log(error);
                        vm.errors = data;
                        return;
                    }
                    vm.$emit('adHocInvoiceRecordGenerated', data);
                    vm.resetInvoice();
                    Swal.fire({
                        title: 'Ad Hoc Invoice Record Generated',
                        text: `The ad hoc invoice record has been generated.`,
                        icon: 'success',
                        showConfirmButton: false,
                        timer: 2000,
                    });
                    vm.close();
                })
                .catch((error) => {
                    console.error('There was an error!', error);
                    Promise.reject(error);
                })
                .finally(() => {
                    vm.generatingAdHocInvoiceRecord = false;
                });
        },
        fetchApprovals: async function () {
            let vm = this;
            vm.loadingApprovals = true;

            fetch(api_endpoints.approvals + 'key-value-list/')
                .then(async (response) => {
                    const data = await response.json();
                    if (!response.ok) {
                        const error =
                            (data && data.message) || response.statusText;
                        console.error(error);
                    }
                    vm.approvals = data;
                })
                .catch((error) => {
                    console.error('There was an error!', error);
                })
                .finally(() => {
                    vm.loadingApprovals = false;
                });
        },
    },
};
</script>
