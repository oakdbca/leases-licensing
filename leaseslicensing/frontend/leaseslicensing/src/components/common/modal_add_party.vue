<template lang="html">
    <div id="modal_add_party">
        <Modal
            ref="modal_add_party"
            transition="modal fade"
            title="Add Party"
            ok-text="Add"
            large
            :ok-disabled="disableOkButton"
            @ok="okClicked"
            @cancel="cancel"
            @mounted="modalMounted"
        >
            <div class="container-fluid">
                <div class="row modal-input-row">
                    <div class="col-sm-3">
                        <label class="form-label">Add party</label>
                    </div>
                    <div class="col-sm-9">
                        <div class="form-check form-check-inline">
                            <input
                                id="inlineRadio1"
                                v-model="type_to_add"
                                class="form-check-input"
                                type="radio"
                                name="inlineRadioOptions"
                                value="person"
                            />
                            <label class="form-check-label" for="inlineRadio1"
                                >Person</label
                            >
                        </div>
                        <div class="form-check form-check-inline">
                            <input
                                id="inlineRadio2"
                                v-model="type_to_add"
                                class="form-check-input"
                                type="radio"
                                name="inlineRadioOptions"
                                value="organisation"
                            />
                            <label class="form-check-label" for="inlineRadio2"
                                >Organisation</label
                            >
                        </div>
                    </div>
                </div>
                <div
                    v-show="type_to_add == 'person'"
                    class="row modal-input-row"
                >
                    <div class="col-sm-3">
                        <label class="form-label">Person</label>
                    </div>
                    <div class="col-sm-7">
                        <select
                            id="select_email_users"
                            ref="email_users"
                            class="form-select"
                            aria-label="Select person to add"
                            :disabled="false"
                        >
                            <option value="null"></option>
                            <option
                                v-for="user in email_users"
                                :key="user.id"
                                :value="user.email"
                            >
                                {{ user.name }}
                            </option>
                        </select>
                    </div>
                </div>
                <div
                    v-show="type_to_add == 'organisation'"
                    class="row modal-input-row"
                >
                    <div class="col-sm-3">
                        <label class="form-label">Organisation</label>
                    </div>
                    <div class="col-sm-7">
                        <select
                            ref="organisations"
                            class="form-select"
                            aria-label="Select organisation to add"
                            :disabled="false"
                        >
                            <option value="null"></option>
                            <option
                                v-for="organisation in organisations"
                                :key="organisation.id"
                                :value="organisation.email"
                            >
                                {{ organisation.name }}
                            </option>
                        </select>
                    </div>
                </div>
            </div>
        </Modal>
    </div>
</template>

<script>
import Modal from '@vue-utils/bootstrap-modal.vue'
import { api_endpoints } from '@/utils/hooks.js'

export default {
    name: 'AddParty',
    components: {
        Modal,
    },
    props: {},
    emits: ['partyToAdd', 'closeModal'],
    data: function () {
        return {
            isModalOpen: false,
            errors: false,
            errorString: '',
            successString: '',
            success: false,
            saving: false,

            type_to_add: '',
            // Person
            email_users: [],
            selected_email_user: null,

            // Organisation
            organisations: [],
            selected_organisation: null,
        }
    },
    computed: {
        showError: function () {
            var vm = this
            return vm.errors
        },
        disableOkButton: function () {
            let disabled = true
            if (this.selected_email_user || this.selected_organisation) {
                disabled = false
            }
            return disabled
        },
    },
    watch: {},
    mounted: function async() {
        let vm = this
        vm.$nextTick(async () => {
            vm.initialiseSelectPerson()
            vm.initialiseSelectOrganisation()
        })
    },
    created: async function () {},
    methods: {
        modalMounted: function () {
            console.log('Add-party mounted.')
        },
        initialiseSelectPerson: function () {
            let vm = this
            $(vm.$refs.email_users)
                .select2({
                    minimumInputLength: 2,
                    theme: 'bootstrap-5',
                    allowClear: true,
                    placeholder: 'Type and select Person',
                    // dropdownParent: $('#modal_add_party'),
                    ajax: {
                        url: api_endpoints.person_lookup,
                        dataType: 'json',
                        data: function (params) {
                            var query = {
                                term: params.term,
                                type: 'public',
                            }
                            return query
                        },
                        processResults: function (data) {
                            return data
                        },
                    },
                })
                .on('select2:select', function (e) {
                    vm.selected_email_user = e.params.data
                })
                .on('select2:unselect', function () {
                    vm.selected_email_user = null
                })
        },
        initialiseSelectOrganisation: function () {
            let vm = this
            $(vm.$refs.organisations)
                .select2({
                    minimumInputLength: 2,
                    theme: 'bootstrap-5',
                    allowClear: true,
                    placeholder: 'Type and select Organisation',
                    ajax: {
                        url: api_endpoints.organisation_lookup,
                        dataType: 'json',
                        data: function (params) {
                            var query = {
                                term: params.term,
                                type: 'public',
                            }
                            return query
                        },
                        processResults: function (data) {
                            return data
                        },
                    },
                })
                .on('select2:select', function (e) {
                    let data = e.params.data
                    vm.selected_organisation = data
                })
                .on('select2:unselect', function () {
                    vm.selected_organisation = null
                })
        },
        okClicked: function () {
            let party_to_add = null
            if (this.type_to_add === 'person') {
                party_to_add = this.selected_email_user
            } else if (this.type_to_add === 'organisation') {
                party_to_add = this.selected_organisation
            }
            if (party_to_add) {
                this.$emit('partyToAdd', {
                    // Issue an event with type and person/organisation
                    type: this.type_to_add,
                    party_to_add: party_to_add,
                })
            }
            this.close()
        },
        cancel: function () {
            this.close()
        },
        close: function () {
            this.selected_email_user = null
            this.selected_organisation = null
            $(this.$refs.email_users).empty()
            $(this.$refs.organisations).empty()
            this.isModalOpen = false
            this.errors = false
            $('.has-error').removeClass('has-error')
            this.$emit('closeModal')
        },
        addEventListeners: function () {},
    },
}
</script>

<style lang="css">
.modal-input-row {
    margin-bottom: 1em;
}
.select2-container--bootstrap-5 {
    z-index: 99999;
}
</style>
