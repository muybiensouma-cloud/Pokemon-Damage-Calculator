import streamlit as st
from pokemon_data import pokemons, moves, natures, items, abilities
from calculator import calculate_all_real_stats, calculate_damage

def kata2hira(text):
    return text.translate({i: i - 96 for i in range(ord('ァ'), ord('ヶ') + 1)})

def hira2kata(text):
    return text.translate({i: i + 96 for i in range(ord('ぁ'), ord('ゖ') + 1)})

def format_with_hira(k):
    return k

import json
import os
from streamlit_local_storage import LocalStorage
localS = LocalStorage()

USER_DATA_FILE = "user_data.json"

SESSION_KEYS = [
    "atk_name", "def_name", "move_name",
    "atk_evs", "def_evs", "atk_nature", "def_nature",
    "atk_rank", "def_rank", "weather", "terrain",
    "atk_item", "def_item", "atk_ability", "def_ability",
    "atk_tera", "def_tera", "atk_gimmick", "def_gimmick"
]

def save_presets(data):
    localS.setItem("pc_presets", json.dumps({"presets": data}, ensure_ascii=False))


def load_state(new_state):
    for k, v in new_state.items():
        if k in st.session_state:
            # specifically clone dicts so they don't share ref
            if isinstance(v, dict): st.session_state[k] = v.copy()
            else: st.session_state[k] = v
            # mirror to ui
            if "ui_"+k in st.session_state: st.session_state["ui_"+k] = v
    if "def_tera" in new_state: st.session_state["def_tera_sel"] = new_state["def_tera"]
    if "def_nature" in new_state: st.session_state["def_nat"] = new_state["def_nature"]

def swap_roles():
    temp = {}
    for k in SESSION_KEYS:
        val = st.session_state.get(k)
        temp[k] = val.copy() if isinstance(val, dict) else val
        
    for k in SESSION_KEYS:
        if k.startswith("atk_"):
            d_key = "def_" + k[4:]
            st.session_state[k] = temp.get(d_key)
            if "ui_"+k in st.session_state: st.session_state["ui_"+k] = temp.get(d_key)
        elif k.startswith("def_"):
            a_key = "atk_" + k[4:]
            st.session_state[k] = temp.get(a_key)
            if "ui_"+k in st.session_state: st.session_state["ui_"+k] = temp.get(a_key)
            
    if "def_tera" in st.session_state: st.session_state["def_tera_sel"] = st.session_state["def_tera"]
    if "def_nature" in st.session_state: st.session_state["def_nat"] = st.session_state["def_nature"]

ls_item = localS.getItem("pc_presets")
if "presets" not in st.session_state:
    if ls_item:
        try: st.session_state.presets = json.loads(ls_item).get("presets", [])
        except: st.session_state.presets = []
    else:
        st.session_state.presets = []

# 状態の初期化
ls_def = localS.getItem("pc_default")
ls_cfg = localS.getItem("pc_app_config")

if "app_config" not in st.session_state:
    st.session_state.app_config = {"clear_chat": True}
    if ls_cfg:
        try:
            import json
            st.session_state.app_config.update(json.loads(ls_cfg))
        except: pass

if "app_init" not in st.session_state:
    if ls_def:
        try: load_state(json.loads(ls_def))
        except: pass
    st.session_state.app_init = True
    
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "atk_name" not in st.session_state: st.session_state.atk_name = "コライドン"
if "def_name" not in st.session_state: st.session_state.def_name = "ディンルー"
if "move_name" not in st.session_state: st.session_state.move_name = "フレアドライブ"

if "atk_evs" not in st.session_state: st.session_state.atk_evs = {"h": 0, "a": 252, "b": 0, "c": 0, "d": 0, "s": 252}
if "def_evs" not in st.session_state: st.session_state.def_evs = {"h": 0, "a": 0, "b": 0, "c": 0, "d": 0, "s": 0}

if "atk_nature" not in st.session_state: st.session_state.atk_nature = "いじっぱり (A↑ C↓)"
if "def_nature" not in st.session_state: st.session_state.def_nature = "わんぱく (B↑ C↓)"

if "atk_rank" not in st.session_state: st.session_state.atk_rank = 0
if "def_rank" not in st.session_state: st.session_state.def_rank = 0

