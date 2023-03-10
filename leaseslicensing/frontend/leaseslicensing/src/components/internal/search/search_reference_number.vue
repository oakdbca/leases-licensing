<template lang="html">
    <FormSection label="Search Reference Number" Index="search_reference_number">
        <div class="row form-group">
            <div class="col-md-3">
                <label for="reference_number_lookup" class="ms-3">
                    <strong>Search Reference Number:</strong>
                </label>
            </div>
            <div class="col-md-5">
                <select
                id="reference_number_lookup"
                name="reference_number_lookup"
                ref="reference_number_lookup"
                class="form-control"
            />
            </div>
        </div>

    </FormSection>
</template>

<script>
import FormSection from '@/components/forms/section_toggle.vue'
import {api_endpoints, helpers}

from '@/utils/hooks'

    export default {
        name:'SearchReferenceNumber',
        components:{
            FormSection,
        },
         data:function () {
            return {
                email_user: null,
             }
        },
        methods:{
            initialiseReferenceNumberLookup: function(){
                let vm = this;
                $(vm.$refs.reference_number_lookup).select2({
                    minimumInputLength: 2,
                    "theme": "bootstrap-5",
                    allowClear: true,
                    placeholder:"Select Reference Number",
                    ajax: {
                        url: api_endpoints.reference_number_lookup,
                        dataType: 'json',
                        data: function(params) {
                            console.log(params)
                            var query = {
                                term: params.term,
                                type: 'public',
                            }
                            return query;
                        },
                    },
                }).
                on("select2:select", function (e) {
                    var selected = $(e.currentTarget);
                    vm.email_user = e.params.data
                });
            },
        },
        mounted: function () {
            this.$nextTick(async () => {
                this.initialiseReferenceNumberLookup();
            });
        },
    }
</script>
