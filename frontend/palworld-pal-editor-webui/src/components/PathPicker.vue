<script setup>
import { usePalEditorStore } from '@/stores/paleditor'
import { computed } from '@vue/reactivity';
import { ref, onMounted } from 'vue'

import IconButton from './modules/IconButton.vue';
import InputArea from './modules/InputArea.vue'
import BarButton from './modules/BarButton.vue'
const palStore = usePalEditorStore()

const sortedPathChildren = computed(() => {
    return Array.from(palStore.PATH_CONTEXT.entries()).sort((a, b) => {
        if (a[1].isDir && !b[1].isDir) {
            return -1;
        } else if (!a[1].isDir && b[1].isDir) {
            return 1;
        }

        return a[1].filename.localeCompare(b[1].filename);
    })
})

const savePickerResult = () => {
    palStore.SHOW_FILE_PICKER = false
    palStore.PAL_GAME_SAVE_PATH = palStore.PAL_FILE_PICKER_PATH

}

// const scrollElement = ref(null);

// const checkScroll = () => {
//     if (!scrollElement.value) return;
//     const scrollTop = scrollElement.value.scrollTop;
//     const scrollHeight = scrollElement.value.scrollHeight;
//     const clientHeight = scrollElement.value.clientHeight;

//     scrollElement.value.classList.toggle('scrolled-top', scrollTop > 0);
//     scrollElement.value.classList.toggle('scrolled-bottom', scrollTop + clientHeight < scrollHeight);
// };

// onMounted(() => {
//     if (scrollElement.value) {
//         scrollElement.value.addEventListener('scroll', checkScroll);
//         checkScroll(); // Initial check to update shadow state
//     }
// });
const abort = () => {
    palStore.SHOW_FILE_PICKER = false
}
</script>

<template>
    <div class="modal-overlay" v-if="palStore.SHOW_FILE_PICKER" @click.self="abort">
        <div class="popup">
            <button class="close-btn" @click="abort">×</button>
            <div class="currentPath">
                <IconButton icon="⤴️" @click="palStore.path_back" />
                <InputArea v-model="palStore.PAL_FILE_PICKER_PATH" />
                <IconButton icon="➡️" @click="palStore.update_picker_result(palStore.PAL_FILE_PICKER_PATH)" />
            </div>

            <ul ref="scrollElement">
                <li v-for="([key, value], index) of sortedPathChildren" :key="index" :isdir="value.isDir"
                    @click="() => { if (value.isDir) palStore.update_picker_result(key) }" :fullpath="key">
                    {{ value.isDir ? "📁" : "📄" }} {{ value.filename }}
                </li>
            </ul>
            <BarButton @click="savePickerResult" content="OK" :disabled="!palStore.IS_PAL_SAVE_PATH" />
        </div>
    </div>
</template>

<style scoped>
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    padding: var(--space-sm);
    background: var(--color-overlay);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.popup {
    position: relative;
    width: min(70rem, 92vw);
    height: min(44rem, 82vh);
    min-width: 0;
    border: var(--rule);
    outline: none;
    border-radius: var(--radius-panel);
    padding: var(--space-lg);
    background-color: var(--color-paper-2);
    z-index: 10;
    box-shadow: var(--shadow-panel);

    display: flex;
    flex-direction: column;
    gap: var(--space-md);
}

.popup .currentPath {
    display: flex;
    gap: var(--space-2xs);
    align-items: center;
}

.popup ul {
    overflow-y: auto;
    list-style-type: none;
    padding: 0;
    flex: 1;
    min-height: 0;
    border: var(--rule);
    border-radius: var(--radius-card);
    background: var(--color-paper);
}

.popup li[isdir=true] {
    cursor: pointer;
}

.popup li {
    margin: .2rem .2rem;
    padding: .3rem .3rem;
    border-radius: var(--radius-input);
    color: var(--color-ink);
}

.popup li:hover[isdir=true] {
    background-color: var(--color-accent-muted);
}

.close-btn {
    position: absolute;
    top: 10px;
    right: 10px;
    background: var(--color-paper-3);
    border-radius: var(--radius-input);
    width: 30px;
    height: 30px;
    border: var(--rule);
    color: var(--color-ink-2);
    font-size: 1.5rem;
    cursor: pointer;
}

.close-btn:hover {
    background: var(--color-paper);
    border-color: var(--color-danger);
    color: var(--color-danger);
}

@media (max-width: 600px) {
    .popup {
        width: 100%;
        height: 88vh;
        padding: var(--space-sm);
    }
}
</style>
