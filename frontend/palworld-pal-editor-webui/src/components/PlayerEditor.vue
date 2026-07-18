<script setup>
import { usePalEditorStore } from '@/stores/paleditor'
import ItemCard from '@/components/modules/TechCard.vue'
import { computed, ref } from 'vue'

const palStore = usePalEditorStore()
const techQuery = ref('')
const techFilter = ref('all')
defineProps({
    section: {
        type: String,
        default: 'profile'
    }
})

const filteredTech = items => {
    const query = techQuery.value.trim().toLowerCase()
    return items.filter(item => {
        const matchesQuery = !query || `${item.I18n?.Name || ''} ${item.I18n?.Type || ''} ${item.InternalName || ''}`.toLowerCase().includes(query)
        const unlocked = palStore.SELECTED_PLAYER_DATA.UnlockedRecipeTechnologyNames.includes(item.InternalName)
        const matchesState = techFilter.value === 'all' || (techFilter.value === 'unlocked' ? unlocked : !unlocked)
        return matchesQuery && matchesState
    })
}

const isMaxLv = () => {
    return palStore.SELECTED_PLAYER_DATA.Level >= (palStore.HIDE_INVALID_OPTIONS ? palStore.MAX_LEVEL : palStore.MAX_INVALID_LEVEL);
};

const isMinLv = () => {
    return palStore.SELECTED_PLAYER_DATA.Level <= 1;
};

const playerPalCount = computed(() => palStore.SELECTED_PLAYER_DATA?.pals?.size || 0)
const serverPlayerCount = computed(() => palStore.PLAYER_MAP.size)
const unlockedTechCount = computed(() => palStore.SELECTED_PLAYER_DATA?.UnlockedRecipeTechnologyNames?.length || 0)
const totalTechCount = computed(() => Object.values(palStore.TECH_LV_DICT || {}).reduce((total, items) => total + items.length, 0))
</script>

