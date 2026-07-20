<script setup>
import PalList from '@/components/PalList.vue'
import PlayerList from '@/components/PlayerList.vue'
import PalEditor from '@/components/PalEditor.vue'
import PlayerEditor from '@/components/PlayerEditor.vue'
import InventoryEditor from '@/components/InventoryEditor.vue'
import { usePalEditorStore } from '@/stores/paleditor'
import { ref, watch } from 'vue'

const palStore = usePalEditorStore()
const workspace = ref('pals')

const showPlayer = section => {
  workspace.value = section
  palStore.SHOW_PLAYER_EDIT_FLAG = true
}

const showInventory = async () => {
  showPlayer('inventory')
  await Promise.all([palStore.loadItemCatalog(), palStore.fetchInventory()])
}

const showPals = () => {
  workspace.value = 'pals'
  if (palStore.SELECTED_PAL_ID) palStore.SHOW_PLAYER_EDIT_FLAG = false
}

watch(() => palStore.SELECTED_PAL_ID, value => {
  if (value && !palStore.SHOW_PLAYER_EDIT_FLAG) workspace.value = 'pals'
})

watch(() => palStore.SHOW_PLAYER_EDIT_FLAG, value => {
  if (value && workspace.value === 'pals') workspace.value = 'player'
})
</script>

<template>
  <div id="EditorDiv">
    <aside class="entity-sidebar">
      <nav class="workspace-nav" aria-label="Editor destinations">
        <button aria-label="Pal box" :class="{ active: workspace === 'pals' }" @click="showPals">
          <span>P</span>Pal box
        </button>
        <button aria-label="Player" :class="{ active: workspace === 'player' }" @click="showPlayer('player')">
          <span>U</span>Player
        </button>
        <button aria-label="Technology" :class="{ active: workspace === 'technology' }" @click="showPlayer('technology')">
          <span>T</span>Technology
        </button>
        <button aria-label="Inventory" :class="{ active: workspace === 'inventory' }" @click="showInventory">
          <span>I</span>Inventory
        </button>
      </nav>

      <section class="selector owners-selector">
        <PlayerList />
      </section>
      <section class="selector pals-selector" v-if="palStore.SELECTED_PLAYER_ID || palStore.BASE_PAL_BTN_CLK_FLAG">
        <PalList />
      </section>
      <a class="sidebar-github" href="https://github.com/Guineabear/Palworld-Pal-Editor" target="_blank"
        rel="noopener noreferrer">GitHub project <span>↗</span></a>
    </aside>

    <main class="editor-canvas">
      <PlayerEditor v-if="workspace === 'player' && palStore.SELECTED_PLAYER_DATA" section="profile" />
      <PlayerEditor v-else-if="workspace === 'technology' && palStore.SELECTED_PLAYER_DATA" section="technology" />
      <InventoryEditor v-else-if="workspace === 'inventory' && palStore.SELECTED_PLAYER_DATA" />
      <PalEditor v-else-if="palStore.SELECTED_PAL_ID && palStore.SELECTED_PAL_DATA" />
      <section v-else class="empty-editor">
        <strong>Select a Pal to begin</strong>
        <span>Choose an owner and Pal from the sidebar.</span>
      </section>
    </main>
  </div>
</template>

<style scoped>
#EditorDiv {
  display: grid;
  grid-template-columns: var(--sidebar-entity) minmax(0, 1fr);
  min-width: 0;
  min-height: 100dvh;
  padding-top: var(--topbar-height);
  background: var(--color-paper);
}

.entity-sidebar {
  position: fixed;
  inset: var(--topbar-height) auto 0 0;
  z-index: 30;
  width: var(--sidebar-entity);
  display: grid;
  grid-template-rows: auto minmax(7rem, .35fr) minmax(10rem, 1fr) auto;
  gap: var(--space-2xs);
  padding: var(--space-xs);
  border-right: var(--rule);
  background: var(--color-paper-2);
}

.workspace-nav {
  display: grid;
  gap: var(--space-3xs);
  padding-bottom: var(--space-2xs);
  border-bottom: var(--rule);
}

.workspace-nav button {
  min-height: 2.6rem;
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  border: 1px solid transparent;
  border-radius: var(--radius-input);
  padding: 0 var(--space-xs);
  background: transparent;
  color: var(--color-ink-2);
  text-align: left;
  white-space: nowrap;
  cursor: pointer;
}

.workspace-nav button span {
  display: grid;
  width: 1.5rem;
  place-items: center;
  color: var(--color-accent);
  font-family: var(--font-mono);
  font-weight: 750;
}

.workspace-nav button:hover { background: var(--color-paper-3); color: var(--color-ink); }
.workspace-nav button.active { border-color: var(--color-accent-strong); background: var(--color-accent-soft); color: var(--color-ink); }

.selector { min-width: 0; min-height: 0; overflow: hidden; }
.sidebar-github {
  display: flex;
  justify-content: space-between;
  padding: var(--space-xs);
  border-radius: var(--radius-input);
  color: var(--color-ink-2);
  text-decoration: none;
}
.sidebar-github:hover { background: var(--color-paper-3); color: var(--color-ink); }

.editor-canvas {
  grid-column: 2;
  min-width: 0;
  min-height: calc(100dvh - var(--topbar-height));
  padding: var(--space-sm);
}

.empty-editor {
  min-height: 20rem;
  display: grid;
  place-content: center;
  border: 1px dashed var(--color-rule);
  border-radius: var(--radius-panel);
  color: var(--color-ink-2);
  text-align: center;
}
.empty-editor strong { color: var(--color-ink); font-size: var(--text-lg); }
.empty-editor span { margin-top: var(--space-3xs); }

@media (max-width: 900px) {
  #EditorDiv { grid-template-columns: minmax(0, 1fr); }
  .entity-sidebar {
    position: static;
    width: auto;
    grid-template-rows: auto auto auto;
    border-right: 0;
    border-bottom: var(--rule);
  }
  .workspace-nav { grid-template-columns: repeat(4, minmax(0, 1fr)); }
  .workspace-nav button { justify-content: center; }
  .owners-selector, .pals-selector { max-height: 13rem; }
  .sidebar-github { display: none; }
  .editor-canvas { grid-column: 1; padding: var(--space-2xs); }
}

@media (max-width: 420px) {
  .workspace-nav button span { display: none; }
  .workspace-nav button { padding-inline: var(--space-2xs); font-size: var(--text-xs); }
}
</style>
