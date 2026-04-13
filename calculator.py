import math

def m5u5_4096(val: float) -> int:
    val = round(val, 5) # Deal with floating point inaccuracies
    int_part = math.floor(val)
    frac = val - int_part
    if frac <= 0.5:
        return int_part
    else:
        return int_part + 1

def get_modified_stat(stat_val: int, rank: int) -> int:
    rank = max(-6, min(6, rank))
    if rank > 0:
        return math.floor(stat_val * (2 + rank) / 2)
    elif rank < 0:
        return math.floor(stat_val * 2 / (2 - rank))
    return stat_val

def get_max_move_power(base_power: int, move_type: str, category: str) -> int:
    if category == "変化": return 0
    if move_type in ["かくとう", "どく"]:
        if base_power >= 150: return 100
        if base_power >= 110: return 95
        if base_power >= 75:  return 90
        if base_power >= 65:  return 85
        if base_power >= 55:  return 80
        if base_power >= 45:  return 75
        return 70
    else:
        if base_power >= 150: return 150
        if base_power >= 110: return 140
        if base_power >= 100: return 130
        if base_power >= 90:  return 120
        if base_power >= 75:  return 110
        if base_power >= 65:  return 100
        if base_power >= 55:  return 90
        if base_power >= 45:  return 80
        return 70

def get_z_move_power(base_power: int) -> int:
    if base_power >= 140: return 200
    if base_power >= 130: return 195
    if base_power >= 120: return 190
    if base_power >= 110: return 185
    if base_power >= 100: return 180
    if base_power >= 90:  return 175
    if base_power >= 80:  return 160
    if base_power >= 70:  return 140
    if base_power >= 60:  return 120
    return 100

def calculate_all_real_stats(base_stats: dict, evs: dict, nature_name: str) -> dict:
    from pokemon_data import natures
    real_stats = {}
    nature_info = natures.get(nature_name, {"up": None, "down": None})
    for stat_key in ["h", "a", "b", "c", "d", "s"]:
        base = base_stats.get(stat_key, 50)
        ev = evs.get(stat_key, 0)
        iv = 31
        if stat_key == "h":
            if base == 1:
                real_stats["h"] = 1
            else:
                real_stats["h"] = math.floor((base * 2 + iv + math.floor(ev / 4)) * 50 / 100) + 50 + 10
        else:
            core = math.floor((base * 2 + iv + math.floor(ev / 4)) * 50 / 100) + 5
            mod = 1.0
            if nature_info["up"] == stat_key: mod = 1.1
            if nature_info["down"] == stat_key: mod = 0.9
            real_stats[stat_key] = math.floor(core * mod)
    return real_stats

