<template>
<div class="container" id="internalApproval">
    <div class="row">
        <h3>{{ approvalLabel }}: {{ approval.lodgement_number }}</h3>
        <div class="col-md-3">
            <CommsLogs :comms_url="comms_url" :logs_url="logs_url" :comms_add_url="comms_add_url" :disable_add_entry="false"/>
            <div class="row">
                <div class="card card-default">
                    <div class="card-header">
                       Submission
                    </div>
                    <div class="card-body card-collapse">
                        <div class="row">

                            <div class="col-sm-12 top-buffer-s">
                                <strong>Issued on</strong><br/>
                                {{ formatDate(approval.issue_date) }}
                            </div>
                            <div class="col-sm-12 top-buffer-s">
                                <table class="table small-table">
                                    <tr>
                                        <th>Lodgement</th>
                                        <th>Date</th>
                                        <th>Action</th>
                                    </tr>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="card card-default">
                    <div class="card-header">
                        Workflow
                    </div>
                    <div class="card-body card-collapse">
                        <div class="row">
                            <div class="col-sm-12">
                                <strong>Status</strong><br/>
                                {{ approval.status }}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-1"></div>
        <div class="col-md-8">
            <div class="row">
                <div v-if="approval && approval.submitter">
                    <Applicant
                        :email_user="approval.submitter"
                        applicantType="SUB"
                        id="approvalSubmitterDetails"
                        :readonly="true"
                        customerType="holder"
                    />
                </div>
            </div>

            <div class="row">

                <FormSection :formCollapse="false" label="License" Index="oBody">
                    <!-- <CollapsibleFilters component_title="Assessor comments" ref="collapsible_filters" @created="collapsible_component_mounted" class="mb-2">
                    </CollapsibleFilters> -->

                    <div v-if="loading.length == 0" class="card-body" :id="oBody">
                      <form class="form-horizontal" action="index.html" method="post">
                          <div v-if="mooringLicence" class="row mb-3">
                            <label for="" class="col-sm-3 control-label">Mooring</label>
                            <div class="col-sm-6">
                                <textarea disabled class="form-control" name="mooring" rows="1" placeholder="" style="resize: none">{{approval.mooring_licence_mooring}}</textarea>
                            </div>
                          </div>
                          <div class="row mb-3">
                            <label for="issue_date" class="col-sm-3 control-label">Issue Date</label>
                            <div class="col-sm-6">
                                <textarea disabled id="issue_date" class="form-control" name="issue_date" rows="1" placeholder="" style="resize: none">{{ formatDate(approval.issue_date) }}</textarea>
                            </div>
                          </div>
                          <div class="row mb-3">
                            <label for="start_date" class="col-sm-3 control-label" >Start Date</label>
                            <div class="col-sm-6">
                                <textarea disabled id="issue_date" class="form-control" name="start_date" rows="1" placeholder="" style="resize: none">{{ formatDate(approval.start_date) }}</textarea>
                            </div>
                          </div>
                          <div class="row mb-3">
                            <label for="expiry_date" class="col-sm-3 control-label">Expiry Date</label>
                            <div class="col-sm-6">
                                <textarea disabled id="issue_date" class="form-control" name="expiry_date" rows="1" placeholder="" style="resize: none">{{ formatDate(approval.expiry_date) }}</textarea>
                            </div>

                          </div>
                          <div class="row mb-3">
                              <label for="" class="col-sm-3 control-label" >{{ approvalLabel }}</label>
                            <div class="col-sm-4">
                                <!-- <p><a target="_blank" :href="approval.licence_document" class="control-label pull-left">Approval.pdf</a></p> -->
                                <!--p><a :href="'#'+approval.id" class="control-label pull-left" @click="viewApprovalPDF(approval.id, approval.latest_apiary_licence_document)">Approval.pdf</a></p-->
                                <p><a target="_blank" :href="approval.licence_document" class="control-label pull-left">Licence.pdf</a></p>
                            </div>
                          </div>
                          <!--div class="form-group">
                            <label for="" class="col-sm-3 control-label" >Document History</label>
                            <div class="col-sm-4">
                                <div v-for="doc in approval.apiary_licence_document_history">
                                    <p><a target="_blank" :href="doc.url" class="control-label pull-left">{{doc.name}}</a></p>
                                </div>
                            </div>
                          </div-->
                       </form>
                  </div>
                </FormSection>

            </div>
        </div>
    </div>
