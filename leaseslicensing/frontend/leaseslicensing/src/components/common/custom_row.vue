<template>
    <table class="party_detail_table">
        <tr>
            <th>Invited to competitive process</th>
            <td><input type="date" class="form-control w-auto" placeholder="DD/MM/YYYY"
                v-model="party_invited_at" disabled></td>
        </tr>
        <tr>
            <th>Removed from competitive process</th>
            <td><input type="date" class="form-control w-auto" placeholder="DD/MM/YYYY"
                v-model="party_full_data.removed_at" :disabled="elementDisabled"
                @change="partyDateChanged($event, 'removed_at')"></td>
        </tr>
        <tr>
            <th>Details</th>
            <td>
                <div v-if="party_full_data.party_details.length > 0" class="details_box p-2">
                    <template v-for="(party_detail, index) in party_full_data.party_details" :key="party_detail.key">
                        <template v-if="index!=0">
                            <hr class="m-1">
                        </template>

                        <div class="detail_wrapper">

                            <template v-if="party_detail.id || elementDisabled">
                                <!-- This is an entry already saved in the database -->
                                <div>{{ party_detail.created_by.full_name?
                                        party_detail.created_by.full_name:
                                        party_detail.created_by.fullname }},
                                     {{ formatDatetime(party_detail.created_at) }}
                                </div>
                            </template>
                            <template v-else>
                                <!-- This entry is the one added just now, and not saved into the database yet -->
                                <div>{{ party_detail.accessing_user.full_name }},
                                     {{ formatDatetime(party_detail.created_at) }}
                                </div>
                                <div class="remove_party_detail text-danger" @click="remove_party_detail(party_detail, $event)"><i class="bi bi-x-circle-fill"></i></div>
                            </template>

                            <div>{{ party_detail.detail }}</div>

                            <template v-for="document in party_detail.party_detail_documents">
                                <div>
                                    <a :href="document.file" target="_blank"><i :class="getFileIconClass(document.file, ['bi', 'fa-lg'])"></i> {{ document.name }}</a>
                                </div>
                            </template>
                        </div>
                    </template>
                </div>
                <div class="new_detail_div mt-2 p-2">
                    <table class="party_detail_table">
                        <tr>
                            <th>New detail</th>
                            <td>
                                <input type="text" class="form-control detail_text" v-model="new_detail_text"
                                    :disabled="removed_from_cp || elementDisabled">
                            </td>
                        </tr>
                        <tr>
                            <th>Documents</th>
                            <td>
                                <div v-if="removed_from_cp || elementDisabled">Attach document</div>
                                <div v-else>
                                    <FileField
                                        :readonly="readonly"
                                        ref="temp_document"
                                        name="temp_document"
                                        :isRepeatable="true"
                                        :documentActionUrl="detailDocumentUrl"
                                        :replace_button_by_text="true"
                                        :temporaryDocumentCollectionId="temporary_document_collection_id"
                                        @update-temp-doc-coll-id="addToTemporaryDocumentCollectionList"
                                        :key="filefield_id"
                                    ></FileField>
                                </div>
                            </td>
                        </tr>
                        <tr>
                            <th></th>
                            <td class="text-end"><button class="btn btn-primary" @click="addDetailClicked"
                                :disabled="removed_from_cp || elementDisabled">
                                <i class="fa-solid fa-circle-plus"></i> Add</button>
                            </td>
                        </tr>
                    </table>
                </div>
            </td>
        </tr>
    </table>
</template>

<script>
import { api_endpoints, helpers } from '@/utils/hooks'
import FileField from '@/components/forms/filefield_immediate.vue'
import { v4 as uuid } from 'uuid';