<template>
    <div class="PalEditor">
        <header class="player-workspace-header">
            <div>
                <span class="workspace-kicker">Player workspace</span>
                <h1>{{ palStore.SELECTED_PLAYER_DATA.NickName }}</h1>
            </div>
        </header>
        <div v-if="section === 'profile'" class="player-profile">
            <section class="player-overview" aria-labelledby="player-overview-heading">
                <div class="section-heading">
                    <div><span class="section-kicker">Selected player</span><h2 id="player-overview-heading">Overview</h2></div>
                    <code>{{ palStore.SELECTED_PLAYER_DATA.InstanceId }}</code>
                </div>
                <div class="player-stat-grid">
                    <article><span>Level</span><strong>{{ palStore.SELECTED_PLAYER_DATA.Level }}</strong><small>Maximum {{ palStore.MAX_LEVEL }}</small></article>
                    <article><span>Owned Pals</span><strong>{{ playerPalCount }}</strong><small>Loaded from this player’s containers</small></article>
                    <article><span>Technology</span><strong>{{ unlockedTechCount }} / {{ totalTechCount }}</strong><small>Recipes currently unlocked</small></article>
                    <article><span>Server roster</span><strong>{{ serverPlayerCount }}</strong><small>Players found in this save</small></article>
                    <article><span>Technology points</span><strong>{{ palStore.SELECTED_PLAYER_DATA.TechnologyPoint }}</strong><small>Standard points available</small></article>
                    <article><span>Ancient points</span><strong>{{ palStore.SELECTED_PLAYER_DATA.bossTechnologyPoint }}</strong><small>Ancient technology currency</small></article>
                </div>
            </section>

            <section class="player-edit-card" aria-labelledby="player-edit-heading">
                <div class="section-heading">
                    <div><span class="section-kicker">Save values</span><h2 id="player-edit-heading">Edit player</h2></div>
                    <span class="state-badge">Viewing cage {{ palStore.SELECTED_PLAYER_DATA.HasViewingCage ? 'unlocked' : 'locked' }}</span>
                </div>
                <div class="player-form-grid">
                    <label><span>{{ palStore.getTranslatedText("Editor_Nickname") }}</span><div><input type="text" name="NickName" v-model="palStore.SELECTED_PLAYER_DATA.NickName"><button @click="palStore.updatePlayer" name="NickName" :value="palStore.SELECTED_PLAYER_DATA.NickName" :disabled="palStore.LOADING_FLAG">Save</button></div></label>
                    <label><span>{{ palStore.getTranslatedText("Editor_TechPoint") }}</span><div><input type="number" name="TechnologyPoint" v-model="palStore.SELECTED_PLAYER_DATA.TechnologyPoint" min="0" max="65535"><button @click="palStore.updatePlayer" name="TechnologyPoint" :value="palStore.SELECTED_PLAYER_DATA.TechnologyPoint" :disabled="palStore.LOADING_FLAG">Save</button></div></label>
                    <label><span>{{ palStore.getTranslatedText("Editor_BossTechPoint") }}</span><div><input type="number" name="bossTechnologyPoint" v-model="palStore.SELECTED_PLAYER_DATA.bossTechnologyPoint" min="0" max="65535"><button @click="palStore.updatePlayer" name="bossTechnologyPoint" :value="palStore.SELECTED_PLAYER_DATA.bossTechnologyPoint" :disabled="palStore.LOADING_FLAG">Save</button></div></label>
                    <div class="level-editor"><span>Player level</span><div><strong>{{ palStore.SELECTED_PLAYER_DATA.Level }}</strong><button @click="palStore.SELECTED_PLAYER_DATA.levelDown" :disabled="palStore.LOADING_FLAG || isMinLv()">−</button><button @click="palStore.SELECTED_PLAYER_DATA.levelUp" :disabled="palStore.LOADING_FLAG || isMaxLv()">+</button><button @click="palStore.SELECTED_PLAYER_DATA.maxLevel" :disabled="palStore.LOADING_FLAG || isMaxLv()">Max</button></div></div>
                </div>
                <div class="player-quick-actions">
                    <button class="primary-action" @click="palStore.updatePlayer" name="unlock_all_techs" :disabled="palStore.LOADING_FLAG">{{ palStore.getTranslatedText("Editor_UnlockAllTech") }}</button>
                    <button v-if="!palStore.SELECTED_PLAYER_DATA.HasViewingCage" @click="palStore.updatePlayer" name="unlock_viewing_cage" :disabled="palStore.LOADING_FLAG">Unlock viewing cage</button>
                </div>
            </section>

            <section class="player-technical" aria-labelledby="player-technical-heading">
                <div class="section-heading"><div><span class="section-kicker">Save references</span><h2 id="player-technical-heading">Containers</h2></div></div>
                <dl>
                    <div><dt>Party container</dt><dd><code>{{ palStore.SELECTED_PLAYER_DATA.OtomoCharacterContainerId }}</code></dd></div>
                    <div><dt>Palbox container</dt><dd><code>{{ palStore.SELECTED_PLAYER_DATA.PalStorageContainerId }}</code></dd></div>
                </dl>
            </section>
        </div>
        <div v-if="section === 'technology'" class="EditorItem item left flex-v technology-panel">
            <div class="technology-heading">
                <div>
                    <p class="cat">{{ palStore.getTranslatedText("Editor_TechEdit") }}</p>
                    <p class="section-description">Search and toggle unlocks by level.</p>
                </div>
                <div class="technology-controls">
                    <input class="tech-search" type="search" v-model="techQuery" placeholder="Search technology" aria-label="Search technology">
                    <div class="tech-filters" aria-label="Technology state filter">
                        <button :class="{ active: techFilter === 'all' }" @click="techFilter = 'all'">All</button>
                        <button :class="{ active: techFilter === 'locked' }" @click="techFilter = 'locked'">Locked</button>
                        <button :class="{ active: techFilter === 'unlocked' }" @click="techFilter = 'unlocked'">Unlocked</button>
                    </div>
                </div>
            </div>
            <div class="EditorItem flex-h maxW no-margin">
                <div class="levels-container">
                    <div class="level-row" v-for="(items, level) in palStore.TECH_LV_DICT" :key="level" v-show="filteredTech(items).length">
                        <div class="level-indicator">
                            Level {{ level }}
                        </div>
                        <div class="cards-row">
                            <ItemCard v-for="item in filteredTech(items)" :key="item.InternalName" :item="item" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
    </div>
</template>

<style scoped>
div.no-margin {
    margin: 0;
}
div.no-padding {
    padding: 0;
}
.PalEditor {
    display: flex;
    width: 100%;
    min-width: 0;
    height: 100%;
    overflow-y: auto;
    flex-wrap: wrap;
    align-items: flex-start;
    align-content: flex-start;
    gap: var(--space-xs);
    padding-right: var(--space-3xs);
}

.EditorItem {
    display: flex;
    flex-shrink: 0;
    min-width: 0;
    max-width: 100%;
    background: var(--color-paper-2);
    padding: var(--space-md);
    border: var(--rule);
    border-radius: var(--radius-panel);
    box-shadow: var(--shadow-panel);
}

