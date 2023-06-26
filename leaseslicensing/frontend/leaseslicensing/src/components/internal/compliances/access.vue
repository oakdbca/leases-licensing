<template>
    <div class="container" id="internalCompliance">
        <div v-if="compliance" class="row">
            <h3>Compliance: {{ compliance.reference }}</h3>
            <div class="col-md-3">

                <CommsLogs class="mb-3" :comms_url="comms_url" :logs_url="logs_url" :comms_add_url="comms_add_url"
                    :disable_add_entry="false" />

                <div class="card card-default mb-3">
                    <div class="card-header">
                        Workflow
                    </div>
                    <div class="card-body card-collapse">
                        <div class="row">
                            <div class="col-sm-12 mb-2 pb-2 border-bottom">
                                <div class="mb-1"><strong>Status</strong></div>
                                <div>{{ compliance.processing_status }}</div>
                            </div>
                            <div class="col-sm-12 mb-2 pb-2">
                                <div class="mb-1"><strong>Currently assigned to</strong>
                                </div>
                                <select v-show="isLoading" class="form-select">
                                    <option value="">Loading...</option>
                                </select>
                                <select @change="assignTo" :disabled="canViewonly || !check_assessor()" v-if="!isLoading"
                                    class="form-select mb-2" v-model="compliance.assigned_to">
                                    <option value="null">Unassigned</option>
                                    <option v-for="member in compliance.allowed_assessors" :value="member.id">
                                        {{ member.first_name }} {{ member.last_name }}</option>
                                </select>
                                <a v-if="showAssignToMeButton && !canViewonly && check_assessor()"
                                    @click.prevent="assignMyself()" class="btn btn-primary float-end mb-2">Assign to
                                    me</a>
                            </div>
                            <div class="col-sm-12 border-top"
                                v-if="!canViewonly && check_assessor() && profile.id == compliance.assigned_to">
                                <div class="mb-1"><strong>Actions</strong></div>
                                <div class="action-buttons">
                                    <button class="btn btn-primary mb-2" @click.prevent="amendmentRequest()">Request
                                        Amendment</button>
                                    <button class="btn btn-primary"
                                        @click.prevent="acceptCompliance()">Approve</button><br />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-9">
                <div class="row">
                    <div class="col">
                        <ul class="nav nav-pills" id="pills-tab" role="tablist">
                            <li class="nav-item">
                                <a class="nav-link active" id="pills-compliance-tab" data-bs-toggle="pill"
                                    href="#pills-compliance" role="tab" aria-controls="pills-compliance"
                                    aria-selected="true" @click="tabClicked('compliance')">Compliance</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" id="pills-related-items-tab" data-bs-toggle="pill"
                                    href="#pills-related-items" role="tab" aria-controls="pills-related-items"
                                    aria-selected="true" @click="tabClicked('related-items')">Related
                                    Items</a>
                            </li>
                        </ul>

                        <div class="tab-content" id="pills-tabContent">
                            <div class="tab-pane active" id="pills-compliance" role="tabpanel"
                                aria-labelledby="pills-compliance-tab">
                                <FormSection :formCollapse="false" :label="'Compliance ' + compliance.reference"
                                    Index="compliance_with_requirements">
                                    <CollapsibleFilters component_title="Assessor comments" ref="collapsible_filters"
                                        @created="collapsible_component_mounted" class="mb-3">
                                        Todo: Populate with assessment data for this compliance
                                    </CollapsibleFilters>
                                    <div v-if="compliance.approval" class="row mb-3">
                                        <label for="" class="col-sm-3 col-form-label">Approval</label>
                                        <div class="col-sm-9">
                                            <router-link class="form-control-text"
                                                :to="{ name: 'internal-approval-detail', params: { approval_id: compliance.approval } }">{{
                                                    compliance.approval_lodgement_number }}</router-link>
                                        </div>
                                    </div>
                                    <div v-if="compliance.holder" class="row mb-3">
                                        <label for="holder" class="col-sm-3 col-form-label">Holder</label>
                                        <div class="col-sm-9">
                                            <input type="text" class="form-control-plaintext" id="holder" name="holder"
                                                :value="compliance.holder">
                                        </div>
                                    </div>
                                    <div v-if="compliance.due_date" class="row mb-3">
                                        <label for="holder" class="col-sm-3 col-form-label">Due Date</label>
                                        <div class="col-sm-9">
                                            <div class="form-control-text">{{ dueDateFormatted }}</div>
                                        </div>
                                    </div>
                                    <div class="row mb-3">
                                        <label for="" class="col-sm-3 col-form-label">Requirement</label>
                                        <div class="col-sm-9">
                                            <input type="text" id="requirement" name="requirement" readonly
                                                :value="compliance.requirement" class="form-control">
                                        </div>
                                    </div>
                                    <div class="row mb-3">
                                        <label for="details" class="col-sm-3 col-form-label">Details</label>
                                        <div class="col-sm-9">
                                            <textarea disabled class="form-control" id="details" name="details"
                                                v-model="compliance.text"></textarea>
                                        </div>
                                    </div>
                                    <div class="row mb-3">
                                        <label for="" class="col-sm-3 col-form-label">Attachments</label>
                                        <div class="col-sm-9">
                                            <template v-if="compliance.documents && compliance.documents.length">
                                                <ul class="list-group">
                                                    <li v-for="d in compliance.documents" class="list-group-item"><i
                                                            class="fa-solid fa-file me-2"></i> <a :href="d.secure_url"
                                                            target="_blank" class="col-form-label">{{ d.name
                                                            }}</a></li>
                                                </ul>
                                            </template>
                                            <template v-else>
                                                <div class="row">
                                                    <div class="col-form-label">No attachments</div>
                                                </div>
                                            </template>
                                        </div>
                                    </div>
                                </FormSection>
                            </div>
                            <div class="tab-pane" id="pills-related-items" role="tabpanel"
                                aria-labelledby="pills-related-items-tab">
                                <FormSection v-if="loadRelatedItems" :formCollapse="false" label="Related Items"
                                    Index="related-items">
                                    <ApprovalsTable :target_compliance_id="compliance.id" ref="approvals_table"
                                        level="internal" />
                                </FormSection>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <ComplianceAmendmentRequest ref="amendment_request" :compliance_id="compliance.id"
                :compliance_lodgement_number="compliance.lodgement_number" v-if="compliance.id" />
        </div>
        <BootstrapSpinner v-else :loading="true" class="text-primary" />
    </div>
