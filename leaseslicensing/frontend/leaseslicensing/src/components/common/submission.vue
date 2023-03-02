<template>
    <div class="">
        <div class="card card-default">
            <div class="card-header">
               Submission
            </div>
            <div class="card-body card-collapse">
                <div class="row">
                    <div class="col-sm-12">
                        <strong>Submitted by</strong><br/>
                        {{ submitter_first_name }}
                        {{ submitter_last_name }}
                    </div>
                    <div class="col-sm-12 top-buffer-s">
                        <strong>Lodged on</strong><br/>
                        {{ formatDate(lodgement_date) }}
                    </div>
                    <div v-if="showingProposal || canSeeSubmission" class="col-sm-12 top-buffer-s">
                        {{ current_lodgement_version.revision_id }} {{ lodgementVersion.revision_id }}
                        <table class="table small w-auto table-sm text-xsmall">
                            <tr>
                                <th>Lodgement</th>
                                <th>Date</th>
                                <th>Action</th>
                            </tr>
                            <tr v-for="p in proposal.reversion_revisions" :key="versionKey(p.revision_id)">
                                <td>{{ p.lodgement_number }}-{{ p.lodgement_sequence }}</td>
                                <td>{{ formatDate(p.lodgement_date, format='DD/MM') }}</td>
                                <td><a v-if="p.revision_id!=current_lodgement_version.revision_id"
                                    @click.prevent="compareRevision(p)" class="actionBtn pull-right">
                                    Compare
                                    </a>
                                    <div v-else>Viewing</div>
                                </td>
                                <!-- <td><a
                                    @click.prevent="compareRevision(p)" class="actionBtn pull-right">
                                    Compare
                                    </a>
                                </td> -->
                            </tr>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'Submission',
    data: function() {
        let vm = this;
        return {

        }
    },
    props: {
        submitter_first_name: {
            type: String,
            default: '',
        },
        submitter_last_name: {
            type: String,
            default: '',
        },
        lodgement_date: {
            type: String,
            default: null,
        },
        showingProposal: {
            type: Boolean
        },
        canSeeSubmission: {
            type: Boolean
        },
        proposal: {},
    },
    methods: {
        formatDate: function(data, format='DD/MM/YYYY HH:mm:ss') {
            return data ? moment(data).format(format): '';
        },
        compareRevision: function(revision) {
            console.log(`clicked, lodgement version ${revision.lodgement_number}-${revision.lodgement_sequence}`,
                revision);
            this.lodgementVersion = revision;
        },
        versionKey: function(revision_id) {
            /** Create dynamic viewing-aware table keys for submissions */

            // A key in the form `1732-0` or `1732-1`
            let key = `${revision_id}-${revision_id==this.current_lodgement_version.revision_id? 0: 1}`;
            // console.log(key);
            return key;
        }
    },
    computed: {
        /** Writable computed lodgement version revision object */
        lodgementVersion: {
            get() {
                return this. current_lodgement_version;
            },
            set(version) {
                console.log("Setting new version", version);
                this.current_lodgement_version = version;
                this.$emit('revision-to-display', version);
            }
        }
    },
    created: function() {
        let vm = this;
        this.current_lodgement_version = this.proposal.reversion_revisions[0];
        this.proposal
        this.showingProposal
        this.canSeeSubmission
    }
}
</script>
