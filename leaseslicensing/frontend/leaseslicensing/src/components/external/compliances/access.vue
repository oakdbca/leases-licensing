<template>
    <div class="container" id="externalCompliance">
        <div v-if="compliance">
            <BootstrapAlert v-if="isDiscarded" type="danger" icon="exclamation-triangle-fill">
                <h3>You cannot access this Compliance with requirements as this has been discarded.</h3>
            </BootstrapAlert>
            <div v-else class="row mb-3">
                <div v-if="!isFinalised">
                    <div v-if="hasAmendmentRequest">
                        <FormSection customColor="red"
                            label="An amendment has been requested for this Compliance with Requirements"
                            Index="amendment_compliance_with_requirements">
                            <div class="row mb-3">
                                <div class="col-12">
                                    <div v-for="a in amendment_request">
                                        <p>Reason: {{ a.reason }}</p>
                                        <p>Details: {{ a.text }}</p>
                                    </div>
                                </div>
                            </div>
                        </FormSection>
                    </div>
                </div>
                <div class="col-md-12">
                    <FormSection :label="'Submit Compliance - ' + compliance.lodgement_number"
                        Index="compliance_with_requirements">
                        <form class="needs-validation" id="complianceForm" name="complianceForm" method="post" novalidate>
                            <alert :show.sync="showError" type="danger">
                                <strong>{{ errorString }}</strong>
                            </alert>
                            <div class="row mb-3">
                                <label class="col-form-label col-sm-2" for="due_date">Due Date:</label>
                                <div class="col-sm-6">
                                    <input type="text" readonly class="form-control-plaintext" id="due_date" name="due_date"
                                        :value="compliance.due_date">
                                </div>
                            </div>
                            <div class="row mb-3">
                                <label class="col-form-label col-sm-2" for="requirement">Requirement:</label>
                                <div class="col-sm-6">
                                    <input type="text" readonly class="form-control-plaintext" id="requirement"
                                        name="requirement" :value="compliance.requirement" required>
                                </div>
                            </div>
                            <div class="row mb-3">
                                <label class="col-form-label col-sm-2" for="detail">Details:</label>
                                <div class="col-sm-9">
                                    <textarea :disabled="isFinalised" class="form-control" id="detail" name="detail"
                                        rows="8" v-model="compliance.text" autofocus></textarea>
                                </div>
                            </div>
                            <div v-if="hasDocuments" class="row mb-3">
                                <label class="col-form-label col-sm-2">Documents:</label>
                                <div class="col-sm-6">
                                    <div class="row mb-3" v-for="d in compliance.documents">
                                        <a :href="d[1]" target="_blank" class="control-label pull-left">{{ d[0] }}</a>
                                        <span v-if="!isFinalised && d.can_delete">
                                            <a @click="delete_document(d)" class="fa fa-trash-o control-label"
                                                title="Remove file" style="cursor: pointer; color:red;"></a>
                                        </span>
                                        <span v-else>
                                            <i class="fa fa-info-circle" aria-hidden="true"
                                                title="Previously submitted documents cannot be deleted"
                                                style="cursor: pointer;"></i>
                                        </span>
                                    </div>
                                </div>
                            </div>
                            <div v-if="!isFinalised" class="row mb-3">
                                <label class="col-form-label col-sm-2">Attachments:</label>
                                <div class="col-sm-9">
                                    <template v-if="files && files.length">
                                        <ul class="list-group">
                                            <li class="list-group-item rounded" v-for="(f, i) in files">
                                                <div class="row">
                                                    <div class="col">
                                                        <span v-if="f.file == null"
                                                            class="btn btn-primary btn-sm btn-file float-start"><i
                                                                class="fa fa-upload" aria-hidden="true"></i>
                                                            Attach File <input type="file" :name="'file-upload-' + i"
                                                                :class="'file-upload-' + i"
                                                                @change="uploadFile('file-upload-' + i, f)" />
                                                        </span>
                                                        <span v-else
                                                            class="btn btn-secondary btn-sm btn-file float-start"><i
                                                                class="fa fa-edit"></i>
                                                            Update File <input type="file" :name="'file-upload-' + i"
                                                                :class="'file-upload-' + i"
                                                                @change="uploadFile('file-upload-' + i, f)" />
                                                        </span>
                                                    </div>
                                                    <div class="col-sm-7">
                                                        <span>{{ f.name }}</span>
                                                    </div>
                                                    <div class="col-sm-1">
                                                        <button v-if="f.file || i > 0" @click.prevent="removeFile(i)"
                                                            class="btn btn-danger btn-sm"><i class="fa fa-trash"
                                                                aria-hidden="true"></i>
                                                        </button>
                                                    </div>

                                                </div>
                                            </li>
                                        </ul>
                                    </template>
                                    <div class="border-top mt-3 p-2">
                                        <button class="btn btn-sm btn-primary" @click.prevent="attachAnother"><i
                                                class="fa fa-add"></i> Add Another
                                            File</button>
                                    </div>
                                </div>
                            </div>
                            <div class="row mb-3">
                                <div class="form-group">
                                    <div class="col">
                                        <button v-if="!isFinalised" @click.prevent="close()"
                                            class="btn btn-secondary me-2">Return to Dashboard</button>
                                        <button v-if="!isFinalised" @click.prevent="validateForm()"
                                            class="btn btn-primary">Submit</button>
                                    </div>
                                </div>
                            </div>
                        </form>
                    </FormSection>
                </div>
            </div>
        </div>
        <BootstrapSpinner v-else :isLoading="true" class="text-primary" />
    </div>
