<script setup>
import { usePalEditorStore } from '@/stores/paleditor'
import PassivePresetBar from '@/components/PassivePresetBar.vue'
import ActivePresetBar from '@/components/ActivePresetBar.vue'
const palStore = usePalEditorStore()

function formatString(input) {
  if (!input) return input;
  // Separate the numeric part and the alphabetic suffix using a regular expression
  const match = input.match(/^(\d+)([A-Za-z]*)$/);
  if (!match) return input; // Return the input as is if it doesn't match the expected pattern

  const [, numbers, suffix] = match;

  // Pad the numeric part with leading zeros to make it at least 3 digits
  const paddedNumbers = numbers.padStart(3, '0');

  // Append the suffix if it exists; otherwise, append an empty space
  const formatted = suffix ? paddedNumbers + suffix : paddedNumbers;
  // if (suffix) {
  //   console.log(formatted)
  // }
  return formatted;
}

function filterInvalid(list) {
  return list.filter(item => {
    if (palStore.HIDE_INVALID_OPTIONS) {
      return !(item.Invalid || item.Experimental || item.IsHuman)
    }
    return true
  })
}

const isMaxSuit = key => {
  return palStore.SELECTED_PAL_DATA.Suitabilities[key] >= palStore.MAX_SUITABILITY_LEVEL;
};

const isMinSuit = key => {
  return palStore.PAL_STATIC_DATA[palStore.SELECTED_PAL_DATA.DataAccessKey]?.Suitabilities[key] ==
    palStore.SELECTED_PAL_DATA.Suitabilities[key] - (palStore.SELECTED_PAL_DATA["Rank"] >= 5 ? 1 : 0);
};

const isMaxLv = () => {
  return palStore.SELECTED_PAL_DATA.Level >= (palStore.HIDE_INVALID_OPTIONS ? palStore.MAX_LEVEL : palStore.MAX_INVALID_LEVEL);
};

const isMinLv = () => {
  return palStore.SELECTED_PAL_DATA.Level <= 1;
};

const isMaxFriendshipLv = () => {
  return palStore.SELECTED_PAL_DATA.FriendshipLevel >= palStore.MAX_FRIENDSHIP_LEVEL;
};

const isMinFriendshipLv = () => {
  return palStore.SELECTED_PAL_DATA.FriendshipLevel <= -3;
};

const suitabilityIconSrc = key => {
  return key ? `/image/suitabilities/${key.split("::").pop()}` : '';
};

</script>

