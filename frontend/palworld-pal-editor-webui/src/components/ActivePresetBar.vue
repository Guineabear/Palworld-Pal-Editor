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

const selectedPreset = computed(() => palStore.ACTIVE_PRESETS.find(preset => preset.id === selectedId.value))
const skillLabel = skill => palStore.ACTIVE_SKILLS[skill]?.I18n?.[0] || skill
const equippedCount = computed(() => palStore.SELECTED_PAL_DATA.EquipWaza?.length || 0)
const learnedCount = computed(() => new Set([
  ...(palStore.SELECTED_PAL_DATA.MasteredWaza || []),
  ...(palStore.SELECTED_PAL_DATA.EquipWaza || []),
]).size)

function clearFeedback() { status.value = ''; error.value = '' }

async function saveCurrent() {
  clearFeedback()
  try {
    const saved = await palStore.createActivePreset(presetName.value)
    selectedId.value = saved.id
    presetName.value = ''
    status.value = `Saved “${saved.name}” with ${saved.equipped.length} equipped and ${saved.learned.length} learned skills.`
  } catch (reason) { error.value = reason.message }
}

async function applySelected() {
  clearFeedback()
  if (!selectedPreset.value) return
  const applied = await palStore.applyActivePreset(selectedPreset.value)
  if (applied) status.value = `Applied “${selectedPreset.value.name}” to this Pal.`
  else error.value = 'The active preset could not be applied to this Pal.'
}

function startRename(preset) { editingId.value = preset.id; editingName.value = preset.name }

async function finishRename(preset) {
  clearFeedback()
  try {
    await palStore.renameActivePreset(preset.id, editingName.value)
    editingId.value = ''
    status.value = 'Active preset renamed.'
  } catch (reason) { error.value = reason.message }
}

async function removePreset(preset) {
  if (!window.confirm(`Delete the “${preset.name}” active preset?`)) return
  clearFeedback()
  try {
    await palStore.deleteActivePreset(preset.id)
    if (selectedId.value === preset.id) selectedId.value = ''
    status.value = 'Active preset deleted.'
  } catch (reason) { error.value = reason.message }
}

async function importFile(event) {
  const file = event.target.files?.[0]
  if (!file) return
  clearFeedback()
  try {
    await palStore.importActivePresets(JSON.parse(await file.text()))
    status.value = 'Active presets imported. Matching names were updated.'
  } catch (reason) { error.value = reason.message || 'That file could not be imported.' }
  finally { event.target.value = '' }
}

onMounted(() => palStore.loadActivePresets())
</script>

<template>
  <section class="active-preset-workbench" aria-labelledby="active-preset-heading">
    <div class="heading-row">
      <div>
        <span class="kicker">Reusable combat loadouts</span>
        <h3 id="active-preset-heading">Active skill presets</h3>
        <p>Save equipped and learned attacks together, then reuse the full loadout on another Pal.</p>
      </div>
      <button class="quiet" type="button" @click="showManager = !showManager">{{ showManager ? 'Done' : 'Manage' }}</button>
    </div>

    <div class="apply-row">
      <label>
        <span>Preset</span>
        <select v-model="selectedId" :disabled="palStore.ACTIVE_PRESETS_LOADING || !palStore.ACTIVE_PRESETS.length">
          <option value="">{{ palStore.ACTIVE_PRESETS.length ? 'Choose a combat preset' : 'No active presets saved yet' }}</option>
          <option v-for="preset in palStore.ACTIVE_PRESETS" :key="preset.id" :value="preset.id">
            {{ preset.name }} · {{ preset.equipped.length }} equipped
          </option>
        </select>
      </label>
      <button class="primary" type="button" :disabled="!selectedPreset || palStore.LOADING_FLAG" @click="applySelected">Apply to this Pal</button>
    </div>

    <div v-if="selectedPreset" class="loadout-preview" aria-live="polite">
      <div>
        <strong>Equipped</strong>
        <span v-for="skill in selectedPreset.equipped" :key="`equipped-${skill}`">{{ skillLabel(skill) }}</span>
        <em v-if="!selectedPreset.equipped.length">None</em>
      </div>
      <div>
        <strong>Learned</strong>
        <span>{{ selectedPreset.learned.length }} skills</span>
      </div>
    </div>

    <form class="save-row" @submit.prevent="saveCurrent">
      <label>
        <span>New preset name</span>
        <input v-model.trim="presetName" maxlength="60" placeholder="Example: Dragon Burst" required>
      </label>
      <button type="submit" :disabled="!presetName || palStore.ACTIVE_PRESETS_LOADING">
        Save {{ equippedCount }} equipped + {{ learnedCount }} learned
      </button>
    </form>

    <div v-if="showManager" class="manager">
      <div class="manager-toolbar">
        <strong>Saved active presets</strong>
        <div>
          <button type="button" @click="palStore.exportActivePresets" :disabled="!palStore.ACTIVE_PRESETS.length">Export</button>
          <button type="button" @click="fileInput.click()">Import</button>
          <input ref="fileInput" class="visually-hidden" type="file" accept="application/json,.json" @change="importFile">
        </div>
      </div>
      <ul v-if="palStore.ACTIVE_PRESETS.length">
        <li v-for="preset in palStore.ACTIVE_PRESETS" :key="preset.id">
          <div>
            <input v-if="editingId === preset.id" v-model.trim="editingName" maxlength="60" aria-label="Active preset name">
            <strong v-else>{{ preset.name }}</strong>
            <span>{{ preset.equipped.length }} equipped · {{ preset.learned.length }} learned</span>
          </div>
          <div class="row-actions">
            <button v-if="editingId === preset.id" type="button" @click="finishRename(preset)">Save</button>
            <button v-else type="button" @click="startRename(preset)">Rename</button>
            <button class="danger" type="button" @click="removePreset(preset)">Delete</button>
          </div>
        </li>
      </ul>
      <p v-else class="empty">Your active presets will appear here.</p>
      <p class="storage-note">Stored in your Paldeck app data, so future editor updates will not remove them.</p>
    </div>

    <p v-if="status" class="status" role="status">{{ status }}</p>
    <p v-if="error" class="error" role="alert">{{ error }}</p>
  </section>
