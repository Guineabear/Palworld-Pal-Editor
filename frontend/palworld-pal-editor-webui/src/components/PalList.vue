<script setup>
import { usePalEditorStore } from '@/stores/paleditor'
import { ref, computed, reactive, onMounted, nextTick, watch } from "vue";

const palStore = usePalEditorStore()

const palListContainer = ref(null);

watch(async () => palStore.SELECTED_PLAYER_ID, async () => {
    await nextTick();
    if (palStore.SHOW_PLAYER_EDIT_FLAG && !palStore.BASE_PAL_BTN_CLK_FLAG) {
        return
    }
    try {
        if (palStore.BASE_PAL_BTN_CLK_FLAG == false) {
            return
        }
        const button = palListContainer.value.querySelector('button:not(:disabled)');
        if (button) {
            button.click();
        }
    } catch (error) {
        return
    }
})

// watch(async () => palStore.ADD_PAL_RESELECT_CTR, async () => {
//     await nextTick();
//     try {
//         const button = palListContainer.value.querySelector('button:not(:disabled)');
//         if (button) {
//             button.click();
//         }
//     } catch (error) {
//         return
//     }
// })

watch(async () => palStore.UPDATE_PAL_RESELECT_CTR, async () => {
    await nextTick();
    try {
        const button = palListContainer.value.querySelector(`button[value="${palStore.SELECTED_PAL_ID}"]`);
        if (button) {
            if (!palStore.isElementInViewport(button)) {
                button.scrollIntoView({ behavior: "smooth" });
            }
        }
    } catch (error) {
        return
    }
})

watch(async () => palStore.SELECTED_PAL_ID, async () => {
    await nextTick();
    if (palStore.SHOW_PLAYER_EDIT_FLAG && !palStore.BASE_PAL_BTN_CLK_FLAG) {
        return
    }
    try {
        const button = palListContainer.value.querySelector(`button[value="${palStore.SELECTED_PAL_ID}"]`);
        if (button) {
            if (palStore.SELECTED_PAL_ID != palStore.SELECTED_PAL_DATA?.InstanceId) {
                palStore.selectPal(palStore.SELECTED_PAL_ID, true)
            }
            if (!palStore.isElementInViewport(button)) {
                button.scrollIntoView({ behavior: "smooth" });
            }
        }
    } catch (error) {
        return
    }
})

onMounted(async () => {
    await nextTick();
    // TODO Note: this is just a temp fix for pal selection when pal list is refreshed by updatePlayer
    await nextTick();
    await nextTick();
    if (palStore.SHOW_PLAYER_EDIT_FLAG && !palStore.BASE_PAL_BTN_CLK_FLAG) {
        return
    }
    const button = palListContainer.value.querySelector('button:not(:disabled)');
    if (button) {
        button.click();
    }
});

function get_filtered_pal_list() {
    // console.log("FILTER")
    return Array.from(palStore.PAL_MAP.values()).filter(pal => !palStore.isFilteredPal(pal))
}

</script>

<template>
    <div class="flex">
        <div class="title">
            <div class="rail-title">
                <span>Paldeck</span>
                <strong>{{ palStore.getTranslatedText("PalList_Text") }}</strong>
            </div>
            <span class="rail-count">{{ get_filtered_pal_list().length }}</span>
            <input class="palFilter" type="text" v-model="palStore.PAL_LIST_SEARCH_KEYWORD" placeholder="Search Pal"
                :disabled="palStore.LOADING_FLAG">
            <button class="add_pal" v-if="!palStore.BASE_PAL_BTN_CLK_FLAG"
                :title="`Add Pal for Player ${palStore.PLAYER_MAP.get(palStore.SELECTED_PLAYER_ID).NickName}`"
                :disabled="palStore.LOADING_FLAG" @click="palStore.addPal" name="add_pal">+</button>
        </div>

        <div class="overflow-list" ref="palListContainer">
            <div class="overflow-container" v-for="pal in get_filtered_pal_list()">
                <button
                    :class="['pal', { 'male': pal.displayGender() == '♂️', 'female': pal.displayGender() == '♀️', 'unref': pal.Is_Unref_Pal, 'out_of_container': !pal.in_owner_palbox }]"
                    :value="pal.InstanceId" @click="palStore.selectPal(pal.InstanceId)"
                    :disabled="palStore.SELECTED_PAL_ID == pal.InstanceId || palStore.LOADING_FLAG"
                    :selected="palStore.SELECTED_PAL_ID == pal.InstanceId"
                    >
                    <img :class="['palIcon']" :src="`/image/pals/${pal.IconAccessKey}`">
                    {{ pal.DisplayName }}
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
    flex-wrap: wrap;
    align-items: center;
    gap: var(--space-2xs);
    min-height: 2.25rem;
    color: var(--color-ink);
    font-weight: 600;
}

div.overflow-list {
    display: flex;
    flex-direction: column;
    min-height: 0;
    overflow-y: auto;
    gap: var(--space-3xs);
    padding-right: var(--space-3xs);
}

