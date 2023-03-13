<template>
    <div>
        <CollapsibleFilters component_title="Filters" ref="collapsible_filters" @created="collapsible_component_mounted" class="mb-2">
                <div class="row">
                    <div class="col-md-3">
                        <div class="form-group">
                            <label for="">Organisation</label>
                            <select class="form-control" v-model="filterOrganisation">
                                <option value="all">All</option>
                                <option v-for="organisation in organisations" :value="organisation.id">{{ organisation.name }}</option>
                            </select>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="form-group">
                            <label for="">Payment Status</label>
                            <select class="form-control" v-model="filterInvoiceStatus">
                                <option value="all">All</option>
                                <option v-for="payment_status in invoice_payment_statuses" :value="status.code">{{ status.description }}</option>
                            </select>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="form-group">
                            <label for="">Invoice Date From</label>
                            <div class="input-group date" ref="invoiceDateFromPicker">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterInvoiceDueDateFrom">
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="form-group">
                            <label for="">Invoice Date To</label>
                            <div class="input-group date" ref="invoiceDateToPicker">
                                <input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterInvoiceDueDateTo">
                                <span class="input-group-addon">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

        </CollapsibleFilters>

        <div class="row">
            <div class="col-lg-12">
                <datatable
                    ref="invoices_datatable"
                    :id="datatable_id"
                    :dtOptions="invoicesOptions"
                    :dtHeaders="invoicesHeaders"
                />
            </div>
        </div>
    </div>
</template>

<script>
import datatable from '@/utils/vue/datatable.vue'
import { api_endpoints, helpers }from '@/utils/hooks'
import CollapsibleFilters from '@/components/forms/collapsible_component.vue'

