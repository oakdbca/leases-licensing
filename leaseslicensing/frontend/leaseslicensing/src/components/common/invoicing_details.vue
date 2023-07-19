<template>
    <form id="invoicing-form" novalidate class="needs-validation">
        <div class="row mb-4">
            <label class="col-form-label col-sm-4"
                >Lease or Licence Charge Method</label
            >
            <div class="col-sm-8">
                <ul class="list-group">
                    <li
                        v-for="(charge_method, index) in charge_methods"
                        :key="charge_method.key"
                        class="list-group-item"
                    >
                        <input
                            v-if="invoicingDetailsComputed"
                            :id="charge_method.key"
                            v-model="invoicingDetailsComputed.charge_method"
                            type="radio"
                            class="form-check-input me-2"
                            name="charge_method"
                            :value="charge_method.id"
                            :disabled="chargeMethodDisabled(charge_method)"
                            required
                            @change="focusNextInput"
                        />
                        <label
                            :for="charge_method.key"
                            class="form-check-label"
                            >{{ charge_method.display_name }}</label
                        >
                        <div
                            v-if="index == charge_methods.length - 1"
                            class="invalid-tooltip mt-2 invalid-charge-method"
                        >
                            You must select a charge method.
                        </div>
                    </li>
                </ul>
            </div>
        </div>
        <div v-if="show_once_off_charge_amount" class="row mb-3">
            <div class="col-sm-4">
                <label for="once_off_charge_amount" class="control-label"
                    >Once-off Charge ($AUD)</label
                >
            </div>
            <div class="col-sm-8">
                <input
                    v-if="invoicingDetailsComputed"
                    id="once_off_charge_amount"
                    v-model="invoicingDetailsComputed.once_off_charge_amount"
                    type="number"
                    min="1"
                    class="form-control"
                    required
                />
            </div>
        </div>
        <div v-if="show_base_fee" class="row mb-3 pb-3 border-bottom">
            <label for="base_fee_amount" class="col-form-label col-sm-4"
                >Base Fee ($AUD)</label
            >
            <div class="col-sm-8">
                <input
                    v-if="invoicingDetailsComputed"
                    id="base_fee_amount"
                    v-model="invoicingDetailsComputed.base_fee_amount"
                    type="number"
                    min="1"
                    class="form-control"
                    required
                />
            </div>
        </div>
        <div v-if="show_review_of_base_fee" class="row mb-3 pb-3 border-bottom">
            <label class="col-form-label col-sm-4">Review of Base Fee</label>
            <div class="col-sm-8">
                <div class="d-flex align-items-center">
                    <div class="pe-3">Once every</div>
                    <div class="pe-3">
                        <input
                            v-if="invoicingDetailsComputed"
                            id="review_once_every"
                            v-model="invoicingDetailsComputed.review_once_every"
                            type="number"
                            min="1"
                            max="5"
                            step="1"
                            class="form-control"
                            :readonly="
                                [2, 3].includes(
                                    invoicingDetailsComputed.review_repetition_type
                                )
                            "
                            required
                        />
                    </div>
                    <div class="">
                        <select
                            v-model="
                                invoicingDetailsComputed.review_repetition_type
                            "
                            class="form-select"
                            aria-label="Repetition Type"
                            required
                        >
                            <option
                                v-for="repetition_type in repetition_types"
                                :key="repetition_type.key"
                                :value="repetition_type.id"
                            >
                                {{ repetition_type.display_name }}
                            </option>
                        </select>
                    </div>
                </div>
            </div>
        </div>
        <div v-if="show_custom_cpi_years" class="row mb-3 pb-3 border-bottom">
            <template v-for="year in financialYearsIncluded" :key="year">
                <div class="row my-2">
                    <div class="div d-flex align-items-center">
                        <div class="col-sm-4 pe-3">
                            <div class="input-group">
                                <span class="input-group-text"
                                    >Financial Year</span
                                >
                                <input
                                    type="text"
                                    readonly
                                    class="form-control form-control-year"
                                    :value="year"
                                />
                            </div>
                        </div>
                        <div class="pe-3">Label</div>
                        <div class="col-sm-4 pe-3">
                            <div class="input-group">
                                <input type="text" class="form-control" />
                            </div>
                        </div>
                        <label class="col-sm-3">
                            <div class="input-group">
                                <span class="input-group-text">CPI</span>
                                <input
                                    step="0.1"
                                    min="0.1"
                                    max="100"
                                    type="number"
                                    class="form-control"
                                />
                                <span class="input-group-text">%</span>
                            </div>
                        </label>
                    </div>
                </div>
            </template>
        </div>
        <div v-if="show_cpi_method">
            <div class="row mb-3">
                <div class="col-sm-4 col-form-label">
                    CPI Calculation Method
                </div>
                <div class="col-sm-8">
                    <select
                        v-model="
                            invoicingDetailsComputed.cpi_calculation_method
                        "
                        class="form-select"
                        aria-label="CPI Calculation Method"
                        required
                    >
                        <option
                            v-for="cpi_calculation_method in cpi_calculation_methods"
                            :key="cpi_calculation_method.id"
                            :value="cpi_calculation_method.id"
                        >
                            {{ cpi_calculation_method.display_name }}
                        </option>
                    </select>
                </div>
            </div>
            <div class="row mb-3 border-bottom">
                <div class="col">
                    <BootstrapAlert class="py-2">
                        The appropriate CPI percentage from the ABS API when the
                        invoice is generated.
                    </BootstrapAlert>
                </div>
            </div>
        </div>
        <div
            v-if="show_invoicing_frequency"
            class="row mb-3 pb-3 border-bottom"
        >
            <label for="invoicing_frequency" class="col-form-label col-sm-4"
                >Invoicing Frequency</label
            >
            <div class="col-sm-8">
                <div class="d-flex align-items-center">
                    <div class="pe-3">Once every</div>
                    <div class="pe-3">
                        <input
                            v-if="invoicingDetailsComputed"
                            id="invoicing_once_every"
                            v-model="
                                invoicingDetailsComputed.invoicing_once_every
                            "
                            type="number"
                            min="1"
                            max="5"
                            step="1"
                            class="form-control"
                            :readonly="
                                [2, 3].includes(
                                    invoicingDetailsComputed.invoicing_repetition_type
                                )
                            "
                            required
                        />
                    </div>
                    <div class="">
                        <select
                            v-model="
                                invoicingDetailsComputed.invoicing_repetition_type
                            "
                            class="form-select"
                            aria-label="Repetition Type"
                            required
                        >
                            <option
                                v-for="repetition_type in repetition_types"
                                :key="repetition_type.key"
                                :value="repetition_type.id"
                            >
                                {{ repetition_type.display_name }}
                            </option>
                        </select>
                    </div>
                </div>
            </div>
        </div>
        <div v-if="show_fixed_annual_increment">
            <AnnualIncrement
                v-if="invoicingDetailsComputed"
                increment-type="annual_increment_amount"
                :years-array="invoicingDetailsComputed.annual_increment_amounts"
                :approval-duration-years="approvalDurationYears"
                @updateYearsArray="updateYearsArray"
            />
        </div>
        <div v-if="show_fixed_annual_percentage">
            <AnnualIncrement
                v-if="invoicingDetailsComputed"
                increment-type="annual_increment_percentage"
                :years-array="
                    invoicingDetailsComputed.annual_increment_percentages
                "
                :approval-duration-years="approvalDurationYears"
                @updateYearsArray="updateYearsArray"
            />
        </div>
        <div v-if="show_percentage_of_gross_turnover">
            <PercentageTurnover
                v-if="invoicingDetailsComputed"
                :start-date="startDate"
                :expiry-date="expiryDate"
            />
        </div>
        <div v-if="show_crown_land_rent_review_date">
            <CrownLandRentReviewDate
                v-if="invoicingDetailsComputed"
                :review-dates="
                    invoicingDetailsComputed.crown_land_rent_review_dates
                "
                @updateReviewDates="updateReviewDates"
            />
        </div>
    </form>
