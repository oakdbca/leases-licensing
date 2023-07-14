<template>
    <div class="row mb-3">
        <div class="col">
            <template v-for="year in financialYearsArray" :key="year.id">
                <div class="card mb-2">
                    <div class="card-body py-1">
                        <div class="div d-flex align-items-center">
                            <div class="col-sm-4 pe-3">
                                <div class="input-group">
                                    <span class="input-group-text"
                                        >Financial Year</span
                                    >
                                    <input
                                        v-model="year.year"
                                        type="text"
                                        readonly
                                        class="form-control form-control-year"
                                    />
                                </div>
                            </div>
                            <label class="col-sm-2 pe-3">
                                <div class="input-group">
                                    <input
                                        v-model="year.percentage"
                                        step="0.1"
                                        min="0.1"
                                        max="100"
                                        type="number"
                                        class="form-control"
                                    />
                                    <span class="input-group-text">%</span>
                                </div>
                            </label>
                            <div class="pe-3">Gross Turnover</div>
                            <div class="col-sm-3">
                                <div class="input-group">
                                    <span class="input-group-text">$</span>
                                    <input
                                        v-model="year.gross_turnover"
                                        type="number"
                                        class="form-control"
                                    />
                                    <span class="input-group-text">AUD</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </template>
        </div>
    </div>
    <div class="row">
        <div class="col">
            <BootstrapAlert class="py-2 mb-0">
                The approval holder will be asked to upload an audited financial
                statement for each financial year.
            </BootstrapAlert>
        </div>
    </div>
</template>

<script>
import { helpers } from '@/utils/hooks'

export default {
    name: 'PercentageTurnover',
    props: {
        startDate: {
            type: String,
            required: true,
        },
        expiryDate: {
            type: String,
            required: true,
        },
    },
    data: function () {
        return {
            financialYearsArray: this.getFinancialYearsArray(),
        }
    },
    computed: {},
    created() {
        console.log(helpers.financialYearsIncluded('2019-03-03', '2022-07-07'))
        console.log(helpers.financialYearsIncluded('2019-03-03', '2019-03-04'))
        console.log(helpers.financialYearsIncluded('2019-03-03', '2020-01-01'))
        console.log(helpers.financialYearsIncluded('2019-09-03', '2027-02-07'))
    },
    methods: {
        getFinancialYearsArray: function () {
            const financialYearsIncluded = helpers.financialYearsIncluded(
                this.startDate,
                this.expiryDate
            )
            const records = []
            for (let i = 0; i < financialYearsIncluded.length; i++) {
                records.push({
                    id: 0,
                    year: financialYearsIncluded[i],
                    percentage: 0.0,
                    gross_turnover: null,
                })
            }
            return records
        },
    },
}
</script>
<style scoped>
.col-percentage {
    width: 20%;
}
</style>
