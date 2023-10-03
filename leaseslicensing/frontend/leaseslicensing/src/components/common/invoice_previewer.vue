<template>
    <div class="col m-3 p-3 border rounded">
        <BootstrapAlert
            ><span class="fw-bold">Future Invoice Preview</span>: Based on the
            information entered, the following invoices will be
            generated</BootstrapAlert
        >
        <BootstrapAlert
            v-if="context == 'Approval'"
            type="warning"
            icon="exclamation-triangle-fill"
            >Invoices with the issue date as today's date will usually be
            generated the next day.</BootstrapAlert
        >
        <BootstrapAlert
            v-if="chargeMethodKey == 'percentage_of_gross_turnover'"
            type="warning"
            icon="exclamation-triangle-fill"
            >Additional invoices may be created if there is a discrepency
            between the {{ billingCycleAdverb }} and annual
            turnover</BootstrapAlert
        >
        <div v-if="loadingPreviewInvoices" class="text-center">
            <BootstrapSpinner
                class="text-primary invoice-preview-spinner"
                :center-of-screen="false"
            />
        </div>

        <table v-else class="table table-sm table-striped text-left">
            <thead>
                <tr>
                    <th class="text-left">Number</th>
                    <th class="text-left">Issue Date</th>
                    <th class="text-left">Time Period</th>
                    <th class="text-left">Amount</th>
                </tr>
            </thead>
            <tbody>
                <template
                    v-for="invoice in previewInvoices"
                    :key="invoice.number"
                >
                    <tr v-if="!invoice.hide">
                        <td>{{ invoice.number }}</td>
                        <td>{{ invoice.issue_date }}</td>
                        <td>{{ invoice.time_period }}</td>
                        <td>
                            {{ invoice.amount_object.prefix
                            }}<span
                                v-if="invoice.amount_object.amount != null"
                                >{{
                                    currency(invoice.amount_object.amount)
                                }}</span
                            >
                            {{ invoice.amount_object.suffix }}
                        </td>
                    </tr>
                </template>
                <tr v-if="showTotal">
                    <td colspan="3" class="text-end fw-bold pt-2">
                        {{
                            pastInvoiceCount > 0 ? 'Remaining Balance' : 'Total'
                        }}
                    </td>
                    <td>
                        {{ totalAmount }}
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<script>
// Todo: Remove all the code that was used to generate the invoice preview
// as that is now done on the backend
import currency from 'currency.js';
import { helpers } from '@/utils/hooks';

