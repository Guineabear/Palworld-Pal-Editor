<script setup>
import { usePalEditorStore } from '@/stores/paleditor'
const palStore = usePalEditorStore()

defineProps(['icon', 'name', 'value'])
defineEmits([])
</script>

<template>
    <button :name="name" :value="value" :disabled="palStore.LOADING_FLAG">
        {{ icon }}
    </button>
</template>

<style scoped>
button {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 2rem;
    height: 2rem;
    padding: 0;
    margin: 0;
    background-color: var(--color-paper-3);
    color: var(--color-ink);
    border: var(--rule);
    outline: none;
    border-radius: var(--radius-input);
    transition: background-color var(--dur-short) var(--ease-out), border-color var(--dur-short) var(--ease-out), transform var(--dur-short) var(--ease-out);
    cursor: pointer;
}

button:hover {
    background-color: var(--color-accent-muted);
    border-color: var(--color-accent);
    transform: translateY(-1px);
}

button:disabled {
    background-color: #8a8a8a;
}
</style>
