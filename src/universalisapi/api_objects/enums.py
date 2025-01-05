"""
Enums for the allowable names of Universalis Regions.

Translation for non-English names was done by a mix of Google Translate and
using results from various non-English FFXIV Wikis. Please submit issues for
better names for some Enum names (especially for the World Enum)

"""

from enum import StrEnum


class Region(StrEnum):
    """Valid Region names for Universalis API endpoints."""

    JAPAN = "japan"
    EUROPE = "europe"
    NA = "north-america"
    OCEANIA = "oceania"
    CHINA = "china"
    CHINACHAR = "中国"


class DataCenter(StrEnum):
    """Valid DC names for Universalis API endpoints."""

    ELEMENTAL = "elemental"
    GAIA = "gaia"
    MANA = "mana"
    AETHER = "aether"
    PRIMAL = "primal"
    CHAOS = "chaos"
    LIGHT = "light"
    CRYSTAL = "crystal"
    MATERIA = "materia"
    METEOR = "meteor"
    DYNAMIS = "dynamis"
    NACLOUDDC = "na cloud dc (beta)"
    CHOCOBO = "陆行鸟"
    MOOGLE = "莫古力"
    FATCAT = "猫小胖"
    DODO = "豆豆柴"
    KOREA = "한국"


class World(StrEnum):
    """Valid World names for Universalis API endpoints."""

    RAVANA = "ravana"
    BISMARCK = "bismarck"
    ASURA = "asura"
    BELIAS = "belias"
    PANDAEMONIUM = "pandaemonium"
    SHINRYU = "shinryu"
    UNICORN = "unicorn"
    YOJIMBO = "yojimbo"
    ZEROMUS = "zeromus"
    TWINTANIA = "twintania"
    BRYNHILDR = "brynhildr"
    FAMFRIT = "famfrit"
    LICH = "lich"
    MATEUS = "mateus"
    OMEGA = "omega"
    JENOVA = "jenova"
    ZALERA = "zalera"
    ZODIARK = "zodiark"
    ALEXANDER = "alexander"
    ANIMA = "anima"
    CARBUNCLE = "carbuncle"
    FENRIR = "fenrir"
    HADES = "hades"
    IXION = "ixion"
    KUJATA = "kujata"
    TYPHON = "typhon"
    ULTIMA = "ultima"
    VALEFOR = "valefor"
    EXODUS = "exodus"
    FAERIE = "faerie"
    LAMIA = "lamia"
    PHOENIX = "phoenix"
    SIREN = "siren"
    GARUDA = "garuda"
    IFRIT = "ifrit"
    RAMUH = "ramuh"
    TITAN = "titan"
    DIABOLOS = "diabolos"
    GILGAMESH = "gilgamesh"
    LEVIATAHN = "leviathan"
    MIDGARDSORMR = "midgardsormr"
    ODIN = "odin"
    SHIVA = "shiva"
    ATOMOS = "atomos"
    BAHAMUT = "bahamut"
    CHOCOBO = "chocobo"
    MOOGLE = "moogle"
    TONBERRY = "tonberry"
    ADAMANTOISE = "adamantoise"
    COUELR = "coeurl"
    MALBORO ="malboro"
    TIAMAT = "tiamat"
    ULTROS = "ultros"
    BEHEMOTH = "behemoth"
    CACTUAR = "cactuar"
    CERBERUS = "cerberus"
    GOBLIN = "goblin"
    MANDRAGORA = "mandragora"
    LOUISOIX = "louisoix"
    SPRIGGAN = "spriggan"
    SEPHIROT = "sephirot"
    SOPHIA = "sophia"
    ZURVAN = "zurvan"
    AEGIS = "aegis"
    BALMUNG = "balmung"
    DURANDAL = "durandal"
    EXCALIBUR = "excalibur"
    GUNGNIR = "gungnir"
    HYPERION = "hyperion"
    MASAMUNE = "masamune"
    RAGNAROK = "ragnarok"
    RIDILL = "ridill"
    SARGATANAS = "sargatanas"
    SAGITTARIUS = "sagittarius"
    PHANTOM = "phantom"
    ALPHA = "alpha"
    RAIDEN = "raiden"
    MARILITH = "marilith"
    SERAPH = "seraph"
    HALICARNASSUS = "halicarnassus"
    MADUIN = "maduin"
    CUCHULAINN = "cuchulainn"
    KRAKEN = "kraken"
    RAFFLESIA = "rafflesia"
    GOLEM = "golem"
    CLOUDTEST1 = "cloudtest01"
    CLOUDTEST2 = "cloudtest02"
    RUBY_SEA = "红玉海"
    PROVIDENCE_POINT = "神意之地" # Area north of Dragonhead in Coerthas
    LA_NOSCEA = "拉诺西亚"
    ISLES_OF_UMBRA = "幻影群岛"
    HOPESEED_POND = "萌芽池"
    UNIVERSALIS_MARKETS = "宇宙和音" # Area in Crystarium
    VOOR_SIAN_SIRAN = "沃仙曦染"
    DAWN_THRONE = "晨曦王座"
    SHIROGANE = "白银乡"
    PLATINUM_MIRAGE = "白金幻象" # Markets in Ul'dah
    RHALGRS_REACH = "神拳痕"
    SHIOZAKE_HOSTELRY = "潮风亭" # Inn in Kugane
    PEREGRINATION_POINT = "旅人栈桥" # Traveler's Bridge? Wanderer's Palace first area
    AT_DAWN = "拂晓之间" # At Dawn? Scions of 7th dawn quest (level 17)
    THE_AERY = "龙巢神殿"
    LYHE_GHIAH = "梦羽宝境" # Treasure dungeon!
    AMETHYST_SHALLOWS = "紫水栈桥" # Lavender Beds area
    YANXIA = "延夏"
    HAUKKE_MANOR = "静语庄园"
    MOR_DHONA = "摩杜纳"
    UMINEKO_TEAHOUSE = "海猫茶屋"
    WHISPERWIND_COVE = "柔风海湾"
    FIELDS_OF_AMBER = "琥珀原" # Ahm Araeng zone
    CRYSTAL_TOWER = "水晶塔"
    SILVER_TEAR_LAKE = "银泪湖"
    COSTA_DEL_SOL = "太阳海岸"
    ISHGARD = "伊修加德"
    BLACK_TEA_BROOK = "红茶川" # River in Old Gridania
    AURUM_VALE = "黄金谷" # Yikes
    CRESCENT_COVE = "月牙湾"
    CEDARWOOD = "雪松原"
    KR_CARBUNCLE = "카벙클" # korean carbuncle
    KR_CHOCOBO = "초코보" # korean chocobo
    KR_MOOGLE = "모그리" # korean moogle
    KR_TONBERRY = "톤베리" # korean tonberry
    KR_FENRIR = "펜리르" # korean fenrir


type APIRegion = World | DataCenter | Region
