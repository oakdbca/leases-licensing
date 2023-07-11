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
        <div v-if="show_fixed_annual_increment">
            <AnnualIncrement
                v-if="invoicingDetailsComputed"
                increment-type="annual_increment_amount"
                :years-array="invoicingDetailsComputed.annual_increment_amounts"
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
                @updateYearsArray="updateYearsArray"
            />
        </div>
        <div v-if="show_percentage_of_gross_turnover">
            <AnnualIncrement
                v-if="invoicingDetailsComputed"
                increment-type="gross_turnover_percentage"
                :years-array="
                    invoicingDetailsComputed.gross_turnover_percentages
                "
                @updateYearsArray="updateYearsArray"
            />
            <div class="row mb-2">
                <div class="col-sm-12">
                    <BootstrapAlert>
                        The approval holder will be asked to upload their
                        audited financial statement once a year.
                    </BootstrapAlert>
                </div>
            </div>
        </div>
        <div v-if="show_review_of_base_fee" class="row mb-3 pb-3 border-bottom">
            <label class="col-form-label col-sm-4">Review of Base Fee</label>
            <div class="col-sm-8">
                <div class="d-flex align-items-center">
                    <div class="pe-3">
                        <input
                            v-if="invoicingDetailsComputed"
                            id="review_once_every"
                            v-model="invoicingDetailsComputed.review_once_every"
                            type="number"
                            min="0"
                            max="5"
                            step="1"
                            class="form-control"
                            required
                        />
                    </div>
                    <div class="pe-3">
                        time<span
                            v-if="
                                invoicingDetailsComputed.review_once_every > 1
                            "
                            >s</span
                        >
                        per
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
                            <option disabled :value="null">
                                Select a Frequency
                            </option>
                            <option
                                v-for="repetition_type in repetition_types"
                                :key="repetition_type.id"
                                :value="repetition_type.id"
                            >
                                {{ repetition_type.display_name }}
                            </option>
                        </select>
                    </div>
                </div>
            </div>
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
        <div v-if="show_invoicing_frequency" class="row mb-2">
            <label for="invoicing_frequency" class="col-form-label col-sm-4"
                >Invoicing Frequency</label
            >
            <div class="col-sm-8">
                <div class="d-flex align-items-center">
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
                            required
                        />
                    </div>
                    <div class="pe-3">
                        time<span
                            v-if="
                                invoicingDetailsComputed.invoicing_once_every >
                                1
                            "
                            >s</span
                        >
                        per
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
                            <option selected disabled :value="null">
                                Select a Frequency
                            </option>
                            <option
                                v-for="repetition_type in repetition_types"
                                :key="repetition_type.id"
                                :value="repetition_type.id"
                            >
                                {{ repetition_type.display_name }}
                            </option>
                        </select>
                    </div>
                </div>
            </div>
        </div>
    </form>
</template>

<script>
import AnnualIncrement from '@/components/common/component_fixed_annual_amount.vue'
import CrownLandRentReviewDate from '@/components/common/component_crown_land_rent_review_date.vue'

export default {
    name: 'InvoicingDetails',
    components: {
        AnnualIncrement,
        CrownLandRentReviewDate,
    },
    props: {
        invoicingDetails: {
            type: Object,
            default() {
                return {}
            },
        },
    },
    emits: ['updateInvoicingDetails'],
    data: function () {
        return {
            charge_methods: [], // For radio button options
            repetition_types: [], // For radio button options
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
                        this.getChargeMethodIdByKey('base_fee_plus_annual_cpi'))
            )
                return true
            return false
        },
        show_review_of_base_fee: function () {
            return this.show_base_fee
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
        updateYearsArray: function (years_array) {
            this.invoicingDetailsComputed = {
                ...this.invoicingDetailsComputed,
                annual_increment_amounts: years_array,
            }
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
                const res = await fetch('/api/charge_methods')
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
                const res = await fetch('/api/repetition_types')
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
    },
}
</script>
<style scoped>
.invalid-charge-method {
    margin-left: -17px;
}
</style>
