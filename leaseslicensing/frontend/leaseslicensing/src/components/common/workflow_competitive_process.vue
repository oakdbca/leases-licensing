<template>
    <div class="card card-default">
        <div class="card-header">
            Workflow
        </div>
        <div v-if="competitive_process" class="card-body card-collapse">
            <div class="row">
                <div class="col-sm-12">
                    <strong>Status</strong><br/>
                    {{ competitive_process.status }}
                </div>
                <div v-if="!finalised" class="col-sm-12">
                    <div class="col-sm-12">
                        <div class="separator"></div>
                    </div>
                    <strong>Currently assigned to</strong><br/>
                    <div class="form-group">
                        <select
                            ref="assigned_officer"
                            :disabled="elementDisabled"
                            class="form-control"
                            v-model="assigned_officer_id"
                            @change="assignTo()"
                        >
                            <option v-for="member in competitive_process.allowed_editors" :value="member.id" :key="member.id">{{ member.first_name }} {{ member.last_name }}</option>
                        </select>
                        <div class="text-end">
                            <a v-if="canAssess &&
                                    competitive_process.assigned_officer != competitive_process.accessing_user.id &&
                                    !elementDisabled"
                                @click.prevent="assignRequestUser()" class="actionBtn pull-right">Assign to me</a>
                        </div>
                    </div>
                </div>

                <div v-if="display_actions">
                    <div class="col-sm-12">
                        <div class="separator"></div>
                    </div>

                    <div>
                        <strong>Action</strong>
                    </div>

                    <template v-for="configuration in configurations_for_buttons" :key="configuration.key">
                        <button
                            v-if="configuration.function_to_show_hide()"
                            class="btn btn-primary w-75 my-1"
                            @click.prevent="configuration.function_when_clicked"
                            :disabled="configuration.function_to_disable()"
                        >{{ configuration.button_title }}</button>
                    </template>
                </div>

            </div>
        </div>
    </div>
</template>

<script>
import { api_endpoints, helpers, constants } from '@/utils/hooks'

