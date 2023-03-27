<template lang="html">
    <div id="internal-proposal-amend">
        <modal transition="modal fade" @ok="ok()" :okDisabled="disableOkButton" @cancel="cancel()" title="Amendment Request" large>
            <div class="container-fluid">
                <div class="row">
                    <form class="form-horizontal" name="amendForm">
                        <alert :show.sync="showError" type="danger"><strong>{{errorString}}</strong></alert>
                        <div class="col-sm-12">
                            <div class="row">
                                <div class="form-group">
                                    <div class="col-sm-3">
                                        <label class="control-label pull-right"  for="reason_select">Reason</label>
                                    </div>
                                    <div class="col-sm-6">
                                        <select class="form-control" id="reason_select" ref="reason_choices"
                                            @change="onReasonChange" v-model="amendment.reason_id">
                                                <option v-for="r in reason_choices" :value="r.key">{{r.value}}</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="form-group">
                                    <div class="col-sm-3">
                                        <label class="control-label pull-right" for="amendment_text">Details</label>
                                    </div>
                                    <div class="col-sm-6">
                                        <textarea class="form-control" v-model="amendment.text" id="amendment_text"></textarea>
                                    </div>
                                </div>
                            </div>

                            <div class="row">
                                <div class="col-sm-offset-2 col-sm-8">
                                    <div class="form-group">
                                        <div class="input-group date" ref="add_attachments" style="width: 70%;">
                                            <!--FileField ref="filefield" :uploaded_documents="amendment.amendment_request_documents" :delete_url="delete_url" :proposal_id="proposal_id" isRepeatable="true" name="amendment_request_file" @refreshFromResponse="refreshFromResponse"/-->

                                            <!-- false for now 17 May 2021 -->
                                            <FileField v-if="false"
                                                ref="filefield"
                                                :uploaded_documents="amendment.amendment_request_documents"
                                                :delete_url="delete_url"
                                                :proposal_id="proposal.id"
                                                :isRepeatable="true"
                                                name="amendment_request_file"
                                            />
                                        </div>
                                    </div>
                                </div>
                            </div>

                        </div>
                    </form>
                </div>
            </div>
        </modal>
    </div>
</template>

<script>
//import $ from 'jquery'
import modal from '@vue-utils/bootstrap-modal.vue'
import alert from '@vue-utils/alert.vue'
import FileField from '@/components/forms/filefield_immediate.vue'

import {helpers, api_endpoints} from "@/utils/hooks.js"
export default {
    name:'amendment-request',
    components:{
        modal,
        alert,
        FileField,
    },
    props:{
        proposal: {
            type: Object,
            default: null,
        },
        //proposal_id:{
        //    type:Number,
        //},
        is_apiary_proposal:{
            type: Boolean,
            default: false,
        },
    },
    data:function () {
        let vm = this;
        return {
            isModalOpen:false,
            form:null,
            amendment: {
                reason:'',
                reason_id: null,
                amendingProposal: false,
                //proposal: vm.proposal,
                proposal_id: vm.proposal.id,
                num_files: 0,
                input_name: 'amendment_request_doc',
                requirement_documents: [],
            },
            reason_choices: {},
            errors: false,
            errorString: '',
            validation_form: null,
        }
    },
    computed: {
        showError: function() {
            var vm = this;
            return vm.errors;
        },
        delete_url: function() {
            return (this.amendment.id) ? '/api/amendment_request/'+this.amendment.id+'/delete_document/' : '';
        },
        disableOkButton: function() {
            // Disable amendment modal ok-button for as long as no amendment
            // reason has been selected
            return this.amendment.reason_id == null;
        }
    },
    methods:{

        ok:function () {
            let vm =this;
            if($(vm.form).valid()){
                vm.sendData();
            }
        },
        cancel:function () {
            let vm = this;
            vm.close();
        },
        close:function () {
            this.isModalOpen = false;
            this.amendment = {
                reason: '',
                reason_id: null,
                proposal_id: this.proposal.id
            };
            /*
            this.errors = false;
            $(this.$refs.reason).val(null).trigger('change');
            $('.has-error').removeClass('has-error');

            this.validation_form.resetForm();
            */
        },
        onReasonChange: function(e) {
            // Update this proposal's amendment reason on selecting a different reason from the modal
            let vm = this;
            let reason = e.target.innerText;
            let reason_id = e.target.value;

            vm.amendment.reason = reason;
            vm.amendment.reason_id = reason_id;
        },
        fetchAmendmentChoices: async function(){
            try {
                const res = await fetch('/api/amendment_request_reason_choices.json')
                const resData = await res.json()
                this.reason_choices = Object.assign({}, resData);
            } catch (error) {
                console.log(error);
            }
        },
        sendData:async function(){
            this.errors = false;
            try {
                await fetch('/api/amendment_request.json',
                    { body: JSON.stringify(this.amendment),
                        method: 'POST'
                    })
                await new swal(
                     'Sent',
                     'An email has been sent to the applicant with the request to amend this application',
                     'success'
                );
                this.amendingProposal = true;
                this.close();
                /*
                try {
                    const res = await fetch(`/api/proposal/${this.proposal.id}/internal_proposal.json`)
                    const resData = await res.json()
                    await this.$emit('refreshFromResponse', response);
                } catch (error) {
                    console.log(error);
                }
                */
                this.$router.push({ path: '/internal' }); //Navigate to dashboard after creating Amendment request
            } catch (error) {
                console.log(error);
                this.errors = true;
                this.errorString = helpers.apiVueResourceError(error);
                this.amendingProposal = true;
            }
        },
        /*
        addFormValidations: function() {
            let vm = this;
            vm.validation_form = $(vm.form).validate({
                rules: {
                    reason: "required"
                },
                messages: {
                    reason: "field is required",
                },
                showErrors: function(errorMap, errorList) {
                    $.each(this.validElements(), function(index, element) {
                        var $element = $(element);
                        $element.attr("data-original-title", "").parents('.form-group').removeClass('has-error');
                    });
                    // destroy tooltips on valid elements
                    $("." + this.settings.validClass).tooltip("destroy");
                    // add or update tooltips
                    for (var i = 0; i < errorList.length; i++) {
                        var error = errorList[i];
                        $(error.element)
                            .tooltip({
                                trigger: "focus"
                            })
                            .attr("data-original-title", error.message)
                            .parents('.form-group').addClass('has-error');
                    }
                }
            });
       },
       */
       eventListerners:function () {
            let vm = this;

            // Intialise select2
            // $(vm.$refs.reason_choices).select2({
            //     "theme": "bootstrap",
            //     allowClear: true,
            //     placeholder:"Select Reason"
            // }).
            // on("select2:select",function (e) {
            //     var selected = $(e.currentTarget);
            //     vm.amendment.reason = selected.val();
            //     vm.amendment.reason_id = selected.val();
            // }).
            // on("select2:unselect",function (e) {
            //     var selected = $(e.currentTarget);
            //     vm.amendment.reason = selected.val();
            //     vm.amendment.reason_id = selected.val();
            // });
       }
   },
   mounted:function () {
       let vm =this;
       vm.form = document.forms.amendForm;
       vm.fetchAmendmentChoices();
       //vm.addFormValidations();
       this.$nextTick(()=>{
            vm.eventListerners();
        });
    //console.log(validate);
   }
}
</script>

<style lang="css">
</style>