if "weather" not in st.session_state: st.session_state.weather = "なし"
if "terrain" not in st.session_state: st.session_state.terrain = "なし"
if "is_critical" not in st.session_state: st.session_state.is_critical = False
if "is_burn" not in st.session_state: st.session_state.is_burn = False
if "atk_item" not in st.session_state: st.session_state.atk_item = "なし"
if "def_item" not in st.session_state: st.session_state.def_item = "なし"
if "atk_ability" not in st.session_state: st.session_state.atk_ability = "なし"
if "def_ability" not in st.session_state: st.session_state.def_ability = "なし"

# Gimmick states
if "atk_tera" not in st.session_state: st.session_state.atk_tera = "なし"
if "def_tera" not in st.session_state: st.session_state.def_tera = "なし"
if "atk_gimmick" not in st.session_state: st.session_state.atk_gimmick = "通常"
if "def_gimmick" not in st.session_state: st.session_state.def_gimmick = "通常"
if "reflect" not in st.session_state: st.session_state.reflect = False
if "light_screen" not in st.session_state: st.session_state.light_screen = False
if "stealth_rock" not in st.session_state: st.session_state.stealth_rock = False
if "spikes" not in st.session_state: st.session_state.spikes = 0
if "ruin" not in st.session_state: st.session_state.ruin = "なし"

st.set_page_config(page_title="PokemonChampions Calc", page_icon="⚡", layout="wide")

def mega_toggle_atk():
    gim = st.session_state.atk_gimmick
    curr = st.session_state.ui_atk_name
    if gim == "メガシンカ":
        cand = "メガ" + curr
        if cand in pokemons: 
            st.session_state.ui_atk_name = cand
            st.session_state.atk_name = cand
        elif cand + "X" in pokemons:
            st.session_state.ui_atk_name = cand + "X"
            st.session_state.atk_name = cand + "X"
    elif gim == "通常":
        if curr.startswith("メガ"):
            base = curr[2:]
            if base.endswith("X") or base.endswith("Y"): base = base[:-1]
            if base in pokemons: 
                st.session_state.ui_atk_name = base
                st.session_state.atk_name = base

def mega_toggle_def():
    gim = st.session_state.def_gimmick
    curr = st.session_state.ui_def_name
    if gim == "メガシンカ":
        cand = "メガ" + curr
        if cand in pokemons: 
            st.session_state.ui_def_name = cand
            st.session_state.def_name = cand
        elif cand + "X" in pokemons:
            st.session_state.ui_def_name = cand + "X"
            st.session_state.def_name = cand + "X"
    elif gim == "通常":
        if curr.startswith("メガ"):
            base = curr[2:]
            if base.endswith("X") or base.endswith("Y"): base = base[:-1]
            if base in pokemons: 
                st.session_state.ui_def_name = base
                st.session_state.def_name = base


# CSS ハック
st.markdown("""
<style>
.block-container { padding-top: 2rem !important; padding-bottom: 160px !important; }
</style>
""", unsafe_allow_html=True)

