<template>
    <div>
        <CollapsibleFilters component_title="Filters" ref="collapsible_filters" @created="collapsible_component_mounted"
            class="mb-2">
            <div class="row">
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Type</label>
                        <select class="form-control" v-model="filterComplianceType">
                            <option value="all">All</option>
                            <option v-for="t in compliance_types" :value="t.id">{{ t.name_display }}</option>
                        </select>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Status</label>
                        <select class="form-control" v-model="filterComplianceStatus">
                            <option value="all">All</option>
                            <option v-for="status in compliance_statuses" :value="status.code">{{ status.description }}
                            </option>
                        </select>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Due Date From</label>
                        <div class="input-group date" ref="complianceDateFromPicker">
                            <input type="date" class="form-control" placeholder="DD/MM/YYYY"
                                v-model="filterComplianceDueDateFrom">
                            <span class="input-group-addon">
                                <span class="glyphicon glyphicon-calendar"></span>
                            </span>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Due Date To</label>
                        <div class="input-group date" ref="complianceDateToPicker">
                            <input type="date" class="form-control" placeholder="DD/MM/YYYY"
                                v-model="filterComplianceDueDateTo">
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
                <datatable ref="compliances_datatable" :id="datatable_id" :dtOptions="compliancesOptions"
                    :dtHeaders="compliancesHeaders" />
            </div>
        </div>
    </div>
</template>

<script>
import datatable from '@/utils/vue/datatable.vue'
import { api_endpoints, constants, helpers } from '@/utils/hooks'
import CollapsibleFilters from '@/components/forms/collapsible_component.vue'

