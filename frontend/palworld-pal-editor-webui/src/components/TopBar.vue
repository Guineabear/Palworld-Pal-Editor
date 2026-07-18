<script setup>
import { usePalEditorStore } from '@/stores/paleditor'
import { watch, ref } from 'vue';
const palStore = usePalEditorStore()

const loadingWidth = ref(0);
const showLoading = ref(false)
const interval = ref(null)

watch(() => palStore.LOADING_FLAG, (newValue) => {
  if (newValue) {
    interval.value = setInterval(() => {
      if (palStore.LOADING_FLAG) {
        if (loadingWidth.value < 20) loadingWidth.value += Math.random() * 8;
        if (loadingWidth.value < 50) loadingWidth.value += Math.random() * 4;
        if (loadingWidth.value < 75) loadingWidth.value += Math.random() * 2;
        if (loadingWidth.value < 98) loadingWidth.value += Math.random() * 1;
      }
    }, 2000);
    showLoading.value = true
    loadingWidth.value = 2
  }

  if (!newValue) {
    loadingWidth.value = 100;
    setTimeout(() => {
      showLoading.value = false
      clearInterval(interval.value);
    }, 250);
  }
});

const show_cheats = () => {
  palStore.HIDE_INVALID_OPTIONS = !palStore.HIDE_INVALID_OPTIONS;
}

const save = async () => {
  await palStore.writeSave();
}
</script>

<template>
  <div class="loading-bar" v-if="showLoading" :style="{ width: loadingWidth + '%' }"></div>
  <header id="topbar" class="app-command-bar">
    <a class="app-brand" href="https://github.com/Guineabear/Palworld-Pal-Editor" target="_blank"
      rel="noopener noreferrer" aria-label="Palworld Pal Editor on GitHub">
      <img src="@/assets/logo.ico" alt="" width="34" height="34">
      <span><strong>Paldeck</strong><small>Pal Editor</small></span>
    </a>
    <div class="save-context" v-if="palStore.SAVE_LOADED_FLAG">
      <strong>Loaded save</strong>
      <span>{{ palStore.PAL_WRITE_BACK_PATH || palStore.PAL_GAME_SAVE_PATH }}</span>
    </div>
    <nav class="primary-actions" v-if="palStore.SAVE_LOADED_FLAG" aria-label="Save actions">
      <button class="op save" @click="save" :disabled="palStore.LOADING_FLAG">{{ palStore.getTranslatedText("TopBar_Btn_Save") }}</button>
      <button class="op" @click="palStore.loadSave" :disabled="palStore.LOADING_FLAG">{{ palStore.getTranslatedText("TopBar_Btn_Reload") }}</button>
      <button class="op quiet" @click="palStore.reset" :disabled="palStore.LOADING_FLAG">{{ palStore.getTranslatedText("TopBar_Btn_Main_Page") }}</button>
    </nav>
    <div class="language-control">
      <select id="languageSelect" v-model="palStore.I18n" @change="palStore.updateI18n" aria-label="Language" :disabled="palStore.LOADING_FLAG">
        <option :value="key" v-for="translated, key in palStore.I18nList">{{ translated }}</option>
      </select>
    </div>
  </header>
</template>

<style scoped>
div#topbar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: var(--topbar-height);
  min-width: 0;
  z-index: 1000;
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: var(--space-2xs);
  padding: var(--space-2xs) var(--space-sm);
  background: var(--color-paper-glass);
  border-bottom: var(--rule);
  box-shadow: var(--shadow-topbar);
  backdrop-filter: blur(12px);
}

div.brand {
  display: flex;
  flex: 0 0 auto;
  align-items: center;
  gap: var(--space-2xs);
  color: var(--color-ink);
  white-space: nowrap;
}

div.brand img {
  border-radius: var(--radius-input);
}

div.brand strong {
  font-weight: 700;
}

div.loading-bar {
  position: fixed;
  top: 0;
  left: 0;
  height: 2px;
  background-color: hsla(160, 100%, 37%, 1);
  transition: width 1s ease-out;
}

div.options {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: var(--space-3xs);
  min-width: 0;
  padding: 0;
}

