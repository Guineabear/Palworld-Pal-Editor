import time
from bs4 import BeautifulSoup
import requests
import json
import re
import os
import sys
from urllib.parse import unquote

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

# URLs for the different languages
urls = {
    "en": "https://paldb.cc/en/Active_Skills",
    "zh-CN": "https://paldb.cc/cn/Active_Skills",
    "ja": "https://paldb.cc/ja/Active_Skills",
    "fr": "https://paldb.cc/fr/Active_Skills",
}
requested_languages = os.environ.get("PAL_EDITOR_UPDATE_LANGS", ",".join(urls))
active_languages = [lang.strip() for lang in requested_languages.split(",") if lang.strip()]


def skill(internal_name):
    return {
        "InternalName": internal_name,
        "Element": "",
        "CT": -1,
        "Power": -1,
        "I18n": {
            "en": {"Name": "", "Description": ""},
            "zh-CN": {"Name": "", "Description": ""},
            "ja": {"Name": "", "Description": ""},
            "fr": {"Name": "", "Description": ""},
        },
        "UniqueSkill": False,
        "SkillFruit": False,
    }


def clean_description(description):
    description = (
        description.strip()
        .replace("。 ", "。")
        .replace("， ", "，")
        .replace("、 ", "、")
    )
    description = re.sub(r"\s+", " ", description)
    description = re.sub(r"\s+", " ", description)
    description = re.sub(r"\s+\.", ".", description)
    description = re.sub(r"\s+。", ".", description)
    description = re.sub(r"\s+;", ";", description)
    return description

el_map = {
    "Fire": "Flame",
    "Ground": "Earth",
    "Ice": "Frost",
}


def get_node_id(lang, type):
    return {
        "en": {
            "ActiveSkills": "ActiveSkills",
            "BossActiveSkills": "BossActiveSkills",
            "UnrevealedActiveSkills": "UnrevealedActiveSkills",
        },
        "zh-CN": {
            "ActiveSkills": "主动技能",
            "BossActiveSkills": "Boss主动技能",
            "UnrevealedActiveSkills": "Unrevealed主动技能",
        },
        "ja": {
            "ActiveSkills": "アクティブスキル",
            "BossActiveSkills": "Bossアクティブスキル",
            "UnrevealedActiveSkills": "Unrevealedアクティブスキル",
        },
        "fr": {
            "ActiveSkills": "Compétencesactives",
            "BossActiveSkills": "BossCompétencesactives",
            "UnrevealedActiveSkills": "UnrevealedCompétencesactives",
        },
    }[lang][type]


def extract_skills():
    skills_data = {}

    for lang in active_languages:
        url = urls[lang]
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for type in ["ActiveSkills", "BossActiveSkills", "UnrevealedActiveSkills"]:
            skills_div = soup.find(id=get_node_id(lang, type))

            if skills_div:
                cards = skills_div.find_all("div", class_="col")
                for card in cards:
                    name_node = card.find(
                        "a", attrs={"data-hover": re.compile(r"Waza")}
                    )

                    if name_node is None:
                        continue

                    internal_name = (
                        unquote(name_node["data-hover"])
                        .split("/")[-1]
                        .strip()
                    )
                    name = name_node.text.strip()
                    desc = clean_description(
                        card.find("div", attrs={"class": "card-body"}).text
                    )
                    if internal_name in skills_data:
                        if type == "UnrevealedActiveSkills":
                            if not name or "text" in re.split(r'[_ ]', name.lower()):
                                name = skills_data[internal_name]["I18n"]["en"]["Name"]
                            if not desc or "text" in re.split(r'[_ ]', desc.lower()):
                                desc = skills_data[internal_name]["I18n"]["en"]["Description"]

                        skills_data[internal_name]["I18n"][lang] = {
                            "Name": name,
                            "Description": desc,
                        }
                        continue

                    skill_data = skill(internal_name)
                    if type == "UnrevealedActiveSkills":
                        skill_data["Invalid"] = True
                    
                    skill_data["I18n"][lang] = {"Name": name, "Description": desc}

                    skill_data["UniqueSkill"] = (
                        True
                        if card.find("img", {"data-bs-title": "Will not inherit"})
                        else False
                    )

                    try:
                        el = card.find("span", {"style": "padding-left: 35px"}).text
                        skill_data["Element"] = el

                        ct_pw = card.find_all("span", {"style": "color: #73ffff"})

                        ct = int(ct_pw[0].text)
                        skill_data["CT"] = ct

                        power = int(ct_pw[1].text)
                        skill_data["Power"] = power

                        fruit = card.find(
                            "img",
                            {
                                "src": f"https://cdn.paldb.cc/image/Others/InventoryItemIcon/Texture/T_itemicon_Consume_SkillCard_{el_map.get(el, el)}.webp"
                            },
                        )

                        if fruit:
                            skill_data["SkillFruit"] = True
                    except:
                        print(f"{card.find_all('span')}")

                    print(json.dumps(skill_data, indent=4))
                    skills_data[skill_data["InternalName"]] = skill_data
    return skills_data


# Fetch and parse HTML for each language
all_skills = extract_skills()
with open("../data/pal_attacks.json", "r", encoding="utf-8") as existing_file:
    existing_skills = json.load(existing_file)
for internal_name, existing_skill in existing_skills.items():
    all_skills.setdefault(internal_name, existing_skill)
for internal_name, skill_data in all_skills.items():
    if not skill_data["Element"] or skill_data["CT"] < 0 or skill_data["Power"] < 0:
        skill_data["Invalid"] = True
    existing_i18n = existing_skills.get(internal_name, {}).get("I18n", {})
    for lang in urls:
        if lang not in active_languages:
            skill_data["I18n"][lang] = existing_i18n.get(lang) or skill_data["I18n"]["en"]
skills_json = json.dumps(all_skills, indent=4, ensure_ascii=False)
with open("tmp_pal_attacks.json", "w", encoding="utf-8") as file:
    file.write(skills_json)