</template>
<script>
import datatable from '@vue-utils/datatable.vue'
import CommsLogs from '@common-utils/comms_logs.vue'
import FormSection from "@/components/forms/section_toggle.vue"
import {
    api_endpoints,
    helpers
}
    from '@/utils/hooks'
import alert from '@vue-utils/alert.vue'

export default {
    name: 'externalComplianceAccess',
    data() {
        let vm = this;
        return {
            form: null,
            loading: [],
            compliance: null,
            original_compliance: {},
            amendment_request: [],
            hasAmendmentRequest: false,
            isFinalised: false,
            errors: false,
            errorString: '',
            pdBody: 'pdBody' + vm._uid,
            oBody: 'oBody' + vm._uid,
            pdBody: 'pdBody' + vm._uid,
            validation_form: null,
            files: [
                {
                    'file': null,
                    'name': ''
                }
            ]
        }
    },
    watch: {
        isFinalised: function () {
            return this.compliance && (this.compliance.customer_status == "Under Review" || this.compliance.customer_status == "Approved");
        },
    },
    filters: {
        formatDate: function (data) {
            return moment(data).format('DD/MM/YYYY HH:mm:ss');
        }
    },
    components: {
        datatable,
        CommsLogs,
        FormSection,
        alert,
    },
    computed: {
        showError: function () {
            var vm = this;
            return vm.errors;
        },
        isLoading: function () {
            return this.loading.length > 0;
        },
        isDiscarded: function () {
            return this.compliance && (this.compliance.customer_status == "Discarded");
        },
        hasDocuments: function () {
            return this.compliance.documents && this.compliance.documents.length > 0;
        }
    },
    methods: {
        uploadFile(target, file_obj) {
            let vm = this;
            let _file = null;
            var input = $('.' + target)[0];
            if (input.files && input.files[0]) {
                var reader = new FileReader();
                reader.readAsDataURL(input.files[0]);
                reader.onload = function (e) {
                    _file = e.target.result;
                };
                _file = input.files[0];
            }
            file_obj.file = _file;
            file_obj.name = _file.name;
        },
        removeFile(index) {
            let length = this.files.length;
            $('.file-row-' + index).remove();
            this.files.splice(index, 1);
            this.$nextTick(() => {
                length == 1 ? this.attachAnother() : '';
            });
        },
        attachAnother() {
            this.files.push({
                'file': null,
                'name': ''
            })
        },

        close: function () {
            this.$router.push({ name: 'external-dashboard' });
        },
        setAmendmentData: function (amendment_request) {
            this.amendment_request = amendment_request;

            if (amendment_request.length > 0)
                this.hasAmendmentRequest = true;
        },
        delete_document: function (doc) {
            let vm = this;
            let data = { 'document': doc }
            if (doc) {
                fetch(helpers.add_endpoint_json(api_endpoints.compliances, vm.compliance.id + '/delete_document'), {
                    method: 'POST',
                    body: JSON.stringify(data),
                }).then(async (response) => {
                    vm.refreshFromResponse(response);
                    vm.compliance = await Object.assign({}, response.json());
                }, (error) => {
                    vm.errors = true;
                    vm.errorString = error.message;
                });
            }
        },
        validateForm: function () {
            let vm = this;
            var form = document.getElementById('complianceForm')

            console.log('validateForm')

            if (form.checkValidity()) {
                vm.sendData();
            } else {
                form.classList.add('was-validated');
                $('#complianceForm').find(":invalid").first().focus();
            }

            return false;
        },
        sendData: function () {
            this.$nextTick(() => {
                this.errors = false;
                let formData = new FormData();
                formData.append('detail', this.compliance.text);
                let numFiles = 0;
                for (let i = 0; i < this.files.length; i++) {
                    formData.append('file' + i, this.files[i].file);
                    formData.append('name' + i, this.files[i].name);
                    numFiles++;
                }
                formData.append('num_files', numFiles);
                this.addingComms = true;

                fetch(helpers.add_endpoint_json(api_endpoints.compliances, this.compliance.id + '/submit'), {
                    method: 'POST',
                    body: formData
                }).then(async response => {
                    if (!response.ok) {
                        return await response.json().then(json => { throw new Error(json); });
                    } else {
                        return await response.json();
                    }
                })
                    .then(data => {
                        this.addingCompliance = false;
                        this.refreshFromResponse(data);
                        this.compliance = Object.assign({}, data);
                        this.$router.push({
                            name: 'submit_compliance',
                            params: { compliance_id: this.compliance.id }
                        });
                    })
                    .catch(error => {
                        this.errors = true;
                        this.addingCompliance = false;
                        this.errorString = error.message;
                        swal.fire({
                            title: 'Proposal Error',
                            text: error.message,
                            icon: 'error'
                        });
                    })
            });
        },
        fetchCompliance: async function (compliance_id) {
            let vm = this;
            fetch(helpers.add_endpoint_json(api_endpoints.compliances, compliance_id)).then(async (response) => {
                const resData = await response.json();
                vm.compliance = Object.assign({}, resData);
                if (vm.compliance.customer_status == "Under Review" || vm.compliance.customer_status == "Approved") { vm.isFinalised = true }

                fetch(helpers.add_endpoint_json(api_endpoints.compliances, compliance_id + '/amendment_request')).then(async (res) => {
                    vm.setAmendmentData(await res.json());
                },
                    err => {
                        console.log(err);
                    });
            }, (error) => {
                console.log(error);
            })
        },
        refreshFromResponse: async function (resData) {
            this.original_compliance = helpers.copyObject(resData);
            this.compliance = helpers.copyObject(resData);
            if (this.compliance.customer_status == "Under Review" || this.compliance.customer_status == "Approved") { this.isFinalised = true }
        },
    },
    created: function () {
        let vm = this;
        this.fetchCompliance(this.$route.params.compliance_id);
    },
    mounted: function () {
        let vm = this;
        vm.form = document.forms.complianceForm;
    },
    beforeRouteEnter: function (to, from, next) {
        next(async (vm) => {
            if (to.params.compliance_id) {
                vm.fetchCompliance(to.params.compliance_id);
            }
        })
    }
}
</script>

<style scoped>
.btn-file {
    position: relative;
    overflow: hidden;
}

.btn-file input[type=file] {
    position: absolute;
    top: 0;
    right: 0;
    min-width: 100%;
    min-height: 100%;
    font-size: 100px;
    text-align: right;
    filter: alpha(opacity=0);
    opacity: 0;
    outline: none;
    background: white;
    cursor: inherit;
    display: block;
}
</style>