.EditorItem.maxW {
    width: 100%;
    min-width: 0;
    padding: var(--space-xs);
    max-width: 100%;
}

div.editField {
    /* border-style: dashed;
    border-width: 1px;
    border-color: white; */
    /* width: 100%; */
    /* flex-wrap: nowrap; */
    width: 100%;
    max-width: 100%;
    min-width: 0;
    flex-wrap: wrap;
    gap: 5px
}

div.basicInfo {
    position: relative;
    max-width: 100%;
    /* min-width: calc(max(100%,var(--editor-panel-width))); */
}

hr {
    border: 0;
    width: 100%;
    height: 2px;
    background-color: #8a8a8a;
    margin: 20px 0;
}

button {
    cursor: pointer;
}

p.cat {
    margin: 0 0 var(--space-2xs);
    color: var(--color-ink);
    font-size: var(--text-sm);
    font-weight: 700;
    letter-spacing: .02em;
}

div {
    display: flex;
    align-items: center;
}

div.flex-v {
    flex-direction: column;
    gap: .2rem;
}

div.flex-h {
    flex-direction: row;
    gap: .5rem
}

div.left {
    justify-content: flex-start;
    align-items: flex-start;
}

p.const {
    display: flex;
    align-items: center;
    background-color: #272727;
    height: 1.8rem;
    margin: .2rem;
    padding: .2rem .4rem;
    border-radius: .5rem;
    color: rgb(208, 212, 226);
    box-shadow: 2px 2px 10px rgb(38, 38, 38);
}

button.edit {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 2rem;
    height: 2rem;
    padding: 0rem;
    margin: 0rem;
    background-color: #848484;
    color: whitesmoke;
    border: none;
    outline: none;
    border-radius: 0.5rem;
    transition: background-color var(--dur-short) var(--ease-out), box-shadow var(--dur-short) var(--ease-out);
}

button.edit:hover {
    background-color: #9c9c9c;
    box-shadow: 2px 2px 10px rgb(38, 38, 38);
}

button.edit:disabled {
    background-color: #8b8b8b;
    box-shadow: 0 0 0;
    filter: grayscale(100%);
    cursor: not-allowed;
}

button.text {
    width: 100%;
    background-color: #2c77c2;
    padding: 1rem .5rem;
    margin: .2rem;
}

button.text:hover {
    background-color: #18518a;
}

button.text:disabled {
    background-color: #8a8a8a;
    box-shadow: 0 0 0;
    filter: grayscale(100%);
    cursor: not-allowed;
}

button.edit_text {
    width: 5rem;
    background-color: #2c77c2;
    padding: 1rem .5rem;
    margin: .2rem;
}

button.edit_text:hover {
    background-color: #18518a;
}

button.edit_text:disabled {
    background-color: #8a8a8a;
    box-shadow: 0 0 0;
    filter: grayscale(100%);
    cursor: not-allowed;
}

button.del {
    background-color: #ffcece;
}

button.del:hover {
    background-color: #7c0f0f;
}

button.del:disabled {
    background-color: #8a8a8a;
    box-shadow: 0 0 0;
    filter: grayscale(100%);
    cursor: not-allowed;
}

input.edit {
    min-width: 0;
    max-width: 100%;
    height: 2rem;
    background-color: #6a6a6c;
    color: whitesmoke;
    border: none;
    outline: none;
    border-radius: 0.5rem;
    font-size: 1.2rem;
    padding-left: 0.7rem;
    padding-right: 0.7rem;
}

input.edit:focus {
    background-color: #b8b8b8;
    color: black;
    /* border: 2px solid #6a6a6c; */
    box-shadow: 2px 2px 10px rgb(38, 38, 38);
}

input.edit::placeholder {
    color: #cccccca2
}

div.spaceBetween {
    display: flex;
    width: 100%;
    justify-content: space-between
}

.tooltip-container {
    position: relative;
    display: inline-block;
}

.tooltip-text {
    visibility: hidden;
    width: 200px;
    background-color: rgba(0, 0, 0, 0.85);
    color: white;
    text-align: center;
    border-radius: 6px;
    padding: 1rem;

    /* Position the tooltip */
    position: absolute;
    z-index: 1;
    bottom: 100%;
    left: 50%;
    margin-left: -60px;
    margin-bottom: .25rem;
}

.tooltip-container:hover .tooltip-text {
    visibility: visible;
}

select.selector {
    display: flex;
    align-items: center;
    background-color: #272727;
    height: 1.8rem;
    margin: .2rem;
    padding: .2rem .4rem;
    border-radius: .5rem;
    color: rgb(208, 212, 226);
    box-shadow: 2px 2px 10px rgb(38, 38, 38);
    /* max-width: 50%; */
}

