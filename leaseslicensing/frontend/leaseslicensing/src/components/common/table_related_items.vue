<template lang="html">
    <datatable ref="related_items_datatable" :id="datatable_id" :dtOptions="datatable_options"
        :dtHeaders="datatable_headers" />
</template>

<script>
import { v4 as uuid } from 'uuid'
import { constants } from '@/utils/hooks'
import datatable from '@/utils/vue/datatable.vue'

export default {
    name: 'TableRelatedItems',
    components: {
        datatable,
    },
    props: {
        ajax_url: {
            type: String,
            required: true,
        }
    },
    data() {
        let vm = this;
        return {
            datatable_id: uuid(),
        }
    },
    computed: {
        column_lodgement_number: function () {
            return {
                data: 'identifier',
                orderable: false,
                searchable: false,
                visible: true,
            }
        },
        column_type: function () {
            return {
                data: 'model_name',
                orderable: false,
                searchable: false,
                visible: true,
            }
        },
        column_description: function () {
            return {
                data: 'descriptor',
                orderable: false,
                searchable: false,
                visible: true,
                'render': function (row, type, full) {
                    /** The related item description is to be determined per type:
                     * - Application - application status
                     * - Lease/License - expiry date
                     */
                    if (full.type === "application") {
                        return constants.PROPOSAL_STATUS[full.descriptor.toUpperCase()].TEXT;
                    } else if (full.type === "lease_license") {
                        return full.descriptor;
                    } else if (full.type === "competitive_process") {
                        return constants.COMPETITIVE_PROCESS_STATUS[full.descriptor.toUpperCase()].TEXT;
                    } else {
                        return full.descriptor;
                    }
                }
            }
        },
        column_action: function () {
            return {
                data: 'action_url',
                orderable: false,
                searchable: false,
                visible: true,
            }
        },
        datatable_options: function () {
            let vm = this
            let columns = [
                vm.column_lodgement_number,
                vm.column_type,
                vm.column_description,
                vm.column_action,
            ]
            return {
                autoWidth: false,
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML,
                },
                responsive: true,
                serverSide: true,
                searching: true,
                ordering: true,
                order: [[0, 'desc']],
                ajax: {
                    "url": vm.ajax_url,
                    "dataSrc": "",
                    "data": function (d) {
                    }
                },
                dom: 'lBfrtip',
                buttons: [],
                columns: columns,
                processing: true,
            }
        },
        datatable_headers: function () {
            return [
                'Number',
                'Type',
                'Description',
                'Action',
            ]
        },
    }
}
</script>
