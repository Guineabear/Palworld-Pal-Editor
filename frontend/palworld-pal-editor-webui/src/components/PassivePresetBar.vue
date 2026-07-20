<script setup>
import { computed, onMounted, ref } from 'vue'
import { usePalEditorStore } from '@/stores/paleditor'

const palStore = usePalEditorStore()
const selectedId = ref('')
const presetName = ref('')
const editingId = ref('')
const editingName = ref('')
const showManager = ref(false)
const status = ref('')
const error = ref('')
const fileInput = ref(null)

const selectedPreset = computed(() =>
  palStore.PASSIVE_PRESETS.find(preset => preset.id === selectedId.value)
)

const skillLabel = skill => palStore.PASSIVE_SKILLS[skill]?.I18n?.[0] || skill

function clearFeedback() {
  status.value = ''
  error.value = ''
}

async function saveCurrent() {
  clearFeedback()
  try {
    const saved = await palStore.createPassivePreset(presetName.value)
    selectedId.value = saved.id
    presetName.value = ''
    status.value = `Saved “${saved.name}” with ${saved.skills.length} skills.`
  } catch (reason) {
    error.value = reason.message
  }
}

async function applySelected() {
  clearFeedback()
  if (!selectedPreset.value) return
  if (selectedPreset.value.skills.length > 6 && palStore.HIDE_INVALID_OPTIONS) {
    error.value = 'Enable Advanced Editing to apply a preset with more than 6 passive skills.'
    return
  }
  const applied = await palStore.applyPassivePreset(selectedPreset.value)
  if (applied) status.value = `Applied “${selectedPreset.value.name}” to this Pal.`
  else error.value = 'The preset could not be applied to this Pal.'
}

function startRename(preset) {
  editingId.value = preset.id
  editingName.value = preset.name
}

async function finishRename(preset) {
  clearFeedback()
  try {
    await palStore.renamePassivePreset(preset.id, editingName.value)
    editingId.value = ''
    status.value = 'Preset renamed.'
  } catch (reason) {
    error.value = reason.message
  }
}

async function removePreset(preset) {
  if (!window.confirm(`Delete the “${preset.name}” preset?`)) return
  clearFeedback()
  try {
    await palStore.deletePassivePreset(preset.id)
    if (selectedId.value === preset.id) selectedId.value = ''
    status.value = 'Preset deleted.'
  } catch (reason) {
    error.value = reason.message
  }
}

async function importFile(event) {
  const file = event.target.files?.[0]
  if (!file) return
  clearFeedback()
  try {
    const document = JSON.parse(await file.text())
    await palStore.importPassivePresets(document)
    status.value = 'Presets imported. Matching names were updated.'
  } catch (reason) {
    error.value = reason.message || 'That file could not be imported.'
  } finally {
    event.target.value = ''
  }
}

onMounted(() => palStore.loadPassivePresets())
</script>

<template>
  <section class="preset-workbench" aria-labelledby="preset-heading">
    <div class="preset-heading-row">
      <div>
        <span class="preset-kicker">Reusable loadouts</span>
        <h3 id="preset-heading">Passive presets</h3>
        <p>Save this Pal’s passive skills once, then apply them to any other Pal.</p>
      </div>
      <button class="quiet-button" type="button" @click="showManager = !showManager">
        {{ showManager ? 'Done' : 'Manage' }}
      </button>
    </div>

    <div class="preset-apply-row">
      <label>
        <span>Preset</span>
        <select v-model="selectedId" :disabled="palStore.PASSIVE_PRESETS_LOADING || !palStore.PASSIVE_PRESETS.length">
          <option value="">{{ palStore.PASSIVE_PRESETS.length ? 'Choose a preset' : 'No presets saved yet' }}</option>
          <option v-for="preset in palStore.PASSIVE_PRESETS" :key="preset.id" :value="preset.id">
            {{ preset.name }} · {{ preset.skills.length }} skills
          </option>
        </select>
      </label>
      <button class="primary-button" type="button" :disabled="!selectedPreset || palStore.LOADING_FLAG" @click="applySelected">
        Apply to this Pal
      </button>
    </div>

    <div v-if="selectedPreset" class="preset-preview" aria-live="polite">
      <span v-for="skill in selectedPreset.skills" :key="skill">{{ skillLabel(skill) }}</span>
      <em v-if="!selectedPreset.skills.length">No passive skills</em>
      <em v-else-if="selectedPreset.skills.length > 6">Advanced preset · enable Advanced Editing before applying</em>
    </div>

    <form class="preset-save-row" @submit.prevent="saveCurrent">
      <label>
        <span>New preset name</span>
        <input v-model.trim="presetName" maxlength="60" placeholder="Example: Base Worker" required>
      </label>
      <button type="submit" :disabled="!presetName || palStore.PASSIVE_PRESETS_LOADING">
        Save current {{ palStore.SELECTED_PAL_DATA.PassiveSkillList.length }} skills
      </button>
    </form>

    <div v-if="showManager" class="preset-manager">
      <div class="manager-toolbar">
        <strong>Saved presets</strong>
        <div>
          <button type="button" @click="palStore.exportPassivePresets" :disabled="!palStore.PASSIVE_PRESETS.length">Export</button>
          <button type="button" @click="fileInput.click()">Import</button>
          <input ref="fileInput" class="visually-hidden" type="file" accept="application/json,.json" @change="importFile">
        </div>
      </div>
      <ul v-if="palStore.PASSIVE_PRESETS.length">
        <li v-for="preset in palStore.PASSIVE_PRESETS" :key="preset.id">
          <div>
            <input v-if="editingId === preset.id" v-model.trim="editingName" maxlength="60" aria-label="Preset name">
            <strong v-else>{{ preset.name }}</strong>
            <span>{{ preset.skills.length }} skills{{ preset.skills.length > 6 ? ' · Advanced' : '' }}</span>
          </div>
          <div class="row-actions">
            <button v-if="editingId === preset.id" type="button" @click="finishRename(preset)">Save</button>
            <button v-else type="button" @click="startRename(preset)">Rename</button>
            <button class="danger-button" type="button" @click="removePreset(preset)">Delete</button>
          </div>
        </li>
      </ul>
      <p v-else class="empty-presets">Your saved presets will appear here.</p>
      <p class="storage-note">Stored in your Paldeck app data, so installing a future update will not remove them.</p>
    </div>

    <p v-if="status" class="preset-status" role="status">{{ status }}</p>
    <p v-if="error" class="preset-error" role="alert">{{ error }}</p>
  </section>
