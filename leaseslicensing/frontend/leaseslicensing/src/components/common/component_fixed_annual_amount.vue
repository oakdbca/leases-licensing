<template>
    <div class="row mb-3 border-bottom">
        <div class="col">
            <button
                class="btn btn-primary btn-sm mb-3"
                @click.prevent="addAnotherYearClicked"
            >
                <i class="fa fa-add"></i> Add Increment Year
            </button>
            <template v-for="item in yearsArrayComputed" :key="item.key">
                <div class="card mb-2">
                    <div class="card-body py-1">
                        <div class="div d-flex align-items-center">
                            <label class="col-sm-4 col-form-label"
                                >Increment
                                <span class="float-end pe-3">Year</span>
                            </label>
                            <div class="align-items-center pe-3">
                                <input
                                    v-model="item.year"
                                    type="number"
                                    :min="minYear"
                                    :max="maxYear"
                                    :step="stepYear"
                                    class="form-control form-control-sm"
                                    :disabled="item.readonly"
                                    required
                                />
                            </div>
                            <label class="col-form-label pe-3">{{
                                valueTitle
                            }}</label>
                            <div class="pe-3">
                                <input
                                    v-if="
                                        incrementType ===
                                        'annual_increment_amount'
                                    "
                                    v-model="item.increment_amount"
                                    type="number"
                                    :min="1"
                                    :max="100000000"
                                    :step="100"
                                    class="form-control form-control-sm"
                                    :disabled="item.readonly"
                                    required
                                />
                                <input
                                    v-else-if="
                                        incrementType ===
                                        'annual_increment_percentage'
                                    "
                                    v-model="item.increment_percentage"
                                    type="number"
                                    :min="0.1"
                                    :max="100"
                                    :step="0.1"
                                    class="form-control form-control-sm"
                                    :disabled="item.readonly"
                                    required
                                />
                                <input
                                    v-else-if="
                                        incrementType ===
                                        'gross_turnover_percentage'
                                    "
                                    v-model="item.percentage"
                                    type="number"
                                    :min="0.1"
                                    :max="100"
                                    :step="0.1"
                                    class="form-control form-control-sm"
                                    :disabled="item.readonly"
                                    required
                                />
                            </div>
                            <div class="">
                                <template v-if="deletable(item)">
                                    <span
                                        class="text-danger"
                                        role="button"
                                        @click="removeARow(item, $event)"
                                        ><i class="bi bi-x-circle-fill"></i
                                    ></span>
                                </template>
                            </div>
                        </div>
                    </div>
                </div>
            </template>
        </div>
    </div>
</template>

<script>
import { v4 as uuid } from 'uuid'

export default {
    name: 'AnnualAmount',
    props: {
        incrementType: {
            type: String,
            required: true,
        },
        yearsArray: {
            type: Array,
            required: true,
        },
        minYear: {
            type: Number,
            default: () => {
                return new Date().getFullYear()
            },
        },
        maxYear: {
            type: Number,
            default: 2100,
        },
        stepYear: {
            type: Number,
            default: 1,
        },
        minIncrement: {
            type: Number,
            default: 1,
        },
    },
    emits: ['updateYearsArray'],
    computed: {
        debug: function () {
            if (this.$route.query.debug) {
                return this.$route.query.debug === 'true'
            }
            return false
        },
        yearsArrayComputed: {
            get() {
                return this.yearsArray
            },
            set(value) {
                console.log('emitting updateYearsArray')
                this.$emit('updateYearsArray', value)
            },
        },
        valueTitle: function () {
            if (this.incrementType === 'annual_increment_amount')
                return 'amount ($AUD)'
            else if (
                [
                    'annual_increment_percentage',
                    'gross_turnover_percentage',
                ].includes(this.incrementType)
            )
                return 'percentage (%)'
            return 'Error: Unkown increment type'
        },
        stepIncrement: function () {
            if (this.incrementType === 'annual_increment_amount') return 100
            else if (
                [
                    'annual_increment_percentage',
                    'gross_turnover_percentage',
                ].includes(this.incrementType)
            )
                return 0.1
            return 'Error: Unkown increment type'
        },
    },
    methods: {
        deletable: function (item) {
            if (item.id === 0 || !item.readonly)
                // If the date is a newly added one, or not readonly, it is deletable.
                return true
            return false
        },
        addAnotherYearClicked: function () {
            let key_name = ''
            if (this.incrementType === 'annual_increment_amount')
                key_name = 'increment_amount'
            else if (this.incrementType === 'annual_increment_percentage')
                key_name = 'increment_percentage'
            else if (this.incrementType === 'gross_turnover_percentage')
                key_name = 'percentage'
            let year = new Date().getFullYear()
            if (this.yearsArrayComputed.length > 0) {
                year =
                    this.yearsArrayComputed[this.yearsArrayComputed.length - 1]
                        .year + 1
            }
            this.yearsArrayComputed.push({
                id: 0,
                key: uuid(),
                year: year,
                [key_name]: null,
                readonly: false,
            })
        },
        removeARow: function (item, e) {
            let vm = this
            let $elem = $(e.target)

            // Fade out a row
            $elem.closest('.card').remove()
            if (item.id === 0) {
                // When a row is newly added one (not stored in the database yet), just remove it from the array
                console.log('removing a row')
                console.log(
                    vm.yearsArrayComputed.filter((i) => i.key !== item.key)
                )
                vm.yearsArrayComputed = vm.yearsArrayComputed.filter(
                    (i) => i.key !== item.key
                )
            } else {
                // When a row is the one already stored in the database, flag it to be deleted.
                item.to_be_deleted = true
            }
        },
    },
}
</script>
