<template lang="html">
    <div class="row form-group">
        <div class="col-md-3">
            <label :for="index" class="ms-3">
                <strong>{{ 'Search ' + label }}:</strong>
            </label>
        </div>
        <div class="col-md-5">
            <select @change="checkResults" :id="index" :name="index" :ref="index" class="form-control" />
        </div>
    </div>
</template>

<script>
import { v4 as uuid } from 'uuid'
import FormSection from '@/components/forms/section_toggle.vue'

export default {
    name: 'Select2SearchOrganisation',
    props: {
        label: {
            type: String,
            required: true,
        },
        lookupApiEndpoint: {
            type: String,
            required: true,
        },
        theme: {
            type: String,
            default: 'bootstrap-5',
        },
    },
    components: {
        FormSection,
    },
    data: function () {
        return {
            email_user: null,
            uuid: uuid(),
            term: null,
            index: 'search-' + this.label.toLowerCase().replace(' ', '-'),
        }
    },
    emits: ['selected', 'new-organisation'],
    methods: {
        initialiseLookup: function () {
            let vm = this;
            $(`#${vm.index}`).select2({
                minimumInputLength: 2,
                'theme': vm.theme,
                allowClear: true,
                placeholder: 'Start Typing the Organisation Name or ABN',
                ajax: {
                    url: vm.lookupApiEndpoint,
                    dataType: 'json',
                    data: function (params) {
                        console.log(params)
                        vm.term = params.term;
                        var query = {
                            term: params.term,
                            type: 'public',
                        }
                        return query;
                    },
                    processResults: function (data) {
                        if (0 == data.results.length) {
                            $(`#${vm.index}`).select2('close');
                            vm.$emit('new-organisation', vm.term);
                            return {
                                results: []
                            }
                        }

                        return {
                            results: data.results
                        }
                    }
                },
            }).on('select2:open', function (e) {
                const searchField = $(`[aria-controls='select2-${vm.index}-results']`)
                searchField[0].focus();
            }).on('select2:select', function (e) {
                var data = e.params.data;
                console.log(data);
                vm.$emit('selected', data);
            })
        },
        checkResults: function () {
            let vm = this;
            let selected = $(`#${vm.index}`).select2('data');
            console.log(selected);
            if (selected.length > 0) {
                console.log(selected[0].id);
                window.location.href = vm.redirectPath + selected[0].id;
            }
        },
    },
    mounted: function () {
        this.initialiseLookup();
    },
}
</script>