<template>
  <div :class="['PalEditor', { 'unref': palStore.SELECTED_PAL_DATA.Is_Unref_Pal }]">
    <header class="pal-workspace-header">
      <div class="selected-pal-heading">
        <img :src="`/image/pals/${palStore.SELECTED_PAL_DATA.IconAccessKey}`" alt="">
        <div>
          <span class="workspace-kicker">Pal profile</span>
          <h1>{{ palStore.SELECTED_PAL_DATA.NickName || palStore.SELECTED_PAL_DATA.I18nName }}</h1>
          <p>{{ palStore.displayPalElement(palStore.SELECTED_PAL_DATA.DataAccessKeyOG) }} {{ palStore.PAL_STATIC_DATA[palStore.SELECTED_PAL_DATA.DataAccessKeyOG]?.I18n || palStore.SELECTED_PAL_DATA.DataAccessKeyOG }} · Lv {{ palStore.SELECTED_PAL_DATA.Level }}</p>
        </div>
      </div>
      <div class="pal-actions">
        <button @click="palStore.dumpPalData" :disabled="palStore.LOADING_FLAG">Export</button>
        <button @click="palStore.dupePal" :disabled="palStore.LOADING_FLAG" v-if="!palStore.BASE_PAL_BTN_CLK_FLAG">Duplicate</button>
        <button class="danger" @click="palStore.delPal" :disabled="palStore.LOADING_FLAG">Delete</button>
      </div>
    </header>
    <div class="pal-editor-layout">
      <div class="pal-editor-main">
    <div class="EditorItem item flex-v basicInfo">
      <img :class="['palIcon']" :src="`/image/pals/${palStore.SELECTED_PAL_DATA.IconAccessKey}`" alt="">
      <p v-if="palStore.SELECTED_PAL_DATA.Is_Unref_Pal">
        {{ palStore.getTranslatedText("Editor_Note_Ghost_Pal") }}
      </p>

      <div class="item flex-v left">
        <p class="cat">
          {{ palStore.getTranslatedText("Editor_Basic_Info") }}
        </p>
        <div class="editField">
          <p class="const" :title="palStore.SELECTED_PAL_DATA.InternalName">
            {{ palStore.getTranslatedText("Editor_Species") }}
            {{ palStore.displayPalElement(palStore.SELECTED_PAL_DATA.DataAccessKeyOG) }}
            {{ palStore.PAL_STATIC_DATA[palStore.SELECTED_PAL_DATA.DataAccessKeyOG]?.I18n ||
              palStore.SELECTED_PAL_DATA.DataAccessKeyOG }}
          </p>
          <!-- <p class="const"> Specie: </p> -->
          <select class="selector" name="CharacterID" v-model="palStore.SELECTED_PAL_DATA.DataAccessKey">
            <option class="" v-for="pal in filterInvalid(palStore.PAL_STATIC_DATA_LIST)" :value="pal.InternalName"
              :key="pal.InternalName" :title="pal.InternalName"> {{ `
              ${pal.Experimental ? `🧪 ${palStore.getTranslatedText("Editor_Experimental")}` : pal.Invalid || pal.IsHuman ? '⚠️' : ""}
              ${formatString(pal.SortingKey) || ""}
              ${palStore.displayPalElement(pal.InternalName)}
              ${pal.I18n}${palStore.HIDE_INVALID_OPTIONS ? '' : ` | ${pal.InternalName}`}`
              }} </option>
          </select>
          <button class="edit" @click="palStore.SELECTED_PAL_DATA.changeSpecie" name="CharacterID"
            :disabled="palStore.LOADING_FLAG">✅</button>

        </div>
        <div class="editField">
          <p class="const">
            {{ palStore.getTranslatedText("Editor_Nickname") }}
          </p>
          <input class="edit" type="text" name="NickName" v-model="palStore.SELECTED_PAL_DATA.NickName"
            :placeholder="palStore.SELECTED_PAL_DATA.I18nName">
          <button class="edit" @click="palStore.updatePal" name="NickName" :value="palStore.SELECTED_PAL_DATA.NickName"
            :disabled="palStore.LOADING_FLAG">✅</button>
        </div>
        <div class="flex-h">
          <div class="editField">
            <p class="const">💙 {{ palStore.getTranslatedText("Editor_Friendship_Level") }} {{ palStore.SELECTED_PAL_DATA.FriendshipLevel }}</p>
            <button class="edit" @click="palStore.SELECTED_PAL_DATA.friendshipLevelDown" name="FriendshipLevel"
              :disabled="palStore.LOADING_FLAG || isMinFriendshipLv()">🔽</button>
            <button class="edit" @click="palStore.SELECTED_PAL_DATA.friendshipLevelUp" name="FriendshipLevel"
              :disabled="palStore.LOADING_FLAG || isMaxFriendshipLv()">🔼</button>
            <button class="edit" @click="palStore.SELECTED_PAL_DATA.maxFriendshipLevel" name="FriendshipLevel"
              :disabled="palStore.LOADING_FLAG || isMaxFriendshipLv()">🔝</button>
          </div>
          <div class="editField" v-if="palStore.SELECTED_PAL_DATA.Level">
            <p class="const"> Lv: {{ palStore.SELECTED_PAL_DATA.Level }}</p>
            <button class="edit" @click="palStore.SELECTED_PAL_DATA.levelDown" name="Level"
              :disabled="palStore.LOADING_FLAG || isMinLv()">🔽</button>
            <button class="edit" @click="palStore.SELECTED_PAL_DATA.levelUp" name="Level"
              :disabled="palStore.LOADING_FLAG || isMaxLv()">🔼</button>
            <button class="edit" @click="palStore.SELECTED_PAL_DATA.maxLevel" name="Level"
              :disabled="palStore.LOADING_FLAG || isMaxLv()">🔝</button>
          </div>
        </div>
        <div class="flex-h">
          <div class="editField" v-if="palStore.SELECTED_PAL_DATA.Gender || !palStore.HIDE_INVALID_OPTIONS">
            <p class="const">
              {{ palStore.getTranslatedText("Editor_Gender") }}
              {{ palStore.SELECTED_PAL_DATA.displayGender() }}
            </p>
            <button class="edit" @click="palStore.SELECTED_PAL_DATA.swapGender" name="Gender"
              :disabled="palStore.LOADING_FLAG">🔄</button>
          </div>

          <div class="editField" v-if="!palStore.SELECTED_PAL_DATA.IsHuman">
            <p class="const">
              {{ palStore.getTranslatedText("Editor_Variant") }}
              {{ palStore.SELECTED_PAL_DATA.displaySpecialType() }}
            </p>
            <button class="edit" @click="palStore.SELECTED_PAL_DATA.swapTower" name="IsTower"
              v-if="palStore.SELECTED_PAL_DATA.HasTowerVariant" :disabled="palStore.LOADING_FLAG">🗼</button>
            <button class="edit" @click="palStore.SELECTED_PAL_DATA.swapBoss" name="IsBOSS"
              v-if="palStore.SELECTED_PAL_DATA.HasBossVariant" :disabled="palStore.LOADING_FLAG">👑</button>
            <button class="edit" @click="palStore.SELECTED_PAL_DATA.swapRare" name="IsRarePal"
              v-if="palStore.SELECTED_PAL_DATA.HasBossVariant" :disabled="palStore.LOADING_FLAG">✨</button>
          </div>
        </div>
        <p class="const">
          🪪 {{ palStore.getTranslatedText("Editor_Pal_CharacterID") }}
          {{ palStore.SELECTED_PAL_DATA.CharacterID }}
        </p>
        <p class="const">
          🆔 {{ palStore.getTranslatedText("Editor_Pal_ID") }}
          {{ palStore.SELECTED_PAL_ID }}
        </p>
        <p class="const">
          🏘️ {{ palStore.getTranslatedText("Editor_Pal_Guild_ID") }}
          {{ palStore.SELECTED_PAL_DATA.group_id }}
        </p>
        <div class="editField">
          <p :class="['const', { 'out_of_container': !palStore.SELECTED_PAL_DATA.in_owner_palbox }]"
            :title="palStore.SELECTED_PAL_DATA.in_owner_palbox ? '' : 'Pal is out of owner palbox, i.e. in viewing cage or taken by someone.'">
            📦 {{ palStore.getTranslatedText("Editor_Pal_Slot") }}
            {{ palStore.SELECTED_PAL_DATA.ContainerId }} @
            {{ palStore.SELECTED_PAL_DATA.SlotIndex }}
          </p>
          <button class="edit edit_text" @click="palStore.updatePal" name="in_owner_palbox"
            :disabled="palStore.LOADING_FLAG" v-if="!palStore.SELECTED_PAL_DATA.in_owner_palbox">
            {{ palStore.getTranslatedText("Editor_Btn_Retrieve_Pal") }}
          </button>
        </div>
        <p class="const">
          🗿 {{ palStore.getTranslatedText("Editor_Pal_Owner") }}
          {{ palStore.SELECTED_PAL_DATA.OwnerName ||
            palStore.getTranslatedText("Editor_Pal_No_Owner") }}
        </p>
        <div class="palInfo">
          <p class="const">
            ❤️ {{ palStore.getTranslatedText("Editor_Estimated_HP") }}
            {{ palStore.SELECTED_PAL_DATA.ComputedMaxHP / 1000 }}
          </p>
          <p class="const">
            ⚔️ {{ palStore.getTranslatedText("Editor_Estimated_ATK") }}
            {{ palStore.SELECTED_PAL_DATA.ComputedAttack }}
          </p>
          <p class="const">
            🛡️ {{ palStore.getTranslatedText("Editor_Estimated_DEF") }}
            {{ palStore.SELECTED_PAL_DATA.ComputedDefense }}
          </p>
          <p class="const">
            🔨 {{ palStore.getTranslatedText("Editor_Estimated_WorkSpeed") }}
            {{ palStore.SELECTED_PAL_DATA.ComputedCraftSpeed }}
          </p>
        </div>

        <div class="editField" v-if="palStore.SELECTED_PAL_DATA.HasWorkerSick">
          <button class="edit text" @click="palStore.updatePal" name="HasWorkerSick" :disabled="palStore.LOADING_FLAG">
            💊 {{ palStore.getTranslatedText("Editor_Btn_Heal_Pal") }}
          </button>
        </div>
        <div class="editField" v-if="palStore.SELECTED_PAL_DATA.IsFaintedPal">
          <button class="edit text" @click="palStore.updatePal" name="IsFaintedPal" :disabled="palStore.LOADING_FLAG">
            💉 {{ palStore.getTranslatedText("Editor_Btn_Revive_Pal") }}
          </button>
        </div>
      </div>
    </div>
    <div class="EditorItem flex-v item left growth-panel">
      <p class="cat">
        {{ palStore.getTranslatedText("Editor_IV") }}
      </p>
      <div class="editField spaceBetween">
        <p class="const">
          ❤️ {{ palStore.getTranslatedText("Editor_IV_HP") }}
          {{ palStore.SELECTED_PAL_DATA.Talent_HP }}
        </p>
        <input class="slider" type="range" name="Talent_HP" min="0" :max="palStore.HIDE_INVALID_OPTIONS ? 100 : 255"
          :disabled="palStore.LOADING_FLAG" v-model="palStore.SELECTED_PAL_DATA.Talent_HP" @mouseup="palStore.updatePal"
          @touchend="palStore.updatePal">
      </div>
      <div class="editField spaceBetween">
        <p class="const">
          🛡️ {{ palStore.getTranslatedText("Editor_IV_DEF") }}
          {{ palStore.SELECTED_PAL_DATA.Talent_Defense }}
        </p>
        <input class="slider" type="range" name="Talent_Defense" min="0"
          :max="palStore.HIDE_INVALID_OPTIONS ? 100 : 255" :disabled="palStore.LOADING_FLAG"
          v-model="palStore.SELECTED_PAL_DATA.Talent_Defense" @mouseup="palStore.updatePal"
          @touchend="palStore.updatePal">
      </div>
      <div class="editField spaceBetween">
        <p class="const">
          ⚔️ {{ palStore.getTranslatedText("Editor_IV_ATK") }}
          {{ palStore.SELECTED_PAL_DATA.Talent_Shot }}
        </p>
        <input class="slider" type="range" name="Talent_Shot" min="0" :max="palStore.HIDE_INVALID_OPTIONS ? 100 : 255"
          :disabled="palStore.LOADING_FLAG" v-model="palStore.SELECTED_PAL_DATA.Talent_Shot"
          @mouseup="palStore.updatePal" @touchend="palStore.updatePal">
      </div>
      <div class="editField spaceBetween" v-if="!palStore.HIDE_INVALID_OPTIONS">
        <p class="const">
          {{ palStore.getTranslatedText("Editor_IV_MELEE") }}
          {{ palStore.SELECTED_PAL_DATA.Talent_Melee }}
        </p>
        <input class="slider" type="range" name="Talent_Melee" min="0" :max="palStore.HIDE_INVALID_OPTIONS ? 100 : 255"
          :disabled="palStore.LOADING_FLAG" v-model="palStore.SELECTED_PAL_DATA.Talent_Melee"
          @mouseup="palStore.updatePal" @touchend="palStore.updatePal">
      </div>
      <hr>
      <p class="cat">
        {{ palStore.getTranslatedText("Editor_Souls_Upgrade") }}
      </p>
      <div class="editField spaceBetween">
        <p class="const">
          ❤️ {{ palStore.getTranslatedText("Editor_Souls_HP") }}
          {{ palStore.SELECTED_PAL_DATA.Rank_HP }}
        </p>
        <input class="slider" type="range" name="Rank_HP" min="0"
          :max="palStore.HIDE_INVALID_OPTIONS ? palStore.MAX_SOULS_LEVEL : 255" :disabled="palStore.LOADING_FLAG"
          v-model="palStore.SELECTED_PAL_DATA.Rank_HP" @mouseup="palStore.updatePal" @touchend="palStore.updatePal">
      </div>
      <div class="editField spaceBetween">
        <p class="const">
          ⚔️ {{ palStore.getTranslatedText("Editor_Souls_ATK") }}
          {{ palStore.SELECTED_PAL_DATA.Rank_Attack }}
        </p>
        <input class="slider" type="range" name="Rank_Attack" min="0"
          :max="palStore.HIDE_INVALID_OPTIONS ? palStore.MAX_SOULS_LEVEL : 255" :disabled="palStore.LOADING_FLAG"
          v-model="palStore.SELECTED_PAL_DATA.Rank_Attack" @mouseup="palStore.updatePal" @touchend="palStore.updatePal">
      </div>
      <div class="editField spaceBetween">
        <p class="const">
          🛡️ {{ palStore.getTranslatedText("Editor_Souls_DEF") }}
          {{ palStore.SELECTED_PAL_DATA.Rank_Defence }}
        </p>
        <input class="slider" type="range" name="Rank_Defence" min="0"
          :max="palStore.HIDE_INVALID_OPTIONS ? palStore.MAX_SOULS_LEVEL : 255" :disabled="palStore.LOADING_FLAG"
          v-model="palStore.SELECTED_PAL_DATA.Rank_Defence" @mouseup="palStore.updatePal"
          @touchend="palStore.updatePal">
      </div>
      <div class="editField spaceBetween">
        <p class="const">
          🔨 {{ palStore.getTranslatedText("Editor_Souls_CraftSpeed") }}
          {{ palStore.SELECTED_PAL_DATA.Rank_CraftSpeed }}
        </p>
        <input class="slider" type="range" name="Rank_CraftSpeed" min="0"
          :max="palStore.HIDE_INVALID_OPTIONS ? palStore.MAX_SOULS_LEVEL : 255" :disabled="palStore.LOADING_FLAG"
          v-model="palStore.SELECTED_PAL_DATA.Rank_CraftSpeed" @mouseup="palStore.updatePal"
          @touchend="palStore.updatePal">
      </div>
      <hr>
      <p class="cat">
        {{ palStore.getTranslatedText("Editor_Condenser") }}
      </p>
      <div class="editField spaceBetween">
        <p class="const">
          ⭐ {{ palStore.getTranslatedText("Editor_Condenser_Rank") }}
          {{ palStore.SELECTED_PAL_DATA.Rank - 1 }}
        </p>
        <input class="slider" type="range" name="Rank" min="1" :max="palStore.HIDE_INVALID_OPTIONS ? 5 : 255"
          v-model="palStore.SELECTED_PAL_DATA.Rank" :disabled="palStore.LOADING_FLAG" @mouseup="palStore.updatePal"
          @touchend="palStore.updatePal">
      </div>
      <hr>
      <p class="cat">{{ palStore.getTranslatedText("Editor_Awakening") }}</p>
      <div class="editField awakening-control">
        <p class="const">
          {{ palStore.SELECTED_PAL_DATA.IsAwakening
            ? palStore.getTranslatedText("Editor_Awakened")
            : palStore.getTranslatedText("Editor_Not_Awakened") }}
        </p>
        <button class="edit edit_text" :class="{ awakened: palStore.SELECTED_PAL_DATA.IsAwakening }"
          @click="palStore.SELECTED_PAL_DATA.toggleAwakening" :disabled="palStore.LOADING_FLAG">
          {{ palStore.SELECTED_PAL_DATA.IsAwakening ? "On" : "Off" }}
        </button>
      </div>
    </div>
    <div class="EditorItem flex-v item left skillPanel work-panel"
      v-if="palStore.PAL_STATIC_DATA[palStore.SELECTED_PAL_DATA.DataAccessKey]?.Suitabilities">
      <p class="cat">
        {{ palStore.getTranslatedText("Editor_Suitabilities") }}
      </p>
      <div class="flex-h">
        <div class="editField skillList">
          <div v-for="(value, key) in palStore.SELECTED_PAL_DATA.Suitabilities"
            v-show="palStore.HIDE_INVALID_OPTIONS || value != 'EPalWorkSuitability::OilExtraction'">
            <p class="const">
              <img :class="['suitIcon']" :src="suitabilityIconSrc(key)" alt="">
              {{ value }}
            </p>
            <button class="edit" @click="palStore.SELECTED_PAL_DATA.suitDown" :name="key"
              :disabled="palStore.LOADING_FLAG || isMinSuit(key)">🔽</button>
            <button class="edit" @click="palStore.SELECTED_PAL_DATA.suitUp" :name="key"
              :disabled="palStore.LOADING_FLAG || isMaxSuit(key)">🔼</button>
          </div>
        </div>
      </div>
    </div>
    <div class="EditorItem item flex-v left skillPanel skills-panel">
      <p class="cat">
        {{ palStore.getTranslatedText("Editor_Passive_Skills") }}
      </p>
      <p v-if="palStore.SELECTED_PAL_DATA.PassiveSkillList.length > 4" class="passive-warning">
        {{ palStore.getTranslatedText("Editor_Passive_Skills_Hidden_Warning") }}
      </p>
      <PassivePresetBar />
      <div class="flex-h">
        <div class="editField skillList">
          <div v-for="skill in palStore.SELECTED_PAL_DATA.PassiveSkillList">
            <div class="tooltip-container">
              <p class="const" :title="palStore.PASSIVE_SKILLS[skill]?.I18n[1] || skill">
                {{ palStore.displayRating(palStore.PASSIVE_SKILLS[skill]?.Rating) }} {{
                  palStore.PASSIVE_SKILLS[skill]?.I18n[0] || skill }}
              </p>
              <span class="tooltip-text">{{ palStore.PASSIVE_SKILLS[skill]?.I18n[1] || skill }}</span>
            </div>

            <button class="edit del" @click="palStore.SELECTED_PAL_DATA.pop_PassiveSkillList" :name="skill"
              :disabled="palStore.LOADING_FLAG">❌</button>
          </div>
          <div class="editField"
            v-if="!palStore.HIDE_INVALID_OPTIONS || palStore.SELECTED_PAL_DATA.PassiveSkillList.length < 6">
            <select class="PassiveSkill selector" name="add_PassiveSkillList"
              v-model="palStore.PAL_PASSIVE_SELECTED_ITEM">
              <option class="PassiveSkill" value="" key="">
                {{ palStore.getTranslatedText("Editor_Select_Skill") }}
              </option>
              <option class="PassiveSkill" v-for="skill in palStore.PASSIVE_SKILLS_LIST" :value="skill.InternalName"
                :key="skill.InternalName" :title="skill.I18n[1]">{{ palStore.displayRating(skill.Rating) }} {{
                  skill.I18n[0] }}</option>
            </select>
            <button class="edit" @click="palStore.SELECTED_PAL_DATA.add_PassiveSkillList" name="add_PassiveSkillList"
              :disabled="palStore.LOADING_FLAG || palStore.SELECTED_PAL_DATA.isEquippedPassiveSkill(palStore.PAL_PASSIVE_SELECTED_ITEM)">➕</button>
          </div>
        </div>
      </div>
      <hr>
      <ActivePresetBar />
      <div class="skill-guidance" role="note">
        <strong>{{ palStore.getTranslatedText("Editor_Active_Save_Guide") }}</strong>
        <span>{{ palStore.getTranslatedText("Editor_Exclusive_Skill_Warning") }}</span>
      </div>
      <p class="cat">
        {{ palStore.getTranslatedText("Editor_Equipped_Skills") }}
      </p>
      <div class="flex-h">
        <div class="editField skillList">
          <div v-for="skill in palStore.SELECTED_PAL_DATA.EquipWaza">
            <div class="tooltip-container">
              <p class="const" :title="palStore.ACTIVE_SKILLS[skill]?.I18n[1] || skill">{{
                palStore.displayElement(palStore.ACTIVE_SKILLS[skill]?.Element) }} {{
                  palStore.ACTIVE_SKILLS[skill]?.I18n[0] || skill
                }}
              </p>
              <span class="tooltip-text">
                <h3>{{ palStore.ACTIVE_SKILLS[skill]?.I18n[0] || skill }}</h3>
                <p>{{ palStore.ACTIVE_SKILLS[skill]?.I18n[1] || "" }}</p>
                <p> --- </p>
                <p>
                  {{ palStore.getTranslatedText("Editor_Skill_ATK") }}
                  {{ palStore.ACTIVE_SKILLS[skill]?.Power }} |
                  {{ palStore.getTranslatedText("Editor_Skill_CD") }}
                  {{ palStore.ACTIVE_SKILLS[skill]?.CT }}
                </p>
                <p>
                  {{ palStore.getTranslatedText("Editor_Skill_EL") }}
                  {{ palStore.displayElement(palStore.ACTIVE_SKILLS[skill]?.Element) }}
                  {{ palStore.ACTIVE_SKILLS[skill]?.Element }}
                </p>
                <p>
                  {{ palStore.ACTIVE_SKILLS[skill]?.IsUniqueSkill ? "✨ Unique" : "" }}
                  {{ palStore.ACTIVE_SKILLS[skill]?.HasSkillFruit ? "🍐 Fruit Available" : "" }}
                </p>
              </span>
            </div>

            <button class="edit del" @click="palStore.SELECTED_PAL_DATA.pop_EquipWaza" :name="skill"
              :disabled="palStore.LOADING_FLAG">❌</button>
          </div>
        </div>
      </div>
      <hr>
      <p class="cat">
        {{ palStore.getTranslatedText("Editor_Mastered_Skills") }}
      </p>
      <div class="flex-h">
        <div class="editField skillList">
          <div v-for="skill in palStore.SELECTED_PAL_DATA.MasteredWaza">
            <div class="tooltip-container">
              <p class="const" :title="palStore.ACTIVE_SKILLS[skill]?.I18n[1] || skill">
                {{ palStore.displayElement(palStore.ACTIVE_SKILLS[skill]?.Element) }}
                {{ palStore.ACTIVE_SKILLS[skill]?.I18n[0] || skill }}
              </p>
              <span class="tooltip-text">
                <h3>{{ palStore.ACTIVE_SKILLS[skill]?.I18n[0] || skill }}</h3>
                <p>{{ palStore.ACTIVE_SKILLS[skill]?.I18n[1] || "" }}</p>
                <p> --- </p>
                <p>
                  {{ palStore.getTranslatedText("Editor_Skill_ATK") }}
                  {{ palStore.ACTIVE_SKILLS[skill]?.Power }} |
                  {{ palStore.getTranslatedText("Editor_Skill_CD") }}
                  {{ palStore.ACTIVE_SKILLS[skill]?.CT }}
                </p>
                <p>
                  {{ palStore.getTranslatedText("Editor_Skill_EL") }}
                  {{ palStore.displayElement(palStore.ACTIVE_SKILLS[skill]?.Element) }}
                  {{ palStore.ACTIVE_SKILLS[skill]?.Element }}
                </p>
                <p>
                  {{ palStore.ACTIVE_SKILLS[skill]?.IsUniqueSkill ? "✨ Unique" : "" }}
                  {{ palStore.ACTIVE_SKILLS[skill]?.HasSkillFruit ? "🍐 Fruit Available" : "" }}
                </p>
              </span>
            </div>
            <button v-if="!palStore.SELECTED_PAL_DATA.isEquippedSkill(skill)
              && (!palStore.SELECTED_PAL_DATA.isEquipSkillFull() || !palStore.HIDE_INVALID_OPTIONS)" class="edit"
              @click="palStore.SELECTED_PAL_DATA.add_EquipWaza" :name="skill"
              :disabled="palStore.LOADING_FLAG">🔼</button>
            <button class="edit del" @click="palStore.SELECTED_PAL_DATA.pop_MasteredWaza" :name="skill"
              :disabled="palStore.LOADING_FLAG">❌</button>
          </div>
          <div class="editField">
            <select class="selector" name="add_MasteredWaza" v-model="palStore.PAL_ACTIVE_SELECTED_ITEM">
              <option value="" key="">
                {{ palStore.getTranslatedText("Editor_Select_Skill") }}
              </option>
              <option v-for="skill in filterInvalid(palStore.ACTIVE_SKILLS_LIST)" :value="skill.InternalName"
                :key="skill.InternalName" :title="skill.I18n[1]">
                {{ `${palStore.displayElement(skill.Element)} ${skill.I18n[0]} ${palStore.skillIcon(skill.InternalName)}
                -
                ⚔️ ${skill.Power} - ⏱️ ${skill.CT}${palStore.HIDE_INVALID_OPTIONS ? '' : ` | ${skill.InternalName}`}` }}
              </option>
            </select>
            <button class="edit" @click="palStore.SELECTED_PAL_DATA.add_MasteredWaza" name="add_MasteredWaza"
              :disabled="palStore.LOADING_FLAG || palStore.SELECTED_PAL_DATA.isMasteredSkill(palStore.PAL_ACTIVE_SELECTED_ITEM)">➕</button>
          </div>
        </div>
      </div>
    </div>
      </div>
      <aside class="pal-summary" aria-label="Live Pal preview">
        <span>Live preview</span>
        <strong>{{ palStore.SELECTED_PAL_DATA.I18nName || palStore.SELECTED_PAL_DATA.DataAccessKeyOG }} · Lv {{ palStore.SELECTED_PAL_DATA.Level }}</strong>
        <dl>
          <div><dt>Attack</dt><dd>{{ palStore.SELECTED_PAL_DATA.ComputedAttack }}</dd></div>
          <div><dt>Defense</dt><dd>{{ palStore.SELECTED_PAL_DATA.ComputedDefense }}</dd></div>
          <div><dt>Health</dt><dd>{{ palStore.SELECTED_PAL_DATA.ComputedMaxHP / 1000 }}</dd></div>
          <div><dt>Work speed</dt><dd>{{ palStore.SELECTED_PAL_DATA.ComputedCraftSpeed }}</dd></div>
          <div><dt>Passives</dt><dd>{{ palStore.SELECTED_PAL_DATA.PassiveSkillList.length }} / 6</dd></div>
        </dl>
        <p>Save changes from the top bar when the Pal looks right.</p>
      </aside>
    </div>
  </div>
