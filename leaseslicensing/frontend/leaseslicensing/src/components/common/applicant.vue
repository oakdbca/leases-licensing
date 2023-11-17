<template lang="html">
    <div class="container m-0 p-0">
        <div class="row">
            <div id="ledgeraccount" class="col-md-12">
                <FormSection
                    v-if="profile"
                    :form-collapse="collapseFormSections"
                    label="Personal Details"
                    index="personal-details"
                >
                    <form>
                        <alert
                            v-if="showPersonalError"
                            type="danger"
                            style="color: red"
                            ><div v-for="item in errorListPersonal" :key="item">
                                <strong>{{ item }}</strong>
                            </div></alert
                        >
                        <div class="row mb-2">
                            <div class="col-md-2">
                                <label for="firstName" class="form-label"
                                    >First Name</label
                                >
                            </div>
                            <div class="col-md-4">
                                <input
                                    id="firstName"
                                    v-model="profile.first_name"
                                    type="text"
                                    class="form-control"
                                    name="firstName"
                                    :readonly="readonly"
                                />
                            </div>
                        </div>
                        <div class="row mb-2">
                            <div class="col-md-2">
                                <label for="lastName" class="form-label"
                                    >Last Name</label
                                >
                            </div>
                            <div class="col-md-4">
                                <input
                                    id="lastName"
                                    v-model="profile.last_name"
                                    type="text"
                                    class="form-control"
                                    name="lastName"
                                    :readonly="readonly"
                                />
                            </div>
                        </div>
                        <div v-if="!readonly" class="col-sm-12">
                            <button
                                v-if="!updatingPersonal"
                                class="btn btn-primary float-end"
                                @click.prevent="updatePersonal()"
                            >
                                Update
                            </button>
                            <button
                                v-else
                                disabled
                                class="btn btn-primary float-end"
                            >
                                <i class="fa fa-spin fa-spinner"></i
                                >&nbsp;Updating
                            </button>
                        </div>
                    </form>
                </FormSection>
                <FormSection
                    v-if="profile"
                    :form-collapse="collapseFormSections"
                    label="Address Details"
                    index="address-details"
                >
                    <form v-if="profile" class="form-horizontal mb-2">
                        <alert
                            v-if="showAddressError"
                            type="danger"
                            style="color: red"
                            ><div v-for="item in errorListAddress" :key="item">
                                <strong>{{ item }}</strong>
                            </div></alert
                        >
                        <fieldset>
                            <legend>Residential Address</legend>
                            <div class="address-box">
                                <div class="row mb-2">
                                    <div class="col-md-2">
                                        <label
                                            for="residentialAddressLine1"
                                            class="form-label"
                                            >Street</label
                                        >
                                    </div>
                                    <div class="col-md-4">
                                        <input
                                            id="line1"
                                            v-model="profile.residential_line1"
                                            type="text"
                                            class="form-control"
                                            name="residentialAddressLine1"
                                            :readonly="readonly"
                                        />
                                    </div>
                                </div>
                                <div
                                    v-if="profile.residential_line2"
                                    class="row mb-2"
                                >
                                    <div class="col-md-2">
                                        <label
                                            for="residentialAddressLine2"
                                            class="form-label"
                                            >Line 2</label
                                        >
                                    </div>
                                    <div class="col-md-4">
                                        <input
                                            id="line1"
                                            v-model="profile.residential_line2"
                                            type="text"
                                            class="form-control"
                                            name="residentialAddressLine2"
                                            :readonly="readonly"
                                        />
                                    </div>
                                </div>
                                <div class="row mb-2">
                                    <div class="col-md-2">
                                        <label
                                            for="residentialLocality"
                                            class="form-label"
                                            >Town/Suburb</label
                                        >
                                    </div>
                                    <div class="col-md-4">
                                        <input
                                            id="locality"
                                            v-model="
                                                profile.residential_locality
                                            "
                                            type="text"
                                            class="form-control"
                                            name="residentialLocality"
                                            :readonly="readonly"
                                        />
                                    </div>
                                </div>
                                <div class="row mb-2">
                                    <div class="col-md-2">
                                        <label
                                            for="residentialState"
                                            class="form-label"
                                            >State</label
                                        >
                                    </div>
                                    <div class="col-md-4">
                                        <input
                                            id="state"
                                            v-model="profile.residential_state"
                                            type="text"
                                            class="form-control"
                                            name="residentialState"
                                            :readonly="readonly"
                                        />
                                    </div>
                                </div>
                                <div class="row mb-2">
                                    <div class="col-md-2">
                                        <label
                                            for="residentialPostcode"
                                            class="form-label"
                                            >Postcode</label
                                        >
                                    </div>
                                    <div class="col-md-4">
                                        <input
                                            id="postcode"
                                            v-model="
                                                profile.residential_postcode
                                            "
                                            type="text"
                                            class="form-control"
                                            name="residentialPostcode"
                                            :readonly="readonly"
                                        />
                                    </div>
                                </div>
                                <div class="row mb-2">
                                    <div class="col-md-2">
                                        <label
                                            for="residentialPostcode"
                                            class="form-label"
                                            >Country</label
                                        >
                                    </div>
                                    <div class="col-md-4">
                                        <select
                                            v-if="countries"
                                            id="country"
                                            v-model="
                                                profile.residential_country
                                            "
                                            class="form-select"
                                            name="Country"
                                            :disabled="readonly"
                                        >
                                            <option
                                                v-for="c in countries"
                                                :key="c.code"
                                                :value="c.code"
                                            >
                                                {{ c.name }}
                                            </option>
                                        </select>
                                        <BootstrapSpinner
                                            v-else
                                            class="text-primary"
                                            :is-loading="true"
                                            :center-of-screen="false"
                                            :small="true"
                                        />
                                    </div>
                                </div>
                            </div>
                        </fieldset>
                    </form>
                    <div class="row">
                        <div class="col-md-2">&nbsp;</div>
                        <div class="col-md-6 form-check form-switch">
                            <label
                                for="postal_same_as_residential"
                                class="form-label"
                            >
                                Postal same as residential address</label
                            >
                            <input
                                id="postal_same_as_residential"
                                v-model="profile.postal_same_as_residential"
                                class="form-check-input"
                                type="checkbox"
                                @change="togglePostal"
                            />
                        </div>
                    </div>

                    <form v-if="profile" class="form-horizontal mb-2">
                        <fieldset
                            :disabled="profile.postal_same_as_residential"
                        >
                            <legend>Postal Address</legend>
                            <div class="address-box">
                                <div class="row mb-2">
                                    <label for="" class="col-md-2 form-label"
                                        >Street</label
                                    >
                                    <div class="col-md-4">
                                        <input
                                            id="postal_line1"
                                            v-model="profile.postal_line1"
                                            :readonly="readonly"
                                            type="text"
                                            class="form-control postal-address"
                                            name="Street"
                                            placeholder=""
                                        />
                                    </div>
                                </div>
                                <div class="row mb-2">
                                    <label for="" class="col-md-2 form-label"
                                        >Town/Suburb</label
                                    >
                                    <div class="col-md-4">
                                        <input
                                            id="postal_locality"
                                            v-model="profile.postal_locality"
                                            :readonly="readonly"
                                            type="text"
                                            class="form-control postal-address"
                                            name="Town/Suburb"
                                            placeholder=""
                                        />
                                    </div>
                                </div>
                                <div class="row mb-2">
                                    <label for="" class="col-md-2 form-label"
                                        >State</label
                                    >
                                    <div class="col-md-4">
                                        <input
                                            id="postal_state"
                                            v-model="profile.postal_state"
                                            :readonly="readonly"
                                            type="text"
                                            class="form-control postal-address"
                                            name="State"
                                            placeholder=""
                                        />
                                    </div>
                                </div>
                                <div class="row mb-2">
                                    <label for="" class="col-md-2 form-label"
                                        >Postcode</label
                                    >
                                    <div class="col-md-4">
                                        <input
                                            id="postal_postcode"
                                            v-model="profile.postal_postcode"
                                            :readonly="readonly"
                                            type="text"
                                            class="form-control postal-address"
                                            name="Postcode"
                                            placeholder=""
                                        />
                                    </div>
                                </div>
                                <div class="row mb-2">
                                    <label for="" class="col-md-2 form-label"
                                        >Country</label
                                    >
                                    <div class="col-sm-4">
                                        <select
                                            v-if="countries"
                                            id="postal_country"
                                            v-model="profile.postal_country"
                                            :disabled="readonly"
                                            class="form-select postal-address"
                                            name="Country"
                                        >
                                            <option
                                                v-for="c in countries"
                                                :key="c.code"
                                                :value="c.code"
                                            >
                                                {{ c.name }}
                                            </option>
                                        </select>
                                        <BootstrapSpinner
                                            v-else
                                            class="text-primary"
                                            :is-loading="true"
                                            :center-of-screen="false"
                                            :small="true"
                                        />
                                    </div>
                                </div>
                            </div>
                        </fieldset>
                    </form>
                    <div v-if="!readonly" class="col-sm-12">
                        <button
                            v-if="!updatingAddress"
                            class="btn btn-primary float-end"
                            @click.prevent="updateAddress()"
                        >
                            Update
                        </button>
                        <button
                            v-else
                            disabled
                            class="btn btn-primary float-end"
                        >
                            <i class="fa fa-spin fa-spinner"></i>&nbsp;Updating
                        </button>
                    </div>
                </FormSection>
                <FormSection
                    :form-collapse="collapseFormSections"
                    label="Contact Details"
                    index="contact-details"
                >
                    <form>
                        <alert
                            v-if="showContactError"
                            type="danger"
                            style="color: red"
                            ><div v-for="item in errorListContact" :key="item">
                                <strong>{{ item }}</strong>
                            </div></alert
                        >
                        <div v-if="profile" class="row mb-2">
                            <div class="col-md-2">
                                <label for="phone" class="form-label"
                                    >Phone</label
                                >
                            </div>
                            <div class="col-md-4">
                                <input
                                    id="phone"
                                    v-model="profile.phone_number"
                                    type="text"
                                    class="form-control"
                                    name="phone"
                                    :readonly="readonly"
                                />
                            </div>
                        </div>
                        <div v-if="profile" class="row mb-2">
                            <div class="col-md-2">
                                <label for="mobile" class="form-label"
                                    >Mobile</label
                                >
                            </div>
                            <div class="col-md-4">
                                <input
                                    id="mobile"
                                    v-model="profile.mobile_number"
                                    type="text"
                                    class="form-control"
                                    name="mobile"
                                    :readonly="readonly"
                                />
                            </div>
                        </div>
                        <div v-if="profile" class="row mb-2">
                            <div class="col-md-2">
                                <label for="email" class="form-label"
                                    >Email</label
                                >
                            </div>
                            <div class="col-md-4">
                                <input
                                    id="email"
                                    v-model="profile.email"
                                    type="text"
                                    class="form-control"
                                    name="email"
                                    :readonly="readonly"
                                />
                            </div>
                        </div>
                    </form>
                    <div v-if="!readonly" class="col-sm-12">
                        <button
                            v-if="!updatingContact"
                            class="btn btn-primary float-end"
                            @click.prevent="updateContact()"
                        >
                            Update
                        </button>
                        <button
                            v-else
                            disabled
                            class="btn btn-primary float-end"
                        >
                            <i class="fa fa-spin fa-spinner"></i>&nbsp;Updating
                        </button>
                    </div>
                </FormSection>
            </div>
        </div>
    </div>
