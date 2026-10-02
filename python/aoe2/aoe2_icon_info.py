# -*- coding: utf-8 -*-
"""AoE2 图标分类表：说明文字中 @图标@ 的文件名 → 类别与中文名。

type: "unit"（兵种）/ "tech"（科技）/ "building"（建筑本体，不进入流程要点）。
未收录的图标按所在建筑文件夹兜底分类（见 rts_overlay.py），名称显示英文原名；
本表可持续补充中文条目。
"""

AOE2_ICON_INFO = {
    # --- 兵种 ---
    "Knight_aoe2DE": {"type": "unit", "name": "骑士"},
    "Scoutcavalry_aoe2DE": {"type": "unit", "name": "侦察骑兵"},
    "Archer_aoe2DE": {"type": "unit", "name": "弩手"},
    "Archer_aoe2de": {"type": "unit", "name": "弩手"},
    "Hand_cannoneer_aoe2DE": {"type": "unit", "name": "手炮兵"},
    "Monk_aoe2DE": {"type": "unit", "name": "僧侣"},
    "Bombard_cannon_aoe2DE": {"type": "unit", "name": "巨型投石机"},
    "Skirmisher_aoe2DE": {"type": "unit", "name": "掷矛兵"},
    "Steppelancericon": {"type": "unit", "name": "草原枪兵"},
    "Battering_ram_aoe2DE": {"type": "unit", "name": "冲撞车"},
    "Heavyscorpion_aoe2DE": {"type": "unit", "name": "重型弩炮"},
    # --- 科技 ---
    "BloodlinesDE": {"type": "tech", "name": "血统"},
    "FletchingDE": {"type": "tech", "name": "箭羽"},
    "Forging_aoe2de": {"type": "tech", "name": "锻造"},
    "IronCastingDE": {"type": "tech", "name": "铸造"},
    "HorseCollarDE": {"type": "tech", "name": "马轭"},
    "DoubleBitAxeDE": {"type": "tech", "name": "双刃斧"},
    "DoubleBitAxe_aoe2DE": {"type": "tech", "name": "双刃斧"},
    "LoomDE": {"type": "tech", "name": "织布"},
    "GoldShaftMiningDE": {"type": "tech", "name": "采金"},
    "WheelbarrowDE": {"type": "tech", "name": "独轮车"},
    "Hand_Cart_aoe2DE": {"type": "tech", "name": "手推车"},
    "PaddedArcherArmorDE": {"type": "tech", "name": "弓箭手护甲"},
    "Scale_Mail_aoe2DE": {"type": "tech", "name": "鳞甲"},
    "Ballistics_aoe2DE": {"type": "tech", "name": "弹道学"},
    "Chemistry_aoe2DE": {"type": "tech", "name": "化学"},
    "CoinageDE": {"type": "tech", "name": "铸币"},
    "PlateBardingArmorDE": {"type": "tech", "name": "骑兵板甲"},
    "ChainBardingArmorDE": {"type": "tech", "name": "骑兵锁甲"},
    # --- 建筑本体（排除，不进入流程要点）---
    "Mill_aoe2de": {"type": "building", "name": "磨坊"},
    "Lumber_camp_aoe2de": {"type": "building", "name": "伐木场"},
    "Mining_camp_aoe2de": {"type": "building", "name": "采矿场"},
    "Blacksmith_aoe2de": {"type": "building", "name": "铁匠铺"},
    "Market_aoe2DE": {"type": "building", "name": "市场"},
    "Barracks_aoe2DE": {"type": "building", "name": "兵营"},
    "Archery_range_aoe2DE": {"type": "building", "name": "射箭场"},
    "Stable_aoe2DE": {"type": "building", "name": "马厩"},
    "Towncenter_aoe2DE": {"type": "building", "name": "城镇中心"},
    "MonasteryAoe2DE": {"type": "building", "name": "修道院"},
    "Siege_workshop_aoe2DE": {"type": "building", "name": "攻城武器厂"},
    "FarmDE": {"type": "building", "name": "农田"},
    "House_aoe2DE": {"type": "building", "name": "房屋"},
    "Palisade_wall_aoe2de": {"type": "building", "name": "木墙"},
    "Tower_aoe2de": {"type": "building", "name": "塔"},
}


# buildorderguide.com 新版导出的裸标识符兼容表（无 @ 包裹、驼峰命名）
# 值为渲染行片段：@图标@ / 图标+文字+图标 可自由组合；渲染器会自动匹配 webp/png/jpg
AOE2_NOTE_TOKEN_COMPAT = {
    "foodUnderTC": "@resource/Aoe2de_food@ under @town_center/Towncenter_aoe2DE@",
    "woodUnderTC": "@resource/Aoe2de_wood@ under @town_center/Towncenter_aoe2DE@",
    "stragglerTree": "@resource/tree@",
    "feudalAge": "@age/FeudalAgeIconDE@",
    "castleAge": "@age/CastleAgeIconDE@",
    "darkAge": "@age/DarkAgeIconDE@",
    "imperialAge": "@age/ImperialAgeIconDE@",
    "doubleBitAxe": "@lumber_camp/DoubleBitAxe_aoe2de@",
    "goldShaftMining": "@mining_camp/GoldShaftMiningDE@",
    "horseCollar": "@mill/HorseCollarDE@",
    "loom": "@town_center/LoomDE@",
    "wheelbarrow": "@mill/WheelbarrowDE@",
    "bloodlines": "@stable/BloodlinesDE@",
    "fletching": "@blacksmith/FletchingDE@",
    "forging": "@blacksmith/Forging_aoe2de@",
    "barracks": "@barracks/Barracks_aoe2DE@",
    "stable": "@stable/Stable_aoe2DE@",
}
