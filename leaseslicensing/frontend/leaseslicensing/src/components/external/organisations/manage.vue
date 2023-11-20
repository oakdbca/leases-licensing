<template>
    <div id="externalOrgInfo" class="container">
        <div class="row">
            <div v-if="org" class="col">
                <div class="row">
                    <FormSection
                        index="organisation-details"
                        label="Organisation Details"
                        :form-collapse="false"
                    >
                        <form
                            id="organisation-details"
                            class="mb-2 needs-validation"
                            novalidate
                            @submit.prevent=""
                        >
                            <div class="row mb-3">
                                <label
                                    for="ledger_organisation_name"
                                    class="col-sm-3 control-label"
                                    >Organisation Name</label
                                >
                                <div class="col-sm-4">
                                    <input
                                        v-model="org.ledger_organisation_name"
                                        type="text"
                                        class="form-control"
                                        name="ledger_organisation_name"
                                        required
                                    />
                                </div>
                            </div>

                            <div class="row mb-3">
                                <label
                                    for="ledger_organisation_trading_name"
                                    class="col-sm-3 control-label"
                                    >Trading Name</label
                                >
                                <div class="col-sm-4">
                                    <input
                                        v-model="
                                            org.ledger_organisation_trading_name
                                        "
                                        type="text"
                                        class="form-control"
                                        name="ledger_organisation_trading_name"
                                    />
                                </div>
                            </div>

                            <div class="row mb-3">
                                <label
                                    for="ledger_organisation_abn"
                                    class="col-sm-3 control-label"
                                    >ABN
                                </label>
                                <div class="col-sm-4">
                                    <input
                                        v-model="org.ledger_organisation_abn"
                                        type="text"
                                        class="form-control"
                                        name="ledger_organisation_abn"
                                        disabled
                                    />
                                </div>
                            </div>

                            <div class="row mb-3">
                                <label
                                    for="ledger_organisation_email"
                                    class="col-sm-3 control-label"
                                    >Email
                                </label>
                                <div class="col-sm-4">
                                    <input
                                        v-model="org.ledger_organisation_email"
                                        type="email"
                                        class="form-control"
                                        name="ledger_organisation_email"
                                    />
                                </div>
                            </div>

                            <div class="form-group">
                                <div class="col-sm-12">
                                    <BootstrapLoadingButton
                                        text="Update"
                                        :is-loading="updatingDetails"
                                        class="btn btn-primary float-end"
                                        @click="
                                            validateForm('organisation-details')
                                        "
                                    />
                                </div>
                            </div>
                        </form>
                    </FormSection>

                    <FormSection
                        v-if="org"
                        index="address-details"
                        label="Address Details"
                        :form-collapse="false"
                    >
                        <form
                            id="address-details"
                            class="mb-2 needs-validation"
                            novalidate
                            @submit.prevent=""
                        >
                            <fieldset class="mb-3">
                                <legend>Postal Address</legend>
                                <div class="address-box">
                                    <div class="row mb-2">
                                        <div class="col-md-2">
                                            <label
                                                for="postalAddressLine1"
                                                class="form-label"
                                                >Street</label
                                            >
                                        </div>
                                        <div class="col-md-4">
                                            <input
                                                id="postalAddressLine1"
                                                v-model="
                                                    org.postal_address
                                                        .postal_line1
                                                "
                                                type="text"
                                                class="form-control"
                                                name="postalAddressLine1"
                                                required
                                            />
                                        </div>
                                    </div>
                                    <div class="row mb-2">
                                        <div class="col-md-2">
                                            <label
                                                for="postalLocality"
                                                class="form-label"
                                                >Town/Suburb</label
                                            >
                                        </div>
                                        <div class="col-md-4">
                                            <input
                                                id="postalLocality"
                                                v-model="
                                                    org.postal_address
                                                        .postal_locality
                                                "
                                                type="text"
                                                class="form-control"
                                                name="postalLocality"
                                                required
                                            />
                                        </div>
                                    </div>
                                    <div class="row mb-2">
                                        <div class="col-md-2">
                                            <label
                                                for="postalState"
                                                class="form-label"
                                                >State</label
                                            >
                                        </div>
                                        <div class="col-md-4">
                                            <input
                                                id="postalState"
                                                v-model="
                                                    org.postal_address
                                                        .postal_state
                                                "
                                                type="text"
                                                class="form-control"
                                                name="postalState"
                                                required
                                            />
                                        </div>
                                    </div>
                                    <div class="row mb-2">
                                        <div class="col-md-2">
                                            <label
                                                for="postalPostcode"
                                                class="form-label"
                                                >Postcode</label
                                            >
                                        </div>
                                        <div class="col-md-4">
                                            <input
                                                id="postalPostcode"
                                                v-model="
                                                    org.postal_address
                                                        .postal_postcode
                                                "
                                                type="text"
                                                class="form-control"
                                                name="postalPostcode"
                                                maxlength="10"
                                                required
                                            />
                                        </div>
                                    </div>
                                    <div class="row mb-2">
                                        <div class="col-md-2">
                                            <label
                                                for="postalPostcode"
                                                class="form-label"
                                                >Country</label
                                            >
                                        </div>
                                        <div class="col-md-4">
                                            <select
                                                id="country"
                                                v-model="
                                                    org.postal_address
                                                        .postal_country
                                                "
                                                class="form-select"
                                                name="Country"
                                                required
                                            >
                                                <option
                                                    v-for="c in countries"
                                                    :key="c.code"
                                                    :value="c.code"
                                                >
                                                    {{ c.name }}
                                                </option>
                                            </select>
                                        </div>
                                    </div>
                                    <div class="row mb-2">
                                        <div class="col-md-2">&nbsp;</div>
                                        <div class="col-md-6">
                                            <div class="form-check form-switch">
                                                <label
                                                    for="billingPostcodeSame"
                                                    class="form-label"
                                                >
                                                    Billing Address same as
                                                    Postal Address</label
                                                >
                                                <input
                                                    id="toggleBillingAddressFieldsDisabled"
                                                    v-model="
                                                        org.billing_same_as_postal
                                                    "
                                                    class="form-check-input"
                                                    type="checkbox"
                                                    @change="
                                                        toggleBillingAddressFieldsDisabled
                                                    "
                                                />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </fieldset>

                            <fieldset
                                class="mb-3"
                                :disabled="org.billing_same_as_postal"
                            >
                                <legend>Billing Address</legend>
                                <div class="address-box">
                                    <div class="row mb-2">
                                        <div class="col-md-2">
                                            <label
                                                for="billingAddressLine1"
                                                class="form-label"
                                                >Street</label
                                            >
                                        </div>
                                        <div class="col-md-4">
                                            <input
                                                id="billingAddressLine1"
                                                v-model="
                                                    org.billing_address
                                                        .billing_line1
                                                "
                                                type="text"
                                                class="form-control billing-address"
                                                name="billingAddressLine1"
                                                required
                                            />
                                        </div>
                                    </div>

                                    <div class="row mb-2">
                                        <div class="col-md-2">
                                            <label
                                                for="billingLocality"
                                                class="form-label"
                                                >Town/Suburb</label
                                            >
                                        </div>
                                        <div class="col-md-4">
                                            <input
                                                id="billingLocality"
                                                v-model="
                                                    org.billing_address
                                                        .billing_locality
                                                "
                                                type="text"
                                                class="form-control billing-address"
                                                name="billingLocality"
                                                required
                                            />
                                        </div>
                                    </div>

                                    <div class="row mb-2">
                                        <div class="col-md-2">
                                            <label
                                                for="billingState"
                                                class="form-label"
                                                >State</label
                                            >
                                        </div>
                                        <div class="col-md-4">
                                            <input
                                                id="billingState"
                                                v-model="
                                                    org.billing_address
                                                        .billing_state
                                                "
                                                type="text"
                                                class="form-control billing-address"
                                                name="billingState"
                                                required
                                            />
                                        </div>
                                    </div>
                                    <div class="row mb-2">
                                        <div class="col-md-2">
                                            <label
                                                for="billingPostcode"
                                                class="form-label"
                                                >Postcode</label
                                            >
                                        </div>
                                        <div class="col-md-4">
                                            <input
                                                id="billingPostcode"
                                                v-model="
                                                    org.billing_address
                                                        .billing_postcode
                                                "
                                                type="text"
                                                class="form-control billing-address"
                                                name="billingPostcode"
                                                maxlength="10"
                                                required
                                            />
                                        </div>
                                    </div>
                                    <div class="row mb-4">
                                        <div class="col-md-2">
                                            <label
                                                for="billingPostcode"
                                                class="form-label"
                                                >Country</label
                                            >
                                        </div>
                                        <div class="col-md-4">
                                            <select
                                                id="country"
                                                v-model="
                                                    org.billing_address
                                                        .billing_country
                                                "
                                                class="form-select billing-address"
                                                name="Country"
                                                required
                                            >
                                                <option
                                                    v-for="c in countries"
                                                    :key="c.code"
                                                    :value="c.code"
                                                >
                                                    {{ c.name }}
                                                </option>
                                            </select>
                                        </div>
                                    </div>
                                </div>
                            </fieldset>

                            <BootstrapLoadingButton
                                text="Update"
                                :is-loading="updatingAddress"
                                class="btn btn-primary float-end"
                                @click="validateForm('address-details')"
                            />
                        </form>
                    </FormSection>

                    <FormSection
                        :form-collapse="true"
                        label="Contact Details"
                        index="contact-details"
                    >
                        <div class="row">
                            <div class="col">
                                <button
                                    style="margin-bottom: 10px"
                                    class="btn btn-primary float-end"
                                    @click.prevent="addContact()"
                                >
                                    Add Contact
                                </button>
                            </div>
                        </div>

                        <datatable
                            id="organisation_contacts_datatable"
                            ref="contacts_datatable"
                            :dt-options="contacts_options"
                            :dt-headers="contacts_headers"
                        />
                    </FormSection>

                    <FormSection
                        :form-collapse="false"
                        label="Account Pins"
                        index="account-pins"
                    >
                        <BootstrapAlert
                            type="warning"
                            icon="exclamation-triangle-fill"
                            class="ms-1"
                        >
                            <ul class="list-group">
                                <li class="list-group-item">
                                    You and your organisation are responsible
                                    for managing the distribution of pin codes.
                                </li>
                                <li class="list-group-item">
                                    If you are not sure which pin code to give
                                    to a staff member please call the Tourism
                                    and Concessions Branch on (08) 9219 9978.
                                </li>
                                <li class="list-group-item">
                                    Never provide these pin codes to people that
                                    are not authorised to
                                    apply/cancel/surrender/pay fees on behalf of
                                    this organisation.
                                </li>
                            </ul>
                        </BootstrapAlert>

                        <h5>Administrator Pins</h5>

                        <BootstrapAlert class="ms-1">
                            <ul class="list-group">
                                <li class="list-group-item">
                                    Provide the new user these pin codes if you
                                    want the them to have administrator
                                    privileges.
                                </li>
                                <li class="list-group-item">
                                    <div class="row">
                                        <div class="col-md-6">
                                            <div class="input-group mb-2 mt-1">
                                                <span
                                                    id="basic-addon1"
                                                    class="input-group-text pin-label"
                                                    >Admin Pin 1</span
                                                >
                                                <input
                                                    ref="admin-pin-1"
                                                    type="text"
                                                    class="form-control"
                                                    :value="org.pins.one"
                                                    aria-label="Username"
                                                    aria-describedby="basic-addon1"
                                                    readonly
                                                />
                                                <button
                                                    class="btn btn-secondary btn-copy input-group-text"
                                                    @click="
                                                        copyToClipboard(
                                                            'admin-pin-1'
                                                        )
                                                    "
                                                >
                                                    copy
                                                </button>
                                            </div>
                                        </div>
                                        <div class="col-md-6">
                                            <div class="input-group mb-2 mt-1">
                                                <span
                                                    id="basic-addon1"
                                                    class="input-group-text pin-label"
                                                    >Admin Pin 2</span
                                                >
                                                <input
                                                    ref="admin-pin-2"
                                                    type="text"
                                                    class="form-control"
                                                    :value="org.pins.two"
                                                    aria-label="Username"
                                                    aria-describedby="basic-addon1"
                                                    readonly
                                                />
                                                <button
                                                    class="btn btn-secondary btn-copy input-group-text"
                                                    @click="
                                                        copyToClipboard(
                                                            'admin-pin-2'
                                                        )
                                                    "
                                                >
                                                    copy
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </li>
                            </ul>
                        </BootstrapAlert>

                        <h5>User Pins</h5>

                        <BootstrapAlert class="ms-1">
                            <ul class="list-group">
                                <li class="list-group-item">
                                    Provide the new user these pin codes if you
                                    want the new user to be a regular user.
                                </li>
                                <li class="list-group-item">
                                    <div class="row">
                                        <div class="col-md-6">
                                            <div class="input-group mb-2 mt-1">
                                                <span
                                                    id="user-pin-1"
                                                    class="input-group-text pin-label"
                                                    >User Pin 1</span
                                                >
                                                <input
                                                    ref="user-pin-1"
                                                    type="text"
                                                    class="form-control"
                                                    :value="org.pins.three"
                                                    aria-label="Username"
                                                    aria-describedby="user-pin-1"
                                                    readonly
                                                />
                                                <button
                                                    class="btn btn-secondary btn-copy input-group-text"
                                                    @click="
                                                        copyToClipboard(
                                                            'user-pin-1'
                                                        )
                                                    "
                                                >
                                                    copy
                                                </button>
                                            </div>
                                        </div>
                                        <div class="col-md-6">
                                            <div class="input-group mb-2 mt-1">
                                                <span
                                                    id="basic-addon1"
                                                    class="input-group-text pin-label"
                                                    >User Pin 2</span
                                                >
                                                <input
                                                    ref="user-pin-2"
                                                    type="text"
                                                    class="form-control"
                                                    :value="org.pins.four"
                                                    aria-label="Username"
                                                    aria-describedby="basic-addon1"
                                                    readonly
                                                />
                                                <button
                                                    class="btn btn-secondary btn-copy input-group-text"
                                                    @click="
                                                        copyToClipboard(
                                                            'user-pin-2'
                                                        )
                                                    "
                                                >
                                                    copy
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </li>
                            </ul>
                        </BootstrapAlert>
                    </FormSection>

                    <FormSection
                        :form-collapse="false"
                        label="Linked User Accounts"
                        index="linked-user-accounts"
                    >
                        <BootstrapAlert
                            type="warning"
                            icon="exclamation-triangle-fill"
                            class="ms-1"
                        >
                            The list of users linked to your organisation is
                            controlled by you and your organisation. The
                            Department cannot manage this list.
                        </BootstrapAlert>

                        <div>
                            <datatable
                                id="organisation_contacts_datatable_ref"
                                ref="contacts_datatable_user"
                                :dt-options="contacts_options_ref"
                                :dt-headers="contacts_headers_ref"
                            />
                        </div>
                    </FormSection>
                </div>
                <AddContact ref="add_contact" :org_id="org.id" />
            </div>
            <div v-else>
                <BootstrapSpinner class="text-primary" :is-loading="true" />
            </div>
        </div>
    </div>
