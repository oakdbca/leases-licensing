<template lang="html">
    <div class="container">
        <div class="row d-flex justify-content-center">
            <div v-if="isProposal" class="col-sm-6 borderDecoration">
                <div class="form-para">
                    <h3>Confirmation</h3>
                </div>
                <div class="form-para">
                    Your application for a <span class="fw-bolder">{{
                        applicationType }}</span>
                    has been
                    successfully
                    submitted.
                </div>
                <div class="form-para">
                    <table>
                        <tbody>
                            <tr>
                                <th scope="row" class="w-25">Reference number:</th>
                                <td>{{ proposal.lodgement_number }}</td>
                            </tr>
                            <tr>
                                <th scope="row">Date / Time:</th>
                                <td> {{ formatDate(proposal.lodgement_date) }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <a href="/external/" class="router-link-active btn btn-primary float-end">Back to Dashboard</a>
            </div>
            <div v-else class="col-sm-offset-3 col-sm-6 borderDecoration">
                <strong>Sorry it looks like there isn't any application currently in your session.</strong>
                <br />
                <a href="/external/" class="router-link-active btn btn-primary float-end">Back to Dashboard</a>
            </div>
        </div>
    </div>
</template>
<script>
import {
    api_endpoints,
    helpers
}
    from '@/utils/hooks'
export default {
    data: function () {
        return {
            "proposal": {},
        }
    },
    computed: {
        applicationType: function () {
            return this.proposal && this.proposal.application_type ?
                this.proposal.application_type.name_display :
                '';
        },
        isProposal: function () {
            return this.proposal && this.proposal.id ? true : false;
        },
        lodgementDateDisplay: function () {
            if (this.proposal) {
                return new Date(this.proposal.lodgement_date).toLocaleString('en-AU');
            }
        },
    },
    methods: {
        formatDate: function (data, format = 'DD/MM/YYYY HH:mm:ss') {
            return data ? moment(data).format(format) : '';
        },
    },
    beforeRouteEnter: function (to, from, next) {
        if (to.params.proposal_id) {
            fetch(`/api/proposal/${to.params.proposal_id}.json`).then(res => {
                next(async (vm) => {
                    console.log(vm)
                    const proposalData = await res.json()
                    console.log(proposalData)
                    vm.proposal = proposalData;
                });
            },
                err => {
                    console.log(err);
                });
        }

    },
}
</script>

<style lang="css" scoped>
.borderDecoration {
    border: 1px solid darkgrey;
    border-radius: 5px;
    padding: 30px;
    margin-top: 30px;
    margin-bottom: 30px;
}

.form-para {
    margin-bottom: 20px;
}
</style>