</template>

<style scoped>
/* Hallmark · component: Pal editing controls · genre: modern-minimal · theme: design.md
 * states: default · hover · focus · active · disabled · loading · error · success
 * pre-emit critique: P5 H5 E5 S5 R5 V4
 */
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

.PalEditor.unref {
  filter: grayscale(100%);
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

/* .EditorItem .Basic-Info {} */

/* option.PassiveSkill{
  background-color: red;
} */

div.basicInfo {
  position: relative;
  max-width: 100%;
  min-width: min(100%, 36rem);
}

div.palInfo {
  display: flex;
  flex-wrap: wrap;
}

div.skillPanel {
  width: 100%;
  max-width: 100%;
  min-width: 0;
  flex-wrap: wrap;
}

div.skillList {
  display: flex;
  flex-wrap: wrap;
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

p.passive-warning {
  margin: 0 0 .4rem 0;
  color: var(--color-warning);
  font-size: .85rem;
}

.skill-guidance {
  display: grid;
  gap: var(--space-3xs);
  width: 100%;
  margin: var(--space-2xs) 0;
  padding: var(--space-2xs) var(--space-xs);
  border: var(--rule);
  border-left: 3px solid var(--color-warning);
  border-radius: var(--radius-input);
  background: var(--color-paper-3);
  color: var(--color-ink-2);
  font-size: var(--text-xs);
}

.skill-guidance strong { color: var(--color-ink); }
.awakening-control { flex-wrap: wrap; }
button.edit_text.awakened {
  border-color: var(--color-success);
  background: var(--color-success-soft);
}

div {
  display: flex;
  align-items: center;
}

/* div.item {
  margin: .5rem;
} */

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
  background-color: var(--color-paper);
  height: 1.8rem;
  margin: .2rem;
  padding: .2rem .4rem;
  border: var(--rule);
  border-radius: var(--radius-input);
  color: var(--color-ink-2);
}

p.out_of_container {
  color: #3db15e !important;
}

img.palIcon {
  max-width: 15vh;
  border-radius: 50%;
  border: var(--rule);
  box-shadow: var(--shadow-control);
  margin-bottom: 1rem;
}

img.suitIcon {
  height: 1.8rem;
  margin: .2rem;
  padding: .2rem .2rem;
}

img.palIcon.unref {
  filter: grayscale(100%);
}

div.editField {
  /* border-style: dashed;
  border-width: 1px;
  border-color: white; */
  /* width: 100%; */
  /* flex-wrap: nowrap; */
  gap: 5px
}

button.edit {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  padding: 0rem;
  margin: 0rem;
  background-color: var(--color-paper-3);
  color: var(--color-ink);
  border: var(--rule);
  outline: none;
  border-radius: var(--radius-input);
  transition: background-color var(--dur-short) var(--ease-out), border-color var(--dur-short) var(--ease-out), transform var(--dur-short) var(--ease-out);
}

button.edit:hover {
  background-color: var(--color-accent-muted);
  border-color: var(--color-accent);
  transform: translateY(-1px);
}

button.edit:disabled {
  background-color: #8b8b8b;
  box-shadow: 0 0 0;
  filter: grayscale(100%);
  cursor: not-allowed;
}

button.text {
  width: 100%;
  background-color: var(--color-accent-strong);
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
  background-color: var(--color-accent-strong);
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

button#dump_btn {
  position: absolute;
  top: 1rem;
  left: 1rem;

  display: flex;
  align-items: center;
  justify-content: center;
  height: 2rem;
  padding: 1rem;
  margin: 0rem;
  background-color: #636363;
  color: rgb(204, 204, 204);
  border: none;
  outline: none;
  border-radius: 0.5rem;
  transition: background-color var(--dur-short) var(--ease-out), border-color var(--dur-short) var(--ease-out);
}

button#dump_btn:hover {
  background-color: #3e3e3e;
  box-shadow: 2px 2px 10px rgb(38, 38, 38);
  color: rgb(204, 204, 204);
}

