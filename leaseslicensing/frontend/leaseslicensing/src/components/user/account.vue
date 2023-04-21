<template>
    <div v-if="email_user" class="container">
        <div class="card">
            <div class="card-header">
                <ul class="nav nav-tabs card-header-tabs">
                    <li class="nav-item">
                        <a class="nav-link active" aria-current="true" data-bs-toggle="tab" data-bs-target="#account"
                            href="#">Account</a>
                    </li>
                    <li v-if="!email_user.is_internal" class="nav-item">
                        <a id="organisations-tab-link" class="nav-link" data-bs-toggle="tab" data-bs-target="#organisations"
                            href="#">Organisations</a>
                    </li>
                </ul>
            </div>
            <div class="card-body tab-content">
                <div class="tab-pane fade show active" id="account" role="tabpanel" aria-labelledby="home-tab">
                    <FormSection index="personal-details" label="Personal Details">
                        <form @submit.prevent="" id="personal-details" class="needs-validation" novalidate>
                            <div class="row mb-1">
                                <div class="col">
                                    <BootstrapAlert> <a href="/sso/setting">Update your account name or MFA</a>
                                        (Multi-Factor Authentication)
                                        <div class="fst-italic mt-1">
                                            <strong>Note: </strong> Changes will not update
                                            until your next login.
                                        </div>
                                    </BootstrapAlert>
                                </div>
                            </div>
                            <div class="row mb-3">
                                <label for="first-name" class="col-sm-2 col-form-label">First Name</label>
                                <div class="col-sm-4">
                                    <input type="text" class="form-control" id="first-name" :value="email_user.first_name"
                                        readonly>
                                </div>
                            </div>
                            <div class="row mb-3">
                                <label for="last-name" class="col-sm-2 col-form-label">Last Name</label>
                                <div class="col-sm-4">
                                    <input type="text" class="form-control" id="last-name" :value="email_user.last_name"
                                        readonly>
                                </div>
                            </div>
                            <div class="row mb-3">
                                <label for="dob" class="col-sm-2 col-form-label">Date of Birth</label>
                                <div class="col-sm-4">
                                    <input type="date" class="form-control" id="dob" v-model="email_user.dob" required>
                                </div>
                            </div>
                            <BootstrapLoadingButton text="Update" :isLoading="updatingDetails"
                                @click="validateForm('personal-details')" class="btn licensing-btn-primary float-end" />
                        </form>
                    </FormSection>

                    <FormSection v-if="email_user.residential_address" index="address-details" label="Address Details">
                        <form @submit.prevent="" id="address-details" class="mb-2 needs-validation" novalidate>
                            <fieldset class="mb-3">
                                <legend>Residential Address</legend>
                                <div class="address-box">
                                    <div class="row mb-2">
                                        <div class="col-md-2">
                                            <label for="residentialAddressLine1" class="form-label">Address</label>
                                        </div>
                                        <div class="col-md-4">
                                            <input type="text" class="form-control" id="residentialAddressLine1"
                                                name="residentialAddressLine1" v-model="
                                                    email_user.residential_address
                                                        .line1
                                                " required />
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
                                                " required />
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
                                                " required />
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
                                                " maxlength="10" required />
                                        </div>
                                    </div>
                                    <div class="row mb-4">
                                        <div class="col-md-2">
                                            <label for="residentialPostcode" class="form-label">Country</label>
                                        </div>
                                        <div class="col-md-4">
                                            <select class="form-select" id="country" name="Country" v-model="
                                                email_user.residential_address
                                                    .country
                                            " required>
                                                <option v-for="c in countries" :value="c.code">
                                                    {{ c.name }}
                                                </option>
                                            </select>
                                        </div>
                                    </div>
                                    <div class="row mb-2">
                                        <div class="col-md-2">
                                            &nbsp;
                                        </div>
                                        <div class="col-md-6">
                                            <div class="form-check form-switch">
                                                <label for="residentialPostcode" class="form-label">
                                                    Postal Address Same as Residential Address</label>
                                                <input @change="togglePostalAddressFieldsDisabled" class="form-check-input"
                                                    type="checkbox" v-model="email_user.postal_same_as_residential"
                                                    id="togglePostalAddressFieldsDisabled">
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </fieldset>
                            <fieldset class="mb-3">
                                <legend>Postal Address</legend>
                                <div class="address-box">
                                    <div class="row mb-2">
                                        <div class="col-md-2">
                                            <label for="postalAddressLine1" class="form-label">Address</label>
                                        </div>
                                        <div class="col-md-4">
                                            <input type="text" class="form-control postal-address" id="postalAddressLine1"
                                                name="postalAddressLine1" v-model="
                                                    email_user.postal_address
                                                        .line1
                                                " required />
                                        </div>
                                    </div>
                                    <div class="row mb-2">
                                        <div class="col-md-2">
                                            <label for="postalLocality" class="form-label">Town/Suburb</label>
                                        </div>
                                        <div class="col-md-4">
                                            <input type="text" class="form-control postal-address" id="postalLocality"
                                                name="postalLocality" v-model="
                                                    email_user.postal_address
                                                        .locality
                                                " required />
                                        </div>
                                    </div>
                                    <div class="row mb-2">
                                        <div class="col-md-2">
                                            <label for="postalState" class="form-label">State</label>
                                        </div>
                                        <div class="col-md-4">
                                            <input type="text" class="form-control postal-address" id="postalState"
                                                name="postalState" v-model="
                                                    email_user.postal_address
                                                        .state
                                                " required />
                                        </div>
                                    </div>
                                    <div class="row mb-2">
                                        <div class="col-md-2">
                                            <label for="postalPostcode" class="form-label">Postcode</label>
                                        </div>
                                        <div class="col-md-4">
                                            <input type="text" class="form-control postal-address" id="postalPostcode"
                                                name="postalPostcode" v-model="
                                                    email_user.postal_address
                                                        .postcode
                                                " maxlength="10" required />
                                        </div>
                                    </div>
                                    <div class="row mb-2">
                                        <div class="col-md-2">
                                            <label for="postalPostcode" class="form-label">Country</label>
                                        </div>
                                        <div class="col-md-4">
                                            <select class="form-select postal-address" id="country" name="Country" v-model="
                                                email_user.postal_address
                                                    .country
                                            " required>
                                                <option v-for="c in countries" :value="c.code">
                                                    {{ c.name }}
                                                </option>
                                            </select>
                                        </div>
                                    </div>
                                </div>
                            </fieldset>
                            <BootstrapLoadingButton text="Update" :isLoading="updatingDetails"
                                @click="validateForm('address-details')" class="btn licensing-btn-primary float-end" />
                        </form>
                    </FormSection>
                    <FormSection index="contact-details" label="Contact Details">
                        <form @submit.prevent="" id="contact-details" class="needs-validation" novalidate>
                            <div class="row mb-3">
                                <label for="phone" class="col-sm-2 col-form-label">Phone (work)</label>
                                <div class="col-sm-4">
                                    <input type="text" class="form-control" id="phone" v-model="email_user.phone_number"
                                        required>
                                </div>
                            </div>
                            <div class="row mb-3">
                                <label for="mobile" class="col-sm-2 col-form-label">Mobile</label>
                                <div class="col-sm-4">
                                    <input type="text" class="form-control" id="mobile" v-model="email_user.mobile_number"
                                        required>
                                </div>
                            </div>
                            <BootstrapLoadingButton text="Update" :isLoading="updatingDetails"
                                @click="validateForm('contact-details')" class="btn licensing-btn-primary float-end" />
                        </form>
                    </FormSection>

                </div>
                <div v-if="!email_user.is_internal" class="tab-pane fade" id="organisations" role="tabpanel"
                    aria-labelledby="organisations-tab">
                    <FormSection index="organisation-details" :label="linkOrganisationTitle">
                        <OrganisationSearch v-if="!selectedOrganisation && !newOrganisation"
                            @selected="organisationSelected" @new-organisation="prepareNewOrganisation"
                            label="Organisations" :lookupApiEndpoint="api_endpoints.organisation_lookup" />
                        <template v-if="selectedOrganisation">
                            <form id="existing-organisation-form" @submit.prevent="" class="needs-validation" novalidate>
                                <div class="row mb-3">
                                    <label for="selectedOrganisation" class="col-sm-3 col-form-label">Selected
                                        Organisation</label>

                                    <div class="col my-auto">
                                        <span class="badge bg-primary fs-6">{{ selectedOrganisation.text }}</span> Wrong
                                        Organisation? <a href="#" @click="searchAgain">Search
                                            Again</a>
                                    </div>
                                </div>
                                <div class="row mb-3">
                                    <div class="col-sm-3">
                                    </div>
                                    <div class="col-sm-7">
                                        <BootstrapAlert>
                                            <ul class="list-group">
                                                <li class="list-group-item">
                                                    This organisation has already been registered with the system.
                                                </li>
                                                <li class="list-group-item">
                                                    Please enter the two pin codes below.
                                                </li>
                                                <li class="list-group-item">
                                                    These pin codes can be retrieved from:
                                                </li>
                                                <li class="list-group-item">
                                                    <span v-for="person in selectedOrganisation.first_five.split(',')"
                                                        class="badge bg-primary bg-first-five">{{ person
                                                        }}</span>
                                                </li>
                                            </ul>
                                        </BootstrapAlert>
                                    </div>
                                </div>
                                <div class="row mb-3">
                                    <label for="pin1" class="col-sm-3 col-form-label">Pin 1</label>
                                    <div class="col-sm-4">
                                        <input type="text" class="form-control" id="pin1" ref="pin1" v-model="pins.pin1"
                                            minlength="12" maxlength="12" required>
                                        <div class="invalid-feedback">
                                            Please enter a 12 digit pin code.
                                        </div>
                                    </div>
                                </div>
                                <div class="row mb-3">
                                    <label for="pin2" class="col-sm-3 col-form-label">Pin 2</label>
                                    <div class="col-sm-4">
                                        <input type="text" class="form-control" id="pin2" ref="pin2" v-model="pins.pin2"
                                            minlength="12" maxlength="12" required>
                                        <div class="invalid-feedback">
                                            Please enter a 12 digit pin code.
                                        </div>
                                    </div>
                                </div>
                                <div v-if="validatePinsError" class="row mb-3">
                                    <label for="pin2" class="col-sm-3 col-form-label">&nbsp;</label>
                                    <div class="col-sm-4">
                                        <BootstrapAlert type="danger" icon="exclamation-triangle-fill">{{
                                            validatePinsError }}
                                        </BootstrapAlert>
                                    </div>
                                </div>
                                <div v-if="pinCodesEntered" class="row mb-3">
                                    <div for="pin2" class="col-sm-3">&nbsp;</div>
                                    <div class="col-sm-4">
                                        <BootstrapLoadingButton text="Submit Request" @click="validatePinsForm"
                                            :isLoading="validatingPins" class="btn licensing-btn-primary" />
                                    </div>
                                </div>
                            </form>
                        </template>
                        <template v-if="newOrganisation">
                            <form id="new-organisation-form" @submit.prevent="" class="needs-validation" novalidate>
                                <div class="row mb-3">
                                    <label for="" class="col-sm-3 col-form-label">&nbsp;</label>
                                    <div class="col-auto">
                                        <BootstrapAlert>
                                            <ul class="list-group">
                                                <li class="list-group-item">
                                                    The organisation you searched for has not yet been registered
                                                </li>
                                                <li class="list-group-item">
                                                    Please enter the details below
                                                </li>
                                            </ul>
                                        </BootstrapAlert>
                                    </div>
                                    <div class="col">
                                        <a href="#" @click="searchAgain">Search
                                            Again</a>
                                    </div>
                                </div>
                                <div class="row mb-3">
                                    <label for="newOrganisationName" class="col-sm-3 col-form-label">Organisation
                                        Name</label>
                                    <div class="col-sm-6">
                                        <input type="text" class="form-control" id="newOrganisationName"
                                            ref="newOrganisationName" v-model="newOrganisation.name" required>
                                    </div>
                                </div>
                                <div class="row mb-3">
                                    <label for="newOrganisationABN" class="col-sm-3 col-form-label">Organisation
                                        ABN or ACN</label>
                                    <div class="col-sm-6">
                                        <input type="text" class="form-control" id="newOrganisationABN"
                                            ref="newOrganisationABN" v-model="newOrganisation.abn" minlength="9"
                                            maxlength="11" required
                                            onkeydown="javascript: return['Backspace','Delete','ArrowLeft','ArrowRight'].includes(event.code) ? true : !isNaN(Number(event.key)) && event.code !== 'Space'">
                                        <div class="invalid-feedback">
                                            This is not a valid ABN or ACN.
                                        </div>
                                    </div>
                                </div>
                                <div class="row mb-3">
                                    <label for="newOrganisationIdentification" class="col-sm-3 col-form-label">Proof of
                                        Employment</label>
                                    <div class="col-sm-9">
                                        <input @change="readFile" type="file" class="form-control"
                                            id="newOrganisationIdentification" ref="newOrganisationIdentification" required>
                                        <div id="passwordHelpBlock" class="form-text">
                                            Please upload a letter on your organisation's official letter head stating
                                            that you are an employee of this organisation.
                                        </div>
                                    </div>
                                </div>
                                <div class="row mb-3">
                                    <div class="col-sm-3"></div>
                                    <div class="col-sm-9">
                                        <BootstrapLoadingButton text="Submit Request" @click="validateOrganisationRequest"
                                            :isLoading="loadingOrganisationRequest" class="btn licensing-btn-primary" />
                                    </div>
                                </div>
                            </form>
                        </template>
                    </FormSection>
                    <FormSection v-if="organisation_requests && organisation_requests.length" index="organisation-requests"
                        label="Linked Organisations">
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th scope="col" class="col-1">Organisation</th>
                                    <th scope="col" class="col-2">ABN / ACN</th>
                                    <th scope="col" class="col-3">Status</th>
                                    <th scope="col" class="col-4">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="org in organisation_requests">
                                    <td><span>{{ org.name }}</span></td>
                                    <td><span>{{ helpers.formatABNorACN(org.abn) }}</span></td>
                                    <td>
                                        <span v-if="'With Assessor' == org.status" class="badge bg-secondary p-2"><i
                                                class="fa fa-clock"></i>
                                            Pending</span>
                                        <span v-if="'Approved' == org.status" class="badge bg-success me-1 p-2"><i
                                                class="fa fa-chain"></i> Linked</span>
                                    </td>
                                    <td>
                                        <template v-if="'Approved' == org.status">
                                            <div>
                                                <a :href="'/external/organisations/manage/' + org.id"
                                                    class="btn btn-primary btn-sm btn-status me-1" role="button">
                                                    <i class="fa fa-pencil-square"></i>
                                                    update</a>
                                                <button class="btn btn-danger btn-sm btn-status">
                                                    <i class="fa fa-chain-broken"></i>
                                                    unlink</button>
                                            </div>
                                        </template>
                                        <span v-else>&nbsp;</span>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </FormSection>
                </div>
            </div>
        </div>
    </div>
    <BootstrapSpinner class="text-primary" v-else />
