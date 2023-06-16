<template>
    <div>
        <CollapsibleComponent componentTitle="Filters" ref="collapsible_filters" @created="collapsible_component_mounted"
            class="mb-2">
            <div class="row mt-1 p-2">
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Organisation</label>
                        <select class="form-control" v-model="filterOrganisation">
                            <option value="">All</option>
                            <option v-for="organisation in organisations" :value="organisation.id">
                                {{ organisation.ledger_organisation_name }}
                            </option>
                        </select>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Role</label>
                        <select class="form-control" v-model="filterRole">
                            <option value="">All</option>
                            <option value="employee">Employee</option>
                            <option value="consultant">Consultant</option>
                        </select>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Status</label>
                        <select class="form-control" v-model="filterStatus">
                            <option value="">All</option>
                            <option value="with_assessor">With Assessor</option>
                            <option value="approved">Approved</option>
                            <option value="declined">Declined</option>
                        </select>
                    </div>
                </div>
            </div>
        </CollapsibleComponent>

        <div class="row">
            <div class="col-lg-12">
                <datatable ref="organisation_requests_datatable" :id="datatable_id" :dtOptions="dtOptions"
                    :dtHeaders="dtHeaders" />
            </div>
        </div>
    </div>
</template>

<script>
import datatable from '@/utils/vue/datatable.vue'
import { api_endpoints, constants, helpers } from '@/utils/hooks'

export default {
    name: 'TableOrganisationRequests',
    props: {
        level: {
            type: String,
            required: true,
            validator: function (val) {
                let options = ['internal', 'referral', 'external']
                return options.indexOf(val) != -1 ? true : false
            },
        },
        target_email_user_id: {
            type: Number,
            required: false,
            default: 0,
        },
    },
    data() {
        let vm = this
        return {
            datatable_id: 'invoices-datatable-' + vm._uid,

            // selected values for filtering
            filterOrganisation: sessionStorage.getItem('filterOrganisation')
                ? sessionStorage.getItem('filterOrganisation')
                : '',
            filterRole: sessionStorage.getItem('filterRole')
                ? sessionStorage.getItem('filterRole')
                : '',
            filterStatus: sessionStorage.getItem('filterStatus')
                ? sessionStorage.getItem('filterStatus')
                : '',

            organisations: [],
            statuses: [],
            // Filters toggle
            filters_expanded: false,
        }
    },
    components: {
        datatable,
    },
    watch: {
        filterOrganisation: function () {
            this.$refs.organisation_requests_datatable.vmDataTable.draw()
            sessionStorage.setItem(
                'filterOrganisation',
                this.filterOrganisation
            )
        },
        filterRole: function () {
            this.$refs.organisation_requests_datatable.vmDataTable.draw()
            sessionStorage.setItem(
                'filterRole',
                this.filterRole
            )
        },
        filterStatus: function () {
            this.$refs.organisation_requests_datatable.vmDataTable.draw()
            sessionStorage.setItem(
                'filterStatus',
                this.filterStatus
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
        filterApplied: function () {
            if (
                this.filterOrganisation === '' &&
                this.filterRole.toLowerCase() === '' &&
                this.filterStatus.toLowerCase() === ''
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
        dtHeaders: function () {
            return [
                'Number',
                'Organisation',
                'Applicant',
                'Role',
                'Status',
                'Lodged On',
                'Assigned To',
                'Action',
            ]
        },
        idColumn: function () {
            return {
                data: 'id',
                orderable: true,
                searchable: true,
                visible: true,
                render: function (row, type, full) {
                    return full.holder
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
        OrganisationNameColumn: function () {
            return {
                data: 'ledger_organisation_name',
                orderable: true,
                searchable: true,
                visible: true,
                render: function (row, type, full) {
                    return full.ledger_organisation_name
                },
            }
        },
        applicantColumn: function () {
            return {
                data: 'requester_name',
                orderable: true,
                searchable: true,
                visible: true,
                render: function (row, type, full) {
                    return full.requester_name
                },
            }
        },
        roleColumn: function () {
            return {
                data: 'role',
                orderable: true,
                searchable: true,
                visible: true,
                render: function (row, type, full) {
                    return full.role
                },
            }
        },
        statusColumn: function () {
            return {
                data: 'status',
                orderable: true,
                searchable: true,
                visible: true,
                render: function (row, type, full) {
                    return full.status
                },
            }
        },
        lodgedOnColumn: function () {
            return {
                data: 'lodgement_date',
                orderable: true,
                searchable: true,
                visible: true,
                render: function (row, type, full) {
                    return full.lodgement_date
                },
            }
        },
        assignedToColumn: function () {
            return {
                data: 'assigned_officer_name',
                orderable: true,
                searchable: true,
                visible: true,
                render: function (row, type, full) {
                    if (!full.assigned_officer) {
                        return 'Unassigned'
                    }
                    return full.assigned_officer_name
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
                    let label = ''
                    // If the processing status is approved or declined, then show the view link
                    // Otherwise show a process link and check another system for what is supposed to happen upon processing

                    if ('With Assessor' == full.status) {
                        label += 'Process'
                    } else {
                        label += 'View'
                    }
                    return `<a href='/internal/organisations/access/${full.id}'>${label}</a>`
                },
            }
        },
        applicableColumns: function () {
            return [
                this.lodgementNumberColumn,
                this.OrganisationNameColumn,
                this.applicantColumn,
                this.roleColumn,
                this.statusColumn,
                this.lodgedOnColumn,
                this.assignedToColumn,
                this.actionColumn,
            ]

        },
        dtOptions: function () {
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
                searching: false,
                autoWidth: false,
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML,
                },
                responsive: true,
                serverSide: true,
                ajax: {
                    url:
                        api_endpoints.organisation_requests_paginated +
                        '?format=datatables',
                    dataSrc: 'data',

                    // adding extra GET params for Custom filtering
                    data: function (d) {
                        // Add filters selected
                        d.filter_organisation = vm.filterOrganisation
                        d.filter_role = vm.filterRole
                        d.filter_status = vm.filterStatus
                    },
                },
                order: [[0, 'desc']],
                dom:
                    "<'d-flex align-items-center'<'me-auto'l>fB>" +
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
        fetchOrganisations: function () {
            let vm = this
            fetch(api_endpoints.organisations + 'key-value-list/')
                .then(async (response) => {
                    const data = await response.json()
                    if (!response.ok) {
                        const error =
                            (data && data.message) || response.statusText
                        console.log(error)
                        return Promise.reject(error)
                    }
                    vm.organisations = data
                    console.log(vm.members)
                })
                .catch((error) => {
                    this.errorMessage = constants.ERRORS.API_ERROR
                    console.error('There was an error!', error)
                })
        },
        collapsible_component_mounted: function () {
            this.$refs.collapsible_filters.showWarningIcon(this.filterApplied)
        },
        expandCollapseFilters: function () {
            this.filters_expanded = !this.filters_expanded
        },
    },
    created: function () {
        this.fetchOrganisations();
    },
}
</script>
