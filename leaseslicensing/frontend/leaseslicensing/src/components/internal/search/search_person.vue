<template lang="html">
    <FormSection label="Search Person" Index="search_person">
        <div class="row form-group">
            <div class="col-md-3">
                <label for="person_lookup" class="ms-3">
                    <strong>Search Person:</strong>
                </label>
            </div>
            <div class="col-md-5">
                <select
                id="person_lookup"
                name="person_lookup"
                ref="person_lookup"
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
        name:'SearchPerson',
        components:{
            FormSection,
        },
         data:function () {
            return {
                email_user: null,
             }
        },
        methods:{
            initialisePersonLookup: function(){
                let vm = this;
                $(vm.$refs.person_lookup).select2({
                    minimumInputLength: 2,
                    "theme": "bootstrap-5",
                    allowClear: true,
                    placeholder:"Select Person",
                    ajax: {
                        url: api_endpoints.person_lookup,
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
                on("select2:open", function (e) {
                    const searchField = $('[aria-controls="select2-person_lookup-results"]')
                    searchField[0].focus();
                }).
                on("select2:select", function (e) {
                    var selected = $(e.currentTarget);
                    window.location = '/internal/search/person/' + selected.val() + '/';
                    alert(JSON.stringify(e.params.data));
                });
            },
        },
        mounted: function () {
            this.$nextTick(async () => {
                this.initialisePersonLookup();
            });
        },
    }
</script>
