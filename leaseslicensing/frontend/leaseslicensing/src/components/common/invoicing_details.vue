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
                            :disabled="
                                context == 'Approval' &&
                                charge_method.id !=
                                    invoicingDetailsComputed.charge_method
                            "
                            @change="onChargeMethodChange"
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
                    :readonly="context != 'Proposal'"
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
                    min="0"
                    step="1"
                    class="form-control"
                    required
                    @keyup="updatePreviewInvoices"
                />
            </div>
        </div>
        <div v-if="show_review_of_base_fee" class="row mb-3 pb-3 border-bottom">
            <label class="col-form-label col-sm-4"
                >Crown Land Rent Review</label
            >
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
                            max="20"
                            step="1"
                            class="form-control"
                            :readonly="crown_land_rent_review_readonly"
                            required
                            @change="saveInvoicingDetails"
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
                            disabled
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
            <template
                v-for="custom_cpi_year in invoicingDetailsComputed.custom_cpi_years"
                :key="custom_cpi_year.year"
            >
                <div class="div d-flex align-items-center mb-3">
                    <div class="col-sm-2 pe-3">
                        <div class="input-group">
                            <span class="input-group-text">Year</span>
                            <input
                                v-model="custom_cpi_year.year"
                                type="text"
                                readonly
                                class="form-control form-control-year text-center"
                            />
                        </div>
                    </div>
                    <div class="pe-3">Label</div>
                    <div class="col-sm-6 pe-3">
                        <div class="input-group">
                            <input
                                v-model="custom_cpi_year.label"
                                type="text"
                                class="form-control"
                                :readonly="
                                    isMigrationProposal &&
                                    custom_cpi_year.has_passed
                                "
                                :required="
                                    !isMigrationProposal &&
                                    custom_cpi_year.has_passed
                                "
                            />
                        </div>
                    </div>
                    <label class="col-sm-3">
                        <div class="input-group">
                            <span class="input-group-text">CPI</span>
                            <input
                                v-model="custom_cpi_year.percentage"
                                step="0.1"
                                min="-100"
                                max="100"
                                type="number"
                                class="form-control"
                                :readonly="
                                    isMigrationProposal &&
                                    custom_cpi_year.has_passed
                                "
                                :required="
                                    !isMigrationProposal &&
                                    custom_cpi_year.has_passed
                                "
                                @change="updatePreviewInvoices"
                                @keyup="updatePreviewInvoices"
                            />
                            <span class="input-group-text">%</span>
                        </div>
                    </label>
                </div>
            </template>
            <div class="row">
                <div class="col">
                    <BootstrapAlert
                        >You will be sent reminders to enter the custom cpi 60
                        days and 45 days prior to the next invoicing
                        period</BootstrapAlert
                    >
                </div>
            </div>
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
                        :disabled="cpi_calculation_method_disabled"
                        @change="updatePreviewInvoices"
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
                        The CPI percentage for the selected quarter will be
                        fetched from the ABS when an invoice is generated
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
                            max="6"
                            step="1"
                            class="form-control"
                            :readonly="invoicing_once_every_readonly"
                            required
                            @change="updatePreviewInvoices"
                        />
                    </div>
                    <div class="">
                        <select
                            v-model="
                                invoicingDetailsComputed.invoicing_repetition_type
                            "
                            class="form-select"
                            aria-label="Repetition Type"
                            :disabled="invoicing_repetition_type_disabled"
                            required
                            @change="onInvoicingRepetitionTypeChange"
                        >
                            <option
                                v-for="repetition_type in filtered_repetition_types"
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
        <div v-if="show_invoicing_quarters" class="row mb-3 pb-3 border-bottom">
            <label for="invoicing_frequency" class="col-form-label col-sm-4"
                >Invoicing Quarters</label
            >
            <div class="col-sm-8">
                <div class="d-flex align-items-center">
                    <div class="pe-3">
                        <select
                            v-model="
                                invoicingDetailsComputed.invoicing_quarters_start_month
                            "
                            :disabled="invoicing_quarters_start_month_disabled"
                            class="form-select"
                            @change="updatePreviewInvoices"
                        >
                            <option
                                :value="1"
                                :selected="
                                    invoicingDetailsComputed.invoicing_quarters_start_month ==
                                    1
                                "
                            >
                                NOV-JAN, FEB-APR, MAY-JUL, AUG-OCT
                            </option>
                            <option
                                :value="2"
                                :selected="
                                    invoicingDetailsComputed.invoicing_quarters_start_month ==
                                    2
                                "
                            >
                                DEC-FEB, MAR-MAY, JUN-AUG, SEP-NOV
                            </option>
                            <option
                                :value="3"
                                :selected="
                                    invoicingDetailsComputed.invoicing_quarters_start_month ==
                                    3
                                "
                            >
                                JAN-MAR, APR-JUN, JUL-SEP, OCT-DEC
                            </option>
                        </select>
                    </div>
                </div>
            </div>
        </div>
        <div v-if="show_percentage_of_gross_turnover_arrears">
            <PercentageTurnoverArrears
                v-if="invoicingDetailsComputed"
                :start-date="startDate"
                :expiry-date="expiryDate"
                :issue-date="issueDate"
                :gross-turnover-percentages="
                    invoicingDetailsComputed.gross_turnover_percentages
                "
                :invoicing-repetition-type="
                    invoicingDetailsComputed.invoicing_repetition_type
                "
                :invoicing-repetition-type-key="
                    getInvoicingRepetitionTypeKeyById(
                        invoicingDetailsComputed.invoicing_repetition_type
                    )
                "
                :proposal-processing-status-id="proposalProcessingStatusId"
                :context="context"
                @update-gross-turnover-percentages="
                    updateGrossTurnoverPercentages
                "
                @on-change-percentage="updatePreviewInvoices"
                @on-change-annual-gross-turnover="updatePreviewInvoices"
                @on-change-quarterly-gross-turnover="updatePreviewInvoices"
                @on-change-monthly-gross-turnover="updatePreviewInvoices"
            />
        </div>
        <div v-if="show_percentage_of_gross_turnover_advance">
            <PercentageTurnoverAdvance
                v-if="invoicingDetailsComputed"
                :start-date="startDate"
                :expiry-date="expiryDate"
                :gross-turnover-percentages="
                    invoicingDetailsComputed.gross_turnover_percentages
                "
                :proposal-processing-status-id="proposalProcessingStatusId"
                :context="context"
                @update-gross-turnover-percentages="
                    updateGrossTurnoverPercentages
                "
                @on-change-percentage="updatePreviewInvoices"
                @on-change-gross-turnover-estimate="updatePreviewInvoices"
                @on-change-gross-turnover-actual="updatePreviewInvoices"
            />
        </div>

        <div v-if="show_fixed_annual_increment">
            <AnnualIncrement
                v-if="invoicingDetailsComputed"
                increment-type="annual_increment_amount"
                :years-array="invoicingDetailsComputed.annual_increment_amounts"
                :approval-duration-years="approvalDurationYears"
                :start-date="startDate"
                :context="context"
                @update-years-array="updateYearsArray"
                @on-change-increment="updatePreviewInvoices"
            />
        </div>
        <div v-if="show_fixed_annual_percentage">
            <AnnualIncrement
                v-if="invoicingDetailsComputed"
                increment-type="annual_increment_percentage"
                :years-array="
                    invoicingDetailsComputed.annual_increment_percentages
                "
                :start-date="startDate"
                :context="context"
                :approval-duration-years="approvalDurationYears"
                @update-years-array="updateYearsArray"
                @on-change-increment="updatePreviewInvoices"
            />
        </div>
        <div
            v-if="show_invoice_previewer"
            class="row mb-3 border-bottom justify-content-center"
        >
            <InvoicePreviewer
                v-if="
                    previewInvoices &&
                    invoicingDetailsComputed &&
                    invoicingDetailsComputed.invoicing_repetition_type
                "
                :preview-invoices="previewInvoices"
                :invoicing-details="invoicingDetailsComputed"
                :start-date="startDate"
                :expiry-date="expiryDate"
                :charge-method-key="
                    getChargeMethodKeyById(
                        invoicingDetailsComputed.charge_method
                    )
                "
                :show-past-invoices="context == 'Proposal'"
                :loading-preview-invoices="loadingPreviewInvoices"
                :context="context"
                @update-default-invoicing-date="updateDefaultInvoicingDate"
            />
        </div>
        <template v-if="show_ad_hoc_invoicing">
            <div class="row mb-3">
                <div class="col-3">
                    <button class="btn btn-primary mb-1">
                        + Add Ad Hoc Invoice
                    </button>
                </div>
                <div class="col-9">
                    <BootstrapAlert class="py-2">
                        Use this option if there are funds in arrears that need
                        invoicing immediately
                    </BootstrapAlert>
                </div>
            </div>
            <div class="row mb-3">
                <div class="col">
                    <ul class="list-group">
                        <li class="list-group-item">
                            <div class="d-flex">
                                <div class="pe-3 w-100">
                                    <label>Description</label>
                                    <input type="text" class="form-control" />
                                </div>
                            </div>
                        </li>
                        <li class="list-group-item">
                            <div class="d-flex">
                                <div class="pe-3">
                                    <label>Amount</label>
                                    <input
                                        type="number"
                                        class="form-control"
                                        step="0.1"
                                    />
                                </div>
                                <div class="pe-3">
                                    <label>Issue Date</label>
                                    <input
                                        type="date"
                                        class="form-control"
                                        :value="
                                            new Date()
                                                .toISOString()
                                                .slice(0, 10)
                                        "
                                    />
                                </div>
                                <div class="pe-3">
                                    <label>Due Date</label>
                                    <input
                                        type="date"
                                        class="form-control"
                                        :value="
                                            new Date()
                                                .toISOString()
                                                .slice(0, 10)
                                        "
                                    />
                                </div>
                            </div>
                        </li>
                    </ul>
                </div>
            </div>
        </template>
    </form>
