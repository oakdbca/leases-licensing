<template>
<!-- External Proposal view -->

<h3>{{ approval.lodgement_number }}</h3>

<div>Issue date: {{ approval.issue_date }}</div>
<div>Commencement: {{ approval.start_date }}</div>
<div>Expiry: {{ approval.expiry_date }}</div>

</template>

<script>
import { api_endpoints, helpers } from '@/utils/hooks'

export default {
    name: 'ExternalApprovalDetail',
    data() {
        let vm = this;
        vm._uid = vm._.uid; // Vue3
        return {
            approval: {
                applicant_id: null
            },
        }
    },
    props: {
        approvalId: {
            type: Number,
        },
    },
    created: async function() {
        await fetch(helpers.add_endpoint_json(api_endpoints.approvals, this.$route.params.approval_id)).then(async response => {
            if (!response.ok) {
                return await response.json().then(json => { throw new Error(json); });
            } else {
                return await response.json();
                }
            })
            .then (data => {
                this.approval = Object.assign({}, data);
                this.approval.applicant_id = data.applicant_id;
            })
            .catch(error => {
                console.log(`Error fetching external approval data ${error}`);
            })
        this;
    }
}
</script>
