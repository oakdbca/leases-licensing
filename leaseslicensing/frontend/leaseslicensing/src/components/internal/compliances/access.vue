<template>
    <div class="container" id="internalCompliance">
        <div v-if="compliance" class="row">
            <h3>Compliance with Requirements {{ compliance.reference }}</h3>
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
                            <div class="col-sm-12 mb-2 pb-2 border-bottom">
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
                                    @click.prevent="assignMyself()" class="btn btn-primary float-end mb-2">Assign to me</a>
                            </div>
                            <div class="col-sm-12" v-if="!canViewonly && check_assessor()">
                                <div class="mb-1"><strong>Actions</strong></div>
                                <button class="btn btn-primary mb-2" @click.prevent="amendmentRequest()">Request
                                    Amendment</button>
                                <button class="btn btn-primary" @click.prevent="acceptCompliance()">Approve</button><br />

                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-9">
                <div class="row">
                    <FormSection :formCollapse="false" label="Compliance with Requirements"
                        Index="compliance_with_requirements">
                        <CollapsibleFilters component_title="Assessor comments" ref="collapsible_filters"
                            @created="collapsible_component_mounted" class="mb-3">
                            Todo: Populate with assessment data for this compliance
                        </CollapsibleFilters>

                        <div class="row mb-3">
                            <label for="" class="col-sm-3 col-form-label">Requirement</label>
                            <div class="col-sm-6">
                                <input type="text" readonly :value="compliance.requirement" class="form-control">
                            </div>
                        </div>
                        <div class="row mb-3">
                            <label for="details" class="col-sm-3 col-form-label">Details</label>
                            <div class="col-sm-6">
                                <textarea disabled class="form-control" name="details" v-model="compliance.text"></textarea>
                            </div>
                        </div>
                        <div class="row mb-3">
                            <label for="" class="col-sm-3 col-form-label">Attachments</label>
                            <div class="col-sm-6">
                                <template v-if="compliance.documents && compliance.documents.length">
                                    <div class="row" v-for="d in compliance.documents">
                                        <a :href="d[1]" target="_blank" class="col-form-label">{{ d[0] }}</a>
                                    </div>
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
            </div>
        </div>
        <ComplianceAmendmentRequest ref="amendment_request" :compliance_id="compliance.id" v-if="compliance.id" />
    </div>
</template>
<script>
import datatable from '@vue-utils/datatable.vue'
import CommsLogs from '@common-utils/comms_logs.vue'
import ComplianceAmendmentRequest from './compliance_amendment_request.vue'
import FormSection from "@/components/forms/section_toggle.vue"
import CollapsibleFilters from '@/components/forms/collapsible_component.vue'
//import ResponsiveDatatablesHelper from "@/utils/responsive_datatable_helper.js"
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
            profile: {},
            compliance: {
                //requester: {}
            },
            DATE_TIME_FORMAT: 'DD/MM/YYYY HH:mm:ss',
            members: [],
            // Filters
            logs_url: helpers.add_endpoint_json(api_endpoints.compliances, vm.$route.params.compliance_id + '/action_log'),
            comms_url: helpers.add_endpoint_json(api_endpoints.compliances, vm.$route.params.compliance_id + '/comms_log'),
            comms_add_url: helpers.add_endpoint_json(api_endpoints.compliances, vm.$route.params.compliance_id + '/add_comms_log'),
        }
    },
    watch: {},
    filters: {
        formatDate: function (data) {
            //return data ? moment(data).format('DD/MM/YYYY'): '';
            console.log(data);
            console.log(moment(data).format('DD/MM/YYYY'));
        },
    },
    //   beforeRouteEnter: async function(to, from, next){
    beforeRouteEnter: function (to, from, next) {
        /*
        const res = await fetch(`/api/proposal/${this.$route.params.proposal_id}/internal_proposal.json`);
        const resData = await res.json();
        this.compliance = Object.assign({}, resData);
        */

        const url = helpers.add_endpoint_json(api_endpoints.compliances, to.params.compliance_id + '/internal_compliance');
        fetch(helpers.add_endpoint_json(api_endpoints.compliances, to.params.compliance_id + '/internal_compliance')).then(async response => {
            if (!response.ok) {
                return await response.text().then(text => { throw new Error(text); });
            } else {
                return await response.json();
            }
        })
            .then(async data => {
                next((vm) => {
                    // const data = await response.json();
                    vm.compliance = Object.assign({}, data);
                    vm.members = vm.compliance.allowed_assessors;
                });
            })
            .catch(error => {
                console.log(error);
                swal.fire({
                    title: 'Proposal Error',
                    text: error,
                    icon: 'error'
                })
            });
    },
    components: {
        datatable,
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
        }
    },
    methods: {
        collapsible_component_mounted: function () {
            this.$refs.collapsible_filters.show_warning_icon(this.filterApplied)
        },
        commaToNewline(s) {
            return s.replace(/[,;]/g, '\n');
        },

        assignMyself: async function () {
            let vm = this;
            /*
            const res = await fetch(helpers.add_endpoint_json(api_endpoints.compliances,(vm.compliance.id+'/assign_request_user')));
            const resData = await res.json();
            this.compliance = Object.assign({}, resData);
            */
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
            if (vm.compliance.assigned_to != 'null') {
                const data = { 'user_id': vm.compliance.assigned_to };
                const url = helpers.add_endpoint_json(api_endpoints.compliances, (vm.compliance.id + '/assign_to'));
                /*
                const res = await fetch(helpers.add_endpoint_json(api_endpoints.compliances,(vm.compliance.id+'/assign_to')),{
                    body: JSON.stringify(data),
                    method: 'POST',
                });
                const resData = await res.json();
                this.compliance = Object.assign({}, resData);
                */
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
                /*
                const res = await fetch(helpers.add_endpoint_json(api_endpoints.compliances,(vm.compliance.id+'/unassign')));
                const resData = await res.json();
                this.compliance = Object.assign({}, resData);
                */
                this.compliance = Object.assign({}, await helpers.fetchWrapper(url));
            }
        },
        acceptCompliance: async function () {
            let vm = this;
            await swal.fire({
                //swal({
                title: "Accept Compliance with requirements",
                text: "Are you sure you want to accept this compliance with requirements?",
                icon: "question",
                showCancelButton: true,
                confirmButtonText: 'Accept'
            });
            /*
            const res = await fetch(helpers.add_endpoint_json(api_endpoints.compliances,(vm.compliance.id+'/accept')));
            const resData = await res.json();
            vm.compliance = Object.assign({}, resData);
            */
            this.compliance = Object.assign({}, await helpers.fetchWrapper(helpers.add_endpoint_json(api_endpoints.compliances, (vm.compliance.id + '/accept'))));
        },
        amendmentRequest: function () {
            this.$refs.amendment_request.amendment.compliance = this.compliance.id;
            this.$refs.amendment_request.isModalOpen = true;
        },
        fetchProfile: async function () {
            //const res = await fetch(api_endpoints.profile);
            //const resData = await res.json();
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
    },
    created: function () {
        this.fetchProfile();
    }
}
</script>