button#dump_btn:disabled {
  background-color: #8a8a8a;
  box-shadow: 0 0 0;
  filter: grayscale(100%);
  cursor: not-allowed;
}

button#del_btn {
  position: absolute;
  top: 1rem;
  right: 1rem;

  display: flex;
  align-items: center;
  justify-content: center;
  height: 2rem;
  padding: 1rem;
  margin: 0rem;
  background-color: var(--color-danger);
  color: whitesmoke;
  border: none;
  outline: none;
  border-radius: 0.5rem;
  transition: background-color var(--dur-short) var(--ease-out), border-color var(--dur-short) var(--ease-out);
}

button#del_btn:hover {
  background-color: #830e25;
  box-shadow: 2px 2px 10px rgb(38, 38, 38);
}

button#del_btn:disabled {
  background-color: #8a8a8a;
  box-shadow: 0 0 0;
  filter: grayscale(100%);
  cursor: not-allowed;
}

button#dupe_btn {
  position: absolute;
  top: 3.5rem;
  left: 1rem;

  display: flex;
  align-items: center;
  justify-content: center;
  height: 2rem;
  padding: 1rem;
  margin: 0rem;
  background-color: #1c8dbd;
  color: whitesmoke;
  border: none;
  outline: none;
  border-radius: 0.5rem;
  transition: background-color var(--dur-short) var(--ease-out), border-color var(--dur-short) var(--ease-out);
}

