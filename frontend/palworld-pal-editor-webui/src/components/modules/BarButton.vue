<script setup>
import { usePalEditorStore } from '@/stores/paleditor'
const palStore = usePalEditorStore()

defineProps(['content', 'name', 'value'])
</script>

<template>
    <button :name="name" :value="value" :disabled="palStore.LOADING_FLAG">
        {{ content }}
    </button>
</template>

<style scoped>
button {
    margin-bottom: 1rem;
    height: 3rem;
    background-color: var(--color-accent-strong);
    color: var(--color-ink);
    border: 1px solid transparent;
    outline: none;
    border-radius: var(--radius-input);
    font-size: var(--text-md);
    font-weight: 650;
    transition: filter var(--dur-short) var(--ease-out), transform var(--dur-short) var(--ease-out);
}

button:hover {
    filter: brightness(1.08);
    transform: translateY(-1px);
    cursor: pointer;
}

button:disabled {
    background-color: #8a8a8a;
    cursor: auto;
}
</style>