.levels-container {
    display: flex;
    flex-direction: column;
    width: 100%;
    min-width: 0;
    max-height: calc(var(--sub-height) - 7rem);
    overflow-y: auto;
    max-width: 100%;
    padding: var(--space-2xs);
    align-items: stretch;
}

.level-row {
    display: flex;
    align-items: center;
    width: 100%;
    min-width: 0;
    max-width: 100%;
    border-bottom: 1px solid var(--color-rule-translucent);
}

.level-indicator {
    flex: 0 0 auto;
    justify-content: center;
    min-width: 5.5rem;
    font-weight: bold;
    margin-right: .5rem;
    color: var(--color-ink);
    background-color: var(--color-paper-3);
    padding: .5rem;
    border: var(--rule);
    border-radius: var(--radius-input);
}

.cards-row {
    flex: 1 1 0;
    display: flex;
    min-width: 0;
    max-width: 100%;
    overflow-x: auto;
    overflow-y: hidden;
    padding-bottom: var(--space-2xs);
    scrollbar-gutter: stable;
}

@media (max-width: 900px) {
    .PalEditor {
        height: auto;
        max-height: none;
    }

    .EditorItem,
    .EditorItem.maxW {
        width: 100%;
    }

    .level-row {
        align-items: flex-start;
    }

    p.const {
        height: auto;
        min-height: 1.8rem;
    }
}

.player-workspace-header {
    display: flex;
    width: 100%;
    min-width: 0;
    align-items: flex-end;
    justify-content: space-between;
    gap: var(--space-md);
    padding: var(--space-sm) var(--space-md);
    border: var(--rule);
    border-radius: var(--radius-panel);
    background: linear-gradient(110deg, var(--color-accent-canvas), var(--color-paper-2) 62%);
    box-shadow: var(--shadow-panel);
}

.player-workspace-header > div { display: block; }

.workspace-kicker {
    color: var(--color-accent);
    font-size: var(--text-xs);
    font-weight: 750;
    letter-spacing: .12em;
    text-transform: uppercase;
}

.player-workspace-header h1 {
    margin: var(--space-3xs) 0 0;
    color: var(--color-ink);
    font-size: clamp(1.65rem, 3vw, 2.5rem);
    font-weight: 760;
    letter-spacing: -.04em;
}

.player-profile {
    display: grid;
    width: 100%;
    min-width: 0;
    grid-template-columns: minmax(0, 1.35fr) minmax(16rem, .65fr);
    gap: var(--space-sm);
    align-items: start;
}

.player-profile > section {
    display: block;
    min-width: 0;
    padding: var(--space-md);
    border: var(--rule);
    border-radius: var(--radius-card);
    background: var(--color-paper-2);
    box-shadow: var(--shadow-panel);
}

.player-overview { grid-column: 1 / -1; }

.section-heading {
    display: flex;
    width: 100%;
    min-width: 0;
    align-items: flex-start;
    justify-content: space-between;
    gap: var(--space-sm);
}

.section-heading > div { display: block; min-width: 0; }
.section-heading h2 { margin: var(--space-3xs) 0 0; color: var(--color-ink); font-size: var(--text-xl); font-style: normal; }
.section-heading > code { max-width: 24rem; color: var(--color-ink-2); font-family: var(--font-mono); font-size: var(--text-xs); overflow-wrap: anywhere; text-align: right; }
.section-kicker { color: var(--color-accent); font-size: var(--text-xs); font-weight: 750; letter-spacing: .08em; text-transform: uppercase; }

.player-stat-grid {
    display: grid;
    width: 100%;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: var(--space-xs);
    margin-top: var(--space-sm);
}

.player-stat-grid article {
    display: grid;
    min-width: 0;
    min-height: 8rem;
    align-content: space-between;
    gap: var(--space-2xs);
    padding: var(--space-sm);
    border: 1px solid var(--color-rule-soft);
    border-radius: var(--radius-input);
    background: var(--color-paper-3);
}

.player-stat-grid span, .player-form-grid label > span, .level-editor > span { color: var(--color-ink-2); font-size: var(--text-xs); font-weight: 700; }
.player-stat-grid strong { color: var(--color-ink); font-family: var(--font-mono); font-size: clamp(1.6rem, 4vw, 2.4rem); line-height: 1; }
.player-stat-grid small { color: var(--color-ink-2); font-size: var(--text-xs); line-height: 1.4; }