div.options:nth-last-child(2) {
  flex: 1 1 auto;
  overflow-x: auto;
  overflow-y: hidden;
  scrollbar-width: thin;
}

div.options:last-child {
  flex: 0 0 auto;
  margin-left: auto;
}

select#languageSelect {
  display: flex;
  align-items: center;
  background-color: var(--color-paper-2);
  height: 2.25rem;
  margin: 0;
  padding: .25rem .55rem;
  border: var(--rule);
  border-radius: var(--radius-input);
  color: var(--color-ink);
}

input.savePath {
  display: flex;
  align-items: center;
  background-color: var(--color-paper-2);
  height: 2.25rem;
  width: clamp(10rem, 19vw, 22rem);
  min-width: 8rem;
  margin: 0;
  padding: .25rem .6rem;
  border-radius: var(--radius-input);
  color: var(--color-ink);
  border: var(--rule);
  outline: none;
}

input.savePath:focus {
  background-color: var(--color-paper-3);
  border-color: var(--color-accent);
  color: var(--color-ink);
}

button.op {
  height: 2.25rem;
  flex: 0 0 auto;
  padding: 0 var(--space-xs);
  background-color: var(--color-paper-3);
  color: var(--color-ink);
  border: var(--rule);
  outline: none;
  border-radius: var(--radius-input);
  white-space: nowrap;
  transition: background-color var(--dur-short) var(--ease-out), border-color var(--dur-short) var(--ease-out), transform var(--dur-short) var(--ease-out);
}

button.op:hover {
  background-color: var(--color-accent-muted);
  border-color: var(--color-accent);
  transform: translateY(-1px);
  cursor: pointer;
}

button.op:disabled {
  background-color: #8a8a8a;
  box-shadow: 0 0 0;
  filter: grayscale(100%);
  cursor: not-allowed;
}

button.op.blue {
  height: 2.25rem;
  background-color: var(--color-accent-strong);
  color: var(--color-ink);
  border: 1px solid transparent;
  outline: none;
  border-radius: var(--radius-input);
  transition: background-color var(--dur-short) var(--ease-out), transform var(--dur-short) var(--ease-out);
}

button.op.blue:hover {
  background-color: rgb(11, 84, 173);
  cursor: pointer;
}

button.op.blue:disabled {
  background-color: #8a8a8a;
  box-shadow: 0 0 0;
  filter: grayscale(100%);
  cursor: not-allowed;
}

button.op.save {
  background-color: var(--color-danger);
}

button.op.save:hover {
  background-color: #830e25;
}

button.op.save:disabled {
  background-color: #8a8a8a;
  box-shadow: 0 0 0;
  filter: grayscale(100%);
  cursor: not-allowed;
}

button.op.toggled {
  background-color: var(--color-success);
  color: var(--color-accent-ink);
}

button.op.toggled:hover {
  background-color: #138d4a;
}

button.op.toggled:disabled {
  background-color: #8a8a8a;
  box-shadow: 0 0 0;
  filter: grayscale(100%);
  cursor: not-allowed;
}

.tooltip-container {
  position: relative;
  display: inline-block;
  flex: 0 0 auto;
}

.tooltip-text {
  visibility: hidden;
  width: 200px;
  background-color: var(--color-paper);
  color: var(--color-ink);
  text-align: center;
  border: var(--rule);
  border-radius: var(--radius-card);
  padding: var(--space-xs);

  /* Position the tooltip */
  position: absolute;
  z-index: 1;
  top: 100%;
  left: 50%;
  margin-left: -60px;
}

.tooltip-container:hover .tooltip-text {
  visibility: visible;
}

.tooltip-container:focus-within .tooltip-text {
  visibility: visible;
}

@media (max-width: 1080px) {
  div.brand strong {
    display: none;
  }
}

@media (max-width: 720px) {
  div#topbar {
    padding-inline: var(--space-2xs);
  }

  div.brand {
    display: none;
  }

  input.savePath {
    width: 10rem;
  }
}

