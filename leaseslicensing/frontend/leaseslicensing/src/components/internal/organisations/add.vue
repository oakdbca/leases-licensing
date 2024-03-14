<template>
    <div id="internal-add-organisation" class="container">
        <div class="row">
            <div class="col">
                <h3>Add Organisation</h3>
            </div>
        </div>
        <div class="row">
            <div class="col-6">
                <form
                    id="organisation-form"
                    class="needs-validation"
                    novalidate
                >
                    <div class="mb-3">
                        <label for="name" class="form-label fw-bold"
                            >Name</label
                        >
                        <input
                            id="name"
                            v-model="organisation.name"
                            type="text"
                            class="form-control"
                            required
                            autofocus
                        />
                        <div class="invalid-feedback">Please enter a name.</div>
                    </div>
                    <div class="mb-3">
                        <label for="trading-name" class="form-label"
                            >Trading Name</label
                        >
                        <input
                            id="trading-name"
                            v-model="organisation.trading_name"
                            type="text"
                            class="form-control"
                        />
                    </div>
                    <div class="mb-3">
                        <label for="abn" class="form-label fw-bold"
                            >ABN / ACN</label
                        >
                        <input
                            id="abn"
                            v-model="organisation.abn"
                            type="text"
                            class="form-control"
                            required
                        />
                        <div class="invalid-feedback">
                            Please enter an abn/acn.
                        </div>
                    </div>
                    <div class="mb-3">
                        <label for="email" class="form-label fw-bold"
                            >Email</label
                        >
                        <input
                            id="email"
                            v-model="organisation.email"
                            type="email"
                            class="form-control"
                            required
                        />
                        <div class="invalid-feedback">
                            Please enter a valid email.
                        </div>
                    </div>
                    <button
                        type="submit"
                        class="btn btn-primary me-2"
                        @click.prevent="validateForm(false)"
                    >
                        Add Organisation
                    </button>
                    <button
                        type="submit"
                        class="btn btn-primary"
                        @click.prevent="validateForm(true)"
                    >
                        Add Organisation and Exit
                    </button>
                </form>
            </div>
        </div>
    </div>
</template>

<script>
import { api_endpoints } from '@/utils/hooks.js';

export default {
    name: 'InternalOrganisationAdd',
    data: function () {
        return {
            organisation: this.emptyOrganisation(),
        };
    },
    methods: {
        emptyOrganisation: function () {
            return {
                name: '',
                trading_name: '',
                abn: '',
                email: '',
            };
        },
        validateForm: function (exit = false) {
            let vm = this;
            var form = document.getElementById('organisation-form');

            if (form.checkValidity()) {
                vm.addOrganisation(exit);
            } else {
                form.classList.add('was-validated');
                $('#organisation-form').find(':invalid').first().focus();
            }

            return false;
        },
        addOrganisation: async function (exit = false) {
            let vm = this;
            const requestOptions = {
                method: 'POST',
                body: JSON.stringify(vm.organisation),
            };
            await fetch(api_endpoints.organisations, requestOptions).then(
                async (response) => {
                    if (!response.ok) {
                        const data = await response.json();
                        vm.errors = data.errors;
                    }
                    if (exit) {
                        vm.$router.push({
                            name: 'organisations-dashboard',
                        });
                    } else {
                        vm.organisation = vm.emptyOrganisation();
                        document.getElementById('organisation-form').reset();
                    }
                }
            );
        },
    },
};
</script>
