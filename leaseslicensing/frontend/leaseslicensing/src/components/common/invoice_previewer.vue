<template>
    <div class="col m-3 p-3 border rounded">
        <BootstrapAlert
            ><span class="fw-bold">Invoice Preview</span>: Based on the
            information you entered, the following invoices would be
            generated</BootstrapAlert
        >
        <div class="mb-3">
            {{ invoiceCount }} invoices will be generated. Days Difference:
            {{ daysDifference }}, Months Difference: {{ monthsDifference }},
            Quarters Difference: {{ quartersDifference }}, Years Difference:
            {{ yearsDifference }}, Total Charge (Before Modifications):
            {{ totalAmount }}
        </div>
        <!-- {{ invoicablePeriods }} -->
        <table class="table table-sm table-striped">
            <thead>
                <tr>
                    <th>Number</th>
                    <th>Issue Date</th>
                    <th>Due Date</th>
                    <th>Time Period</th>
                    <th>Amount</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="invoice in invoices" :key="invoice.number">
                    <td>{{ invoice.number }}</td>
                    <td>{{ invoice.issueDate }}</td>
                    <td>{{ invoice.dueDate }}</td>
                    <td>{{ invoice.timePeriod }}</td>
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
    data() {
        return {
            repetitionIntervalAdded: 0,
        }
    },
    computed: {
        daysDifference: function () {
            const date1 = new Date(this.startDate)
            const date2 = new Date(this.expiryDate)
            const diffTime = Math.abs(date2 - date1)
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
            return diffDays
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
        invoicablePeriods: function () {
            const invoicablePeriods = []
            let startDate = moment(this.startDate)
            let endDate = this.getEndOfNextFinancialYear(startDate)
            while (endDate.isBefore(this.expiryDate)) {
                let days = endDate.diff(startDate, 'days') + 1
                invoicablePeriods.push({
                    label: `${startDate.format(
                        'DD/MM/YYYY'
                    )} to ${endDate.format('DD/MM/YYYY')} (${days} days)`,
                    startDate: startDate.format('DD/MM/YYYY'),
                    endDate: endDate.format('DD/MM/YYYY'),
                    days: days,
                })
                startDate = endDate.clone().add(1, 'days')
                endDate = this.getEndOfNextFinancialYear(startDate)
            }
            // Check if one more financial year is required
            let expiryDate = moment(this.expiryDate)
            if (expiryDate.isAfter(startDate)) {
                let days = expiryDate.diff(startDate, 'days') + 1
                invoicablePeriods.push({
                    label: `${startDate.format(
                        'DD/MM/YYYY'
                    )} to ${expiryDate.format('DD/MM/YYYY')} (${days} days)`,
                    startDate: startDate.format('DD/MM/YYYY'),
                    endDate: expiryDate.format('DD/MM/YYYY'),
                    days: days,
                })
            }
            return invoicablePeriods
        },
        invoices: function () {
            const invoices = []
            // Todo: First day of invoicing past the start date
            var issueDate = this.getFirstIssueDate(this.startDate)
            for (
                let i = 0;
                i < this.invoiceCount + this.repetitionIntervalAdded;
                i++
            ) {
                // Net 30 payment terms
                let dueDate = issueDate.clone().add(30, 'days')
                let invoicingPeriodIndex = Math.round(i / this.invoicesPerYear)
                console.log(`\ninvoicesPerYear = ${this.invoicesPerYear}`)
                console.log(`\n ${invoicingPeriodIndex}`)
                invoices.push({
                    number: i + 1,
                    issueDate: this.getIssueDate(issueDate),
                    dueDate: this.getDueDate(dueDate),
                    timePeriod:
                        this.invoicablePeriods[invoicingPeriodIndex].label,
                    amount: this.getAmountForInvoice(
                        issueDate,
                        this.invoicablePeriods[invoicingPeriodIndex].days
                    ),
                })
                issueDate = this.addRepetitionInterval(issueDate)
            }
            return invoices
        },
    },
    mounted() {},
    methods: {
        getAmountForInvoice(issueDate, days) {
            if (this.chargeMethodKey == 'percentage_of_gross_turnover') {
                return this.getAmountForGrossTurnoverInvoice(issueDate)
            }
            // If this is a full leap year change it to 365 days so it is charged the full base fee
            if (days == 366) {
                days = 365
            }
            if (!this.invoicingDetails.base_fee_amount) {
                return 'Enter Base Fee'
            }
            let baseFeeAmount = this.invoicingDetails.base_fee_amount
            baseFeeAmount =
                (this.daysDifference * (baseFeeAmount / 365)) /
                this.invoiceCount

            if (this.chargeMethodKey == 'base_fee_plus_annual_cpi') {
                return `$${currency(baseFeeAmount)} + CPI (ABS)`
            }
            if (this.chargeMethodKey == 'base_fee_plus_annual_cpi_custom') {
                return `$${currency(baseFeeAmount)} + CPI (CUSTOM)`
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
            this.repetitionIntervalAdded = 1
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
            firstIssueDate.set(
                'date',
                this.invoicingDetails.invoicing_day_of_month
            )
            firstIssueDate.set(
                'month',
                this.invoicingDetails.invoicing_month_of_year - 1
            )
            if (firstIssueDate.isBefore(today)) {
                firstIssueDate = this.addRepetitionInterval(firstIssueDate)
            }
            return firstIssueDate
        },
        getIssueDate(issueDate) {
            if (this.chargeMethodKey == 'percentage_of_gross_turnover') {
                return `On receipt of ${
                    issueDate.year() - 1
                }-${issueDate.year()} financial statement`
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
                return this.invoicablePeriods[index]
                    ? this.invoicablePeriods[index].label
                    : ''
            }
        },
        getInvoicingPeriod(startDate, endDate) {
            for (let i = 0; i < this.invoicablePeriods.length; i++) {
                const invoicablePeriod = this.invoicablePeriods[i]
                if (
                    startDate.isBetween(invoicablePeriod) &&
                    endDate.isSame(invoicablePeriod.endDate)
                ) {
                    return invoicablePeriod
                }
            }
            return
        },
        getEndOfNextFinancialYear(startDate) {
            const endOfFinancialYear = moment(startDate)
                .set('date', 30)
                .set('month', 5)
            return startDate.isBefore(endOfFinancialYear)
                ? endOfFinancialYear
                : endOfFinancialYear.add(1, 'years')
        },
    },
}
</script>

<style scoped></style>
