<template lang="html">
    <div :id="'approvalCancellation' + approval_id">
        <modal transition="modal fade" @ok="validateForm()" @cancel="cancel()" :title="title" large>
            <div class="container-fluid">
                <div class="row">
                    <form id="approvalForm" class="form-horizontal required-validation" name="approvalForm" novalidate>
                        <alert :show.sync="showError" type="danger"><strong>{{ errorString }}</strong></alert>
                        <div class="col-sm-12">
                            <div class="row mb-3">
                                <label class="col-sm-3 col-form-label" for="Name">Cancellation Date</label>
                                <div class="col-sm-9">
                                    <div class="input-group date" ref="cancellation_date">
                                        <input type="date" class="form-control" placeholder="DD/MM/YYYY"
                                            id="cancellation_date" name="cancellation_date"
                                            v-model="approval_cancellation.cancellation_date" required>
                                        <div class="invalid-feedback">
                                            Please select the cancellation date.
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <label class="col-sm-3 col-form-label" for="Name">Cancellation Details</label>
                                <div class="col-sm-9">
                                    <textarea name="cancellation_details" class="cancellation-details form-control" required
                                        v-model="approval_cancellation.cancellation_details"></textarea>
                                    <div class="invalid-feedback">
                                        Please enter some details about the cancellation.
                                    </div>
                                </div>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        </modal>
    </div>
</template>

<script>
import modal from '@vue-utils/bootstrap-modal.vue'
import alert from '@vue-utils/alert.vue'
import { helpers, api_endpoints } from "@/utils/hooks.js"
import Swal from 'sweetalert2'

export default {
    name: 'Cancel-Approval',
    components: {
        modal,
        alert
    },
    props: {
        approval_id: {
            type: Number,
            default: null,
        },
    },
    data: function () {
        let vm = this;
        return {
            isModalOpen: false,
            form: null,
            approval_cancellation: {
                cancellation_date: new Date().toISOString().slice(0, 10),
            },
            state: 'proposed_approval',
            validation_form: null,
            errors: false,
            errorString: '',
            successString: '',
            success: false,
        }
    },
    computed: {
        showError: function () {
            var vm = this;
            return vm.errors;
        },
        title: function () {
            return 'Cancel Approval';
        }
    },
    methods: {
        cancel: function () {
            this.close()
        },
        resetForm: function () {
            this.isModalOpen = false;
            this.approval_cancellation = {
                cancellation_date: new Date().toISOString().slice(0, 10),
            };
            vm.errors = false;
        },
        close: function () {
            var form = document.getElementById('approvalForm')
            form.classList.remove('was-validated');
            this.resetForm();
        },
        fetchContact: function (id) {
            let vm = this;
            vm.$http.get(api_endpoints.contact(id)).then((response) => {
                vm.contact = response.body; vm.isModalOpen = true;
            }, (error) => {
                console.log(error);
            });
        },
        validateForm: function () {
            let vm = this;
            var form = document.getElementById('approvalForm')

            if (form.checkValidity()) {
                console.log('Form valid');
                vm.sendData();
            } else {
                form.classList.add('was-validated');
                $('#approvalForm').find(":invalid").first().focus();
            }

            return false;
        },
        sendData: function () {
            let vm = this;
            vm.errors = false;
            console.log(vm.approval_cancellation.cancellation_date)
            let approval_cancellation = Object.assign({}, vm.approval_cancellation);
            approval_cancellation.cancellation_date = helpers.formatDateForAPI(vm.approval_cancellation.cancellation_date);
            const requestOptions = {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(approval_cancellation)
            };
            fetch(helpers.add_endpoint_json(api_endpoints.approvals, vm.approval_id + '/approval_cancellation'), requestOptions)
                .then(async response => {
                    const data = await response.json();
                    if (!response.ok) {
                        const error = (data && data.message) || response.statusText;
                        if (400 == response.status) {
                            vm.errors = true;
                            vm.errorString = helpers.getErrorStringFromResponseData(data);
                        }
                        console.log(error)
                        return Promise.reject(error);
                    }
                    vm.close();
                    Swal.fire({
                        title: 'Cancelled',
                        text: 'An email has been sent to the proponent regarding the cancellation of this approval',
                        icon: 'success',
                        showCancelButton: false,
                        confirmButtonText: 'Ok',
                        buttonsStyling: false,
                        customClass: {
                            confirmButton: 'btn btn-primary',
                        },
                    });
                    this.resetForm();
                    vm.$emit('refreshFromResponse', response);
                }, (error) => {
                    vm.errors = true;
                    vm.errorString = helpers.apiVueResourceError(error);
                });
        },

    },
    mounted: function () {

    }
}
</script>
