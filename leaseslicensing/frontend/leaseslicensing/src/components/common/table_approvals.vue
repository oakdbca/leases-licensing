<template>
    <div>
        <CollapsibleFilters component_title="Filters" ref="collapsible_filters" @created="collapsible_component_mounted"
            class="mb-2">
            <div class="row mb-2">
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Type</label>
                        <select class="form-control" v-model="filterApprovalType">
                            <option value="all">All</option>
                            <option v-for="ap in approvalTypes" :value="ap.id">{{ ap.name_display }}</option>
                        </select>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Status</label>
                        <select class="form-control" v-model="filterApprovalStatus">
                            <option value="all">All</option>
                            <option v-for="status in approval_statuses" :value="status.code">{{ status.description }}
                            </option>
                        </select>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Expiry Date From</label>
                        <div class="input-group date" ref="approvalDateFromPicker">
                            <input type="date" class="form-control" v-model="filterApprovalExpiryDateFrom">
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Expiry Date To</label>
                        <div class="input-group date" ref="approvalDateToPicker">
                            <input type="date" class="form-control" v-model="filterApprovalExpiryDateTo">
                        </div>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="filter-region">Organisation</label>
                        <select id="filter-region" class="form-control" v-model="filterApprovalOrganisation">
                            <option value="all">All</option>
                            <option v-for="organisation in organisations" :value="organisation.id">{{
                                organisation.ledger_organisation_name }}
                            </option>
                        </select>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="filter-region">Region</label>
                        <select id="filter-region" class="form-control" v-model="filterApprovalRegion">
                            <option value="all">All</option>
                            <option v-for="region in regions" :value="region.id">{{ region.name }}
                            </option>
                        </select>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="filter-district">District</label>
                        <select id=" filter-district" class="form-control" v-model="filterApprovalDistrict">
                            <option value="all">All</option>
                            <option v-for="district in districts" :value="district.id">{{ district.name }}
                            </option>
                        </select>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="filter-group">Group</label>
                        <select id="filter-group" class="form-control" v-model="filterApprovalGroup">
                            <option value="all">All</option>
                            <option v-for="group in groups" :value="group.id">{{ group.name }}
                            </option>
                        </select>
                    </div>
                </div>
            </div>
        </CollapsibleFilters>

        <div class="row">
            <div class="col-lg-12">
                <datatable ref="approvals_datatable" :id="datatable_id" :dtOptions="datatable_options"
                    :dtHeaders="datatable_headers" />
            </div>
        </div>
        <ApprovalCancellation ref="approval_cancellation" :approval_id="selectedApprovalId"
            :approval_lodgement_number="selectedApprovalLodgementNumber"
            @refreshFromResponse="refreshFromResponseApprovalModify">
        </ApprovalCancellation>
        <ApprovalSurrender ref="approval_surrender" :approval_id="selectedApprovalId"
            :approval_lodgement_number="selectedApprovalLodgementNumber"
            @refreshFromResponse="refreshFromResponseApprovalModify">
        </ApprovalSurrender>
        <ApprovalSuspension ref="approval_suspension" :approval_id="selectedApprovalId"
            :approval_lodgement_number="selectedApprovalLodgementNumber"
            @refreshFromResponse="refreshFromResponseApprovalModify">
        </ApprovalSuspension>
        <div v-if="approvalHistoryId">
            <ApprovalHistory ref="approval_history" :key="approvalHistoryId" :approvalId="approvalHistoryId"
                :approvalLodgementNumber="selectedApprovalLodgementNumber" />
        </div>
    </div>
</template>

<script>
import datatable from '@/utils/vue/datatable.vue'
import ApprovalCancellation from '../internal/approvals/approval_cancellation.vue'
import ApprovalSuspension from '../internal/approvals/approval_suspension.vue'
import ApprovalSurrender from '../internal/approvals/approval_surrender.vue'
import ApprovalHistory from '../internal/approvals/approval_history.vue'
import { api_endpoints, constants, helpers } from '@/utils/hooks'
import CollapsibleFilters from '@/components/forms/collapsible_component.vue'
import { v4 as uuid } from 'uuid';
import Swal from 'sweetalert2'