button#dupe_btn:hover {
  background-color: #0e6b92;
  box-shadow: 2px 2px 10px rgb(38, 38, 38);
}

button#dupe_btn:disabled {
  background-color: #8a8a8a;
  box-shadow: 0 0 0;
  filter: grayscale(100%);
  cursor: not-allowed;
}

input.edit {
  height: 2rem;
  min-width: 0;
  background-color: var(--color-paper);
  color: var(--color-ink);
  border: var(--rule);
  outline: none;
  border-radius: var(--radius-input);
  font-size: var(--text-md);
  padding-left: 0.7rem;
  padding-right: 0.7rem;
}

input.edit:focus {
  background-color: var(--color-paper-3);
  color: var(--color-ink);
  border-color: var(--color-accent);
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
  max-width: 100%;
  min-width: 0;
  background-color: var(--color-paper);
  height: 1.8rem;
  margin: .2rem;
  padding: .2rem .4rem;
  border: var(--rule);
  border-radius: var(--radius-input);
  color: var(--color-ink);
}

@media (max-width: 900px) {
  .PalEditor {
    height: auto;
    max-height: none;
  }

  .EditorItem,
  div.basicInfo,
  div.skillPanel {
    width: 100%;
    min-width: 0;
  }
}

.pal-workspace-header {
  display: flex;
  width: 100%;
  min-width: 0;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-md);
  padding: var(--space-sm) var(--space-md);
  border: var(--rule);
  border-radius: var(--radius-panel);
  background:
    radial-gradient(circle at 12% 50%, var(--color-accent-bloom), transparent 18rem),
    linear-gradient(110deg, var(--color-accent-canvas), var(--color-paper-2) 65%);
  box-shadow: var(--shadow-panel);
}

