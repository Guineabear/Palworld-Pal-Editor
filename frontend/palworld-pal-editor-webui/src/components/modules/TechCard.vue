<template>
    <button type="button" :class="['tech', { bossTech: item.BossTechnology }, { locked: isLocked }]" :style="bgStyle"
        @click="toggleLock">
        <div class="techHeader">{{ item.I18n.Type ?? "⚠️ INVALID" }}</div>
        <div class="techFooter">{{ item.I18n.Name ?? item.internalName }}</div>
    </button>
</template>

<script setup>
import { ref, computed } from 'vue'
import { usePalEditorStore } from '@/stores/paleditor'
const palStore = usePalEditorStore()

const props = defineProps({
    item: {
        type: Object,
        required: true
    }
})

function toggleLock() {
    palStore.SELECTED_PLAYER_DATA.toggleTech(props.item.InternalName, isLocked.value)
}

const bgStyle = computed(() => {
    let internalName = props.item.InternalName;
    const cat = internalName.split('_')[0] == "SkillUnlock" ? "pals" : "tech";
    if (cat == "pals") {
        internalName = internalName.replace("SkillUnlock_", "")
    }
    return {
        backgroundImage: `url('/image/${cat}/${internalName}')`
    }
})

const isLocked = computed(() => {
    return !palStore.SELECTED_PLAYER_DATA.UnlockedRecipeTechnologyNames.includes(props.item.InternalName)
})

</script>

<style scoped>
.tech {
    width: 100%;
    min-width: 0;
    height: 10.5rem;
    background-position: center;
    background-size: 90px 90px;
    background-repeat: no-repeat;
    position: relative;
    box-shadow: var(--shadow-control);
    background-color: var(--color-tech-card);
    border: 1px solid var(--color-tech-border);
    border-radius: var(--radius-card);
    margin: 0;
    cursor: pointer;
    overflow: hidden;
    padding: 0;
    color: var(--color-ink);
    font-family: var(--font-body);
    text-align: left;
    transition: transform var(--dur-short) var(--ease-out), border-color var(--dur-short) var(--ease-out), filter var(--dur-short) var(--ease-out);
}

.tech:hover {
    transform: translateY(-2px);
    border-color: var(--color-focus);
}

.tech:active {
    transform: translateY(0);
}

.tech.bossTech {
    background-color: #6b2f77;
    border-color: #b74fff;
}

.tech.locked {
    filter: grayscale(100%) brightness(.68);
}

.techHeader {
    position: absolute;
    top: 0;
    width: 100%;
    text-align: center;
    background-color: var(--color-tech-overlay);
    color: var(--color-ink);
    font-size: var(--text-xs);
    font-weight: 600;
    padding: var(--space-3xs);
}

.techFooter {
    position: absolute;
    bottom: 0;
    width: 100%;
    text-align: center;
    min-height: 2.4rem;
    display: grid;
    place-items: center;
    background-color: var(--color-tech-overlay);
    text-shadow: -1px 0 black, 0 1px black, 1px 0 black, 0 -1px black;
    font-size: var(--text-xs);
    line-height: 1.2;
    color: var(--color-ink);
    padding: var(--space-3xs);
}
</style>
