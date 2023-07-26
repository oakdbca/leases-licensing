<template>
    <div class="col m-3 p-3 border rounded">
        <BootstrapAlert
            ><span class="fw-bold">Invoice Preview</span>: Based on the
            information you entered, the following invoices would be
            generated</BootstrapAlert
        >
        <BootstrapAlert
            v-if="chargeMethodKey == 'percentage_of_gross_turnover'"
            type="warning"
            icon="exclamation-triangle-fill"
            >Additional invoices may be created if there is a discrepency
            between the quarterly and annual turnover</BootstrapAlert
        >
        <!-- <div class="mb-3">
            {{ invoiceCount }} invoices will be generated. Days Difference:
            {{ daysDifference }}, Months Difference: {{ monthsDifference }},
            Quarters Difference: {{ quartersDifference }}, Years Difference:
            {{ yearsDifference }}, Total Charge (Before Modifications):
            {{ totalAmount }}
        </div> -->
        <!-- <div>test: {{ test }}</div>
        <div v-for="(period, index) in invoicingPeriods" :key="period.label">
            {{ index }} {{ period.label }}
        </div> -->
        <!-- <div v-for="period in quarterlyInvoicingPeriods" :key="period">
            {{ period }}
        </div> -->
        <div v-if="chargeMethodKey != 'percentage_of_gross_turnover'">
            <table class="table table-sm">
                <thead>
                    <tr>
                        <th scope="col">Duration in Days</th>
                        <th scope="col">Cost per Day</th>
                        <th scope="col">Total of Payments</th>
                    </tr>
                </thead>
                <tbody>
                    <tr class="">
                        <td scope="row">{{ daysDifference }}</td>
                        <td>{{ costPerDay }} (rounded)</td>
                        <td>{{ totalAmount }}</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <table class="table table-sm table-striped">
            <thead>
                <tr>
                    <th>Number</th>
                    <th>Issue Date</th>
                    <th>Time Period</th>
                    <!-- <th>Days Running Total</th>
                    <th>Amount Running Total</th> -->
                    <th>Amount</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="invoice in invoices" :key="invoice.number">
                    <td>{{ invoice.number }}</td>
                    <td>{{ invoice.issueDate }}</td>
                    <td>{{ invoice.timePeriod }}</td>
                    <!-- <td>{{ invoice.daysRunningTotal }}</td>
                    <td>${{ invoice.amountRunningTotal }}</td> -->
                    <td>{{ invoice.amount }}</td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<script>
/*globals moment*/

import currency from 'currency.js'

