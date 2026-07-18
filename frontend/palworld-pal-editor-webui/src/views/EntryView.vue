<script setup>
import { usePalEditorStore } from '@/stores/paleditor'
import PathPicker from '@/components/PathPicker.vue'
import { onMounted } from 'vue'

const palStore = usePalEditorStore()

onMounted(() => {
  palStore.get_updates()
})
</script>

<template>
  <main class="open-save-screen">
    <PathPicker />

    <header class="open-save-header">
      <a class="launch-brand" href="https://github.com/Guineabear/Palworld-Pal-Editor" target="_blank"
        rel="noopener noreferrer" aria-label="Paldeck on GitHub">
        <img src="@/assets/logo.ico" alt="" width="38" height="38">
        <span><strong>Paldeck</strong><small>Pal Editor</small></span>
      </a>
      <a class="github-link" href="https://github.com/Guineabear/Palworld-Pal-Editor" target="_blank"
        rel="noopener noreferrer">GitHub project ↗</a>
    </header>

    <section class="open-save-content">
      <div class="open-save-copy">
        <p class="compatibility">Palworld 1.0 compatible</p>
        <p>Choose the folder containing <code>Level.sav</code>. Paldeck keeps the editing workflow local and leaves your sign-in details alone.</p>
      </div>

      <div class="open-save-panel">
        <div class="open-save-primary">
          <div>
            <strong>Open Level.sav</strong>
            <span>Choose the save folder, then open it in the editor.</span>
          </div>
          <button class="choose-save" @click="palStore.show_file_picker" :disabled="palStore.LOADING_FLAG">
            Choose save
          </button>
        </div>

        <div class="selected-path">
          <span>Selected folder</span>
          <code>{{ palStore.PAL_GAME_SAVE_PATH || 'No folder selected' }}</code>
          <input id="save-folder" type="text" v-model="palStore.PAL_GAME_SAVE_PATH"
            placeholder="C:\Users\...\Pal\Saved\SaveGames\..." :disabled="palStore.LOADING_FLAG">
          <button class="open-editor" @click="palStore.loadSave"
            :disabled="palStore.LOADING_FLAG || !palStore.PAL_GAME_SAVE_PATH">
            {{ palStore.getTranslatedText('EntryView_BTN_Load') }}
          </button>
        </div>

        <div class="safety-line">
          <strong>Before editing</strong>
          <span>Stop the game or server and keep a backup of the save folder.</span>
        </div>
      </div>

      <div class="recent-save" v-if="palStore.PAL_GAME_SAVE_PATH">
        <span>Recent save</span>
        <button @click="palStore.loadSave" :disabled="palStore.LOADING_FLAG">
          <span><strong>Last selected world</strong><code>{{ palStore.PAL_GAME_SAVE_PATH }}</code></span>
          <b>Open →</b>
        </button>
      </div>
    </section>

    <footer class="open-save-footer">
      <span>Version {{ palStore.VERSION }}</span>
      <span>Back up before every edit</span>
      <span v-if="!palStore.IS_OFFICIAL_BUILD" class="build-warning">{{ palStore.getTranslatedText('EntryView_Version_Warning') }}</span>
      <a v-if="palStore.IS_OFFICIAL_BUILD && palStore.UPDATE_DATA.version" :href="palStore.UPDATE_DATA.download_gh"
        target="_blank" rel="noopener noreferrer">Update {{ palStore.UPDATE_DATA.version }} available</a>
    </footer>
  </main>
</template>

<style scoped>
.open-save-screen {
  min-height: 100dvh;
  display: grid;
  grid-template-rows: auto 1fr auto;
  background: var(--color-paper);
}

.open-save-header,
.open-save-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-sm);
  padding: var(--space-sm) clamp(var(--space-sm), 4vw, var(--space-xl));
}

.launch-brand {
  display: flex;
  align-items: center;
  gap: var(--space-2xs);
  color: var(--color-ink);
  text-decoration: none;
}

.launch-brand img { border-radius: var(--radius-input); }
.launch-brand span { display: flex; flex-direction: column; line-height: 1.05; }
.launch-brand strong { font-size: var(--text-lg); }
.launch-brand small { color: var(--color-ink-2); font-size: var(--text-xs); letter-spacing: .08em; text-transform: uppercase; }
.github-link { color: var(--color-ink-2); text-decoration: none; }
.github-link:hover { color: var(--color-accent); }