export default {
    name: 'TableCompliances',
    props: {
        level: {
            type: String,
            required: true,
            validator: function (val) {
                let options = ['internal', 'referral', 'external', 'organisation_view'];
                return options.indexOf(val) != -1 ? true : false;
            }
        },
        target_email_user_id: {
            type: Number,
            required: false,
            default: 0,
        },
        target_organisation_id: {
            type: Number,
            required: false,
            default: 0,
        },
        compliances_referred_to_me: {
            type: Boolean,
            default: false,
        },
    },
    data() {
        let vm = this;
        return {
            datatable_id: 'compliances-datatable-' + vm._.uid,

            // selected values for filtering
            filterComplianceType: sessionStorage.getItem('filterComplianceType') ? sessionStorage.getItem('filterComplianceType') : 'all',
            filterComplianceStatus: sessionStorage.getItem('filterComplianceStatus') ? sessionStorage.getItem('filterComplianceStatus') : 'all',
            filterComplianceDueDateFrom: sessionStorage.getItem('filterComplianceDueDateFrom') ? sessionStorage.getItem('filterComplianceDueDateFrom') : '',
            filterComplianceDueDateTo: sessionStorage.getItem('filterComplianceDueDateTo') ? sessionStorage.getItem('filterComplianceDueDateTo') : '',

            // filtering options
            compliance_types: [],
            compliance_statuses: [],

            // Filters toggle
            filters_expanded: false,

            dateFormat: 'DD/MM/YYYY',
            datepickerOptions: {
                format: 'DD/MM/YYYY',
                showClear: true,
                useCurrent: false,
                keepInvalid: true,
                allowInputToggle: true
            },

        }
    },
    components: {
        datatable,
        CollapsibleFilters,
    },
    watch: {
        filterComplianceType: function () {
            this.$refs.compliances_datatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem('filterComplianceType', this.filterComplianceType);
        },
        filterComplianceStatus: function () {
            this.$refs.compliances_datatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem('filterComplianceStatus', this.filterComplianceStatus);
        },
        filterComplianceDueDateFrom: function () {
            this.$refs.compliances_datatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem('filterComplianceDueDateFrom', this.filterComplianceDueDateFrom);
        },
        filterComplianceDueDateTo: function () {
            this.$refs.compliances_datatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem('filterComplianceDueDateTo', this.filterComplianceDueDateTo);
        },
        filterApplied: function () {
            if (this.$refs.collapsible_filters) {
                // Collapsible component exists
                this.$refs.collapsible_filters.show_warning_icon(this.filterApplied)
            }
        }
    },
    computed: {
        filterApplied: function () {
            if (this.filterComplianceType === 'all' && this.filterComplianceStatus.toLowerCase() === 'all' &&
                this.filterComplianceDueDateFrom.toLowerCase() === '' && this.filterComplianceDueDateTo.toLowerCase() === '') {
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
        is_organisation_view: function () {
            return this.level == 'organisation_view'
        },
        compliancesHeaders: function () {
            let headers = ['Number', 'Type', 'Holder', 'Approval', 'Status', 'Due Date', 'Action'];
            if (this.is_organisation_view) {
                headers = ['Number', 'Type', 'Approval', 'Status', 'Due Date', 'Action'];
            } else if (this.level === 'internal') {
                headers = ['Number', 'Type', 'Holder', 'Approval', 'Status', 'Due Date', 'Assigned To', 'Action'];
            }
            return headers;
        },
        holderColumn: function () {
            return {
                data: "id",
                orderable: true,
                searchable: true,
                visible: true,
                'render': function (row, type, full) {
                    //return full.approval_submitter;
                    return full.holder;
                },
                name: 'proposal__ind_applicant__first_name, proposal__ind_applicant__last_name'
            }
        },
        applicationTypeColumn: function () {
            return {
                data: "id",
                orderable: true,
                searchable: true,
                visible: true,
                'render': function (row, type, full) {
                    return full.application_type;
                    //return full.id;
                },
                // Searches for `registration_of_interest` or `lease_licence`, but should suffice
                name: 'proposal__application_type__name'
            }
        },
        lodgementNumberColumn: function () {
            return {
                // 2. Lodgement Number
                data: "id",
                orderable: true,
                searchable: true,
                visible: true,
                'render': function (row, type, full) {
                    return full.lodgement_number;
                },
                name: 'lodgement_number',
            }
        },
        licenceNumberColumn: function () {
            return {
                // 3. Licence/Permit
                data: "id",
                orderable: true,
                searchable: true,
                visible: true,
                'render': function (row, type, full) {
                    return full.approval_lodgement_number
                    //return full.id;
                },
                name: "approval__lodgement_number",
            }
        },
        dueDateColumn: function () {
            return {
                // 5. Due Date
                data: "id",
                orderable: true,
                searchable: false,
                visible: true,
                'render': function (row, type, full) {
                    let dueDate = '';
                    if (full.requirement) {
                        dueDate = full.requirement.read_due_date;
                    }
                    //return dueDate;
                    return full.due_date;
                },
                name: "due_date",
            }
        },
        processingStatusColumn: function () {
            let vm = this;
            return {
                data: "processing_status",
                orderable: true,
                searchable: true,
                visible: true,
                render: function (row, type, full) {
                    return vm.getStatusHtml(full.processing_status)
                },
            }
        },
        customerStatusColumn: function () {
            let vm = this;
            return {
                data: "customer_status",
                orderable: true,
                searchable: true,
                visible: true,
                render: function (row, type, full) {
                    return vm.getStatusHtml(full.customer_status)
                },
            }
        },
        actionColumn: function () {
            let vm = this;
            return {
                // 7. Action
                data: "id",
                orderable: false,
                searchable: false,
                visible: true,
                'render': function (row, type, full) {
                    let links = '';
                    if (!vm.is_external) {
                        //if (full.processing_status=='With Assessor' && vm.check_assessor(full)) {
                        if (full.can_process) {
                            links += `<a href='/internal/compliance/${full.id}'>Process</a><br/>`;

                        }
                        else {
                            links += `<a href='/internal/compliance/${full.id}'>View</a><br/>`;
                        }
                    }
                    else {
                        // FIXME If checked for `can_user_view` first an already submitted Compliance can potentially be submitted again and again
                        if (full.can_user_view) {
                            links += `<a href='/external/compliance/${full.id}'>View</a><br/>`;

                        }
                        else {
                            links += `<a href='/external/compliance/${full.id}'>Submit</a><br/>`;
                        }
                    }
                    return links;
                }
            }
        },
        assignedToNameColumn: function () {
            return {
                // 7. Action
                data: "id",
                orderable: true,
                searchable: true,
                visible: true,
                'render': function (row, type, full) {
                    return full.assigned_to_name;
                }
            }
        },
        applicableColumns: function () {
            let columns = [
                this.lodgementNumberColumn, // Number
                this.applicationTypeColumn, // Type
                this.holderColumn, // Holder
                this.licenceNumberColumn, // Approval
                this.customerStatusColumn, // Status
                this.dueDateColumn, // Due Date
                this.actionColumn, //Action
            ]
            if (this.is_organisation_view) {
                columns = [
                    this.lodgementNumberColumn,
                    this.applicationTypeColumn,
                    this.licenceNumberColumn,
                    this.processingStatusColumn,
                    this.dueDateColumn,
                    this.actionColumn,
                ]
            }
            else if (this.level === 'internal') {
                columns = [
                    this.lodgementNumberColumn,
                    this.applicationTypeColumn,
                    this.holderColumn,
                    this.licenceNumberColumn,
                    this.processingStatusColumn,
                    this.dueDateColumn,
                    this.assignedToNameColumn,
                    this.actionColumn,
                ]
            }
            return columns;
        },
        compliancesOptions: function () {
            let vm = this;
            let buttons = []
            if (this.level === 'internal') {
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
                    processing: constants.DATATABLE_PROCESSING_HTML,
                },
                responsive: true,
                serverSide: true,
                searching: true,

                ajax: {
                    "url": api_endpoints.compliances_paginated_external + '?format=datatables&target_email_user_id=' + vm.target_email_user_id +
                        '&target_organisation_id=' + vm.target_organisation_id + '&compliances_referred_to_me=' + vm.compliances_referred_to_me,
                    "dataSrc": 'data',

                    // adding extra GET params for Custom filtering
                    "data": function (d) {
                        // Add filters selected
                        d.filter_application_type = vm.filterComplianceType;
                        d.filter_compliance_status = vm.filterComplianceStatus;
                        d.filter_due_date_from = vm.filterComplianceDueDateFrom;
                        d.filter_due_date_to = vm.filterComplianceDueDateTo;
                    }
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
            this.$refs.collapsible_filters.show_warning_icon(this.filterApplied)
        },
        expandCollapseFilters: function () {
            this.filters_expanded = !this.filters_expanded
        },
        getStatusHtml: function (status) {
            let class_name = '';
            let icon = '';

            if ('Future' == status) {
                class_name = 'info';
                icon = 'calendar-plus';
            }
            if ('Due Soon' == status) {
                class_name = 'warning';
                icon = 'clock';
            }
            if ('Overdue' == status) {
                class_name = 'danger';
                icon = 'exclamation-circle';
            }
            if ('With Assessor' == status) {
                class_name = 'primary';
                icon = 'clipboard';
            }
            if ('Under Review' == status) {
                class_name = 'secondary';
                icon = 'clipboard';
            }
            if ('Approved' == status) {
                class_name = 'success';
                icon = 'check';
            }
            return `<span class="badge bg-${class_name} py-2"><i class="fa fa-${icon}" aria-hidden="true"></i> ${status}</span>`

        },
        fetchFilterLists: function () {
            let vm = this;

            // Types
            fetch(api_endpoints.application_types + 'key-value-list/')
                .then(async (response) => {
                    const data = await response.json()
                    if (!response.ok) {
                        const error =
                            (data && data.message) || response.statusText
                        console.log(error)
                        return Promise.reject(error)
                    }
                    vm.compliance_types = data
                    console.log('Compliance Types: ')
                    console.log(vm.compliance_types)
                })
                .catch((error) => {
                    console.error('There was an error!', error)
                })

            // Statuses
            fetch(api_endpoints.compliance_statuses_dict)
                .then(async (response) => {
                    const data = await response.json()
                    if (!response.ok) {
                        const error =
                            (data && data.message) || response.statusText
                        console.log(error)
                        return Promise.reject(error)
                    }
                    vm.compliance_statuses = data
                    console.log('Compliance Statuses: ')
                    console.log(vm.compliance_statuses)
                })
                .catch((error) => {
                    console.error('There was an error!', error)
                })
        },
    },
    created: function () {
        this.fetchFilterLists();
        $.fn.pulse = function (options) {
            var options = $.extend({
                times: 3,
                duration: 1000
            }, options);

            var period = function (callback) {
                $(this).animate({ opacity: 0 }, options.duration, function () {
                    $(this).animate({ opacity: 1 }, options.duration, callback);
                });
            };
            return this.each(function () {
                var i = +options.times, self = this,
                    repeat = function () { --i && period.call(self, repeat) };
                period.call(this, repeat);
            });
        };
        $('.pulsate').each(function (element) {
            $(element).pulse({ times: 6, duration: 1000 });
        });
    },
}
</script>