export default {
    name: 'TableInvoices',
    props: {
        level:{
            type: String,
            required: true,
            validator: function(val) {
                let options = ['internal', 'referral', 'external'];
                return options.indexOf(val) != -1 ? true: false;
            }
        },
        target_email_user_id: {
            type: Number,
            required: false,
            default: 0,
        },
    },
    data() {
        let vm = this;
        return {
            datatable_id: 'invoices-datatable-' + vm._uid,

            // selected values for filtering
            filterOrganisation: sessionStorage.getItem('filterOrganisation') ? sessionStorage.getItem('filterOrganisation') : 'all',
            filterInvoiceStatus: sessionStorage.getItem('filterInvoiceStatus') ? sessionStorage.getItem('filterInvoiceStatus') : 'all',
            filterInvoiceDueDateFrom: sessionStorage.getItem('filterInvoiceDueDateFrom') ? sessionStorage.getItem('filterInvoiceDueDateFrom') : '',
            filterInvoiceDueDateTo: sessionStorage.getItem('filterInvoiceDueDateTo') ? sessionStorage.getItem('filterInvoiceDueDateTo') : '',

            // filtering options
            invoice_types: [],
            invoice_statuses: [],

            // Filters toggle
            filters_expanded: false,

            dateFormat: 'DD/MM/YYYY',
            datepickerOptions:{
                format: 'DD/MM/YYYY',
                showClear:true,
                useCurrent:false,
                keepInvalid:true,
                allowInputToggle:true
            },

        }
    },
    components:{
        datatable,
        CollapsibleFilters,
    },
    watch: {
        filterInvoiceStatus: function() {
            this.$refs.invoices_datatable.vmDataTable.draw();
            sessionStorage.setItem('filterInvoiceStatus', this.filterInvoiceStatus);
        },
        filterOrganisation: function() {
            this.$refs.invoices_datatable.vmDataTable.draw();
            sessionStorage.setItem('filterOrganisation', this.filterOrganisation);
        },
        filterInvoiceDueDateFrom: function() {
            this.$refs.invoices_datatable.vmDataTable.draw();
            sessionStorage.setItem('filterInvoiceDueDateFrom', this.filterInvoiceDueDateFrom);
        },
        filterInvoiceDueDateTo: function() {
            this.$refs.invoices_datatable.vmDataTable.draw();
            sessionStorage.setItem('filterInvoiceDueDateTo', this.filterInvoiceDueDateTo);
        },
        filterApplied: function(){
            if (this.$refs.collapsible_filters){
                // Collapsible component exists
                this.$refs.collapsible_filters.show_warning_icon(this.filterApplied)
            }
        }
    },
    computed: {
        filterApplied: function(){
            if(this.filterInvoiceStatus.toLowerCase() === 'all' && this.filterOrganisation.toLowerCase() === 'all' &&
                this.filterInvoiceDueDateFrom.toLowerCase() === '' && this.filterInvoiceDueDateTo.toLowerCase() === ''){
                return false
            } else {
                return true
            }
        },
        is_external: function() {
            return this.level == 'external'
        },
        is_internal: function() {
            return this.level == 'internal'
        },
        invoicesHeaders: function() {
            return [
                'Number',
                'Approval',
                'Type',
                'Holder',
                'Status',
                'Invoice',
                'Amount',
                'GST',
                'Invoice Date',
            ];
        },
        idColumn: function() {
            return {
                data: "id",
                orderable: true,
                searchable: true,
                visible: true,
                'render': function(row, type, full){
                    return full.holder;
                }
            }
        },
        invoiceNumberColumn: function() {
            return {
                data: "invoice_number",
                orderable: true,
                searchable: true,
                visible: true,
                'render': function(row, type, full){
                    return full.invoice_number;
                }
            }
        },
        approvalNumberColumn: function() {
            return {
                data: "approval_number",
                orderable: true,
                searchable: true,
                visible: true,
                'render': function(row, type, full){
                    return full.approval_number
                }
            }
        },
        typeColumn: function() {
            return {
                data: "type",
                orderable: true,
                searchable: true,
                visible: true,
                'render': function(row, type, full){
                    return full.type
                }
            }
        },
        holderColumn: function() {
            return {
                data: "holder",
                orderable: true,
                searchable: true,
                visible: true,
                'render': function(row, type, full){
                    return full.holder
                }
            }
        },
        statusColumn: function() {
            return {
                data: "processing_status",
                orderable: true,
                searchable: true,
                visible: true,
                'render': function(row, type, full){
                    return full.processing_status
                }
            }
        },

        invoiceColumn: function() {
            return {
                data: "invoice",
                orderable: true,
                searchable: true,
                visible: true,
                'render': function(row, type, full){
                    return full.invoice
                }
            }
        },
        amountColumn: function() {
            return {
                data: "amount",
                orderable: true,
                searchable: true,
                visible: true,
                'render': function(row, type, full){
                    return full.amount
                }
            }
        },
        gstColumn: function() {
            return {
                data: "gst",
                orderable: true,
                searchable: true,
                visible: true,
                'render': function(row, type, full){
                    return full.gst
                }
            }
        },
        invoiceDateColumn: function() {
            return {
                data: "invoice_date",
                orderable: true,
                searchable: true,
                visible: true,
                'render': function(row, type, full){
                    return full.invoice_date
                }
            }
        },
        actionColumn: function() {
            let vm = this;
            return {
                        // 7. Action
                        data: "id",
                        orderable: true,
                        searchable: true,
                        visible: true,
                        'render': function(row, type, full){
                        let links = '';
                            links +=  `<a href='${full.id}'>Record Payment</a><br/><a href='${full.id}'>Edit Oracle</a><br /><a href='${full.id}'>Invoice Number</a>`;
                            return links;
                        }
                    }
        },
        assignedToNameColumn: function() {
            return {
                        // 7. Action
                        data: "id",
                        orderable: true,
                        searchable: true,
                        visible: true,
                        'render': function(row, type, full){
                            //return full.assigned_to_name;
                            return full.id;
                        }
                    }
        },

        applicableColumns: function() {
            let columns = [
                this.lodgementNumberColumn,
                this.licenceNumberColumn,
                this.conditionColumn,
                this.dueDateColumn,
                this.statusColumn,
                this.actionColumn,
                ]
            if (this.level === 'internal') {
                columns = [
                    this.lodgementNumberColumn,
                    this.applicationTypeColumn,
                    this.idColumn,
                    this.licenceNumberColumn,
                    //this.conditionColumn,
                    this.statusColumn,
                    this.dueDateColumn,
                    //this.assignedToNameColumn,
                    this.actionColumn,
                    ]
            }
            return columns;
        },
        invoicesOptions: function() {
            let vm = this;
            let buttons = []
            if (this.level === 'internal'){
                buttons = [
                    {
                        extend: 'excel',
                        text: '<i class="fa-solid fa-download"></i> Excel',
                        className: 'btn btn-primary ml-2',
                        exportOptions: {
                            columns: ':visible'
                        }
                    },
                    {
                        extend: 'csv',
                        text: '<i class="fa-solid fa-download"></i> CSV',
                        className: 'btn btn-primary',
                        exportOptions: {
                            columns: ':visible'
                        }
                    },
                ]
            }

            return {
                searching: false,
                autoWidth: false,
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                serverSide: true,
                searching: true,

                ajax: {
                    "url": api_endpoints.invoices_paginated_internal + '?format=datatables',
                    "dataSrc": 'data',

                    // adding extra GET params for Custom filtering
                    "data": function ( d ) {
                        // Add filters selected
                        d.filter_invoice_status = vm.filterInvoiceStatus;
                        d.filter_lodged_from = vm.filterProposalLodgedFrom;
                        d.filter_lodged_to = vm.filterProposalLodgedTo;
                    }
                },
                dom: "<'d-flex align-items-center'<'me-auto'l>fB>" +
                     "<'row'<'col-sm-12'tr>>" +
                     "<'d-flex align-items-center'<'me-auto'i>p>",
                buttons: buttons,
                columns: vm.applicableColumns,
                processing: true,
                initComplete: function() {
                    console.log('in initComplete')
                },
            }
        },

    },
    methods: {
        collapsible_component_mounted: function(){
            this.$refs.collapsible_filters.show_warning_icon(this.filterApplied)
        },
        expandCollapseFilters: function(){
            this.filters_expanded = !this.filters_expanded
        },
        fetchFilterLists: function(){
            let vm = this;

            // Statuses
            fetch(api_endpoints.invoice_statuses_dict).then(async(response) => {
                vm.invoice_statuses = await response.json();
            },(error) => {
                console.log(error);
            })
        },
        addEventListeners: function(){
            let vm = this;
        }
    },
    created: function(){
        this.fetchFilterLists()
    },
    mounted: function(){
        this.$nextTick(() => {
            this.addEventListeners();
        });
    }
}
</script>

<style scoped>
</style>
