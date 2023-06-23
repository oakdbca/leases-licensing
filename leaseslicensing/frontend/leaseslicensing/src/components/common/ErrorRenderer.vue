<template>
    <template v-if="typeof errors === 'string'">
        {{ errors }}
    </template>
    <template v-else>
        <template v-if="Array.isArray(this.errors)">
            <template v-if="this.errors.length > 1">
                <ul class="errors-list">
                    <li v-for="error in errors">{{ error }}</li>
                </ul>
            </template>
            <template v-else>
                {{ errors[0] }}
            </template>
        </template>
        <template v-else-if="typeof errors === 'object'">
            <template v-if="Object.keys(this.errors).length > 1">
                <ul class="errors-list">
                    <li v-for="(error, key) in errors"><span class="fw-bold">{{ key }}</span>: {{ error }}</li>
                </ul>
            </template>
            <template v-else>
                <span class="fw-bold">{{ Object.keys(errors)[0] }}</span>: {{ Object.values(errors)[0] }}
            </template>
        </template>
    </template>
</template>
<script>
export default {
    name: 'ErrorRenderer',
    props: {
        errors: {
            type: [Object, String, Array],
            required: true
        },
    },
}
</script>
<style scoped>
.errors-list {
    margin-bottom: 0;
}
</style>