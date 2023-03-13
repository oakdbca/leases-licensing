<template>
    <div class="container" id="SearchDash">

        <Select2Search
            label="Person"
            :lookupApiEndpoint="api_endpoints.person_lookup"
            redirectPath="/internal/person/details/"
        />

        <Select2Search
            label="Organisation"
            :lookupApiEndpoint="api_endpoints.organisations"
            redirectPath=""
        />

        <Select2Search
            label="Reference Number"
            :lookupApiEndpoint="api_endpoints.organisations"
            redirectPath=""
        />

    </div>
</template>

<script>
import Select2Search from "./Select2Search.vue";
import { api_endpoints } from "@/utils/hooks.js"

export default {
    name: 'InternalSearch',
    data() {
        return {
            api_endpoints: api_endpoints,
        }
    },
    components:{
        Select2Search,
    },
}
</script>