</template>

<script>
import AnnualIncrement from '@/components/common/component_fixed_annual_amount.vue';
import PercentageTurnoverAdvance from '@/components/common/component_percentage_gross_turnover_advance.vue';
import PercentageTurnoverArrears from '@/components/common/component_percentage_gross_turnover_arrears.vue';
import InvoicePreviewer from '@/components/common//invoice_previewer.vue';

import { api_endpoints, constants, helpers, utils } from '@/utils/hooks';

export default {
    name: 'InvoicingDetails',
    components: {
        AnnualIncrement,
        PercentageTurnoverAdvance,
        PercentageTurnoverArrears,
        InvoicePreviewer,
    },
    props: {
        context: {
            type: String,
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
        issueDate: {
            type: String,
            required: true,
        },
        proposalProcessingStatusId: {
            type: String,
            required: true,
        },
        proposalTypeCode: {
            type: String,
            required: true,
        },
        approvalType: {
            type: String,
            required: true,
        },
    },
    emits: ['updateInvoicingDetails'],
    data: function () {
        return {
            sequentialYearHasPassed: helpers.sequentialYearHasPassed,
            yearsElapsedSinceStartDate: helpers.yearsElapsedSinceStartDate,
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
            previewInvoices: null,
            loadingPreviewInvoices: false,
        };
    },
    computed: {
        debug: function () {
            if (this.$route.query.debug) {
                return this.$route.query.debug === 'true';
            }
            return false;
        },
        invoicingDetailsComputed: {
            get() {
                return this.invoicingDetails;
            },
            set(value) {
                this.$emit('updateInvoicingDetails', value);
            },
        },
        isMigrationProposal: function () {
            return (
                this.proposalTypeCode == constants.PROPOSAL_TYPE.MIGRATION.code
            );
        },
        financialYearRows: function () {
            const rows = [];
            for (let i = 0; i < this.financialYearsIncluded.length; i++) {
                let financialYear = this.financialYearsIncluded[i];
                let year = financialYear.split('-')[1];
                rows.push({
                    year: year,
                    financial_year: financialYear,
                    label: '',
                    cpi: '',
                });
            }
            return rows;
        },
        show_once_off_charge_amount: function () {
            if (this.invoicingDetails && this.invoicingDetails.charge_method)
                if (
                    this.invoicingDetails.charge_method ===
                    this.getChargeMethodIdByKey('once_off_charge')
                )
                    return true;
            return false;
        },
        show_fixed_annual_increment: function () {
            if (this.invoicingDetails && this.invoicingDetails.charge_method)
                if (
                    this.invoicingDetails.charge_method ===
                    this.getChargeMethodIdByKey(
                        'base_fee_plus_fixed_annual_increment'
                    )
                )
                    return true;
            return false;
        },
        show_fixed_annual_percentage: function () {
            if (this.invoicingDetails && this.invoicingDetails.charge_method)
                if (
                    this.invoicingDetails.charge_method ===
                    this.getChargeMethodIdByKey(
                        'base_fee_plus_fixed_annual_percentage'
                    )
                )
                    return true;
            return false;
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
                return true;
            return false;
        },
        show_review_of_base_fee: function () {
            return this.show_base_fee;
        },
        show_cpi_method: function () {
            if (this.invoicingDetails && this.invoicingDetails.charge_method)
                if (
                    this.invoicingDetails.charge_method ===
                    this.getChargeMethodIdByKey('base_fee_plus_annual_cpi')
                )
                    return true;
            return false;
        },
        show_custom_cpi_years: function () {
            if (this.invoicingDetails && this.invoicingDetails.charge_method)
                if (
                    this.invoicingDetails.charge_method ===
                    this.getChargeMethodIdByKey(
                        'base_fee_plus_annual_cpi_custom'
                    )
                )
                    return true;
            return false;
        },
        show_percentage_of_gross_turnover_advance: function () {
            if (this.invoicingDetails && this.invoicingDetails.charge_method)
                if (
                    this.invoicingDetails.charge_method ===
                    this.getChargeMethodIdByKey(
                        'percentage_of_gross_turnover_in_advance'
                    )
                )
                    return true;
            return false;
        },
        show_percentage_of_gross_turnover_arrears: function () {
            if (this.invoicingDetails && this.invoicingDetails.charge_method)
                if (
                    this.invoicingDetails.charge_method ===
                    this.getChargeMethodIdByKey('percentage_of_gross_turnover')
                )
                    return true;
            return false;
        },
        show_crown_land_rent_review_date: function () {
            return this.show_base_fee;
        },
        crown_land_rent_review_readonly: function () {
            return this.context != 'Proposal';
        },
        invoicing_once_every_readonly: function () {
            return (
                [1, 2].includes(
                    this.invoicingDetailsComputed.invoicing_repetition_type
                ) ||
                this.getChargeMethodIdByKey('percentage_of_gross_turnover') ||
                this.getChargeMethodIdByKey(
                    'percentage_of_gross_turnover_in_advance'
                ) ||
                this.context != 'Proposal'
            );
        },
        cpi_calculation_method_disabled: function () {
            return this.context != 'Proposal';
        },
        invoicing_repetition_type_disabled: function () {
            return this.context != 'Proposal';
        },
        invoicing_quarters_start_month_disabled: function () {
            return this.context != 'Proposal';
        },
        invoicing_schedule_disabled: function () {
            return this.context != 'Proposal';
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
                        this.getChargeMethodIdByKey(
                            'percentage_of_gross_turnover_in_advance'
                        ),
                    ].includes(this.invoicingDetails.charge_method)
                )
                    return true;
                return false;
            }
            return false;
        },
        show_invoice_previewer: function () {
            return this.show_invoicing_frequency;
        },
        show_invoicing_quarters: function () {
            return (
                (this.invoicingDetails.charge_method ==
                    this.getChargeMethodIdByKey(
                        'percentage_of_gross_turnover'
                    ) ||
                    this.invoicingDetails.charge_method ==
                        this.getChargeMethodIdByKey(
                            'percentage_of_gross_turnover_in_advance'
                        )) &&
                this.show_invoicing_frequency &&
                this.invoicingDetailsComputed.invoicing_repetition_type == 2
            );
        },
        show_month_of_year_to_invoice: function () {
            return (
                1 == this.invoicingDetailsComputed.invoicing_repetition_type &&
                this.show_invoicing_frequency
            );
        },
        show_ad_hoc_invoicing: function () {
            // Todo: add logic
            return constants.APPROVAL_TYPE.LICENCE == this.approvalType;
        },
        filtered_repetition_types: function () {
            // Don't show annual invoicing option for gross turnover charge method
            if (this.invoicingDetails) {
                if (
                    this.invoicingDetails.charge_method ==
                        this.getChargeMethodIdByKey(
                            'percentage_of_gross_turnover'
                        ) ||
                    this.invoicingDetails.charge_method ==
                        this.getChargeMethodIdByKey(
                            'percentage_of_gross_turnover_in_advance'
                        )
                ) {
                    return this.repetition_types.filter(
                        (repetition_type) => repetition_type.id != 1
                    );
                }
            }
            return this.repetition_types;
        },
    },
    created: function () {
        this.fetchChargeMethods();
        this.fetchRepetitionTypes();
        this.fetchCPICalculationMethods();
        if (!this.invoicingDetailsComputed.invoicing_quarters_start_month) {
            // 1 = January [JAN, APR, JUL, OCT], 2 = February [FEB, MAY, AUG, NOV], 3 = March [MAR, JUN, SEP, DEC]
            this.invoicingDetailsComputed.invoicing_quarters_start_month = 3;
        }
        this.invoicingDetailsComputed.context = this.context;
    },
    mounted: function () {
        this.$nextTick(function () {
            this.invoicingDetailsComputed = {
                ...this.invoicingDetailsComputed,
                custom_cpi_years: this.getCustomCPIYears(),
            };
        });
    },
    methods: {
        getCustomCPIYears: function () {
            const rows = [];
            let periodStartDate = moment(this.startDate);
            for (let i = 0; i < this.approvalDurationYears; i++) {
                let hasPassed = periodStartDate.isSameOrBefore(moment());
                if (!this.invoicingDetailsComputed.custom_cpi_years[i]) {
                    rows.push({
                        year: i + 1,
                        label: '',
                        percentage: null,
                        has_passed: hasPassed,
                    });
                } else {
                    rows.push(
                        this.invoicingDetailsComputed.custom_cpi_years[i]
                    );
                }
                periodStartDate = periodStartDate.add(1, 'year');
            }
            return rows;
        },
        onChargeMethodChange: function (event) {
            this.$nextTick(() => {
                $(event.target)
                    .closest('.row')
                    .next('.row')
                    .find('input')
                    .focus();
            });
            const chargeMethodKey = this.getChargeMethodKeyById(
                this.invoicingDetailsComputed.charge_method
            );
            if (
                [
                    'percentage_of_gross_turnover',
                    'percentage_of_gross_turnover_in_advance',
                ].includes(chargeMethodKey)
            ) {
                this.invoicingDetailsComputed.invoicing_repetition_type = 2;
            } else {
                this.invoicingDetailsComputed.invoicing_repetition_type = 1;
            }
            this.updatePreviewInvoices();
        },
        onInvoicingRepetitionTypeChange: function (event) {
            if (['1', '2'].includes(event.target.value)) {
                this.invoicingDetailsComputed.invoicing_once_every = 1;
            }
            this.updatePreviewInvoices();
        },
        updateReviewDates: function (review_dates) {
            this.invoicingDetailsComputed = {
                ...this.invoicingDetailsComputed,
                crown_land_rent_review_dates: review_dates,
            };
        },
        updateYearsArray: function (incrementType, years_array) {
            if ('annual_increment_amount' == incrementType) {
                this.invoicingDetailsComputed = {
                    ...this.invoicingDetailsComputed,
                    annual_increment_amounts: years_array,
                };
            } else {
                this.invoicingDetailsComputed = {
                    ...this.invoicingDetailsComputed,
                    annual_increment_percentages: years_array,
                };
            }
        },
        updateGrossTurnoverPercentages: function (gross_turnover_percentages) {
            this.invoicingDetailsComputed = {
                ...this.invoicingDetailsComputed,
                gross_turnover_percentages: gross_turnover_percentages,
            };
        },
        updateDefaultInvoicingDate: function (firstIssueDate) {
            if (!this.invoicingDetailsComputed.invoicing_day_of_month) {
                let invoicing_day_of_month = firstIssueDate.date();
                this.invoicingDetailsComputed = {
                    ...this.invoicingDetailsComputed,
                    invoicing_day_of_month: invoicing_day_of_month,
                };
            }
            if (
                this.invoicingDetailsComputed.invoicing_repetition_type == 1 &&
                !this.invoicingDetailsComputed.invoicing_month_of_year
            ) {
                let invoicing_month_of_year = firstIssueDate.month() + 1;
                this.invoicingDetailsComputed = {
                    ...this.invoicingDetailsComputed,
                    invoicing_month_of_year: invoicing_month_of_year,
                };
            }
        },
        chargeMethodDisabled: function (charge_method) {
            return (
                (this.context == 'Approval' &&
                    !(
                        charge_method.id ==
                        this.invoicingDetailsComputed.charge_method
                    )) ||
                ([
                    'base_fee_plus_fixed_annual_increment',
                    'base_fee_plus_fixed_annual_percentage',
                ].includes(charge_method.key) &&
                    // The approval runs for less than a full year
                    this.approvalDurationYears - 1 == 0)
            );
        },
        getChargeMethodIdByKey: function (key) {
            let charge_method = this.charge_methods.find(
                (charge_method) => charge_method.key === key
            );
            if (charge_method) return charge_method.id;
            else return 0;
        },
        getChargeMethodKeyById: function (id) {
            let charge_method = this.charge_methods.find(
                (charge_method) => charge_method.id === id
            );
            if (charge_method) return charge_method.key;
            else return '';
        },
        getInvoicingRepetitionTypeKeyById: function (id) {
            let repetition_type = this.repetition_types.find(
                (repetition_type) => repetition_type.id === id
            );
            if (repetition_type) return repetition_type.key;
            else return '';
        },
        fetchChargeMethods: async function () {
            let vm = this;
            try {
                const res = await fetch(api_endpoints.charge_methods);
                if (!res.ok) throw new Error(res.statusText); // 400s or 500s error
                let charge_methods = await res.json();
                vm.charge_methods = charge_methods;
                // This has to happen here as the show_invoice_previewer computed method depends on the charge_method key
                this.fetchPreviewInvoices();
            } catch (err) {
                console.error({ err });
            }
        },
        fetchRepetitionTypes: async function () {
            let vm = this;
            try {
                const res = await fetch(api_endpoints.repetition_types);
                if (!res.ok) throw new Error(res.statusText); // 400s or 500s error
                let repetition_types = await res.json();
                vm.repetition_types = repetition_types;
                vm.$nextTick(function () {
                    const chargeMethodKey = this.getChargeMethodKeyById(
                        this.invoicingDetailsComputed.charge_method
                    );

                    if (!vm.invoicingDetailsComputed.review_once_every) {
                        vm.invoicingDetailsComputed.review_once_every = 5;
                    }
                    if (!vm.invoicingDetailsComputed.invoicing_once_every) {
                        vm.invoicingDetailsComputed.invoicing_once_every = 1;
                    }
                    if (!vm.invoicingDetailsComputed.review_repetition_type) {
                        vm.invoicingDetailsComputed.review_repetition_type = 1;
                    }
                    if (
                        'percentage_of_gross_turnover' != chargeMethodKey &&
                        !vm.invoicingDetailsComputed.invoicing_repetition_type
                    ) {
                        vm.invoicingDetailsComputed.invoicing_repetition_type = 1;
                    }
                });
            } catch (err) {
                console.error({ err });
            }
        },
        fetchCPICalculationMethods: async function () {
            let vm = this;
            try {
                const res = await fetch(
                    api_endpoints.cpi_calculation_methods + 'no-pagination/'
                );
                if (!res.ok) throw new Error(res.statusText); // 400s or 500s error
                let cpi_calculation_methods = await res.json();
                vm.cpi_calculation_methods = cpi_calculation_methods;
                if (
                    vm.invoicingDetailsComputed.cpi_calculation_method == null
                ) {
                    vm.invoicingDetailsComputed.cpi_calculation_method =
                        cpi_calculation_methods.find(
                            (x) => x.name == 'latest_sep_qtr'
                        ).id;
                }
            } catch (err) {
                console.error({ err });
            }
        },
        fetchPreviewInvoices: async function () {
            if (!this.show_invoice_previewer) {
                return;
            }
            this.previewInvoices = await utils.fetchUrl(
                api_endpoints.invoicing_details +
                    `${this.invoicingDetails.id}/preview_invoices/`
            );
        },
        saveInvoicingDetails: async function () {
            const requestOptions = {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(this.invoicingDetailsComputed),
            };
            await utils.fetchUrl(
                api_endpoints.invoicing_details +
                    `${this.invoicingDetails.id}/`,
                requestOptions
            );
        },
        updatePreviewInvoices: async function () {
            const requestOptions = {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(this.invoicingDetailsComputed),
            };
            this.loadingPreviewInvoices = true;
            this.previewInvoices = await utils.fetchUrl(
                api_endpoints.invoicing_details +
                    `${this.invoicingDetails.id}/update_and_preview_invoices/`,
                requestOptions
            );
            this.loadingPreviewInvoices = false;
        },
    },
};
</script>
<style scoped>
.invalid-charge-method {
    margin-left: -17px;
}
</style>
