<script setup>
import { usePalEditorStore } from '@/stores/paleditor'
const palStore = usePalEditorStore()

defineProps(['placeholder'])
const model = defineModel()

</script>

<template>
    <input type="text" v-model="model" :placeholder="placeholder" :disabled="palStore.LOADING_FLAG">
</template>

<style scoped>
input {
    display: flex;
    align-items: center;
    min-width: 0;
    background-color: var(--color-paper);
    height: 1.6rem;
    max-width: 100%;
    /* margin: .2rem; */
    padding: .2rem .4rem;
    border-radius: var(--radius-input);
    color: var(--color-ink);
    /* box-shadow: 2px 2px 10px rgb(38, 38, 38); */
    transition: background-color var(--dur-short) var(--ease-out), border-color var(--dur-short) var(--ease-out);

    border: var(--rule);
    outline: none;
    flex: 1;
}

input:focus {
    background-color: var(--color-paper-3);
    border-color: var(--color-accent);
    color: var(--color-ink);
}
</style>