</template>

<style scoped>
/* Hallmark · component: preset workbench · genre: modern-minimal · theme: Paldeck
 * states: default · hover · focus · active · disabled · loading · error · success
 * contrast: pass
 */
.active-preset-workbench { width: 100%; margin: 0 0 var(--space-sm); padding: var(--space-sm); border: 1px solid var(--color-rule-soft); border-radius: var(--radius-card); background: linear-gradient(135deg, var(--color-paper-3), var(--color-paper-2)); }
.heading-row, .manager-toolbar, .apply-row, .save-row, .manager li { display: flex; align-items: center; justify-content: space-between; gap: var(--space-sm); }
.heading-row h3 { margin: .15rem 0; color: var(--color-ink); font-size: var(--text-lg); font-style: normal; }
.heading-row p, .storage-note, .empty { margin: 0; color: var(--color-ink-2); font-size: var(--text-xs); }
.kicker { color: var(--color-accent); font-size: var(--text-xs); font-weight: 750; letter-spacing: .08em; text-transform: uppercase; }
.apply-row, .save-row { margin-top: var(--space-sm); align-items: end; }
label { display: grid; min-width: 0; flex: 1; gap: var(--space-3xs); color: var(--color-ink-2); font-size: var(--text-xs); }
select, input, button { min-height: 2.5rem; border: var(--rule); border-radius: var(--radius-input); padding: 0 var(--space-xs); background: var(--color-paper); color: var(--color-ink); }
button { cursor: pointer; font-weight: 700; }
button:hover:not(:disabled) { border-color: var(--color-accent); }
button:focus-visible, select:focus-visible, input:focus-visible { outline: 2px solid var(--color-focus); outline-offset: 2px; }
button:active:not(:disabled) { transform: translateY(1px); }
button:disabled { cursor: not-allowed; opacity: .5; }
.primary { border-color: var(--color-accent); background: var(--color-accent); color: var(--color-accent-ink); }
.quiet { flex: 0 0 auto; background: transparent; }
.loadout-preview { display: grid; gap: var(--space-2xs); margin-top: var(--space-xs); }
.loadout-preview > div { display: flex; flex-wrap: wrap; align-items: center; gap: var(--space-3xs); }
.loadout-preview strong { width: 5rem; color: var(--color-ink-2); font-size: var(--text-xs); }
.loadout-preview span { padding: .3rem .55rem; border: 1px solid var(--color-rule-soft); border-radius: var(--radius-pill); background: var(--color-paper); color: var(--color-ink); font-size: var(--text-xs); }
.loadout-preview em { color: var(--color-ink-2); font-size: var(--text-xs); }
.manager { margin-top: var(--space-sm); padding-top: var(--space-sm); border-top: 1px solid var(--color-rule-soft); }
.manager-toolbar > div, .row-actions { display: flex; gap: var(--space-3xs); }
.manager ul { display: grid; gap: var(--space-3xs); margin: var(--space-xs) 0; padding: 0; list-style: none; }
.manager li { padding: var(--space-xs); border-radius: var(--radius-input); background: var(--color-paper); }
.manager li > div:first-child { display: grid; min-width: 0; gap: .1rem; }
.manager li span { color: var(--color-ink-2); font-size: var(--text-xs); }
.danger { color: var(--color-danger); }
.storage-note { margin-top: var(--space-xs); }
.status, .error { margin: var(--space-xs) 0 0; padding: var(--space-xs); border-radius: var(--radius-input); font-size: var(--text-xs); }
.status { background: var(--color-success-soft); color: var(--color-success); }
.error { background: var(--color-danger-soft); color: var(--color-danger); }
.visually-hidden { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
@media (max-width: 700px) { .heading-row, .apply-row, .save-row, .manager li { align-items: stretch; flex-direction: column; } .quiet { align-self: flex-start; } .apply-row button, .save-row button { width: 100%; } .row-actions { width: 100%; } .row-actions button { flex: 1; } }
</style>