</template>

<script>
import AnnualIncrement from '@/components/common/component_fixed_annual_amount.vue'
import PercentageTurnover from '@/components/common/component_percentage_turnover.vue'
import CrownLandRentReviewDate from '@/components/common/component_crown_land_rent_review_date.vue'

import { api_endpoints, helpers } from '@/utils/hooks'

export default {
    name: 'InvoicingDetails',
    components: {
        AnnualIncrement,
        PercentageTurnover,
        CrownLandRentReviewDate,
    },
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
    },
    emits: ['updateInvoicingDetails'],
    data: function () {
        return {
            approvalDurationYears: helpers.yearsInDateRange(
                this.startDate,
                this.expiryDate
            ),
            financialYearsIncluded: helpers.financialYearsIncluded(
                this.startDate,
                this.expiryDate
            ),
            charge_methods: [],
            repetition_types: [],
            cpi_calculation_methods: [],
        }
    },
    computed: {
        debug: function () {
            if (this.$route.query.debug) {
                return this.$route.query.debug === 'true'
            }
            return false
        },
        invoicingDetailsComputed: {
            get() {
                return this.invoicingDetails
            },
            set(value) {
                console.log('emitting updateInvoicingDetails = ', value)
                this.$emit('updateInvoicingDetails', value)
            },
        },
        show_once_off_charge_amount: function () {
            if (this.invoicingDetails && this.invoicingDetails.charge_method)
                if (
                    this.invoicingDetails.charge_method ===
                    this.getChargeMethodIdByKey('once_off_charge')
                )
                    return true
            return false
        },
        show_fixed_annual_increment: function () {
            if (this.invoicingDetails && this.invoicingDetails.charge_method)
                if (
                    this.invoicingDetails.charge_method ===
                    this.getChargeMethodIdByKey(
                        'base_fee_plus_fixed_annual_increment'
                    )
                )
                    return true
            return false
        },
        show_fixed_annual_percentage: function () {
            if (this.invoicingDetails && this.invoicingDetails.charge_method)
                if (
                    this.invoicingDetails.charge_method ===
                    this.getChargeMethodIdByKey(
                        'base_fee_plus_fixed_annual_percentage'
                    )
                )
                    return true
            return false
        },
        show_base_fee: function () {
            if (
                this.show_fixed_annual_increment ||
                this.show_fixed_annual_percentage ||
                (this.invoicingDetails &&
                    this.invoicingDetails.charge_method &&
                    this.invoicingDetails.charge_method ===
                        this.getChargeMethodIdByKey(
                            'base_fee_plus_annual_cpi'
                        )) ||
                (this.invoicingDetails.charge_method &&
                    this.invoicingDetails.charge_method ===
                        this.getChargeMethodIdByKey(
                            'base_fee_plus_annual_cpi_custom'
                        ))
            )
                return true
            return false
        },
        show_review_of_base_fee: function () {
            return this.show_base_fee
        },
        show_cpi_method: function () {
            if (this.invoicingDetails && this.invoicingDetails.charge_method)
                if (
                    this.invoicingDetails.charge_method ===
                    this.getChargeMethodIdByKey('base_fee_plus_annual_cpi')
                )
                    return true
            return false
        },
        show_custom_cpi_years: function () {
            if (this.invoicingDetails && this.invoicingDetails.charge_method)
                if (
                    this.invoicingDetails.charge_method ===
                    this.getChargeMethodIdByKey(
                        'base_fee_plus_annual_cpi_custom'
                    )
                )
                    return true
            return false
        },
        show_percentage_of_gross_turnover: function () {
            if (this.invoicingDetails && this.invoicingDetails.charge_method)
                if (
                    this.invoicingDetails.charge_method ===
                    this.getChargeMethodIdByKey('percentage_of_gross_turnover')
                )
                    return true
            return false
        },
        show_crown_land_rent_review_date: function () {
            return this.show_base_fee
        },
        show_invoicing_frequency: function () {
            if (this.invoicingDetails) {
                if (
                    [
                        this.getChargeMethodIdByKey(
                            'base_fee_plus_fixed_annual_increment'
                        ),
                        this.getChargeMethodIdByKey(
                            'base_fee_plus_fixed_annual_percentage'
                        ),
                        this.getChargeMethodIdByKey('base_fee_plus_annual_cpi'),
                        this.getChargeMethodIdByKey(
                            'base_fee_plus_annual_cpi_custom'
                        ),
                        this.getChargeMethodIdByKey(
                            'percentage_of_gross_turnover'
                        ),
                    ].includes(this.invoicingDetails.charge_method)
                )
                    return true
                return false
            }
            return false
        },
    },
    created: function () {
        this.fetchChargeMethods()
        this.fetchRepetitionTypes()
        this.fetchCPICalculationMethods()
    },
    mounted: function () {},
    methods: {
        focusNextInput: function (event) {
            this.$nextTick(() => {
                $(event.target)
                    .closest('.row')
                    .next('.row')
                    .find('input')
                    .focus()
            })
        },
        updateReviewDates: function (review_dates) {
            this.invoicingDetailsComputed = {
                ...this.invoicingDetailsComputed,
                crown_land_rent_review_dates: review_dates,
            }
        },
        updateYearsArray: function (incrementType, years_array) {
            console.log('updateYearsArray = ', years_array)
            if ('annual_increment_amount' == incrementType) {
                this.invoicingDetailsComputed = {
                    ...this.invoicingDetailsComputed,
                    annual_increment_amounts: years_array,
                }
            } else {
                this.invoicingDetailsComputed = {
                    ...this.invoicingDetailsComputed,
                    annual_increment_percentages: years_array,
                }
            }
        },
        chargeMethodDisabled: function (charge_method) {
            return (
                [
                    'base_fee_plus_fixed_annual_increment',
                    'base_fee_plus_fixed_annual_percentage',
                ].includes(charge_method.key) && this.approvalDurationYears == 0
            )
        },
        getChargeMethodIdByKey: function (key) {
            let charge_method = this.charge_methods.find(
                (charge_method) => charge_method.key === key
            )
            if (charge_method) return charge_method.id
            else return 0
        },
        fetchChargeMethods: async function () {
            let vm = this
            try {
                const res = await fetch(api_endpoints.charge_methods)
                if (!res.ok) throw new Error(res.statusText) // 400s or 500s error
                let charge_methods = await res.json()
                vm.charge_methods = charge_methods
            } catch (err) {
                console.log({ err })
            }
        },
        fetchRepetitionTypes: async function () {
            let vm = this
            try {
                const res = await fetch(api_endpoints.repetition_types)
                if (!res.ok) throw new Error(res.statusText) // 400s or 500s error
                let repetition_types = await res.json()
                vm.repetition_types = repetition_types
                vm.$nextTick(function () {
                    if (!vm.invoicingDetailsComputed.review_once_every) {
                        vm.invoicingDetailsComputed.review_once_every = 1
                    }
                    if (!vm.invoicingDetailsComputed.invoicing_once_every) {
                        vm.invoicingDetailsComputed.invoicing_once_every = 1
                    }
                    if (!vm.invoicingDetailsComputed.review_repetition_type) {
                        vm.invoicingDetailsComputed.review_repetition_type = 1
                    }
                    if (
                        !vm.invoicingDetailsComputed.invoicing_repetition_type
                    ) {
                        vm.invoicingDetailsComputed.invoicing_repetition_type = 1
                    }
                })
            } catch (err) {
                console.log({ err })
            }
        },
        fetchCPICalculationMethods: async function () {
            let vm = this
            try {
                const res = await fetch(
                    api_endpoints.cpi_calculation_methods + 'no-pagination/'
                )
                if (!res.ok) throw new Error(res.statusText) // 400s or 500s error
                let cpi_calculation_methods = await res.json()
                vm.cpi_calculation_methods = cpi_calculation_methods
                if (
                    vm.invoicingDetailsComputed.cpi_calculation_method == null
                ) {
                    alert('testing')
                    vm.invoicingDetailsComputed.cpi_calculation_method =
                        cpi_calculation_methods[0].id
                }
            } catch (err) {
                console.log({ err })
            }
        },
    },
}
</script>
<style scoped>
.invalid-charge-method {
    margin-left: -17px;
}
</style>
