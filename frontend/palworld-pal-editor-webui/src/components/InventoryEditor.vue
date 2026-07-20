<script setup>
import { computed, ref } from 'vue'
import { usePalEditorStore } from '@/stores/paleditor'

const palStore = usePalEditorStore()
const activeContainer = ref('common')
const itemQuery = ref('')
const groupFilter = ref('all')
const selectedItemId = ref('')
const addCount = ref(1)
const showAdvanced = ref(false)

const container = computed(() => palStore.PLAYER_INVENTORY.find(value => value.Key === activeContainer.value))
const catalogueById = computed(() => new Map(palStore.ITEM_CATALOG.map(item => [item.InternalName, item])))
const groups = computed(() => [...new Set(palStore.ITEM_CATALOG.filter(item => item.CanCreate).map(item => item.Group))].sort())
const filteredItems = computed(() => {
  const query = itemQuery.value.trim().toLowerCase()
  return palStore.ITEM_CATALOG.filter(item => {
    if (!showAdvanced.value && !item.CanCreate) return false
    if (groupFilter.value !== 'all' && item.Group !== groupFilter.value) return false
    return !query || `${item.Name} ${item.InternalName} ${item.Type}`.toLowerCase().includes(query)
  }).slice(0, 150)
})
const selectedItem = computed(() => catalogueById.value.get(selectedItemId.value))

const selectCatalogueItem = item => {
  if (!item.CanCreate) return
  selectedItemId.value = item.InternalName
  addCount.value = Math.min(Math.max(1, addCount.value), item.MaxStack)
}

const addItem = async () => {
  if (!selectedItem.value?.CanCreate) return
  if (await palStore.patchInventory({
    Action: 'add', Container: activeContainer.value,
    StaticId: selectedItemId.value, Count: Number(addCount.value)
  })) selectedItemId.value = ''
}

const saveCount = (slot, event) => palStore.patchInventory({
  Action: 'set_count', Container: activeContainer.value,
  SlotIndex: slot.SlotIndex, StaticId: slot.StaticId, Count: Number(event.target.value)
})

const removeItem = slot => palStore.patchInventory({
  Action: 'remove', Container: activeContainer.value, SlotIndex: slot.SlotIndex
})
</script>

<template>
  <div class="inventory-workspace">
    <header class="inventory-header">
      <div><span class="workspace-kicker">Player inventory</span><h1>{{ palStore.SELECTED_PLAYER_DATA.NickName }}</h1></div>
      <span class="safety-badge">Save-safe editing</span>
    </header>

    <div class="container-tabs" role="tablist" aria-label="Inventory sections">
      <button v-for="section in palStore.PLAYER_INVENTORY" :key="section.Key"
        :class="{ active: activeContainer === section.Key }" @click="activeContainer = section.Key">
        {{ section.Label }} <span>{{ section.Items.length }}/{{ section.Capacity }}</span>
      </button>
    </div>

    <p v-if="palStore.INVENTORY_ERROR" class="inventory-error">{{ palStore.INVENTORY_ERROR }}</p>
    <section class="inventory-layout" v-if="container">
      <div class="current-items">
        <div class="section-title"><div><span>Current contents</span><h2>{{ container.Label }}</h2></div><small>{{ container.Capacity - container.Items.length }} free slots</small></div>
        <div v-if="!container.Items.length" class="empty-state">This section is empty.</div>
        <article v-for="slot in container.Items" :key="slot.SlotIndex" class="inventory-row">
          <div class="slot-number">{{ slot.SlotIndex + 1 }}</div>
          <div class="item-copy">
            <strong>{{ catalogueById.get(slot.StaticId)?.Name || slot.StaticId }}</strong>
            <span>{{ slot.StaticId }}</span>
          </div>
          <span v-if="slot.Dynamic" class="linked-badge">Linked item</span>
          <input type="number" :value="slot.Count" min="1"
            :max="catalogueById.get(slot.StaticId)?.MaxStack || slot.Count"
            :disabled="slot.Dynamic || palStore.INVENTORY_LOADING" @change="saveCount(slot, $event)" aria-label="Item quantity">
          <button class="remove-button" :disabled="slot.Dynamic || palStore.INVENTORY_LOADING" @click="removeItem(slot)">Remove</button>
        </article>
      </div>

      <aside class="item-browser" v-if="activeContainer === 'common'">
        <div class="section-title"><div><span>Add an item</span><h2>Catalogue</h2></div></div>
        <div class="catalogue-controls">
          <input type="search" v-model="itemQuery" placeholder="Search items or internal names" aria-label="Search items">
          <select v-model="groupFilter" aria-label="Item group"><option value="all">All groups</option><option v-for="group in groups" :key="group">{{ group }}</option></select>
        </div>
        <label class="advanced-toggle"><input type="checkbox" v-model="showAdvanced"> Show protected and unreleased records</label>
        <div class="catalogue-list">
          <button v-for="item in filteredItems" :key="item.InternalName" :disabled="!item.CanCreate"
            :class="{ selected: selectedItemId === item.InternalName }" @click="selectCatalogueItem(item)">
            <span><strong>{{ item.Name }}</strong><small>{{ item.Group }} · stack {{ item.MaxStack }}</small></span>
            <em v-if="item.Dynamic">Linked</em><em v-else-if="item.Disabled">Unreleased</em>
          </button>
        </div>
        <div class="add-panel" v-if="selectedItem">
          <div><strong>{{ selectedItem.Name }}</strong><span>{{ selectedItem.Description || selectedItem.InternalName }}</span></div>
          <label>Quantity <input type="number" v-model.number="addCount" min="1" :max="selectedItem.MaxStack"></label>
          <button class="primary-action" @click="addItem" :disabled="palStore.INVENTORY_LOADING">Add to {{ container.Label }}</button>
        </div>
        <p class="inventory-note">Equipment marked “Linked” is visible but protected because Palworld stores its durability and rarity in a separate record.</p>
      </aside>
      <aside class="item-browser" v-else>
        <div class="section-title"><div><span>Protected section</span><h2>{{ container.Label }}</h2></div></div>
        <p class="inventory-note">New items are added to the main Bag. Palworld manages placement in this section, and linked equipment remains read-only to protect its companion records.</p>
        <button class="primary-action" @click="activeContainer = 'common'">Open Bag catalogue</button>
      </aside>
    </section>
    <div v-else-if="palStore.INVENTORY_LOADING" class="empty-state">Reading inventory…</div>
  </div>
