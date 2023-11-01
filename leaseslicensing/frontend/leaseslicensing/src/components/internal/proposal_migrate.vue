<template lang="html">
    <div class="container">
        <div class="row">
            <div class="col-sm-12">
                <form
                    class="form-horizontal"
                    name="personal_form"
                    method="post"
                >
                    <FormSection label="Apply for a" index="propsal_apply_for">
                        <div class="col">
                            <div class="form-group">
                                <ul class="list-group">
                                    <li class="list-group-item">
                                        Lease or Licence
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </FormSection>
                    <FormSection
                        label="on behalf of"
                        index="proposal_apply_on_behalf_of"
                    >
                        <div v-if="!addNewUser" class="container">
                            <form>
                                {{ applicant }}
                                <div class="mb-3 row">
                                    <label
                                        for="inputName"
                                        class="col-3 col-form-label"
                                        >Select Proponent Type:</label
                                    >
                                    <div class="col-5">
                                        <ul class="list-group">
                                            <li class="list-group-item">
                                                <div class="form-check">
                                                    <input
                                                        id=""
                                                        v-model="applicantType"
                                                        class="form-check-input"
                                                        type="radio"
                                                        name="transferee_type"
                                                        value="organisation"
                                                        @change="
                                                            transfereeTypeChanged
                                                        "
                                                    />
                                                    <label
                                                        class="form-check-label"
                                                        for=""
                                                    >
                                                        Organisation
                                                    </label>
                                                </div>
                                            </li>
                                            <li class="list-group-item">
                                                <div class="form-check">
                                                    <input
                                                        id=""
                                                        v-model="applicantType"
                                                        class="form-check-input"
                                                        type="radio"
                                                        name="transferee_type"
                                                        value="individual"
                                                        @change="
                                                            transfereeTypeChanged
                                                        "
                                                    />
                                                    <label
                                                        class="form-check-label"
                                                        for=""
                                                    >
                                                        Individual
                                                    </label>
                                                </div>
                                            </li>
                                        </ul>
                                    </div>
                                </div>
                                <div
                                    v-if="applicantType == 'organisation'"
                                    class="row mb-3"
                                >
                                    <div class="col-3">Select Organisation</div>
                                    <div class="col-5">
                                        <select
                                            id="search"
                                            ref="search"
                                            class="form-select"
                                            placeholder="Start typing the Organisation's Name or ABN"
                                        />
                                    </div>
                                </div>
                                <div
                                    v-if="applicantType == 'individual'"
                                    class="row mb-3"
                                >
                                    <div class="col-3">Select Individual</div>
                                    <div class="col-5">
                                        <select
                                            id="search"
                                            ref="search"
                                            class="form-select"
                                            placeholder="Start typing the individual's name or email"
                                        />
                                    </div>
                                </div>
                            </form>
                        </div>
                        <div v-else class="container">
                            <div class="row">
                                <div class="col-8">
                                    <form
                                        id="new"
                                        class="needs-validation"
                                        novalidate
                                        @submit.prevent="validateForm"
                                    >
                                        <fieldset
                                            v-if="applicantType == 'individual'"
                                            class="rounded-3 border p-3"
                                        >
                                            <legend
                                                class="float-none w-auto px-3"
                                            >
                                                Add New Individual
                                            </legend>
                                            <div class="row mb-3">
                                                <label
                                                    for="email"
                                                    class="col-sm-3 col-form-label"
                                                    >Email</label
                                                >
                                                <div class="col-sm-9">
                                                    <input
                                                        id="email"
                                                        ref="email"
                                                        v-model="newUser.email"
                                                        type="email"
                                                        class="form-control"
                                                    />
                                                </div>
                                            </div>
                                            <div class="row mb-3">
                                                <BootstrapAlert type="primary">
                                                    The first and last name for
                                                    the user will be populated
                                                    by auth2 if/when the user
                                                    logs in.
                                                </BootstrapAlert>
                                            </div>
                                            <button
                                                type="submit"
                                                class="btn btn-primary float-end"
                                            >
                                                Add New Individual
                                            </button>
                                            <button
                                                class="btn btn-secondary float-end me-2"
                                                @click.prevent="cancelAddNew"
                                            >
                                                Cancel
                                            </button>
                                        </fieldset>
                                        <fieldset
                                            v-else
                                            class="rounded-3 border p-3"
                                        >
                                            <legend
                                                class="float-none w-auto px-3"
                                            >
                                                Add New Organisation
                                            </legend>
                                            <div class="row mb-3">
                                                <label
                                                    for="organisation-name"
                                                    class="col-sm-3 col-form-label"
                                                    >Organisation Name</label
                                                >
                                                <div class="col-sm-9">
                                                    <input
                                                        id="organisation-name"
                                                        ref="organisation-name"
                                                        v-model="
                                                            newOrganisation.organisation_name
                                                        "
                                                        type="text"
                                                        class="form-control"
                                                        maxlength="255"
                                                        required
                                                    />
                                                </div>
                                            </div>
                                            <div class="row mb-3">
                                                <label
                                                    for="trading-name"
                                                    class="col-sm-3 col-form-label"
                                                    >Trading Name</label
                                                >
                                                <div class="col-sm-9">
                                                    <input
                                                        id="trading-name"
                                                        v-model="
                                                            newOrganisation.trading_name
                                                        "
                                                        type="text"
                                                        maxlength="255"
                                                        class="form-control"
                                                    />
                                                </div>
                                            </div>
                                            <div class="row mb-3">
                                                <label
                                                    for="abn"
                                                    class="col-sm-3 col-form-label"
                                                    >ABN</label
                                                >
                                                <div class="col-sm-9">
                                                    <input
                                                        id="abn"
                                                        v-model="
                                                            newOrganisation.abn
                                                        "
                                                        type="number"
                                                        class="form-control"
                                                        maxlength="11"
                                                        required
                                                    />
                                                </div>
                                            </div>
                                            <div class="row mb-3">
                                                <label
                                                    for="email"
                                                    class="col-sm-3 col-form-label"
                                                    >Email</label
                                                >
                                                <div class="col-sm-9">
                                                    <input
                                                        id="email"
                                                        ref="email"
                                                        v-model="
                                                            newOrganisation.email
                                                        "
                                                        type="email"
                                                        class="form-control"
                                                        required
                                                    />
                                                </div>
                                            </div>
                                            <button
                                                type="submit"
                                                class="btn btn-primary float-end"
                                            >
                                                Add New Organisation
                                            </button>
                                            <button
                                                class="btn btn-secondary float-end me-2"
                                                @click.prevent="cancelAddNew"
                                            >
                                                Cancel
                                            </button>
                                        </fieldset>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </FormSection>
                    <div class="col-sm-12">
                        <button
                            v-if="!creatingProposal"
                            :disabled="isDisabled"
                            class="btn btn-primary float-end continue"
                            @click.prevent="submit()"
                        >
                            Continue
                        </button>
                        <BootstrapButtonSpinner
                            v-else
                            class="btn btn-primary float-end continue"
                            :is-loading="true"
                            :center-of-screen="false"
                            :small="true"
                        />
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>
<script>
import FormSection from '@/components/forms/section_toggle.vue';
import { api_endpoints } from '@/utils/hooks';
export default {
    name: 'ProposalMigrate',
    components: {
        FormSection,
    },
    data: function () {
        return {
            selectedApplication: null,
            searchApiEndpoint: api_endpoints.organisation_lookup,
            searchPlaceholder: 'Start typing the Organisation Name or ABN',
            applicantType: 'organisation',
            applicant: null,
            creatingProposal: false,
            addNewUser: false,
            newUser: null,
            newOrganisation: null,
        };
    },
    computed: {
        isLoading: function () {
            return this.loading.length > 0;
        },
        isDisabled: function () {
            let disabled = true;
            if (this.applicant) {
                disabled = false;
            }
            return disabled;
        },
        alertText: function () {
            let text = '';
            if (
                this.selectedApplication &&
                this.selectedApplication.description
            ) {
                text = this.selectedApplication.description;
            }
            text = 'a ' + text;
            return text;
        },
    },
    created: function () {
        this.initNewUser();
        this.initNewOrganisation();
    },
    mounted: function () {
        this.setPlaceholderAndApiEndpoint();
    },
    methods: {
        initNewUser: function () {
            this.newUser = { email: '' };
        },
        initNewOrganisation: function () {
            this.newOrganisation = {
                organisation_name: '',
                trading_name: '',
                abn: '',
                email: '',
            };
        },
        cancelAddNew: function () {
            this.addNewUser = false;
            this.initNewUser();
            this.initNewOrganisation();
            this.$nextTick(() => {
                this.initialiseSearch();
                this.$nextTick(() => {
                    $('#search').select2('open');
                });
            });
        },
        submit: function () {
            swal.fire({
                title: 'Create ' + this.selectedApplication.description,
                text: 'Are you sure you want to create ' + this.alertText + '?',
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: 'Proceed',
                reverseButtons: true,
                buttonsStyling: false,
                customClass: {
                    confirmButton: 'btn btn-primary',
                    cancelButton: 'btn btn-secondary me-2',
                },
            }).then(
                (result) => {
                    if (result.isConfirmed) {
                        this.createProposal();
                    }
                },
                (error) => {
                    console.error(error);
                }
            );
        },
        setPlaceholderAndApiEndpoint: function () {
            if (this.applicantType == 'individual') {
                this.searchPlaceholder =
                    "Start typing the Individual's Name or Email";
                this.searchApiEndpoint = api_endpoints.person_lookup;
                this.initialiseSearch();
            } else {
                this.searchPlaceholder =
                    'Start typing the Organisation Name or ABN';
                this.searchApiEndpoint = api_endpoints.organisation_lookup;
                this.initialiseSearch();
            }
        },
        transfereeTypeChanged: function () {
            this.setPlaceholderAndApiEndpoint();
            setTimeout(() => {
                this.initialiseSearch();
                $('#search').select2('open');
                this.resetApplicant();
            }, 200);
        },
        initialiseSearch: function () {
            let vm = this;
            $('#search')
                .select2({
                    minimumInputLength: 2,
                    theme: 'bootstrap-5',
                    allowClear: true,
                    placeholder: vm.searchPlaceholder,
                    ajax: {
                        url: vm.searchApiEndpoint,
                        dataType: 'json',
                        data: function (params) {
                            let query = {
                                term: params.term,
                                type: 'public',
                            };
                            return query;
                        },
                        processResults: function (data, params) {
                            if (data.results.length == 0) {
                                swal.fire({
                                    title: 'No Results Found',
                                    html: `<p>No results found for the search term '${params.term}'.</p><p> Would you like to add a new ${vm.applicantType} to the ledger database?</p>`,
                                    icon: 'warning',
                                    confirmButtonText: 'Yes please',
                                    cancelButtonText: 'Search Again',
                                    showCancelButton: true,
                                    reverseButtons: true,
                                    buttonsStyling: false,
                                    customClass: {
                                        confirmButton: 'btn btn-primary',
                                        cancelButton: 'btn btn-secondary me-2',
                                    },
                                }).then(async (result) => {
                                    if (result.isConfirmed) {
                                        vm.addNewUser = true;
                                        vm.$nextTick(() => {
                                            if (
                                                vm.applicantType == 'individual'
                                            ) {
                                                vm.newUser.email = params.term;
                                                vm.$refs.email.focus();
                                            } else {
                                                if (
                                                    /^\d+$/.test(
                                                        params.term.replace(
                                                            /\s/g,
                                                            ''
                                                        )
                                                    )
                                                ) {
                                                    vm.newOrganisation.abn =
                                                        params.term;
                                                } else {
                                                    vm.newOrganisation.organisation_name =
                                                        params.term;
                                                }
                                                vm.$refs[
                                                    'organisation-name'
                                                ].focus();
                                            }
                                        });
                                    } else {
                                        $('#search').select2('open');
                                    }
                                });
                            }
                            return {
                                results: data.results,
                            };
                        },
                    },
                })
                .on('select2:open', function () {
                    const searchField = $(
                        `[aria-controls='select2-search-results']`
                    );
                    searchField[0].focus();
                })
                .on('select2:select', function (e) {
                    this.applicant = e.params.data.id;
                    document.activeElement.blur();
                })
                .on('select2:clear', function () {
                    vm.resetApplicant();
                });
        },
        resetApplicant: function () {
            this.applicant = null;
        },
        validateForm: function () {
            let vm = this;
            var form = document.getElementById('new');

            if (form.checkValidity()) {
                vm.sendData();
            } else {
                form.classList.add('was-validated');
                $('form#new').find(':invalid').first().focus();
            }

            return false;
        },
        createProposal: async function () {
            this.$nextTick(async () => {
                let res = null;
                try {
                    this.creatingProposal = true;
                    let payload = null;
                    if ('individual' == this.applicantType) {
                        payload = {
                            ind_applicant: this.applicant,
                            application_type: this.selectedApplication,
                        };
                    } else {
                        payload = {
                            org_applicant: this.applicant,
                            application_type: this.selectedApplication,
                        };
                    }
                    res = await fetch(api_endpoints.proposal, {
                        body: JSON.stringify(payload),
                        method: 'POST',
                    });
                    const resData = await res.json();
                    const proposal = Object.assign({}, resData);
                    this.$router.push({
                        name: 'draft_proposal',
                        params: { proposal_id: proposal.id },
                    });
                } catch (error) {
                    console.error(error);
                    await swal.fire({
                        title: 'Create Proposal',
                        icon: 'error',
                        text: 'There was an error attempting to create your application. Please try again later.',
                    });
                    this.$router.go();
                }
            });
        },
    },
};
</script>

<style scoped lang="css">
button.continue {
    width: 150px;
}
</style>
