<template lang="html">
    <div>
        <div class="form-group">
            <ckeditor :editor="editor" v-model="detailsText" :config="editor.defaultConfig" :name="name" :required="isRequired"
                :disabled="readonly" :read-only="readonly" :id="id"/>
        </div>
    </div>
</template>

<script>
import Editor from './ckeditor.js'

export default {
    name: 'RichText',
    emits: ['textChanged'],
    props: [
        "id",
        "name",
        "proposalData",
        "isRequired",
        "label",
        "readonly",
        "can_view_richtext_src",
        "placeholder_text"
    ],
    data() {
        let vm = this;
        if (vm.can_view_richtext_src) {
            var remove_buttons = ''
        } else {
            var remove_buttons = 'Source,About'
        }

        return {
            detailsText: '',
            editor: Editor,
        }
    },
    watch: {
        detailsText: function () {
            // Parent component can subscribe this event in order to update text
            if (this.proposalData == this.detailsText) {
                // Only emit if the text was changed through input, not through the parent component
                return;
            }
            this.$emit('textChanged', this.detailsText)
        }
    },
    methods: {
        focus() {
            console.log('focus rich text')
            this.$nextTick(() => {
                $('.ck-editor__editable').focus();
            })
        },
    },
    created: function () {
        if (this.proposalData) {
            this.detailsText = this.proposalData;
        }
        this.editor.defaultConfig["placeholder"] = this.placeholder_text;
    },
}
</script>
