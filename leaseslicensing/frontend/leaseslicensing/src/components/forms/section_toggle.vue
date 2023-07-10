<template lang="html">
    <div :id="custom_id" class="card mb-2 section-toggle">
        <div class="card-header fw-bold h4 p-4">
            <div
                :id="'show_hide_switch_' + section_body_id"
                class="row"
                aria-expanded="true"
                :aria-controls="section_body_id"
                @click="toggle_show_hide"
            >
                <div class="col-11 label" :style="'color:' + customColor">
                    {{ label }}
                    <small v-if="subtitle" class="text-muted">{{
                        subtitle
                    }}</small>
                </div>
                <div class="col-1 text-end">
                    <i
                        :id="chevron_elem_id"
                        class="bi fw-bold chevron-toggle cursor-pointer"
                        role="button"
                        :data-bs-target="'#' + section_body_id"
                    >
                    </i>
                </div>
            </div>
        </div>
        <div
            :id="section_body_id"
            :class="detailsClass"
            :style="'color:' + customColor"
        >
            <slot></slot>
        </div>
    </div>
</template>

<script>
import { v4 as uuid } from 'uuid'

export default {
    name: 'FormSection',
    props: {
        label: {
            type: String,
            required: true,
        },
        subtitle: {
            type: String,
            default: '',
        },
        index: {
            type: String,
            required: true,
        },
        hideHeader: {
            type: Boolean,
            default: false,
        },
        customColor: {
            type: String,
            default: '',
        },
        formCollapse: {
            type: Boolean,
            default: false,
        },
    },
    data: function () {
        return {
            custom_id: uuid(),
            chevron_elem_id: 'chevron_elem_' + uuid(),
        }
    },
    computed: {
        detailsClass: function () {
            return this.formCollapse ? 'card-body collapse' : 'card-body'
        },
        section_header_id: function () {
            return 'section_header_' + this.index
        },
        section_body_id: function () {
            return 'section_body_' + this.index
        },
    },
    mounted: function () {
        // eslint-disable-next-line no-undef
        chevron_toggle.init()
    },
}
</script>
