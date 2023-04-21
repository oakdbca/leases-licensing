<template>
    <div>
        <div v-if="is_internal" class="row">
            <div class="text-end mb-2">
                <button type="button" class="btn btn-primary pull-right" @click="add_party_clicked"
                    :disabled="elementDisabled"><i class="fa-solid fa-circle-plus"></i> Add Party</button>
            </div>
        </div>

        <div class="row">
            <div class="col-lg-12">
                <datatable ref="parties_datatable" :id="datatable_id" :dtHeaders="datatable_headers"
                    :dtOptions="datatable_options" :key="datatable_key" />
            </div>
        </div>

        <AddPartyModal ref="add_party" @closeModal="closeModal" @refreshDatatable="refreshFromResponse"
            @partyToAdd="addParty"/>
    </div>
</template>

<script>
import { v4 as uuid } from 'uuid'
import datatable from '@/utils/vue/datatable.vue'
import AddPartyModal from '@/components/common/modal_add_party.vue';
import { expandToggleParties } from '@/components/common/table_functions.js'
import { api_endpoints, constants } from "@/utils/hooks.js"

export default {
    name: 'TableParties',
    props: {
        level: '',
        competitive_process_parties: {
            type: Array,
            default: function () {
                return []
            }
        },
        competitive_process_id: '',
        accessing_user: null,
        processing: {
            type: Boolean,
            default: false
        },
        discarded: {
            type: Boolean,
            default: false
        },
        declined: {
            type: Boolean,
            default: false
        },
        completed: {
            type: Boolean,
            default: false
        },
        finalised: {
            type: Boolean,
            default: false
        },
    },
    data() {
        let vm = this;
        return {
            datatable_id: uuid(),
            datatable_key: uuid(),
            new_party_id: -1, // This is used to identify new parties in the datatable

            // For expander
            td_expand_class_name: 'expand-icon',
            td_collapse_class_name: 'collapse-icon',
            expandable_row_class_name: 'expandable_row',
            custom_row_apps: {},
        }
    },
    components: {
        datatable,
        AddPartyModal,
    },
    created: function () {
    },
    mounted: function () {
        let vm = this
        vm.$nextTick(() => {
            vm.addEventListeners();
        });
    },
    computed: {
        column_id: () => {
            return {
                data: "id",
                name: 'id',
                orderable: false,
                searchable: false,
                visible: false,
                'render': function (row, type, full) {
                    return full.id
                }
            }
        },
        column_name: () => {
            return {
                data: null,
                'render': function (row, type, full) {
                    if (full.is_person) {
                        return  "fullname" in full.person? full.person.fullname:
                                "full_name" in full.person? full.person.full_name:
                                "(name)";
                    } else {
                        return "";
                    }
                }
            }
        },
        column_organisation: () => {
            return {
                data: null,
                'render': function (row, type, full) {
                    if (full.is_organisation)
                        return full.organisation.trading_name;
                    return ''
                }
            }
        },
        column_phone: () => {
            return {
                data: null,
                'render': function(row, type, full){
                    if (full.is_person && full.person) {
                        return full.person.phone_number? full.person.phone_number: "";
                    } else if (full.is_organisation && full.organisation) {
                        // Return the phone number of the first org contact in the list
                        if (full.organisation.contacts && full.organisation.contacts.length > 0) {
                            return full.organisation.contacts[0].phone_number;
                        }
                        return "";
                    } else {
                        return '(phone)';
                    }
                }
            }
        },
        column_mobile: () => {
            return {
                data: null,
                'render': function(row, type, full){
                    if (full.is_person && full.person) {
                        return full.person.mobile_number? full.person.mobile_number: "";
                    } else if (full.is_organisation && full.organisation) {
                        // Return the mobile number of the first org contact in the list
                        if (full.organisation.contacts && full.organisation.contacts.length > 0) {
                            return full.organisation.contacts[0].mobile_number;
                        }
                        return "";
                    } else {
                        return '(mobile)';
                    }
                }
            }

        },
        column_email: () => {
            return {
                data: null,
                'render': function(row, type, full){
                    if (full.is_person && full.person) {
                        return full.person.email? full.person.email: "";
                    } else if (full.is_organisation) {
                        return full.organisation.ledger_organisation_email;
                    } else {
                        return '(email)';
                    }
                }
            }
        },
        is_external: function() {
            return this.level == 'external'
        },
        is_internal: function () {
            return this.level == 'internal'
        },
        datatable_headers: function(){
            if (this.is_internal){
                return ['id', 'Name', 'Organisation', 'Phone', 'Mobile', 'Email']
            }
            return []
        },
        datatable_options: function () {
            let vm = this

            let columns = []
            let search = null
            if (vm.is_internal) {
                columns = [
                    vm.column_id,
                    vm.column_name,
                    vm.column_organisation,
                    vm.column_phone,
                    vm.column_mobile,
                    vm.column_email,
                ]
                search = true
            }

            return {
                autoWidth: false,
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML,
                },
                columnDefs: [
                    {responsivePriority: 1, targets: 1},
                    {responsivePriority: 2, targets: 2},
                    {responsivePriority: 6, targets: 3},
                    {responsivePriority: 5, targets: 4},
                    {responsivePriority: 4, targets: 5},
                ],
                createdRow: function (row, full_data, dataIndex) {
                    full_data.expanded = false
                },
                rowCallback: function (row, aho) {
                    let $row = $(row)
                    $row.children().first().addClass(vm.td_expand_class_name)
                },
                responsive: true,
                serverSide: false,
                data: vm.competitive_process_parties,
                searching: search,
                dom: "<'d-flex align-items-center'<'me-auto'l>f>" +
                    "<'row'<'col-sm-12'tr>>" +
                    "<'d-flex align-items-center'<'me-auto'i>>",
                columns: columns,
                processing: true,
                initComplete: function () {
                    console.log('in initComplete')
                },
            }
        },
        elementDisabled: function() {
            // Returns whether an element is disabled
            // True while processing (saving), when discarded, finalized, declined, or completed
            return this.processing || this.discarded || this.finalised || this.declined || this.completed;
        }
    },
    methods: {
        addParty: async function(params){
            let url;
            let is_person = params.type === 'person';
            let is_organisation = params.type === 'organisation'

            if (is_person) {
                for (let party of this.competitive_process_parties) {
                    if (party.is_person && party.person_id === params.party_to_add.id)
                        // Person has been already added
                        return
                    }
                url = `${api_endpoints.users}${params.party_to_add.id}`;
            } else if (is_organisation) {
                for (let party of this.competitive_process_parties){
                    if (party.is_organisation && party.organisation === params.party_to_add.id)
                        // Organisation has already been added
                        return;
                }
                url = `${api_endpoints.organisations_viewset}${params.party_to_add.id}`;
            }

            console.log(api_endpoints)
            await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            }).then(async response => {
                if (response.ok) {
                    return await response.json();
                } else {
                    return response.text().then(text => { throw new Error(text) });
                }
            }).then(data => {
                let new_data = {
                    'id': 0,  // This is competitive_process_party id.  Empty string because this is not saved yet.
                    'is_person': is_person, //true,
                    'is_organisation': is_organisation, // false,
                    'person': is_person? data: null, // Either a person or an organisation
                    'person_id': is_person? data.id: null,
                    'organisation': is_organisation? data: null,
                    'organisation_id': is_organisation? data.id: null,
                    'invited_at': null,
                    'removed_at': null,
                    'party_details': [],
                    'expanded': false,
                }
                this.competitive_process_parties.push(new_data)
                this.$refs.parties_datatable.vmDataTable.row.add(new_data).draw()
            }).catch(error => {
                console.error(error.message);
            });

            for (let party of this.competitive_process_parties) {
                // Somehow all the expander collapsed when adding a new row.  Accordingly set the expanded attribute to false
                party.expanded = false
            }

        },
        openAddPartyModal: function () {
            this.$nextTick(() => {
                this.$refs.add_party.isModalOpen = true;
            });
        },
        closeModal: function () {
            this.uuid++;
        },
        refreshFromResponse: async function () {
            // await this.$refs.vessels_datatable.vmDataTable.ajax.reload();
            console.log('TODO: update table')
        },
        number_of_columns: function () {
            // Return the number of visible columns
            let num = this.$refs.parties_datatable.vmDataTable.columns(':visible').nodes().length;
            return num
        },
        updateCustomRowColSpan: function () {
            // Set colspan to the manually added table row
            $('tr.' + this.expandable_row_class_name + ' td').attr('colspan', this.number_of_columns())
        },
        add_party_clicked: function () {
            this.openAddPartyModal()
        },
        addClickEventHandler: function () {
            let vm = this

            vm.$refs.parties_datatable.vmDataTable.on('click', 'td', function () {
                expandToggleParties(vm, this);
            })
        },
        addResponsiveResizeHandler: function () {
            console.log('in addResponsiveResizeHandler')
            // When columns are shown/hidden, expand/collapse the child row according to the current expand-collapse status of each row
            let vm = this
            vm.$refs.parties_datatable.vmDataTable.on('responsive-resize', function (e, datatable, columns) {
                // This event can be used to inform external libraries and controls that Responsive has changed the visibility of columns in the table in response to a resize or recalculation event.
                vm.updateCustomRowColSpan()
                datatable.rows().every(function (rowIdx, tableLoop, rowLoop) {
                    // Work on each row
                    let full_data = this.data()
                    if (full_data.expanded) {
                        this.child.show()
                    } else {
                        this.child.hide()
                    }
                })
            })
        },
        addTableDrawListener: function() {
            /** Listens on datatable draw events and adds a negative id to new rows.
             *  This is because new rows are not yet saved to the database and therefore
             *  do not have an id, but need to be distinguishable in the frontend for
             *  adding new details/documents.
             */

            let vm = this;
            // The id of the datatable
            let id = $(vm.$refs.parties_datatable)[0].id;

            $(`#${id}`).DataTable().on('draw.dt', function (e, table) {
                // Iterate through all new rows and add a negative id to those with id = 0
                $(table.aoData).each(function (_, row) {
                    let _id = row._aData["id"];
                    if (_id == 0) {
                        row._aData["id"] = vm.new_party_id;
                        console.log("ID", row._aData["id"]);
                        vm.new_party_id --;
                    }
                })
            })
        },
        addEventListeners: function () {
            console.log('in addEventListener')
            this.addTableDrawListener();
            this.addClickEventHandler()
            this.addResponsiveResizeHandler()
        },
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

.expandable_row {
    background-color: lightgray !important;
}
</style>
