<template>
    <div>
        <CollapsibleFilters
            ref="collapsible_filters"
            component_title="Filters"
            class="mb-2"
            @created="collapsible_component_mounted"
        >
            <div class="row mt-1 p-2">
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Type</label>
                        <select
                            v-model="filterApplicationType"
                            class="form-control"
                        >
                            <option value="all">All</option>
                            <option
                                v-for="application_type in application_types"
                                :key="application_type.id"
                                :value="application_type.id"
                            >
                                {{ application_type.name_display }}
                            </option>
                        </select>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Status</label>
                        <select
                            v-model="filterApplicationStatus"
                            class="form-control"
                        >
                            <option value="all">All</option>
                            <option
                                v-for="status in application_statuses"
                                :key="status.code"
                                :value="status.code"
                            >
                                {{ status.description }}
                            </option>
                        </select>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for=""
                            >Lodged From {{ filterProposalLodgedFrom }}</label
                        >
                        <div
                            ref="proposalDateFromPicker"
                            class="input-group date"
                        >
                            <input
                                v-model="filterProposalLodgedFrom"
                                type="date"
                                class="form-control"
                            />
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for=""
                            >Lodged To {{ filterProposalLodgedTo }}</label
                        >
                        <div
                            ref="proposalDateToPicker"
                            class="input-group date"
                        >
                            <input
                                v-model="filterProposalLodgedTo"
                                type="date"
                                class="form-control"
                            />
                        </div>
                    </div>
                </div>
            </div>
        </CollapsibleFilters>

        <div v-if="is_external && !email_user_id_assigned" class="row">
            <div class="col-md-12">
                <div class="text-end">
                    <button
                        type="button"
                        class="btn btn-primary mb-2"
                        @click="new_application_button_clicked"
                    >
                        <i class="fa-solid fa-circle-plus"></i> New Application
                    </button>
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-lg-12">
                <datatable
                    :id="datatable_id"
                    ref="application_datatable"
                    :dt-options="dtOptions"
                    :dt-headers="dtHeaders"
                />
            </div>
        </div>
    </div>
</template>

<script>
import datatable from '@/utils/vue/datatable.vue';
import { v4 as uuid } from 'uuid';
import { api_endpoints, constants } from '@/utils/hooks';
import CollapsibleFilters from '@/components/forms/collapsible_component.vue';
import { expandToggle } from '@/components/common/table_functions.js';
import { discardProposal } from '@/components/common/workflow_functions.js';

