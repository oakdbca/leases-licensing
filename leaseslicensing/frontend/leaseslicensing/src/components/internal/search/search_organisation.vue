<template lang="html">
    <FormSection label="Search Organisation" Index="search_organisation">
        <div class="row form-group">
            <div class="col-md-3">
                <label for="organisation_lookup" class="ms-3">
                    <strong>Search Organisation:</strong>
                </label>
            </div>
            <div class="col-md-5">
                <select
                id="organisation_lookup"
                name="organisation_lookup"
                ref="organisation_lookup"
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
        name:'SearchOrganisation',
        components:{
            FormSection,
        },
         data:function () {
            return {
                email_user: null,
             }
        },
        methods:{
            initialiseOrganisationLookup: function(){
                let vm = this;
                $(vm.$refs.organisation_lookup).select2({
                    minimumInputLength: 2,
                    "theme": "bootstrap-5",
                    allowClear: true,
                    placeholder:"Select Organisation",
                    ajax: {
                        url: api_endpoints.organisation_lookup,
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
                this.initialiseOrganisationLookup();
            });
        },
    }
</script>
