<template>
    <div>
        <CollapsibleFilters component_title="Filters" ref="collapsible_filters" @created="collapsible_component_mounted"
            class="mb-2">
            <div class="row mt-1 p-2">
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Status</label>
                        <select class="form-control" v-model="filterApplicationStatus">
                            <option value="all">All</option>
                            <option v-for="status in application_statuses" :value="status.id">{{ status.text }}</option>
                        </select>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Created From</label>
                        <div class="input-group date" ref="proposalDateFromPicker">
                            <!-- input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterCompetitiveProcessCreatedFrom" -->
                            <input type="date" class="form-control" placeholder="DD/MM/YYYY"
                                v-model="filterCompetitiveProcessCreatedFrom">
                            <span class="input-group-addon">
                                <span class="glyphicon glyphicon-calendar"></span>
                            </span>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="form-group">
                        <label for="">Created To</label>
                        <div class="input-group date" ref="proposalDateToPicker">
                            <!-- input type="text" class="form-control" placeholder="DD/MM/YYYY" v-model="filterCompetitiveProcessCreatedTo" -->
                            <input type="date" class="form-control" placeholder="DD/MM/YYYY"
                                v-model="filterCompetitiveProcessCreatedTo">
                            <span class="input-group-addon">
                                <span class="glyphicon glyphicon-calendar"></span>
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </CollapsibleFilters>

        <div v-if="is_internal" class="row">
            <div class="text-end mb-2">
                <button type="button" class="btn btn-primary pull-right" @click="new_competitive_process_clicked"><i
                        class="fa-solid fa-circle-plus"></i> New Competitive Process</button>
            </div>
        </div>

        <div class="row">
            <div class="col-lg-12">
                <datatable ref="competitive_process_datatable" :id="datatable_id" :dtOptions="datatable_options"
                    :dtHeaders="datatable_headers" :key="datatable_key" />
            </div>
        </div>
    </div>
</template>

<script>
import datatable from '@/utils/vue/datatable.vue'
import { api_endpoints, constants, helpers } from '@/utils/hooks'
import CollapsibleFilters from '@/components/forms/collapsible_component.vue'
import { v4 as uuid } from 'uuid'
import { expandToggleCP } from '@/components/common/table_functions.js'