export default {
    name: 'CustomRow',
    emits: ["add-detail"],
    props: {
        party_full_data: null,
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
    },
    components: {
        FileField,
    },
    data() {
        let vm = this;
        return {
            temporary_document_collection_id: 0,
            new_detail_text: '',
            datetimeFormat: 'DD/MM/YYYY HH:mm:ss',
            filefield_id: uuid(),
        }
    },
    created: function(){

    },
    computed: {
        readonly: function(){
            return false
        },
        existingDetail: function() {
            return false
        },
        detailDocumentUrl: function() {
            let url = '';
            if (this.existingDetail) {
                // url = helpers.add_endpoint_join(
                //     api_endpoints.vesselownership,
                //     this.vessel.vessel_ownership.id + '/process_vessel_registration_document/'
                // )
            } else {
                url = 'temporary_document';
            }
            return url;
        },
        party_invited_at: function() {
            // For now use field `created_at` instead at `invited_at` for invitation date
            // Date of invitation is supposed to be read-only, so no point in utilizing a
            // writable field
            return this.formatDatetime(this.party_full_data.created_at, "YYYY-MM-DD");
        },
        removed_from_cp: function() {
            // Returns whether this party has been removed from the Competitive Process
            return moment(this.party_full_data.removed_at).isValid()? true: false;
        },
        elementDisabled: function() {
            // Returns whether an element is disabled
            // True while processing (saving) or when discarded
            return this.processing || this.discarded || this.declined;
        }
    },
    methods: {
        remove_party_detail: function(item, e){
            let vm = this
            let $elem = $(e.target)

            $elem.closest('.detail_wrapper').fadeOut(500, function(){
                const index = vm.party_full_data.party_details.indexOf(item)
                if (index > -1){
                    vm.party_full_data.party_details.splice(index, 1)
                }
            }).prev('hr').fadeOut(500)
        },
        getFileIconClass: function(filepath, additional_class_names){
            return helpers.getFileIconClass(filepath, additional_class_names)
        },
        formatDatetime: function(dt, format){
            if (format == null) {
                format = this.datetimeFormat;
            }
            return moment(dt).format(format);
        },
        addDetailClicked: function(){
            /** On adding new party details emit an event to the
             * `competitive_process` vue component, containing
             *  the party's ID and a dictionary of the new details
             */

            let now = new Date()
            let new_party_data = {};
            let new_detail = {
                'id': 0,  // Should be 0, which is used to determine this as a new entry at the backend
                'key': uuid(),  // This is used only for vue for-loop
                'created_at': now,
                'detail': this.new_detail_text,
                'temporary_document_collection_id': this.temporary_document_collection_id,
                'created_by_id': this.accessing_user.id,
                'created_by': this.accessing_user, // added to prevent vue renderer crash
                'accessing_user': this.accessing_user,
                'party_detail_documents': this.$refs.temp_document.documents,
            }
            new_party_data[this.party_full_data.id] = new_detail;
            this.$emit("add-detail", new_party_data);
        },
        addToTemporaryDocumentCollectionList(temp_doc_id) {
            console.log({temp_doc_id})
            this.temporary_document_collection_id = temp_doc_id;
        },
        partyDateChanged: function(e, date_field) {
            if (!date_field in this.party_full_data) {
                return;
            }
            let new_date = e.target.value;
            if (new_date === '') {
                // Set date to `null` if form field has been cleared
                new_date = null;
            } else if (date_field === 'removed_at') {
                // Clear detail text box when `removed_at` is set
                this.new_detail_text = '';
            }
            this.party_full_data[date_field] = new_date;
        },
    }
}
</script>
<style scoped>
.party_detail_table {
    width: 100%;
}
.party_detail_table th, td {
    border: none;
}
.new_detail_div {
    border: 1px solid lightgray;
    border-radius: 0.25em;
    background-color: white;
}
.details_box {
    /* border: 1px solid lightgray; */
    border-radius: 0.25em;
    background-color: whitesmoke;
}
.detail_text {
    width: 100%;
}
.remove_party_detail{
    position: absolute;
    top: 0;
    right: 0;
    cursor: pointer;
}
.detail_wrapper {
    position: relative;
}

</style>