export default {
    name: 'TableApplications',
    components: {
        datatable,
        CollapsibleFilters,
    },
    props: {
        level: {
            type: String,
            required: true,
            validator: function (val) {
                let options = [
                    'internal',
                    'referral',
                    'external',
                    'organisation_view',
                ];
                return options.indexOf(val) != -1 ? true : false;
            },
        },
        email_user_id_assigned: {
            type: Number,
            required: false,
            default: 0,
        },
        target_organisation_id: {
            type: Number,
            required: false,
            default: 0,
        },
        targetEmailUserId: {
            type: Number,
            required: false,
            default: 0,
        },
        filterApplicationType_cache_name: {
            type: String,
            required: false,
            default: 'filterApplicationType',
        },
        filterApplicationStatus_cache_name: {
            type: String,
            required: false,
            default: 'filterApplicationStatus',
        },
        filterProposalLodgedFrom_cache_name: {
            type: String,
            required: false,
            default: 'filterApplicationLodgedFrom',
        },
        filterProposalLodgedTo_cache_name: {
            type: String,
            required: false,
            default: 'filterApplicationLodgedTo',
        },
    },
    emits: ['filter-appied'],
    data() {
        let vm = this;
        return {
            datatable_id: 'applications-datatable-' + uuid(),

            // selected values for filtering
            filterApplicationType: sessionStorage.getItem(
                vm.filterApplicationType_cache_name
            )
                ? sessionStorage.getItem(vm.filterApplicationType_cache_name)
                : 'all',
            filterApplicationStatus: sessionStorage.getItem(
                vm.filterApplicationStatus_cache_name
            )
                ? sessionStorage.getItem(vm.filterApplicationStatus_cache_name)
                : 'all',
            filterProposalLodgedFrom: sessionStorage.getItem(
                vm.filterProposalLodgedFrom_cache_name
            )
                ? sessionStorage.getItem(vm.filterProposalLodgedFrom_cache_name)
                : '',
            filterProposalLodgedTo: sessionStorage.getItem(
                vm.filterProposalLodgedTo_cache_name
            )
                ? sessionStorage.getItem(vm.filterProposalLodgedTo_cache_name)
                : '',

            // filtering options
            application_types: [],
            application_statuses: [],

            dateFormat: 'DD/MM/YYYY',
            datepickerOptions: {
                format: 'DD/MM/YYYY',
                showClear: true,
                useCurrent: false,
                keepInvalid: true,
                allowInputToggle: true,
            },

            // For Expandable row
            td_expand_class_name: 'expand-icon',
            td_collapse_class_name: 'collapse-icon',
            expandable_row_class_name: 'expandable_row_class_name',
        };
    },
    computed: {
        number_of_columns: function () {
            let num = this.$refs.application_datatable.vmDataTable
                .columns(':visible')
                .nodes().length;
            return num;
        },
        filterApplied: function () {
            let filter_applied = true;
            if (
                this.filterApplicationStatus === 'all' &&
                this.filterApplicationType === 'all' &&
                this.filterProposalLodgedFrom === '' &&
                this.filterProposalLodgedTo === ''
            ) {
                filter_applied = false;
            }
            return filter_applied;
        },
        debug: function () {
            if (this.$route.query.debug) {
                return this.$route.query.debug === 'true';
            }
            return false;
        },
        is_external: function () {
            return this.level == 'external';
        },
        is_internal: function () {
            return this.level == 'internal';
        },
        is_organisation_view: function () {
            return this.level == 'organisation_view';
        },
        dtHeaders: function () {
            if (this.is_organisation_view) {
                return [
                    'id',
                    'Number',
                    'Type',
                    'Status',
                    'Lodged On',
                    'Action',
                ];
            }
            if (this.is_external) {
                return [
                    'id',
                    'Number',
                    'Type',
                    'Submitter',
                    'Applicant',
                    'Status',
                    'Lodged On',
                    'Action',
                ];
            }
            if (this.is_internal) {
                return [
                    'id',
                    'Number',
                    'Type',
                    'Submitter',
                    'Applicant',
                    'Status',
                    'Lodged On',
                    'Assigned Officer',
                    'Action',
                ];
            }
            // Default
            return [];
        },
        column_id: function () {
            let vm = this;
            return {
                // 1. ID
                data: 'id',
                orderable: false,
                searchable: false,
                visible: false,
                render: function (row, type, full) {
                    if (vm.debug) {
                        console.log(full);
                    }
                    return full.id;
                },
            };
        },
        column_lodgement_number: function () {
            return {
                // 2. Lodgement Number
                data: 'id',
                orderable: true,
                searchable: true,
                visible: true,
                render: function (row, type, full) {
                    if (full.migrated) {
                        return full.lodgement_number + ' (M)';
                    } else {
                        return full.lodgement_number;
                    }
                },
                name: 'lodgement_number',
            };
        },
        column_type: function () {
            return {
                // 3. Type (This corresponds to the 'ApplicationType' at the backend)
                data: 'id',
                orderable: true,
                searchable: true,
                visible: true,
                render: function (row, type, full) {
                    return full.application_type.name_display;
                },
                name: 'application_type_id__name',
            };
        },
        column_submitter: function () {
            return {
                data: 'id',
                orderable: true,
                searchable: true,
                visible: true,
                render: function (row, type, full) {
                    if (full.submitter) {
                        return full.submitter.fullname;
                    } else {
                        return '';
                    }
                },
                name: 'submitter__first_name, submitter__last_name',
            };
        },
        column_applicant: function () {
            return {
                data: 'id',
                orderable: true,
                searchable: true,
                visible: true,
                render: function (row, type, full) {
                    if (full.applicant_name) {
                        return `${full.applicant_name}`;
                    }
                    return '';
                },
                name: 'proposalapplicant__first_name, proposalapplicant__last_name',
            };
        },
        column_status: function () {
            let vm = this;
            return {
                // 5. Status
                data: 'id',
                orderable: true,
                searchable: true,
                visible: true,
                render: function (row, type, full) {
                    if (vm.is_internal) {
                        return full.processing_status;
                    }
                    return full.customer_status;
                },
                name: 'processing_status',
            };
        },
        column_lodged_on: function () {
            return {
                // 6. Lodged
                data: 'id',
                orderable: true,
                searchable: false,
                visible: true,
                render: function (row, type, full) {
                    if (full.lodgement_date) {
                        return moment(full.lodgement_date).format('DD/MM/YYYY');
                    }
                    return '';
                },
                name: 'lodgement_date',
            };
        },
        column_assigned_officer: function () {
            return {
                data: 'id',
                orderable: true,
                searchable: true,
                visible: true,
                render: function (row, type, full) {
                    if (full.assigned_officer) {
                        return full.assigned_officer.fullname;
                    } else {
                        return '';
                    }
                },
                name: 'assigned_officer__first_name, assigned_officer__last_name, assigned_approver__first_name, assigned_approver__last_name',
            };
        },
        column_action: function () {
            let vm = this;
            return {
                // 8. Action
                data: 'id',
                orderable: false,
                searchable: false,
                visible: true,
                render: function (row, type, full) {
                    let links = '';
                    if (vm.is_internal) {
                        if (full.accessing_user_can_process) {
                            links += `<a href='/internal/proposal/${full.id}'>Process</a><br/>`;
                        } else if (full.can_edit_invoicing_details) {
                            links += `<a href='/internal/proposal/${full.id}'>Edit Invoicing</a><br/>`;
                        } else {
                            links += `<a href='/internal/proposal/${full.id}'>View</a><br/>`;
                        }
                    }
                    if (vm.is_external) {
                        if (full.can_user_edit) {
                            links += `<a href='/external/proposal/${full.id}'>Continue</a><br/>`;
                            links += `<a href='#${full.id}' data-discard-proposal='${full.id}'>Discard</a><br/>`;
                        } else if (full.can_user_view) {
                            if (vm.email_user_id_assigned) {
                                links += `<a href="/external/proposal/${full.id}/referral/">Complete Referral</a><br/>`;
                            } else {
                                links += `<a href='/external/proposal/${full.id}'>View</a><br/>`;
                            }
                        }
                    }
                    return links;
                },
            };
        },
        dtOptions: function () {
            let vm = this;

            let columns = [];
            let search = null;
            let buttons = [
                {
                    extend: 'excel',
                    text: '<i class="fa-solid fa-download"></i> Excel',
                    className: 'btn btn-primary rounded me-2',
                    exportOptions: {
                        columns: ':visible',
                    },
                },
                {
                    extend: 'csv',
                    text: '<i class="fa-solid fa-download"></i> CSV',
                    className: 'btn btn-primary rounded',
                    exportOptions: {
                        columns: ':visible',
                    },
                },
            ];
            if (this.is_organisation_view) {
                columns = [
                    vm.column_id,
                    vm.column_lodgement_number,
                    vm.column_type,
                    vm.column_status,
                    vm.column_lodged_on,
                    vm.column_action,
                ];
                search = true;
            }

            if (vm.is_external) {
                columns = [
                    vm.column_id,
                    vm.column_lodgement_number,
                    vm.column_type,
                    vm.column_submitter,
                    vm.column_applicant,
                    vm.column_status,
                    vm.column_lodged_on,
                    //vm.column_assigned_officer,
                    vm.column_action,
                ];
                search = false;
            }
            if (vm.is_internal) {
                columns = [
                    vm.column_id,
                    vm.column_lodgement_number,
                    vm.column_type,
                    vm.column_submitter,
                    vm.column_applicant,
                    vm.column_status,
                    vm.column_lodged_on,
                    vm.column_assigned_officer,
                    vm.column_action,
                ];
                // eslint-disable-next-line no-unused-vars
                search = true;
            }

            return {
                autoWidth: false,
                responsive: true,
                serverSide: true,
                searching: true,
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML,
                },
                rowCallback: function (row, proposal) {
                    let row_jq = $(row);
                    row_jq.attr('id', 'proposal_id_' + proposal.id);
                    row_jq.children().first().addClass(vm.td_expand_class_name);
                },
                ajax: {
                    url:
                        api_endpoints.proposals_paginated_list +
                        '?format=datatables&email_user_id_assigned=' +
                        vm.email_user_id_assigned +
                        '&target_email_user_id=' +
                        vm.targetEmailUserId +
                        '&target_organisation_id=' +
                        vm.target_organisation_id,
                    dataSrc: 'data',

                    // adding extra GET params for Custom filtering
                    data: function (d) {
                        d.filter_application_type = vm.filterApplicationType;
                        d.filter_application_status =
                            vm.filterApplicationStatus;
                        d.filter_lodged_from = vm.filterProposalLodgedFrom;
                        d.filter_lodged_to = vm.filterProposalLodgedTo;
                        d.level = vm.level;

                        // Add search terms to be concatenated on the queryset
                        d.search_terms =
                            'proposalapplicant__first_name, proposalapplicant__last_name';
                    },
                },
                dom:
                    "<'d-flex align-items-center'<'me-auto'l>fB>" +
                    "<'row'<'col-sm-12'tr>>" +
                    "<'d-flex align-items-center'<'me-auto'i>p>",
                buttons: buttons,
                order: [[1, 'desc']],
                columns: columns,
                processing: true,
                initComplete: function () {},
            };
        },
    },
    watch: {
        filterApplicationType: function () {
            this.$refs.application_datatable.vmDataTable.draw(); // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem(
                this.filterApplicationType_cache_name,
                this.filterApplicationType
            );
            this.$emit('filter-appied');
        },
        filterApplicationStatus: function () {
            this.$refs.application_datatable.vmDataTable.draw(); // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem(
                this.filterApplicationStatus_cache_name,
                this.filterApplicationStatus
            );
            this.$emit('filter-appied');
        },
        filterProposalLodgedFrom: function () {
            this.$refs.application_datatable.vmDataTable.draw(); // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem(
                this.filterProposalLodgedFrom_cache_name,
                this.filterProposalLodgedFrom
            );
            this.$emit('filter-appied');
        },
        filterProposalLodgedTo: function () {
            this.$refs.application_datatable.vmDataTable.draw(); // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem(
                this.filterProposalLodgedTo_cache_name,
                this.filterProposalLodgedTo
            );
            this.$emit('filter-appied');
        },
        filterApplied: function () {
            if (this.$refs.collapsible_filters) {
                // Collapsible component exists
                this.$refs.collapsible_filters.show_warning_icon(
                    this.filterApplied
                );
            }
        },
    },
    created: function () {
        this.fetchFilterLists();
    },
    mounted: function () {
        let vm = this;
        this.$nextTick(() => {
            vm.addEventListeners();
        });
    },
    methods: {
        updateFilters: function () {
            this.$nextTick(() => {
                this.filterApplicationType = sessionStorage.getItem(
                    this.filterApplicationType_cache_name
                )
                    ? sessionStorage.getItem(
                          this.filterApplicationType_cache_name
                      )
                    : 'all';
                this.filterApplicationStatus = sessionStorage.getItem(
                    this.filterApplicationStatus_cache_name
                )
                    ? sessionStorage.getItem(
                          this.filterApplicationStatus_cache_name
                      )
                    : 'all';
                this.filterProposalLodgedFrom = sessionStorage.getItem(
                    this.filterProposalLodgedFrom_cache_name
                )
                    ? sessionStorage.getItem(
                          this.filterProposalLodgedFrom_cache_name
                      )
                    : '';
                this.filterProposalLodgedTo = sessionStorage.getItem(
                    this.filterProposalLodgedTo_cache_name
                )
                    ? sessionStorage.getItem(
                          this.filterProposalLodgedTo_cache_name
                      )
                    : '';
                this.$refs.application_datatable.vmDataTable.draw();
            });
        },
        adjust_table_width: function () {
            this.$refs.application_datatable.vmDataTable.columns.adjust();
            this.$refs.application_datatable.vmDataTable.responsive.recalc();
        },
        collapsible_component_mounted: function () {
            this.$refs.collapsible_filters.show_warning_icon(
                this.filterApplied
            );
        },
        //getActionDetailTable: function(sticker){
        //    let thead = `<thead>
        //                    <tr>
        //                        <th scope="col">Date</th>
        //                        <th scope="col">User</th>
        //                        <th scope="col">Action</th>
        //                        <th scope="col">Date of Lost</th>
        //                        <th scope="col">Date of Returned</th>
        //                        <th scope="col">Reason</th>
        //                    </tr>
        //                <thead>`
        //    let tbody = ''
        //    for (let detail of sticker.sticker_action_details){
        //        tbody += `<tr>
        //            <td>${moment(detail.date_updated).format('DD/MM/YYYY')}</td>
        //            <td>${detail.user_detail ? detail.user_detail.first_name : ''} ${detail.user_detail ? detail.user_detail.last_name : ''} </td>
        //            <td>${detail.action ? detail.action : ''}</td>
        //            <td>${detail.date_of_lost_sticker ? moment(detail.date_of_lost_sticker, 'YYYY-MM-DD').format('DD/MM/YYYY') : ''}</td>
        //            <td>${detail.date_of_returned_sticker ? moment(detail.date_of_returned_sticker, 'YYYY-MM-DD').format('DD/MM/YYYY') : ''}</td>
        //            <td>${detail.reason}</td>
        //        </tr>`
        //    }
        //    tbody = '<tbody>' + tbody + '</tbody>'

        //    let details = '<table class="table table-striped table-bordered table-sm table-sticker-details" id="table-sticker-details-' + sticker.id + '">' + thead + tbody + '</table>'
        //    return details
        //},
        new_application_button_clicked: async function () {
            //await this.$router.isReady()
            console.log(this.$router);
            await this.$router.push({
                name: 'apply_proposal',
            });
            console.log(' new application');
        },
        discardProposal: function (proposal_id) {
            discardProposal(proposal_id)
                .then(() => {
                    this.$refs.application_datatable.vmDataTable.draw();
                })
                .catch((error) => {
                    console.log(error);
                });
        },
        fetchFilterLists: async function () {
            let vm = this;

            // Application Types
            fetch(api_endpoints.application_types + 'key-value-list/').then(
                async (response) => {
                    const resData = await response.json();
                    vm.application_types = resData;
                },
                () => {}
            );

            // Application Statuses
            const res = await fetch(api_endpoints.application_statuses_dict);
            const data = await res.json();
            if (vm.is_internal) {
                vm.application_statuses = data.internal_statuses;
            } else {
                vm.application_statuses = data.external_statuses;
            }
        },
        addEventListeners: function () {
            let vm = this;
            vm.$refs.application_datatable.vmDataTable.on(
                'click',
                'a[data-discard-proposal]',
                function (e) {
                    e.preventDefault();
                    let id = $(this).attr('data-discard-proposal');
                    vm.discardProposal(id);
                }
            );

            // Listener for thr row
            vm.$refs.application_datatable.vmDataTable.on(
                'click',
                'td',
                function () {
                    expandToggle(vm, this);
                }
            );
        },
    },
};
</script>
