<template lang="html">
    <div id="add-external-referral">
        <modal @ok="validateForm" :title="title()" large okText="Send Invite">
            <form class="needs-validation form-horizontal" id="addExternalReferralForm" name="addExternalReferralForm"
                novalidate>
                <div class="row mt-3">
                    <div class="col-lg-12 ps-5 pe-5">
                        <BootstrapAlert v-if="errors" class="d-flex align-items-center" type="danger"
                            icon="exclamation-triangle-fill">
                            <ErrorRenderer :errors="errors" />
                        </BootstrapAlert>

                        <div class="row mb-3">
                            <label for="email" class="col-sm-3 col-form-label">Email
                            </label>
                            <div class="col-sm-9">
                                <input type="email" class="form-control" ref="Email" name="email"
                                    v-model="external_referee_invite.email" required
                                    pattern="^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$" />
                                <div class="invalid-feedback">
                                    Please enter a valid email address.
                                </div>
                            </div>
                        </div>

                        <div class="row mb-3 mt-3">
                            <label for="first_name" class="col-sm-3 col-form-label">First Name</label>
                            <div class="col-sm-9">
                                <input type="text" class="form-control" id="first_name" name="first_name" ref="first_name"
                                    v-model="external_referee_invite.first_name" required />
                                <div class="invalid-feedback">
                                    Please enter the referee's first name.
                                </div>
                            </div>
                        </div>

                        <div class="row mb-3">
                            <label for="last_name" class="col-sm-3 col-form-label">Last
                                Name</label>
                            <div class="col-sm-9">
                                <input type="text" class="form-control" name="last_name"
                                    v-model="external_referee_invite.last_name" required />
                                <div class="invalid-feedback">
                                    Please enter the referee's last name.
                                </div>
                            </div>
                        </div>

                        <div class="row mb-4">
                            <label for="mobile" class="col-sm-3 col-form-label">Organisation</label>
                            <div class="col-sm-9">
                                <input type="text" class="form-control" name="organisation"
                                    v-model="external_referee_invite.organisation" required />
                                <div class="invalid-feedback">
                                    Please enter the referee's organisation.
                                </div>
                            </div>
                        </div>

                        <BootstrapAlert>
                            <ul class="list-group">
                                <li class="list-group-item">
                                    When you click 'Send Invite', the external referee will be sent an invite email.
                                </li>
                                <li class="list-group-item">
                                    They will be asked to create an account to login and complete their referral.
                                </li>
                            </ul>
                        </BootstrapAlert>

                    </div>
                </div>
            </form>
        </modal>
    </div>
</template>

<script>
import modal from '@vue-utils/bootstrap-modal.vue'
import alert from '@vue-utils/alert.vue'
import ErrorRenderer from '@common-utils/ErrorRenderer.vue'
import { helpers, api_endpoints } from "@/utils/hooks.js"

export default {
    name: 'Add-External-Referral',
    components: {
        modal,
        ErrorRenderer
    },
    emits: ['external-referee-invite-sent'],
    props: {
        proposal_id: {
            type: Number,
            required: true
        },
        email: {
            type: String,
            required: true
        },
    },
    data: function () {
        let vm = this;
        return {
            isModalOpen: false,
            external_referee_invite: {},
            errors: null,
        }
    },
    watch: {
        isModalOpen: function (val) {
            if (val) {
                this.$nextTick(() => {
                    this.$refs.Email.focus();
                })
            }
        },
        email: function (val) {
            this.external_referee_invite.email = val;
        }
    },
    methods: {
        title: function () {
            return "Invite External Referee";
        },
        close: function () {
            this.isModalOpen = false;
            this.errors = null;
            document.getElementById('addExternalReferralForm').classList.remove('was-validated');
        },
        validateForm: function () {
            let vm = this;
            var form = document.getElementById('addExternalReferralForm')
            if (form.checkValidity()) {
                vm.sendData();
            } else {
                form.classList.add('was-validated');
                $('#addExternalReferralForm').find(":invalid").first().focus();
            }
            return false;
        },
        sendData: async function () {
            let vm = this;
            vm.errors = false;
            const url = api_endpoints.proposal + `${vm.proposal_id}/external_referee_invite/`;
            const requestOptions = {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(vm.external_referee_invite)
            };

            fetch(url, requestOptions)
                .then(async response => {
                    const data = await response.json();
                    if (!response.ok) {
                        const error = (data && data.message) || response.statusText;
                        vm.errors = data;
                        return;
                    }
                    console.log(data)
                    swal.fire({
                        title: 'Success',
                        text: 'External referee invite sent',
                        icon: 'success',
                        confirmButtonText: 'OK'
                    })
                    vm.$emit('external-referee-invite-sent');
                    vm.close();
                })
                .catch(error => {
                    console.error('There was an error!', error);
                    vm.errors = error;
                });
        },
    }
}
</script>