header#topbar.app-command-bar {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1000;
  display: grid;
  grid-template-columns: auto minmax(10rem, 1fr) auto auto;
  align-items: center;
  gap: var(--space-xs);
  height: var(--topbar-height);
  width: 100%;
  min-width: 0;
  padding: var(--space-2xs) var(--space-sm);
  overflow: visible;
  border-bottom: var(--rule);
  background: var(--color-paper-glass);
  box-shadow: var(--shadow-topbar);
  backdrop-filter: blur(12px);
}

.app-brand {
  display: flex;
  align-items: center;
  gap: var(--space-2xs);
  color: var(--color-ink);
  text-decoration: none;
}

.app-brand img { border-radius: var(--radius-input); }
.app-brand span { display: flex; flex-direction: column; line-height: 1.05; }
.app-brand strong { font-size: var(--text-md); font-weight: 750; }
.app-brand small { color: var(--color-ink-2); font-size: .68rem; letter-spacing: .08em; text-transform: uppercase; }

.save-context {
  display: block;
  min-width: 0;
}

.save-context strong,
.save-context span { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.save-context strong { color: var(--color-ink); font-size: var(--text-xs); }
.save-context span { color: var(--color-ink-2); font-family: var(--font-mono); font-size: .68rem; }

header#topbar.app-command-bar input.savePath {
  width: 100%;
  min-width: 0;
  max-width: none;
  font-family: var(--font-mono);
  font-size: var(--text-xs);
}

.primary-actions { display: flex; align-items: center; gap: var(--space-3xs); }

header#topbar.app-command-bar button.op {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 2.35rem;
  padding-inline: var(--space-xs);
  font-size: var(--text-sm);
}

header#topbar.app-command-bar button.op.save { background: var(--color-accent); color: var(--color-accent-ink); font-weight: 750; }
header#topbar.app-command-bar button.op.quiet { background: transparent; }

.utility-menu { position: relative; }

.utility-menu summary {
  min-width: 4.5rem;
  padding: .45rem var(--space-xs);
  border: var(--rule);
  border-radius: var(--radius-input);
  background: var(--color-paper-3);
  color: var(--color-ink);
  cursor: pointer;
  list-style: none;
  text-align: center;
}

.utility-menu summary::-webkit-details-marker { display: none; }
.utility-menu[open] summary { border-color: var(--color-accent); }

.utility-popover {
  position: absolute;
  top: calc(100% + var(--space-2xs));
  right: 0;
  z-index: 1200;
  display: grid;
  gap: var(--space-3xs);
  width: 15rem;
  padding: var(--space-2xs);
  border: var(--rule);
  border-radius: var(--radius-card);
  background: var(--color-paper-2);
  box-shadow: var(--shadow-panel);
}

.utility-popover button.op { width: 100%; justify-content: flex-start; }
.utility-navigation { display: none !important; }
.language-control { min-width: 0; justify-self: end; grid-column: 4; }
.language-control select { min-width: 6.5rem; }

@media (max-width: 1050px) {
  header#topbar.app-command-bar { grid-template-columns: auto minmax(8rem, 1fr) auto auto; }
  .language-control { grid-column: 4; }
  .primary-actions .quiet, .save-context-label, .app-brand small { display: none; }
  .save-context { grid-template-columns: minmax(0, 1fr); }
}

@media (max-width: 700px) {
  header#topbar.app-command-bar { grid-template-columns: auto minmax(0, 1fr) auto auto; gap: var(--space-3xs); }
  .language-control { grid-column: 3; }
  .save-context, header#topbar.app-command-bar .primary-actions .op:not(.save), .app-brand span { display: none; }
  .primary-actions { justify-self: end; }
  .language-control { grid-column: 4; }
  .utility-navigation { display: flex !important; }
}

@media (max-width: 420px) {
  header#topbar.app-command-bar { grid-template-columns: auto auto 1fr; }
  .app-brand { display: none; }
  .language-control { grid-column: 3; }
  .language-control select { min-width: 5rem; }
  header#topbar.app-command-bar button.op { padding-inline: var(--space-2xs); font-size: .72rem; }
  .utility-menu summary { min-width: 4rem; padding-inline: var(--space-2xs); font-size: .75rem; }
}
</style>
