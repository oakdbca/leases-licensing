<template>
    <div>
        <CollapsibleComponent componentTitle="Filters" ref="collapsible_filters" @created="collapsible_component_mounted"
            class="mb-2">
            <div class="row mt-1 p-2">
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Organisation</label>
                        <select class="form-control" v-model="filterInvoiceOrganisation">
                            <option value="all">All</option>
                            <option v-for="organisation in organisations" :value="organisation.id">
                                {{ organisation.ledger_organisation_name }}
                            </option>
                        </select>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Payment Status</label>
                        <select class="form-control" v-model="filterInvoiceStatus">
                            <option value="all">All</option>
                            <option v-for="status in invoice_statuses" :value="status.id">
                                {{ status.name }}
                            </option>
                            <option value="overdue">Overdue</option>
                        </select>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Invoice Due Date From</label>
                        <div class="input-group date" ref="invoiceDateFromPicker">
                            <input type="date" class="form-control" v-model="filterInvoiceDueDateFrom" />
                            <span class="input-group-addon">
                                <span class="glyphicon glyphicon-calendar"></span>
                            </span>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Invoice Due Date To</label>
                        <div class="input-group date" ref="invoiceDateToPicker">
                            <input type="date" class="form-control" v-model="filterInvoiceDueDateTo" />
                            <span class="input-group-addon">
                                <span class="glyphicon glyphicon-calendar"></span>
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </CollapsibleComponent>

        <div class="row">
            <div class="col-lg-12">
                <datatable ref="invoices_datatable" :id="datatable_id" :dtOptions="invoicesOptions"
                    :dtHeaders="invoicesHeaders" />
            </div>
        </div>

        <InvoiceViewTransactions ref="invoice_view_transactions" :invoice_id="selectedInvoiceId"
            :invoice_lodgement_number="selectedInvoiceLodgementNumber" :invoice_amount="selectedInvoiceAmount">
        </InvoiceViewTransactions>
        <EditOracleInvoiceNumber ref="invoice_edit_oracle_invoice_number" :invoice_id="selectedInvoiceId"
            :invoice_lodgement_number="selectedInvoiceLodgementNumber"
            :oracle_invoice_number="selectedInvoiceOracleInvoiceNumber"
            @oracleInvoiceNumberUpdated="oracleInvoiceNumberUpdated">
        </EditOracleInvoiceNumber>
        <InvoiceRecordTransaction ref="invoice_record_transaction" :invoice_id="selectedInvoiceId"
            :invoice_lodgement_number="selectedInvoiceLodgementNumber" :balance_remaining="selectedInvoiceBalanceRemaining"
            @transactionRecorded="transactionRecorded">
        </InvoiceRecordTransaction>
    </div>
</template>

<script>
import datatable from '@/utils/vue/datatable.vue'
import InvoiceViewTransactions from '../internal/invoices/invoice_view_transactions.vue'
import InvoiceRecordTransaction from '../internal/invoices/invoice_record_transaction.vue'
import EditOracleInvoiceNumber from '../internal/invoices/invoice_edit_oracle_invoice_number.vue'

import { v4 as uuid } from 'uuid';
import { api_endpoints, constants, helpers, utils } from '@/utils/hooks'

