<template lang="html">
    <div id="add-contact">
        <modal :title="title()" large @ok="validateForm">
            <form
                id="addContactForm"
                class="needs-validation form-horizontal"
                name="addContactForm"
                novalidate
            >
                <div class="row">
                    <alert v-model:show="showError" type="danger"
                        ><strong>{{ errorString }}</strong></alert
                    >
                    <div class="col-lg-12 ps-5 pe-5">
                        <div class="row mb-3 mt-3">
                            <label
                                for="first_name"
                                class="col-sm-3 col-form-label"
                                >Given Name(s):
                            </label>
                            <div class="col-sm-9">
                                <input
                                    id="first_name"
                                    ref="first_name"
                                    v-model="contact.first_name"
                                    type="text"
                                    class="form-control"
                                    name="first_name"
                                    required
                                />
                                <div class="invalid-feedback">
                                    Please enter your given names.
                                </div>
                            </div>
                        </div>

                        <div class="row mb-3">
                            <label
                                for="last_name"
                                class="col-sm-3 col-form-label"
                                >Last Name</label
                            >
                            <div class="col-sm-9">
                                <input
                                    v-model="contact.last_name"
                                    type="text"
                                    class="form-control"
                                    name="last_name"
                                    required
                                />
                                <div class="invalid-feedback">
                                    Please enter your last name.
                                </div>
                            </div>
                        </div>

                        <div class="row mb-3">
                            <label for="phone" class="col-sm-3 col-form-label"
                                >Phone
                            </label>
                            <div class="col-sm-9">
                                <input
                                    v-model="contact.phone_number"
                                    type="text"
                                    class="form-control"
                                    name="phone"
                                    minlength="8"
                                />
                                <div class="invalid-feedback">
                                    Please enter a valid phone number.
                                </div>
                            </div>
                        </div>

                        <div class="row mb-3">
                            <label for="mobile" class="col-sm-3 col-form-label"
                                >Mobile
                            </label>
                            <div class="col-sm-9">
                                <input
                                    v-model="contact.mobile_number"
                                    type="text"
                                    class="form-control"
                                    name="mobile"
                                    required
                                    minlength="10"
                                />
                                <div class="invalid-feedback">
                                    Please enter a valid mobile number.
                                </div>
                            </div>
                        </div>

                        <div class="row mb-3">
                            <label for="fax" class="col-sm-3 col-form-label"
                                >Fax
                            </label>
                            <div class="col-sm-9">
                                <input
                                    v-model="contact.fax_number"
                                    type="text"
                                    class="form-control"
                                    name="fax"
                                    minlength="8"
                                />
                                <div class="invalid-feedback">
                                    Please enter a valid fax number.
                                </div>
                            </div>
                        </div>

                        <div class="row mb-3">
                            <label for="email" class="col-sm-3 col-form-label"
                                >Email
                            </label>
                            <div class="col-sm-9">
                                <input
                                    v-model="contact.email"
                                    type="email"
                                    class="form-control"
                                    name="email"
                                    required
                                    pattern="[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$"
                                />
                                <div class="invalid-feedback">
                                    Please enter a valid email address.
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </form>
        </modal>
    </div>
</template>

<script>
import modal from '@vue-utils/bootstrap-modal.vue';
import alert from '@vue-utils/alert.vue';
import { helpers, api_endpoints } from '@/utils/hooks.js';
export default {
    name: 'AddOrganisationContact',
    components: {
        modal,
        alert,
    },
    props: {
        org_id: {
            type: Number,
        },
    },
    data: function () {
        return {
            isModalOpen: false,
            form: null,
            contact: {},
            errors: false,
            errorString: '',
            successString: '',
            success: false,
        };
    },
    computed: {
        showError: function () {
            var vm = this;
            return vm.errors;
        },
    },
    mounted: function () {
        let vm = this;
        vm.form = document.forms.addContactForm;
    },
    methods: {
        title: function () {
            let vm = this;
            if (vm.contact.id) {
                return 'Update Contact';
            }
            return 'Add Contact';
        },
        close: function () {
            this.isModalOpen = false;
            this.contact = {};
            this.errors = false;
            this.form.reset();
            this.form.classList.remove('was-validated');
        },
        fetchContact: function (id) {
            let vm = this;
            vm.$http.get(api_endpoints.contact(id)).then(
                (response) => {
                    vm.contact = response.body;
                    vm.isModalOpen = true;
                },
                (error) => {
                    console.error(error);
                }
            );
        },
        validateForm: function () {
            let vm = this;
            var form = document.getElementById('addContactForm');

            if (form.checkValidity()) {
                vm.sendData();
            } else {
                form.classList.add('was-validated');
                $('#addContactForm').find(':invalid').first().focus();
            }

            return false;
        },
        sendData: function () {
            let vm = this;
            vm.errors = false;
            if (vm.contact.id) {
                const requestOptions = {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(vm.contact),
                };
                fetch(
                    helpers.add_endpoint_json(
                        api_endpoints.organisation_contacts,
                        vm.contact.id
                    ),
                    requestOptions
                ).then(
                    () => {
                        vm.$parent.refreshDatatable();
                        vm.close();
                    },
                    (error) => {
                        console.error(error);
                        vm.errors = true;
                        vm.errorString = helpers.apiVueResourceError(error);
                    }
                );
            } else {
                vm.contact.organisation = vm.org_id;
                vm.contact.user_status = 'contact_form';
                const requestOptions = {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(vm.contact),
                };
                fetch(api_endpoints.organisation_contacts, requestOptions).then(
                    () => {
                        vm.close();
                        vm.$parent.addedContact();
                    },
                    (error) => {
                        console.error(error);
                        vm.errors = true;
                        vm.errorString = helpers.apiVueResourceError(error);
                    }
                );
            }
        },
    },
};
</script>
