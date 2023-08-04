<template>
    <div class="row mb-3">
        <div class="col">
            <template
                v-for="year in grossTurnoverPercentagesComputed"
                :key="year.year"
            >
                <div class="card mb-2">
                    <div class="card-body py-3 border-bottom">
                        <div class="div d-flex align-items-center">
                            <div class="col-sm-4 pe-3">
                                <div class="input-group">
                                    <span class="input-group-text"
                                        >Financial Year</span
                                    >
                                    <input
                                        v-model="year.financial_year"
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
                                        step="0.01"
                                        min="0"
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
                                        :readonly="
                                            grossTurnoverReadonly(
                                                year.financial_year
                                            )
                                        "
                                    />
                                    <span class="input-group-text">AUD</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="card-body py-3">
                        <div
                            v-for="index in parseInt(4)"
                            :key="index"
                            class="div d-flex align-items-center pb-1"
                        >
                            <div class="col-sm-4 pe-3">&nbsp;</div>
                            <div class="pe-3 quarter">
                                <div class="input-group">
                                    <input
                                        type="text"
                                        readonly
                                        class="form-control form-control-quarter"
                                        :value="`Q${index} ${getFinancialQuarterLabel(
                                            index
                                        )}`"
                                    />
                                </div>
                            </div>
                            <div class="pe-3">Gross Turnover</div>
                            <div class="col-sm-3">
                                <div class="input-group">
                                    <span class="input-group-text">$</span>
                                    <input
                                        v-model="year.gross_turnover"
                                        type="number"
                                        class="form-control"
                                        :readonly="
                                            grossTurnoverReadonly(
                                                year.financial_year
                                            )
                                        "
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
    <div class="row mb-3 pb-3 border-bottom">
        <div class="col">
            <BootstrapAlert class="py-2 mb-0">
                The system will generate compliances to ask for an audited
                financial statement for each financial quarter and year
            </BootstrapAlert>
        </div>
    </div>
</template>

<script>
import { constants, helpers } from '@/utils/hooks';

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
        grossTurnoverPercentages: {
            type: Array,
            required: true,
        },
        proposalProcessingStatusId: {
            type: String,
            required: true,
        },
    },
    emits: ['updateGrossTurnoverPercentages'],
    data: function () {
        return {
            financialYearHasPassed: helpers.financialYearHasPassed,
            getFinancialQuarterLabel: helpers.getFinancialQuarterLabel,
        };
    },
    computed: {
        grossTurnoverPercentagesComputed: {
            get: function () {
                return this.grossTurnoverPercentages;
            },
            set: function (value) {
                this.$emit('updateGrossTurnoverPercentages', value);
            },
        },
    },
    created: function () {
        const financialYearsIncluded = helpers.financialYearsIncluded(
            this.startDate,
            this.expiryDate
        );
        if (
            this.grossTurnoverPercentages.length !=
            financialYearsIncluded.length
        ) {
            this.populateFinancialYearsArray(financialYearsIncluded);
        }
    },
    methods: {
        grossTurnoverReadonly: function (financialYear) {
            // Gross turnover is readonly if the financial year hasn't passed
            // or if the proposal is being edited from the proposal details page
            return (
                !this.financialYearHasPassed(financialYear) ||
                constants.PROPOSAL_STATUS.APPROVED_EDITING_INVOICING.ID ==
                    this.proposalProcessingStatusId
            );
        },
        populateFinancialYearsArray: function (financialYearsIncluded) {
            var financialYears = [];

            for (let i = 0; i < financialYearsIncluded.length; i++) {
                let year = financialYearsIncluded[i].split('-')[1];
                if (
                    this.grossTurnoverPercentagesComputed.filter(
                        (x) => x.year == year
                    ).length == 0
                ) {
                    financialYears.push({
                        id: 0,
                        year: year,
                        financial_year: financialYearsIncluded[i],
                        percentage: 0.0,
                        gross_turnover: null,
                    });
                }
            }
            this.grossTurnoverPercentagesComputed =
                this.grossTurnoverPercentagesComputed.concat(...financialYears);
        },
    },
};
</script>

<style scoped>
.quarter {
    width: 142px;
}
.form-control-quarter {
    width: 50px;
}
</style>