export default {
    name: 'InvoicePreviewer',
    props: {
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
    },
    computed: {
        showSummary: function () {
            return this.chargeMethodKey != 'percentage_of_gross_turnover'
        },
        daysDifference: function () {
            const dateStart = moment(this.startDate)
            const dateEnd = moment(this.expiryDate)
            // Add one day to the end date so it is inclusive
            // Todo: confirm with business that expiry date is inclusive
            return Math.ceil(dateEnd.diff(dateStart, 'days', true)) + 1
        },
        monthsDifference: function () {
            const dateStart = moment(this.startDate)
            const dateEnd = moment(this.expiryDate)
            return Math.ceil(dateEnd.diff(dateStart, 'months', true))
        },
        quartersDifference: function () {
            const dateStart = moment(this.startDate)
            const dateEnd = moment(this.expiryDate)
            return Math.ceil(dateEnd.diff(dateStart, 'quarters', true))
        },
        yearsDifference: function () {
            const dateStart = moment(this.startDate)
            const dateEnd = moment(this.expiryDate)
            return Math.ceil(dateEnd.diff(dateStart, 'years', true))
        },
        costPerDay: function () {
            if (!this.invoicingDetails.base_fee_amount) {
                return `Enter Base Fee`
            }
            let costPerDay = currency(
                this.invoicingDetails.base_fee_amount / 365
            )
            return `$${costPerDay}`
        },
        invoiceCount: function () {
            var invoiceCount = 0
            // Annually
            if (this.invoicingDetails.invoicing_repetition_type == 1) {
                invoiceCount = this.yearsDifference
            }
            // Quarterly
            if (this.invoicingDetails.invoicing_repetition_type == 2) {
                invoiceCount = this.quartersDifference
            }
            // Monthly
            if (this.invoicingDetails.invoicing_repetition_type == 3) {
                invoiceCount = this.monthsDifference
            }
            return invoiceCount
        },
        totalAmount: function () {
            if (!this.invoicingDetails.base_fee_amount) {
                return `Enter Base Fee`
            }
            let totalAmount = currency(
                this.daysDifference *
                    (this.invoicingDetails.base_fee_amount / 365)
            )
            return `$${totalAmount}`
        },
        billingCycle: function () {
            if (this.invoicingDetails.invoicing_repetition_type == 1) {
                return 'Annual'
            }
            if (this.invoicingDetails.invoicing_repetition_type == 2) {
                return 'Quarter'
            }
            if (this.invoicingDetails.invoicing_repetition_type == 3) {
                return 'Month'
            }
            return 'Unknown'
        },
        invoicesPerYear: function () {
            if (this.invoicingDetails.invoicing_repetition_type == 1) {
                return 1
            }
            if (this.invoicingDetails.invoicing_repetition_type == 2) {
                return 4
            }
            if (this.invoicingDetails.invoicing_repetition_type == 3) {
                return 12
            }
            return 0
        },
        invoicingPeriods: function () {},
        invoicingPeriods: function () {
            const invoicingPeriods = []
            var startDate = moment(this.startDate)
            var endDate = this.getEndOfNextInterval(startDate)
            var expiryDate = moment(this.expiryDate)

            while (endDate.isBefore(this.expiryDate)) {
                let days = endDate.diff(startDate, 'days') + 1
                invoicingPeriods.push({
                    label: `${startDate.format(
                        'DD/MM/YYYY'
                    )} to ${endDate.format('DD/MM/YYYY')} (${days} days)`,
                    startDate: startDate.format('DD/MM/YYYY'),
                    endDate: endDate.format('DD/MM/YYYY'),
                    days: days,
                })
                startDate = endDate.clone().add(1, 'days')
                endDate = this.getEndOfNextInterval(startDate)
            }
            // Check if one more period is required
            if (expiryDate.isAfter(startDate)) {
                let days = expiryDate.diff(startDate, 'days') + 1
                invoicingPeriods.push({
                    label: `${startDate.format(
                        'DD/MM/YYYY'
                    )} to ${expiryDate.format('DD/MM/YYYY')} (${days} days)`,
                    startDate: startDate.format('DD/MM/YYYY'),
                    endDate: expiryDate.format('DD/MM/YYYY'),
                    days: days,
                })
            }
            return invoicingPeriods
        },
        invoices: function () {
            const invoices = []
            var issueDate = this.getFirstIssueDate(this.startDate)
            var daysRunningTotal = 0
            var amountRunningTotal = currency(0.0)
            for (let i = 0; i < this.invoicingPeriods.length; i++) {
                // Net 30 payment terms
                let dueDate = issueDate.clone().add(30, 'days')
                daysRunningTotal += this.invoicingPeriods[i].days
                amountRunningTotal = amountRunningTotal.add(
                    this.getAmountForInvoice(this.invoicingPeriods[i].days)
                )
                invoices.push({
                    number: i + 1,
                    issueDate: this.getIssueDate(issueDate),
                    dueDate: this.getDueDate(dueDate),
                    timePeriod: this.invoicingPeriods[i].label,
                    amount: this.getAmountForInvoiceDisplay(
                        issueDate,
                        this.invoicingPeriods[i].days
                    ),
                    daysRunningTotal: daysRunningTotal,
                    amountRunningTotal: amountRunningTotal,
                })
                issueDate = this.addRepetitionInterval(issueDate)
            }
            return invoices
        },
    },
    mounted() {},
    methods: {
        getAmountForInvoice(days) {
            if (!this.invoicingDetails.base_fee_amount) {
                return 0.0
            }
            let baseFeeAmount = this.invoicingDetails.base_fee_amount
            baseFeeAmount = days * (baseFeeAmount / 365)
            return baseFeeAmount
        },
        getAmountForInvoiceDisplay(issueDate, days) {
            if (this.chargeMethodKey == 'percentage_of_gross_turnover') {
                return this.getAmountForGrossTurnoverInvoice(issueDate)
            }
            // If this is a full leap year change it to 365 days so it isn't charged more than the full base fee
            if (days == 366) {
                days = 365
            }
            if (!this.invoicingDetails.base_fee_amount) {
                return 'Enter Base Fee'
            }
            let baseFeeAmount = this.invoicingDetails.base_fee_amount
            baseFeeAmount = days * (baseFeeAmount / 365)

            if (this.chargeMethodKey == 'base_fee_plus_annual_cpi') {
                return `$${currency(baseFeeAmount)} + CPI (ABS)`
            }
            if (this.chargeMethodKey == 'base_fee_plus_annual_cpi_custom') {
                return `$${currency(baseFeeAmount)} + CPI (CUSTOM)`
            }

            if (
                this.chargeMethodKey == 'base_fee_plus_fixed_annual_increment'
            ) {
                return `$${currency(baseFeeAmount)} + Annual Increment`
            }

            if (
                this.chargeMethodKey == 'base_fee_plus_fixed_annual_percentage'
            ) {
                let percentage = this.invoicingDetails
                    .annual_increment_percentages
                return `$${currency(
                    baseFeeAmount
                )} + Annual Increment (Percentage)`
            }

            return `$${currency(baseFeeAmount)}`
        },
        getAmountForGrossTurnoverInvoice(issueDate) {
            console.log(issueDate.year())
            const grossTurnoverPercentages =
                this.invoicingDetails.gross_turnover_percentages
            const grossTurnoverPercentage = grossTurnoverPercentages.find(
                (grossTurnoverPercentage) =>
                    grossTurnoverPercentage.year == issueDate.year()
            )
            console.log(grossTurnoverPercentage)
            if (!grossTurnoverPercentage) {
                return '???'
            }
            return `${grossTurnoverPercentage.percentage}% of Gross Turnover`
        },
        addRepetitionInterval(issueDate) {
            if (this.invoicingDetails.invoicing_repetition_type == 1) {
                return issueDate.add(1, 'years')
            }
            if (this.invoicingDetails.invoicing_repetition_type == 2) {
                return issueDate.add(3, 'months')
            }
            if (this.invoicingDetails.invoicing_repetition_type == 3) {
                return issueDate.add(1, 'months')
            }
            return issueDate
        },
        getFirstIssueDate(startDate) {
            var today = moment()
            var firstIssueDate = moment(startDate)
            if (this.chargeMethodKey != 'percentage_of_gross_turnover') {
                return this.getEndOfNextIntervalAnnual(firstIssueDate).add(
                    1,
                    'days'
                )
            }
            firstIssueDate.set(
                'date',
                this.invoicingDetails.invoicing_day_of_month
            )
            firstIssueDate.set(
                'month',
                this.invoicingDetails.invoicing_month_of_year - 1
            )
            // This works for quarterly invoicing
            if (this.invoicingDetails.invoicing_repetition_type == 2) {
                let firstIssueDate = moment(startDate)
                // This works for annual and monthly invoicing
                while (firstIssueDate.isBefore(today)) {
                    firstIssueDate = this.getEndOfNextFinancialQuarter(
                        firstIssueDate
                    ).add(1, 'days')
                }
                return firstIssueDate.set(
                    'date',
                    this.invoicingDetails.invoicing_day_of_month
                )
            }
            // This works for annual and monthly invoicing
            while (firstIssueDate.isBefore(today)) {
                firstIssueDate = this.addRepetitionInterval(firstIssueDate)
            }
            return firstIssueDate
        },
        getIssueDate(issueDate) {
            if (this.chargeMethodKey == 'percentage_of_gross_turnover') {
                return `On receipt of ${issueDate.year() - 2}-${
                    issueDate.year() - 1
                } financial statement`
            }
            return issueDate.format('DD/MM/YYYY')
        },
        getDueDate(dueDate) {
            if (this.chargeMethodKey == 'percentage_of_gross_turnover') {
                return '30 Days after issue'
            }
            return dueDate.format('DD/MM/YYYY')
        },
        getTimePeriod(startDate, endDate, index) {
            if (this.invoicingDetails.invoicing_repetition_type == 1) {
                console.log(`Index: ${index}`)
                return this.invoicingPeriods[index]
                    ? this.invoicingPeriods[index].label
                    : ''
            }
        },
        getInvoicingPeriod(startDate, endDate) {
            for (let i = 0; i < this.invoicingPeriods.length; i++) {
                const invoicablePeriod = this.invoicingPeriods[i]
                if (
                    startDate.isBetween(invoicablePeriod) &&
                    endDate.isSame(invoicablePeriod.endDate)
                ) {
                    return invoicablePeriod
                }
            }
            return
        },
        getEndOfNextInterval(startDate) {
            if (this.chargeMethodKey == 'percentage_of_gross_turnover') {
                return this.getEndOfNextIntervalGrossTurnover(startDate)
            }
            // All other charge methods are based around each year of the duration of the lease/license
            return this.getEndOfNextIntervalAnnual(startDate)
        },
        getEndOfNextIntervalAnnual(startDate) {
            if (this.invoicingDetails.invoicing_repetition_type == 1) {
                return startDate.clone().add('years', 1).subtract('days', 1)
            }
            if (this.invoicingDetails.invoicing_repetition_type == 2) {
                return startDate.clone().add('quarters', 1).subtract('days', 1)
            }
            if (this.invoicingDetails.invoicing_repetition_type == 3) {
                return startDate.clone().add('months', 1).subtract('days', 1)
            }
            return startDate
        },
        getEndOfNextIntervalGrossTurnover(startDate) {
            // Gross turnover intervals are based around financial years and quarters
            if (this.invoicingDetails.invoicing_repetition_type == 1) {
                return this.getEndOfNextFinancialYear(startDate)
            }
            if (this.invoicingDetails.invoicing_repetition_type == 2) {
                return this.getEndOfNextFinancialQuarter(startDate)
            }
            if (this.invoicingDetails.invoicing_repetition_type == 3) {
                return moment(startDate)
                    .endOf('month')
                    .set({ hour: 0, minute: 0, second: 0, millisecond: 0 })
            }
            return startDate
        },
        getEndOfNextFinancialYear(startDate) {
            const endOfFinancialYear = moment(startDate)
                .set('date', 30)
                .set('month', 5)
            return startDate.isBefore(endOfFinancialYear)
                ? endOfFinancialYear
                : endOfFinancialYear.add(1, 'years')
        },
        getEndOfNextFinancialQuarter(startDate) {
            const quarters = this.getQuartersFromStartMonth()
            console.log(`\n\nStart Date: ${startDate}`)
            for (let i = 0; i < quarters.length; i++) {
                let endOfFinancialQuarter = moment(startDate)
                    .set('month', quarters[i] - 1)
                    .endOf('month')
                    // Reset the time to 00:00:00
                    .set({ hour: 0, minute: 0, second: 0, millisecond: 0 })
                if (startDate < endOfFinancialQuarter) {
                    return endOfFinancialQuarter
                }
            }
            // None of the four quarters were after the start date, so use the first quarter of the next year
            return moment(startDate)
                .set('month', quarters[0] - 1)
                .set('year', startDate.year() + 1)
        },
        getQuartersFromStartMonth() {
            const quarters = []
            for (let i = 0; i < 4; i++) {
                quarters.push(
                    this.invoicingDetails.invoicing_quarters_start_month + i * 3
                )
            }
            return quarters
        },
    },
}
</script>
