<template>
    <div class="row mb-4">
        <div class="col-sm-3">
            <label for="" class="control-label">Rent or licence charge method</label>
        </div>
        <div class="col-sm-9">
            <div v-for="charge_method in charge_methods" class="form-check" :id="charge_method.id">
                <input
                    v-if="invoicing_details"
                    type="radio" 
                    class="form-check-input"
                    name="charge_method"
                    :id="charge_method.key" 
                    :value="charge_method.id" 
                    v-model="invoicing_details.charge_method"
                />
                <label :for="charge_method.key" class="form-check-label">{{ charge_method.display_name }}</label>
            </div>
        </div>
    </div>
    <div v-show="show_once_off_charge_amount" class="row mb-2">
        <div class="col-sm-3">
            <label for="once_off_charge_amount" class="control-label">Once-off charge [AU$]</label>
        </div>
        <div class="col-sm-2">
            <input v-if="invoicing_details" type="number" min="0" step="100" id="once_off_charge_amount" class="form-control" v-model="invoicing_details.once_off_charge_amount">
        </div>
    </div>
    <div v-show="show_base_fee" class="row mb-4">
        <div class="col-sm-3">
            <label for="base_fee_amount" class="control-label">Base fee [AU$]</label>
        </div>
        <div class="col-sm-2">
            <input v-if="invoicing_details" type="number" min="0" step="100" id="base_fee_amount" class="form-control" v-model="invoicing_details.base_fee_amount">
        </div>
    </div>
    <div v-show="show_fixed_annual_increment">
        <AnnualIncrement
            v-if="invoicing_details"
            increment_type="annual_increment_amount"
            :years_array="invoicing_details.annual_increment_amounts"
        />
    </div>
    <div v-show="show_fixed_annual_percentage">
        <AnnualIncrement
            v-if="invoicing_details"
            increment_type="annual_increment_percentage"
            :years_array="invoicing_details.annual_increment_percentages"
        />
    </div>
    <div v-show="show_percentage_of_gross_turnover">
        <AnnualIncrement
            v-if="invoicing_details"
            increment_type="gross_turnover_percentage"
            :years_array="invoicing_details.gross_turnover_percentages"
        />
        <div class="row mb-2">
            <div class="col-sm-12">
                Approval holder will be asked to upload their audited financial statement once a year.
            </div>
        </div>
    </div>
    <div v-show="show_review_of_base_fee" class="row mb-2">
        <div class="col-sm-3">
            <label class="control-label">Review of base fee</label>
        </div>
        <div class="col-sm-2">
            <label for="review_once_every" class="control-label">Once every</label>
        </div>
        <div class="col-sm-2">
            <input v-if="invoicing_details" type="number" min="0" max="5" step="1" id="review_once_every" class="form-control" v-model="invoicing_details.review_once_every">
        </div>
        <div class="col-sm-2">
            <div v-for="repetition_type in repetition_types" class="form-check" :id="repetition_type.id">
                <input
                    v-if="invoicing_details"
                    type="radio" 
                    name="repetition_type_review"
                    class="form-check-input"
                    :id="'review_' + repetition_type.key" 
                    :value="repetition_type.id" 
                    v-model="invoicing_details.review_repetition_type"
                />
                <label :for="'review_' + repetition_type.key" class="form-check-label">{{ repetition_type.display_name }}</label>
            </div>
        </div>
    </div>
    <div v-show="show_crown_land_rent_review_date">
        <CrownLandRentReviewDate
            v-if="invoicing_details"
            :review_dates="invoicing_details.crown_land_rent_review_dates" 
        />
    </div>
    <div v-show="show_invoicing_frequency" class="row mb-2">
        <div class="col-sm-3">
            <label for="invoicing_frequency" class="control-label">Invoicing Frequency</label>
        </div>
        <div class="col-sm-2">
            <label for="invoicing_once_every" class="control-label">Once every</label>
        </div>
        <div class="col-sm-2">
            <input v-if="invoicing_details" type="number" min="0" max="5" step="1" id="invoicing_once_every" class="form-control" v-model="invoicing_details.invoicing_once_every">
        </div>
        <div class="col-sm-2">
            <div v-for="repetition_type in repetition_types" class="form-check" :id="repetition_type.id">
                <input
                    v-if="invoicing_details"
                    type="radio" 
                    name="repetition_type_invoicing"
                    class="form-check-input"
                    :id="'invoicing_' + repetition_type.key" 
                    :value="repetition_type.id" 
                    v-model="invoicing_details.invoicing_repetition_type"
                />
                <label :for="'invoicing_' + repetition_type.key" class="form-check-label">{{ repetition_type.display_name }}</label>
            </div>
        </div>
    </div>
