<template lang="html">
    <div class="">
        <div v-if="debug">components/form.vue</div>
        <div v-if="proposal && show_application_title" id="scrollspy-heading" class="">
            <h3>{{ applicationTypeText }} Application: {{ proposal.lodgement_number }}</h3>
        </div>

        <div class="">
            <ul class="nav nav-pills" id="pills-tab" role="tablist">
                <li class="nav-item mr-1" role="presentation">
                    <button class="nav-link" id="pills-applicant-tab" data-bs-toggle="pill"
                        data-bs-target="#pills-applicant" role="tab" aria-controls="pills-applicant" aria-selected="true">
                        Applicant
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="pills-map-tab" data-bs-toggle="pill" data-bs-target="#pills-map" role="tab"
                        aria-controls="pills-map" aria-selected="false" @click="toggleComponentMapOn">
                        Map
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="pills-details-tab" data-bs-toggle="pill"
                        data-bs-target="#pills-details" role="tab" aria-controls="pills-details" aria-selected="false">
                        Details
                    </button>
                </li>
                <template v-if="show_related_items_tab">
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="pills-related-items-tab" data-bs-toggle="pill"
                            data-bs-target="#pills-related-items" role="tab" aria-controls="pills-related-items"
                            aria-selected="false">
                            Related Items
                        </button>
                    </li>
                </template>
            </ul>
            <div class="tab-content" id="pills-tabContent">
                <div class="tab-pane fade" id="pills-applicant" role="tabpanel" aria-labelledby="pills-applicant-tab">
                    <Applicant v-if="'individual' == proposal.applicant_type" :email_user="email_user_applicant"
                        id="proposalStartApplicant" :readonly="readonly" :collapseFormSections="false"
                        :proposalId="proposal.id" />
                    <OrganisationApplicant v-else :org="proposal.applicant_obj" />
                </div>
                <div class="tab-pane fade" id="pills-map" role="tabpanel" aria-labelledby="pills-map-tab">
                    <FormSection :formCollapse="false" label="Map" Index="proposal_geometry">
                        <slot name="slot_map_checklist_questions"></slot>
                        <ComponentMap ref="component_map" :key="componentMapKey" :is_internal="is_internal"
                            :is_external="is_external" @featuresDisplayed="updateTableByFeatures" :can_modify="can_modify"
                            :display_at_time_of_submitted="show_col_status_when_submitted"
                            @featureGeometryUpdated="featureGeometryUpdated" @popupClosed="popupClosed" :proposal="proposal"
                            :readonly="readonly" @refreshFromResponse="refreshFromResponse" />

                    </FormSection>
                </div>
                <div class="tab-pane fade show active" id="pills-details" role="tabpanel"
                    aria-labelledby="pills-details-tab">
                    <RegistrationOfInterest :proposal="proposal" :readonly="readonly" ref="registration_of_interest"
                        v-if="registrationOfInterest">
                        <template v-slot:slot_proposal_details_checklist_questions>
                            <slot name="slot_proposal_details_checklist_questions"></slot>
                        </template>

                        <template v-slot:slot_proposal_impact_checklist_questions>
                            <slot name="slot_proposal_impact_checklist_questions"></slot>
                        </template>
                    </RegistrationOfInterest>

                    <LeaseLicence :proposal="proposal" :readonly="readonly" ref="lease_licence" v-if="leaseLicence">
                    </LeaseLicence>

                    <FormSection label="Geospatial Data" Index="other_section">
                        <slot name="slot_other_checklist_questions"></slot>

                        <div class="row mb-3">
                            <div class="col-sm-3">
                                <label class="col-form-label">Identifiers</label>
                            </div>
                            <div class="col-sm-9">
                                <Multiselect v-model="proposal.identifiers" label="name" track-by="id"
                                    placeholder="Start typing to search Identifiers" :options="identifiers"
                                    :hide-selected="true" :multiple="true" :searchable="true" :loading="loadingIdentifiers"
                                    @search-change="ajaxLookupIdentifiers" />
                            </div>
                        </div>

                        <div class="row mb-3">
                            <div class="col-sm-3">
                                <label class="col-form-label">Vestings</label>
                            </div>
                            <div class="col-sm-9">
                                <Multiselect v-model="proposal.vestings" label="name" track-by="id"
                                    placeholder="Start typing to search Vestings" :options="vestings" :hide-selected="true"
                                    :multiple="true" :searchable="true" :loading="loadingVestings"
                                    @search-change="ajaxLookupVestings" />
                            </div>
                        </div>

                        <div class="row mb-3">
                            <div class="col-sm-3">
                                <label class="col-form-label">Feature Names</label>
                            </div>
                            <div class="col-sm-9">
                                <Multiselect v-model="proposal.names" label="name" track-by="id"
                                    placeholder="Start typing to search Feature Names" :options="names"
                                    :hide-selected="true" :multiple="true" :searchable="true" :loading="loadingNames"
                                    @search-change="ajaxLookupNames" />
                            </div>
                        </div>

                        <div class="row mb-3">
                            <div class="col-sm-3">
                                <label class="col-form-label">Legal Acts</label>
                            </div>
                            <div class="col-sm-9">
                                <Multiselect v-model="proposal.acts" label="name" track-by="id"
                                    placeholder="Start typing to search Legal Acts" :options="acts" :hide-selected="true"
                                    :multiple="true" :searchable="true" :loading="loadingActs"
                                    @search-change="ajaxLookupActs" />
                            </div>
                        </div>

                        <div class="row mb-3">
                            <div class="col-sm-3">
                                <label class="col-form-label">Tenures</label>
                            </div>
                            <div class="col-sm-9">
                                <Multiselect v-model="proposal.tenures" label="name" track-by="id"
                                    placeholder="Start typing to search Tenures" :options="tenures" :hide-selected="true"
                                    :multiple="true" :searchable="true" :loading="loadingTenures"
                                    @search-change="ajaxLookupTenures" />
                            </div>
                        </div>

                        <div class="row mb-3">
                            <div class="col-sm-3">
                                <label class="col-form-label">Categories</label>
                            </div>
                            <div class="col-sm-9">
                                <Multiselect v-model="proposal.categories" label="name" track-by="id"
                                    placeholder="Start typing to search Categories" :options="categories"
                                    :hide-selected="true" :multiple="true" :searchable="true" :loading="loadingCategories"
                                    @search-change="ajaxLookupCategories" />
                            </div>
                        </div>

                        <div class="row mb-3">
                            <div class="col-sm-3">
                                <label class="col-form-label">Regions</label>
                            </div>
                            <div class="col-sm-9">
                                <Multiselect v-model="proposal.regions" label="name" track-by="id"
                                    placeholder="Start typing to search Regions" :options="regions" :hide-selected="true"
                                    :multiple="true" :searchable="true" :loading="loadingRegions"
                                    @search-change="ajaxLookupRegions" />
                            </div>
                        </div>

                        <div class="row mb-3">
                            <div class="col-sm-3">
                                <label class="col-form-label">Districts</label>
                            </div>
                            <div class="col-sm-9">
                                <Multiselect v-model="proposal.districts" label="name" track-by="id"
                                    placeholder="Start typing to search Districts" :options="districts"
                                    :hide-selected="true" :multiple="true" :searchable="true" :loading="loadingDistricts"
                                    @search-change="ajaxLookupDistricts" />
                            </div>
                        </div>

                        <div class="row mb-3">
                            <div class="col-sm-3">
                                <label class="col-form-label">LGAs</label>
                            </div>
                            <div class="col-sm-9">
                                <Multiselect v-model="proposal.lgas" label="name" track-by="id"
                                    placeholder="Start typing to search LGAs" :options="lgas" :hide-selected="true"
                                    :multiple="true" :searchable="true" :loading="loadingLGAs"
                                    @search-change="ajaxLookupLGAs" />
                            </div>
                        </div>
                    </FormSection>

                    <FormSection label="Categorisation" Index="categorisation">
                        <div v-if="proposal.site_name || is_internal" class="row mb-3">
                            <div class="col-sm-3">
                                <label class="col-form-label">Site Name</label>
                            </div>
                            <div class="col-sm-9">
                                <input class="form-control" v-model="proposal.site_name" type="text" name="site_name"
                                    id="site_name" :disabled="is_external" />
                            </div>
                        </div>
                        <div class="row mb-3">
                            <div class="col-sm-3">
                                <label class="col-form-label">Groups</label>
                            </div>
                            <div class="col-sm-9">
                                <Multiselect v-model="proposal.groups" label="name" track-by="id"
                                    placeholder="Select Groups" :options="groups" :hide-selected="true" :multiple="true"
                                    :searchable="true" :loading="loadingGroups" />

                            </div>
                        </div>
                    </FormSection>

                    <FormSection label="Deed Poll" Index="deed_poll">
                        <slot name="slot_deed_poll_checklist_questions"></slot>
                        <div class="col-sm-12 section-style">
                            <p>
                                <strong>It is a requirement of all lease and licence holders to sign a deed poll to
                                    release
                                    and indemnify the State of Western Australia.
                                    Please note: electronic or digital signatures cannot be accepted.
                                    <p></p>
                                    The deed poll must be signed and have a witness signature and be dated. Once
                                    signed and
                                    dated, please scan and attach the deed poll below.
                                </strong>
                            </p>

                            <label for="deed_poll_document">Deed poll:</label>
                            <FileField :readonly="readonly" ref="deed_poll_document" name="deed_poll_document"
                                id="deed_poll_document" :isRepeatable="true" :documentActionUrl="deedPollDocumentUrl"
                                :replace_button_by_text="true" />
                        </div>
                    </FormSection>

                    <template v-if="show_additional_documents_tab">
                        <FormSection label="Additional Documents" Index="additional_documents">
                            <slot name="slot_additional_documents_checklist_questions"></slot>
                        </FormSection>
                    </template>
                </div>

                <!-- Related Items tab is shown on the internal proposal page -->
                <template v-if="show_related_items_tab">
                    <div class="tab-pane fade" id="pills-related-items" role="tabpanel"
                        aria-labelledby="pills-related-items-tab">
                        <slot name="slot_section_related_items"></slot>
                    </div>
                </template>
            </div>
        </div>
    </div>
