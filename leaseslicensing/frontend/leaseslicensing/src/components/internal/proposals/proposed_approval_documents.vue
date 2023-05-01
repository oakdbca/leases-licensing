<template lang="html">
    <div id="proposedApprovalDocuments">
        <div class="container-fluid">
            <div class="row">
                <form class="form-horizontal" name="approvalDocumentsForm">
                    <div class="col-sm-12">
                        <div class="form-group">

                            <div v-if="!readonly" class="row modal-input-row">
                                <div v-if="withApprover">
                                    Selected documents that need to be attached as part of the approval of this application
                                </div>
                                <div v-else class="col-sm-12">
                                    Select zero or more documents that need to be attached as part of the approval of this application
                                </div>
                            </div>
                            <div class="form-group" v-if="isLeaseLicence && !readonly && !withApprover">
                                <div class="row modal-input-row">
                                    <div class="col-sm-4">
                                        <select
                                            ref="select_document"
                                            class="form-control"
                                            id="documentTypeSelector"
                                            :disabled="this.availableDocumentTypes.length == 0"
                                        >
                                            <option></option>
                                            <option v-for="docType in availableDocumentTypes" :value="docType.id">{{ docType.name }}</option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            <div v-for="docType in selectedDocumentTypes">
                                <div class="row modal-input-row">
                                    <div class="col-sm-3">
                                        <textarea :disabled="true" class="control-label pull-left"
                                                rows="1" placeholder="<selected document type>"
                                                style="resize: none"
                                        >{{ docType.name }}</textarea>
                                    </div>
                                    <div class="col-sm-9">
                                        <FileField
                                            :readonly="withApprover || readonly"
                                            :name="'lease_licence_approval_documents_' + docType.name + '_' + docType.id"
                                            :id="'lease_licence_approval_documents_' + docType.name + '_' + docType.id"
                                            :approval_type="selectedApprovalTypeId"
                                            :approval_type_document_type="docType.id"
                                            :isRepeatable="true"
                                            :documentActionUrl="leaseLicenceApprovalDocumentsUrl"
                                            :replace_button_by_text="true"
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </form>
            </div>
        </div>

        <div slot="footer">
        </div>
    </div>
</template>

<script>
import { constants } from '@/utils/hooks';
import { helpers, api_endpoints } from "@/utils/hooks.js"
import FileField from '@/components/forms/filefield_immediate.vue'

export default {
    name: "ProposedApprovalDocuments",
    props: {
        proposal: {
            type: Object,
            required: true,
        },
        proposal_id: {
            type: Number,
            required: true,
        },
        readonly: {
            type: Boolean,
            default: false,
        },
        availableDocumentTypes: {
            type: Array,
            default: [],
        },
        selectedDocumentTypes: {
            type: Array,
            default: [],
        },
    },
    components: {
        FileField,
    },
    data: function() {
        let vm = this;
        return {
            selectedApprovalTypeId: null,
        }
    },
    computed: {
        withApprover: function(){
            return [constants.PROPOSAL_STATUS.WITH_APPROVER.ID,].includes(
                this.proposal.processing_status_id
                ) ?
                true :
                false;
        },
        isLeaseLicence: function(){
            if (this.proposal && this.proposal.application_type.name === 'lease_licence') {
                return true;
            }
        },
        leaseLicenceApprovalDocumentsUrl: function() {
            return helpers.add_endpoint_join(
                api_endpoints.proposal,
                this.proposal.id + '/process_lease_licence_approval_document/'
                )
        },
        canChangeDocuments: function() {
            /** TODO: (53-1) Approval type, commencement and expiry and approval document
             *  cannot be changed by the approver, _but_ can the approver add additional
             *  documents? If so, requires more sophisticated logic to distinguish between
             *  sources of proposed approval documents (e.g. in
             *  `vm.proposal.proposed_issuance_approval`).
             */

            let with_assessor = [constants.PROPOSAL_STATUS.WITH_ASSESSOR.ID,
            constants.PROPOSAL_STATUS.WITH_ASSESSOR_CONDITIONS.ID,].includes(
                this.proposal.processing_status_id) ?
                    true :
                    false;

            return with_assessor;
        },
    },
    methods: {
        emitUpdateSelectedDocumentTypes: function(id, remove) {
            this.$emit("update-selected-document-types", id, remove);
        },
        documentTypeSelectorBlur() {
            $('#'+'documentTypeSelector').val(null).trigger("change");
        },
        /**
         * Initialise the select2 control for adding documents as part of the application
         */
        initSelectDocument: function() {
            let vm = this;

            $(vm.$refs.select_document).select2({
                "theme": "bootstrap-5",
                allowClear: true,
                placeholder: "Add a document",
                multiple: false, // TODO: Maybe there is a more elegant solution with mutliple selection
                templateSelection: function (data) {
                    // Add custom styling to the <option> tag for the selected option or placeholder

                    if (data.id === '') {
                        if (vm.selectedDocumentTypes.length == 0) {
                            return $('<div style="color: grey;">Add a document</div>');
                        } else {
                            return $('<div style="color: grey;">Add another document</div>');
                        }
                    }
                    return $('<div">' + data.text + '</div>');
                },
                templateResult: function(result) {
                    // Add custom styling to the selection dropdown options

                    if(!result.id) {
                        return $('<div style="color: grey;">' + result.text + '</div>');
                    }
                    else {
                        return $('<div>' + result.text + '</div>');
                    }
                },
            }).on("select2:select", function (e) {
                var selected = $(e.currentTarget);
                // Check if user can add documents
                if (vm.canChangeDocuments) {
                    var added = vm.emitUpdateSelectedDocumentTypes(selected.val());
                    if (added) {
                        // If a new item has been added, clear the select2 field. If an existing
                        // item has been selected, show it as selected so it can be deleted.
                        console.log('added');
                        vm.documentTypeSelectorBlur();
                    }
                }
            }).on("select2:unselecting", function (e) {
                var self = $(this);
                setTimeout(() => {
                    self.select2('close');
                }, 0);
            }).on("select2:unselect", function (e) {
                // Check if user can change documents
                if (vm.canChangeDocuments) {
                    let unselected_id = e.params.data.id;
                    // Remove the unselected item from the list of selected items
                    vm.emitUpdateSelectedDocumentTypes(unselected_id, true);
                    vm.documentTypeSelectorBlur();
                }
            });
        }
    },
    created: async function() {
        let vm = this;
        vm.approval = Object.assign({}, vm.proposal.proposed_issuance_approval);
        vm.selectedApprovalTypeId = this.approval.approval_type;

        this.$nextTick(()=>{
            this.initSelectDocument();
        });
    }
}

</script>