.open-save-content {
  width: min(48rem, calc(100% - 2rem));
  margin: auto;
  padding-block: var(--space-lg) var(--space-xl);
}

.compatibility {
  margin: 0 0 var(--space-xs);
  color: var(--color-accent);
  font-size: var(--text-xs);
  font-weight: 750;
  letter-spacing: .08em;
  text-transform: uppercase;
}

.open-save-copy > p:last-child {
  max-width: 39rem;
  margin: var(--space-md) 0 var(--space-lg);
  color: var(--color-ink-2);
  font-size: var(--text-lg);
  line-height: 1.55;
}

.open-save-copy code,
.selected-path code,
.recent-save code { font-family: var(--font-mono); }

.open-save-panel {
  border: var(--rule);
  border-radius: var(--radius-panel);
  background: var(--color-paper-2);
  box-shadow: var(--shadow-panel);
  overflow: clip;
}

.open-save-primary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-md);
  padding: var(--space-md);
  border-bottom: var(--rule);
  background: var(--color-accent-soft);
}

.open-save-primary strong,
.open-save-primary span { display: block; }
.open-save-primary strong { color: var(--color-ink); font-size: var(--text-lg); }
.open-save-primary span { margin-top: var(--space-3xs); color: var(--color-ink-2); }

button {
  min-height: 2.75rem;
  border: 1px solid var(--color-rule);
  border-radius: var(--radius-input);
  padding: 0 var(--space-sm);
  color: var(--color-ink);
  background: var(--color-paper-3);
  font-weight: 700;
  white-space: nowrap;
  cursor: pointer;
  transition: transform var(--dur-short) var(--ease-out), background-color var(--dur-short) var(--ease-out);
}

button:hover { transform: translateY(-1px); }
button:active { transform: translateY(0); }
button:disabled { opacity: .55; cursor: not-allowed; transform: none; }

.choose-save,
.open-editor { border-color: var(--color-accent); background: var(--color-accent); color: var(--color-accent-ink); }

.selected-path {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: var(--space-2xs);
  padding: var(--space-md);
}

.selected-path > span { grid-column: 1 / -1; color: var(--color-ink-2); font-size: var(--text-xs); font-weight: 700; }
.selected-path > code { grid-column: 1 / -1; overflow-wrap: anywhere; color: var(--color-ink-2); font-size: var(--text-xs); }
.selected-path input {
  min-width: 0;
  min-height: 2.75rem;
  border: var(--rule);
  border-radius: var(--radius-input);
  padding: 0 var(--space-xs);
  background: var(--color-paper);
  color: var(--color-ink);
  font-family: var(--font-mono);
}

.safety-line {
  display: flex;
  gap: var(--space-xs);
  padding: var(--space-xs) var(--space-md);
  border-top: var(--rule);
  color: var(--color-ink-2);
  font-size: var(--text-xs);
}
.safety-line strong { color: var(--color-warning); }

.recent-save { margin-top: var(--space-lg); }
.recent-save > span { color: var(--color-ink-2); font-size: var(--text-xs); font-weight: 700; }
.recent-save > button {
  width: 100%;
  min-height: 4.25rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-sm);
  margin-top: var(--space-2xs);
  background: transparent;
  text-align: left;
}
.recent-save button span { min-width: 0; }
.recent-save button strong,
.recent-save button code { display: block; }
.recent-save button code { margin-top: var(--space-3xs); overflow: hidden; color: var(--color-ink-2); font-size: var(--text-xs); text-overflow: ellipsis; white-space: nowrap; }

.open-save-footer { color: var(--color-ink-2); font-size: var(--text-xs); }
.open-save-footer a { color: var(--color-accent); }
.build-warning { color: var(--color-warning); }

@media (max-width: 620px) {
  .open-save-primary,
  .safety-line { align-items: stretch; flex-direction: column; }
  .choose-save { width: 100%; }
  .selected-path { grid-template-columns: minmax(0, 1fr); }
  .open-editor { width: 100%; }
  .open-save-footer { align-items: flex-start; flex-direction: column; }
}

@media (max-width: 420px) {
  .github-link { display: none; }
}
</style>