</template>

<script>
import { api_endpoints, constants, helpers, utils } from '@/utils/hooks';
import datatable from '@vue-utils/datatable.vue';
import AddContact from '@common-utils/add_contact.vue';
import BootstrapLoadingButton from '../../../utils/vue/BootstrapLoadingButton.vue';
import swal from 'sweetalert2';

export default {
    name: 'ManageOrganisation',
    components: {
        datatable,
        AddContact,
        BootstrapLoadingButton,
    },
    beforeRouteEnter: function (to, from, next) {
        let initialisers = [
            utils.fetchCountries(),
            utils.fetchOrganisation(to.params.org_id),
            utils.fetchOrganisationAddress(to.params.org_id),
            utils.fetchOrganisationPermissions(to.params.org_id),
        ];
        Promise.all(initialisers).then((data) => {
            next((vm) => {
                vm.countries = data[0];
                vm.org = Object.assign({}, data[1], data[2]);
                vm.myorgperms = data[3];
                vm.org.postal_address =
                    vm.org.postal_address != null ? vm.org.postal_address : {};
                vm.org.billing_address =
                    vm.org.billing_address != null
                        ? vm.org.billing_address
                        : {};
                vm.org.billing_same_as_postal =
                    vm.isBillingAddressSame != null
                        ? vm.isBillingAddressSame
                        : {};
                // vm.org.pins = vm.org.pins != null ? vm.org.pins : {};
            });
        });
    },
    beforeRouteUpdate: function (to, from, next) {
        let initialisers = [
            utils.fetchOrganisation(to.params.org_id),
            utils.fetchOrganisationPermissions(to.params.org_id),
            utils.fetchOrganisationAddress(to.params.org_id),
        ];
        Promise.all(initialisers).then((data) => {
            next((vm) => {
                vm.org = Object.assign({}, data[0], data[2]);
                vm.myorgperms = data[1];
                vm.org.postal_address =
                    vm.org.postal_address != null ? vm.org.postal_address : {};
                vm.org.billing_address =
                    vm.org.billing_address != null
                        ? vm.org.billing_address
                        : {};
                vm.org.billing_same_as_postal =
                    vm.isBillingAddressSame != null
                        ? vm.isBillingAddressSame
                        : {};
                // vm.org.address = vm.org.address != null ? vm.org.address : {};
                // vm.org.pins = vm.org.pins != null ? vm.org.pins : {};
            });
        });
    },
    props: {
        isApplication: {
            type: Boolean,
            default: false,
        },
    },
    data() {
        let vm = this;
        return {
            adBody: 'adBody' + vm._uid,
            pBody: 'pBody' + vm._uid,
            cBody: 'cBody' + vm._uid,
            oBody: 'oBody' + vm._uid,
            org: null,
            loading: [],
            countries: [],
            contact_user: {
                first_name: null,
                last_name: null,
                email: null,
                mobile_number: null,
                phone_number: null,
            },
            updatingDetails: false,
            updatingAddress: false,
            updatingContact: false,
            logsTable: null,
            myorgperms: null,
            DATE_TIME_FORMAT: 'DD/MM/YYYY HH:mm:ss',
            logsDtOptions: {
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML,
                },
                responsive: true,
                deferRender: true,
                autowidth: true,
                order: [[2, 'desc']],
                dom:
                    "<'row'<'col-sm-5'l><'col-sm-6'f>>" +
                    "<'row'<'col-sm-12'tr>>" +
                    "<'row'<'col-sm-5'i><'col-sm-7'p>>",
                processing: true,
                ajax: {
                    url: helpers.add_endpoint_json(
                        api_endpoints.organisations,
                        vm.$route.params.org_id + '/action_log'
                    ),
                    dataSrc: '',
                },
                columns: [
                    {
                        data: 'who',
                    },
                    {
                        data: 'what',
                    },
                    {
                        data: 'when',
                        mRender: function (data) {
                            return moment(data).format(vm.DATE_TIME_FORMAT);
                        },
                    },
                ],
            },
            commsDtOptions: {
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML,
                },
                responsive: true,
                deferRender: true,
                autowidth: true,
                order: [[0, 'desc']],
                processing: true,
                ajax: {
                    url: helpers.add_endpoint_json(
                        api_endpoints.organisations,
                        vm.$route.params.org_id + '/comms_log'
                    ),
                    dataSrc: '',
                },
                columns: [
                    {
                        title: 'Date',
                        data: 'created',
                        render: function (date) {
                            return moment(date).format(vm.DATE_TIME_FORMAT);
                        },
                    },
                    {
                        title: 'Type',
                        data: 'type',
                    },
                    {
                        title: 'Reference',
                        data: 'reference',
                    },
                    {
                        title: 'To',
                        data: 'to',
                        render: vm.commaToNewline,
                    },
                    {
                        title: 'CC',
                        data: 'cc',
                        render: vm.commaToNewline,
                    },
                    {
                        title: 'From',
                        data: 'fromm',
                        render: vm.commaToNewline,
                    },
                    {
                        title: 'Subject/Desc.',
                        data: 'subject',
                    },
                    {
                        title: 'Text',
                        data: 'text',
                        render: function (value) {
                            var ellipsis = '...',
                                truncated = _.truncate(value, {
                                    length: 100,
                                    omission: ellipsis,
                                    separator: ' ',
                                }),
                                result = '<span>' + truncated + '</span>',
                                popTemplate = _.template(
                                    '<a href="#" ' +
                                        'role="button" ' +
                                        'data-toggle="popover" ' +
                                        'data-trigger="click" ' +
                                        'data-placement="top auto"' +
                                        'data-html="true" ' +
                                        'data-content="<%= text %>" ' +
                                        '>more</a>'
                                );
                            if (_.endsWith(truncated, ellipsis)) {
                                result += popTemplate({
                                    text: value,
                                });
                            }

                            return result;
                        },
                        createdCell: function (cell) {
                            //TODO why this is not working?
                            // the call to popover is done in the 'draw' event
                            $(cell).popover();
                        },
                    },
                    {
                        title: 'Documents',
                        data: 'documents',
                        render: function (values) {
                            var result = '';
                            _.forEach(values, function (value) {
                                // We expect an array [docName, url]
                                // if it's a string it is the url
                                var docName = '',
                                    url = '';
                                if (_.isArray(value) && value.length > 1) {
                                    docName = value[0];
                                    url = value[1];
                                }
                                if (typeof s === 'string') {
                                    url = value;
                                    // display the first  chars of the filename
                                    docName = _.last(value.split('/'));
                                    docName = _.truncate(docName, {
                                        length: 18,
                                        omission: '...',
                                        separator: ' ',
                                    });
                                }
                                result +=
                                    '<a href="' +
                                    url +
                                    '" target="_blank"><p>' +
                                    docName +
                                    '</p></a><br>';
                            });
                            return result;
                        },
                    },
                ],
            },
            commsTable: null,

            contacts_headers: [
                'Name',
                'Phone',
                'Mobile',
                'Fax',
                'Email',
                'Action',
            ],
            contacts_options: {
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML,
                },
                responsive: true,
                ajax: {
                    url: helpers.add_endpoint_json(
                        api_endpoints.organisations,
                        vm.$route.params.org_id + '/contacts'
                    ),
                    dataSrc: '',
                },
                columns: [
                    {
                        data: 'id',
                        mRender: function (data, type, full) {
                            return full.first_name + ' ' + full.last_name;
                        },
                    },
                    { data: 'phone_number' },
                    { data: 'mobile_number' },
                    { data: 'fax_number' },
                    { data: 'email' },
                    {
                        data: 'id',
                        mRender: function (data, type, full) {
                            let links = '';
                            let name = full.first_name + ' ' + full.last_name;
                            links += `<a data-email='${full.email}' data-name='${name}' data-id='${full.id}' class="remove-contact">Remove</a><br/>`;
                            return links;
                        },
                    },
                ],
                processing: true,
            },

            contacts_headers_ref: ['Name', 'Role', 'Email', 'Status', 'Action'],
            contacts_options_ref: {
                language: {
                    processing: constants.DATATABLE_PROCESSING_HTML,
                },
                responsive: true,
                ajax: {
                    url: helpers.add_endpoint_json(
                        api_endpoints.organisations,
                        vm.$route.params.org_id + '/contacts_exclude'
                    ),
                    dataSrc: '',
                },
                columns: [
                    {
                        data: 'id',
                        mRender: function (data, type, full) {
                            return full.first_name + ' ' + full.last_name;
                        },
                    },
                    { data: 'user_role' },
                    { data: 'email' },
                    { data: 'user_status' },
                    {
                        data: 'id',
                        mRender: function (data, type, full) {
                            let links = '';
                            if (vm.myorgperms.is_admin) {
                                if (full.user_status == 'Pending') {
                                    links += `<a data-email='${full.email}' data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="accept_contact">Accept</a><br/>`;
                                    links += `<a data-email='${full.email}'  data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="decline_contact">Decline</a><br/>`;
                                } else if (full.user_status == 'Suspended') {
                                    links += `<a data-email='${full.email}' data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="reinstate_contact">Reinstate</a><br/>`;
                                } else if (full.user_status == 'Active') {
                                    links += `<a data-email='${full.email}' data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="unlink_contact">Unlink</a><br/>`;
                                    links += `<a data-email='${full.email}'  data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="suspend_contact">Suspend</a><br/>`;
                                    if (full.user_role == 'Organisation User') {
                                        links += `<a data-email='${full.email}'  data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="make_admin_contact">Make Organisation Admin</a><br/>`;
                                    } else {
                                        links += `<a data-email='${full.email}'  data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="make_user_contact">Make Organisation User</a><br/>`;
                                    }
                                } else if (full.user_status == 'Unlinked') {
                                    links += `<a data-email='${full.email}'  data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="relink_contact">Reinstate</a><br/>`;
                                } else if (full.user_status == 'Declined') {
                                    links += `<a data-email='${full.email}'  data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="accept_declined_contact">Accept (Previously Declined)</a><br/>`;
                                }
                            }
                            return links;
                        },
                    },
                ],
                processing: true,
            },
        };
    },
    computed: {
        classCompute: function () {
            return this.isApplication ? 'row' : 'container';
        },
        isBillingAddressSame: function () {
            return (
                Object.values(this.org.postal_address).toString() ==
                Object.values(this.org.billing_address).toString()
            );
        },
    },
    created: function () {
        let vm = this;
        this.personal_form = document.forms.personal_form;
        let initialisers = [
            utils.fetchCountries(),
            utils.fetchOrganisation(vm.$route.params.org_id),
            // Todo: It shouldn't be necessary to do an additional fetch to get the address details
            // Ledger gw api has been updated to return the address details in the fetchOrganisation call
            utils.fetchOrganisationAddress(vm.$route.params.org_id),
            utils.fetchOrganisationPermissions(vm.$route.params.org_id),
        ];
        Promise.all(initialisers).then((data) => {
            vm.countries = data[0];
            vm.org = Object.assign({}, data[1], data[2]);
            vm.myorgperms = data[3];
            vm.org.postal_address =
                vm.org.postal_address != null ? vm.org.postal_address : {};
            vm.org.billing_address =
                vm.org.billing_address != null ? vm.org.billing_address : {};
            vm.org.billing_same_as_postal =
                vm.isBillingAddressSame != null ? vm.isBillingAddressSame : {};
        });
    },
    mounted: function () {
        this.personal_form = document.forms.personal_form;
    },
    updated: function () {
        $('.panelClicker[data-toggle="collapse"]').on('click', function () {
            var chev = $(this).children()[0];
            window.setTimeout(function () {
                $(chev).toggleClass(
                    'glyphicon-chevron-down glyphicon-chevron-up'
                );
            }, 100);
        });
        this.$nextTick(() => {
            this.eventListeners();
        });
    },
    methods: {
        addContact: function () {
            this.$refs.add_contact.isModalOpen = true;
        },
        toggleBillingAddressFieldsDisabled: function () {
            if (!this.org.billing_same_as_postal) {
                $('.billing-address').first().focus();
            } else {
                this.org.billing_address.billing_line1 =
                    this.org.postal_address.postal_line1;
                this.org.billing_address.billing_locality =
                    this.org.postal_address.postal_locality;
                this.org.billing_address.billing_state =
                    this.org.postal_address.postal_state;
                this.org.billing_address.billing_postcode =
                    this.org.postal_address.postal_postcode;
                this.org.billing_address.billing_country =
                    this.org.postal_address.postal_country;
            }
        },
        eventListeners: function () {
            let vm = this;
            if (typeof vm.$refs.contacts_datatable !== 'undefined') {
                vm.$refs.contacts_datatable.vmDataTable.on(
                    'click',
                    '.remove-contact',
                    (e) => {
                        e.preventDefault();

                        let name = $(e.target).data('name');
                        let email = $(e.target).data('email');
                        let id = $(e.target).data('id');
                        swal({
                            title: 'Delete Contact',
                            text:
                                'Are you sure you want to remove ' +
                                name +
                                '(' +
                                email +
                                ') as a contact  ?',
                            type: 'error',
                            showCancelButton: true,
                            confirmButtonText: 'Accept',
                        }).then(
                            () => {
                                vm.deleteContact(id);
                            },
                            (error) => {
                                console.error(error);
                            }
                        );
                    }
                );

                vm.$refs.contacts_datatable_user.vmDataTable.on(
                    'click',
                    '.accept_contact',
                    (e) => {
                        e.preventDefault();
                        let firstname = $(e.target).data('firstname');
                        let lastname = $(e.target).data('lastname');
                        let name = firstname + ' ' + lastname;
                        let email = $(e.target).data('email');
                        let mobile = $(e.target).data('mobile');
                        let phone = $(e.target).data('phone');
                        vm.contact_user.first_name = firstname;
                        vm.contact_user.last_name = lastname;
                        vm.contact_user.email = email;
                        vm.contact_user.mobile_number = mobile;
                        vm.contact_user.phone_number = phone;
                        swal({
                            title: 'Contact Accept',
                            text:
                                'Are you sure you want to accept contact request ' +
                                name +
                                ' (' +
                                email +
                                ')?',
                            showCancelButton: true,
                            confirmButtonText: 'Accept',
                        }).then(
                            (result) => {
                                if (result) {
                                    vm.$http
                                        .post(
                                            helpers.add_endpoint_json(
                                                api_endpoints.organisations,
                                                vm.org.id + '/accept_user'
                                            ),
                                            JSON.stringify(vm.contact_user),
                                            {
                                                emulateJSON: true,
                                            }
                                        )
                                        .then(
                                            () => {
                                                swal({
                                                    title: 'Contact Accept',
                                                    text:
                                                        'You have successfully accepted ' +
                                                        name +
                                                        '.',
                                                    type: 'success',
                                                    confirmButtonText: 'OK',
                                                }).then(
                                                    () => {
                                                        vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                                    },
                                                    (error) => {
                                                        console.error(error);
                                                    }
                                                );
                                            },
                                            (error) => {
                                                swal(
                                                    'Contact Accept',
                                                    'There was an error accepting ' +
                                                        name +
                                                        '.',
                                                    'error'
                                                );
                                                console.error(error);
                                            }
                                        );
                                }
                            },
                            (error) => {
                                console.error(error);
                            }
                        );
                    }
                );
                vm.$refs.contacts_datatable_user.vmDataTable.on(
                    'click',
                    '.accept_declined_contact',
                    (e) => {
                        e.preventDefault();
                        let firstname = $(e.target).data('firstname');
                        let lastname = $(e.target).data('lastname');
                        let name = firstname + ' ' + lastname;
                        let email = $(e.target).data('email');
                        let mobile = $(e.target).data('mobile');
                        let phone = $(e.target).data('phone');
                        vm.contact_user.first_name = firstname;
                        vm.contact_user.last_name = lastname;
                        vm.contact_user.email = email;
                        vm.contact_user.mobile_number = mobile;
                        vm.contact_user.phone_number = phone;
                        swal({
                            title: 'Contact Accept (Previously Declined)',
                            text:
                                'Are you sure you want to accept the previously declined contact request for ' +
                                name +
                                ' (' +
                                email +
                                ')?',
                            showCancelButton: true,
                            confirmButtonText: 'Accept',
                        }).then(
                            (result) => {
                                if (result.value) {
                                    vm.$http
                                        .post(
                                            helpers.add_endpoint_json(
                                                api_endpoints.organisations,
                                                vm.org.id +
                                                    '/accept_declined_user'
                                            ),
                                            JSON.stringify(vm.contact_user),
                                            {
                                                emulateJSON: true,
                                            }
                                        )
                                        .then(
                                            () => {
                                                swal({
                                                    title: 'Contact Accept (Previously Declined)',
                                                    text:
                                                        'You have successfully accepted ' +
                                                        name +
                                                        '.',
                                                    type: 'success',
                                                    confirmButtonText: 'OK',
                                                }).then(
                                                    () => {
                                                        vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                                    },
                                                    (error) => {
                                                        console.error(error);
                                                    }
                                                );
                                            },
                                            (error) => {
                                                swal(
                                                    'Contact Accept (Previously Declined)',
                                                    'There was an error accepting ' +
                                                        name +
                                                        '.',
                                                    'error'
                                                );
                                                console.error(error);
                                            }
                                        );
                                }
                            },
                            (error) => {
                                console.error(error);
                            }
                        );
                    }
                );
                vm.$refs.contacts_datatable_user.vmDataTable.on(
                    'click',
                    '.decline_contact',
                    (e) => {
                        e.preventDefault();
                        let firstname = $(e.target).data('firstname');
                        let lastname = $(e.target).data('lastname');
                        let name = firstname + ' ' + lastname;
                        let email = $(e.target).data('email');
                        let mobile = $(e.target).data('mobile');
                        let phone = $(e.target).data('phone');
                        vm.contact_user.first_name = firstname;
                        vm.contact_user.last_name = lastname;
                        vm.contact_user.email = email;
                        vm.contact_user.mobile_number = mobile;
                        vm.contact_user.phone_number = phone;
                        swal({
                            title: 'Contact Decline',
                            text:
                                'Are you sure you want to decline the contact request for ' +
                                name +
                                ' (' +
                                email +
                                ')?',
                            showCancelButton: true,
                            confirmButtonText: 'Accept',
                        }).then(
                            (result) => {
                                if (result) {
                                    vm.$http
                                        .post(
                                            helpers.add_endpoint_json(
                                                api_endpoints.organisations,
                                                vm.org.id + '/decline_user'
                                            ),
                                            JSON.stringify(vm.contact_user),
                                            {
                                                emulateJSON: true,
                                            }
                                        )
                                        .then(
                                            () => {
                                                swal({
                                                    title: 'Contact Decline',
                                                    text:
                                                        'You have successfully declined ' +
                                                        name +
                                                        '.',
                                                    type: 'success',
                                                    confirmButtonText: 'OK',
                                                }).then(
                                                    () => {
                                                        vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                                    },
                                                    (error) => {
                                                        console.error(error);
                                                    }
                                                );
                                            },
                                            (error) => {
                                                swal(
                                                    'Contact Decline',
                                                    'There was an error declining ' +
                                                        name +
                                                        '.',
                                                    'error'
                                                );
                                                console.error(error);
                                            }
                                        );
                                }
                            },
                            (error) => {
                                console.error(error);
                            }
                        );
                    }
                );
                vm.$refs.contacts_datatable_user.vmDataTable.on(
                    'click',
                    '.unlink_contact',
                    (e) => {
                        e.preventDefault();
                        let firstname = $(e.target).data('firstname');
                        let lastname = $(e.target).data('lastname');
                        let name = firstname + ' ' + lastname;
                        let email = $(e.target).data('email');
                        let mobile = $(e.target).data('mobile');
                        let phone = $(e.target).data('phone');
                        vm.contact_user.first_name = firstname;
                        vm.contact_user.last_name = lastname;
                        vm.contact_user.email = email;
                        vm.contact_user.mobile_number = mobile;
                        vm.contact_user.phone_number = phone;
                        swal({
                            title: 'Unlink',
                            text:
                                'Are you sure you want to unlink ' +
                                name +
                                ' (' +
                                email +
                                ')?',
                            showCancelButton: true,
                            confirmButtonText: 'Accept',
                        }).then(
                            (result) => {
                                if (result) {
                                    vm.$http
                                        .post(
                                            helpers.add_endpoint_json(
                                                api_endpoints.organisations,
                                                vm.org.id + '/unlink_user'
                                            ),
                                            JSON.stringify(vm.contact_user),
                                            {
                                                emulateJSON: true,
                                            }
                                        )
                                        .then(
                                            () => {
                                                swal({
                                                    title: 'Unlink',
                                                    text:
                                                        'You have successfully unlinked ' +
                                                        name +
                                                        '.',
                                                    type: 'success',
                                                    confirmButtonText: 'OK',
                                                }).then(
                                                    () => {
                                                        vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                                    },
                                                    (error) => {
                                                        console.error(error);
                                                    }
                                                );
                                            },
                                            (error) => {
                                                if (error.status == 500) {
                                                    swal(
                                                        'Unlink',
                                                        'Last Organisation Admin can not be unlinked.',
                                                        'error'
                                                    );
                                                } else {
                                                    swal(
                                                        'Unlink',
                                                        'There was an error unlinking this user ' +
                                                            error,
                                                        'error'
                                                    );
                                                }
                                            }
                                        );
                                }
                            },
                            (error) => {
                                console.error(error);
                            }
                        );
                    }
                );
                vm.$refs.contacts_datatable_user.vmDataTable.on(
                    'click',
                    '.make_admin_contact',
                    (e) => {
                        e.preventDefault();
                        let firstname = $(e.target).data('firstname');
                        let lastname = $(e.target).data('lastname');
                        let name = firstname + ' ' + lastname;
                        let email = $(e.target).data('email');
                        let mobile = $(e.target).data('mobile');
                        let phone = $(e.target).data('phone');
                        vm.contact_user.first_name = firstname;
                        vm.contact_user.last_name = lastname;
                        vm.contact_user.email = email;
                        vm.contact_user.mobile_number = mobile;
                        vm.contact_user.phone_number = phone;
                        swal({
                            title: 'Organisation Admin',
                            text:
                                'Are you sure you want to make ' +
                                name +
                                ' (' +
                                email +
                                ') an Organisation Admin?',
                            showCancelButton: true,
                            confirmButtonText: 'Accept',
                        }).then(
                            (result) => {
                                if (result) {
                                    vm.$http
                                        .post(
                                            helpers.add_endpoint_json(
                                                api_endpoints.organisations,
                                                vm.org.id + '/make_admin_user'
                                            ),
                                            JSON.stringify(vm.contact_user),
                                            {
                                                emulateJSON: true,
                                            }
                                        )
                                        .then(
                                            () => {
                                                swal({
                                                    title: 'Organisation Admin',
                                                    text:
                                                        'You have successfully made ' +
                                                        name +
                                                        ' an Organisation Admin.',
                                                    type: 'success',
                                                    confirmButtonText: 'OK',
                                                }).then(
                                                    () => {
                                                        vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                                    },
                                                    (error) => {
                                                        console.error(error);
                                                    }
                                                );
                                            },
                                            (error) => {
                                                swal(
                                                    'Organisation Admin',
                                                    'There was an error making ' +
                                                        name +
                                                        ' an Organisation Admin.',
                                                    'error'
                                                );
                                                console.error(error);
                                            }
                                        );
                                }
                            },
                            (error) => {
                                console.error(error);
                            }
                        );
                    }
                );
                vm.$refs.contacts_datatable_user.vmDataTable.on(
                    'click',
                    '.make_user_contact',
                    (e) => {
                        e.preventDefault();
                        let firstname = $(e.target).data('firstname');
                        let lastname = $(e.target).data('lastname');
                        let name = firstname + ' ' + lastname;
                        let email = $(e.target).data('email');
                        let mobile = $(e.target).data('mobile');
                        let phone = $(e.target).data('phone');
                        vm.contact_user.first_name = firstname;
                        vm.contact_user.last_name = lastname;
                        vm.contact_user.email = email;
                        vm.contact_user.mobile_number = mobile;
                        vm.contact_user.phone_number = phone;
                        swal({
                            title: 'Organisation User',
                            text:
                                'Are you sure you want to make ' +
                                name +
                                ' (' +
                                email +
                                ') an Organisation User?',
                            showCancelButton: true,
                            confirmButtonText: 'Accept',
                        }).then(
                            (result) => {
                                if (result) {
                                    vm.$http
                                        .post(
                                            helpers.add_endpoint_json(
                                                api_endpoints.organisations,
                                                vm.org.id + '/make_user'
                                            ),
                                            JSON.stringify(vm.contact_user),
                                            {
                                                emulateJSON: true,
                                            }
                                        )
                                        .then(
                                            () => {
                                                swal({
                                                    title: 'Organisation User',
                                                    text:
                                                        'You have successfully made ' +
                                                        name +
                                                        ' an Organisation User.',
                                                    type: 'success',
                                                    confirmButtonText: 'OK',
                                                }).then(
                                                    () => {
                                                        vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                                    },
                                                    (error) => {
                                                        console.error(error);
                                                    }
                                                );
                                            },
                                            (error) => {
                                                console.error(error);
                                                let text =
                                                    helpers.apiVueResourceError(
                                                        error
                                                    );
                                                swal(
                                                    'Company Admin',
                                                    'There was an error making ' +
                                                        name +
                                                        ' an Organisation User. ' +
                                                        text,
                                                    'error'
                                                );
                                            }
                                        );
                                }
                            },
                            (error) => {
                                console.error(error);
                            }
                        );
                    }
                );
                vm.$refs.contacts_datatable_user.vmDataTable.on(
                    'click',
                    '.suspend_contact',
                    (e) => {
                        e.preventDefault();
                        let firstname = $(e.target).data('firstname');
                        let lastname = $(e.target).data('lastname');
                        let name = firstname + ' ' + lastname;
                        let email = $(e.target).data('email');
                        let mobile = $(e.target).data('mobile');
                        let phone = $(e.target).data('phone');
                        vm.contact_user.first_name = firstname;
                        vm.contact_user.last_name = lastname;
                        vm.contact_user.email = email;
                        vm.contact_user.mobile_number = mobile;
                        vm.contact_user.phone_number = phone;
                        swal({
                            title: 'Suspend User',
                            text:
                                'Are you sure you want to Suspend  ' +
                                name +
                                ' (' +
                                email +
                                ')?',
                            showCancelButton: true,
                            confirmButtonText: 'Accept',
                        }).then(
                            (result) => {
                                if (result) {
                                    vm.$http
                                        .post(
                                            helpers.add_endpoint_json(
                                                api_endpoints.organisations,
                                                vm.org.id + '/suspend_user'
                                            ),
                                            JSON.stringify(vm.contact_user),
                                            {
                                                emulateJSON: true,
                                            }
                                        )
                                        .then(
                                            () => {
                                                swal({
                                                    title: 'Suspend User',
                                                    text:
                                                        'You have successfully suspended ' +
                                                        name +
                                                        ' as a User.',
                                                    type: 'success',
                                                    confirmButtonText: 'OK',
                                                }).then(
                                                    () => {
                                                        vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                                    },
                                                    (error) => {
                                                        console.error(error);
                                                    }
                                                );
                                            },
                                            (error) => {
                                                swal(
                                                    'Suspend User',
                                                    'There was an error suspending ' +
                                                        name +
                                                        ' as a User.',
                                                    'error'
                                                );
                                                console.error(error);
                                            }
                                        );
                                }
                            },
                            (error) => {
                                console.error(error);
                            }
                        );
                    }
                );
                vm.$refs.contacts_datatable_user.vmDataTable.on(
                    'click',
                    '.reinstate_contact',
                    (e) => {
                        e.preventDefault();
                        let firstname = $(e.target).data('firstname');
                        let lastname = $(e.target).data('lastname');
                        let name = firstname + ' ' + lastname;
                        let email = $(e.target).data('email');
                        let mobile = $(e.target).data('mobile');
                        let phone = $(e.target).data('phone');
                        vm.contact_user.first_name = firstname;
                        vm.contact_user.last_name = lastname;
                        vm.contact_user.email = email;
                        vm.contact_user.mobile_number = mobile;
                        vm.contact_user.phone_number = phone;
                        swal({
                            title: 'Reinstate User',
                            text:
                                'Are you sure you want to Reinstate  ' +
                                name +
                                ' (' +
                                email +
                                ')?',
                            showCancelButton: true,
                            confirmButtonText: 'Accept',
                        }).then(
                            (result) => {
                                if (result) {
                                    vm.$http
                                        .post(
                                            helpers.add_endpoint_json(
                                                api_endpoints.organisations,
                                                vm.org.id + '/reinstate_user'
                                            ),
                                            JSON.stringify(vm.contact_user),
                                            {
                                                emulateJSON: true,
                                            }
                                        )
                                        .then(
                                            () => {
                                                swal({
                                                    title: 'Reinstate User',
                                                    text:
                                                        'You have successfully reinstated ' +
                                                        name +
                                                        '.',
                                                    type: 'success',
                                                    confirmButtonText: 'OK',
                                                }).then(
                                                    () => {
                                                        vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                                    },
                                                    (error) => {
                                                        console.error(error);
                                                    }
                                                );
                                            },
                                            (error) => {
                                                swal(
                                                    'Reinstate User',
                                                    'There was an error reinstating ' +
                                                        name +
                                                        '.',
                                                    'error'
                                                );
                                                console.error(error);
                                            }
                                        );
                                }
                            },
                            (error) => {
                                console.error(error);
                            }
                        );
                    }
                );
                vm.$refs.contacts_datatable_user.vmDataTable.on(
                    'click',
                    '.relink_contact',
                    (e) => {
                        e.preventDefault();
                        let firstname = $(e.target).data('firstname');
                        let lastname = $(e.target).data('lastname');
                        let name = firstname + ' ' + lastname;
                        let email = $(e.target).data('email');
                        let mobile = $(e.target).data('mobile');
                        let phone = $(e.target).data('phone');
                        vm.contact_user.first_name = firstname;
                        vm.contact_user.last_name = lastname;
                        vm.contact_user.email = email;
                        vm.contact_user.mobile_number = mobile;
                        vm.contact_user.phone_number = phone;
                        swal({
                            title: 'Relink User',
                            text:
                                'Are you sure you want to Relink  ' +
                                name +
                                ' (' +
                                email +
                                ')?',
                            showCancelButton: true,
                            confirmButtonText: 'Accept',
                        }).then(
                            (result) => {
                                if (result) {
                                    vm.$http
                                        .post(
                                            helpers.add_endpoint_json(
                                                api_endpoints.organisations,
                                                vm.org.id + '/relink_user'
                                            ),
                                            JSON.stringify(vm.contact_user),
                                            {
                                                emulateJSON: true,
                                            }
                                        )
                                        .then(
                                            () => {
                                                swal({
                                                    title: 'Relink User',
                                                    text:
                                                        'You have successfully relinked ' +
                                                        name +
                                                        '.',
                                                    type: 'success',
                                                    confirmButtonText: 'OK',
                                                }).then(
                                                    () => {
                                                        vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                                    },
                                                    (error) => {
                                                        console.error(error);
                                                    }
                                                );
                                            },
                                            (error) => {
                                                swal(
                                                    'Relink User',
                                                    'There was an error relink ' +
                                                        name +
                                                        '.',
                                                    'error'
                                                );
                                                console.error(error);
                                            }
                                        );
                                }
                            },
                            (error) => {
                                console.error(error);
                            }
                        );
                    }
                );
            } // endif
        },
        updateDetails_noconfirm: function () {
            let vm = this;
            vm.$http.post(
                helpers.add_endpoint_json(
                    api_endpoints.organisations,
                    vm.org.id + '/update_details'
                ),
                JSON.stringify(vm.org),
                {
                    emulateJSON: true,
                }
            );
        },
        validateForm: function (formId) {
            let vm = this;
            var form = document.getElementById(formId);

            if (form.checkValidity()) {
                if (formId == 'address-details') {
                    const code1 = vm.org.postal_address.postal_postcode;
                    const code2 = vm.org.billing_address.billing_postcode;
                    if (
                        isNaN(Number.parseInt(code1)) ||
                        isNaN(Number.parseInt(code2))
                    ) {
                        swal.fire(
                            'Failure updating organisation details.',
                            'Postcode should only contain numeric value.',
                            'error'
                        );
                    } else {
                        vm.updateAddress();
                    }
                } else if (formId == 'organisation-details') {
                    vm.updateDetails();
                }
            } else {
                form.classList.add('was-validated');
                $(form).find('input:invalid').first().focus();
            }
            return false;
        },
        updateDetails: function () {
            let vm = this;
            vm.updatingDetails = true;
            let payload = JSON.stringify({
                organisation_id: vm.org.ledger_organisation_id,
                organisation_name: vm.org.ledger_organisation_name
                    ? vm.org.ledger_organisation_name
                    : null,
                organisation_abn: vm.org.ledger_organisation_abn,
                organisation_email: vm.org.ledger_organisation_email,
                organisation_trading_name:
                    vm.org.ledger_organisation_trading_name,
            });
            fetch(
                helpers.add_endpoint_json(
                    api_endpoints.organisations,
                    vm.org.id + '/update_details'
                ),
                {
                    method: 'PUT',
                    body: payload,
                }
            )
                .then(async (response) => {
                    const data = await response.json();
                    if (!response.ok) {
                        const error =
                            (data && data.message) || response.statusText;
                        return Promise.reject(error);
                    }
                    swal.fire(
                        'Success',
                        'Organisation details updated successfully.',
                        'success'
                    );
                })
                .catch((error) => {
                    swal.fire(
                        'Failure updating organisation details.',
                        'Something went wrong! Please try again.',
                        'error'
                    );
                    console.error(error);
                })
                .finally(() => {
                    vm.updatingDetails = false;
                });
        },
        addedContact: function () {
            let vm = this;
            swal(
                'Added',
                'The contact has been successfully added.',
                'success'
            );
            vm.$refs.contacts_datatable.vmDataTable.ajax.reload();
        },
        deleteContact: function (id) {
            let vm = this;

            vm.$http
                .delete(
                    helpers.add_endpoint_json(
                        api_endpoints.organisation_contacts,
                        id
                    ),
                    {
                        emulateJSON: true,
                    }
                )
                .then(
                    () => {
                        swal(
                            'Contact Deleted',
                            'The contact was successfully deleted',
                            'success'
                        );
                        vm.$refs.contacts_datatable.vmDataTable.ajax.reload();
                    },
                    (error) => {
                        console.error(error);
                        swal(
                            'Contact Deleted',
                            'The contact could not be deleted because of the following error ' +
                                error,
                            'error'
                        );
                    }
                );
        },
        updateAddress: function () {
            let vm = this;
            vm.updatingAddress = true;
            let payload = JSON.stringify({
                organisation_id: vm.org.ledger_organisation_id,
                postal_address: {
                    postal_line1: vm.org.postal_address.postal_line1,
                    postal_locality: vm.org.postal_address.postal_locality,
                    postal_state: vm.org.postal_address.postal_state,
                    postal_postcode: vm.org.postal_address.postal_postcode,
                    postal_country: vm.org.postal_address.postal_country,
                },
                billing_address: {
                    billing_line1: vm.org.billing_address.billing_line1,
                    billing_locality: vm.org.billing_address.billing_locality,
                    billing_state: vm.org.billing_address.billing_state,
                    billing_postcode: vm.org.billing_address.billing_postcode,
                    billing_country: vm.org.billing_address.billing_country,
                },
            });

            fetch(
                helpers.add_endpoint_json(
                    api_endpoints.organisations,
                    vm.org.id + '/update_address'
                ),
                {
                    method: 'POST',
                    body: payload,
                }
            )
                .then(async (response) => {
                    const data = await response.json();
                    if (!response.ok) {
                        const error =
                            (data && data.message) || response.statusText;
                        console.error(error);
                        return Promise.reject(error);
                    }
                    vm.org.billing_same_as_postal =
                        vm.isBillingAddressSame != null
                            ? vm.isBillingAddressSame
                            : {};
                    swal.fire(
                        'Success',
                        'Organisation address updated successfully',
                        'success'
                    );
                })
                .catch((error) => {
                    swal.fire(
                        'Failure updating organisation address.',
                        'Something went wrong! Please try again.',
                        'error'
                    );
                    console.error(error);
                })
                .finally(() => {
                    vm.updatingAddress = false;
                });
        },
        unlinkUser: function (d) {
            let vm = this;
            let org = vm.org;
            let org_name = org.name;
            let person = helpers.copyObject(d);
            swal({
                title: 'Unlink From Organisation',
                text:
                    'Are you sure you want to unlink ' +
                    person.name +
                    ' ' +
                    person.id +
                    ' from ' +
                    org.name +
                    ' ?',
                type: 'question',
                showCancelButton: true,
                confirmButtonText: 'Accept',
            }).then(
                () => {
                    vm.$http
                        .post(
                            helpers.add_endpoint_json(
                                api_endpoints.organisations,
                                org.id + '/unlink_user'
                            ),
                            { user: person.id },
                            {
                                emulateJSON: true,
                            }
                        )
                        .then(
                            (response) => {
                                vm.org = response.body;
                                if (vm.org.postal_address == null) {
                                    vm.org.postal_address = {};
                                }
                                if (vm.org.billing_address == null) {
                                    vm.org.billing_address = {};
                                }
                                swal(
                                    'Unlink',
                                    'You have successfully unlinked ' +
                                        person.name +
                                        ' from ' +
                                        org_name +
                                        '.',
                                    'success'
                                );
                            },
                            (error) => {
                                swal(
                                    'Unlink',
                                    'There was an error unlinking ' +
                                        person.name +
                                        ' from ' +
                                        org_name +
                                        '. ' +
                                        error.body,
                                    'error'
                                );
                            }
                        );
                },
                (error) => {
                    console.error(error);
                }
            );
        },
        copyToClipboard: function (refName) {
            var element = this.$refs[refName];
            var title = refName
                .replaceAll('-', ' ')
                .replace(/(?:^|\s|["'([{])+\S/g, (match) =>
                    match.toUpperCase()
                );
            try {
                // Access to navigator.clipboard requires https
                if (window.location.protocol == 'https:') {
                    navigator.clipboard.writeText(element.value);
                } else {
                    const textArea = document.createElement('textarea');
                    textArea.value = element.value;
                    document.body.appendChild(textArea);
                    textArea.focus();
                    textArea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textArea);
                }
                swal.fire({
                    title: `${title} copied to clipboard`,
                    icon: 'success',
                    timer: 1500,
                    showConfirmButton: false,
                });
            } catch (err) {
                swal.fire({
                    title: 'Copy Failed',
                    text: `Unable to access the clipboard`,
                    icon: 'error',
                });
                console.error('Unable to copy to clipboard', err);
            }
        },
    },
};
</script>

<style scoped>
.top-buffer-s {
    margin-top: 25px;
}

#organisation_contacts_datatable {
    width: 100% !important;
}

.btn-copy:hover {
    background-color: linear-gradient(rgb(0 0 0/40%) 0 0);
}

.pin-label {
    width: 120px;
}

input[readonly] {
    background-color: white;
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
input[type='number'] {
    -moz-appearance: textfield;
    appearance: textfield;
}
</style>
