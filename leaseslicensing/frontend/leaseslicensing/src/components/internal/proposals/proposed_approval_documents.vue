<template lang="html">
    <div id="proposedApprovalDocuments">
        <div class="container-fluid">
            <div class="row">
                <form class="form-horizontal" name="approvalDocumentsForm">
                    <div class="col-sm-12">
                        <div class="form-group">
                            <div v-if="!readonly" class="row mb-3">
                                <div v-if="withApprover">
                                    Selected documents that need to be attached
                                    as part of the approval of this application
                                </div>
                                <div v-else class="col-sm-12">
                                    Select zero or more documents that that are
                                    required for the approval of this
                                    application
                                </div>
                            </div>
                            <div
                                v-if="isLeaseLicence && !readonly"
                                class="form-group"
                            >
                                <div class="row mb-3">
                                    <div class="col-sm-4">
                                        <select
                                            id="documentTypeSelector"
                                            ref="select_document"
                                            class="form-control"
                                            :v-model="selectedDocumentTypesIds"
                                            :disabled="
                                                availableDocumentTypes.length ==
                                                0
                                            "
                                        >
                                            <option></option>
                                            <option
                                                v-for="docType in availableDocumentTypes"
                                                :key="docType.id"
                                                :value="docType.id"
                                            >
                                                {{ docType.name }}
                                            </option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <div
                                v-for="docType in selectedDocumentTypes"
                                :key="docType.id"
                                class="border rounded mb-3 p-3"
                                :value="docType.id"
                            >
                                <div class="row mb-3">
                                    <div class="col fw-bold">
                                        {{ docType.name }}
                                    </div>
                                </div>
                                <div class="row mb-3">
                                    <div class="col">
                                        <FileField
                                            :id="
                                                'lease_licence_approval_documents_' +
                                                docType.name +
                                                '_' +
                                                docType.id
                                            "
                                            :readonly="readonly"
                                            :name="
                                                'lease_licence_approval_documents_' +
                                                docType.name +
                                                '_' +
                                                docType.id
                                            "
                                            :approval_type="
                                                selectedApprovalTypeId
                                            "
                                            :approval_type_document_type="
                                                docType.id
                                            "
                                            :is-repeatable="true"
                                            :document-action-url="
                                                leaseLicenceApprovalDocumentsUrl
                                            "
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

        <!-- eslint-disable-next-line vue/no-deprecated-slot-attribute -->
        <div slot="footer"></div>
        <!--eslint-enable-->
    </div>
</template>

<script>
import { constants } from '@/utils/hooks';
import { helpers, api_endpoints } from '@/utils/hooks.js';
import FileField from '@/components/forms/filefield_immediate.vue';
import { updateIdListFromAvailable } from '@/components/common/workflow_functions.js';

