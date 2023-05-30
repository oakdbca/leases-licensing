<template lang="html">
    <div>
        <div class="form-group">
            <ckeditor :editor="editor" v-model="detailsText" :config="editorConfig" :name="name" :required="isRequired"
                :disabled="readonly" :read-only="readonly" />
        </div>
    </div>
</template>

<script>
import ClassicEditor from '@ckeditor/ckeditor5-build-classic'

export default {
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
            editorConfig: {
                language: 'en',
                placeholder: vm.placeholder_text,
            },
            detailsText: '',
            editor: ClassicEditor,
        }
    },
    components: {
        ckeditor: ClassicEditor.component
    },
    watch: {
        detailsText: function () {
            // Parent component can subscribe this event in order to update text
            this.$emit('textChanged', this.detailsText)
        }
    },
    created: function () {
        if (this.proposalData) {
            this.detailsText = this.proposalData;
        }
    },
}
</script>
