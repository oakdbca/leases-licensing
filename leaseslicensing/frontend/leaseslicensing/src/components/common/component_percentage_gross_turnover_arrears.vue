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
                                        step="0.1"
                                        min="0"
                                        max="100"
                                        type="number"
                                        class="form-control"
                                        :readonly="
                                            !editingFromProposalPage &&
                                            (hasGrossTurnoverEntries(year) ||
                                                year.locked)
                                        "
                                        @change="$emit('onChangePercentage')"
                                        @keyup="$emit('onChangePercentage')"
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
                                            grossAnnualTurnoverReadonly(year)
                                        "
                                        @change="
                                            grossAnnualTurnoverChanged(
                                                $event,
                                                year
                                            )
                                        "
                                        @keyup="
                                            grossAnnualTurnoverChanged(
                                                $event,
                                                year
                                            )
                                        "
                                    />
                                    <span class="input-group-text">AUD</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div
                        v-if="
                            (!editingFromProposalPage ||
                                !financialYearHasPassed(year.financial_year)) &&
                            year.gross_turnover &&
                            year.discrepency
                        "
                        class="card-body"
                    >
                        <BootstrapAlert>
                            <template v-if="year.discrepency > 0">
                                The gross annual turnover entered is greater
                                than the sum of the four quarters.<br />
                                When you complete editing, the system will
                                generate a charge invoice record for
                                <strong
                                    >${{ currency(year.discrepency) }}</strong
                                >
                            </template>
                            <template v-else-if="year.discrepency < 0">
                                The gross annual turnover entered is less than
                                the sum of the four quarters.<br />
                                When you complete editing, the system will
                                generate a refund invoice record for
                                <strong
                                    >${{
                                        currency(Math.abs(year.discrepency))
                                    }}</strong
                                >
                            </template>
                        </BootstrapAlert>
                    </div>
                    <div
                        v-if="
                            invoicingReptitionQuarterly &&
                            (!editingFromProposalPage ||
                                !financialYearHasPassed(year.financial_year))
                        "
                        class="card-body py-3"
                    >
                        <div
                            v-for="quarter in year.quarters"
                            :key="year.year + quarter.quarter"
                            class="div d-flex align-items-center pb-1"
                        >
                            <div class="col-sm-5">&nbsp;</div>
                            <div class="pe-3 quarter">
                                <div class="input-group">
                                    <input
                                        type="text"
                                        readonly
                                        class="form-control form-control-quarter"
                                        :value="`Q${
                                            quarter.quarter
                                        } ${getFinancialQuarterLabel(
                                            quarter.quarter
                                        )}`"
                                    />
                                </div>
                            </div>
                            <div class="pe-3">Gross Turnover</div>
                            <div class="col-sm-3">
                                <div class="input-group">
                                    <span class="input-group-text">$</span>
                                    <input
                                        v-model="quarter.gross_turnover"
                                        type="number"
                                        class="form-control"
                                        :readonly="
                                            grossQuarterlyTurnoverReadonly(
                                                year.financial_year,
                                                quarter.quarter
                                            ) ||
                                            (!editingFromProposalPage &&
                                                year.locked)
                                        "
                                        @change="
                                            $emit(
                                                'onChangeQuarterlyGrossTurnover'
                                            )
                                        "
                                        @keyup="
                                            $emit(
                                                'onChangeQuarterlyGrossTurnover'
                                            )
                                        "
                                    />
                                    <span class="input-group-text">AUD</span>
                                </div>
                            </div>
                        </div>
                        <div
                            v-if="quartersTotal(year) > 0"
                            class="div d-flex align-items-center pb-1 pt-2"
                        >
                            <div class="col-sm-4 pe-3">&nbsp;</div>
                            <div class="pe-3 quarter">
                                <div class="input-group"></div>
                            </div>
                            <div class="pe-3">Quarters Total&nbsp;&nbsp;</div>
                            <div class="col-sm-3">
                                <div class="input-group">
                                    <span class="input-group-text">$</span>
                                    <input
                                        type="text"
                                        readonly
                                        class="form-control"
                                        :value="quartersTotal(year)"
                                    />
                                    <span class="input-group-text">AUD</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div
                        v-if="
                            !invoicingReptitionQuarterly &&
                            (!editingFromProposalPage ||
                                !financialYearHasPassed(year.financial_year))
                        "
                        class="card-body py-3"
                    >
                        <div
                            v-for="month in year.months"
                            :key="month.year + month.month"
                            class="div d-flex align-items-center pb-1"
                        >
                            <div class="col-sm-5">&nbsp;</div>
                            <div class="pe-3 quarter">
                                <div class="input-group">
                                    <input
                                        type="text"
                                        readonly
                                        class="form-control form-control-quarter"
                                        :value="`${month.label}`"
                                    />
                                </div>
                            </div>
                            <div class="pe-3">Gross Turnover</div>
                            <div class="col-sm-3">
                                <div class="input-group">
                                    <span class="input-group-text">$</span>
                                    <input
                                        v-model="month.gross_turnover"
                                        type="number"
                                        class="form-control"
                                        :readonly="
                                            grossMonthlyTurnoverReadonly(
                                                month.year,
                                                month.month
                                            ) ||
                                            (!editingFromProposalPage &&
                                                month.locked)
                                        "
                                        @change="
                                            $emit(
                                                'onChangeMonthlyGrossTurnover'
                                            )
                                        "
                                        @keyup="
                                            $emit(
                                                'onChangeMonthlyGrossTurnover'
                                            )
                                        "
                                    />
                                    <span class="input-group-text">AUD</span>
                                </div>
                            </div>
                        </div>
                        <div
                            v-if="monthsTotal(year) > 0"
                            class="div d-flex align-items-center pb-1 pt-2"
                        >
                            <div class="col-sm-4 pe-3">&nbsp;</div>
                            <div class="pe-3 quarter">
                                <div class="input-group"></div>
                            </div>
                            <div class="pe-3">Months Total&nbsp;&nbsp;</div>
                            <div class="col-sm-3">
                                <div class="input-group">
                                    <span class="input-group-text">$</span>
                                    <input
                                        type="text"
                                        readonly
                                        class="form-control"
                                        :value="monthsTotal(year)"
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
            <BootstrapAlert v-if="context == 'Proposal'" class="py-2 mb-0">
                The system will generate compliances to ask for an audited
                financial statement for each financial quarter and year
            </BootstrapAlert>
        </div>
    </div>
</template>

<script>
import currency from 'currency.js';
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
        invoicingRepetitionType: {
            type: Number,
            required: true,
        },
        invoicingRepetitionTypeKey: {
            type: String,
            required: true,
        },
        proposalProcessingStatusId: {
            type: String,
            required: true,
        },
        context: {
            type: String,
            required: true,
        },
    },
    emits: [
        'updateGrossTurnoverPercentages',
        'onChangePercentage',
        'onChangeAnnualGrossTurnover',
        'onChangeQuarterlyGrossTurnover',
        'onChangeMonthlyGrossTurnover',
    ],
    data: function () {
        return {
            originalAnnualTurnover: null,
            financialYearHasPassed: helpers.financialYearHasPassed,
            getFinancialQuarterLabel: helpers.getFinancialQuarterLabel,
            helpers: helpers,
            currency: currency,
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
        invoicingReptitionQuarterly: function () {
            // Todo: Relying on ids like this is dangerous - need to use the key property instead
            return this.invoicingRepetitionType == 2;
        },
    },
    watch: {
        invoicingRepetitionType: function (newVal) {
            if (newVal) {
                this.populateFinancialYearsArray(
                    helpers.financialYearsIncluded(
                        this.startDate,
                        this.expiryDate
                    )
                );
            }
        },
    },
    created: function () {
        const financialYearsIncluded = helpers.financialYearsIncluded(
            this.startDate,
            this.expiryDate
        );
        this.populateFinancialYearsArray(financialYearsIncluded);
    },
    methods: {
        editingFromProposalPage: function () {
            return (
                constants.PROPOSAL_STATUS.APPROVED_EDITING_INVOICING.ID ==
                this.proposalProcessingStatusId
            );
        },
        grossAnnualTurnoverReadonly: function (grossTurnoverPercentage) {
            // Gross turnover is readonly if the financial year hasn't passed
            // or if the proposal is being edited from the proposal details page
            // Todo: Only allow entry of the annual figure if all the quarterly figures are already entered
            return (
                !this.financialYearHasPassed(
                    grossTurnoverPercentage.financial_year
                ) ||
                (!this.editingFromProposalPage &&
                    !this.allQuartersEntered(grossTurnoverPercentage))
            );
        },
        grossQuarterlyTurnoverReadonly: function (
            financialYear,
            financialQuarter
        ) {
            // Gross turnover is readonly if the financial quarter hasn't passed
            // or if the proposal is being edited from the proposal details page
            return !this.helpers.financialQuarterHasPassed(
                financialYear,
                financialQuarter
            );
        },
        grossMonthlyTurnoverReadonly: function (year, month) {
            // Gross turnover is readonly if the month hasn't passed
            return !this.helpers.monthHasPassed(year, month);
        },
        allQuartersEntered: function (grossTurnoverPercentage) {
            // Returns true if all the quarterly figures have been entered

            for (let i = 0; i < grossTurnoverPercentage.quarters.length; i++) {
                if (
                    grossTurnoverPercentage.quarters[i].gross_turnover ==
                        null ||
                    grossTurnoverPercentage.quarters[i].gross_turnover == ''
                ) {
                    return false;
                }
            }
            return true;
        },
        quartersTotal: function (grossTurnoverPercentage) {
            return grossTurnoverPercentage.quarters.reduce(
                (total, quarter) =>
                    total + parseFloat(quarter.gross_turnover || 0),
                0
            );
        },
        monthsTotal: function (grossTurnoverPercentage) {
            return grossTurnoverPercentage.months.reduce(
                (total, month) => total + parseFloat(month.gross_turnover || 0),
                0
            );
        },
        grossAnnualTurnoverChanged: function (event, year) {
            var total_of_quarters = year.quarters.reduce(
                (total, quarter) =>
                    total + parseFloat(quarter.gross_turnover || 0),
                0
            );
            if (event.target.value != total_of_quarters) {
                year.discrepency = currency(
                    (event.target.value * year.percentage) / 100 -
                        (total_of_quarters * year.percentage) / 100
                );
            } else {
                year.discrepency = 0;
            }
            this.$emit('onChangeAnnualGrossTurnover');
        },
        getPeriods: function (year) {
            if (this.invoicingReptitionQuarterly) {
                return year.quarters;
            }
            return year.months;
        },
        hasGrossTurnoverEntries: function (year) {
            var periods = this.getPeriods(year);
            for (let i = 0; i < periods.length; i++) {
                if (
                    periods[i].gross_turnover != null &&
                    periods[i].gross_turnover != ''
                ) {
                    return true;
                }
            }
            return false;
        },
        hasAllGrossTurnoverEntries: function (year) {
            var periods = this.getPeriods(year);
            for (let i = 0; i < periods.length; i++) {
                if (
                    periods[i].gross_turnover == null ||
                    periods[i].gross_turnover == ''
                ) {
                    return false;
                }
            }
            return true;
        },
        populateFinancialYearsArray: function (financialYearsIncluded) {
            var financialYear = null;
            var financialYears = [];

            for (let i = 0; i < financialYearsIncluded.length; i++) {
                let year = financialYearsIncluded[i].split('-')[1];
                if (
                    this.grossTurnoverPercentagesComputed.filter(
                        (x) => x.year == year
                    ).length == 0
                ) {
                    financialYear = {
                        year: year,
                        financial_year: financialYearsIncluded[i],
                        percentage: 0.0,
                        gross_turnover: null,
                        quarters: [],
                    };
                    financialYears.push(financialYear);
                }
                if (this.invoicingReptitionQuarterly) {
                    let grossTurnoverPercentage = this
                        .grossTurnoverPercentagesComputed[i]
                        ? this.grossTurnoverPercentagesComputed[i]
                        : financialYear;
                    if (!grossTurnoverPercentage.quarters) {
                        grossTurnoverPercentage.quarters = [];
                    }
                    grossTurnoverPercentage.months = [];
                    for (let j = 0; j < 4; j++) {
                        if (
                            !helpers.financialQuarterIncluded(
                                this.startDate,
                                this.expiryDate,
                                grossTurnoverPercentage.financial_year,
                                j + 1
                            )
                        ) {
                            continue;
                        }
                        if (!grossTurnoverPercentage.quarters[j]) {
                            if (
                                !grossTurnoverPercentage.quarters.find(
                                    (x) => x.quarter == j + 1
                                )
                            ) {
                                grossTurnoverPercentage.quarters.push({
                                    quarter: j + 1,
                                    gross_turnover: null,
                                });
                            }
                        }
                    }
                } else {
                    let financialMonths = helpers.getFinancialMonths(
                        financialYearsIncluded[i]
                    );
                    let grossTurnoverPercentage = this
                        .grossTurnoverPercentagesComputed[i]
                        ? this.grossTurnoverPercentagesComputed[i]
                        : financialYear;
                    if (!grossTurnoverPercentage.months) {
                        grossTurnoverPercentage.months = [];
                    }
                    grossTurnoverPercentage.quarters = [];
                    for (let j = 0; j < financialMonths.length; j++) {
                        let year = financialMonths[j].year;
                        let month = financialMonths[j].month;
                        let monthStart = moment(
                            `${year}-${month}-01`,
                            'YYYY-MM-DD'
                        );
                        let monthEnd = moment(monthStart).endOf('month');
                        if (
                            !helpers.datesOverlap(
                                this.startDate,
                                this.expiryDate,
                                monthStart,
                                monthEnd
                            )
                        ) {
                            continue;
                        }
                        if (
                            !grossTurnoverPercentage.months.find(
                                (x) => x.month == month && x.year == year
                            )
                        ) {
                            grossTurnoverPercentage.months.push({
                                year: year,
                                month: month,
                                label: financialMonths[j].label,
                                gross_turnover: null,
                            });
                        }
                    }
                }
            }
            financialYears = this.grossTurnoverPercentagesComputed.concat(
                ...financialYears
            );
            financialYears.sort((a, b) => a.year - b.year);
            this.grossTurnoverPercentagesComputed = financialYears;
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
