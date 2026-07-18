<script setup>
import { usePalEditorStore } from '@/stores/paleditor'
import { ref } from 'vue'
const palStore = usePalEditorStore()

const PW = ref("")

</script>
<template>
    <div id="authDiv">
        <span class="auth-kicker">Protected workspace</span>
        <img alt="Paldeck" class="logo" src="@/assets/logo.ico" width="96" height="96" />
        <h1>Unlock Paldeck</h1>
        <p>{{ palStore.getTranslatedText("AuthView_PW_Prompt_2") }}</p>
        
        <input type="password" v-model="PW"
                placeholder="PASSWORD" :disabled="palStore.LOADING_FLAG">
        <button @click="palStore.login" :disabled="palStore.LOADING_FLAG" :value="PW">
            {{ palStore.getTranslatedText("AuthView_BTN_Unlock") }}
        </button>
        <a href="https://github.com/Guineabear/Palworld-Pal-Editor" target="_blank" rel="noopener noreferrer">Paldeck on GitHub</a>
    </div>
</template>

<style scoped>
div#authDiv {
    display: flex;
    flex-direction: column;
    width: min(30rem, calc(100% - 2rem));
    margin: calc(var(--topbar-height) + 12vh) auto var(--space-lg);
    padding: var(--space-lg);
    border: var(--rule);
    border-radius: var(--radius-panel);
    background: var(--color-paper-2);
    box-shadow: var(--shadow-panel);
}

.auth-kicker {
    color: var(--color-accent);
    font-size: var(--text-xs);
    font-weight: 750;
    letter-spacing: .12em;
    text-transform: uppercase;
}

.logo { margin: var(--space-md) 0; border-radius: 1.35rem; box-shadow: var(--shadow-control); }

h1 {
    margin: 0 0 var(--space-2xs);
    color: var(--color-ink);
    font-size: 2.25rem;
    font-weight: 780;
    letter-spacing: -.045em;
}

a {
    align-self: center;
    margin-top: var(--space-md);
    color: var(--color-accent);
    font-size: var(--text-sm);
    text-underline-offset: .2em;
}

p {
    word-wrap: break-word;
    font-size: var(--text-md);
    margin: 0 0 var(--space-xs);
}

input {
    height: 3rem;
    background-color: var(--color-paper);
    color: var(--color-ink);
    border: var(--rule);
    outline: none;
    border-radius: var(--radius-input);
    font-size: var(--text-md);
    padding-left: 0.7rem;
    padding-right: 0.7rem;
    margin: var(--space-sm) 0;
}

input:focus {
    background-color: var(--color-paper-3);
    border-color: var(--color-accent);
    color: var(--color-ink);
}

button {
    height: 3rem;
    background-color: var(--color-accent-strong);
    color: var(--color-ink);
    border: 1px solid transparent;
    outline: none;
    border-radius: var(--radius-input);
    font-size: var(--text-md);
    font-weight: 650;
    transition: filter var(--dur-short) var(--ease-out), transform var(--dur-short) var(--ease-out);
    margin: 0;
}

button:hover {
    filter: brightness(1.08);
    transform: translateY(-1px);
    cursor: pointer;
}

button:disabled {
    background-color: #8a8a8a;
}
</style>