</template>

<style scoped>
.inventory-workspace { min-width: 0; display: grid; gap: var(--space-xs); }
.inventory-header, .section-title { display: flex; align-items: center; justify-content: space-between; gap: var(--space-xs); }
.inventory-header { padding: var(--space-sm); border: var(--rule); border-radius: var(--radius-panel); background: var(--color-paper-2); }
.inventory-header h1, .section-title h2 { margin: 0; color: var(--color-ink); }
.workspace-kicker, .section-title span { color: var(--color-accent); font-size: var(--text-xs); font-weight: 750; letter-spacing: .08em; text-transform: uppercase; }
.safety-badge, .linked-badge { border: 1px solid var(--color-accent-strong); border-radius: 999px; padding: .3rem .55rem; color: var(--color-accent); font-size: var(--text-xs); }
.container-tabs { display: flex; gap: var(--space-3xs); overflow-x: auto; }
.container-tabs button { display: flex; gap: var(--space-xs); min-height: 2.6rem; border: var(--rule); border-radius: var(--radius-input); padding: 0 var(--space-xs); background: var(--color-paper-2); color: var(--color-ink-2); white-space: nowrap; cursor: pointer; }
.container-tabs button.active { border-color: var(--color-accent-strong); background: var(--color-accent-soft); color: var(--color-ink); }
.container-tabs span { color: var(--color-ink-3); }
.inventory-layout { display: grid; grid-template-columns: minmax(28rem, 1.25fr) minmax(22rem, .75fr); gap: var(--space-xs); align-items: start; }
.current-items, .item-browser { min-width: 0; display: grid; gap: var(--space-xs); padding: var(--space-sm); border: var(--rule); border-radius: var(--radius-panel); background: var(--color-paper-2); }
.inventory-row { display: grid; grid-template-columns: 2.2rem minmax(0, 1fr) auto 6rem auto; align-items: center; gap: var(--space-xs); min-height: 3.5rem; border-top: var(--rule); }
.slot-number { color: var(--color-ink-3); font-family: var(--font-mono); }
.item-copy { min-width: 0; display: grid; }
.item-copy span, .catalogue-list small, .add-panel span, .inventory-note { color: var(--color-ink-3); font-size: var(--text-xs); overflow-wrap: anywhere; }
input, select { min-height: 2.5rem; border: var(--rule); border-radius: var(--radius-input); padding: 0 var(--space-xs); background: var(--color-paper); color: var(--color-ink); }
.inventory-row input { width: 6rem; }
button { font: inherit; }
.remove-button { border: var(--rule); border-radius: var(--radius-input); padding: .55rem .75rem; background: transparent; color: var(--color-ink-2); cursor: pointer; }
button:disabled { opacity: .45; cursor: not-allowed; }
.catalogue-controls { display: grid; grid-template-columns: 1fr 9rem; gap: var(--space-3xs); }
.advanced-toggle { display: flex; align-items: center; gap: var(--space-3xs); color: var(--color-ink-2); font-size: var(--text-sm); }
.catalogue-list { max-height: 27rem; overflow: auto; display: grid; gap: 2px; }
.catalogue-list button { display: flex; justify-content: space-between; gap: var(--space-xs); border: 1px solid transparent; border-radius: var(--radius-input); padding: .65rem; background: var(--color-paper); color: var(--color-ink); text-align: left; cursor: pointer; }
.catalogue-list button:hover, .catalogue-list button.selected { border-color: var(--color-accent-strong); background: var(--color-accent-soft); }
.catalogue-list button span { display: grid; }
.catalogue-list em { color: var(--color-ink-3); font-size: var(--text-xs); font-style: normal; }
.add-panel { display: grid; gap: var(--space-xs); padding-top: var(--space-xs); border-top: var(--rule); }
.add-panel > div { display: grid; }
.add-panel label { display: flex; align-items: center; justify-content: space-between; }
.primary-action { min-height: 2.7rem; border: 0; border-radius: var(--radius-input); padding: 0 var(--space-xs); background: var(--color-accent); color: var(--color-paper); font-weight: 750; cursor: pointer; }
.inventory-note, .inventory-error, .empty-state { margin: 0; padding: var(--space-xs); border-radius: var(--radius-input); background: var(--color-paper-3); }
.inventory-error { color: var(--color-danger); }
@media (max-width: 1050px) { .inventory-layout { grid-template-columns: 1fr; } }
@media (max-width: 650px) { .inventory-row { grid-template-columns: 2rem 1fr auto; } .linked-badge { grid-column: 2; } .inventory-row input, .remove-button { grid-row: 2; } .catalogue-controls { grid-template-columns: 1fr; } }
</style>
