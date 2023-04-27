<template>
    <div class="container" id="externalDash">
        <div v-if="is_debug">src/components/internal/dashboard.vue</div>
        <ul class="nav nav-pills" id="pills-tab" role="tablist">
            <li class="nav-item">
                <a class="nav-link" id="pills-applications-tab" data-bs-toggle="pill" href="#pills-applications" role="tab"
                    aria-controls="pills-applications" aria-selected="true"
                    @click="tabClicked('applications')">Applications</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" id="pills-competitive-processes-tab" data-bs-toggle="pill"
                    href="#pills-competitive-processes" role="tab" aria-controls="pills-competitive-processes"
                    aria-selected="false" @click="tabClicked('competitive-processes')">Competitive Processes</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" id="pills-map-tab" data-bs-toggle="pill" href="#pills-map" role="tab"
                    aria-controls="pills-map" aria-selected="false" @click="mapTabClicked">Map</a>
            </li>
        </ul>
        <div class="tab-content" id="pills-tabContent">
            <div class="tab-pane active" id="pills-applications" role="tabpanel" aria-labelledby="pills-applications-tab">
                <FormSection :formCollapse="false" label="Applications" Index="applications">
                    <ApplicationsTable ref="applications_table" level="internal"
                        filterApplicationType_cache_name="filterApplicationTypeForApplicationTabley"
                        filterApplicationStatus_cache_name="filterApplicationStatusForApplicationTable"
                        filterApplicationLodgedFrom_cache_name="filterApplicationLodgedFromForApplicationTable"
                        filterApplicationLodgedTo_cache_name="filterApplicationLodgedToForApplicationTable" />
                </FormSection>
                <FormSection :formCollapse="false" label="Applications referred to me" Index="leases_and_licences">
                    <ApplicationsReferredToMeTable ref="applications_referred_to_me_table" v-if="accessing_user"
                        level="internal" :email_user_id_assigned="accessing_user.id"
                        filterApplicationType_cache_name="filterApplicationTypeForApplicationReferredToMeTable"
                        filterApplicationStatus_cache_name="filterApplicationStatusForApplicationReferredToMeTable"
                        filterApplicationLodgedFrom_cache_name="filterApplicationLodgedFromForApplicationReferredToMeTable"
                        filterApplicationLodgedTo_cache_name="filterApplicationLodgedToForApplicationReferredToMeTable" />
                </FormSection>
            </div>
            <div class="tab-pane" id="pills-competitive-processes" role="tabpanel"
                aria-labelledby="pills-competitive-processes-tab">
                <FormSection :formCollapse="false" label="Competitive Processes" Index="competitive_processes">
                    <CompetitiveProcessesTable ref="competitive_processes_table" level="internal" />
                </FormSection>
            </div>
            <div class="tab-pane" id="pills-map" role="tabpanel" aria-labelledby="pills-map-tab">
                <FormSection :formCollapse="false" label="Map" Index="map">
                    <MapComponent v-if="loadMap" ref="component_map_with_filters" level="internal" />
                </FormSection>
            </div>
        </div>
    </div>
</template>

<script>
import FormSection from "@/components/forms/section_toggle.vue"
import ApplicationsTable from "@/components/common/table_proposals"
import ApplicationsReferredToMeTable from "@/components/common/table_proposals"
import CompetitiveProcessesTable from "@/components/common/table_competitive_processes"
import MapComponent from "@/components/common/component_map_with_filters"
import { api_endpoints, helpers } from '@/utils/hooks'

export default {
    name: 'InternalDashboard',
    data() {
        let vm = this;
        return {
            empty_list: '/api/empty_list',
            accessing_user: null,
            loadMap: false,
            //proposals_url: helpers.add_endpoint_json(api_endpoints.proposals,'user_list'),
            //approvals_url: helpers.add_endpoint_json(api_endpoints.approvals,'user_list'),
            //compliances_url: helpers.add_endpoint_json(api_endpoints.compliances,'user_list'),

            proposals_url: api_endpoints.proposals_paginated_external,
            approvals_url: api_endpoints.approvals_paginated_external,
            compliances_url: api_endpoints.compliances_paginated_external,

            system_name: api_endpoints.system_name,
        }
    },
    components: {
        FormSection,
        ApplicationsTable,
        ApplicationsReferredToMeTable,
        CompetitiveProcessesTable,
        MapComponent,
        //WaitingListTable,
        //LicencesAndPermitsTable,
        //CompliancesTable,
        //AuthorisedUserApplicationsTable,
    },
    watch: {

    },
    computed: {
        is_debug: function () {
            return this.$route.query.hasOwnProperty('debug') && this.$route.query.debug == 'true' ? true : false
        },
        is_external: function () {
            return this.level == 'external'
        },
        is_internal: function () {
            return this.level == 'internal'
        },
    },
    methods: {
        tabClicked: function (param) {
            if (param == 'applications') {
                this.$refs.applications_table.adjust_table_width()
                this.$refs.applications_referred_to_me_table.adjust_table_width()
            } else if (param === 'competitive-processes') {
                this.$refs.competitive_processes_table.adjust_table_width()
            }
        },
        mapTabClicked: function () {
            this.loadMap = true;
        },
        set_active_tab: function (tab_href_name) {
            let elem = $('#pills-tab a[href="#' + tab_href_name + '"]')
            let tab = bootstrap.Tab.getInstance(elem)
            if (!tab)
                tab = new bootstrap.Tab(elem)
            tab.show()
        },
        },
    mounted: async function () {
        const res = await fetch('/api/profile');
        const resData = await res.json();
        this.accessing_user = resData
        this.$nextTick(function () {
            chevron_toggle.init();
            this.set_active_tab('pills-applications')
        })
    },
}
</script>

<style lang="css" scoped>
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

.admin>div {
    display: inline-block;
    vertical-align: top;
    margin-right: 1em;
}
</style>
