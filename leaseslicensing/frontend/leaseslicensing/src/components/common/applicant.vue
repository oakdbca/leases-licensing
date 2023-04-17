<template lang="html">
    <div class="container m-0 p-0">
        <div class="row">
            <div class="col-md-12" id="ledgeraccount">
                <FormSection v-if="email_user.personal_details" :formCollapse="collapseFormSections"
                    label="Personal Details" index="personal-details">
                    <form>
                        <div class="row mb-2">
                            <div class="col-md-2">
                                <label for="firstName" class="form-label">First Name</label>
                            </div>
                            <div class="col-md-4">
                                <input type="text" class="form-control" id="firstName" name="firstName"
                                    v-model="email_user.first_name" :readonly="readonly" />
                            </div>
                        </div>
                        <div class="row mb-2">
                            <div class="col-md-2">
                                <label for="lastName" class="form-label">Last Name</label>
                            </div>
                            <div class="col-md-4">
                                <input type="text" class="form-control" id="lastName" name="lastName"
                                    v-model="email_user.last_name" :readonly="readonly" />
                            </div>
                        </div>
                        <button v-if="!readonly" @click.prevent="updatePersonalDetails"
                            class="btn btn-primary float-end">Update</button>
                    </form>
                </FormSection>
                <FormSection v-if="email_user.address_details" :formCollapse="collapseFormSections" label="Address Details"
                    index="address-details">
                    <form v-if="email_user.residential_address" class="form-horizontal mb-2">
                        <fieldset>
                            <legend>Residential Address</legend>
                            <div class="address-box">
                                <div class="row mb-2">
                                    <div class="col-md-2">
                                        <label for="residentialAddressLine1" class="form-label">Line 1</label>
                                    </div>
                                    <div class="col-md-4">
                                        <input type="text" class="form-control" id="residentialAddressLine1"
                                            name="residentialAddressLine1" v-model="
                                                email_user.residential_address
                                                    .line1
                                            " :readonly="readonly" />
                                    </div>
                                </div>
                                <div v-if="email_user.residential_address.line2" class="row mb-2">
                                    <div class="col-md-2">
                                        <label for="residentialAddressLine2" class="form-label">Line 2</label>
                                    </div>
                                    <div class="col-md-4">
                                        <input type="text" class="form-control" id="residentialAddressLine2"
                                            name="residentialAddressLine2" v-model="
                                                email_user.residential_address
                                                    .line2
                                            " :readonly="readonly" />
                                    </div>
                                </div>
                                <div class="row mb-2">
                                    <div class="col-md-2">
                                        <label for="residentialLocality" class="form-label">Town/Suburb</label>
                                    </div>
                                    <div class="col-md-4">
                                        <input type="text" class="form-control" id="residentialLocality"
                                            name="residentialLocality" v-model="
                                                email_user.residential_address
                                                    .locality
                                            " :readonly="readonly" />
                                    </div>
                                </div>
                                <div class="row mb-2">
                                    <div class="col-md-2">
                                        <label for="residentialState" class="form-label">State</label>
                                    </div>
                                    <div class="col-md-4">
                                        <input type="text" class="form-control" id="residentialState"
                                            name="residentialState" v-model="
                                                email_user.residential_address
                                                    .state
                                            " :readonly="readonly" />
                                    </div>
                                </div>
                                <div class="row mb-2">
                                    <div class="col-md-2">
                                        <label for="residentialPostcode" class="form-label">Postcode</label>
                                    </div>
                                    <div class="col-md-4">
                                        <input type="text" class="form-control" id="residentialPostcode"
                                            name="residentialPostcode" v-model="
                                                email_user.residential_address
                                                    .postcode
                                            " :readonly="readonly" />
                                    </div>
                                </div>
                                <div class="row mb-2">
                                    <div class="col-md-2">
                                        <label for="residentialPostcode" class="form-label">Country</label>
                                    </div>
                                    <div class="col-md-4">
                                        <select class="form-select" id="country" name="Country" v-model="
                                            email_user.residential_address
                                                .country
                                        " :readonly="readonly">
                                            <option v-for="c in countries" :value="c.code">
                                                {{ c.name }}
                                            </option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                        </fieldset>
                    </form>
                    <form v-if="email_user.postal_address" class="form-horizontal mb-2">
                        <fieldset>
                            <legend>Postal Address</legend>
                            <div class="address-box">
                                <div class="row mb-2">
                                    <label for="" class="col-md-2 form-label">Postal Address</label>
                                    <div class="col-md-4">
                                        <input :readonly="readonly" type="text" class="form-control" id="postal_line1"
                                            name="Street" placeholder="" v-model="
                                                email_user.postal_address
                                                    .line1
                                            " />
                                    </div>
                                </div>
                                <div class="row mb-2">
                                    <label for="" class="col-md-2 form-label">Town/Suburb</label>
                                    <div class="col-md-4">
                                        <input :readonly="readonly" type="text" class="form-control" id="postal_locality"
                                            name="Town/Suburb" placeholder="" v-model="
                                                email_user.postal_address
                                                    .locality
                                            " />
                                    </div>
                                </div>
                                <div class="row mb-2">
                                    <label for="" class="col-md-2 form-label">State</label>
                                    <div class="col-md-4">
                                        <input :readonly="readonly" type="text" class="form-control" id="postal_state"
                                            name="State" placeholder="" v-model="
                                                email_user.postal_address
                                                    .state
                                            " />
                                    </div>
                                </div>
                                <div class="row mb-2">
                                    <label for="" class="col-md-2 form-label">Postcode</label>
                                    <div class="col-md-4">
                                        <input :readonly="readonly" type="text" class="form-control" id="postal_postcode"
                                            name="Postcode" placeholder="" v-model="
                                                email_user.postal_address
                                                    .postcode
                                            " />
                                    </div>
                                </div>
                                <div class="row mb-2">
                                    <label for="" class="col-md-2 form-label">Country</label>
                                    <div class="col-sm-4">
                                        <select :disabled="readonly" class="form-select" id="postal_country" name="Country"
                                            v-model="
                                                email_user.postal_address
                                                    .country
                                            ">
                                            <option v-for="c in countries" :value="c.code">
                                                {{ c.name }}
                                            </option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                        </fieldset>
                    </form>
                    <button v-if="!readonly" @click.prevent="updateAddressDetails"
                        class="btn btn-primary float-end">Update</button>
                </FormSection>
                <FormSection :formCollapse="collapseFormSections" label="Contact Details" index="contact-details">
                    <form>
                        <div v-if="email_user.phone_number" class="row mb-2">
                            <div class="col-md-2">
                                <label for="phone" class="form-label">Phone</label>
                            </div>
                            <div class="col-md-4">
                                <input type="text" class="form-control" id="phone" name="phone"
                                    v-model="email_user.phone_number" :readonly="readonly" />
                            </div>
                        </div>
                        <div v-if="email_user.mobile_number" class="row mb-2">
                            <div class="col-md-2">
                                <label for="mobile" class="form-label">Mobile</label>
                            </div>
                            <div class="col-md-4">
                                <input type="text" class="form-control" id="mobile" name="mobile"
                                    v-model="email_user.mobile_number" :readonly="readonly" />
                            </div>
                        </div>
                        <div v-if="email_user.email" class="row mb-2">
                            <div class="col-md-2">
                                <label for="email" class="form-label">Email</label>
                            </div>
                            <div class="col-md-4">
                                <input type="text" class="form-control" id="email" name="email" v-model="email_user.email"
                                    :readonly="readonly" />
                            </div>
                        </div>
                    </form>
                    <button v-if="!readonly" @click.prevent="updateContactDetails"
                        class="btn btn-primary float-end">Update</button>
                </FormSection>
            </div>
        </div>
    </div>
