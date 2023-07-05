<template lang="html">
    <div class="container m-0 p-0">
        <div class="row">
            <div class="col-md-12" id="approval-details">
                <FormSection
                    :formCollapse="false"
                    :label="label"
                    Index="fs-details-details"
                >
                    <div class="container">
                        <div class="row">
                            <div class="col-6">
                                <form
                                    v-if="approval_details.approval_type"
                                    class="form-horizontal mb-2"
                                >
                                    <div class="mb-3 row">
                                        <label
                                            for="txt-approval-type"
                                            class="col-6 col-form-label"
                                            >Approval Type</label
                                        >
                                        <div class="col-6">
                                            <input
                                                type="text"
                                                class="form-control"
                                                name="ApprovalType"
                                                id="txt-approval-type"
                                                :readonly="true"
                                                v-model="
                                                    approval_details.approval_type
                                                "
                                            />
                                        </div>
                                    </div>
                                </form>
                            </div>

                            <div class="col-6">
                                <form
                                    v-if="approval_details.licence_document"
                                    class="form-horizontal mb-2"
                                >
                                    <div class="mb-3 row">
                                        <label
                                            for="txt-license-document"
                                            class="col-6 col-form-label"
                                            >{{
                                                approval_details.approval_type
                                            }}</label
                                        >

                                        <div class="col-6">
                                            <span
                                                v-if="
                                                    approval_details.licence_document.endsWith(
                                                        '.pdf'
                                                    )
                                                "
                                                class="fa fa-file-pdf"
                                                style="color: red"
                                            >
                                                &nbsp;
                                            </span>
                                            <span
                                                v-else
                                                class="fa fa-file"
                                                style="color: red"
                                            >
                                                &nbsp;
                                            </span>
                                            <a
                                                target="_blank"
                                                :href="
                                                    approval_details.licence_document
                                                "
                                                id="txt-license-document"
                                                class="form-label pull-left"
                                                >Approval.pdf</a
                                            >
                                        </div>
                                    </div>
                                </form>
                            </div>
                        </div>

                        <form
                            v-if="approval_details.start_date"
                            class="form-horizontal mb-2"
                        >
                            <div class="mb-3 row">
                                <label
                                    for="txt-start-date"
                                    class="col-3 col-form-label"
                                    >Commencement</label
                                >
                                <div class="col-3">
                                    <input
                                        type="text"
                                        class="form-control"
                                        name="StartDate"
                                        id="txt-start-date"
                                        :readonly="true"
                                        v-model="approval_details.start_date"
                                    />
                                </div>
                            </div>
                        </form>

                        <form
                            v-if="approval_details.expiry_date"
                            class="form-horizontal mb-2"
                        >
                            <div class="mb-3 row">
                                <label
                                    for="txt-expiry-date"
                                    class="col-3 col-form-label"
                                    >Expiry</label
                                >
                                <div class="col-3">
                                    <input
                                        type="text"
                                        class="form-control"
                                        name="ExpiryDate"
                                        id="txt-expiry-date"
                                        :readonly="true"
                                        v-model="approval_details.expiry_date"
                                    />
                                </div>
                            </div>
                        </form>

                        <GisDataDetails
                            :selected_data="externalApprovalGisData"
                            :searchable="false"
                            :readonly="true"
                            placeholder="N/A"
                        />
                    </div>
                </FormSection>
            </div>
        </div>
    </div>
</template>
<script>
import FormSection from '@/components/forms/section_toggle.vue'
import GisDataDetails from '@/components/common/gis_data_details.vue'

export default {
    name: 'ApprovalDetails',
    props: {
        approval_details: {
            type: Object,
            default(rawProps) {
                return {}
            },
        },
        label: {
            type: String,
            required: false,
            default: 'Details',
        },
    },
    components: {
        FormSection,
        GisDataDetails,
    },
    computed: {
        externalApprovalGisData() {
            let properties = [
                'regions',
                'districts',
                'lgas',
                'names',
                'categories',
                // 'identifiers',
                // 'vestings',
                // 'acts',
                // 'tenures',
            ]

            if (this.approval_details.gis_data === undefined) return {}

            // Return a GIS data dictionary of only the properties we want
            return Object.fromEntries(
                Object.entries(
                    JSON.parse(JSON.stringify(this.approval_details.gis_data))
                ).filter(([k, v]) => properties.includes(k))
            )
        },
    },
}
</script>