.state-badge { padding: .35rem .55rem; border-radius: var(--radius-pill); background: var(--color-accent-soft); color: var(--color-accent); font-size: var(--text-xs); white-space: nowrap; }
.player-form-grid { display: grid; gap: var(--space-xs); margin-top: var(--space-sm); }
.player-form-grid label, .level-editor { display: grid; min-width: 0; gap: var(--space-3xs); }
.player-form-grid label > div, .level-editor > div { display: flex; width: 100%; min-width: 0; gap: var(--space-3xs); }
.player-form-grid input { width: 100%; min-width: 0; height: 2.65rem; padding: 0 var(--space-xs); border: var(--rule); border-radius: var(--radius-input); background: var(--color-paper); color: var(--color-ink); }
.player-form-grid button, .player-quick-actions button { min-height: 2.65rem; padding: 0 var(--space-xs); border: var(--rule); border-radius: var(--radius-input); background: var(--color-paper-3); color: var(--color-ink); cursor: pointer; font-weight: 700; white-space: nowrap; }
.player-form-grid button:hover:not(:disabled), .player-quick-actions button:hover:not(:disabled) { border-color: var(--color-accent); }
.player-form-grid button:focus-visible, .player-form-grid input:focus-visible, .player-quick-actions button:focus-visible { outline: 2px solid var(--color-focus); outline-offset: 2px; }
.player-form-grid button:active:not(:disabled), .player-quick-actions button:active:not(:disabled) { transform: translateY(1px); }
.player-form-grid button:disabled, .player-quick-actions button:disabled { cursor: not-allowed; opacity: .5; }
.level-editor strong { display: grid; min-width: 4rem; place-items: center; border-radius: var(--radius-input); background: var(--color-paper); color: var(--color-ink); font-family: var(--font-mono); }
.player-quick-actions { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: var(--space-xs); margin-top: var(--space-sm); }
.player-quick-actions .primary-action { border-color: var(--color-accent); background: var(--color-accent); color: var(--color-accent-ink); }

.player-technical dl { margin: var(--space-sm) 0 0; }
.player-technical dl > div { display: grid; gap: var(--space-3xs); padding: var(--space-xs) 0; border-bottom: 1px solid var(--color-rule-soft); }
.player-technical dt { color: var(--color-ink-2); font-size: var(--text-xs); }
.player-technical dd { min-width: 0; margin: 0; }
.player-technical code { color: var(--color-ink); font-family: var(--font-mono); font-size: var(--text-xs); overflow-wrap: anywhere; }

@media (max-width: 900px) {
    .player-profile { grid-template-columns: minmax(0, 1fr); }
    .player-overview { grid-column: auto; }
    .player-stat-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 520px) {
    .section-heading { align-items: flex-start; flex-direction: column; }
    .section-heading > code { text-align: left; }
    .player-stat-grid, .player-quick-actions { grid-template-columns: minmax(0, 1fr); }
}

.technology-panel { width: 100%; }

.technology-heading {
    display: flex;
    width: 100%;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-sm);
}

.technology-controls {
    display: grid;
    gap: var(--space-2xs);
    width: min(32rem, 55%);
}

.tech-filters {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: var(--space-3xs);
}

.tech-filters button {
    min-height: 2.25rem;
    border: var(--rule);
    border-radius: var(--radius-input);
    background: var(--color-paper-3);
    color: var(--color-ink-2);
    cursor: pointer;
}

.tech-filters button.active {
    border-color: var(--color-accent);
    background: var(--color-accent);
    color: var(--color-accent-ink);
    font-weight: 750;
}

.technology-heading > div { display: block; }

.section-description {
    color: var(--color-ink-2);
    font-size: var(--text-sm);
}

.tech-search {
    width: 100%;
    min-width: 10rem;
    height: 2.5rem;
    padding: .4rem .75rem;
    border: var(--rule);
    border-radius: var(--radius-pill);
    background: var(--color-paper);
    color: var(--color-ink);
}

.tech-search:focus { border-color: var(--color-accent); }

@media (max-width: 620px) {
    .player-workspace-header,
    .technology-heading { align-items: stretch; flex-direction: column; }
    .technology-controls, .tech-search { width: 100%; }
}

.level-row {
    align-items: flex-start;
    gap: var(--space-xs);
    padding-block: var(--space-xs);
}

.level-indicator {
    position: sticky;
    top: calc(var(--topbar-height) + var(--space-sm));
}

.cards-row {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(8.5rem, 1fr));
    gap: var(--space-xs);
    overflow: visible;
    padding: 0;
}
</style>
