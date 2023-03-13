<template lang="html">
    <div class="container m-0 p-0">
        <div class="row">
            <div class="col-md-12" id="ledgeraccount">
                <FormSection v-if="email_user.personal_details" :formCollapse="true" label="Personal Details" subtitle="" Index="personal-details" >
                    <form>
                        <div class="row mb-2">
                            <div class="col-md-3">
                                <label for="firstName" class="form-label">First Name</label>
                            </div>
                            <div class="col-md-9">
                                <input type="text" class="form-control" id="firstName" name="firstName" v-model="email_user.first_name" :readonly="readonly">
                            </div>
                        </div>
                        <div class="row mb-2">
                            <div class="col-md-3">
                                <label for="lastName" class="form-label">Last Name</label>
                            </div>
                            <div class="col-md-9">
                                <input type="text" class="form-control" id="lastName" name="lastName" v-model="email_user.last_name" :readonly="readonly">
                            </div>
                        </div>
                    </form>
                </FormSection>
                <FormSection v-if="email_user.address_details" :formCollapse="true" label="Address Details" subtitle="" Index="address-details" >
                    <form class="form-horizontal" action="index.html" method="post">
                        <div class="address-box">
                            <div class="form-group">
                                <label for="" class="col-sm-3 control-label">Residential Address</label>
                                <div class="col-sm-6">
                                    <input :readonly="readonly" type="text" class="form-control" id="line1" name="Street" placeholder="" v-model="profile.residential_address.line1">
                                </div>
                            </div>
                            <div class="form-group">
                                <label for="" class="col-sm-3 control-label" >Town/Suburb</label>
                                <div class="col-sm-6">
                                    <input :readonly="readonly" type="text" class="form-control" id="locality" name="Town/Suburb" placeholder="" v-model="profile.residential_address.locality">
                                </div>
                            </div>
                            <div class="form-group">
                                <label for="" class="col-sm-3 control-label">State</label>
                                <div class="col-sm-3">
                                    <input :readonly="readonly" type="text" class="form-control" id="state" name="State" placeholder="" v-model="profile.residential_address.state">
                                </div>
                                <label for="" class="col-sm-1 control-label">Postcode</label>
                                <div class="col-sm-2">
                                    <input :readonly="readonly" type="text" class="form-control" id="postcode" name="Postcode" placeholder="" v-model="profile.residential_address.postcode">
                                </div>
                            </div>
                            <div class="form-group">
                                <label for="" class="col-sm-3 control-label" >Country</label>
                                <div class="col-sm-4">
                                    <select :disabled="readonly" class="form-control" id="country" name="Country" v-model="profile.residential_address.country">
                                        <!--option v-for="c in countries" :value="c.alpha2Code">{{ c.name }}</option-->
                                        <option v-for="c in countries" :value="c.code">{{ c.name }}</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                        <div class="form-group"/>
                            <div class="address-box">
                                <div class="form-group">
                                    <div class="col-sm-3">
                                    </div>
                                    <div class="col-sm-6">
                                    <input :readonly="readonly" type="checkbox" id="postal_same_as_residential" v-model="profile.postal_same_as_residential"/>
                                    <label for="postal_same_as_residential" class="control-label">Same as residential address</label>
                                    </div>
                                </div>
                                <div class="form-group">
                                    <label for="" class="col-sm-3 control-label">Postal Address</label>
                                    <div class="col-sm-6">
                                        <input :readonly="postalAddressReadonly" type="text" class="form-control" id="postal_line1" name="Street" placeholder="" v-model="profile.postal_address.line1">
                                    </div>
                                </div>
                                <div class="form-group">
                                    <label for="" class="col-sm-3 control-label" >Town/Suburb</label>
                                    <div class="col-sm-6">
                                        <input :readonly="postalAddressReadonly" type="text" class="form-control" id="postal_locality" name="Town/Suburb" placeholder="" v-model="profile.postal_address.locality">
                                    </div>
                                </div>
                                <div class="form-group">
                                    <label for="" class="col-sm-3 control-label">State</label>
                                    <div class="col-sm-3">
                                        <input :readonly="postalAddressReadonly" type="text" class="form-control" id="postal_state" name="State" placeholder="" v-model="profile.postal_address.state">
                                    </div>
                                    <label for="" class="col-sm-1 control-label">Postcode</label>
                                    <div class="col-sm-2">
                                        <input :readonly="postalAddressReadonly" type="text" class="form-control" id="postal_postcode" name="Postcode" placeholder="" v-model="profile.postal_address.postcode">
                                    </div>
                                </div>
                                <div class="form-group">
                                    <label for="" class="col-sm-3 control-label" >Country</label>
                                    <div class="col-sm-4">
                                        <select :disabled="postalAddressReadonly" class="form-control" id="postal_country" name="Country" v-model="profile.postal_address.country">
                                            <!--option v-for="c in countries" :value="c.alpha2Code">{{ c.name }}</option-->
                                            <option v-for="c in countries" :value="c.code">{{ c.name }}</option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                       </form>

                </FormSection>
                <FormSection v-if="email_user.contact_details" :formCollapse="true" label="Contact Details" subtitle="" Index="contact-details" >
                    <form>
                        <div class="row mb-2">
                            <div class="col-md-3">
                                <label for="phone" class="form-label">Phone</label>
                            </div>
                            <div class="col-md-9">
                                <input type="text" class="form-control" id="phone" name="phone" v-model="email_user.phone_number" :readonly="readonly">
                            </div>
                        </div>
                        <div class="row mb-2">
                            <div class="col-md-3">
                                <label for="mobile" class="form-label">Mobile</label>
                            </div>
                            <div class="col-md-9">
                                <input type="text" class="form-control" id="mobile" name="mobile" v-model="email_user.mobile_number" :readonly="readonly">
                            </div>
                        </div>
                        <div class="row mb-2">
                            <div class="col-md-3">
                                <label for="email" class="form-label">Email</label>
                            </div>
                            <div class="col-md-9">
                                <input type="text" class="form-control" id="email" name="email" v-model="email_user.email" :readonly="readonly">
                            </div>
                        </div>
                    </form>
                </FormSection>
            </div>
        </div>
    </div>