</template>

<script>
import OrganisationSearch from '@/components/internal/search/OrganisationSearch.vue'
import Swal from 'sweetalert2';
import BootstrapLoadingButton from '../../utils/vue/BootstrapLoadingButton.vue';
import { api_endpoints, constants, helpers, utils } from '@/utils/hooks'

export default {
    name: "Account",
    data() {
        return {
            api_endpoints: api_endpoints,
            countries: null,
            email_user: null,
            updatingDetails: false,
            selectedOrganisation: null,
            newOrganisation: null,
            organisation_requests: null,
            term: null,
            role: 'Employee',
            loadingOrganisationRequest: false,
            validatePinsError: null,
            validatingPins: false,
            pins: {
                pin1: '',
                pin2: '',
            },
            loadingOrganisationRequests: false,
            helpers: helpers,
        };
    },
    components: {
        BootstrapLoadingButton,
        OrganisationSearch,
    },
    computed: {
        linkOrganisationTitle: function () {
            if (this.organisation_requests && this.organisation_requests.length) {
                return 'Link another Organisation';
            }
            return 'Link an organisation';
        }
    },
    methods: {
        numbersOnly: function (event) {
            return event.keyCode === 8 || event.charCode >= 48 && event.charCode <= 57;
        },
        togglePostalAddressFieldsDisabled: function () {
            console.log('togglePostalAddressFieldsDisabled')

            $('.postal-address').each(function () {
                if ($(this).attr('disabled')) {
                    $(this).removeAttr('disabled');
                } else {
                    $(this).attr('disabled', 'disabled');
                }
            });
            if (!this.email_user.postal_same_as_residential) {
                $('.postal-address').first().focus();
            }
        },
        pinCodesEntered: function () {
            return this.$refs.pin1.value.length == 12 && this.$refs.pin2.value.length == 12;
        },
        fetchInitialData: function () {
            let vm = this;
            let initialisers = [
                utils.fetchCountries(),
                utils.fetchLedgerAccount(),
                utils.fetchRequestUserID(),
                utils.fetchOrganisationRequests(),
            ]
            Promise.all(initialisers).then(data => {
                vm.countries = data[0];
                vm.email_user = data[1].data;
                vm.email_user.id = data[2].id;
                vm.email_user.is_internal = data[2].is_internal;
                vm.organisation_requests = data[3].results;
                // Convert date to format that the date picker can use
                vm.email_user.dob = vm.email_user.dob.split("/").reverse().join("-");
                this.$nextTick(() => {
                    if (vm.email_user.postal_same_as_residential) {
                        vm.togglePostalAddressFieldsDisabled();
                    }
                    if (window.location.hash == '#organisations') {
                        console.log('opening organisations tab')
                        var tab_element = document.querySelector('#organisations-tab-link');
                        var tab = new bootstrap.Tab(tab_element);
                        tab.show();
                        this.$nextTick(() => {
                            $('#search-organisations').select2('open');
                        })
                    }
                });
                console.log(vm.email_user.dob)
            });
        },
        fetchOrganisationRequests: function () {
            let vm = this;
            vm.loadingOrganisationRequests = true;
            utils.fetchOrganisationRequests().then(data => {
                vm.organisation_requests = data.results;
                vm.loadingOrganisationRequests = false;
            });
        },
        // copyResidentialAddress: function (event) {
        //     let vm = this;
        //     if (event.target.checked) {
        //         vm.email_user.postal_address = { ...vm.email_user.residential_address };
        //         vm.togglePostalAddressFieldsDisabled();
        //     } else {
        //         Object.keys(vm.email_user.postal_address).forEach((i) => vm.email_user.postal_address[i] = '');
        //         vm.email_user.postal_address.country = 'AU';
        //         vm.togglePostalAddressFieldsDisabled();
        //     }
        // },
        validateForm: function (formId) {
            let vm = this;
            var form = document.getElementById(formId)

            if (form.checkValidity()) {
                console.log('Form valid');
                vm.updateDetails();
            } else {
                form.classList.add('was-validated');
                $(form).find("input:invalid").first().focus();
            }

            return false;
        },
        updateDetails: function () {
            let vm = this;
            vm.updatingDetails = true;
            let email_user = { ...vm.email_user };
            email_user.postal_address = { ...vm.email_user.postal_address };
            email_user.residential_address = { ...vm.email_user.residential_address };
            // Convert date back to format that the API expects
            email_user.dob = email_user.dob.split("-").reverse().join("/");
            // Remove the read-only fields from the payload
            delete email_user.first_name;
            delete email_user.last_name;
            this.updateAddressFieldNames(email_user)
            email_user.postal_address.postal_same_as_residential = vm.email_user.postal_same_as_residential
            let payload = JSON.stringify({ 'payload': email_user })
            console.log(payload)
            fetch(vm.api_endpoints.updateAccountDetails(vm.email_user.id), {
                method: 'POST',
                body: payload,
            })
                .then(async (response) => {
                    const data = await response.json()
                    if (!response.ok) {
                        const error =
                            (data && data.message) || response.statusText
                        console.log(error)
                        return Promise.reject(error)
                    }
                    console.log(data)
                    Swal.fire(
                        'Success',
                        'Details updated successfully',
                        'success'
                    )
                })
                .catch((error) => {
                    console.error('There was an error!', error)
                }).finally(() => {
                    vm.updatingDetails = false;
                });

        },
        updateAddressFieldNames: function (email_user) {
            Object.keys(email_user.postal_address).forEach(
                function (i) {
                    email_user.postal_address['postal_' + i] = email_user.postal_address[i];
                    delete email_user.postal_address[i];
                }
            );
            Object.keys(email_user.residential_address).forEach(
                function (i) {
                    email_user.residential_address['residential_' + i] = email_user.residential_address[i];
                    delete email_user.residential_address[i];
                }
            );
        },
        organisationSelected: function (organisation) {
            this.selectedOrganisation = organisation;
            this.$nextTick(() => {
                $('#pin1').focus();
            });
        },
        searchAgain: function () {
            this.selectedOrganisation = null;
            this.newOrganisation = null;
            this.$nextTick(() => {
                $('#search-organisations').select2('open');
            });
        },
        prepareNewOrganisation: function (term) {
            this.newOrganisation = {};
            let termAbn = Number(term)
            if (!isNaN(termAbn) && Number.isInteger(termAbn)) {
                this.newOrganisation.abn = term;
                this.$nextTick(() => {
                    $('#newOrganisationABN').focus();
                });
            } else {
                this.newOrganisation.name = term;
                this.$nextTick(() => {
                    $('#newOrganisationName').focus();
                });
            }
        },
        validatePinsForm: function () {
            let vm = this;
            var form = document.getElementById('existing-organisation-form')

            if (form.checkValidity()) {
                console.log('Form valid');
                vm.validatePins();
            } else {
                form.classList.add('was-validated');
                $('#existing-organisation-form').find("input:invalid").first().focus();
            }

            return false;
        },
        validatePins: function () {
            let vm = this;
            vm.validatingPins = true;
            const requestOptions = {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(vm.pins)
            };
            fetch(helpers.add_endpoint_json(api_endpoints.organisations, (vm.selectedOrganisation.id + '/validate_pins')), requestOptions)
                .then(async (response) => {
                    const data = await response.json()
                    if (!response.ok) {
                        const error =
                            (data && data.message) || response.statusText
                        console.log(error)
                        return Promise.reject(error)
                    }
                    if (data.valid) {
                        Swal.fire(
                            'Success',
                            'The pins you entered have been validated and your request will be processed by an organisation administrator.',
                            'success')
                        vm.selectedOrganisation = null;
                        vm.fetchOrganisationRequests();
                    } else {
                        Swal.fire(
                            'Error',
                            'The pins you entered are not valid. Please check the pins and try again.',
                            'error')
                    }

                    console.log(data)
                })
                .catch((error) => {
                    console.error('There was an error!', error)
                }).finally(() => {
                    vm.validatingPins = false;
                });
        },
        validateOrganisationRequest: function () {
            let vm = this;
            var form = document.getElementById('new-organisation-form')

            if (form.checkValidity()) {
                console.log('Form valid');
                vm.submitOrganisationRequest();
            } else {
                form.classList.add('was-validated');
                $('#new-organisation-form').find("input:invalid").first().focus();
            }

            return false;
        },
        submitOrganisationRequest: function () {
            let vm = this;
            vm.loadingOrganisationRequest = true;
            let data = new FormData();
            data.append('name', vm.newOrganisation.name);
            data.append('abn', vm.newOrganisation.abn);
            data.append('identification', vm.newOrganisation.identification);
            data.append('role', vm.role);
            const requestOptions = {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: data
            };
            fetch(api_endpoints.organisation_requests, requestOptions)
                .then(async (response) => {
                    const data = await response.json()
                    if (!response.ok) {
                        const error =
                            (data && data.message) || response.statusText
                        console.log(error)
                        return Promise.reject(error)
                    }
                    Swal.fire(
                        'Success',
                        'Your request has been submitted successfully. You will be notified once your request has been processed.',
                        'success')
                    vm.newOrganisation = null;
                    vm.fetchOrganisationRequests();
                    console.log(data)
                })
                .catch((error) => {
                    this.errorMessage = constants.ERRORS.API_ERROR
                    console.error('There was an error!', error)
                }).finally(() => {
                    vm.loadingOrganisationRequest = false;
                })

        },
        readFile: function () {
            let vm = this;
            let _file = null;
            var input = $(vm.$refs.newOrganisationIdentification)[0];
            if (input.files && input.files[0]) {
                var reader = new FileReader();
                reader.readAsDataURL(input.files[0]);
                reader.onload = function (e) {
                    _file = e.target.result;
                };
                _file = input.files[0];
            }
            vm.newOrganisation.identification = _file;
        },
    },
    created: function () {
        this.fetchInitialData();
    },
    mounted: function () {

    },
};
</script>

<style scoped>
.card-header-tabs .nav-link {
    margin-bottom: -1px;
}

.btn-status {
    height: 28px;
}

.col-1 {
    width: 49%;
}

.col-2 {
    width: 16%;
}

.col-3 {
    width: 15%;
}

.col-4 {
    width: 20%;
}

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

/* Hide the number input arrows */

/* Chrome, Safari, Edge, Opera */
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
}

/* Firefox */
input[type=number] {
    -moz-appearance: textfield;
}
</style>