</template>

<style scoped>
.preset-workbench { width: 100%; margin: var(--space-xs) 0 var(--space-sm); padding: var(--space-sm); border: 1px solid var(--color-rule-soft); border-radius: var(--radius-card); background: linear-gradient(135deg, var(--color-paper-3), var(--color-paper-2)); }
.preset-heading-row, .manager-toolbar, .preset-apply-row, .preset-save-row, .preset-manager li { display: flex; align-items: center; justify-content: space-between; gap: var(--space-sm); }
.preset-heading-row h3 { margin: .15rem 0; color: var(--color-ink); font-size: var(--text-lg); }
.preset-heading-row p, .storage-note, .empty-presets { margin: 0; color: var(--color-ink-2); font-size: var(--text-xs); }
.preset-kicker { color: var(--color-accent); font-size: var(--text-xs); font-weight: 750; letter-spacing: .08em; text-transform: uppercase; }
.preset-apply-row, .preset-save-row { margin-top: var(--space-sm); align-items: end; }
label { display: grid; min-width: 0; flex: 1; gap: var(--space-3xs); color: var(--color-ink-2); font-size: var(--text-xs); }
select, input, button { min-height: 2.5rem; border: var(--rule); border-radius: var(--radius-input); padding: 0 var(--space-xs); background: var(--color-paper); color: var(--color-ink); }
button { cursor: pointer; font-weight: 700; }
button:hover:not(:disabled) { border-color: var(--color-accent); }
button:disabled { cursor: not-allowed; opacity: .5; }
.primary-button { border-color: var(--color-accent); background: var(--color-accent); color: var(--color-accent-ink); }
.quiet-button { flex: 0 0 auto; background: transparent; }
.preset-preview { display: flex; flex-wrap: wrap; gap: var(--space-3xs); margin-top: var(--space-xs); }
.preset-preview span { padding: .3rem .55rem; border: 1px solid var(--color-preset-chip-border); border-radius: var(--radius-pill); background: var(--color-preset-chip); color: var(--color-ink); font-size: var(--text-xs); }
.preset-preview em { color: var(--color-ink-2); font-size: var(--text-xs); }
.preset-manager { margin-top: var(--space-sm); padding-top: var(--space-sm); border-top: 1px solid var(--color-rule-soft); }
.manager-toolbar > div, .row-actions { display: flex; gap: var(--space-3xs); }
.preset-manager ul { display: grid; gap: var(--space-3xs); margin: var(--space-xs) 0; padding: 0; list-style: none; }
.preset-manager li { padding: var(--space-xs); border-radius: var(--radius-input); background: var(--color-paper); }
.preset-manager li > div:first-child { display: grid; min-width: 0; gap: .1rem; }
.preset-manager li span { color: var(--color-ink-2); font-size: var(--text-xs); }
.danger-button { color: var(--color-danger); }
.storage-note { margin-top: var(--space-xs); }
.preset-status, .preset-error { margin: var(--space-xs) 0 0; padding: var(--space-xs); border-radius: var(--radius-input); font-size: var(--text-xs); }
.preset-status { background: var(--color-success-soft); color: var(--color-success); }
.preset-error { background: var(--color-preset-error); color: var(--color-danger); }
.visually-hidden { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
@media (max-width: 700px) { .preset-heading-row, .preset-apply-row, .preset-save-row, .preset-manager li { align-items: stretch; flex-direction: column; } .quiet-button { align-self: flex-start; } .preset-apply-row button, .preset-save-row button { width: 100%; } .row-actions { width: 100%; } .row-actions button { flex: 1; } }
</style>
