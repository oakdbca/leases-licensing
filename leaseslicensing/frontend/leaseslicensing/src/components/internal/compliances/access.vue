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
                        <div class="mb-1 fw-bold">Status</div>
                        <div>{{ compliance.processing_status_display }}</div>
                    </div>
                    <div class="card-body card-collapse border-top">
                        <div class="mb-1 fw-bold">Currently assigned to
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
                        <a v-if="showAssignToMeButton && !canViewonly && check_assessor()" @click.prevent="assignMyself()"
                            class="float-end mb-2" role="button">Assign to
                            me</a>
                    </div>

                    <div v-if="compliance.assigned_to" class="card-body border-top">
                        <div class="mb-1 fw-bold">Invite Referee</div>
                        <div class="mb-3">
                            <select ref="referees" class="form-select">
                            </select>
                            <template v-if='!sendingReferral'>
                                <template v-if="selected_referral">
                                    <label class="control-label pull-left" for="Name">Comments</label>
                                    <textarea class="form-control comments_to_referral" name="name"
                                        v-model="referral_text"></textarea>
                                    <div class="text-end">
                                        <a @click.prevent="sendReferral()" class="actionBtn" role="button">Send</a>
                                    </div>
                                </template>
                            </template>
                            <template v-else>
                                <span @click.prevent="sendReferral()" disabled class="actionBtn text-primary pull-right">
                                    Sending Referral&nbsp;
                                    <i class="fa fa-circle-o-notch fa-spin fa-fw"></i>
                                </span>
                            </template>
                        </div>
                    </div>

                    <div v-if="compliance.assigned_to && compliance.latest_referrals && compliance.latest_referrals.length > 0"
                        class="card-body border-top">
                        <div class="col-sm-12">
                            <div class="fw-bold mb-1">Recent Referrals <small class="text-secondary fw-lighter">(Showing
                                    {{ compliance.latest_referrals.length }} of {{ compliance.referrals.length }})</small>
                            </div>
                            <table class="table table-sm table-hover table-referrals">
                                <thead>
                                    <tr>
                                        <th>Referee</th>
                                        <th>Status</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="r in compliance.latest_referrals">
                                        <td class="truncate-name">
                                            {{ r.referee_obj.first_name }} {{ r.referee_obj.last_name }}
                                        </td>
                                        <td>
                                            {{ r.processing_status_display }}
                                        </td>
                                        <td class="text-center">
                                            <template
                                                v-if="constants.REFERRAL_STATUS.PROCESSING_STATUS_WITH_REFERRAL.ID == r.processing_status">
                                                <a @click.prevent="remindReferral.bind(this)(referrals_api_endpoint, r.id, r.referee_obj['fullname'])"
                                                    role="button" data-bs-toggle="popover" data-bs-trigger="hover focus"
                                                    :data-bs-content="'Send a reminder to ' + r.referee_obj['fullname']"
                                                    data-bs-placement="bottom"><i class="fa fa-bell text-warning"
                                                        aria-hidden="true"></i>
                                                </a>
                                                <a @click.prevent="recallReferral.bind(this)(referrals_api_endpoint, r.id, r.referee_obj['fullname'])"
                                                    role="button" data-bs-toggle="popover" data-bs-trigger="hover focus"
                                                    :data-bs-content="'Recall the referral request sent to ' + r.referee_obj['fullname']"
                                                    data-bs-placement="bottom"><i class="fa fa-times-circle text-danger"
                                                        aria-hidden="true"></i>
                                                </a>
                                            </template>
                                            <template v-else>
                                                <small><a
                                                        @click.prevent="resendReferral.bind(this)(referrals_api_endpoint, r.id, r.referee_obj['fullname'])"
                                                        role="button" data-bs-toggle="popover" data-bs-trigger="hover focus"
                                                        :data-bs-content="'Resend this referral request to ' + r.referee_obj['fullname']"><i
                                                            class="fa fa-envelope text-primary" aria-hidden="true"></i>
                                                    </a></small>
                                            </template>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                            <MoreReferrals ref="more_referrals" @switchStatus="switchStatus" :canAction="true"
                                :isFinalised="isFinalised" :referral_url="referralListURL"
                                :api_endpoint="referrals_api_endpoint" />
                        </div>
                    </div>

                    <div class="card-body border-top" v-if="canViewActions">
                        <div class="mb-1 fw-bold">Actions</div>
                        <div class="action-buttons">
                            <button class="btn btn-primary mb-2" @click.prevent="amendmentRequest()">Request
                                Amendment</button>
                            <button class="btn btn-primary" @click.prevent="acceptCompliance()">Approve</button><br />
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
                                    <CollapsibleFilters v-if="compliance.assessment" :collapsed="!canEditComments"
                                        component_title="Assessor comments" ref="collapsible_filters"
                                        @created="collapsible_component_mounted" class="mb-3">
                                        <div class="container px-3">
                                            <div class="row mb-3 mt-3">
                                                <div class="col">
                                                    <div class="form-floating">
                                                        <textarea class="form-control"
                                                            v-model="compliance.assessment.assessor_comment" placeholder=""
                                                            id="assessor_comment" :disabled="!canEditComments" />
                                                        <label for="assessor_comment">Assessor Comments</label>
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="row mb-3 mt-3">
                                                <div class="col">
                                                    <div class="form-floating">
                                                        <textarea class="form-control"
                                                            v-model="compliance.assessment.deficiency_comment"
                                                            placeholder="" id="deficiency_comment"
                                                            :disabled="!canEditComments" />
                                                        <label for="deficiency_comment">Deficiency Comments</label>
                                                    </div>
                                                </div>
                                            </div>
                                            <template v-for="referral in compliance.referrals ">
                                                <div v-if="referral.processing_status != constants.REFERRAL_STATUS.PROCESSING_STATUS_RECALLED.ID"
                                                    class="row mb-3 mt-3" :key="referral.id">
                                                    <div class="col">
                                                        <div class="form-floating">
                                                            <textarea class="form-control referral-comment"
                                                                :id="'comment_map_' + referral.id"
                                                                :disabled="referral.referral !== profile.id"
                                                                v-model="referral.comment_map" />
                                                            <label :for="'comment_map_' + referral.id">Referral Comment by
                                                                <span class="fw-bold">{{
                                                                    referral.referee_obj.fullname }}</span></label>
                                                        </div>
                                                    </div>
                                                </div>
                                            </template>
                                        </div>
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
import MoreReferrals from '@common-utils/more_referrals.vue'
import FormSection from "@/components/forms/section_toggle.vue"
import CollapsibleFilters from '@/components/forms/collapsible_component.vue'
import ApprovalsTable from "@/components/common/table_approvals.vue"
import { remindReferral, recallReferral, resendReferral } from '@/components/common/workflow_functions.js'