export default {
    name: 'TableInvoices',
    props: {
        level: {
            type: String,
            required: true,
            validator: function (val) {
                let options = ['internal', 'referral', 'external']
                return options.indexOf(val) != -1 ? true : false
            },
        },
        approval_id: {
            type: Number,
            required: false,
        },
        target_email_user_id: {
            type: Number,
            required: false,
        },
    },
    data() {
        let vm = this
        return {
            datatable_id: 'invoices-datatable-' + uuid(),

            // selected values for filtering
            filterInvoiceOrganisation: sessionStorage.getItem('filterInvoiceOrganisation')
                ? sessionStorage.getItem('filterInvoiceOrganisation')
                : 'all',
            filterInvoiceStatus: sessionStorage.getItem('filterInvoiceStatus')
                ? sessionStorage.getItem('filterInvoiceStatus')
                : 'all',
            filterInvoiceDueDateFrom: sessionStorage.getItem(
                'filterInvoiceDueDateFrom'
            )
                ? sessionStorage.getItem('filterInvoiceDueDateFrom')
                : '',
            filterInvoiceDueDateTo: sessionStorage.getItem(
                'filterInvoiceDueDateTo'
            )
                ? sessionStorage.getItem('filterInvoiceDueDateTo')
                : '',

            // filtering options
            organisations: [],
            invoice_types: [],
            invoice_statuses: [],

            // Filters toggle
            filters_expanded: false,

            selectedInvoiceId: null,
            selectedInvoiceLodgementNumber: null,
            selectedInvoiceAmount: null,
            selectedInvoiceOracleInvoiceNumber: null,
            selectedInvoiceBalanceRemaining: null,

            dateFormat: 'DD/MM/YYYY',
            datepickerOptions: {
                format: 'DD/MM/YYYY',
                showClear: true,
                useCurrent: false,
                keepInvalid: true,
                allowInputToggle: true,
            },
        }
    },
    components: {
        datatable,
        InvoiceViewTransactions,
        EditOracleInvoiceNumber,
        InvoiceRecordTransaction,
    },
    watch: {
        filterInvoiceOrganisation: function () {
            this.$refs.invoices_datatable.vmDataTable.draw()
            sessionStorage.setItem(
                'filterInvoiceOrganisation',
                this.filterInvoiceOrganisation
            )
        },
        filterInvoiceStatus: function () {
            this.$refs.invoices_datatable.vmDataTable.draw()
            sessionStorage.setItem(
                'filterInvoiceStatus',
                this.filterInvoiceStatus
            )
        },
        filterInvoiceDueDateFrom: function () {
            this.$refs.invoices_datatable.vmDataTable.draw()
            sessionStorage.setItem(
                'filterInvoiceDueDateFrom',
                this.filterInvoiceDueDateFrom
            )
        },
        filterInvoiceDueDateTo: function () {
            this.$refs.invoices_datatable.vmDataTable.draw()
            sessionStorage.setItem(
                'filterInvoiceDueDateTo',
                this.filterInvoiceDueDateTo
            )
        },
        filterApplied: function () {
            if (this.$refs.collapsible_filters) {
                // Collapsible component exists
                this.$refs.collapsible_filters.showWarningIcon(
                    this.filterApplied
                )
            }
        },
    },
    computed: {
        url: function () {
            if (this.approval_id) {
                return api_endpoints.invoices + `?approval_id=${this.approval_id}&format=datatables`
            }
            return api_endpoints.invoices + '?format=datatables'
        },
        filterApplied: function () {
            if (
                this.filterInvoiceStatus.toLowerCase() === 'all' &&
                this.filterInvoiceOrganisation === 'all' &&
                this.filterInvoiceDueDateFrom.toLowerCase() === '' &&
                this.filterInvoiceDueDateTo.toLowerCase() === ''
            ) {
                return false
            } else {
                return true
            }
        },
        is_external: function () {
            return this.level == 'external'
        },
        is_internal: function () {
            return this.level == 'internal'
        },
        invoicesHeaders: function () {
            if (this.approval_id) {

            }
            return [
                'ID',
                'Number',
                'Approval',
                'Type',
                'Holder',
                'Status',
                'Invoice',
                'Amount',
                'Inc GST',
                'Date Due',
                'Date Issued',
                'Action',
                'Oracle Invoice Number',
            ]
        },
        idColumn: function () {
            return {
                data: 'id',
                orderable: true,
                searchable: true,
                visible: false,
                render: function (row, type, full) {
                    return full.id
                },
            }
        },
        lodgementNumberColumn: function () {
            return {
                data: 'lodgement_number',
                orderable: true,
                searchable: true,
                visible: true,
                render: function (row, type, full) {
                    return full.lodgement_number
                },
            }
        },
        approvalColumn: function () {
            return {
                data: 'approval_lodgement_number',
                orderable: true,
                searchable: true,
                visible: true,
                name: 'approval.lodgement_number',
                render: function (row, type, full) {
                    return full.approval_lodgement_number
                },
            }
        },
        approvalTypeColumn: function () {
            return {
                data: 'approval_type',
                orderable: true,
                searchable: false, // TODO: Change this once approvals have a proper approval type field
                visible: true,
                render: function (row, type, full) {
                    return full.approval_type
                },
            }
        },
        holderColumn: function () {
            return {
                data: 'holder',
                orderable: true,
                searchable: false,
                visible: true,
                render: function (row, type, full) {
                    return full.holder
                },
            }
        },
        statusColumn: function () {
            return {
                data: 'status_display',
                orderable: true,
                searchable: true,
                visible: true,
                name: 'status',
                render: function (row, type, full) {
                    let status_html = '';
                    if ('unpaid' == full.status) {
                        if (new Date(full.date_due) < new Date()) {
                            return `<span class="badge bg-danger">${full.status_display} (Overdue)</span>`
                        }
                        return `<span class="badge bg-warning">${full.status_display}</span>`
                    }
                    if ('paid' == full.status) {
                        return `<span class="badge bg-success">${full.status_display}</span>`
                    }
                    if ('void' == full.status) {
                        return `<span class="badge bg-secondary">${full.status_display}</span>`
                    }
                },
            }
        },
        invoicePDFColumn: function () {
            return {
                data: 'invoice_pdf_secure_url',
                orderable: true,
                searchable: false,
                visible: true,
                render: function (row, type, full) {
                    return `<a href="${full.invoice_pdf_secure_url}" target="_blank">Invoice <i class="fa-solid fa-file-pdf fa-lg ps-1" style="color:red;"></i></a>`
                },
            }
        },
        amountColumn: function () {
            return {
                data: 'amount',
                orderable: true,
                searchable: true,
                visible: true,
                render: function (row, type, full) {
                    return `$${full.amount}`
                },
            }
        },
        incGSTColumn: function () {
            return {
                data: 'inc_gst',
                orderable: true,
                searchable: true,
                visible: true,
                render: function (row, type, full) {
                    if (full.inc_gst) {
                        return '<i class="fa fa-check" aria-hidden="true" style="color:green;"></i>';
                    } else {
                        return '<i class="fa fa-times" aria-hidden="true" style="color:red;"></i>';
                    }
                },
            }
        },
        dateIssuedColumn: function () {
            return {
                data: 'date_issued',
                orderable: true,
                searchable: true,
                visible: true,
                render: function (row, type, full) {
                    return new Date(full.date_issued).toLocaleDateString('en-AU')
                },
            }
        },
        dateDueColumn: function () {
            return {
                data: 'date_due',
                orderable: true,
                searchable: true,
                visible: true,
                render: function (row, type, full) {
                    return new Date(full.date_due).toLocaleDateString('en-AU')
                },
            }
        },
        actionColumn: function () {
            let vm = this
            return {
                data: 'id',
                orderable: true,
                searchable: true,
                visible: true,
                render: function (row, type, full) {
                    let links = ''
                    if (full.transaction_count > 0) {
                        links += `<a href="#${full.id}" data-view-transactions="${full.id}" data-invoice-lodgement-number="${full.lodgement_number}" data-invoice-amount="${full.amount}">View Transactions</a><br />`;
                    }
                    // In the case that an invoice is overpaid we will want to allow recording a transaction to correct the balance
                    if ('unpaid' === full.status || full.balance != '0.00') {
                        links += `<a href="#${full.id}" data-record-transaction="${full.id}" data-invoice-lodgement-number="${full.lodgement_number}" data-balance-remaining="${full.balance}">Record Transaction</a><br />`;
                    }
                    if (full.is_finance_officer) {
                        links += `<a href="#${full.id}" data-edit-oracle-invoice-number="${full.id}" data-invoice-lodgement-number="${full.lodgement_number}" data-oracle-invoice-number="${full.oracle_invoice_number}">Edit Oracle Invoice Number</a><br />`;
                    }
                    return links
                },
            }
        },
        oracleInvoiceNumberColumn: function () {
            return {
                data: 'oracle_invoice_number',
                orderable: true,
                searchable: false,
                visible: true,
                render: function (row, type, full) {
                    let oracleInvoiceNumber = 'Not Yet Entered';
                    if (full.oracle_invoice_number) {
                        oracleInvoiceNumber = full.oracle_invoice_number;
                    }
                    return oracleInvoiceNumber;
                },
            }
        },
        applicableColumns: function () {
            let columns = [
                this.idColumn,
                this.lodgementNumberColumn,
                this.approvalColumn,
                this.approvalTypeColumn,
                this.holderColumn,
                this.statusColumn,
                this.invoicePDFColumn,
                this.amountColumn,
                this.incGSTColumn,
                this.dateDueColumn,
                this.dateIssuedColumn,
                this.actionColumn,
            ]
            if (this.level === 'internal') {
                columns = [
                    this.idColumn,
                    this.lodgementNumberColumn,
                    this.approvalColumn,
                    this.approvalTypeColumn,
                    this.holderColumn,
                    this.statusColumn,
                    this.invoicePDFColumn,
                    this.amountColumn,
                    this.incGSTColumn,
                    this.dateDueColumn,
                    this.dateIssuedColumn,
                    this.actionColumn,
                    this.oracleInvoiceNumberColumn,
                ]
            }
            return columns
        },
        invoicesOptions: function () {
            let vm = this
            let buttons = []
            if (this.level === 'internal') {
                buttons = [
                    {
                        extend: 'excel',
                        text: '<i class="fa-solid fa-download"></i> Excel',
                        className: 'btn btn-primary ml-2',
                        exportOptions: {
                            columns: ':visible',
                        },
                    },
                    {
                        extend: 'csv',
                        text: '<i class="fa-solid fa-download"></i> CSV',
                        className: 'btn btn-primary',
                        exportOptions: {
                            columns: ':visible',
                        },
                    },
                ]
            }

            return {
                searching: true,
                autoWidth: true,
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML,
                },
                responsive: true,
                serverSide: true,

                ajax: {
                    url: vm.url
                    ,
                    dataSrc: 'data',

                    // adding extra GET params for Custom filtering
                    data: function (d) {
                        // Add filters selected
                        d.filter_invoice_organisation = vm.filterInvoiceOrganisation
                        d.filter_invoice_status = vm.filterInvoiceStatus
                        d.filter_invoice_due_date_from = vm.filterInvoiceDueDateFrom
                        d.filter_invoice_due_date_to = vm.filterInvoiceDueDateTo
                    },
                },
                dom: "<'d-flex align-items-center'<'me-auto'l>fB>" +
                    "<'row'<'col-sm-12'tr>>" +
                    "<'d-flex align-items-center'<'me-auto'i>p>",
                buttons: buttons,
                columns: vm.applicableColumns,
                processing: true,
                initComplete: function () {
                    console.log('in initComplete')
                },
            }
        },
    },
    methods: {
        collapsible_component_mounted: function () {
            this.$refs.collapsible_filters.showWarningIcon(this.filterApplied)
        },
        adjust_table_width: function () {
            this.$refs.invoices_datatable.vmDataTable.columns.adjust()
            this.$refs.invoices_datatable.vmDataTable.responsive.recalc()
        },
        expandCollapseFilters: function () {
            this.filters_expanded = !this.filters_expanded
        },
        fetchFilterLists: async function () {
            let vm = this

            fetch(api_endpoints.invoices + 'statuses/').then(
                async (response) => {
                    vm.invoice_statuses = await response.json()
                },
                (error) => {
                    console.log(error)
                }
            )

            fetch(api_endpoints.organisations + 'key-value-list/')
                .then(async (response) => {
                    const data = await response.json()
                    if (!response.ok) {
                        const error =
                            (data && data.message) || response.statusText
                        console.log(error)
                        reject(error)
                    }
                    console.log('organisations: ', data)
                    vm.organisations = data;
                })
                .catch((error) => {
                    console.error('There was an error!', error)
                    reject(error)
                })
        },
        viewTransactions: function (id, lodgement_number, amount) {
            let vm = this;
            vm.selectedInvoiceId = parseInt(id);
            vm.selectedInvoiceLodgementNumber = lodgement_number;
            console.log('amount: ', amount)
            vm.selectedInvoiceAmount = Number(amount);
            vm.$refs.invoice_view_transactions.isModalOpen = true;
        },
        editOracleInvoiceNumber: function (id, lodgement_number, oracle_invoice_number) {
            let vm = this;
            vm.selectedInvoiceId = parseInt(id);
            vm.selectedInvoiceLodgementNumber = lodgement_number;
            console.log(typeof (oracle_invoice_number))
            vm.selectedInvoiceOracleInvoiceNumber = oracle_invoice_number;
            vm.$refs.invoice_edit_oracle_invoice_number.isModalOpen = true;
        },
        oracleInvoiceNumberUpdated: function (oracle_invoice_number) {
            let vm = this;
            vm.$refs.invoice_edit_oracle_invoice_number.isModalOpen = false;
            vm.$refs.invoices_datatable.vmDataTable.draw();
        },
        recordTransaction: function (id, lodgement_number, balance_remaining) {
            let vm = this;
            vm.selectedInvoiceId = parseInt(id);
            vm.selectedInvoiceLodgementNumber = lodgement_number;
            vm.selectedInvoiceBalanceRemaining = Number(balance_remaining);
            vm.$refs.invoice_record_transaction.isModalOpen = true;
        },
        transactionRecorded: function () {
            let vm = this;
            vm.$refs.invoice_record_transaction.isModalOpen = false;
            vm.$refs.invoices_datatable.vmDataTable.draw();
        },
        addEventListeners: function () {
            let vm = this;

            vm.$refs.invoices_datatable.vmDataTable.on('click', 'a[data-view-transactions]', function (e) {
                e.preventDefault();
                var id = $(this).attr('data-view-transactions');
                var lodgement_number = $(this).attr('data-invoice-lodgement-number');
                var amount = $(this).attr('data-invoice-amount');
                vm.viewTransactions(id, lodgement_number, amount);
            });

            vm.$refs.invoices_datatable.vmDataTable.on('click', 'a[data-edit-oracle-invoice-number]', function (e) {
                e.preventDefault();
                var id = $(this).attr('data-edit-oracle-invoice-number');
                var lodgement_number = $(this).attr('data-invoice-lodgement-number');
                var oracle_invoice_number = $(this).attr('data-oracle-invoice-number');
                if (oracle_invoice_number == 'null') {
                    oracle_invoice_number = null;
                }
                vm.editOracleInvoiceNumber(id, lodgement_number, oracle_invoice_number);
            });

            vm.$refs.invoices_datatable.vmDataTable.on('click', 'a[data-record-transaction]', function (e) {
                e.preventDefault();
                var id = $(this).attr('data-record-transaction');
                var lodgement_number = $(this).attr('data-invoice-lodgement-number');
                var balance_remaining = $(this).attr('data-balance-remaining');
                vm.recordTransaction(id, lodgement_number, balance_remaining);
            });
        },
    },
    created: function () {
        this.fetchFilterLists()
    },
    mounted: function () {
        this.$nextTick(() => {
            this.addEventListeners()
        })
    },
}
</script>