export default {
    name: 'ProposedApprovalDocuments',
    components: {
        FileField,
    },
    props: {
        proposal: {
            type: Object,
            required: true,
        },
        proposalId: {
            type: Number,
            required: true,
        },
        readonly: {
            type: Boolean,
            default: false,
        },
        approvalTypes: {
            type: Array,
            default: () => [],
        },
        selectedApprovalTypeId: {
            type: Number,
            default: null,
        },
    },
    data: function () {
        return {
            selectedDocumentTypes: [],
            availableDocumentTypes: [],
        };
    },
    computed: {
        withApprover: function () {
            return [constants.PROPOSAL_STATUS.WITH_APPROVER.ID].includes(
                this.proposal.processing_status_id
            )
                ? true
                : false;
        },
        isLeaseLicence: function () {
            if (
                this.proposal &&
                this.proposal.application_type.name === 'lease_licence'
            ) {
                return true;
            }
            return false;
        },
        leaseLicenceApprovalDocumentsUrl: function () {
            return helpers.add_endpoint_join(
                api_endpoints.proposal,
                this.proposal.id + '/process_lease_licence_approval_document/'
            );
        },
        canChangeDocuments: function () {
            /** The assessor and the approver can change the documents
             */

            return [
                constants.PROPOSAL_STATUS.WITH_ASSESSOR.ID,
                constants.PROPOSAL_STATUS.WITH_ASSESSOR_CONDITIONS.ID,
                constants.PROPOSAL_STATUS.WITH_APPROVER.ID,
            ].includes(this.proposal.processing_status_id);
        },
        selectedDocumentTypesIds: function () {
            // Return the ids of selected document types from the document type-dropdown
            return this.selectedDocumentTypes.map(({ id }) => id);
        },
    },
    created: async function () {
        let vm = this;
        vm.approval = Object.assign({}, vm.proposal.proposed_issuance_approval);
        vm.availableDocumentTypes = [];
        vm.selectedDocumentTypes = [];

        vm.$nextTick(() => {
            vm.initSelectDocument();

            // Available Document Types
            for (const approvalType of vm.approvalTypes) {
                if (approvalType.id === vm.selectedApprovalTypeId) {
                    for (const docType of approvalType.approval_type_document_types) {
                        vm.availableDocumentTypes.push(docType);
                    }
                }
            }

            // Selected Document Types
            if (vm.approval.selected_document_types) {
                vm.selectedDocumentTypes = vm.approval.selected_document_types;
            }
        });
    },
    methods: {
        documentTypeSelectorBlur() {
            $('#' + 'documentTypeSelector')
                .val(null)
                .trigger('change');
        },
        /**
         * Initialise the select2 control for adding documents as part of the application
         */
        initSelectDocument: function () {
            let vm = this;

            $(vm.$refs.select_document)
                .select2({
                    dropdownParent: $('#proposedIssuanceApproval .modal'),
                    theme: 'bootstrap-5',
                    allowClear: true,
                    placeholder: 'Add a document',
                    multiple: false,
                    templateSelection: function (data) {
                        // Add custom styling to the <option> tag for the selected option or placeholder

                        if (data.id === '') {
                            if (vm.selectedDocumentTypes.length == 0) {
                                return $(
                                    '<div style="color: grey;">Add a document</div>'
                                );
                            } else {
                                return $(
                                    '<div style="color: grey;">Add another document</div>'
                                );
                            }
                        }
                        return $('<div">' + data.text + '</div>');
                    },
                    templateResult: function (result) {
                        // Add custom styling to the selection dropdown options

                        if (!result.id) {
                            return $(
                                '<div style="color: grey;">' +
                                    result.text +
                                    '</div>'
                            );
                        } else {
                            return $('<div>' + result.text + '</div>');
                        }
                    },
                })
                .on('select2:select', function (e) {
                    var selected = $(e.currentTarget);
                    // Check if user can add documents
                    if (vm.canChangeDocuments) {
                        let added = vm.updateSelectedDocumentTypes(
                            selected.val()
                        );
                        if (added) {
                            // If a new item has been added, clear the select2 field. If an existing
                            // item has been selected, show it as selected so it can be deleted.
                            console.log('added');
                            vm.documentTypeSelectorBlur();
                        }
                    }
                })
                .on('select2:unselecting', function () {
                    var self = $(this);
                    setTimeout(() => {
                        self.select2('close');
                    }, 0);
                })
                .on('select2:unselect', function (e) {
                    // Check if user can change documents
                    if (vm.canChangeDocuments) {
                        let unselected_id = e.params.data.id;
                        // Remove the unselected item from the list of selected items
                        vm.updateSelectedDocumentTypes(unselected_id, true);
                        vm.documentTypeSelectorBlur();
                    }
                });
        },
        /**
         * Update selected items from multi-select document type-dropdown.
         * @param {int} ids The group id
         * @param {Boolean} remove Whether to remove that document type from the list of selected types.
         */
        updateSelectedDocumentTypes(id, remove) {
            let list = updateIdListFromAvailable(
                id,
                this.selectedDocumentTypes,
                this.availableDocumentTypes,
                remove
            );
            if (list) {
                this.selectedDocumentTypes = list;
            } else {
                return false;
            }
        },
    },
};
</script>