export default {
    name: 'InvoicePreviewer',
    props: {
        previewInvoices: {
            type: Array,
            required: true,
        },
        invoicingDetails: {
            type: Object,
            required: true,
        },
        startDate: {
            type: String,
            required: true,
        },
        expiryDate: {
            type: String,
            required: true,
        },
        chargeMethodKey: {
            type: String,
            required: true,
        },
        loadingPreviewInvoices: {
            type: Boolean,
            required: true,
        },
        showPastInvoices: {
            type: Boolean,
            default: true,
        },
        context: {
            type: String,
            required: true,
        },
    },
    emits: ['updateDefaultInvoicingDate'],
    data: function () {
        return {
            ordinalSuffixOf: helpers.ordinalSuffixOf,
            defaultInvoiceDateSet: false,
        };
    },
    computed: {
        showTotal: function () {
            return ![
                'percentage_of_gross_turnover',
                'percentage_of_gross_turnover_in_advance',
            ].includes(this.chargeMethodKey);
        },
        daysDifference: function () {
            const dateStart = moment(this.startDate);
            const dateEnd = moment(this.expiryDate);
            // Add one day to the end date so it is inclusive
            // Todo: confirm with business that expiry date is inclusive
            return Math.ceil(dateEnd.diff(dateStart, 'days', true)) + 1;
        },
        monthsDifference: function () {
            const dateStart = moment(this.startDate);
            const dateEnd = moment(this.expiryDate);
            return Math.ceil(dateEnd.diff(dateStart, 'months', true));
        },
        quartersDifference: function () {
            const dateStart = moment(this.startDate);
            const dateEnd = moment(this.expiryDate);
            return Math.ceil(dateEnd.diff(dateStart, 'quarters', true));
        },
        yearsDifference: function () {
            const dateStart = moment(this.startDate);
            const dateEnd = moment(this.expiryDate);
            return Math.ceil(dateEnd.diff(dateStart, 'years', true));
        },
        costPerDay: function () {
            if (!this.invoicingDetails.base_fee_amount) {
                return `Enter Base Fee`;
            }
            let costPerDay = currency(
                this.invoicingDetails.base_fee_amount / 365
            );
            return `$${costPerDay}`;
        },
        invoiceCount: function () {
            var invoiceCount = 0;
            // Annually
            if (this.invoicingDetails.invoicing_repetition_type == 1) {
                invoiceCount = this.yearsDifference;
            }
            // Quarterly
            if (this.invoicingDetails.invoicing_repetition_type == 2) {
                invoiceCount = this.quartersDifference;
            }
            // Monthly
            if (this.invoicingDetails.invoicing_repetition_type == 3) {
                invoiceCount = this.monthsDifference;
            }
            return invoiceCount;
        },
        pastInvoiceCount: function () {
            return this.invoices.filter((amountObject) => amountObject.hide)
                .length;
        },
        totalAmount: function () {
            if (!this.invoicingDetails.base_fee_amount) {
                return `Enter Base Fee`;
            }
            let totalAmount =
                this.previewInvoices[this.previewInvoices.length - 1]
                    .amount_running_total;

            return `$${currency(totalAmount)}`;
        },
        billingCycle: function () {
            if (this.invoicingDetails.invoicing_repetition_type == 1) {
                return 'Annual';
            }
            if (this.invoicingDetails.invoicing_repetition_type == 2) {
                return 'Quarter';
            }
            if (this.invoicingDetails.invoicing_repetition_type == 3) {
                return 'Month';
            }
            return 'Unknown';
        },
        billingCycleAdverb: function () {
            if (this.invoicingDetails.invoicing_repetition_type == 1) {
                return 'annually';
            }
            if (this.invoicingDetails.invoicing_repetition_type == 2) {
                return 'quarterly';
            }
            if (this.invoicingDetails.invoicing_repetition_type == 3) {
                return 'monthly';
            }
            return 'Unknown';
        },
        invoicesPerYear: function () {
            if (this.invoicingDetails.invoicing_repetition_type == 1) {
                return 1;
            }
            if (this.invoicingDetails.invoicing_repetition_type == 2) {
                return 4;
            }
            if (this.invoicingDetails.invoicing_repetition_type == 3) {
                return 12;
            }
            return 0;
        },
        invoicingPeriods: function () {
            if (!this.invoicingDetails) {
                return [];
            }
            const invoicingPeriods = [];
            let startDate = moment(this.startDate);
            let endDate = this.getEndOfNextInterval(startDate);
            let expiryDate = moment(this.expiryDate);

            while (endDate.isBefore(this.expiryDate)) {
                let days = endDate.diff(startDate, 'days') + 1;
                invoicingPeriods.push({
                    label: `${startDate.format(
                        'DD/MM/YYYY'
                    )} to ${endDate.format('DD/MM/YYYY')} (${days} days)`,
                    startDate: startDate.format('YYYY-MM-DD'),
                    endDate: endDate.format('YYYY-MM-DD'),
                    days: days,
                });
                startDate = endDate.clone().add(1, 'days');
                endDate = this.getEndOfNextInterval(startDate);
            }
            // Check if one more period is required
            if (expiryDate.isAfter(startDate)) {
                let days = expiryDate.diff(startDate, 'days') + 1;
                invoicingPeriods.push({
                    label: `${startDate.format(
                        'DD/MM/YYYY'
                    )} to ${expiryDate.format('DD/MM/YYYY')} (${days} days)`,
                    startDate: startDate.format('YYYY-MM-DD'),
                    endDate: endDate.format('YYYY-MM-DD'),
                    days: days,
                });
            }
            return invoicingPeriods;
        },
        invoices: function () {
            const invoices = [];
            var firstIssueDate = this.getFirstIssueDate(this.startDate);
            var daysRunningTotal = 0;
            var amountRunningTotal = currency(0.0);
            var issueDate = firstIssueDate.clone();

            for (let i = 0; i < this.invoicingPeriods.length; i++) {
                // Net 30 payment terms
                let dueDate = issueDate.clone().add(30, 'days');
                daysRunningTotal += this.invoicingPeriods[i].days;
                let amountObject = this.getAmountForInvoice(
                    issueDate,
                    this.invoicingPeriods[i].endDate,
                    this.invoicingPeriods[i].days,
                    i
                );
                amountRunningTotal = amountRunningTotal.add(
                    amountObject.amount
                );
                let issueDateNowOrFuture = issueDate.clone();
                if (issueDateNowOrFuture.isBefore(moment())) {
                    issueDateNowOrFuture = moment();
                }
                invoices.push({
                    number: i + 1,
                    issueDate: this.getIssueDate(
                        issueDateNowOrFuture,
                        this.invoicingPeriods[i].endDate
                    ),
                    dueDate: this.getDueDate(dueDate),
                    timePeriod: this.invoicingPeriods[i].label,
                    amountObject: amountObject,
                    daysRunningTotal: daysRunningTotal,
                    amountRunningTotal: amountRunningTotal,
                    hide:
                        !this.showPastInvoices && issueDate.isBefore(moment()),
                });
                issueDate = this.addRepetitionInterval(issueDate);
            }
            return invoices;
        },
    },
    mounted() {},
    methods: {
        currency,
        getAmountForInvoice(issueDate, endDate, days, index) {
            const amountObject = {
                prefix: '$',
                amount: 0.0,
                suffix: '',
            };
            if (this.chargeMethodKey == 'percentage_of_gross_turnover') {
                return this.getAmountForGrossTurnoverInvoiceDisplay(
                    endDate,
                    amountObject
                );
            }

            if (!this.invoicingDetails.base_fee_amount) {
                return amountObject;
            }
            let baseFeeAmount = this.invoicingDetails.base_fee_amount;
            // If this is a full leap year change it to 365 days so it isn't charged more than the full base fee
            if (days == 366) {
                days = 365;
            }
            baseFeeAmount = days * (baseFeeAmount / 365);

            if (this.chargeMethodKey == 'base_fee_plus_annual_cpi') {
                amountObject.amount = currency(baseFeeAmount);
                amountObject.suffix = ' + CPI (ABS)';
            }
            let yearSequenceIndex = this.getYearSequenceIndex(index);
            if (this.chargeMethodKey == 'base_fee_plus_annual_cpi_custom') {
                amountObject.amount = currency(baseFeeAmount);
                let customCpiYear =
                    this.invoicingDetails.custom_cpi_years[yearSequenceIndex];
                if (customCpiYear && customCpiYear.percentage > 0) {
                    amountObject.amount = currency(
                        baseFeeAmount * (1 + customCpiYear.percentage / 100)
                    );
                } else {
                    amountObject.suffix = ' + CPI (CUSTOM)';
                }
            }

            if (
                this.chargeMethodKey == 'base_fee_plus_fixed_annual_percentage'
            ) {
                let percentage = 0.0;
                let suffix =
                    yearSequenceIndex > 0
                        ? `Enter percentage for year ${yearSequenceIndex + 1}`
                        : '';
                let annual_increment_percentage =
                    this.invoicingDetails.annual_increment_percentages[
                        yearSequenceIndex - 1
                    ];
                if (annual_increment_percentage) {
                    percentage =
                        annual_increment_percentage.increment_percentage ||
                        currency(0.0);
                    baseFeeAmount =
                        baseFeeAmount * (1 + currency(percentage) / 100);
                    suffix = '';
                }
                amountObject.amount = currency(baseFeeAmount);
                amountObject.suffix = suffix;
            }

            if (
                this.chargeMethodKey == 'base_fee_plus_fixed_annual_increment'
            ) {
                let increment_amount = 0.0;
                let suffix =
                    yearSequenceIndex > 0
                        ? `Enter increment amount for year ${
                              yearSequenceIndex + 1
                          }`
                        : '';
                let annual_increment_amount =
                    this.invoicingDetails.annual_increment_amounts[
                        yearSequenceIndex - 1
                    ];
                if (annual_increment_amount) {
                    increment_amount =
                        annual_increment_amount.increment_amount ||
                        currency(0.0);
                    baseFeeAmount =
                        currency(baseFeeAmount).add(increment_amount);
                    suffix = '';
                }
                amountObject.amount = currency(baseFeeAmount);
                amountObject.suffix = suffix;
            }

            return amountObject;
        },
        getYearSequenceIndex(index) {
            if (this.invoicingDetails.invoicing_repetition_type == 1) {
                return index;
            }
            if (this.invoicingDetails.invoicing_repetition_type == 2) {
                let quarterlyIndex = index / 4;
                return Math.floor(quarterlyIndex);
            }
            if (this.invoicingDetails.invoicing_repetition_type == 3) {
                let monthlyIndex =
                    index / (12 / this.invoicingDetails.invoicing_once_every);
                return Math.floor(monthlyIndex);
            }
        },
        getAmountForGrossTurnoverInvoiceDisplay(endDate, amountObject) {
            amountObject.prefix = '';
            amountObject.amount = '';
            const financialYear = helpers.getFinancialYearFromDate(endDate);
            const grossTurnoverPercentages =
                this.invoicingDetails.gross_turnover_percentages;
            const grossTurnoverPercentage = grossTurnoverPercentages.find(
                (grossTurnoverPercentage) =>
                    grossTurnoverPercentage.year == financialYear.split('-')[1]
            );
            if (!grossTurnoverPercentage) {
                amountObject.suffix = '???';
                return amountObject;
            }
            amountObject.suffix = `${grossTurnoverPercentage.percentage}% of Gross Turnover`;
            return amountObject;
        },
        addRepetitionInterval(issueDate) {
            if (this.invoicingDetails.invoicing_repetition_type == 1) {
                return issueDate.add(1, 'years');
            }
            if (this.invoicingDetails.invoicing_repetition_type == 2) {
                return issueDate.add(3, 'months');
            }
            if (this.invoicingDetails.invoicing_repetition_type == 3) {
                return issueDate.add(
                    this.invoicingDetails.invoicing_once_every,
                    'months'
                );
            }
            return issueDate;
        },
        getFirstIssueDate(startDate) {
            var firstIssueDate = moment(startDate);
            if (this.chargeMethodKey != 'percentage_of_gross_turnover') {
                firstIssueDate = firstIssueDate.subtract(30, 'days');
            }
            return firstIssueDate;
        },
        getIssueDate(issueDate, endDate) {
            if (this.chargeMethodKey == 'percentage_of_gross_turnover') {
                let q = helpers.getFinancialQuarterFromDate(endDate);
                let financialYear = helpers.getFinancialYearFromDate(endDate);
                return `On receipt of Q${q} ${financialYear} financial statement`;
            }
            return issueDate.format('DD/MM/YYYY');
        },
        getDueDate(dueDate) {
            if (this.chargeMethodKey == 'percentage_of_gross_turnover') {
                return '30 Days after issue';
            }
            return dueDate.format('DD/MM/YYYY');
        },
        getEndOfNextInterval(startDate) {
            if (this.chargeMethodKey == 'percentage_of_gross_turnover') {
                return this.getEndOfNextIntervalGrossTurnover(startDate);
            }
            // All other charge methods are based around each year of the duration of the lease/license
            return this.getEndOfNextIntervalAnnual(startDate);
        },
        getEndOfNextIntervalAnnual(startDate) {
            if (this.invoicingDetails.invoicing_repetition_type == 1) {
                return startDate.clone().add(1, 'years').subtract(1, 'days');
            }
            if (this.invoicingDetails.invoicing_repetition_type == 2) {
                return startDate.clone().add(1, 'quarters').subtract(1, 'days');
            }
            if (this.invoicingDetails.invoicing_repetition_type == 3) {
                return startDate
                    .clone()
                    .add(this.invoicingDetails.invoicing_once_every, 'months')
                    .subtract(1, 'days');
            }
            return startDate;
        },
        getEndOfNextIntervalGrossTurnover(startDate) {
            // Gross turnover intervals are based around financial years and quarters
            if (this.invoicingDetails.invoicing_repetition_type == 1) {
                return this.getEndOfNextFinancialYear(startDate);
            }
            if (this.invoicingDetails.invoicing_repetition_type == 2) {
                return this.getEndOfNextFinancialQuarter(startDate);
            }
            if (this.invoicingDetails.invoicing_repetition_type == 3) {
                return moment(startDate)
                    .endOf('month')
                    .set({ hour: 0, minute: 0, second: 0, millisecond: 0 });
            }
            return startDate;
        },
        getEndOfNextFinancialYear(startDate) {
            const endOfFinancialYear = moment(startDate)
                .set('date', 30)
                .set('month', 5);
            return startDate.isBefore(endOfFinancialYear)
                ? endOfFinancialYear
                : endOfFinancialYear.add(1, 'years');
        },
        getEndOfNextFinancialQuarter(startDate) {
            const quarters = this.getQuartersFromStartMonth();
            for (let i = 0; i < quarters.length; i++) {
                let endOfFinancialQuarter = moment(startDate)
                    .set('month', quarters[i] - 1)
                    .endOf('month')
                    // Reset the time to 00:00:00
                    .set({ hour: 0, minute: 0, second: 0, millisecond: 0 });
                if (startDate < endOfFinancialQuarter) {
                    return endOfFinancialQuarter;
                }
            }
            // None of the four quarters were after the start date, so use the first quarter of the next year
            return moment(startDate)
                .set('month', quarters[0] - 1)
                .set('year', startDate.year() + 1);
        },
        getQuartersFromStartMonth() {
            let startMonth = 3;
            // Start month must be between 1 and 3
            if (this.invoicingDetails.invoicing_quarters_start_month) {
                startMonth =
                    this.invoicingDetails.invoicing_quarters_start_month;
            }
            const quarters = [];
            for (let i = 0; i < 4; i++) {
                quarters.push(startMonth + i * 3);
            }
            return quarters;
        },
    },
};
</script>