.selected-pal-heading {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: var(--space-sm);
}

.selected-pal-heading > div { display: block; min-width: 0; }

.selected-pal-heading img {
  width: 5rem;
  height: 5rem;
  flex: 0 0 5rem;
  object-fit: cover;
  border: 1px solid var(--color-accent-border);
  border-radius: 1.35rem;
  background: var(--color-paper);
  box-shadow: var(--shadow-control);
}

.workspace-kicker {
  color: var(--color-accent);
  font-size: var(--text-xs);
  font-weight: 750;
  letter-spacing: .12em;
  text-transform: uppercase;
}

.selected-pal-heading h1 {
  margin: var(--space-3xs) 0;
  color: var(--color-ink);
  font-size: clamp(1.65rem, 3vw, 2.6rem);
  font-weight: 780;
  letter-spacing: -.045em;
  line-height: 1;
  overflow-wrap: anywhere;
}

.selected-pal-heading p { color: var(--color-ink-2); font-size: var(--text-sm); }

.editor-tabs {
  display: flex;
  gap: var(--space-3xs);
  padding: var(--space-3xs);
  border: var(--rule);
  border-radius: var(--radius-pill);
  background: var(--color-paper);
}

.editor-tabs button {
  padding: .45rem .8rem;
  border: 0;
  border-radius: var(--radius-pill);
  background: transparent;
  color: var(--color-ink-2);
}

