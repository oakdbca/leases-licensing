<template>
    <FormSection :formCollapse="false" label="Details" index="details">
        <form>
            <div class="row mb-2">
                <label for="trading_name" class="col-md-2 col-form-label">Trading
                    Name</label>
                <div class="col-md-6">
                    <input type="text" class="form-control" id="trading_name" v-model="org.trading_name" disabled>
                </div>
            </div>
            <div class="row mb-2">
                <label for="organisation_abn" class="col-md-2 col-form-label">ABN</label>
                <div class="col-md-6">
                    <input type="text" class="form-control" id="organisation_abn" v-model="org.organisation_abn" disabled>
                </div>
            </div>
            <div class="row mb-2">
                <label for="organisation_email" class="col-md-2 col-form-label">Email</label>
                <div class="col-md-6">
                    <input type="text" class="form-control" id="organisation_email" v-model="org.organisation_email"
                        disabled>
                </div>
            </div>
            <div class="row mb2">
                <div class="col">
                    <a role="button" :href="'/external/organisations/manage/' + org.id" class="btn btn-primary float-end"><i
                            class="fa fa-external-link" aria-hidden="true"></i> Update
                        Organisation Details</a>
                </div>
            </div>
        </form>
    </FormSection>
    <FormSection v-if="orgHasAddress" :formCollapse="true" label="Address Details" index="addressdetails">
        <form>
            <div class="row mb-2">
                <label for="" class="col-sm-2 col-form-label">Street</label>
                <div class="col-sm-6">
                    <input type="text" class="form-control" name="street" v-model="org.address.line1">
                </div>
            </div>
            <div class="row mb-2">
                <label for="" class="col-sm-2 col-form-label">Town/Suburb</label>
                <div class="col-sm-6">
                    <input type="text" class="form-control" name="surburb" v-model="org.address.locality">
                </div>
            </div>
            <div class="row mb-2">
                <label for="" class="col-sm-2 col-form-label">State</label>
                <div class="col-sm-2">
                    <input type="text" class="form-control" name="country" v-model="org.address.state">
                </div>
                <label for="" class="col-sm-2 col-form-label">Postcode</label>
                <div class="col-sm-2">
                    <input type="text" class="form-control" name="postcode" v-model="org.address.postcode">
                </div>
            </div>
            <div class="row mb-2">
                <label for="" class="col-sm-2 col-form-label">Country</label>
                <div class="col-sm-4">
                    <select class="form-control" name="country" v-model="org.address.country">
                        <option v-for="c in countries" :value="c.alpha2Code">{{
                            c.name }}</option>
                    </select>
                </div>
            </div>
        </form>
    </FormSection>
</template>

<script>

import { api_endpoints, constants, helpers } from '@/utils/hooks'

export default {
    name: 'OrganisationApplicant',
    props: {
        org: {
            type: Object,
            default: null
        },
    },
    data() {
        let vm = this;
        return {
            loading: [],
            countries: [],
        }
    },
    computed: {
        isLoading: function () {
            return this.loading.length == 0;
        },
        formattedABN: function () {
            if (this.org.organisation_abn == null || this.org.organisation_abn == '') {
                return ''
            }
            return helpers.formatABN(this.org.organisation_abn)
        },
        orgHasAddress: function () {
            return this.org && this.org.address && Object.keys(this.org.address).length !== 0
        }
    },
    methods: {

    },
    created: function () {

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

.discount {
    width: 100px;
}

.row-waiver {
    height: 32px;
}

.badge {
    cursor: pointer;
}
</style>