</template>

<script>
import FormSection from "@/components/forms/section_toggle.vue"

import { api_endpoints, helpers } from '@/utils/hooks'

export default {
    name: 'Applicant',
    props:{
        email_user: {
            type: Object,
            required: true,
        },
        applicantType: {
            type: String,
            required: true,
        },
        customerType: {
            type: String,
            required: false,
        },
        proposalId: {
            type: Number,
        },
    },
    data:function () {
        let vm=this;
        return{
            electoralRollSectionIndex: 'electoral_roll_' + vm._uid,
            silentElector: null,
            readonly: true,
            values:null,
            countries: [],
            showAddressError: false,
            detailsBody: 'detailsBody'+vm._uid,
            addressBody: 'addressBody'+vm._uid,
            contactsBody: 'contactsBody'+vm._uid,
            electoralRollBody: 'electoralRollBody'+vm._uid,
            panelClickersInitialised: false,
            contacts_table_id: vm._uid+'contacts-table',
            contacts_table_initialised: false,
            contacts_options:{
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>"
                },
                responsive: true,
                ajax: {
                    "url": vm.contactsURL,
                    "dataSrc": ''
                },
                columns: [
                    {
                        title: 'Name',
                        mRender:function (data,type,full) {
                            return full.first_name + " " + full.last_name;
                        }
                    },
                    {
                        title: 'Phone',
                        data:'phone_number'
                    },
                    {
                        title: 'Mobile',
                        data:'mobile_number'
                    },
                    {
                        title: 'Fax',
                        data:'fax_number'
                    },
                    {
                        title: 'Email',
                        data:'email'
                    },
                    ],
                    processing: true
            },
            contacts_table: null,
        }
    },
    components: {
        //FileField,
        FormSection,
        //Assessment
    },
    computed:{
        electoralRollDocumentUrl: function() {
            let url = '';
            //if (this.profile && this.profile.id) {
            if (this.proposalId) {
                url = helpers.add_endpoint_join(
                    '/api/proposal/',
                    this.proposalId + '/process_electoral_roll_document/'
                )
            }
            return url;
        },

        postalAddressReadonly: function() {
            /*
            if (this.readonly || this.email_user.postal_same_as_residential) {
                return true;
            }
            */
            return true;
        },
        contactsURL: function(){
            // We don't need anything relating to organisations
            //return this.proposal != null ? helpers.add_endpoint_json(api_endpoints.organisations, this.proposal.org_applicant.id+'/contacts') : '';
            return ''
        },
        customerLabel: function() {
            let label = 'Applicant';
            if (this.customerType && this.customerType === 'holder') {
                label = 'Holder';
            }
            return label;
        },

        //applicantType: function(){
        //    return this.proposal.applicant_type;
        //},
        // hasAssessorMode:function(){
        //     return this.proposal && this.proposal.assessor_mode.has_assessor_mode ? true : false;
        // },
    },
    methods:{
        fetchCountries:async function (){
            try {
                const res = await fetch(api_endpoints.countries);
                const resData = await res.json()
                vm.countries = Object.assign({}, resData);
            } catch (err) {
            }
        },

        initialiseOrgContactTable: function(){
            let vm = this;
            //console.log("i am here")
            //if (vm.proposal && !vm.contacts_table_initialised){
            if (!vm.contacts_table_initialised){
                // We don't need anything relating to organisations
                //vm.contacts_options.ajax.url = helpers.add_endpoint_json(api_endpoints.organisations, vm.proposal.org_applicant.id + '/contacts');
                vm.contacts_table = $('#'+vm.contacts_table_id).DataTable(vm.contacts_options);
                vm.contacts_table_initialised = true;
            }
        },
    },
    mounted: function(){
        console.log("applicant mounted");
        let vm=this;
        this.fetchCountries();
        if (!vm.panelClickersInitialised){
        $('.panelClicker[data-toggle="collapse"]').on('click', function () {
            var chev = $(this).children()[0];
            window.setTimeout(function () {
                $(chev).toggleClass("glyphicon-chevron-down glyphicon-chevron-up");
            },100);
        });
        vm.panelClickersInitialised = true;
        }
        this.$nextTick(() => {
            vm.initialiseOrgContactTable();
        });
        this.silentElector = this.storedSilentElector;
    }
}
</script>