.editor-tabs button:hover { color: var(--color-ink); background: var(--color-paper-3); }
.editor-tabs button.active { color: var(--color-accent-ink); background: var(--color-accent); font-weight: 750; }

.basicInfo,
.growth-panel,
.work-panel,
.skills-panel {
  width: 100%;
}

.basicInfo > img.palIcon { display: none; }
.basicInfo > #dump_btn,
.basicInfo > #dupe_btn,
.basicInfo > #del_btn { display: none; }

.pal-actions-menu { position: relative; flex: 0 0 auto; }

.pal-actions-menu summary {
  padding: .45rem .75rem;
  border: var(--rule);
  border-radius: var(--radius-input);
  background: var(--color-paper-3);
  color: var(--color-ink);
  cursor: pointer;
  list-style: none;
}

.pal-actions-menu summary::-webkit-details-marker { display: none; }
.pal-actions-menu[open] summary { border-color: var(--color-accent); }

.pal-actions-menu > div {
  position: absolute;
  top: calc(100% + var(--space-2xs));
  right: 0;
  z-index: 50;
  display: grid;
  width: 12rem;
  gap: var(--space-3xs);
  padding: var(--space-2xs);
  border: var(--rule);
  border-radius: var(--radius-card);
  background: var(--color-paper-2);
  box-shadow: var(--shadow-panel);
}

