<template>
    <div class="container" id="approvalsDash">
        <ul class="nav nav-pills" id="pills-tab" role="tablist">
            <li class="nav-item">
                <a class="nav-link active" id="pills-approvals-tab" data-bs-toggle="pill" href="#pills-approvals" role="tab"
                    aria-controls="pills-approvals" aria-selected="true" @click="tabClicked('approvals')">Approvals</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" id="pills-map-tab" data-bs-toggle="pill" href="#pills-map" role="tab"
                    aria-controls="pills-map" aria-selected="false" @click="mapTabClicked">Map</a>
            </li>
        </ul>
        <div class="tab-content" id="pills-tabContent">
            <div class="tab-pane active" id="pills-approvals" role="tabpanel" aria-labelledby="pills-approvals-tab">
                <FormSection :formCollapse="false" label="Approvals" Index="approvals">
                    <ApprovalsTable ref="approvals_table" level="internal" :approvalTypeFilter="approvalTypeFilter" />
                </FormSection>
            </div>
            <div class="tab-pane" id="pills-map" role="tabpanel" aria-labelledby="pills-map-tab">
                <FormSection v-if="loadMap" :formCollapse="false" label="Map" Index="map">
                    <MapComponent ref="component_map_with_filters" level="internal" />
                </FormSection>
            </div>
        </div>
    </div>
</template>

<script>
import FormSection from "@/components/forms/section_toggle.vue"
import ApprovalsTable from "@/components/common/table_approvals.vue"
import MapComponent from "@/components/common/component_map_with_filters"

export default {
    name: 'InternalApprovalsDashboard',
    data() {
        let vm = this;
        return {
            approvalTypeFilter: ['ml', 'aap', 'aup'],
            loadMap: false,
        }
    },
    components: {
        FormSection,
        ApprovalsTable,
        MapComponent,
    },
    methods: {
        tabClicked: function (param) {
            if (param == 'approvals') {
                this.$refs.approvals_table.adjust_table_width()
            }
        },
        mapTabClicked: function () {
            console.log(this.$refs.component_map_with_filters);
            this.loadMap = true;
            // this.$nextTick(() => {
            //     this.$refs.component_map_with_filters.forceToRefreshMap()
            // })
        },
    },
}
</script>