</template>

<script>
import { none } from 'ol/centerconstraint';
import { v4 as uuid } from 'uuid'
import AnnualIncrement from '@/components/common/component_fixed_annual_amount.vue'
import CrownLandRentReviewDate from '@/components/common/component_crown_land_rent_review_date.vue'

export default {
    name: 'InvoicingDetails',
    props: {
        invoicing_details: {
            type: Object,
            default(rawProps){
                return {}
            }
        }
    },
    data: function() {
        let vm = this;
        return {
            charge_methods: [],  // For radio button options
            repetition_types: [],  // For radio button options
        }
    },
    components: {
        AnnualIncrement,
        CrownLandRentReviewDate,
    },
    created: function(){
        this.fetchChargeMethods()
        this.fetchRepetitionTypes()
    },
    mounted: function(){

    },
    computed: {
        debug: function(){
            if (this.$route.query.debug){
                return this.$route.query.debug === 'true'
            }
            return false
        },
        show_once_off_charge_amount: function(){
            if (this.invoicing_details && this.invoicing_details.charge_method)
                if (this.invoicing_details.charge_method === this.getChargeMethodIdByKey('once_off_charge'))
                    return true
            return false
        },
        show_fixed_annual_increment: function(){
            if (this.invoicing_details && this.invoicing_details.charge_method)
                if (this.invoicing_details.charge_method === this.getChargeMethodIdByKey('base_fee_plus_fixed_annual_increment'))
                    return true
            return false
        },
        show_fixed_annual_percentage: function(){
            if (this.invoicing_details && this.invoicing_details.charge_method)
                if (this.invoicing_details.charge_method === this.getChargeMethodIdByKey('base_fee_plus_fixed_annual_percentage'))
                    return true
            return false
        },
        show_base_fee: function(){
            if (this.show_fixed_annual_increment || this.show_fixed_annual_percentage || (
                this.invoicing_details && this.invoicing_details.charge_method && this.invoicing_details.charge_method === this.getChargeMethodIdByKey('base_fee_plus_annual_cpi'
            )))
                return true
            return false
        },
        show_review_of_base_fee: function(){
            return this.show_base_fee
        },
        show_percentage_of_gross_turnover: function(){
            if (this.invoicing_details && this.invoicing_details.charge_method)
                if (this.invoicing_details.charge_method === this.getChargeMethodIdByKey('percentage_of_gross_turnover'))
                    return true
            return false
        },
        show_crown_land_rent_review_date: function(){
            return this.show_base_fee
        },
        show_invoicing_frequency: function(){
            if (this.invoicing_details){
                if ([
                    this.getChargeMethodIdByKey('base_fee_plus_fixed_annual_increment'),
                    this.getChargeMethodIdByKey('base_fee_plus_fixed_annual_percentage'),
                    this.getChargeMethodIdByKey('base_fee_plus_annual_cpi'),
                    this.getChargeMethodIdByKey('percentage_of_gross_turnover')].includes(this.invoicing_details.charge_method))
                    return true
                return false
            }
        },
    },
    methods: {
        getChargeMethodIdByKey: function(key){
            let charge_method = this.charge_methods.find(charge_method => charge_method.key === key)
            if (charge_method)
                return charge_method.id
            else
                return 0
        },
        fetchChargeMethods: async function(){
            let vm = this
            try {
                const res = await fetch('/api/charge_methods')
                if (!res.ok)
                    throw new Error(res.statusText)  // 400s or 500s error
                let charge_methods = await res.json()
                vm.charge_methods = charge_methods
            } catch(err){
                console.log({err})
            } finally {

            }
        },
        fetchRepetitionTypes: async function(){
            let vm = this
            try {
                const res = await fetch('/api/repetition_types')
                if (!res.ok)
                    throw new Error(res.statusText)  // 400s or 500s error
                let repetition_types = await res.json()
                vm.repetition_types= repetition_types
            } catch(err){
                console.log({err})
            } finally {

            }
        }
    },
}
</script>