.pal-actions-menu button {
  padding: .55rem .7rem;
  border: var(--rule);
  border-radius: var(--radius-input);
  background: var(--color-paper-3);
  color: var(--color-ink);
  text-align: left;
}

.pal-actions-menu button:hover { border-color: var(--color-accent); }
.pal-actions-menu button.danger { color: var(--color-danger-bright); }

.growth-panel .editField,
.work-panel .editField,
.skills-panel .editField { width: 100%; }

@media (max-width: 760px) {
  .pal-workspace-header { align-items: stretch; flex-direction: column; }
  .editor-tabs { width: 100%; overflow-x: auto; border-radius: var(--radius-card); }
  .editor-tabs button { flex: 1 0 auto; }
  .pal-actions-menu { align-self: flex-end; }
}

@media (max-width: 420px) {
  .selected-pal-heading img { width: 3.75rem; height: 3.75rem; flex-basis: 3.75rem; }
  .pal-workspace-header { padding: var(--space-xs); }

  .basicInfo > .item,
  .basicInfo .editField,
  .basicInfo .palInfo,
  .basicInfo .flex-h {
    width: 100%;
    min-width: 0;
    max-width: 100%;
    flex-wrap: wrap;
  }

  .basicInfo p.const {
    width: auto;
    max-width: 100%;
    height: auto;
    min-height: 1.8rem;
    overflow-wrap: anywhere;
  }

  .basicInfo select.selector {
    width: 100%;
    min-width: 0;
    max-width: 100%;
  }

  .basicInfo input.edit {
    flex: 1 1 10rem;
    min-width: 0;
    max-width: 100%;
  }

  .skillPanel,
  .skillPanel .skillList,
  .skillPanel .flex-h,
  .skillPanel .editField,
  .skillPanel p.cat {
    width: 100%;
    min-width: 0;
    max-width: 100%;
  }

  .skillPanel .flex-h,
  .skillPanel .editField {
    flex-wrap: nowrap;
  }

  .skillPanel .editField.skillList {
    flex-wrap: wrap;
  }

  .skillPanel .editField.skillList > div {
    max-width: 100%;
  }

  .skillPanel .tooltip-text {
    left: 0;
    right: auto;
    max-width: min(12.5rem, calc(100vw - var(--space-md)));
  }

  .skillPanel select {
    min-width: 0;
    max-width: 100%;
    flex: 1 1 auto;
  }

  .skillPanel button.edit {
    flex: 0 0 2rem;
  }
}

/* Approved single-canvas Workbench layout. */
.PalEditor {
  display: block;
  height: auto;
  overflow: visible;
  padding: 0;
}

.pal-workspace-header {
  position: sticky;
  top: calc(var(--topbar-height) + var(--space-sm));
  z-index: 20;
  margin-bottom: var(--space-sm);
  border-radius: var(--radius-card);
}

.pal-actions {
  display: flex;
  align-items: center;
  gap: var(--space-3xs);
}

.pal-actions button {
  min-height: 2.35rem;
  border: var(--rule);
  border-radius: var(--radius-input);
  padding: 0 var(--space-xs);
  background: var(--color-paper-3);
  color: var(--color-ink);
  white-space: nowrap;
}

.pal-actions button:hover { border-color: var(--color-accent); }
.pal-actions button.danger { color: var(--color-danger); }

.pal-editor-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(14rem, 17rem);
  gap: var(--space-sm);
  align-items: start;
}

.pal-editor-main {
  display: grid;
  min-width: 0;
  gap: var(--space-sm);
}

.pal-editor-main > .EditorItem {
  width: 100%;
  margin: 0;
  border-radius: var(--radius-card);
  box-shadow: none;
}

.pal-summary {
  position: sticky;
  top: calc(var(--topbar-height) + 8.5rem);
  min-width: 0;
  padding: var(--space-sm);
  border: var(--rule);
  border-radius: var(--radius-card);
  background: var(--color-paper-2);
  box-shadow: var(--shadow-panel);
}

.pal-summary > span {
  color: var(--color-accent);
  font-size: var(--text-xs);
  font-weight: 750;
  letter-spacing: .08em;
  text-transform: uppercase;
}

.pal-summary > strong {
  display: block;
  margin-top: var(--space-3xs);
  color: var(--color-ink);
  font-size: var(--text-lg);
  overflow-wrap: anywhere;
}

.pal-summary dl { margin: var(--space-sm) 0 0; }
.pal-summary dl div {
  display: flex;
  justify-content: space-between;
  gap: var(--space-sm);
  padding: var(--space-xs) 0;
  border-bottom: 1px solid var(--color-rule-soft);
}
.pal-summary dt { color: var(--color-ink-2); }
.pal-summary dd { margin: 0; color: var(--color-ink); font-family: var(--font-mono); font-weight: 750; }
.pal-summary p {
  margin: var(--space-sm) 0 0;
  padding: var(--space-xs);
  border-radius: var(--radius-input);
  background: var(--color-success-soft);
  color: var(--color-success);
  font-size: var(--text-xs);
  line-height: 1.5;
}

@media (max-width: 1100px) {
  .pal-editor-layout { grid-template-columns: minmax(0, 1fr); }
  .pal-summary { position: static; order: -1; }
}

@media (max-width: 760px) {
  .pal-workspace-header { position: static; }
  .pal-actions { flex-wrap: wrap; }
}
</style>