export default {
    name: 'Workflow',
    data: function() {
        let vm = this;

        return {
            showingProposal: false,
            showingRequirements: false,

            "loading": [],

            department_users : [],
            configurations_for_buttons: [
                {
                    'key': 'complete',
                    'button_title': 'Complete',
                    'function_when_clicked': vm.issueComplete,
                    'function_to_show_hide': () => {
                        return vm.user_is_eligible(this.action_roles("complete"))
                    },
                    'function_to_disable': () => {
                        return this.elementDisabled;
                    }
                },
                {
                    'key': 'discard',
                    'button_title': 'Discard',
                    'function_when_clicked': vm.issueDiscard,
                    'function_to_show_hide': () => {
                        return vm.user_is_eligible(this.action_roles("discard"))
                    },
                    'function_to_disable': () => {
                        return this.elementDisabled;
                    }
                },
                {
                    'key': 'unlock',
                    'button_title': 'Unlock',
                    'function_when_clicked': vm.issueUnlock,
                    'function_to_show_hide': () => {
                        return vm.user_is_eligible(this.action_roles("unlock"))
                    },
                    'function_to_disable': () => {
                        // Disable Unlock button only on processing|discarded|finalised,
                        // but not on completed|declined
                        return this.processing || this.discarded || this.finalised;
                    }
                },
            ]
        }
    },
    props: {
        competitive_process: {
            type: Object,
            default: null,
        },
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
        finalised: {
            type: Boolean,
            default: false,
        },
        canAction: {
            type: Boolean,
            default: false,
        },
        canAssess: {
            type: Boolean,
            default: false,
        },
        can_user_edit: {
            type: Boolean,
            default: false,
        },
        //proposed_decline_status: {
        //    type: Boolean,
        //    default: false,
        //},
    },
    components: {
    },
    computed: {
        proposal_form_url: function() {
            return (this.competitive_process) ? `/api/competitive_process/${this.competitive_process.id}/assessor_save.json` : '';
        },
        canLimitedAction:function(){
            // TOOD: refer to proposal_apiary.vue
            return true
        },
        // show_toggle_proposal: function(){
        //     if(this.competitive_process.status.id == constants.WITH_ASSESSOR_CONDITIONS || this.competitive_process.status.id == constants.WITH_APPROVER || this.isFinalised){
        //         return true
        //     } else {
        //         return false
        //     }
        // },
        // show_toggle_requirements: function(){
        //     if(this.competitive_process.status.id == constants.WITH_APPROVER || this.isFinalised){
        //         return true
        //     } else {
        //         return false
        //     }
        // },
        debug: function(){
            return (this.$route.query.debug && this.$route.query.debug == 'true') ? true : false
        },
        display_actions: function(){
            if (this.debug) return true

            return !this.finalised && this.canAction
        },
        assigned_officer_id: function() {
            if (this.competitive_process.assigned_officer) {
                return this.competitive_process.assigned_officer.id;
            } else {
                return null;
            }
        },
        elementDisabled: function() {
            /** Returns whether an element is disabled
             * True while processing (saving), when discarded, when finalized, or when declined
             * */

            return this.processing || this.discarded || this.finalised || this.declined;
        }
    },
    filters: {
        formatDate: function(data){
            return data ? moment(data).format('DD/MM/YYYY HH:mm:ss'): '';
        }
    },
    methods: {
        user_is_eligible: function(status_roles){
            /** Checks whether the user's roles allow for making certain
             *  actions (e.g. complete, discard) on this competitive process
             *  given the competitive process' current workflow status.
             */

            let status_id = this.competitive_process.status_id;
            if (status_id in status_roles) {
                let eligible_roles = status_roles[status_id];

                // Return true if the accessing user's roles are in the eligible roles
                if (eligible_roles.filter(
                        role => this.competitive_process.accessing_user_roles.includes(
                            role)).length > 0) {
                                return true;
                            }
            }
            return false;
        },
        action_roles: function(action) {
            /** Returns a dictionary of workflow status and user roles to define
             *  when workflow action items (e.g. complete, discard) are usable
             */

            if (["complete", "discard"].includes(action)) {
                // A competitive process editor can complete or discard a competitive process in progress
                return { [constants.COMPETITIVE_PROCESS_STATUS.IN_PROGRESS.ID]:
                                [constants.ROLES.COMPETITIVE_PROCESS_EDITOR.ID,], }
            } else if (action == "unlock") {
                // A competitive process editor can unlock a completed or declined competitive process
                return { [constants.COMPETITIVE_PROCESS_STATUS.COMPLETED_APPLICATION.ID]:
                                [constants.ROLES.COMPETITIVE_PROCESS_EDITOR.ID,],
                            [constants.COMPETITIVE_PROCESS_STATUS.COMPLETED_DECLINED.ID]:
                                [constants.ROLES.COMPETITIVE_PROCESS_EDITOR.ID,],
                            }
            } else {
                console.warn(`action_roles: action ${action} not recognised`);
                return {};
            }
        },
        get_allowed_ids: function(ids){
            let me = this

            let displayable_status_ids = ids.map(a_status => {
                if (a_status.hasOwnProperty('ID'))
                    return a_status.ID
                else if (a_status.hasOwnProperty('id'))
                    return a_status.id
                else if (a_status.hasOwnProperty('Id'))
                    return a_status.Id
                else
                    return a_status
            })

            return displayable_status_ids
        },
        absorb_type_difference: function(processing_status_id){
            let ret_value = ''

            if(processing_status_id.hasOwnProperty('ID'))
                ret_value = processing_status_id.ID
            else if(processing_status_id.hasOwnProperty('id'))
                ret_value = processing_status_id.id
            else if(processing_status_id.hasOwnProperty('Id'))
                ret_value = processing_status_id.Id
            else
                ret_value = processing_status_id.toLowerCase()

            return ret_value
        },
        completeEditing: function(){
        },
        initialiseAssignedOfficerSelect:function(reinit=false){
            let vm = this;
            if (reinit){
                $(vm.$refs.assigned_officer).data('select2') ? $(vm.$refs.assigned_officer).select2('destroy'): '';
            }
            // Assigned officer select
            $(vm.$refs.assigned_officer).select2({
                "theme": "bootstrap-5",
                allowClear: true,
                placeholder:"Select Officer"
            }).
            on("select2:select",function (e) {
                var selected = $(e.currentTarget);
                // Competitve process only has one relevant status, so we can just set the assigned officer
                if (vm.competitive_process.status_id == constants.COMPETITIVE_PROCESS_STATUS.IN_PROGRESS.ID){
                    vm.competitive_process.assigned_officer = selected.val();
                }
                else{
                    console.warn(`Can not change assignment while in status {vm.competitive_process.status}`);
                }
                vm.assignTo();
            }).on("select2:unselecting", function(e) {
                var self = $(this);
                setTimeout(() => {
                    self.select2('close');
                }, 0);
            }).on("select2:unselect",function (e) {
                // Competitve process only has one relevant status, so we can just unset the assigned officer
                if (vm.competitive_process.status_id == constants.COMPETITIVE_PROCESS_STATUS.IN_PROGRESS.ID){
                    vm.competitive_process.assigned_officer = null;
                }
                else{
                    console.warn(`Can not change assignment while in status {vm.competitive_process.status}`);
                }
                vm.assignTo();
            })
        },
        updateAssignedOfficerSelect:function(selected_user){
            let vm = this;

            $(vm.$refs.assigned_officer).val(selected_user)
            $(vm.$refs.assigned_officer).trigger('change')
        },
        refreshFromResponse:function(response){
            let vm = this;
            vm.competitive_process = helpers.copyObject(response.body);
            vm.competitive_process.applicant.address = vm.competitive_process.applicant.address != null ? vm.competitive_process.applicant.address : {};
            vm.$nextTick(() => {
                vm.initialiseAssignedOfficerSelect(true);
                vm.updateAssignedOfficerSelect();
            });
        },
        assignRequestUser: function(){
            this.$emit('assignRequestUser')
        },
        assignTo: function(){
            this.$emit('assignTo')
        },
        issueComplete: function(){
            this.$emit('issueComplete')
        },
        issueDiscard: function(){
            this.$emit('issueDiscard')
        },
        issueUnlock: function(){
            this.$emit('issueUnlock')
        },
    },
    created: function(){
        //this.fetchDeparmentUsers()
    },
    mounted: function(){
        let vm = this
        this.$nextTick(() => {
            vm.initialiseAssignedOfficerSelect()
        })
    },
}
</script>

<style scoped>
.actionBtn {
    cursor: pointer;
}
.separator {
    border: 1px solid;
    margin-top: 15px;
    margin-bottom: 10px;
    width: 100%;
}
</style>
