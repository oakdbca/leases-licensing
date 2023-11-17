<template lang="html">
    <div>
        <div class="form-group">
            <ckeditor
                :id="id"
                v-model="detailsText"
                :editor="editor"
                :config="editor.defaultConfig"
                :name="name"
                :required="isRequired"
                :disabled="readonly"
                :read-only="readonly"
            />
        </div>
    </div>
</template>

<script>
import Editor from './ckeditor.js';

export default {
    name: 'RichText',
    props: [
        'id',
        'name',
        'proposalData',
        'isRequired',
        'label',
        'readonly',
        'can_view_richtext_src',
        'placeholder_text',
    ],
    emits: ['textChanged'],
    data() {
        return {
            detailsText: '',
            editor: Editor,
        };
    },
    watch: {
        detailsText: function () {
            // Parent component can subscribe this event in order to update text
            if (this.proposalData == this.detailsText) {
                // Only emit if the text was changed through input, not through the parent component
                return;
            }
            this.$emit('textChanged', this.detailsText);
        },
    },
    created: function () {
        if (this.proposalData) {
            this.detailsText = this.proposalData;
        }
        this.editor.defaultConfig['placeholder'] = this.placeholder_text;
    },
    methods: {
        focus() {
            this.$nextTick(() => {
                $('.ck-editor__editable').focus();
            });
        },
    },
};
</script>