</div>
</template>
<script>
import $ from 'jquery'
import datatable from '@vue-utils/datatable.vue'
import CommsLogs from '@common-utils/comms_logs.vue'
import Applicant from '@/components/common/applicant.vue'
import FormSection from "@/components/forms/section_toggle.vue"
import { api_endpoints, helpers } from '@/utils/hooks'
//import OnSiteInformation from '@/components/common/apiary/section_on_site_information.vue'
//import TemporaryUse from '@/components/common/apiary/section_temporary_use.vue'
//import ComponentSiteSelection from '@/components/common/apiary/component_site_selection.vue'
//import SectionAnnualRentalFee from '@/components/common/apiary/section_annual_rental_fee.vue'
export default {
    name: 'ApprovalDetail',
    data() {
    let vm = this;
    vm._uid = vm._.uid; // Vue3
    return {
        showExpired: false,
        moorings_datatable_id: 'moorings-datatable-' + vm._uid,
        ml_vessels_datatable_id: 'ml-vessels-datatable-' + vm._uid,
        ml_authorised_users_datatable_id: 'ml-authorised-users-datatable-' + vm._uid,
        loading: [],
        approval: {
            applicant_id: null

        },
        DATE_TIME_FORMAT: 'DD/MM/YYYY HH:mm:ss',
        adBody: 'adBody'+vm._uid,
        pBody: 'pBody'+vm._uid,
        cBody: 'cBody'+vm._uid,
        oBody: 'oBody'+vm._uid,
        org: {
            address: {}
        },

        // Filters
        logs_url: helpers.add_endpoint_json(api_endpoints.approvals,vm.$route.params.approval_id+'/action_log'),
        comms_url: helpers.add_endpoint_json(api_endpoints.approvals,vm.$route.params.approval_id+'/comms_log'),
        comms_add_url: helpers.add_endpoint_json(api_endpoints.approvals,vm.$route.params.approval_id+'/add_comms_log'),
        moorings_datatable_headers: [
                //'Id',
                'Mooring',
                'Sticker',
                'Licensee',
                'Allocated By',
                'Mobile',
                'Email',
            ],

        moorings_datatable_options: {
            autoWidth: false,
            responsive: true,
            columns: [
                {
                    data: "mooring_name",
                },
                {
                    data: "sticker",
                },
                {
                    data: "licensee",
                },
                {
                    data: "allocated_by",
                },
                {
                    data: "mobile",
                },
                {
                    data: "email",
                },
            ],
        },
        ml_vessels_datatable_headers: [
                //'Id',
                'Vessel',
                'Rego No',
                'Sticker',
                'Owner',
                'Mobile',
                'Email',
            ],

        ml_vessels_datatable_options: {
            autoWidth: false,
            responsive: true,
            columns: [
                {
                    data: "vessel_name",
                },
                {
                    data: "rego_no",
                },
                {
                    data: "sticker_numbers",
                },
                {
                    data: "owner",
                },
                {
                    data: "mobile",
                },
                {
                    data: "email",
                },
            ],
        },
        ml_authorised_users_datatable_headers: [
                'Number',
                'Vessel',
                'Holder',
                'Mobile',
                'Email',
                'Status',
            ],

        ml_authorised_users_datatable_options: {
            autoWidth: false,
            responsive: true,
            columns: [
                {
                    data: "lodgement_number",
                },
                {
                    data: "vessel_name",
                },
                {
                    data: "holder",
                },
                {
                    data: "mobile",
                },
                {
                    data: "email",
                },
                {
                    data: "status",
                },
            ],
        },

    }
  },
  watch: {
      showExpired: function(value){
          console.log(value)
          //this.$refs.approvals_datatable.vmDataTable.ajax.reload()
          this.$nextTick(() => {
              this.constructMLAuthorisedUsersTable()
          });
      },
  },
    props: {
        approvalId: {
            type: Number,
        },
    },
  created: async function(){
      //const response = await this.$http.get(helpers.add_endpoint_json(api_endpoints.approvals,this.$route.params.approval_id));
      const response = await fetch(helpers.add_endpoint_json(api_endpoints.approvals,this.$route.params.approval_id))
      const resData = await response.json()
      console.log({resData})
      //this.approval = Object.assign({}, response.body);
      this.approval = Object.assign({}, resData);
      this.approval.applicant_id = resData.applicant_id;
      if (this.approval.submitter.postal_address == null){ this.approval.submitter.postal_address = {}; }
      await this.$nextTick(() => {
          if (this.approval && this.approval.id && this.authorisedUserPermit) {
              this.constructMooringsTable();
          }
          if (this.approval && this.approval.id && this.mooringLicence) {
              this.constructMLVesselsTable();
              this.constructMLAuthorisedUsersTable();
          }
      })
  },
  components: {
        datatable,
        CommsLogs,
        FormSection,
        Applicant,
  },
  computed: {
    isLoading: function () {
      return this.loading.length > 0;
    },
    approvalLabel: function() {
        let description = '';
        if (this.approval && this.approval.approval_type_dict) {
            description = this.approval.approval_type_dict.description;
        } else {
            description = "License"
        }
        return description;
    },
    annualAdmissionPermit: function() {
        let permit = false;
        if (this.approval && this.approval.approval_type_dict && this.approval.approval_type_dict.code === 'aap') {
            permit = true;
        }
        return permit;
    },
    authorisedUserPermit: function() {
        let permit = false;
        if (this.approval && this.approval.approval_type_dict && this.approval.approval_type_dict.code === 'aup') {
            permit = true;
        }
        return permit;
    },
    mooringLicence: function() {
        let permit = false;
        if (this.approval && this.approval.approval_type_dict && this.approval.approval_type_dict.code === 'ml') {
            permit = true;
        }
        return permit;
    },

  },
  methods: {
    formatDate: function(data){
        return data? moment(data).format(this.DATE_TIME_FORMAT): '';
    },
    constructMooringsTable: function() {
        let vm = this;
        this.$refs.moorings_datatable.vmDataTable.clear().draw();

        for (let aum of vm.approval.authorised_user_moorings_detail) {
            this.$refs.moorings_datatable.vmDataTable.row.add(
                {
                    'mooring_name': aum.mooring_name,
                    'sticker': aum.sticker,
                    'licensee': aum.licensee,
                    'allocated_by': aum.allocated_by,
                    'mobile': aum.mobile,
                    'email': aum.email,
                }
            ).draw();
        }
    },
    constructMLVesselsTable: function() {
        let vm = this;
        this.$refs.ml_vessels_datatable.vmDataTable.clear().draw();

        for (let mlv of vm.approval.mooring_licence_vessels_detail) {
            this.$refs.ml_vessels_datatable.vmDataTable.row.add(
                {
                    'vessel_name': mlv.vessel_name,
                    'rego_no': mlv.rego_no,
                    'sticker_numbers': mlv.sticker_numbers,
                    'owner': mlv.owner,
                    'mobile': mlv.mobile,
                    'email': mlv.email,
                }
            ).draw();
        }
    },
    constructMLAuthorisedUsersTable: function() {
        let vm = this;
        this.$refs.ml_authorised_users_datatable.vmDataTable.clear().draw();

        for (let mlau of vm.approval.mooring_licence_authorised_users) {
            if (this.showExpired || (!this.showExpired && ['current'].includes(mlau.status))) {
                this.$refs.ml_authorised_users_datatable.vmDataTable.row.add(
                    {
                        'lodgement_number': mlau.lodgement_number,
                        'vessel_name': mlau.vessel_name,
                        'holder': mlau.holder,
                        'mobile': mlau.mobile,
                        'email': mlau.email,
                        'status': mlau.status,
                    }
                ).draw();
            }
        }
    },

    commaToNewline(s){
        return s.replace(/[,;]/g, '\n');
    },
    viewApprovalPDF: function(id,media_link){
            let vm=this;
            //console.log(approval);
            vm.$http.get(helpers.add_endpoint_json(api_endpoints.approvals,(id+'/approval_pdf_view_log')),{
                })
                .then((response) => {
                    //console.log(response)
                }, (error) => {
                    console.log(error);
                });
            window.open(media_link, '_blank');
    },


  },
  mounted: function () {
  },
}
</script>
<style scoped>
.top-buffer-s {
    margin-top: 10px;
}
.actionBtn {
    cursor: pointer;
}
.hidePopover {
    display: none;
}
</style>
