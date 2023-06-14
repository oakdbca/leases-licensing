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
                data: 'lodgement_number',
                orderable: false,
                searchable: false,
                visible: true,
            }
        },
        column_type: function () {
            return {
                data: 'item_type',
                orderable: false,
                searchable: false,
                visible: true,
            }
        },
        column_description: function () {
            return {
                data: 'description',
                orderable: false,
                searchable: false,
                visible: true,
            }
        },
        column_action: function () {
            return {
                data: 'detail_url',
                orderable: false,
                searchable: false,
                visible: true,
                render: function (data, type, row) {
                    return `<a href="${data}" target="_blank">View</a>`
                }
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
                    "dataSrc": "data",
                    "data": function (d) {
                    },
                    error: function(response, textStatus, errorThrown){
                        let error = response.responseJSON? response.responseJSON.data: response.responseText;
                        console.log(
                            `${textStatus}: ${errorThrown}: ${JSON.stringify(error)}`
                        );
                    },
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
