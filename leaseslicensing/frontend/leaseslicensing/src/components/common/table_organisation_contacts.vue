<template>
    <div>
        <CollapsibleComponent
            ref="collapsible_filters"
            component-title="Filters"
            class="mb-2"
            @created="collapsible_component_mounted"
        >
            <div class="row mt-1 p-2">
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Role</label>
                        <select v-model="filterRole" class="form-control">
                            <option value="">All</option>
                            <option value="consultant">Consultant</option>
                            <option value="organisation_user">Employee</option>
                            <option value="organisation_admin">Admin</option>
                        </select>
                    </div>
                </div>
            </div>
        </CollapsibleComponent>

        <div class="row">
            <div class="col-lg-12">
                <datatable
                    :id="datatable_id"
                    ref="organisation_contacts_datatable"
                    :dt-options="dtOptions"
                    :dt-headers="dtHeaders"
                />
            </div>
        </div>
    </div>
</template>

<script>
import { v4 as uuid } from 'uuid';
import datatable from '@/utils/vue/datatable.vue';
import { api_endpoints, constants } from '@/utils/hooks';

export default {
    name: 'TableOrganisationContacts',
    components: {
        datatable,
    },
    props: {
        level: {
            type: String,
            required: true,
            validator: function (val) {
                let options = ['internal', 'referral', 'external'];
                return options.indexOf(val) != -1 ? true : false;
            },
        },
        /**
         * The organisation for which to display contacts
         */
        organisationId: {
            type: Number,
            required: true,
        },
    },
    data() {
        return {
            datatable_id: 'organisation-contacts-datatable-' + uuid(),
            // selected values for filtering
            filterRole: sessionStorage.getItem('filterRole')
                ? sessionStorage.getItem('filterRole')
                : '',
            // Filters toggle
            filters_expanded: false,
        };
    },
    computed: {
        filterApplied: function () {
            if (this.filterRole.toLowerCase() === '') {
                return false;
            } else {
                return true;
            }
        },
        is_external: function () {
            return this.level == 'external';
        },
        is_internal: function () {
            return this.level == 'internal';
        },
        dtHeaders: function () {
            return [
                'Number',
                'Name',
                'Role',
                'Phone',
                'Mobile',
                'Fax',
                'Email',
            ];
        },
        idColumn: function () {
            return {
                data: 'id',
                orderable: true,
                searchable: false,
                visible: false,
                render: function (row, type, full) {
                    return full.id;
                },
            };
        },
        nameColumn: function () {
            return {
                data: 'full_name',
                orderable: true,
                searchable: false,
                visible: true,
                render: function (row, type, full) {
                    return full.full_name;
                },
                name: 'first_name, last_name',
            };
        },
        roleColumn: function () {
            return {
                data: 'user_role',
                orderable: true,
                searchable: true,
                visible: true,
                render: function (row, type, full) {
                    return full.user_role;
                },
            };
        },
        phoneColumn: function () {
            return {
                data: 'phone_number',
                orderable: false,
                searchable: false,
                visible: true,
                render: function (row, type, full) {
                    return full.phone_number;
                },
            };
        },
        mobileColumn: function () {
            return {
                data: 'mobile_number',
                orderable: false,
                searchable: false,
                visible: true,
                render: function (row, type, full) {
                    return full.mobile_number;
                },
            };
        },
        faxColumn: function () {
            return {
                data: 'fax_number',
                orderable: false,
                searchable: false,
                visible: true,
                render: function (row, type, full) {
                    return full.fax_number;
                },
            };
        },
        emailColumn: function () {
            return {
                data: 'email',
                orderable: true,
                searchable: false,
                visible: true,
                render: function (row, type, full) {
                    return full.email;
                },
            };
        },
        applicableColumns: function () {
            return [
                this.idColumn,
                this.nameColumn,
                this.roleColumn,
                this.phoneColumn,
                this.mobileColumn,
                this.faxColumn,
                this.emailColumn,
            ];
        },
        dtOptions: function () {
            let vm = this;
            let buttons = [];
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
                ];
            }

            return {
                searching: true,
                autoWidth: false,
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML,
                },
                responsive: true,
                serverSide: true,
                ajax: {
                    url:
                        api_endpoints.organisation_contacts_paginated +
                        '?format=datatables',
                    dataSrc: 'data',

                    // adding extra GET params for Custom filtering
                    data: function (d) {
                        // Add filters selected
                        d.filter_role = vm.filterRole;
                        // Add search terms to be concatenated on the queryset
                        d.search_terms = 'first_name, last_name, email';
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
                    console.log('in initComplete');
                },
            };
        },
    },
    watch: {
        filterRole: function () {
            this.$refs.organisation_contacts_datatable.vmDataTable.draw();
            sessionStorage.setItem('filterRole', this.filterRole);
        },
        filterApplied: function () {
            if (this.$refs.collapsible_filters) {
                // Collapsible component exists
                this.$refs.collapsible_filters.showWarningIcon(
                    this.filterApplied
                );
            }
        },
    },
    created: function () {},
    methods: {
        collapsible_component_mounted: function () {
            this.$refs.collapsible_filters.showWarningIcon(this.filterApplied);
        },
        expandCollapseFilters: function () {
            this.filters_expanded = !this.filters_expanded;
        },
    },
};
</script>
