<template>
    <div class="container" id="SearchDash">

        <SearchPerson />

        <SearchOrganisation />

        <SearchReferenceNumber />

    </div>
</template>

<script>
import FormSection from "@/components/forms/section_toggle.vue"
import SearchPerson from "./search_person.vue"
import SearchOrganisation from "./search_organisation.vue"
import SearchReferenceNumber from "./search_reference_number.vue"

export default {
    name: 'InternalSearch',
    data() {
        let vm = this;
        return {

        }
    },
    components:{
        FormSection,
        SearchPerson,
        SearchOrganisation,
        SearchReferenceNumber,
    },
    methods: {

    },
}
</script>
