<template>
    <div class="row mb-4">
        <div class="col">
            <template v-for="item in years_array" :key="item.key">
                <div class="card mb-3">
                    <div class="card-body">
                        <div class="row mb-2 row_wrapper align-items-center">
                            <label class="col-sm-2 col-form-label"
                                >Increment
                                <span v-if="debug" class="debug_msg"
                                    >id:{{ item.id }}</span
                                ></label
                            >
                            <label class="col-sm-1 col-form-label">year</label>
                            <div class="col-sm-2 align-items-center">
                                <input
                                    v-model="item.year"
                                    type="number"
                                    :min="min_year"
                                    :max="max_year"
                                    :step="step_year"
                                    class="form-control form-control-sm"
                                    :disabled="item.readonly"
                                />
                            </div>
                            <label class="col-sm-3 col-form-label">{{
                                value_title
                            }}</label>
                            <div class="col-sm-2">
                                <input
                                    v-if="
                                        increment_type ===
                                        'annual_increment_amount'
                                    "
                                    v-model="item.increment_amount"
                                    type="number"
                                    :min="min_increment"
                                    :max="max_increment"
                                    :step="step_increment"
                                    class="form-control form-control-sm"
                                    :disabled="item.readonly"
                                />
                                <input
                                    v-else-if="
                                        increment_type ===
                                        'annual_increment_percentage'
                                    "
                                    v-model="item.increment_percentage"
                                    type="number"
                                    :min="min_increment"
                                    :max="max_increment"
                                    :step="step_increment"
                                    class="form-control form-control-sm"
                                    :disabled="item.readonly"
                                />
                                <input
                                    v-else-if="
                                        increment_type ===
                                        'gross_turnover_percentage'
                                    "
                                    v-model="item.percentage"
                                    type="number"
                                    :min="min_increment"
                                    :max="max_increment"
                                    :step="step_increment"
                                    class="form-control form-control-sm"
                                    :disabled="item.readonly"
                                />
                            </div>
                            <div class="col-sm-1">
                                <template v-if="deletable(item)">
                                    <span
                                        class="remove_a_row text-danger"
                                        @click="remove_a_row(item, $event)"
                                        ><i class="bi bi-x-circle-fill"></i
                                    ></span>
                                </template>
                            </div>
                        </div>
                    </div>
                </div>
            </template>
            <button class="btn btn-primary" @click="addAnotherYearClicked">
                <i class="fa fa-add"></i> Add increment year
            </button>
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
            default: 2021,
        },
        maxYear: {
            type: Number,
            default: 2100,
        },
        stepYear: {
            type: Number,
            default: 1,
        },
    },
    computed: {
        debug: function () {
            if (this.$route.query.debug) {
                return this.$route.query.debug === 'true'
            }
            return false
        },
        value_title: function () {
            if (this.increment_type === 'annual_increment_amount')
                return 'amount [AU$]'
            else if (
                [
                    'annual_increment_percentage',
                    'gross_turnover_percentage',
                ].includes(this.increment_type)
            )
                return 'percentage [%]'
            return 'Error: Unkown increment type'
        },
        step_increment: function () {
            if (this.increment_type === 'annual_increment_amount') return 100
            else if (
                [
                    'annual_increment_percentage',
                    'gross_turnover_percentage',
                ].includes(this.increment_type)
            )
                return 0.1
            return 'Error: Unkown increment type'
        },
    },
    created: function () {},
    mounted: function () {},
    methods: {
        deletable: function (item) {
            if (item.id === 0 || !item.readonly)
                // If the date is a newly added one, or not readonly, it is deletable.
                return true
            return false
        },
        addAnotherYearClicked: function (e) {
            e.preventDefault()

            let key_name = ''
            if (this.increment_type === 'annual_increment_amount')
                key_name = 'increment_amount'
            else if (this.increment_type === 'annual_increment_percentage')
                key_name = 'increment_percentage'
            else if (this.increment_type === 'gross_turnover_percentage')
                key_name = 'percentage'

            this.years_array.push({
                id: 0,
                key: uuid(),
                year: null,
                [key_name]: null,
                readonly: false,
            })
        },
        remove_a_row: function (item, e) {
            let vm = this
            let $elem = $(e.target)

            // Fade out a row
            $elem.closest('.row_wrapper').fadeOut(500, function () {
                if (item.id === 0) {
                    // When a row is newly added one (not stored in the database yet), just remove it from the array
                    const index = vm.years_array.indexOf(item)
                    if (index > -1) {
                        vm.years_array.splice(index, 1)
                    }
                } else {
                    // When a row is the one already stored in the database, flag it to be deleted.
                    item.to_be_deleted = true
                }
            })
        },
    },
}
</script>

<style scoped>
.remove_a_row {
    cursor: pointer;
}

.debug_msg {
    font-size: 0.6em;
    color: darkgray;
}
</style>