export default {
    name: 'TableApprovals',
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
        target_compliance_id: {
            type: Number,
            required: false,
            default: 0,
        },
    },
    data() {
        let vm = this;
        return {
            datatable_id: 'approvals-datatable-' + uuid(),
            show_expired_surrendered: false,
            selectedWaitingListAllocationId: null,
            approvalHistoryId: null,
            uuid: 0,
            mooringBayId: null,
            statusValues: [],
            filterApprovalType: null,
            approvalTypes: [],
            holderList: [],
            organisations: [],
            regions: [],
            districts: [],
            groups: [],
            profile: {},
            selectedApprovalId: null,
            selectedApprovalLodgementNumber: null,

            // selected values for filtering
            filterApprovalType: sessionStorage.getItem('filterApprovalType') ? sessionStorage.getItem('filterApprovalType') : 'all',
            filterApprovalStatus: sessionStorage.getItem('filterApprovalStatus') ? sessionStorage.getItem('filterApprovalStatus') : 'all',
            filterApprovalExpiryDateFrom: sessionStorage.getItem('filterApprovalExpiryDateFrom') ? sessionStorage.getItem('filterApprovalExpiryDateFrom') : '',
            filterApprovalExpiryDateTo: sessionStorage.getItem('filterApprovalExpiryDateTo') ? sessionStorage.getItem('filterApprovalExpiryDateTo') : '',

            filterApprovalOrganisation: sessionStorage.getItem('filterApprovalOrganisation') ? sessionStorage.getItem('filterApprovalOrganisation') : 'all',
            filterApprovalRegion: sessionStorage.getItem('filterApprovalRegion') ? sessionStorage.getItem('filterApprovalRegion') : 'all',
            filterApprovalDistrict: sessionStorage.getItem('filterApprovalDistrict') ? sessionStorage.getItem('filterApprovalDistrict') : 'all',
            filterApprovalGroup: sessionStorage.getItem('filterApprovalGroup') ? sessionStorage.getItem('filterApprovalGroup') : 'all',


            // filtering options
            approval_types: [],
            approval_statuses: [],

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

            // For Expandable row
            td_expand_class_name: 'expand-icon',
            td_collapse_class_name: 'collapse-icon',
            expandable_row_class_name: 'expandable_row_class_name',
        }
    },
    components: {
        datatable,
        ApprovalCancellation,
        ApprovalSuspension,
        ApprovalSurrender,
        ApprovalHistory,
        CollapsibleFilters,
    },
    watch: {
        show_expired_surrendered: function (value) {
            console.log(value)
            this.$refs.approvals_datatable.vmDataTable.ajax.reload()
        },
        filterApprovalType: function () {
            this.$refs.approvals_datatable.vmDataTable.draw();
            sessionStorage.setItem('filterApprovalType', this.filterApprovalType);
        },
        filterApprovalStatus: function () {
            this.$refs.approvals_datatable.vmDataTable.draw();
            sessionStorage.setItem('filterApprovalStatus', this.filterApprovalStatus);
        },
        filterApprovalExpiryDateFrom: function () {
            this.$refs.approvals_datatable.vmDataTable.draw();
            sessionStorage.setItem('filterApprovalExpiryDateFrom', this.filterApprovalExpiryDateFrom);
        },
        filterApprovalExpiryDateTo: function () {
            this.$refs.approvals_datatable.vmDataTable.draw();
            sessionStorage.setItem('filterApprovalExpiryDateTo', this.filterApprovalExpiryDateTo);
        },
        filterApprovalOrganisation: function () {
            this.$refs.approvals_datatable.vmDataTable.draw();
            sessionStorage.setItem('filterApprovalOrganisation', this.filterApprovalOrganisation);
        },
        filterApprovalRegion: function () {
            this.$refs.approvals_datatable.vmDataTable.draw();
            sessionStorage.setItem('filterApprovalRegion', this.filterApprovalRegion);
        },
        filterApprovalDistrict: function () {
            this.$refs.approvals_datatable.vmDataTable.draw();
            sessionStorage.setItem('filterApprovalDistrict', this.filterApprovalDistrict);
        },
        filterApprovalGroup: function () {
            this.$refs.approvals_datatable.vmDataTable.draw();
            sessionStorage.setItem('filterApprovalGroup', this.filterApprovalGroup);
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
            let filter_applied = true
            if (this.filterApprovalType === 'all' &&
                this.filterApprovalStatus.toLowerCase() === 'all' &&
                this.filterApprovalExpiryDateFrom.toLowerCase() === '' &&
                this.filterApprovalExpiryDateTo.toLowerCase() === '' &&
                this.filterApprovalOrganisation === 'all' &&
                this.filterApprovalRegion === 'all' &&
                this.filterApprovalDistrict === 'all' &&
                this.filterApprovalGroup === 'all'
            ) {
                filter_applied = false
            }
            return filter_applied
        },
        csrf_token: function () {
            return helpers.getCookie('csrftoken')
        },
        debug: function () {
            if (this.$route.query.debug) {
                return this.$route.query.debug === 'Tru3'
            }
            return false
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
        // Datatable settings
        datatable_headers: function () {
            if (this.is_organisation_view) {
                return [
                    'Id',
                    'Number',
                    'Type',
                    'Status',
                    'Document',
                    'Expiry Date',
                    'Action',
                ]
            } else if (this.is_external) {
                return [
                    'Id',
                    'Number',
                    'Type',
                    'Site',
                    'Holder',
                    'Status',
                    'Expiry Date',
                    'Document',
                    'Action',
                    'Original Lease/License Number',
                    'Site Name',
                    'Groups',
                    'Categories',
                ]
            } else if (this.is_internal) {
                return [
                    'Id',
                    'Number',
                    'Type',
                    'Holder',
                    'Application',
                    'Status',
                    'Expiry Date',
                    'Document',
                    'Action',
                    'Original Lease/License Number',
                    'Site Name',
                    'Groups',
                    'Categories',
                ]
            }
        },
        columnId: function () {
            return {
                data: "id",
                orderable: false,
                searchable: false,
                visible: false,
                'render': function (row, type, full) {
                    console.log('---full---')
                    console.log(full)
                    return full.id
                }
            }
        },
        columnLodgementNumber: function () {
            return {
                data: "lodgement_number",
                orderable: true,
                searchable: true,
                visible: true,
                'render': function (row, type, full) {
                    if (full.migrated) {
                        return full.lodgement_number + ' (M)'
                    } else {
                        return full.lodgement_number
                    }
                }
            }
        },
        columnType: function () {
            return {
                data: "application_type",
                orderable: true,
                searchable: true,
                visible: true,
                'render': function (row, type, full) {
                    return full.application_type;
                },
            }
        },
        columnSite: function () {
            return {
                data: "site_name",
                orderable: true,
                searchable: true,
                visible: true,
                'render': function (row, type, full) {
                    // TODO Site
                    return full.site_name;
                }
            }
        },
        columnGroups: function () {
            return {
                data: "groups_names_list",
                orderable: true,
                searchable: true,
                visible: true,
                'render': function (row, type, full) {
                    let html = '';
                    if (full.groups_names_list) {
                        for (let i = 0; i < full.groups_names_list.length; i++) {
                            html += `<span class="badge bg-primary">${full.groups_names_list[i]}</span>&nbsp;`;
                        }
                    }
                    return html
                }
            }
        },
        columnCategories: function () {
            return {
                data: "categories_list",
                orderable: true,
                searchable: true,
                visible: true,
                'render': function (row, type, full) {
                    let html = '';
                    if (full.categories_list) {
                        for (let i = 0; i < full.categories_list.length; i++) {
                            html += `<span class="badge bg-primary">${full.categories_list[i]}</span>&nbsp;`;
                        }
                    }
                    return html
                }
            }
        },
        columnHolder: function () {
            return {
                data: "holder",
                orderable: true,
                searchable: true,
                visible: true,
                'render': function (row, type, full) {
                    return full.holder;
                },
            }
        },
        columnLinkedApplications: function () {
            return {
                data: "id",
                orderable: true,
                searchable: true,
                visible: true,
                'render': function (row, type, full) {
                    return full.linked_applications.join(', ');
                },
            }
        },
        columnStatus: function () {
            return {
                data: "status",
                orderable: true,
                searchable: true,
                visible: true,
                'render': function (row, type, full) {
                    return full.status
                }
            }
        },
        columnExpiryDate: function () {
            return {
                data: "expiry_date",
                orderable: true,
                searchable: false,
                visible: true,
                'render': function (row, type, full) {
                    if (full.expiry_date) {
                        return moment(full.expiry_date).format('DD/MM/YYYY')
                    }
                    return ''
                }
            }
        },
        columnDocument: function () {
            return {
                data: "id",
                orderable: true,
                searchable: true,
                visible: true,
                'render': function (row, type, full) {
                    let _file_name = "Approval.PDF"
                    if (full.licence_document) {
                        return `<a href="${full.licence_document}" target="_blank">
                            <i class="fa fa-file-pdf" style='color: red'></i>
                            ${_file_name}</a>`
                    } else {
                        // Should not happen that there is no license document, but better not show one being
                        // there when that is not the case
                        console.warn(`No license document for license ${full.lodgement_number}`)
                        return "";
                    }
                }
            }
        },
        columnOriginalLeaseLicenseNumber: function () {
            return {
                data: "original_leaselicense_number",
                orderable: true,
                searchable: true,
                visible: true,
                'render': function (row, type, full) {
                    if (full.original_leaselicense_number) {
                        return full.original_leaselicense_number
                    }
                    return 'N/A'
                }
            }
        },
        columnAction: function () {
            let vm = this;
            return {
                // 10. Action
                data: "id",
                orderable: false,
                searchable: false,
                visible: true,
                'render': function (row, type, full) {
                    let links = '';
                    if (vm.debug) {
                        links += `<a href='#${full.id}' data-request-new-sticker='${full.id}'>Request New Sticker</a><br/>`;
                    }

                    if (vm.is_external && full.can_reissue) {
                        links += `<a href='/external/approval/${full.id}'>View</a><br/>`;
                        if (full.can_action || vm.debug) {
                            if (full.amend_or_renew === 'amend' || vm.debug) {
                                links += `<a href='#${full.id}' data-amend-approval='${full.current_proposal}'>Amend</a><br/>`;
                            } else if (full.can_renew) {
                                links += `<a href='#${full.id}' data-renew-approval='${full.current_proposal}'>Renew</a><br/>`;
                            }
                            links += `<a href='#${full.id}' data-surrender-approval='${full.id}' data-approval-lodgement-number="${full.lodgement_number}">Surrender</a><br/>`;
                        }
                    } else if (!vm.is_external) {
                        links += `<a href='/internal/approval/${full.id}'>View</a><br/>`;
                        links += `<a href='#${full.id}' data-history-approval='${full.id}' data-approval-lodgement-number="${full.lodgement_number}">History</a><br/>`;
                        if (full.is_approver && full.can_reissue && full.current_proposal) {
                            links += `<a href='#${full.id}' data-reissue-approval='${full.current_proposal}'>Reissue</a><br/>`;
                        }
                        if (vm.is_internal && vm.wlaDash) {
                            links += full.offer_link;
                        }
                        if (full.is_assessor) {
                            if (full.can_reissue && full.can_action) {
                                links += `<a href='#${full.id}' data-cancel-approval='${full.id}' data-approval-lodgement-number="${full.lodgement_number}">Cancel</a><br/>`;
                                links += `<a href='#${full.id}' data-surrender-approval='${full.id}' data-approval-lodgement-number="${full.lodgement_number}">Surrender</a><br/>`;
                            }
                            if (full.status == 'Current' && full.can_action) {
                                links += `<a href='#${full.id}' data-suspend-approval='${full.id}' data-approval-lodgement-number="${full.lodgement_number}">Suspend</a><br/>`;
                            }
                            if (full.can_reinstate) {
                                links += `<a href='#${full.id}' data-reinstate-approval='${full.id}'>Reinstate</a><br/>`;
                            }
                            // Todo: Not yet totally sure under which circumstances this action should be visible
                            if (constants.APPROVAL_STATUS.CURRENT.TEXT == full.status) {
                                links += `<a href='#${full.id}' data-review-invoice-detail-approval='${full.id}' data-approval-lodgement-number="${full.lodgement_number}">Review Invoice Details</a><br/>`;
                            }
                            if (full.status == constants.APPROVAL_STATUS.CURRENT_EDITING_INVOICING.TEXT) {
                                links += `<a href='/internal/approval/${full.id}#edit-invoicing'>Continue Editing Invoicing</a><br/>`;
                            }

                            if ('current_pending_renewal_review' == full.status) {
                                links += `<a href='#${full.id}' data-review-renewal-approval='${full.id}' data-approval-lodgement-number="${full.lodgement_number}">Review Renewal</a><br/>`;
                            }

                        }
                        if (full.renewal_document && full.renewal_notification_sent_to_holder) {
                            links += `<a href='${full.renewal_document}' target='_blank'>Renewal Notice</a><br/>`;
                        }
                    }

                    return links;
                }
            }
        },
        datatable_options: function () {
            let vm = this;
            let selectedColumns = [];
            if (this.is_organisation_view) {
                selectedColumns = [
                    vm.columnId,
                    vm.columnLodgementNumber,
                    vm.columnType,
                    vm.columnStatus,
                    vm.columnDocument,
                    vm.columnExpiryDate,
                    vm.columnAction,
                ]
            } else if (this.is_external) {
                selectedColumns = [
                    vm.columnId,
                    vm.columnLodgementNumber,
                    vm.columnType,
                    vm.columnSite,
                    vm.columnHolder,
                    vm.columnStatus,
                    vm.columnExpiryDate,
                    vm.columnDocument,
                    vm.columnAction,
                    vm.columnOriginalLeaseLicenseNumber,
                    vm.columnSite,
                    vm.columnGroups,
                    vm.columnCategories,
                ]
            } else if (vm.is_internal) {
                selectedColumns = [
                    vm.columnId,
                    vm.columnLodgementNumber,
                    vm.columnType,
                    vm.columnHolder,
                    vm.columnLinkedApplications,
                    vm.columnStatus,
                    vm.columnExpiryDate,
                    vm.columnDocument,
                    vm.columnAction,
                    vm.columnOriginalLeaseLicenseNumber,
                    vm.columnSite,
                    vm.columnGroups,
                    vm.columnCategories,
                ]
            }
            let buttons = []
            if (vm.is_internal) {
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
                autoWidth: false,
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML,
                },
                rowCallback: function (row, proposal) {
                    let row_jq = $(row)
                    row_jq.attr('id', 'proposal_id_' + proposal.id)
                    row_jq.children().first().addClass(vm.td_expand_class_name)
                },
                responsive: true,
                serverSide: true,
                //searching: false,
                searching: true,
                ajax: {
                    "url": api_endpoints.approvals_paginated_list + '?format=datatables&target_email_user_id=' + vm.target_email_user_id +
                        '&target_organisation_id=' + vm.target_organisation_id + '&target_compliance_id=' + vm.target_compliance_id,
                    //"url": api_endpoints.approvals,
                    "dataSrc": 'data',

                    // adding extra GET params for Custom filtering
                    "data": function (d) {
                        d.filter_approval_type = vm.filterApprovalType
                        d.filter_approval_status = vm.filterApprovalStatus
                        d.filter_approval_expiry_date_from = vm.filterApprovalExpiryDateFrom
                        d.filter_approval_expiry_date_to = vm.filterApprovalExpiryDateTo

                        d.filter_approval_organisation = vm.filterApprovalOrganisation
                        d.filter_approval_region = vm.filterApprovalRegion
                        d.filter_approval_district = vm.filterApprovalDistrict
                        d.filter_approval_group = vm.filterApprovalGroup

                        d.level = vm.level
                    }
                },
                //dom: 'frt', //'lBfrtip',
                //dom: 'lBfrtip',
                dom: "<'d-flex align-items-center'<'me-auto'l>fB>" +
                    "<'row'<'col-sm-12'tr>>" +
                    "<'d-flex align-items-center'<'me-auto'i>p>",
                buttons: buttons,
                columns: selectedColumns,
                processing: true,
                initComplete: function () {
                    console.log('in initComplete')
                },
            }
        },
    },
    methods: {
        number_of_columns: function () {
            let num_cols = this.$refs.approvals_datatable.vmDataTable.columns(':visible').nodes().length;
            return num_cols;
        },
        adjust_table_width: function () {
            this.$refs.approvals_datatable.vmDataTable.columns.adjust()
            this.$refs.approvals_datatable.vmDataTable.responsive.recalc()
        },
        collapsible_component_mounted: function () {
            this.$refs.collapsible_filters.show_warning_icon(this.filterApplied)
        },
        sendData: function (params) {
            let vm = this
            fetch(helpers.add_endpoint_json(api_endpoints.approvals, params.approval_id + '/request_new_stickers'), { body: params, method: 'POST', }).then(
                res => {
                    helpers.post_and_redirect('/sticker_replacement_fee/', { 'csrfmiddlewaretoken': vm.csrf_token, 'data': JSON.stringify(res.body) });
                },
                err => {
                    console.log(err)
                }
            )
        },
        fetchProfile: function () {
            let vm = this;
            fetch(api_endpoints.profile).then((response) => {
                vm.profile = response.body

            }, (error) => {
                console.log(error);

            })
        },
        refreshFromResponseApprovalModify: function () {
            this.$refs.approvals_datatable.vmDataTable.ajax.reload();
        },
        refreshFromResponse: async function (lodgementNumber) {
            console.log("refreshFromResponse");
            await swal({
                title: "Saved",
                text: 'Mooring Licence Application ' + lodgementNumber + ' has been created',
                type: 'success'
            });
            await this.$refs.approvals_datatable.vmDataTable.ajax.reload();
        },
        addEventListeners: function () {
            let vm = this;
            /*
            // update to bs5
            // Lodged From
            $(vm.$refs.approvalDateFromPicker).datetimepicker(vm.datepickerOptions);
            $(vm.$refs.approvalDateFromPicker).on('dp.change',function (e) {
                if ($(vm.$refs.approvalDateFromPicker).data('DateTimePicker').date()) {
                    // DateFrom has been picked
                    vm.filterApprovalExpiryDateFrom = e.date.format('DD/MM/YYYY');
                    $(vm.$refs.approvalDateToPicker).data("DateTimePicker").minDate(e.date);
                }
                else if ($(vm.$refs.approvalDateFromPicker).data('date') === "") {
                    vm.filterApprovalExpiryDateFrom = "";
                    $(vm.$refs.approvalDateToPicker).data("DateTimePicker").minDate(false);
                }
            });

            // Lodged To
            $(vm.$refs.approvalDateToPicker).datetimepicker(vm.datepickerOptions);
            $(vm.$refs.approvalDateToPicker).on('dp.change',function (e) {
                if ($(vm.$refs.approvalDateToPicker).data('DateTimePicker').date()) {
                    // DateTo has been picked
                    vm.filterApprovalExpiryDateTo = e.date.format('DD/MM/YYYY');
                    $(vm.$refs.approvalDateFromPicker).data("DateTimePicker").maxDate(e.date);
                }
                else if ($(vm.$refs.approvalDateToPicker).data('date') === "") {
                    vm.filterApprovalExpiryDateTo = "";
                    $(vm.$refs.approvalDateFromPicker).data("DateTimePicker").maxDate(false);
                }
            });
            */

            //Internal Action shortcut listeners
            let table = vm.$refs.approvals_datatable.vmDataTable
            table.on('processing.dt', function (e) {
            })
            table.on('click', 'a[data-offer]', async function (e) {
                e.preventDefault();
                var id = $(this).attr('data-offer');
                vm.mooringBayId = parseInt($(this).attr('data-mooring-bay'));
                await vm.offerMooringLicence(id);
            }).on('responsive-display.dt', function () {
                var tablePopover = $(this).find('[data-toggle="popover"]');
                if (tablePopover.length > 0) {
                    tablePopover.popover();
                    // the next line prevents from scrolling up to the top after clicking on the popover.
                    $(tablePopover).on('click', function (e) {
                        e.preventDefault();
                        return true;
                    });
                }
            }).on('draw.dt', function () {
                var tablePopover = $(this).find('[data-toggle="popover"]');
                if (tablePopover.length > 0) {
                    tablePopover.popover();
                    // the next line prevents from scrolling up to the top after clicking on the popover.
                    $(tablePopover).on('click', function (e) {
                        e.preventDefault();
                        return true;
                    });
                }
            });
            // Internal Reissue listener
            vm.$refs.approvals_datatable.vmDataTable.on('click', 'a[data-reissue-approval]', function (e) {
                e.preventDefault();
                var id = $(this).attr('data-reissue-approval');
                vm.reissueApproval(id);
            });

            //Internal Cancel listener
            vm.$refs.approvals_datatable.vmDataTable.on('click', 'a[data-cancel-approval]', function (e) {
                e.preventDefault();
                var id = $(this).attr('data-cancel-approval');
                var lodgement_number = $(this).attr('data-approval-lodgement-number');
                vm.cancelApproval(id, lodgement_number);
            });

            //Internal Suspend listener
            vm.$refs.approvals_datatable.vmDataTable.on('click', 'a[data-suspend-approval]', function (e) {
                e.preventDefault();
                var id = $(this).attr('data-suspend-approval');
                var lodgement_number = $(this).attr('data-approval-lodgement-number');
                vm.suspendApproval(id, lodgement_number);
            });

            // Internal Reinstate listener
            vm.$refs.approvals_datatable.vmDataTable.on('click', 'a[data-reinstate-approval]', function (e) {
                e.preventDefault();
                var id = $(this).attr('data-reinstate-approval');
                vm.reinstateApproval(id);
            });

            //Internal/ External Surrender listener
            vm.$refs.approvals_datatable.vmDataTable.on('click', 'a[data-surrender-approval]', function (e) {
                e.preventDefault();
                var id = $(this).attr('data-surrender-approval');
                var lodgement_number = $(this).attr('data-approval-lodgement-number');
                vm.surrenderApproval(id, lodgement_number);
            });

            //External Request New Sticker listener
            vm.$refs.approvals_datatable.vmDataTable.on('click', 'a[data-request-new-sticker]', function (e) {
                e.preventDefault();
                var id = $(this).attr('data-request-new-sticker');
                vm.requestNewSticker(id);
            });

            // External renewal listener
            vm.$refs.approvals_datatable.vmDataTable.on('click', 'a[data-renew-approval]', function (e) {
                e.preventDefault();
                var id = $(this).attr('data-renew-approval');
                vm.renewApproval(id);
            });

            // External amend listener
            vm.$refs.approvals_datatable.vmDataTable.on('click', 'a[data-amend-approval]', function (e) {
                e.preventDefault();
                var id = $(this).attr('data-amend-approval');
                vm.amendApproval(id);
            });

            // Internal history listener
            vm.$refs.approvals_datatable.vmDataTable.on('click', 'a[data-history-approval]', function (e) {
                e.preventDefault();
                var id = $(this).attr('data-history-approval');
                var lodgement_number = $(this).attr('data-approval-lodgement-number');
                vm.approvalHistory(id, lodgement_number);
            });

            // Internal review invoice details listener
            vm.$refs.approvals_datatable.vmDataTable.on('click', 'a[data-review-invoice-detail-approval]', function (e) {
                e.preventDefault();
                var id = $(this).attr('data-review-invoice-detail-approval');
                var lodgement_number = $(this).attr('data-approval-lodgement-number');
                vm.approvalReviewInvoiceDetails(id, lodgement_number);
            });

            // Internal review renewal listener
            vm.$refs.approvals_datatable.vmDataTable.on('click', 'a[data-review-renewal-approval]', function (e) {
                e.preventDefault();
                var id = $(this).attr('data-review-renewal-approval');
                var lodgement_number = $(this).attr('data-approval-lodgement-number');
                vm.approvalReviewRenewal(id, lodgement_number);
            });
        },
        fetchFilterLists: async function () {
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
                    vm.approvalTypes = data
                    console.log(vm.approvalTypes)
                })
                .catch((error) => {
                    console.error('There was an error!', error)
                })
            // Statuses
            fetch(api_endpoints.approval_statuses_dict)
                .then(async (response) => {
                    const data = await response.json()
                    if (!response.ok) {
                        const error =
                            (data && data.message) || response.statusText
                        console.log(error)
                        return Promise.reject(error)
                    }
                    vm.approval_statuses = data
                    console.log(vm.approval_statuses)
                })
                .catch((error) => {
                    console.error('There was an error!', error)
                })
            // Organisations
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
                    console.log(vm.organisations)
                })
                .catch((error) => {
                    console.error('There was an error!', error)
                })
            // Regions
            fetch(api_endpoints.regions + 'key-value-list/')
                .then(async (response) => {
                    const data = await response.json()
                    if (!response.ok) {
                        const error =
                            (data && data.message) || response.statusText
                        console.log(error)
                        return Promise.reject(error)
                    }
                    vm.regions = data
                    console.log(vm.regions)
                })
                .catch((error) => {
                    console.error('There was an error!', error)
                })
            // Districts
            fetch(api_endpoints.districts + 'key-value-list/')
                .then(async (response) => {
                    const data = await response.json()
                    if (!response.ok) {
                        const error =
                            (data && data.message) || response.statusText
                        console.log(error)
                        return Promise.reject(error)
                    }
                    vm.districts = data
                    console.log(vm.districts)
                })
                .catch((error) => {
                    console.error('There was an error!', error)
                })
            // Category
            fetch(api_endpoints.groups + 'key-value-list/')
                .then(async (response) => {
                    const data = await response.json()
                    if (!response.ok) {
                        const error =
                            (data && data.message) || response.statusText
                        console.log(error)
                        return Promise.reject(error)
                    }
                    vm.groups = data
                    console.log(vm.groups)
                })
                .catch((error) => {
                    console.error('There was an error!', error)
                })
            // Not totally sure what this does so commenting out for now
            // const statusRes = await fetch(api_endpoints.approval_statuses_dict);
            // const statusData = await statusRes.json()
            // for (let s of statusData) {
            //     if (this.wlaDash && !(['extended', 'awaiting_payment', 'approved'].includes(s.code))) {
            //         this.statusValues.push(s);
            //         //} else if (!(['extended', 'awaiting_payment', 'offered', 'approved'].includes(s.code))) {
            //     } else if (!(['extended', 'awaiting_payment', 'offered', 'approved'].includes(s.code))) {
            //         this.statusValues.push(s);
            //     }
            // }
        },
        reissueApproval: async function (proposal_id) {
            let vm = this;
            await swal.fire({
                title: "Reissue Approval",
                text: "Are you sure you want to reissue this approval?",
                icon: "warning",
                showCancelButton: true,
                reverseButtons: true,
                confirmButtonText: 'Reissue Approval',
                confirmButtonColor: '#226fbb'
            }).then(async (result) => {
                if (result.isConfirmed) {
                    const requestOptions = {
                        method: "POST",
                    };
                    fetch(helpers.add_endpoint_json(api_endpoints.proposal, (proposal_id + '/reissue_approval')), requestOptions)
                        .then(async response => {
                            const data = await response.json();
                            if (!response.ok) {
                                const error = (data && data.message) || response.statusText;
                                console.log(error)
                                Swal.fire({
                                    title: "Reissue Approval",
                                    text: data,
                                    icon: "error",
                                })
                                Promise.reject(error);
                            }
                            vm.$router.push({
                                name: "internal-proposal",
                                params: { proposal_id: data.id }
                            });

                        }, (error) => {
                            console.log(error);
                            Swal.fire({
                                title: "Reissue Approval",
                                text: error.body,
                                icon: "error",
                            })
                        });
                }
            })

        },

        reinstateApproval: async function (approval_id) {
            let vm = this;
            let status = 'with_approver'
            Swal.fire({
                title: "Reinstate Approval",
                text: "Are you sure you want to reinstate this approval?",
                icon: "warning",
                showCancelButton: true,
                confirmButtonText: 'Reinstate approval',
            }).then(async (result) => {
                if (result.isConfirmed) {
                    try {
                        const response = await fetch(helpers.add_endpoint_json(api_endpoints.approvals, (approval_id + '/approval_reinstate')),
                            {
                                method: 'POST',
                            })
                        Swal.fire(
                            'Reinstate',
                            'Your approval has been reinstated',
                            'success'
                        )
                        vm.$refs.approvals_datatable.vmDataTable.ajax.reload();
                    } catch (error) {
                        console.log(error);
                        Swal.fire(
                            "Reinstate Approval",
                            error.body,
                            "error"
                        )
                    }
                }
            })

        },
        cancelApproval: function (approval_id, approval_lodgement_number) {
            this.selectedApprovalId = parseInt(approval_id);
            this.selectedApprovalLodgementNumber = approval_lodgement_number;
            this.$refs.approval_cancellation.isModalOpen = true;
            this.$nextTick(() => {
                $(`#approvalCancellation${approval_id} textarea.cancellation-details`).focus();
            });
        },
        suspendApproval: function (approval_id, approval_lodgement_number) {
            this.selectedApprovalId = parseInt(approval_id);
            this.selectedApprovalLodgementNumber = approval_lodgement_number;
            this.$refs.approval_suspension.isModalOpen = true;
            this.$nextTick(() => {
                $(`#approvalSuspension${approval_id} input#to_date`).focus();
            });
        },
        surrenderApproval: function (approval_id, approval_lodgement_number) {
            this.selectedApprovalId = parseInt(approval_id);
            this.selectedApprovalLodgementNumber = approval_lodgement_number;
            this.$refs.approval_surrender.isModalOpen = true;
            this.$nextTick(() => {
                $(`#approvalSurrender${approval_id} textarea.surrender-details`).focus();
            });
        },
        requestNewSticker: function (approval_id) {
            this.$refs.request_new_sticker_modal.approval_id = approval_id
            this.$refs.request_new_sticker_modal.isModalOpen = true
        },
        approvalHistory: function (id, approvalLodgementNumber) {
            this.approvalHistoryId = parseInt(id);
            this.selectedApprovalLodgementNumber = approvalLodgementNumber;
            this.uuid++;
            this.$nextTick(() => {
                this.$refs.approval_history.isModalOpen = true;
            });
        },
        approvalReviewInvoiceDetails: function (approval_id, approval_lodgement_number) {
            let vm = this;
            Swal.fire({
                title: "Approval Review Invoice Details",
                text: "Are you sure you want to review the invoice details for this approval?",
                icon: "warning",
                showCancelButton: true,
                reverseButtons: true,
                confirmButtonText: 'Review Invoice Details',
                confirmButtonColor: '#226fbb',
                buttonsStyling: false,
                customClass: {
                    confirmButton: 'btn btn-primary',
                    cancelButton: 'btn btn-secondary me-2'
                },
            }).then(async (result) => {
                if (result.isConfirmed) {
                    let requestOptions = {
                        method: "PATCH",
                    };
                    fetch(helpers.add_endpoint_join(api_endpoints.approvals, (approval_id + '/review_invoice_details/')), requestOptions)
                        .then(async response => {
                            const data = await response.json();
                            if (!response.ok) {
                                const error = (data && data.message) || response.statusText;
                                console.log(error)
                                Promise.reject(error);
                            }
                            vm.$router.push({
                                name: "internal-approval-detail",
                                hash: "#edit-invoicing",
                                params: { approval_id: approval_id }
                            });
                        }, (error) => {
                            console.log(error);
                        });
                }
            })
        },
        approvalReviewRenewal: function (approval_id, approval_lodgement_number) {
            alert('Will implement when we have an idea what is supposed to happen here.')
        },
        renewApproval: async function (proposal_id) {
            let vm = this;
            let status = 'with_approver'
            Swal.fire({
                title: "Renew Approval",
                text: "Are you sure you want to renew this approval?",
                icon: "warning",
                showCancelButton: true,
                confirmButtonText: 'Renew approval',
            }).then(async (result) => {
                if (result.isConfirmed) {
                    const requestOptions = {
                        method: "POST",
                    };
                    fetch(helpers.add_endpoint_json(api_endpoints.proposal, (proposal_id + '/renew_approval')), requestOptions)
                        .then(async response => {
                            const data = await response.json();
                            if (!response.ok) {
                                const error = (data && data.message) || response.statusText;
                                console.log(error)
                                return Promise.reject(error);
                            }
                            vm.$router.push({
                                name: "draft_proposal",
                                params: { proposal_id: data.id }
                            });

                        }, (error) => {
                            console.log(error);
                            Swal.fire({
                                title: "Renew Approval",
                                text: error.body,
                                icon: "error",
                            })
                        });
                }
            })

        },

        amendApproval: async function (proposal_id) {
            let vm = this;
            swal.fire({
                title: "Amend Approval",
                text: "Are you sure you want to amend this approval?",
                icon: "warning",
                showCancelButton: true,
                confirmButtonText: 'Amend approval',
            })
            try {
                const response = fetch(helpers.add_endpoint_json(api_endpoints.proposal, (proposal_id + '/renew_amend_approval_wrapper')) + '?debug=' + vm.debug + '&type=amend',
                    {
                        method: 'POST',
                    })
                vm.$router.push({
                    name: "draft_proposal",
                    params: { proposal_id: proposal.id }
                });
            } catch (error) {
                console.log(error);
                swal.fire({
                    title: "Amend Approval",
                    text: error.body,
                    icon: "error",
                })
            }
        },


    },
    created: async function () {
        await this.fetchFilterLists();
        await this.fetchProfile();
    },
    mounted: function () {
        this.$nextTick(() => {
            this.addEventListeners();
        });
    }
}
</script>

<style scoped></style>