import {
    api_endpoints,
    constants,
    helpers,
}
    from '@/utils/hooks'
import Swal from 'sweetalert2'
export default {
    name: 'complianceAccess',
    data() {
        let vm = this;
        return {
            constants: constants,
            referrals_api_endpoint: api_endpoints.compliance_referrals,
            loading: [],
            loadRelatedItems: false,
            profile: {},
            compliance: null,
            DATE_FORMAT: 'DD/MM/YYYY',
            members: [],
            sendingReferral: false,
            selected_referral: null,
            referral_text: '',
            // Filters
            logs_url: helpers.add_endpoint_json(api_endpoints.compliances, vm.$route.params.compliance_id + '/action_log'),
            comms_url: helpers.add_endpoint_json(api_endpoints.compliances, vm.$route.params.compliance_id + '/comms_log'),
            comms_add_url: helpers.add_endpoint_json(api_endpoints.compliances, vm.$route.params.compliance_id + '/add_comms_log'),
            remindReferral: remindReferral,
            recallReferral: recallReferral,
            resendReferral: resendReferral,
        }
    },
    components: {
        ApprovalsTable,
        CommsLogs,
        ComplianceAmendmentRequest,
        FormSection,
        CollapsibleFilters,
        MoreReferrals,
    },
    computed: {
        isLoading: function () {
            return this.loading.length > 0;
        },
        referralListURL: function () {
            return this.compliance ? api_endpoints.compliance_referrals + 'datatable_list/?compliance_id=' + this.compliance.id : '';
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
        canEditComments: function () {
            return constants.COMPLIANCE_PROCESSING_STATUS.WITH_ASSESSOR.ID == this.compliance.processing_status;
        },
        isFinalised: function () {
            return this.compliance && [
                constants.COMPLIANCE_PROCESSING_STATUS.APPROVED.ID,
                constants.COMPLIANCE_PROCESSING_STATUS.DISCARDED.ID
            ].includes(this.compliance.processing_status);
        },
        canViewActions: function () {
            return this.profile.is_assessor && constants.COMPLIANCE_PROCESSING_STATUS.WITH_ASSESSOR.ID == this.compliance.processing_status && this.profile.id == this.compliance.assigned_to
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
        sendReferral: async function () {
            let vm = this
            swal.fire({
                title: "Send Referral",
                text: "Are you sure you want to send to referral?",
                icon: "warning",
                showCancelButton: true,
                confirmButtonText: 'Send Referral',
                reverseButtons: true,
                buttonsStyling: false,
                customClass: {
                    confirmButton: 'btn btn-primary',
                    cancelButton: 'btn btn-secondary me-2'
                }
            }).then(async result => {
                if (result.isConfirmed) {
                    // When Yes
                    await vm.performSendReferral()
                }
            })
        },
        performSendReferral: async function () {
            let vm = this
            let my_headers = { 'Accept': 'application/json', 'Content-Type': 'application/json' }

            vm.sendingReferral = true;
            await fetch(`/api/compliances/${this.compliance.id}/`, {
                method: 'PUT',
                headers: my_headers,
                body: JSON.stringify(vm.compliance),
            }).then(async response => {
                if (!response.ok) {
                    return await response.json().then(json => {
                        throw new Error(json);
                    });
                } else {
                    return await response.json();
                }
            }).then(async () => {
                return fetch(helpers.add_endpoint_json(api_endpoints.compliances, (vm.compliance.id + '/assessor_send_referral')), {
                    method: 'POST',
                    headers: my_headers,
                    body: JSON.stringify({ 'email': vm.selected_referral, 'text': vm.referral_text }),
                });
            }).then(async response => {
                if (!response.ok) {
                    return await response.json().then(json => {
                        console.log('json', json)
                        throw new Error(JSON.stringify(json));
                    });
                } else {
                    return await response.json();
                }
            }).then(async response => {
                console.log('settings updated compliance from response')
                vm.compliance = Object.assign({}, response); // 'with_referral'
            }).catch(error => {
                let errorText = '';
                try {
                    // console.log(`error type. ${typeof error}`);
                    // console.log(`Error sending referral. ${error}`);
                    // console.log(`${error.type}`);
                    // console.log(`${JSON.stringify(error, Object.getOwnPropertyNames(error))}`);
                    // console.log(`${JSON.parse(error.message).type}`);

                    error = JSON.parse(error.message);
                    console.log(`error type. ${typeof error}`);
                    errorText = helpers.formatErrorV2(error);
                    console.log(`errorText type. ${typeof errorText}`);

                } catch (e) {
                    errorText = error.message;
                }
                swal.fire({
                    title: "Failed to send referral.",
                    html: `${errorText}`,
                    icon: "warning",
                    customClass: 'swal-wide',
                })
            }).finally(() => {
                vm.sendingReferral = false;
                vm.selected_referral = '';
                vm.referral_text = '';
                $(vm.$refs.referees).val(null).trigger('change');
            });
        },
        initialiseSelects: function (reinit = false) {
            let vm = this;
            if (reinit) {
                $(vm.$refs.referees).data('select2') ? $(vm.$refs.referees).select2('destroy') : '';
            }
            $(vm.$refs.referees).select2({
                minimumInputLength: 2,
                "theme": "bootstrap-5",
                allowClear: true,
                placeholder: "Search Referee by Email",
                ajax: {
                    url: api_endpoints.users + 'get_referees/',
                    dataType: 'json',
                    data: function (params) {
                        var query = {
                            term: params.term,
                            type: 'public',
                        }
                        return query;
                    },
                },

            })
                .on("select2:select", function (e) {
                    let data = e.params.data.id;
                    vm.selected_referral = data;
                })
                .on("select2:unselect", function (e) {
                    var selected = $(e.currentTarget);
                    vm.selected_referral = null;
                })
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
        switchStatus: function (new_processing_status) {
            const requestOptions = {
                method: 'POST',
                body: JSON.stringify({ 'status': new_processing_status }),
            };
            fetch(helpers.add_endpoint_json(api_endpoints.compliances, (this.compliance.id + '/switch_status')), requestOptions)
                .then(async response => {
                    if (!response.ok) {
                        return await response.json().then(json => { throw new Error(json); });
                    } else {
                        return await response.json();
                    }
                })
                .then(data => {
                    this.compliance = Object.assign({}, data);
                    this.$nextTick(() => {
                        this.initialiseSelects();
                        // this.updateAssignedOfficerSelect();
                    });
                })
                .catch(error => {
                    swal.fire({
                        title: 'Compliance Error',
                        text: error,
                        icon: 'error'
                    });
                });
        },
        fetchCompliance: function (compliance_id) {
            let vm = this;
            fetch(helpers.add_endpoint_json(api_endpoints.compliances, compliance_id + '/internal_compliance')).then(async response => {
                if (!response.ok) {
                    return await response.text().then(text => {
                        swal.fire({
                            title: 'Compliance Error',
                            text: text,
                            icon: 'error'
                        })
                    });
                } else {
                    return await response.json();
                }
            })
                .then(async data => {
                    vm.compliance = Object.assign({}, data);
                    vm.members = vm.compliance.allowed_assessors;
                    this.$nextTick(() => {
                        $("textarea").each(function (textarea) {
                            if ($(this)[0].scrollHeight > 70) {
                                $(this).height($(this)[0].scrollHeight - 30);
                            }
                        });
                        this.initialiseSelects();
                        this.initialisePopovers();
                    });
                })
                .catch(error => {
                    swal.fire({
                        title: 'Compliance Error',
                        text: constants.ERRORS.NETWORK_ERROR,
                        icon: 'error'
                    })
                });
        },
        initialisePopovers: function () {
            var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
            var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
                return new bootstrap.Popover(popoverTriggerEl)
            })
        },
    },
    beforeRouteEnter: function (to, from, next) {
        next(vm => {
            vm.fetchCompliance(to.params.compliance_id);
        })
    },
    created: function () {
        this.fetchProfile();
        if (!this.compliance) {
            this.fetchCompliance(this.$route.params.compliance_id);
        }
    },
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