# サイドバー
with st.sidebar:
    st.markdown("""
        <div style='text-align: left; margin-bottom: 20px;'>
            <img src='https://www.pokemonchampions.jp/assets/img/common/logo@1x.webp' style='height: 55px; margin-bottom: 10px; object-fit: contain; display: block;'>
            <h2 style='margin: 0; font-size: 1.2rem; line-height: 1.3;'>PokemonChampions<br>ダメージ計算ツール</h2>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<hr style='margin: 5px 0; border: none; border-top: 1px solid #ddd;'>", unsafe_allow_html=True)
    with st.form("chat_form", clear_on_submit=st.session_state.app_config["clear_chat"]):
        chat_input = st.text_area("文章でスピード入力\n（例: カイリューのげきりんをパオジアンに）", height=100)
        submitted = st.form_submit_button("設定を反映", use_container_width=True)
        
    with st.expander("使い方を表示"):
        st.markdown("""
        - **自動反映**: 「HBサザンドラ」と入力で努力値を自動MAX(252)。
        - **文脈理解**: 「CSメガカイリュー を チョッキサザンドラ に」等、近いポケモンの持ち物や状態として自動判別します。
        - **略称対応**: 意地、全振、珠、タスキなどの略称入力に対応。
        """)

    if submitted and chat_input:
        text_full = hira2kata(chat_input)
        import re
        
        # 1. Pokemon extraction
        found_pokes = []
        temp_text = text_full
        for p in sorted(pokemons.keys(), key=len, reverse=True):
            p_kata = hira2kata(p)
            while p_kata in temp_text:
                idx = temp_text.find(p_kata)
                found_pokes.append((idx, p))
                temp_text = temp_text[:idx] + " "*len(p_kata) + temp_text[idx+len(p_kata):]
        found_pokes.sort()
        if len(found_pokes) >= 1:
            st.session_state.atk_name = found_pokes[0][1]
            st.session_state.ui_atk_name = found_pokes[0][1]
        if len(found_pokes) >= 2:
            st.session_state.def_name = found_pokes[1][1]
            st.session_state.ui_def_name = found_pokes[1][1]
            
        # 2. Extract Moves
        found_moves = []
        temp_text = text_full
        for m in sorted(moves.keys(), key=len, reverse=True):
            m_kata = hira2kata(m)
            while m_kata in temp_text:
                idx = temp_text.find(m_kata)
                found_moves.append((idx, m))
                temp_text = temp_text[:idx] + " "*len(m_kata) + temp_text[idx+len(m_kata):]
        found_moves.sort()
        if len(found_moves) >= 1:
            st.session_state.move_name = found_moves[0][1]
            st.session_state.ui_move_name = found_moves[0][1]

        # --- Proximity Helper ---
        pos_atk = text_full.find(hira2kata(st.session_state.atk_name)) if st.session_state.atk_name else -1
        pos_def = text_full.find(hira2kata(st.session_state.def_name)) if st.session_state.def_name else -1
        
        def assign_to_closest(attr_pos, atk_key, def_key, val):
            if attr_pos == -1: return
            if pos_def != -1 and pos_atk != -1:
                if abs(attr_pos - pos_def) < abs(attr_pos - pos_atk):
                    st.session_state[def_key] = val
                else:
                    st.session_state[atk_key] = val
            elif pos_def != -1:
                st.session_state[def_key] = val
            else:
                st.session_state[atk_key] = val

        # 3. Extract Items
        item_synonyms = {
            "ハチマキ": "こだわりハチマキ", "鉢巻": "こだわりハチマキ",
            "メガネ": "こだわりメガネ", "眼鏡": "こだわりメガネ",
            "スカーフ": "こだわりスカーフ",
            "珠": "いのちのたま", "タマ": "いのちのたま",
            "チョッキ": "とつげきチョッキ",
            "タスキ": "きあいのタスキ", "襷": "きあいのタスキ",
            "残飯": "たべのこし", "ザンパン": "たべのこし"
        }
        for syn, real_item in item_synonyms.items():
            kata_syn = hira2kata(syn)
            if kata_syn in text_full:
                assign_to_closest(text_full.find(kata_syn), "atk_item", "def_item", real_item)
                
        for i in items.keys():
            if i != "なし":
                kata_i = hira2kata(i)
                if kata_i in text_full:
                    assign_to_closest(text_full.find(kata_i), "atk_item", "def_item", i)

        # 4. Extract Abilities
        for a in abilities:
            if a != "なし":
                kata_a = hira2kata(a)
                if kata_a in text_full:
                    assign_to_closest(text_full.find(kata_a), "atk_ability", "def_ability", a)

        # 5. Extract Weather / Terrains
        weathers_list = ["はれ", "あめ", "すなあらし", "ゆき"]
        terrains_list = ["グラス", "エレキ", "サイコ", "ミスト"]
        for w in weathers_list:
            if hira2kata(w) in text_full:
                st.session_state.weather = w
        for t in terrains_list:
            if hira2kata(t) in text_full:
                st.session_state.terrain = t

        # 6. Natures & EVs
        nature_syns = {
            "イジ": "いじっぱり", "意地": "いじっぱり",
            "ヨウキ": "ようき", "陽気": "ようき",
            "ヒカエメ": "ひかえめ", "控えめ": "ひかえめ",
            "オクビョウ": "おくびょう", "臆病": "おくびょう",
            "ノンキ": "のんき", "呑気": "のんき"
        }
        for syn, real_n_base in nature_syns.items():
            kata_syn = hira2kata(syn)
            if kata_syn in text_full:
                for full_n in natures.keys():
                    if full_n.startswith(real_n_base):
                        assign_to_closest(text_full.find(kata_syn), "atk_nature", "def_nature", full_n)
                        break
                
        # Regex for EVs
        # 1. Matches like "AS252"
        for match in re.finditer(r'([HhAaBbCcDdSs]+)\s*(\d{1,3})', chat_input):
            stats_str = match.group(1).lower()
            val = int(match.group(2))
            pos_ev = match.start()
            target_evs = st.session_state.def_evs if (pos_def != -1 and pos_atk != -1 and abs(pos_ev - pos_def) < abs(pos_ev - pos_atk)) else st.session_state.atk_evs
            for char in set(stats_str):
                if char in target_evs: target_evs[char] = val
                
        # 2. Keywords like "AS全振", "HBブッパ", "HD特化"
        for match in re.finditer(r'([A-Za-z]+)\s*(?:ブッパ|全振|特化)', text_full):
            stats_str = match.group(1).lower()
            pos_ev = match.start()
            target_evs = st.session_state.def_evs if (pos_def != -1 and pos_atk != -1 and abs(pos_ev - pos_def) < abs(pos_ev - pos_atk)) else st.session_state.atk_evs
            for char in set(stats_str):
                if char in target_evs: target_evs[char] = 252

        # 3. 2-3 Letter Standalone Combinations like "CS", "AS", "HB"
        for match in re.finditer(r'(?<![A-Za-z])([HhAaBbCcDdSs]{2,3})(?![A-Za-z0-9])', chat_input):
            stats_str = match.group(1).lower()
            pos_ev = match.start()
            target_evs = st.session_state.def_evs if (pos_def != -1 and pos_atk != -1 and abs(pos_ev - pos_def) < abs(pos_ev - pos_atk)) else st.session_state.atk_evs
            for char in set(stats_str):
                if char in target_evs: target_evs[char] = 252

        # 7. Mega Evolution Gimmick Auto-Toggle & Item Restriction
        if st.session_state.atk_name.startswith("メガ"):
            st.session_state.atk_gimmick = "メガシンカ"
            st.session_state.atk_item = "なし"
        else:
            st.session_state.atk_gimmick = "通常"

        if st.session_state.def_name.startswith("メガ"):
            st.session_state.def_gimmick = "メガシンカ"
            st.session_state.def_item = "なし"
        else:
            st.session_state.def_gimmick = "通常"


        
    st.markdown("<hr style='margin: 10px 0; border: none; border-top: 1px solid #ddd;'><h4 style='margin-bottom: 8px; font-size: 1rem;'>お気に入り構成</h4>", unsafe_allow_html=True)
    if st.button(":material/bookmark: 現在の構成を保存", use_container_width=True):
        preset_name = f"{st.session_state.atk_name} vs {st.session_state.def_name}"
        current_state = {k: st.session_state.get(k) for k in SESSION_KEYS}
        st.session_state.presets.append({"name": preset_name, "state": current_state})
        save_presets(st.session_state.presets)
        
    if st.session_state.presets:
        for i, preset in enumerate(st.session_state.presets):
            if st.button(preset["name"], key=f"preset_{i}", use_container_width=True):
                load_state(preset["state"])
                st.rerun()

    st.markdown("<hr style='margin: 20px 0; border: none; border-top: 1px solid #ddd;'>", unsafe_allow_html=True)
    with st.popover(":material/settings: アプリ設定", use_container_width=True):
        st.markdown("**🎨 テーマ変更について**")
        st.caption("画面右上の「⋮」メニュー ＞ Settings ＞ Theme から自由に変更可能です！")
        
        st.markdown("<hr style='margin: 12px 0; border-top: 1px dashed #ccc;'>", unsafe_allow_html=True)
        
        st.markdown("**🗑️ データの初期化 (キャッシュクリア)**")
        st.caption("保存した「お気に入り構成」「デフォルト設定」など全てを削除してスッキリさせます。")
        if st.button("すべてのデータを完全削除", use_container_width=True):
            localS.setItem("pc_default", "")
            localS.setItem("pc_presets", "")
            localS.setItem("pc_app_config", "")
            st.session_state.presets = []
            st.success("全て削除しました！再読み込みで適用されます。")
            
        st.markdown("<hr style='margin: 12px 0; border-top: 1px dashed #ccc;'>", unsafe_allow_html=True)
        
        st.markdown("**💬 チャットの挙動**")
        st.caption("スピード入力の送信後に、書いた文章を自動で消去するかそのまま残しておくかを選べます。")
        def update_chat_config():
            st.session_state.app_config["clear_chat"] = st.session_state.temp_clear_chat
            localS.setItem("pc_app_config", json.dumps(st.session_state.app_config, ensure_ascii=False))
        st.toggle("送信後に文章を自動消去する", value=st.session_state.app_config["clear_chat"], key="temp_clear_chat", on_change=update_chat_config)
            
        st.markdown("<hr style='margin: 12px 0; border-top: 1px dashed #ccc;'>", unsafe_allow_html=True)

        st.markdown("**🚀 起動時のデフォルト構成**")
        st.caption("現在の画面のすべて（ポケモン・努力値・持ち物など）をスマホ/PCに記録し、次回起動時の初期状態にします。")
        if st.button(":material/save: 現在の構成をデフォルトにする", use_container_width=True):
            current_state = {k: st.session_state.get(k) for k in SESSION_KEYS}
            localS.setItem("pc_default", json.dumps(current_state, ensure_ascii=False))
            st.success("記憶しました！次回起動時から適用されます。")
        if st.button(":material/delete: デフォルト設定をリセット", use_container_width=True):
            localS.setItem("pc_default", "")
            st.success("初期化しました！")
    # 環境ギミック選択はメイン側に移動




types_list = ["なし", "ノーマル", "ほのお", "みず", "でんき", "くさ", "こおり", "かくとう", "どく", "じめん", "ひこう", "エスパー", "むし", "いわ", "ゴースト", "ドラゴン", "あく", "はがね", "フェアリー"]

# UI Helper functions for Pokemon Image and Stats
def render_pokemon_card(poke_name, is_atk=True):
    p_data = pokemons.get(poke_name, {})
    if not p_data: return
    
    # Use custom image url from pokemon_data if specified, otherwise fallback to official-artwork
    img_url = p_data.get("img_url", f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{p_data.get('id', 1)}.png")
    type_badges = "".join([f'<span style="background-color: #6c757d; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.8em; margin-right: 5px;">{t}</span>' for t in p_data.get("types", [])])
    
    stats = p_data.get("base_stats", {})
    stats_str = f"H{stats.get('h',0)} A{stats.get('a',0)} B{stats.get('b',0)} C{stats.get('c',0)} D{stats.get('d',0)} S{stats.get('s',0)}"
    
    st.markdown(f'''
    <div style="display: flex; align-items: center; border-radius: 8px; margin-bottom: 15px;">
        <img src="{img_url}" style="height: 90px; width: 90px; object-fit: contain; margin-right: 15px;">
        <div>
            <div style="font-size: 1.3em; font-weight: 900; margin-bottom: 4px;">{poke_name}</div>
            <div style="margin-bottom: 4px;">{type_badges}</div>
            <div style="font-size: 0.85em; font-weight: bold; opacity: 0.8;">{stats_str}</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)


st.markdown("<br>", unsafe_allow_html=True)
st.button(":material/swap_horiz: 攻守を入れ替える", use_container_width=True, on_click=swap_roles)
col1, col2 = st.columns(2)

# ATK COLUMN
with col1:
    st.markdown("<div style='background-color: #d9534f; color: white; padding: 5px 15px; border-radius: 4px; font-weight: bold; margin-bottom: 10px;'>攻撃側 (Attacker)</div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.session_state.atk_name = st.selectbox("ポケモン選択", list(pokemons.keys()), format_func=format_with_hira, key="ui_atk_name", index=list(pokemons.keys()).index(st.session_state.atk_name))
        
        render_pokemon_card(st.session_state.atk_name, is_atk=True)
        
        c1, c2 = st.columns([2, 1])
        st.session_state.move_name = c1.selectbox("攻撃技", list(moves.keys()), format_func=format_with_hira, key="ui_move_name", index=list(moves.keys()).index(st.session_state.move_name))
        st.session_state.atk_tera = c2.selectbox("テラスタル (攻撃)", types_list, format_func=format_with_hira, index=types_list.index(st.session_state.atk_tera))
        
        g_opts = ["通常", "メガシンカ", "Zわざ", "ダイマックス"]
        st.radio("攻撃側 世代ギミック", g_opts, horizontal=True, key="atk_gimmick", on_change=mega_toggle_atk)
        
        st.markdown("**持ち物・特性**")
        st.session_state.atk_item = st.selectbox("持ち物 (攻撃)", list(items.keys()), format_func=format_with_hira, index=list(items.keys()).index(st.session_state.atk_item))
        st.session_state.atk_ability = st.selectbox("特性 (攻撃)", abilities, format_func=format_with_hira, index=abilities.index(st.session_state.atk_ability))
        
        st.markdown("**ステータス調整**")
        st.session_state.atk_nature = st.selectbox("性格 (攻撃)", list(natures.keys()), index=list(natures.keys()).index(st.session_state.atk_nature))
        
        c1, c2 = st.columns(2)
        st.session_state.atk_evs["a"] = c1.slider("A 努力値", 0, 252, st.session_state.atk_evs["a"], step=4)
        st.session_state.atk_evs["c"] = c2.slider("C 努力値", 0, 252, st.session_state.atk_evs["c"], step=4)

        st.session_state.atk_rank = st.selectbox("A/C ランク (攻撃)", list(range(-6, 7)), index=list(range(-6, 7)).index(st.session_state.atk_rank))

        c1, c2 = st.columns(2)
        st.session_state.is_critical = c1.checkbox("急所", value=st.session_state.is_critical)
        st.session_state.is_burn = c2.checkbox("やけど", value=st.session_state.is_burn)

# DEF COLUMN
with col2:
    st.markdown("<div style='background-color: #0275d8; color: white; padding: 5px 15px; border-radius: 4px; font-weight: bold; margin-bottom: 10px;'>防御側 (Defender)</div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.session_state.def_name = st.selectbox("ポケモン選択", list(pokemons.keys()), format_func=format_with_hira, key="ui_def_name", index=list(pokemons.keys()).index(st.session_state.def_name))
        
        render_pokemon_card(st.session_state.def_name, is_atk=False)
        
        st.session_state.def_tera = st.selectbox("テラスタル (防御)", types_list, format_func=format_with_hira, key="def_tera_sel", index=types_list.index(st.session_state.def_tera))
        
        g_opts_def = ["通常", "メガシンカ", "ダイマックス"]
        st.radio("防御側 世代ギミック", g_opts_def, horizontal=True, key="def_gimmick", on_change=mega_toggle_def)
        
        st.markdown("**持ち物・特性**")
        st.session_state.def_item = st.selectbox("持ち物 (防御)", list(items.keys()), format_func=format_with_hira, index=list(items.keys()).index(st.session_state.def_item))
        st.session_state.def_ability = st.selectbox("特性 (防御)", abilities, format_func=format_with_hira, index=abilities.index(st.session_state.def_ability))
        
        st.markdown("**ステータス調整**")
        st.session_state.def_nature = st.selectbox("性格 (防御)", list(natures.keys()), key="def_nat", index=list(natures.keys()).index(st.session_state.def_nature))
        
        c1, c2, c3 = st.columns(3)
        st.session_state.def_evs["h"] = c1.slider("H 努力値", 0, 252, st.session_state.def_evs["h"], step=4)
        st.session_state.def_evs["b"] = c2.slider("B 努力値", 0, 252, st.session_state.def_evs["b"], step=4)
        st.session_state.def_evs["d"] = c3.slider("D 努力値", 0, 252, st.session_state.def_evs["d"], step=4)

        st.session_state.def_rank = st.selectbox("B/D ランク (防御)", list(range(-6, 7)), index=list(range(-6, 7)).index(st.session_state.def_rank))

        st.markdown("**防御状態**")
        c1, c2 = st.columns(2)
        st.session_state.reflect = c1.checkbox("リフレクター", value=st.session_state.reflect)
        st.session_state.light_screen = c2.checkbox("ひかりのかべ", value=st.session_state.light_screen)
        
        c1, c2 = st.columns(2)
        st.session_state.stealth_rock = c1.checkbox("ステルスロック", value=st.session_state.stealth_rock)
        st.session_state.spikes = c2.selectbox("まきびし", [0, 1, 2, 3], index=st.session_state.spikes)


# ==========================
# 3. 環境ギミック設定
# ==========================
st.markdown("### 環境ギミック")
env_col1, env_col2 = st.columns(2)
weathers = ["なし", "はれ", "あめ", "すなあらし", "ゆき"]
st.session_state.weather = env_col1.selectbox("天候", weathers, index=weathers.index(st.session_state.weather))
terrains = ["なし", "グラス", "エレキ", "サイコ", "ミスト"]
st.session_state.terrain = env_col2.selectbox("フィールド", terrains, index=terrains.index(st.session_state.terrain))

# ==========================
# 4. 計算実行
# ==========================
atk_base = pokemons[st.session_state.atk_name]["base_stats"]
def_base = pokemons[st.session_state.def_name]["base_stats"]

atk_real_stats = calculate_all_real_stats(atk_base, st.session_state.atk_evs, st.session_state.atk_nature)
def_real_stats = calculate_all_real_stats(def_base, st.session_state.def_evs, st.session_state.def_nature)

move_data = moves[st.session_state.move_name]
atk_types = pokemons[st.session_state.atk_name]["types"]
def_types = pokemons[st.session_state.def_name]["types"]

result = calculate_damage(
    atk_real_stats, atk_types,
    def_real_stats, def_types,
    move_data,
    atk_rank=st.session_state.atk_rank,
    def_rank=st.session_state.def_rank,
    weather=st.session_state.weather,
    terrain=st.session_state.terrain,
    is_critical=st.session_state.is_critical,
    is_burn=st.session_state.is_burn,
    atk_tera=st.session_state.atk_tera,
    def_tera=st.session_state.def_tera,
    is_dynamax=(st.session_state.atk_gimmick == "ダイマックス"),
    is_zmove=(st.session_state.atk_gimmick == "Zわざ"),
    reflect=st.session_state.reflect,
    light_screen=st.session_state.light_screen,
    ruin_ability=st.session_state.ruin,
    stealth_rock=st.session_state.stealth_rock,
    spikes=st.session_state.spikes,
    def_is_dynamax=(st.session_state.def_gimmick == "ダイマックス"),
    atk_item=st.session_state.atk_item,
    def_item=st.session_state.def_item,
    atk_ability=st.session_state.atk_ability,
    def_ability=st.session_state.def_ability
)

# ==========================
# 4. Sticky Bottom UI Render
# ==========================
hazard_pct = result.get('hazard_pct', 0)
rem_min = max(0, 100 - result['max_pct'] - hazard_pct)
rem_max = max(0, 100 - result['min_pct'] - hazard_pct)
if rem_min > 50: hp_color = "#38b000"
elif rem_min > 25: hp_color = "#ffbc00"
else: hp_color = "#ef233c"

effectiveness_html = f"<div style='font-weight: bold; color: #155724; font-size: 0.85em;'>{result['effectiveness']}</div>" if result['effectiveness'] else ""

sticky_html = f'''
<style>
.sticky-bottom-result {{
position: fixed; bottom: 0; left: 0; width: 100%;
background-color: #ffffff; border-top: 1px solid #e0e0e0;
padding: 15px 5%; z-index: 999999; box-shadow: 0px -4px 15px rgba(0,0,0,0.08);
}}
</style>
<div class="sticky-bottom-result">
<div style="max-width: 1000px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center;">

<!-- LEFT: Damage Amount -->
<div style="flex: 1; text-align: right; padding-right: 20px;">
<div style="font-size: 1.25em; font-weight: 900; color: #d9534f; line-height: 1.1;">{result['min_damage']} 〜 {result['max_damage']}</div>
<div style="font-size: 0.8em; font-weight: bold; color: #444; margin-top: 2px;">ダメージ ({result['min_pct']}% 〜 {result['max_pct']}%)</div>
</div>

<!-- CENTER: HP Bar -->
<div style="flex: 2; padding: 0 10px;">
<div style="width: 100%; display: flex; align-items: center; justify-content: flex-end; margin-bottom: 2px;">
<span style="font-size: 0.7em; color: #888; font-weight: bold; margin-right: 2px;">HP</span>
</div>
<div style="width: 100%; background-color: #e9ecef; border-radius: 4px; height: 10px; display: flex;">
<div style="width: {rem_min}%; background-color: {hp_color}; height: 100%; transition: width 0.3s ease-out;"></div>
<div style="width: {rem_max - rem_min}%; background-color: #90e0ef; height: 100%; transition: width 0.3s ease-out;"></div>
<div style="flex: 1; background-color: transparent;"></div>
<div style="width: {hazard_pct}%; background-color: #555555; height: 100%;"></div>
</div>
<div style="margin-top: 4px; text-align: center;">{effectiveness_html}</div>
</div>

<!-- RIGHT: Hits Msg & Percentages -->
<div style="flex: 1; padding-left: 20px;">
<div style="font-size: 1.3em; font-weight: bold; color: #333; line-height: 1.1;">{result['hits_msg']}</div>
<div style="font-size: 0.9em; color: #666; font-weight: bold; margin-top: 2px;">{result.get('ko_prob_msg', '')}</div>
</div>
</div>
</div>
'''

st.markdown(sticky_html, unsafe_allow_html=True)