</template>
<script>
import CommsLogs from '@common-utils/comms_logs.vue'
import ComplianceAmendmentRequest from './compliance_amendment_request.vue'
import FormSection from "@/components/forms/section_toggle.vue"
import CollapsibleFilters from '@/components/forms/collapsible_component.vue'
import ApprovalsTable from "@/components/common/table_approvals.vue"

import {
    api_endpoints,
    helpers,
}
    from '@/utils/hooks'
import Swal from 'sweetalert2'
export default {
    name: 'complianceAccess',
    data() {
        let vm = this;
        return {
            loading: [],
            loadRelatedItems: false,
            profile: {},
            compliance: null,
            DATE_FORMAT: 'DD/MM/YYYY',
            members: [],
            // Filters
            logs_url: helpers.add_endpoint_json(api_endpoints.compliances, vm.$route.params.compliance_id + '/action_log'),
            comms_url: helpers.add_endpoint_json(api_endpoints.compliances, vm.$route.params.compliance_id + '/comms_log'),
            comms_add_url: helpers.add_endpoint_json(api_endpoints.compliances, vm.$route.params.compliance_id + '/add_comms_log'),
        }
    },
    components: {
        ApprovalsTable,
        CommsLogs,
        ComplianceAmendmentRequest,
        FormSection,
        CollapsibleFilters,
    },
    computed: {
        isLoading: function () {
            return this.loading.length > 0;
        },
        canViewonly: function () {
            return this.compliance.processing_status == 'Due' || this.compliance.processing_status == 'Future' || this.compliance.processing_status == 'Approved';
        },
        showAssignToMeButton: function () {
            return this.compliance.assigned_to != this.profile.id
        },
        dueDateFormatted: function () {
            return moment(this.compliance.due_date).format(this.DATE_FORMAT);
        },
    },
    methods: {
        collapsible_component_mounted: function () {
            this.$refs.collapsible_filters.show_warning_icon(this.filterApplied)
        },
        commaToNewline(s) {
            return s.replace(/[,;]/g, '\n');
        },
        tabClicked: function (param) {
            if (param == 'related-items') {
                this.loadRelatedItems = true;
                this.$nextTick(() => {
                    this.$refs.approvals_table.adjust_table_width()
                })
            }
        },
        assignMyself: async function () {
            let vm = this;
            this.compliance = Object.assign({}, await helpers.fetchWrapper(helpers.add_endpoint_json(api_endpoints.compliances, (vm.compliance.id + '/assign_request_user'))));
            Swal.fire({
                title: 'Success',
                text: `Compliance ${this.compliance.reference} has been assigned to you`,
                icon: 'success',
                timer: 2000,
                showConfirmButton: false,
            })
        },
        assignTo: async function () {
            let vm = this;
            console.log(vm.compliance.assigned_to)
            if (vm.compliance.assigned_to != 'null') {
                const url = helpers.add_endpoint_json(api_endpoints.compliances, (vm.compliance.id + '/assign_to'));
                const data = { 'user_id': vm.compliance.assigned_to };
                this.compliance = Object.assign({}, await helpers.fetchWrapper(url, 'POST', data));
                let assessor_assigned = this.compliance.allowed_assessors.find(function (assessor) {
                    console.log(assessor.id, vm.compliance.assigned_to)
                    return assessor.id === vm.compliance.assigned_to;
                });
                console.log(assessor_assigned)
                Swal.fire({
                    title: 'Success',
                    text: `Compliance ${this.compliance.reference} has been assigned to ${assessor_assigned.fullname}`,
                    icon: 'success',
                    customClass: 'swal-wide',
                    timer: 2000,
                    showConfirmButton: false,
                })
            }
            else {
                console.log('unassign')
                const url = await helpers.add_endpoint_json(api_endpoints.compliances, (vm.compliance.id + '/unassign'));
                this.compliance = Object.assign({}, await helpers.fetchWrapper(url));
            }
        },
        acceptCompliance: async function () {
            let vm = this;
            await swal.fire({
                title: `Approve Compliance ${vm.compliance.lodgement_number}`,
                text: "Are you sure you want to approve this compliance?",
                icon: "question",
                showCancelButton: true,
                reverseButtons: true,
                confirmButtonText: 'Accept',
                confirmButtonColor: '#226fbb',
                buttonsStyling: false,
                customClass: {
                    confirmButton: 'btn btn-primary',
                    cancelButton: 'btn btn-secondary me-2'
                },
            });
            await helpers.fetchWrapper(helpers.add_endpoint_json(api_endpoints.compliances, (vm.compliance.id + '/accept'))).then(function (response) {
                vm.compliance = Object.assign({}, response);
                Swal.fire({
                    title: 'Success',
                    text: `Compliance ${vm.compliance.reference} has been approved.`,
                    icon: 'success',
                    timer: 2000,
                    showConfirmButton: false,
                })
                vm.$router.push({ name: 'internal-compliances-dash' });
            });
        },
        amendmentRequest: function () {
            this.$refs.amendment_request.amendment.compliance = this.compliance.id;
            this.$refs.amendment_request.isModalOpen = true;
        },
        fetchProfile: async function () {
            this.profile = Object.assign({}, await helpers.fetchWrapper(api_endpoints.profile));
        },
        check_assessor: function () {
            let vm = this;
            var assessor = vm.members.filter(function (elem) {
                return (elem.id == vm.profile.id);
            });
            if (assessor.length > 0)
                return true;
            else
                return false;
        },
        fetchCompliance: function (compliance_id) {
            let vm = this;
            fetch(helpers.add_endpoint_json(api_endpoints.compliances, compliance_id + '/internal_compliance')).then(async response => {
                if (!response.ok) {
                    return await response.text().then(text => { throw new Error(text); });
                } else {
                    return await response.json();
                }
            })
                .then(async data => {
                    vm.compliance = Object.assign({}, data);
                    vm.members = vm.compliance.allowed_assessors;
                })
                .catch(error => {
                    console.log(error);
                    swal.fire({
                        title: 'Compliance Error',
                        text: error,
                        icon: 'error'
                    })
                });
        },
    },
    beforeRouteEnter: function (to, from, next) {
        console.log('beforeRouteEnter')
        next(vm => {
            vm.fetchCompliance(to.params.compliance_id);
        })
    },
    created: function () {
        console.log('created')
        this.fetchProfile();
        if (!this.compliance) {
            this.fetchCompliance(this.$route.params.compliance_id);
        }
    }
}
</script>
<style scoped>
.action-buttons {
    box-sizing: border-box;
    width: 100%;
}

.action-buttons button {
    width: 190px;
}

.form-control-text {
    display: block;
    width: fit-content;
    margin: 0px;
    padding: 0.375em 0 0.375em 0;
    line-height: 1.5;
    height: 100%;
}
</style>
