<script setup>
import { usePalEditorStore } from '@/stores/paleditor'
import { ref, computed, reactive, onMounted, nextTick } from "vue";
const palStore = usePalEditorStore()
const playerListContainer = ref(null);
onMounted(async () => {
  await nextTick(); // Wait for the DOM to update with the dynamic buttons
  const buttons = playerListContainer.value.querySelectorAll('button:not(:disabled)');
  if (buttons.length > 0) {
    buttons[0].click(); // Simulate a click on the first enabled button
  }
});
</script>

<template>
  <div class="flex">
    <div class="title">
      <div class="rail-title">
        <span>Owners</span>
        <strong>{{ palStore.getTranslatedText("PlayerList_Text") }}</strong>
      </div>
      <span class="rail-count">{{ palStore.PLAYER_MAP.size }}</span>
      <div class="tooltip-container">
        <button class="playerSettings"
          v-if="palStore.SELECTED_PLAYER_ID != null && !palStore.PLAYER_MAP.get(palStore.SELECTED_PLAYER_ID).HasViewingCage"
          :title="palStore.getTranslatedText('PlayerList_Viewing_Cage')" :disabled="palStore.LOADING_FLAG"
          @click="palStore.updatePlayer" name="unlock_viewing_cage">🧊</button>
        <span class="tooltip-text">{{ palStore.getTranslatedText('PlayerList_Viewing_Cage') }}</span>
      </div>
    </div>
    <div class="overflow-list" ref="playerListContainer">
      <div class="overflow-container" v-if="palStore.HAS_WORKING_PAL_FLAG">
        <button class="player" @click="palStore.selectPlayer(palStore.PAL_BASE_WORKER_BTN)"
          :disabled="palStore.BASE_PAL_BTN_CLK_FLAG || palStore.LOADING_FLAG">
          {{ palStore.getTranslatedText('PlayerList_Base_Pal') }}
        </button>
      </div>
      <div class="overflow-container" v-for="player in palStore.PLAYER_MAP.values()">
        <button class="player real" @click="palStore.selectPlayer(player.InstanceId)" :title="player.InstanceId"
          :disabled="(player.InstanceId == palStore.SELECTED_PLAYER_ID && palStore.SHOW_PLAYER_EDIT_FLAG) || palStore.LOADING_FLAG"
          :selected="player.InstanceId == palStore.SELECTED_PLAYER_ID">
          {{ player.NickName }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
div.flex {
  display: flex;
  flex-direction: column;
  width: 100%;
  min-width: 0;
  height: 100%;
  padding: var(--space-xs);
  border: var(--rule);
  border-radius: var(--radius-panel);
  background: var(--color-paper-2);
  box-shadow: var(--shadow-panel);
}

div.title {
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2xs);
  min-height: 2.25rem;
  color: var(--color-ink);
  font-weight: 600;
}

.rail-title { display: flex; flex: 1 1 auto; min-width: 0; flex-direction: column; line-height: 1.1; }
.rail-title span { color: var(--color-accent); font-size: .65rem; font-weight: 750; letter-spacing: .12em; text-transform: uppercase; }
.rail-title strong { color: var(--color-ink); font-size: var(--text-xs); font-weight: 750; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.rail-count { display: grid; min-width: 1.65rem; height: 1.65rem; place-items: center; border: var(--rule); border-radius: var(--radius-pill); color: var(--color-ink-2); font-size: var(--text-xs); }

div.overflow-list {
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow-y: auto;
  gap: var(--space-3xs);
  padding-right: var(--space-3xs);
}

div.overflow-container {
  align-items: center;
  display: flex;
  overflow: hidden;
  white-space: nowrap;
  max-height: 3.25rem;
  flex-shrink: 0;
  border-radius: var(--radius-input);
}

button.player {
  min-width: 100%;
  max-height: 5rem;
  padding: .55rem .7rem;
  background-color: var(--color-warning-soft);
  color: var(--color-ink);
  border: 1px solid transparent;
  outline: none;
  border-radius: var(--radius-input);
  font-size: var(--text-sm);
  overflow: hidden;
  text-overflow: ellipsis;
  transition: background-color var(--dur-short) var(--ease-out), border-color var(--dur-short) var(--ease-out);
  cursor: pointer;
}

button.playerSettings {
  background-color: var(--color-paper-3);
  width: 1.8rem;
  height: 1.8rem;
  padding: 0;
  color: var(--color-ink);
  border: var(--rule);
  outline: none;
  border-radius: var(--radius-input);
  font-size: 1rem;
}

button.playerSettings:hover {
  background-color: var(--color-paper-3);
  border-color: var(--color-accent);
  cursor: pointer;
}

button.player:hover {
  background-color: var(--color-warning-strong);
}

button.player.real {
  background-color: var(--color-paper-3);
  border-color: var(--color-rule);
}

button.player.real:hover {
  background-color: var(--color-accent-muted);
  border-color: var(--color-accent);
}

button.player.real:disabled {
  background-color: #8a8a8a;
  box-shadow: 0 0 0;
  filter: grayscale(100%);
  cursor: not-allowed;
}

button.player:disabled {
  background-color: #8a8a8a;
  box-shadow: 0 0 0;
  filter: grayscale(100%);
  cursor: not-allowed;
}

button.playerSettings:disabled {
  background-color: #8a8a8a;
  box-shadow: 0 0 0;
  filter: grayscale(100%);
  cursor: not-allowed;
}

button.player[selected="true"] {
  filter: none;
  border-color: var(--color-accent);
  box-shadow: inset 3px 0 0 var(--color-accent);
}

.tooltip-text {
  visibility: hidden;
  width: 200px;
  background-color: var(--color-paper);
  color: var(--color-ink);
  text-align: center;
  border: var(--rule);
  border-radius: var(--radius-card);
  padding: 1rem;

  position: absolute;
  z-index: 1;
  top: 5rem;
  margin-left: -60px;
}

.tooltip-container:hover .tooltip-text {
  visibility: visible;
}

.tooltip-container:focus-within .tooltip-text {
  visibility: visible;
}

@media (max-width: 900px) {
  div.flex {
    height: auto;
    max-height: 12rem;
  }

  .tooltip-text {
    display: none;
  }
}

div.flex {
  padding: var(--space-2xs);
  border: 0;
  border-radius: var(--radius-input);
  background: transparent;
  box-shadow: none;
}

button.player.real:disabled[selected="true"] {
  background: var(--color-accent-soft);
  border-color: var(--color-accent);
  filter: none;
  opacity: 1;
}
</style>
