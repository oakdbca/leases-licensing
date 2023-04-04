<template lang="html">
    <div id="AddComms">
        <modal transition="modal fade" @ok="validateForm()" @cancel="cancel()" title="Communication log - Add Entry" large>
            <div class="container-fluid">
                <div class="row">
                    <form id="commsForm" name="commsForm" class="needs-validation" novalidate>
                        <alert :show.sync="errorString" type="danger"><strong>{{ errorString }}</strong></alert>
                        <div class="col-sm-12">
                            <div class="form-group">
                                <div class="row mb-2">
                                    <div class="col-sm-3">
                                        <label class="form-label" for="to">To</label>
                                    </div>
                                    <div class="col-sm-4">
                                        <input type="text" class="form-control" id="to" name="to" v-model="comms.to"
                                            autofocus required>
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="row mb-2">
                                    <div class="col-sm-3">
                                        <label class="form-label" for="Name">From</label>
                                    </div>
                                    <div class="col-sm-4">
                                        <input type="text" class="form-control" name="fromm" v-model="comms.fromm" required>
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="row mb-2">
                                    <div class="col-sm-3">
                                        <label class="form-label" for="Name">Type</label>
                                    </div>
                                    <div class="col-sm-4">
                                        <select class="form-select" name="type" v-model="comms.type" required>
                                            <option value="" selected disabled>Select Type</option>
                                            <option value="email">Email</option>
                                            <option value="mail">Mail</option>
                                            <option value="phone">Phone</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="row mb-2">
                                    <div class="col-sm-3">
                                        <label class="form-label" for="Name">Subject/Description</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <input type="text" class="form-control" name="subject" style="width:70%;"
                                            v-model="comms.subject" required>
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="row mb-2">
                                    <div class="col-sm-3">
                                        <label class="form-label" for="Name">Text</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <textarea name="text" class="form-control" style="width:70%;" v-model="comms.text"
                                            required></textarea>
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="row mb-2">
                                    <div class="col-sm-3">
                                        <label class="form-label" for="Name">Attachments</label>
                                    </div>
                                    <div class="col-sm-9">
                                        <template v-for="(f, i) in files">
                                            <div :class="'row top-buffer file-row-' + i">
                                                <div class="col-sm-4">
                                                    <span v-if="f.file == null" class="btn btn-primary btn-file pull-left">
                                                        Attach File <input type="file" :name="'file-upload-' + i"
                                                            :class="'file-upload-' + i"
                                                            @change="uploadFile('file-upload-' + i, f)" />
                                                    </span>
                                                    <span v-else class="btn btn-info btn-file pull-left">
                                                        Update File <input type="file" :name="'file-upload-' + i"
                                                            :class="'file-upload-' + i"
                                                            @change="uploadFile('file-upload-' + i, f)" />
                                                    </span>
                                                </div>
                                                <div class="col-sm-4">
                                                    <span>{{ f.name }}</span>
                                                </div>
                                                <div class="col-sm-4">
                                                    <button @click="removeFile(i)" class="btn btn-danger">Remove</button>
                                                </div>
                                            </div>
                                        </template>
                                        <a href="" @click.prevent="attachAnother"><i
                                                class="fa fa-lg fa-plus top-buffer-2x"></i></a>
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
import Swal from 'sweetalert2'

import { constants, helpers, api_endpoints } from "@/utils/hooks.js"
export default {
    name: 'Add-Comms',
    components: {
        modal,
        alert
    },
    props: {
        url: {
            type: String,
            required: true
        }
    },
    data: function () {
        let vm = this;
        return {
            isModalOpen: false,
            form: null,
            comms: {
                type: '',
            },
            state: 'proposed_approval',
            addingComms: false,
            errors: false,
            errorString: null,
            successString: '',
            success: false,
            datepickerOptions: {
                format: 'DD/MM/YYYY',
                showClear: true,
                useCurrent: false,
                keepInvalid: true,
                allowInputToggle: true
            },
            files: [
                {
                    'file': null,
                    'name': ''
                }
            ]
        }
    },
    computed: {
        showError: function () {
            var vm = this;
            return vm.errors;
        },
        title: function () {
            return this.processing_status == 'With Approver' ? 'Issue Comms' : 'Propose to issue approval';
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
        cancel: function () {
            this.close()
        },
        close: function () {
            let vm = this;
            this.isModalOpen = false;
            this.comms = {
                type: '',
            };
            $('#commsForm').removeClass('was-validated')
            let file_length = vm.files.length;
            this.files = [];
            for (var i = 0; i < file_length; i++) {
                vm.$nextTick(() => {
                    $('.file-row-' + i).remove();
                });
            }
            this.attachAnother();
        },
        sendData: function () {
            let vm = this;
            let comms = new FormData(vm.form);
            for (var i = 0; i < vm.files.length; i++) {
                comms.append('files', vm.files[i].file);
            }
            vm.addingComms = true;
            fetch(vm.url, {
                body: comms,
                method: 'POST',
            })
                .then(async (response) => {
                    const data = await response.json()
                    if (!response.ok) {
                        const error =
                            (data && data.message) || response.statusText
                        vm.errorString = constants.ERRORS.NETWORK_ERROR
                        console.error(error)
                        return Promise.reject(error)
                    }
                    Swal.fire(
                        'Success',
                        'Communication logged successfully',
                        'success'
                    )
                    vm.close();
                })
                .catch((error) => {
                    vm.errorString = constants.ERRORS.API_ERROR_INTERNAL
                    console.error('There was an error!', error)
                }).finally(() => {
                    vm.addingComms = false;
                })
        },
        validateForm: function () {
            let vm = this;
            var form = document.getElementById('commsForm')

            if (form.checkValidity()) {
                console.log('Form valid');
                vm.sendData();
            } else {
                form.classList.add('was-validated');
                $('#commsForm').find(":invalid").first().focus();
            }

            return false;
        },
    },
    mounted: function () {
        let vm = this;
        vm.form = document.forms.commsForm;
    }
}
</script>

<style lang="css">
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

.top-buffer {
    margin-top: 5px;
}

.top-buffer-2x {
    margin-top: 10px;
}
</style>