def calculate_damage(atk_stats, atk_types_original, def_stats, def_types_original, move,
                     atk_rank=0, def_rank=0, weather="なし", terrain="なし", 
                     is_critical=False, is_burn=False,
                     atk_tera=None, def_tera=None,
                     is_dynamax=False, is_zmove=False,
                     reflect=False, light_screen=False, stealth_rock=False, spikes=0, def_is_dynamax=False,
                     atk_item="なし", def_item="なし", atk_ability="なし", def_ability="なし",
                     ruin_ability="なし"): # ruin_ability kept for backward compatibility if needed, but handled inside abilities
    from pokemon_data import get_type_multiplier, items
    
    actual_power = move["power"]
    move_type = move["type"]

    # ==== 特性によるわざタイプと威力の書き換え（スキン系） ====
    if atk_ability == 'スカイスキン' and move_type == 'ノーマル':
        move_type = 'ひこう'; actual_power = math.floor(actual_power * 1.2)
    elif atk_ability == 'フェアリースキン' and move_type == 'ノーマル':
        move_type = 'フェアリー'; actual_power = math.floor(actual_power * 1.2)
    elif atk_ability == 'フリーズスキン' and move_type == 'ノーマル':
        move_type = 'こおり'; actual_power = math.floor(actual_power * 1.2)
    elif atk_ability == 'エレキスキン' and move_type == 'ノーマル':
        move_type = 'でんき'; actual_power = math.floor(actual_power * 1.2)

    # ==== ギミック反映 ====
    if is_dynamax:
        actual_power = get_max_move_power(actual_power, move_type, move["category"])
    elif is_zmove:
        actual_power = get_z_move_power(actual_power)
        
    atk_types = [atk_tera] if atk_tera and atk_tera != "なし" else atk_types_original
    def_types = [def_tera] if def_tera and def_tera != "なし" else def_types_original

    # ==== ステータス補正（こだいかっせい、アイテム等） ====
    a_stat = atk_stats["a"]
    c_stat = atk_stats["c"]
    b_stat = def_stats["b"]
    d_stat = def_stats["d"]

    # パラドックス特性チェック
    if atk_ability == 'こだいかっせい / クォークチャージ':
        highest = max([atk_stats["a"], atk_stats["b"], atk_stats["c"], atk_stats["d"], atk_stats["s"]])
        if highest == atk_stats["a"]: a_stat = math.floor(a_stat * 1.3)
        elif highest == atk_stats["c"]: c_stat = math.floor(c_stat * 1.3)
    
    if def_ability == 'こだいかっせい / クォークチャージ':
        highest = max([def_stats["a"], def_stats["b"], def_stats["c"], def_stats["d"], def_stats["s"]])
        if highest == def_stats["b"]: b_stat = math.floor(b_stat * 1.3)
        elif highest == def_stats["d"]: d_stat = math.floor(d_stat * 1.3)

    # アイテムでのステータス補正
    if items.get(atk_item, {}).get("type") == "stat_multi":
        if items[atk_item]["stat"] == "a": a_stat = math.floor(a_stat * items[atk_item]["val"])
        if items[atk_item]["stat"] == "c": c_stat = math.floor(c_stat * items[atk_item]["val"])
    if items.get(def_item, {}).get("type") == "stat_multi":
        if "b" in items[def_item]["stat"]: b_stat = math.floor(b_stat * items[def_item]["val"])
        if "d" in items[def_item]["stat"]: d_stat = math.floor(d_stat * items[def_item]["val"])

    # ==== ランク補正＆最終ステータス決定 ====
    if move["category"] == "物理":
        final_atk = get_modified_stat(a_stat, atk_rank)
        final_def = get_modified_stat(b_stat, def_rank)
        wall_active = reflect
        if weather == "ゆき" and "こおり" in def_types:
            final_def = math.floor(final_def * 1.5)
        # ちからもち
        if atk_ability == 'ちからもち / ヨガパワー': final_atk *= 2
        # ファーコート
        if def_ability == 'ファーコート': final_def *= 2
    else:
        final_atk = get_modified_stat(c_stat, atk_rank)
        final_def = get_modified_stat(d_stat, def_rank)
        wall_active = light_screen
        if weather == "すなあらし" and "いわ" in def_types:
            final_def = math.floor(final_def * 1.5)
        # こおりのりんぷん (特殊半減=特防2倍相当として扱う)
        if def_ability == 'こおりのりんぷん': final_def *= 2
        # サンパワー
        if atk_ability == 'サンパワー' and weather == "はれ": final_atk = math.floor(final_atk * 1.5)

    # ==== 四災特性 ====
    # ruin_ability, または個別のAbilityで判定
    if "わざわいのつるぎ" in [ruin_ability, atk_ability, def_ability] and move["category"] == "物理":
        if atk_ability != "わざわいのつるぎ": final_atk = math.floor(final_atk * 0.75) # 防御側のわざわいなら攻撃側の攻撃が下がる？いいえ、わざわいのつるぎは「自分以外の防御を0.75倍」
        # 厳密には：「防御が下がる」。自分がつるぎなら相手の防御を下げる。自分がつるぎじゃないなら自分の防御が下がる
    
    # 簡易実装（対象の防御や特攻を下げる）
    active_ruins = {ruin_ability, atk_ability, def_ability}
    if "わざわいのつるぎ" in active_ruins and move["category"] == "物理" and def_ability != "わざわいのつるぎ":
        final_def = math.floor(final_def * 0.75)
    if "わざわいのたま" in active_ruins and move["category"] == "特殊" and def_ability != "わざわいのたま":
        final_def = math.floor(final_def * 0.75)
    if "わざわいのおふだ" in active_ruins and move["category"] == "物理" and atk_ability != "わざわいのおふだ":
        final_atk = math.floor(final_atk * 0.75)
    if "わざわいのうつわ" in active_ruins and move["category"] == "特殊" and atk_ability != "わざわいのうつわ":
        final_atk = math.floor(final_atk * 0.75)

    # ==== 技の威力補正アイテム＆特性 ====
    power_mod = 4096
    
    # 特性での威力補正
    if atk_ability == 'かたいツメ' and move.get('is_contact'): power_mod = m5u5_4096(power_mod * 5325 / 4096) # 1.3x
    if atk_ability == 'パンクロック' and move.get('is_sound'): power_mod = m5u5_4096(power_mod * 5325 / 4096)
    if atk_ability == 'てつのこぶし' and move.get('is_punch'): power_mod = m5u5_4096(power_mod * 4915 / 4096) # 1.2x
    if atk_ability == 'きれあじ' and move.get('is_slice'): power_mod = m5u5_4096(power_mod * 6144 / 4096) # 1.5x
    if atk_ability == 'がんじょうあご' and move.get('is_bite'): power_mod = m5u5_4096(power_mod * 6144 / 4096)
    if atk_ability == 'すいほう' and move_type == 'みず': power_mod = m5u5_4096(power_mod * 8192 / 4096) # 2.0x
    if atk_ability == 'トランジスタ' and move_type == 'でんき': power_mod = m5u5_4096(power_mod * 5325 / 4096) # 1.3x in SV
    if atk_ability == 'りゅうのあぎと' and move_type == 'ドラゴン': power_mod = m5u5_4096(power_mod * 6144 / 4096)
    if atk_ability == 'はがねのせいしん' and move_type == 'はがね': power_mod = m5u5_4096(power_mod * 6144 / 4096)
    if atk_ability == 'すなのちから' and weather == 'すなあらし' and move_type in ['いわ', 'じめん', 'はがね']: power_mod = m5u5_4096(power_mod * 5325 / 4096)
    
    # アイテムでの威力補正
    itm = items.get(atk_item, {})
    if itm.get('type') == 'dmg_multi_punch' and move.get('is_punch'): power_mod = m5u5_4096(power_mod * 4505 / 4096) # 1.1x
    if itm.get('type') == 'dmg_multi_same_type': power_mod = m5u5_4096(power_mod * 4915 / 4096) # 1.2x

    if power_mod != 4096: actual_power = m5u5_4096(actual_power * power_mod / 4096)

    # ==== 基礎ダメージの計算 ====
    base1 = math.floor(50 * 2 / 5) + 2
    base2 = math.floor(base1 * actual_power * final_atk / max(1, final_def))
    base_damage = math.floor(base2 / 50) + 2

    # ==== ダメージ計算オプション ====
    # 天候・フィールド
    weather_mod = 4096
    if weather == "はれ":
        if move_type == "ほのお": weather_mod = 6144
        elif move_type == "みず": weather_mod = 2048
    elif weather == "あめ":
        if move_type == "みず": weather_mod = 6144
        elif move_type == "ほのお": weather_mod = 2048
    
    if def_ability == 'すいほう' and move_type == 'ほのお': weather_mod = 2048 # すいほうの炎半減

    terrain_mod = 4096
    if terrain == "エレキ" and move_type == "でんき": terrain_mod = 5325
    elif terrain == "グラス" and move_type == "くさ": terrain_mod = 5325
    elif terrain == "サイコ" and move_type == "エスパー": terrain_mod = 5325
    elif terrain == "ミスト" and move_type == "ドラゴン": terrain_mod = 2048

    # 壁
    wall_mod = 4096
    if wall_active and not is_critical:
        wall_mod = 2048 # シングルなので0.5

    # 急所
    crit_mod = 4096
    if is_critical:
        crit_mod = 6144 if atk_ability != 'スナイパー' else 9216 # 1.5x or 2.25x

    # Parent Bond (おやこあい)
    parental_bond = (atk_ability == 'おやこあい')

    def calc_roll(r, is_second_hit=False):
        d = base_damage
        if crit_mod != 4096: d = m5u5_4096(d * crit_mod / 4096)
        
        # おやこあいの2撃目
        if is_second_hit:
            d = m5u5_4096(d * 1024 / 4096) # 0.25x
            
        d = math.floor(d * r / 100)
        
        # タイプ一致 (STAB)
        stab_mod = 4096
        if atk_tera and atk_tera != "なし":
            if move_type == atk_tera:
                if atk_tera in atk_types_original:
                    stab_mod = 8192 if atk_ability == 'てきおうりょく' else 8192 # テラス一致適応力は2.25xだが簡易化
                    if atk_ability == 'てきおうりょく': stab_mod = 9216
                else:
                    stab_mod = 6144
            elif move_type in atk_types_original:
                stab_mod = 6144
        else:
            if move_type in atk_types:
                stab_mod = 8192 if atk_ability == 'てきおうりょく' else 6144
                
        if stab_mod != 4096: d = m5u5_4096(d * stab_mod / 4096)

        # タイプ相性
        type_mod = get_type_multiplier(move_type, def_types)
        d = math.floor(d * type_mod)

        # 最終ダメージ補正（アイテム等）
        final_mod = 4096
        # アイテム
        if itm.get('type') == 'dmg_multi': final_mod = m5u5_4096(final_mod * 5325 / 4096) # 生命の珠
        if itm.get('type') == 'dmg_multi_se' and type_mod > 1: final_mod = m5u5_4096(final_mod * 4915 / 4096) # 達人の帯
        if itm.get('type') == 'dmg_multi_phys' and move["category"] == "物理": final_mod = m5u5_4096(final_mod * 4505 / 4096)
        if itm.get('type') == 'dmg_multi_spec' and move["category"] == "特殊": final_mod = m5u5_4096(final_mod * 4505 / 4096)
        if itm.get('type') == 'dmg_multi_type' and move_type == itm.get('target_type'): final_mod = m5u5_4096(final_mod * 5325 / 4096)
        
        if items.get(def_item, {}).get('type') == 'def_dmg_multi_se' and type_mod > 1: final_mod = m5u5_4096(final_mod * 2048 / 4096) # 半減のみ

        # 特性（防御側）
        if def_ability == 'マルチスケイル / ファントムガード': final_mod = m5u5_4096(final_mod * 2048 / 4096)
        if def_ability == 'もふもふ':
            if move.get('is_contact'): final_mod = m5u5_4096(final_mod * 2048 / 4096)
            if move_type == 'ほのお': final_mod = m5u5_4096(final_mod * 8192 / 4096)
        if def_ability == 'フィルター / ハードロック / プリズムアーマー' and type_mod > 1:
            final_mod = m5u5_4096(final_mod * 3072 / 4096) # 0.75x
            
        if final_mod != 4096: d = m5u5_4096(d * final_mod / 4096)

        # やけど
        burn_mod = 2048 if is_burn and move["category"] == "物理" else 4096
        if burn_mod != 4096: d = m5u5_4096(d * burn_mod / 4096)
        
        # 天候・フィールド・壁
        if weather_mod != 4096: d = m5u5_4096(d * weather_mod / 4096)
        if terrain_mod != 4096: d = m5u5_4096(d * terrain_mod / 4096)
        if wall_mod != 4096: d = m5u5_4096(d * wall_mod / 4096)
        
        return max(1, d) if type_mod > 0 else 0

    damage_rolls_1 = [calc_roll(r) for r in range(85, 101)]
    if parental_bond:
        damage_rolls_2 = [calc_roll(r, is_second_hit=True) for r in range(85, 101)]
        base_damage_array = [d1 + d2 for d1 in damage_rolls_1 for d2 in damage_rolls_2]
    else:
        base_damage_array = damage_rolls_1

    target_hp = def_stats["h"]
    if def_is_dynamax: target_hp *= 2

    hazard_dmg = 0
    if stealth_rock:
        rock_mod = get_type_multiplier("いわ", def_types_original)
        hazard_dmg += math.floor(target_hp * 0.125 * rock_mod)
    if spikes > 0 and "ひこう" not in def_types_original:
        spikes_frac = [0, 1/8, 1/6, 1/4][min(3, spikes)]
        hazard_dmg += math.floor(target_hp * spikes_frac)

    eff_hp = max(1, target_hp - hazard_dmg)

    min_dmg = min(base_damage_array)
    max_dmg = max(base_damage_array)
    min_pct = round(min_dmg / target_hp * 100, 1)
    max_pct = round(max_dmg / target_hp * 100, 1)

    hits_msg = "無効"
    ko_prob_msg = ""
    
    if max_dmg > 0:
        current_dist = {0: 1}
        total_combinations = 1
        found_ko = False
        
        for hits in range(1, 6):
            next_dist = {}
            for d, count in current_dist.items():
                for roll in base_damage_array:
                    new_d = d + roll
                    next_dist[new_d] = next_dist.get(new_d, 0) + count
            
            current_dist = next_dist
            total_combinations *= len(base_damage_array)
            
            ko_count = sum(count for d, count in current_dist.items() if d >= eff_hp)
            if ko_count == total_combinations:
                hits_msg = f"確定{hits}発"
                ko_prob_msg = ""
                found_ko = True
                break
            elif ko_count > 0:
                prob = ko_count / total_combinations * 100
                hits_msg = f"乱数{hits}発"
                ko_prob_msg = f"({prob:.2f}%)"
                found_ko = True
                break
                
        if not found_ko:
            hits_msg = f"確定{math.ceil(eff_hp / max_dmg)}発"
            ko_prob_msg = ""

    if parental_bond and hits_msg != "無効":
        hits_msg += " (2回ずつ)"

    type_mod_raw = get_type_multiplier(move_type, def_types)
    eff_msg = "効果は バツグンだ！" if type_mod_raw > 1 else "効果は いまひとつのようだ" if type_mod_raw < 1 and type_mod_raw > 0 else "効果がないみたいだ" if type_mod_raw == 0 else ""

    return {
        "min_damage": min_dmg,
        "max_damage": max_dmg,
        "min_pct": min_pct,
        "max_pct": max_pct,
        "hazard_pct": round(hazard_dmg / target_hp * 100, 1),
        "hits_msg": hits_msg,
        "ko_prob_msg": ko_prob_msg,
        "effectiveness": eff_msg,
        "type_mod": type_mod_raw,
        "crit_mod": is_critical,
        "stab": (move["type"] in atk_types) or (atk_tera == move["type"])
    }