.overflow-container {
    display: flex;
    overflow: hidden;
    white-space: nowrap;
    max-height: 3.25rem;
    flex-shrink: 0;
    border-radius: var(--radius-input);
    width: 100%;
}

input.palFilter {
    order: 3;
    flex: 1 1 calc(100% - 2.5rem);
    display: flex;
    align-items: center;
    background-color: var(--color-paper);
    width: auto;
    min-width: 0;
    height: 2rem;
    margin: 0;
    padding: .25rem .65rem;
    border-radius: var(--radius-pill);
    color: var(--color-ink);
    border: var(--rule);
    outline: none;
}

input.palFilter:focus {
    background-color: var(--color-paper-3);
    border-color: var(--color-accent);
    color: var(--color-ink);
}

img.palIcon {
    width: 2.1rem;
    height: 2.1rem;
    object-fit: cover;
    margin-right: var(--space-2xs);
    border-radius: 50%;
}

button {
    cursor: pointer;
}

button.pal {
    display: flex;
    align-items: center;
    justify-content: left;
    white-space: nowrap;
    min-width: 100%;
    max-height: 3rem;
    padding: .35rem .55rem;
    min-height: 3rem;
    background-color: var(--color-paper-3);
    color: var(--color-ink);
    border: 1px solid var(--color-rule);
    outline: none;
    border-radius: var(--radius-input);
    font-size: var(--text-sm);
    text-align: left;
    overflow: hidden;
    text-overflow: ellipsis;
    transition: background-color var(--dur-short) var(--ease-out), border-color var(--dur-short) var(--ease-out);
}

button.pal:hover {
    background-color: var(--color-accent-muted);
    border-color: var(--color-accent);
}

button.pal:disabled {
    background-color: #8a8a8a;
    box-shadow: 0 0 0;
    filter: grayscale(100%);
    cursor: not-allowed;
}

button.pal:disabled:hover {
    background-color: #8a8a8a;
    box-shadow: 0 0 0;
    filter: grayscale(100%);
    cursor: not-allowed;
}

button.pal.male {
    /* background-color: #095594; */
    border-color: #095594;
    border-style: solid;
    border-width: 0.15rem;
}

button.pal.male:hover {
    background-color: #023b69;
}

button.pal.male:disabled {
    background-color: #023b69;
    box-shadow: 0 0 0;
    filter: grayscale(100%);
    cursor: not-allowed;
}

button.pal.male:disabled[selected="true"] {
    background-color: #023b69;
    box-shadow: 0 0 0;
    filter: none;
    cursor: not-allowed;
}

button.pal.female {
    border-color: #a13268;
    border-style: solid;
    border-width: 0.15rem;
}

button.pal.female:hover {
    background-color: #5d0b32;
}

button.pal.female:disabled {
    background-color: #5d0b32;
    box-shadow: 0 0 0;
    filter: grayscale(100%);
    cursor: not-allowed;
}

button.pal.female:disabled[selected="true"] {
    background-color: #5d0b32;
    box-shadow: 0 0 0;
    filter: none;
    cursor: not-allowed;
}

button.unref {
    filter: grayscale(100%);
}

button.unref:hover {
    background-color: #5e5e5e !important;
}

button.unref:disabled {
    background-color: #5e5e5e !important;
    box-shadow: 0 0 0;
    filter: grayscale(100%);
    cursor: not-allowed;
}

button.out_of_container {
    color: #3db15e;
}

button.add_pal {
    order: 4;
    flex: 0 0 2rem;
    height: 2rem;
    background-color: var(--color-success);
    color: var(--color-accent-ink);
    border: 1px solid transparent;
    outline: none;
    border-radius: var(--radius-input);
    font-size: 1rem;
}

button.add_pal:hover {
    filter: brightness(1.08);
    cursor: pointer;
}

button.add_pal:disabled {
    background-color: #8a8a8a;
    box-shadow: 0 0 0;
    filter: grayscale(100%);
    cursor: not-allowed;
}

.rail-title { display: flex; flex: 1 1 auto; min-width: 0; flex-direction: column; line-height: 1.1; }
.rail-title span { color: var(--color-accent); font-size: .65rem; font-weight: 750; letter-spacing: .12em; text-transform: uppercase; }
.rail-title strong { color: var(--color-ink); font-size: var(--text-xs); font-weight: 750; white-space: nowrap; }
.rail-count { display: grid; min-width: 1.65rem; height: 1.65rem; place-items: center; border: var(--rule); border-radius: var(--radius-pill); color: var(--color-ink-2); font-size: var(--text-xs); }

@media (max-width: 900px) {
    div.flex {
        height: auto;
        max-height: 16rem;
    }
}

div.flex {
    padding: var(--space-2xs);
    border: 0;
    border-radius: var(--radius-input);
    background: transparent;
    box-shadow: none;
}

button.pal:disabled[selected="true"] {
    background: var(--color-accent-soft);
    border-color: var(--color-accent);
    filter: none;
    opacity: 1;
}
</style>