export default {
    name: 'TableCompetitiveProcesses',
    props: {
        level: {
            type: String,
            required: true,
            validator: function (val) {
                let options = ['internal', 'referral', 'external'];
                return options.indexOf(val) != -1 ? true : false;
            }
        },
        /*
        target_email_user_id: {
            type: Number,
            required: false,
            default: 0,
        }
        */
    },
    data() {
        let vm = this;
        return {
            datatable_id: "competitive-process-datatable-" + uuid(),
            datatable_key: uuid(),

            // selected values for filtering
            filterApplicationStatus: sessionStorage.getItem('filterApplicationStatus') ? sessionStorage.getItem('filterApplicationStatus') : 'all',
            filterCompetitiveProcessCreatedFrom: sessionStorage.getItem('filterCompetitiveProcessCreatedFrom') ? sessionStorage.getItem('filterCompetitiveProcessCreatedFrom') : '',
            filterCompetitiveProcessCreatedTo: sessionStorage.getItem('filterCompetitiveProcessCreatedTo') ? sessionStorage.getItem('filterCompetitiveProcessCreatedTo') : '',

            // filtering options
            application_statuses: [],

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
        CollapsibleFilters,
    },
    watch: {
        filterApplicationStatus: function () {
            this.$refs.competitive_process_datatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem('filterApplicationStatus', this.filterApplicationStatus);
        },
        filterCompetitiveProcessCreatedFrom: function () {
            console.log('filterCompetitiveProcessCreatedFrom changed')
            this.$refs.competitive_process_datatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem('filterCompetitiveProcessCreatedFrom', this.filterCompetitiveProcessCreatedFrom);
        },
        filterCompetitiveProcessCreatedTo: function () {
            console.log('filterCompetitiveProcessCreatedTo changed')
            this.$refs.competitive_process_datatable.vmDataTable.draw();  // This calls ajax() backend call.  This line is enough to search?  Do we need following lines...?
            sessionStorage.setItem('filterCompetitiveProcessCreatedTo', this.filterCompetitiveProcessCreatedTo);
        },
        filterApplied: function () {
            if (this.$refs.collapsible_filters) {
                // Collapsible component exists
                this.$refs.collapsible_filters.show_warning_icon(this.filterApplied)
            }
        }
    },
    computed: {
        number_of_columns: function () {
            let num = this.$refs.competitive_process_datatable.vmDataTable.columns(':visible').nodes().length;
            return num
        },
        filterApplied: function () {
            let filter_applied = true
            if (this.filterApplicationStatus.toLowerCase() === 'all' && this.filterCompetitiveProcessCreatedFrom.toLowerCase() === '' && this.filterCompetitiveProcessCreatedTo.toLowerCase() === '') {
                filter_applied = false
            }
            return filter_applied
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
        datatable_headers: function () {
            if (this.is_external) {
                return []
            }
            if (this.is_internal) {
                return ['Id', 'Lodgement Number', 'Registration of Interest', 'Status', 'Created On', 'Assigned Officer', 'Action']
            }
        },
        column_id: function () {
            return {
                data: "id",
                // name: 'id',
                orderable: false,
                searchable: false,
                visible: false,
                'render': function (row, type, full) {
                    return full.id
                }
            }
        },
        column_lodgement_number: function () {
            return {
                data: "lodgement_number",
                name: 'lodgement_number',
                orderable: true,
                searchable: true,
                visible: true,
                'render': function (row, type, full) {
                    if (full.migrated) {
                        return full.lodgement_number + ' (M)'
                    } else {
                        return full.lodgement_number
                    }
                },
                name: "lodgement_number",
            }
        },
        column_registration_of_interest: function () {
            return {
                data: "registration_of_interest",
                name: 'originating_proposal__lodgement_number',
                orderable: true,
                searchable: true,
                visible: true,
                'render': function (row, type, full) {
                    if (full.registration_of_interest) {
                        return '<a href="' + api_endpoints.proposal + full.registration_of_interest.id + '">' + full.registration_of_interest.lodgement_number + '</a>'
                    } else {
                        return ''
                    }
                },
            }
        },
        column_status: function () {
            let vm = this
            return {
                data: 'status',
                name: 'status',
                orderable: true,
                searchable: true,
                visible: true,
            }
        },
        column_created_on: function () {
            return {
                data: "id",
                name: 'created_at',
                orderable: true,
                searchable: false,
                visible: true,
                'render': function (row, type, full) {
                    return moment(full.created_at).format('DD/MM/YYYY')
                }
            }
        },
        column_assigned_to: function () {
            return {
                data: "assigned_officer",
                name: 'assigned_officer_id__first_name, assigned_officer_id__last_name',  // This functionality works with `LedgerDatatablesFilterBackend` as filter backaned
                orderable: true,
                searchable: true,
                visible: true,
                'render': function (row, type, full) {
                    if (full.assigned_officer) {
                        return full.assigned_officer.fullname
                    } else {
                        return ''
                    }
                },
            }
        },
        column_action: function () {
            let vm = this
            return {
                // 8. Action
                // data: "action",
                data: null,
                orderable: false,
                searchable: false,
                visible: true,
                'render': function (row, type, full) {
                    console.log({ full })
                    let links = '';
                    if (vm.is_internal) {
                        if (full.can_accessing_user_process) {
                            links += '<a href="/internal/competitive_process/' + full.id + '">Process</a>'
                        }
                        else if (full.can_accessing_user_view) {
                            links += '<a href="/internal/competitive_process/' + full.id + '">View</a>'
                        }
                    }
                    return links;
                }
            }
        },
        datatable_options: function () {
            let vm = this

            let columns = []
            let search = null
            let buttons = []
            if (vm.is_external) {
                columns = [
                ]
                search = false
                buttons = []
            }
            if (vm.is_internal) {
                columns = [
                    vm.column_id,
                    vm.column_lodgement_number,
                    vm.column_registration_of_interest,
                    vm.column_status,
                    vm.column_created_on,
                    vm.column_assigned_to,
                    vm.column_action,
                ]
                search = true
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
                rowCallback: function (row, competitive_process) {
                    let row_jq = $(row)
                    row_jq.attr('id', 'competitive_process_id_' + competitive_process.id)
                    row_jq.children().first().addClass(vm.td_expand_class_name)
                },
                responsive: true,
                serverSide: true,
                searching: search,
                ajax: {
                    "url": api_endpoints.competitive_process + '?format=datatables',
                    "dataSrc": 'data',

                    // adding extra GET params for Custom filtering
                    "data": function (d) {
                        d.filter_status = vm.filterApplicationStatus
                        d.filter_competitive_process_created_from = vm.filterCompetitiveProcessCreatedFrom
                        d.filter_competitive_process_created_to = vm.filterCompetitiveProcessCreatedTo
                        d.level = vm.level
                    }
                },
                //dom: 'lBfrtip',
                dom: "<'d-flex align-items-center'<'me-auto'l>fB>" +
                    "<'row'<'col-sm-12'tr>>" +
                    "<'d-flex align-items-center'<'me-auto'i>p>",
                //buttons:[ ],
                buttons: buttons,
                order: [[1, 'desc']],
                columns: columns,
                processing: true,
                initComplete: function () {
                },
            }
        }
    },
    methods: {
        createNewCompetitiveProcess: async function () {
            await fetch(api_endpoints.competitive_process, { method: 'POST' })
                .then(async response => {
                    if (!response.ok) {
                        return await response.json().then(json => { throw new Error(json); });
                    } else {
                        return await response.json();
                    }
                })
                .then(data => {
                    const competitive_process = Object.assign({}, data);
                    this.$router.push({
                        name: "internal-competitive-process",
                        params: { competitive_process_id: competitive_process.id }
                    });
                })
                .catch(error => {
                    console.log(`Error fetching external approval data ${error.message}`);
                    throw error;
                })
        },
        adjust_table_width: function () {
            this.$refs.competitive_process_datatable.vmDataTable.columns.adjust()
            this.$refs.competitive_process_datatable.vmDataTable.responsive.recalc()
        },
        collapsible_component_mounted: function () {
            this.$refs.collapsible_filters.show_warning_icon(this.filterApplied)
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
        expandCollapseFilters: function () {
            this.filters_expanded = !this.filters_expanded
        },
        new_competitive_process_clicked: function () {
            let vm = this
            swal.fire({
                title: "Create New Competitive Process",
                text: "Are you sure you want to create new competitive process?",
                icon: "warning",
                showCancelButton: true,
                confirmButtonText: 'Create New Competitive Process',
                preConfirm: () => {
                    return true;
                }
                // confirmButtonColor:'#dc3545'
            }).then(async result => {
                if (result.isConfirmed) {
                    // When Yes
                    await vm.createNewCompetitiveProcess()
                    vm.datatable_key = uuid()
                }
            }).catch(error => {
                swal.fire({
                    title: "New Competitive Process",
                    text: error.message,
                    icon: "error",
                });
            });


            //this.$router.push({
            //    name: 'apply_proposal'
            //})
            console.log('New Competitive Process Clicked')
        },
        fetchFilterLists: async function () {
            let vm = this;

            try {
                const res = await fetch(api_endpoints.competitive_process_statuses_dict)
                if (!res.ok)
                    throw new Error(res.statusText)  // 400s or 500s error

                let aho = await res.json()
                vm.application_statuses = aho
            } catch (err) {

            } finally {

            }
        },
        addEventListeners: function () {
            let vm = this

            // Lodged From
            //$(vm.$refs.proposalDateFromPicker).datetimepicker(vm.datepickerOptions);
            //$(vm.$refs.proposalDateFromPicker).on('dp.change',function (e) {
            //    if ($(vm.$refs.proposalDateFromPicker).data('DateTimePicker').date()) {
            //        // DateFrom has been picked
            //        vm.filterCompetitiveProcessCreatedFrom = e.date.format('DD/MM/YYYY');
            //        $(vm.$refs.proposalDateToPicker).data("DateTimePicker").minDate(e.date);
            //    }
            //    else if ($(vm.$refs.proposalDateFromPicker).data('date') === "") {
            //        vm.filterCompetitiveProcessCreatedFrom = "";
            //        $(vm.$refs.proposalDateToPicker).data("DateTimePicker").minDate(false);
            //    }
            //});

            // Lodged To
            //$(vm.$refs.proposalDateToPicker).datetimepicker(vm.datepickerOptions);
            //$(vm.$refs.proposalDateToPicker).on('dp.change',function (e) {
            //    if ($(vm.$refs.proposalDateToPicker).data('DateTimePicker').date()) {
            //        // DateTo has been picked
            //        vm.filterCompetitiveProcessCreatedTo = e.date.format('DD/MM/YYYY');
            //        $(vm.$refs.proposalDateFromPicker).data("DateTimePicker").maxDate(e.date);
            //    }
            //    else if ($(vm.$refs.proposalDateToPicker).data('date') === "") {
            //        vm.filterCompetitiveProcessCreatedTo = "";
            //        $(vm.$refs.proposalDateFromPicker).data("DateTimePicker").maxDate(false);
            //    }
            //});

            // Listener for thr row
            vm.$refs.competitive_process_datatable.vmDataTable.on('click', 'td', function (e) {
                expandToggleCP(vm, this);
            })
        },
    },
    created: function () {
        this.fetchFilterLists()
    },
    mounted: function () {
        let vm = this;
        this.$nextTick(() => {
            vm.addEventListeners();
        });
    }
}
</script>

<style scoped>
.collapse-icon {
    cursor: pointer;
}

.collapse-icon::before {
    top: 5px;
    left: 4px;
    height: 14px;
    width: 14px;
    border-radius: 14px;
    line-height: 14px;
    border: 2px solid white;
    line-height: 14px;
    content: '-';
    color: white;
    background-color: #d33333;
    display: inline-block;
    box-shadow: 0px 0px 3px #444;
    box-sizing: content-box;
    text-align: center;
    text-indent: 0 !important;
    font-family: 'Courier New', Courier monospace;
    margin: 5px;
}

.expand-icon {
    cursor: pointer;
}

.expand-icon::before {
    top: 5px;
    left: 4px;
    height: 14px;
    width: 14px;
    border-radius: 14px;
    line-height: 14px;
    border: 2px solid white;
    line-height: 14px;
    content: '+';
    color: white;
    background-color: #337ab7;
    display: inline-block;
    box-shadow: 0px 0px 3px #444;
    box-sizing: content-box;
    text-align: center;
    text-indent: 0 !important;
    font-family: 'Courier New', Courier monospace;
    margin: 5px;
}
</style>