</template>

<script>
import Profile from '@/components/user/profile.vue'
import Applicant from '@/components/common/applicant.vue'
import OrganisationApplicant from '@/components/common/organisation_applicant.vue'
import FormSection from '@/components/forms/section_toggle.vue'
import RichText from '@/components/forms/richtext.vue'
import FileField from '@/components/forms/filefield_immediate.vue'
import ComponentMap from '@/components/common/component_map.vue'
import RegistrationOfInterest from './form_registration_of_interest.vue'
import LeaseLicence from './form_lease_licence.vue'
import Multiselect from 'vue-multiselect'

import {
    api_endpoints,
    helpers,
    utils
}
    from '@/utils/hooks'
/*
import Confirmation from '@/components/common/confirmation.vue'
*/
export default {
    name: 'ApplicationForm',
    emits: ["refreshFromResponse"],
    props: {
        show_related_items_tab: {
            type: Boolean,
            default: false,
        },
        show_additional_documents_tab: {
            type: Boolean,
            default: false,
        },
        proposal: {
            type: Object,
            required: true
        },
        show_application_title: {
            type: Boolean,
            default: true,
        },
        submitterId: {
            type: Number,
        },
        canEditActivities: {
            type: Boolean,
            default: true
        },
        is_external: {
            type: Boolean,
            default: false
        },
        is_internal: {
            type: Boolean,
            default: false
        },
        is_referral: {
            type: Boolean,
            default: false
        },
        hasReferralMode: {
            type: Boolean,
            default: false
        },
        hasAssessorMode: {
            type: Boolean,
            default: false
        },
        referral: {
            type: Object,
            required: false
        },
        readonly: {
            type: Boolean,
            default: true,
        },
        registrationOfInterest: {
            type: Boolean,
            default: true,
        },
        leaseLicence: {
            type: Boolean,
            default: true,
        },
    },
    data: function () {
        return {
            can_modify: true,
            show_col_status_when_submitted: true,
            componentMapKey: 0,
            /*
            componentMapOn: false,
            */
            values: null,
            profile: {},
            uuid: 0,
            keep_current_vessel: true,
            showPaymentTab: false,
            detailsText: null,
            defaultLocality: {
                id: null,
                proposal_id: this.proposal.id,
                district: null,
                lga: '',
            },
            districts: null,
            lgas: null,
            groups: null,
            api_endpoints: api_endpoints,

            // data for the multiselects
            identifiers: [],
            names: [],
            vestings: [],
            acts: [],
            tenures: [],
            categories: [],
            regions: [],
            districts: [],
            lgas: [],
            groups: [],

            // Loaders for the multiselects
            loadingIdentifiers: false,
            loadingVestings: false,
            loadingNames: false,
            loadingActs: false,
            loadingTenures: false,
            loadingCategories: false,
            loadingRegions: false,
            loadingDistricts: false,
            loadingLGAs: false,
            loadingGroups: false,
        }
    },
    components: {
        RegistrationOfInterest,
        LeaseLicence,
        Applicant,
        OrganisationApplicant,
        Profile,
        FormSection,
        RichText,
        FileField,
        ComponentMap,
        Multiselect,
    },
    computed: {
        email_user_applicant: function () {
            return this.proposal.applicant_obj
        },
        debug: function () {
            if (this.$route.query.debug) {
                return this.$route.query.debug === 'true'
            }
            return false
        },
        proposalId: function () {
            return this.proposal ? this.proposal.id : null;
        },
        deedPollDocumentUrl: function () {
            return helpers.add_endpoint_join(
                api_endpoints.proposal,
                this.proposal.id + '/process_deed_poll_document/'
            )
        },
        supportingDocumentsUrl: function () {
            return helpers.add_endpoint_join(
                api_endpoints.proposal,
                this.proposal.id + '/process_deed_poll_document/'
            )
        },
        profileVar: function () {
            if (this.is_external) {
                return this.profile;
            } else if (this.proposal) {
                return this.proposal.submitter;
            }
        },
        applicantType: function () {
            if (this.proposal) {
                return this.proposal.applicant_type;
            }
        },
        applicationTypeText: function () {
            let text = '';
            if (this.proposal) {
                text = this.proposal.application_type.name_display;
            }
            return text;
        },

    },
    methods: {
        addAnotherLocality: function () {
            this.localities.push(
                Object.assign({}, this.defaultLocality)
            )
        },
        removeLocality: function (locality, index) {
            console.log('removeLocality', locality, index)
            if (locality.id) {
                alert('Remove locality from database');
            }
            this.localities.splice(index, 1)
        },

        incrementComponentMapKey: function () {
            this.componentMapKey++;
        },
        toggleComponentMapOn: function () {
            //this.incrementComponentMapKey()
            //this.componentMapOn = true;
            this.$nextTick(() => {
                this.$refs.component_map.forceMapRefresh();
            });
        },
        updateTableByFeatures: function () {
        },
        featureGeometryUpdated: function () {
        },
        popupClosed: function () {
        },
        populateProfile: function (profile) {
            this.profile = Object.assign({}, profile);
        },
        ajaxLookupIdentifiers: function (query) {
            this.loadingIdentifiers = true;
            utils.fetchKeyValueLookup(api_endpoints.identifiers, query).then(data => {
                this.loadingIdentifiers = false;
                this.identifiers = data;
            });
        },
        ajaxLookupVestings: function (query) {
            this.loadingVestings = true;
            utils.fetchKeyValueLookup(api_endpoints.vestings, query).then(data => {
                this.loadingVestings = false;
                this.vestings = data;
            });
        },
        ajaxLookupNames: function (query) {
            this.loadingNames = true;
            utils.fetchKeyValueLookup(api_endpoints.names, query).then(data => {
                this.loadingNames = false;
                this.names = data;
            });
        },
        ajaxLookupActs: function (query) {
            this.loadingActs = true;
            utils.fetchKeyValueLookup(api_endpoints.acts, query).then(data => {
                this.loadingActs = false;
                this.acts = data;
            });
        },
        ajaxLookupTenures: function (query) {
            this.loadingTenures = true;
            utils.fetchKeyValueLookup(api_endpoints.tenures, query).then(data => {
                this.loadingTenures = false;
                this.tenures = data;
            });
        },
        ajaxLookupCategories: function (query) {
            this.loadingCategories = true;
            utils.fetchKeyValueLookup(api_endpoints.categories, query).then(data => {
                this.loadingCategories = false;
                this.categories = data;
            });
        },
        ajaxLookupRegions: function (query) {
            this.loadingRegions = true;
            utils.fetchKeyValueLookup(api_endpoints.regions, query).then(data => {
                this.loadingRegions = false;
                this.regions = data;
            });
        },
        ajaxLookupDistricts: function (query) {
            this.loadingDistricts = true;
            utils.fetchKeyValueLookup(api_endpoints.districts, query).then(data => {
                this.loadingDistricts = false;
                this.districts = data;
            });
        },
        ajaxLookupLGAs: function (query) {
            this.loadingLGAs = true;
            utils.fetchKeyValueLookup(api_endpoints.lgas, query).then(data => {
                this.loadingLGAs = false;
                this.lgas = data;
            });
        },
        refreshFromResponse: function (data) {
            this.$emit('refreshFromResponse', data);
        }
    },
    created: function () {
        utils.fetchKeyValueLookup(api_endpoints.groups, '').then(data => {
            this.groups = data;
        });
    },
    mounted: function () {
        this.$emit('formMounted')
    }

}
</script>

<style lang="css" scoped>
.question-title {
    padding-left: 15px;
}

.section-style {
    padding-left: 15px;
    margin-bottom: 20px;
}

.list-inline-item {
    padding-right: 15px;
}

.section {
    text-transform: capitalize;
}

.list-group {
    margin-bottom: 0;
}

.fixed-top {
    position: fixed;
    top: 56px;
}

.nav-item {
    margin-bottom: 2px;
}

.nav-item>li>a {
    background-color: yellow !important;
    color: #fff;
}

.nav-item>li.active>a,
.nav-item>li.active>a:hover,
.nav-item>li.active>a:focus {
    color: white;
    background-color: blue;
    border: 1px solid #888888;
}

.admin>div {
    display: inline-block;
    vertical-align: top;
    margin-right: 1em;
}

.nav-pills .nav-link {
    border-bottom-left-radius: 0;
    border-bottom-right-radius: 0;
    border-top-left-radius: 0.5em;
    border-top-right-radius: 0.5em;
    margin-right: 0.25em;
}

.nav-pills .nav-link {
    background: lightgray;
}

.nav-pills .nav-link.active {
    background: gray;
}
</style>