</template>

<script>
import { api_endpoints, helpers } from '@/utils/hooks'

export default {
    name: 'Applicant',
    props: {
        email_user: {
            type: Object,
            required: true,
        },
        customerType: {
            type: String,
            required: false,
        },
        proposalId: {
            type: Number,
        },
        collapseFormSections: {
            type: Boolean,
            default: true,
        },
        readonly: {
            type: Boolean,
            default: true,
        },
    },
    data: function () {
        let vm = this
        return {
            electoralRollSectionIndex: 'electoral_roll_' + vm._uid,
            silentElector: null,
            values: null,
            countries: [],
            showAddressError: false,
            detailsBody: 'detailsBody' + vm._uid,
            addressBody: 'addressBody' + vm._uid,
            contactsBody: 'contactsBody' + vm._uid,
            electoralRollBody: 'electoralRollBody' + vm._uid,
            panelClickersInitialised: false,
        }
    },
    computed: {
        electoralRollDocumentUrl: function () {
            let url = ''
            if (this.proposalId) {
                url = helpers.add_endpoint_join(
                    '/api/proposal/',
                    this.proposalId + '/process_electoral_roll_document/'
                )
            }
            return url
        },
        customerLabel: function () {
            let label = 'Applicant'
            if (this.customerType && this.customerType === 'holder') {
                label = 'Holder'
            }
            return label
        },
    },
    methods: {
        updatePersonalDetails: function () {
            alert('To be implemented');
        },
        updateAddressDetails: function () {
            alert('To be implemented');
        },
        updateContactDetails: function () {
            alert('To be implemented');
        },
        fetchCountries: function (id) {
            let vm = this
            fetch(api_endpoints.countries)
                .then(async (response) => {
                    const data = await response.json()
                    if (!response.ok) {
                        const error =
                            (data && data.message) || response.statusText
                        console.log(error)
                        return Promise.reject(error)
                    }
                    vm.countries = data
                    console.log(vm.countries)
                })
                .catch((error) => {
                    this.errorMessage = constants.ERRORS.API_ERROR
                    console.error('There was an error!', error)
                })
        },
    },
    mounted: function () {
        console.log('applicant mounted')
        let vm = this
        this.fetchCountries()
        if (!vm.panelClickersInitialised) {
            $('.panelClicker[data-toggle="collapse"]').on('click', function () {
                var chev = $(this).children()[0]
                window.setTimeout(function () {
                    $(chev).toggleClass(
                        'glyphicon-chevron-down glyphicon-chevron-up'
                    )
                }, 100)
            })
            vm.panelClickersInitialised = true
        }
        this.silentElector = this.storedSilentElector
    },
}
</script>

<style scoped>
fieldset,
legend {
    all: revert;
}

legend {
    color: grey;
}

fieldset {
    border-color: #efefef;
    border-style: solid;
}
</style>