</template>

<script>
import { helpers, utils, api_endpoints, constants } from '@/utils/hooks';
import FormSection from '@/components/forms/section_toggle.vue';
import alert from '@vue-utils/alert.vue';

export default {
    name: 'Applicant',
    components: {
        FormSection,
        alert,
    },
    props: {
        emailUser: {
            type: Object,
            default: null,
        },
        proposalId: {
            type: Number,
            default: null,
        },
        customerType: {
            type: String,
            required: false,
            default: 'applicant',
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
        let vm = this;
        return {
            electoralRollSectionIndex: 'electoral_roll_' + vm._uid,
            silentElector: null,
            values: null,
            countries: null,
            detailsBody: 'detailsBody' + vm._uid,
            addressBody: 'addressBody' + vm._uid,
            contactsBody: 'contactsBody' + vm._uid,
            electoralRollBody: 'electoralRollBody' + vm._uid,
            panelClickersInitialised: false,
            updatingPersonal: false,
            updatingAddress: false,
            updatingContact: false,
            missing_fields: [],
            errorListPersonal: [],
            showPersonalError: false,
            errorListAddress: [],
            showAddressError: false,
            errorListContact: [],
            showContactError: false,
            profile: {
                last_name: '',
                first_name: '',
                dob: '',
                residential_line1: '',
                residential_line2: '',
                residential_line3: '',
                residential_locality: '',
                residential_state: '',
                residential_country: '',
                residential_postcode: '',
                postal_same_as_residential: false,
                postal_line1: '',
                postal_line2: '',
                postal_line3: '',
                postal_locality: '',
                postal_state: '',
                postal_country: '',
                postal_postcode: '',
                email: '',
                phone_number: null,
                mobile_number: null,
            },
        };
    },
    computed: {
        customerLabel: function () {
            let label = 'Applicant';
            if (this.customerType && this.customerType === 'holder') {
                label = 'Holder';
            }
            return label;
        },
    },
    mounted: function () {
        let vm = this;
        vm.fetchCountries();
        if (vm.proposalId) {
            vm.fetchProfile();
        } else if (vm.emailUser) {
            vm.profile = Object.assign({}, vm.emailUser);

            // The address information we are interested in
            let address_keys = [
                'line1',
                'postcode',
                'locality',
                'state',
                'country',
            ];
            // Add residential and postal address information as direct properties to the profile
            let res_addr = vm.emailUser.residential_address;
            let post_addr = vm.emailUser.postal_address;
            vm.profile = address_keys.reduce((profile, k) => {
                if (res_addr && Object.keys(res_addr).includes(k)) {
                    profile[`residential_${k}`] = res_addr[k];
                }
                if (post_addr && Object.keys(post_addr).includes(k)) {
                    profile[`postal_${k}`] = post_addr[k];
                }
                return profile;
            }, vm.profile);
        } else {
            console.error('No profile or proposal id provided');
        }
        if (!vm.panelClickersInitialised) {
            $('.panelClicker[data-toggle="collapse"]').on('click', function () {
                var chev = $(this).children()[0];
                window.setTimeout(function () {
                    $(chev).toggleClass(
                        'glyphicon-chevron-down glyphicon-chevron-up'
                    );
                }, 100);
            });
            vm.panelClickersInitialised = true;
        }
        this.silentElector = this.storedSilentElector;
    },
    methods: {
        togglePostal: function () {
            if (!this.profile.postal_same_as_residential) {
                $('.postal-address').first().focus();
            } else {
                this.profile.postal_line1 = this.profile.residential_line1;
                this.profile.postal_line2 = this.profile.residential_line2;
                this.profile.postal_line3 = this.profile.residential_line3;
                this.profile.postal_locality =
                    this.profile.residential_locality;
                this.profile.postal_state = this.profile.residential_state;
                this.profile.postal_country = this.profile.residential_country;
                this.profile.postal_postcode =
                    this.profile.residential_postcode;
            }
        },
        fetchCountries: function () {
            let vm = this;
            let url = api_endpoints.countries;
            utils
                .fetchUrl(url)
                .then((data) => {
                    vm.countries = Object.assign({}, data);
                })
                .catch((error) => {
                    this.errorMessage = constants.ERRORS.API_ERROR;
                    console.error(`Error fetching countries data: ${error}`);
                });
        },
        fetchProfile: function () {
            let vm = this;
            let url = api_endpoints.profile + '/' + vm.proposalId;
            utils
                .fetchUrl(url)
                .then((data) => {
                    vm.profile = Object.assign({}, data);
                })
                .catch((error) => {
                    this.errorMessage = constants.ERRORS.API_ERROR;
                    console.error(`Error fetching profile data: ${error}`);
                });
        },
        updatePersonal: function () {
            var required_fields = [];
            let vm = this;
            vm.missing_fields = [];
            vm.errorListPersonal = [];
            required_fields = $('#firstName, #lastName');
            vm.missing_fields = [];
            required_fields.each(function () {
                if (this.value == '') {
                    vm.errorListPersonal.push(
                        'Value not provided: ' + this.name
                    );
                    vm.missing_fields.push({ id: this.id });
                }
            });

            if (vm.missing_fields.length > 0) {
                vm.showPersonalError = true;
            } else {
                vm.showPersonalError = false;
                vm.updatingPersonal = true;
                fetch(
                    helpers.add_endpoint_json(
                        api_endpoints.proposal,
                        vm.proposalId + '/update_personal'
                    ),
                    {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(vm.profile),
                    }
                )
                    .then((response) => {
                        response.json().then((data) => {
                            vm.profile = data;
                        });
                    })
                    .catch((error) => {
                        console.error(error);
                    })
                    .finally(() => {
                        vm.updatingPersonal = false;
                    });
            }
        },
        updateContact: function () {
            var required_fields = [];
            let vm = this;
            vm.missing_fields = [];
            vm.errorListContact = [];
            required_fields = $('#email');
            vm.missing_fields = [];
            required_fields.each(function () {
                if (this.value == '') {
                    vm.errorListContact.push(
                        'Value not provided: ' + this.name
                    );
                    vm.missing_fields.push({ id: this.id });
                }
            });
            if (
                vm.profile.mobile_number == '' ||
                vm.profile.phone_number == ''
            ) {
                vm.errorListContact.push(
                    'Value not provided: mobile/ Phone number'
                );
                vm.missing_fields.push({ id: $('#mobile').id });
            }
            if (vm.missing_fields.length > 0) {
                vm.showContactError = true;
            } else {
                vm.showContactError = false;
                vm.updatingContact = true;
                fetch(
                    helpers.add_endpoint_json(
                        api_endpoints.proposal,
                        vm.proposalId + '/update_contact'
                    ),
                    {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(vm.profile),
                    }
                )
                    .then((response) => {
                        response.json().then((data) => {
                            vm.profile = data;
                        });
                    })
                    .catch((error) => {
                        console.error(error);
                    })
                    .finally(() => {
                        vm.updatingContact = false;
                    });
            }
        },
        updateAddressWrapper: function () {
            this.$nextTick(() => {
                this.updateAddress();
            });
        },
        updateAddress: async function () {
            var required_fields = [];
            let vm = this;

            vm.missing_fields = [];
            vm.errorListAddress = [];
            required_fields = $(
                '#postcode, #line1, #locality, #country, #state'
            );
            if (!vm.profile.postal_same_as_residential) {
                required_fields = $(
                    '#postcode, #line1, #locality, #country, #state, #postal_line1, #postal_locality, #postal_postcode, #postal_country, #postal_state'
                );
            }
            vm.missing_fields = [];
            required_fields.each(function () {
                if (this.value == '') {
                    vm.errorListAddress.push(
                        'Value not provided: ' + this.name
                    );
                    vm.missing_fields.push({ id: this.id });
                }
            });

            if (vm.missing_fields.length > 0) {
                vm.showAddressError = true;
            } else {
                vm.showAddressError = false;

                vm.updatingAddress = true;
                let payload = {};
                payload.residential_line1 = vm.profile.residential_line1;
                payload.residential_locality = vm.profile.residential_locality;
                payload.residential_state = vm.profile.residential_state;
                payload.residential_postcode = vm.profile.residential_postcode;
                payload.residential_country = vm.profile.residential_country;
                payload.postal_line1 = vm.profile.postal_line1;
                payload.postal_locality = vm.profile.postal_locality;
                payload.postal_state = vm.profile.postal_state;
                payload.postal_postcode = vm.profile.postal_postcode;
                payload.postal_country = vm.profile.postal_country;
                if (vm.profile.postal_same_as_residential) {
                    payload.postal_same_as_residential = true;
                }
                fetch(
                    helpers.add_endpoint_json(
                        api_endpoints.proposal,
                        vm.proposalId + '/update_address'
                    ),
                    {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(vm.profile),
                    }
                )
                    .then((response) => {
                        response.json().then((data) => {
                            vm.profile = data;
                        });
                    })
                    .catch((error) => {
                        console.error(error);
                    })
                    .finally(() => {
                        vm.updatingAddress = false;
                    });
            }
        },
    },
};
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
