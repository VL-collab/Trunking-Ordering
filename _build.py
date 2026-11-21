# -*- coding: utf-8 -*-
"""Build index.html from the Lik Hung trunking catalogue PDF."""
import base64
import io
import json
from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(r"D:\AI\Cursor\Trunking Ordering")
PDF = ROOT / "Trunking21 - 25v2.pdf"
TEMPLATE = ROOT / "_ui.html"

COVER = [{"id": "QT", "label": "肚臍蓋 QT"}, {"id": "ST", "label": "螺絲蓋 ST"}, {"id": "CT", "label": "彈夾蓋 CT"}]
FLANGE = [{"id": "SG", "label": "單摺邊 SG"}, {"id": "RG", "label": "勾摺邊 RG"}]
FINISH = [
    {"id": "GI", "label": "鍍鋅鋼"},
    {"id": "H", "label": "熱浸鋅 H"},
    {"id": "S", "label": "304 不銹鋼 S"},
    {"id": "X", "label": "316 不銹鋼 X"},
]
COMP3 = [{"id": "", "label": "標準"}, {"id": "D", "label": "2 倉"}, {"id": "T", "label": "3 倉"}]
ENDSTYLE = [{"id": "built", "label": "茜身連駁"}, {"id": "plain", "label": "普通平邊"}]
LID_UF = [{"id": "A", "label": "密封蓋 A"}, {"id": "B", "label": "活動蓋 B"}]

TS = [
    ("50 × 50", "2X2", "T10"),
    ("75 × 50", "3X2", "T12"),
    ("75 × 75", "3X3", "T12"),
    ("100 × 75", "4X3", "T12"),
    ("100 × 100", "4X4", "T14"),
    ("150 × 100", "6X4", "T14"),
    ("150 × 150", "6X6", "T16"),
    ("200 × 150", "8X6", "T16"),
    ("200 × 200", "8X8", "T16"),
]
TS_LABELS = [a for a, _, _ in TS]
WT = TS[1:]

TRAY_W = [50, 75, 100, 150, 200, 300, 400, 500, 600, 700, 800, 900]
TRAY_N = [2, 3, 4, 6, 8, 12, 16, 20, 24, 28, 32, 36]
LAD_W = [150, 300, 450, 600, 900, 1000]


def sizes(edges, labels, cols, codes, fits=None):
    out = []
    for i, lab in enumerate(labels):
        dims = {edges[k]: str(cols[k][i]) for k in range(len(edges))}
        out.append({
            "id": lab,
            "label": lab,
            "fit": (fits[i] if fits else lab),
            "dims": dims,
            "code": codes[i],
        })
    return out


def repeat(v, n):
    return tuple([v] * n)


def product(**kwargs):
    kwargs.setdefault("unit", "件")
    kwargs.setdefault("edges", [])
    kwargs.setdefault("options", [])
    return kwargs


PRODUCTS = []


def add(item):
    for s in item["sizes"]:
        missing = [e for e in item["edges"] if e not in s["dims"]]
        if missing:
            raise SystemExit(f"{item['id']} size {s['id']} missing {missing}")
    PRODUCTS.append(item)


def trunk_family(pid, zh, en, group, img, edges, cols, bodies, blurb, length=None):
    add(product(
        id=pid, cat="trunking", group=group, zh=zh, en=en, img=img, blurb=blurb,
        edges=list(edges), length=length, unit="條" if length else "件",
        options=[{"key": "cover", "label": "槽蓋", "choices": COVER},
                 {"key": "comp", "label": "槽內間格", "choices": [{"id": "", "label": "單倉"}, {"id": "D", "label": "二倉 D"}, {"id": "T", "label": "多倉 T"}]}],
        prefixKey="cover", compSuffix=True,
        sizes=sizes(edges, TS_LABELS, cols, bodies),
    ))


# --- trunking straight ---
trunk_family(
    "ct-straight", "電線槽", "Cable Trunking", "直身線槽", "ct-body",
    "AB",
    [(50, 75, 75, 100, 100, 150, 150, 200, 200), (50, 50, 75, 75, 100, 100, 150, 150, 200)],
    [f"{c}{t}" for _, c, t in TS],
    "標準長度 2.44 m。A 闊、B 高。槽蓋可選肚臍蓋、螺絲蓋或彈夾蓋。",
    2.44,
)

MITRE_AB = [(125, 150, 150, 175, 175, 225, 225, 275, 275)] * 2
MITRE_DE = [(125, 125, 150, 150, 175, 175, 225, 225, 275)] * 2
trunk_family("ct-m90-f", "90° 斜角槽曲 · 正面蓋型", "90° Mitre Bend · Front Opening", "槽曲", "ct-m90-f",
             "ABCDE", MITRE_AB + [(106,) * 9] + MITRE_DE, [f"{c}.1{t}" for _, c, t in TS], "圖下尺寸表。C 為 106。")
trunk_family("ct-m90-i", "90° 斜角槽曲 · 內開蓋型", "90° Mitre Bend · Internal Opening", "槽曲", "ct-m90-i",
             "ABCDE", MITRE_AB + [(106,) * 9] + MITRE_DE, [f"{c}.2{t}" for _, c, t in TS], "圖下尺寸表。C 為 106。")
trunk_family("ct-m90-e", "90° 斜角槽曲 · 外開蓋型", "90° Mitre Bend · External Opening", "槽曲", "ct-m90-e",
             "ABCDE", MITRE_AB + [(106,) * 9] + MITRE_DE, [f"{c}.4B{t}" for _, c, t in TS], "圖下尺寸表。C 為 106。")
trunk_family("ct-s90-f", "90° 死角槽曲 · 正面蓋型", "90° Sharp Bend · Front Opening", "槽曲", "ct-s90-f",
             "ABCDE", MITRE_AB + [(75,) * 9] + MITRE_DE, [f"{c}.1A{t}" for _, c, t in TS], "圖下尺寸表。C 為 75。")
trunk_family("ct-s90-i", "90° 死角槽曲 · 內開蓋型", "90° Sharp Bend · Internal Opening", "槽曲", "ct-s90-i",
             "ABCDE", MITRE_AB + [(75,) * 9] + MITRE_DE, [f"{c}.2A{t}" for _, c, t in TS], "圖下尺寸表。C 為 75。")
trunk_family("ct-s90-e", "90° 死角槽曲 · 外開蓋型", "90° Sharp Bend · External Opening", "槽曲", "ct-s90-e",
             "ABCDE", MITRE_AB + [(75,) * 9] + MITRE_DE, [f"{c}.4A{t}" for _, c, t in TS], "圖下尺寸表。C 為 75。")

TEE_AB = [
    (100, 125, 125, 150, 150, 225, 225, 275, 275),
    (150, 175, 175, 200, 200, 300, 300, 350, 350),
]
TEE_DE = [
    (100, 100, 125, 125, 150, 175, 225, 225, 275),
    (150, 150, 175, 175, 200, 250, 300, 300, 350),
]
MITRE_C = (70, 70, 70, 70, 70, 106, 106, 106, 106)
SHARP_C = (50, 50, 50, 50, 50, 75, 75, 75, 75)
trunk_family("ct-mt-f", "斜角三叉 · 正面蓋型", "Mitre Tee · Front Opening", "三叉 / 十字", "ct-mt-f",
             "ABCDE", TEE_AB + [MITRE_C] + TEE_DE, [f"{c}.3{t}" for _, c, t in TS], "圖下尺寸表。100 mm 及以下 C 為 70，150 mm 起 C 為 106。")
trunk_family("ct-mt-t1", "斜角三叉 · 頂開蓋款式 1", "Mitre Tee · Top Opening Type 1", "三叉 / 十字", "ct-mt-t1",
             "ABCDE", TEE_AB + [MITRE_C] + TEE_DE, [f"{c}.13B1{t}" for _, c, t in TS], "圖下尺寸表。100 mm 及以下 C 為 70，150 mm 起 C 為 106。")
trunk_family("ct-mt-t2", "斜角三叉 · 頂開蓋款式 2", "Mitre Tee · Top Opening Type 2", "三叉 / 十字", "ct-mt-t2",
             "ABCDE", TEE_AB + [MITRE_C] + TEE_DE, [f"{c}.13B2{t}" for _, c, t in TS], "圖下尺寸表。100 mm 及以下 C 為 70，150 mm 起 C 為 106。")
trunk_family("ct-mt-i", "斜角三叉 · 內開蓋型", "Mitre Tee · Internal Opening", "三叉 / 十字", "ct-mt-i",
             "ABCDE", TEE_AB + [MITRE_C] + TEE_DE, [f"{c}.13CD{t}" for _, c, t in TS], "圖下尺寸表。100 mm 及以下 C 為 70，150 mm 起 C 為 106。")
trunk_family("ct-st-f", "死角三叉 · 正面蓋型", "Sharp Tee · Front Opening", "三叉 / 十字", "ct-st-f",
             "ABCDE", TEE_AB + [SHARP_C] + TEE_DE, [f"{c}.3A{t}" for _, c, t in TS], "圖下尺寸表。100 mm 及以下 C 為 50，150 mm 起 C 為 75。")
trunk_family("ct-st-t1", "死角三叉 · 頂開蓋款式 1", "Sharp Tee · Top Opening Type 1", "三叉 / 十字", "ct-st-t1",
             "ABCDE", TEE_AB + [SHARP_C] + TEE_DE, [f"{c}.13AB1{t}" for _, c, t in TS], "圖下尺寸表。100 mm 及以下 C 為 50，150 mm 起 C 為 75。")
trunk_family("ct-st-t2", "死角三叉 · 頂開蓋款式 2", "Sharp Tee · Top Opening Type 2", "三叉 / 十字", "ct-st-t2",
             "ABCDE", TEE_AB + [SHARP_C] + TEE_DE, [f"{c}.13AB2{t}" for _, c, t in TS], "圖下尺寸表。100 mm 及以下 C 為 50，150 mm 起 C 為 75。")
trunk_family("ct-st-i", "死角三叉 · 內開蓋型", "Sharp Tee · Internal Opening", "三叉 / 十字", "ct-st-i",
             "ABCDE", TEE_AB + [SHARP_C] + TEE_DE, [f"{c}.13ACD{t}" for _, c, t in TS], "圖下尺寸表。100 mm 及以下 C 為 50，150 mm 起 C 為 75。")

B135_A = (95, 105, 105, 116, 116, 137, 137, 157, 157)
B135_D = (95, 95, 105, 105, 116, 116, 137, 137, 157)
trunk_family("ct-135-f", "135° 斜角槽曲 · 正面蓋型", "135° Bend · Front Opening", "槽曲", "ct-135-f",
             "ABCD", [B135_A, (75,) * 9, B135_A, B135_D], [f"{c}.11A{t}" for _, c, t in TS], "135° 正面蓋。")
trunk_family("ct-135-i", "135° 斜角槽曲 · 內開蓋型", "135° Bend · Internal Opening", "槽曲", "ct-135-i",
             "ABCD", [B135_A, (75,) * 9, B135_A, B135_D], [f"{c}.11B{t}" for _, c, t in TS], "135° 內開蓋。")
trunk_family("ct-135-e", "135° 斜角槽曲 · 外開蓋型", "135° Bend · External Opening", "槽曲", "ct-135-e",
             "ABCD", [B135_A, (75,) * 9, B135_A, B135_D], [f"{c}.11C{t}" for _, c, t in TS], "135° 外開蓋。")

CROSS_A = (150, 175, 175, 200, 200, 300, 300, 350, 350)
CROSS_D = (150, 150, 175, 175, 200, 250, 300, 300, 350)
trunk_family("ct-x-f", "90° 十字槽曲 · 正曲型", "90° Mitre Cross · Flat Bend", "三叉 / 十字", "ct-x-f",
             "ABCDE", [CROSS_A, CROSS_A, (70, 70, 70, 70, 70, 106, 106, 106, 106), CROSS_D, CROSS_D],
             [f"{c}.5{t}" for _, c, t in TS], "十字正曲。")
trunk_family("ct-x-i", "90° 十字槽曲 · 內曲型", "90° Mitre Cross · Internal Bend", "三叉 / 十字", "ct-x-i",
             "ABCDE", [CROSS_A, CROSS_A, (70, 70, 70, 70, 70, 106, 106, 106, 106), CROSS_D, CROSS_D],
             [f"{c}.5CD{t}" for _, c, t in TS], "十字內曲。")

FL_A = (50, 75, 75, 100, 100, 150, 150, 200, 200)
FL_Y = (50, 50, 75, 75, 100, 100, 150, 150, 200)
trunk_family("ct-fl-top", "槽蓋刁士 · 喇叭咀", "Flared Connector · Top Opening", "刁士", "ct-fl-top",
             "ACXYZ", [FL_A, (50,) * 9, FL_A, FL_Y, (50,) * 9], [f"{c}.15A{t}" for _, c, t in TS], "頂開喇叭咀。")
trunk_family("ct-fl-90", "槽蓋刁士 · 頂開 90°", "Flared Connector · Top Opening 90°", "刁士", "ct-fl-90",
             "ACXYZ", [FL_A, (50,) * 9, FL_A, FL_Y, (50,) * 9], [f"{c}.15B{t}" for _, c, t in TS], "頂開 90° 槽蓋刁士。")
trunk_family("ct-fl-side", "槽蓋刁士 · 扭向槽口短蓋", "Flared Connector · Side Opening", "刁士", "ct-fl-side",
             "ACXYZ", [FL_A, (50,) * 9, FL_A, FL_Y, (50,) * 9], [f"{c}.17{t}" for _, c, t in TS], "扭向槽口短蓋。")

RED = [
    ("75×75 → 50×50", (150, 50, 75, 75, 50), "3X3.6T12"),
    ("100×50 → 50×50", (150, 50, 100, 50, 50), "4X2.6T12"),
    ("100×100 → 75×75", (150, 75, 100, 100, 75), "4X4.6T14"),
    ("150×100 → 100×100", (200, 100, 150, 100, 100), "6X4.6T14"),
    ("150×150 → 100×100", (200, 100, 150, 150, 100), "6X6.6T16"),
    ("200×200 → 150×150", (200, 150, 200, 200, 150), "8X8.6T16"),
]
for key, zh, img in (("L", "左刁士", "ct-red-l"), ("E", "正刁士", "ct-red-e"), ("R", "右刁士", "ct-red-r")):
    add(product(
        id="ct-red-" + key.lower(), cat="trunking", group="刁士",
        zh="刁士 · " + zh, en="Reducer · " + {"L": "Left", "E": "Equal", "R": "Right"}[key],
        img=img, blurb="同一尺寸的左 / 正 / 右刁士共用目錄型號，方向已寫在項目名稱。",
        edges=list("ABCDE"), prefixKey="cover",
        options=[{"key": "cover", "label": "槽蓋", "choices": COVER}],
        sizes=[{
            "id": lab, "label": lab, "fit": lab,
            "dims": dict(zip("ABCDE", map(str, dims))),
            "code": code,
        } for lab, dims, code in RED],
    ))

EC_A = (48, 48, 73, 73, 98, 98, 148, 148, 198)
EC_B = (48, 73, 73, 98, 98, 148, 148, 198, 198)
add(product(id="ct-end", cat="trunking", group="配件", zh="槽尾冚", en="End Cap", img="ct-end",
            blurb="槽尾封板。", edges=list("ABC"),
            sizes=sizes("ABC", TS_LABELS, [EC_A, EC_B, (25,) * 9], [f"ECS{c}" for _, c, _ in TS])))
add(product(id="ct-sup", cat="trunking", group="配件", zh="電線掛片", en="Cable Support", img="ct-sup",
            blurb="電線掛片。", edges=list("ABC"),
            sizes=sizes("ABC", TS_LABELS, [(250,) * 9, (45, 70, 70, 95, 95, 145, 145, 195, 195), (45, 45, 70, 70, 95, 95, 145, 145, 195)],
                        [f"CSF{c}" for _, c, _ in TS])))
add(product(id="ct-flg", cat="trunking", group="配件", zh="槽吊咀", en="Flange", img="ct-flg",
            blurb="槽吊咀。", edges=list("ABC"),
            sizes=sizes("ABC", TS_LABELS, [EC_A, EC_B, (25,) * 9], [f"FF{c}" for _, c, _ in TS])))

CPF_ROWS = [
    ("50 × 50", (40, 70, "-"), "CPF2"),
    ("75 × 50", (40, 70, "-"), "CPF2"),
    ("75 × 75", (68, 68, 35), "CPF3"),
    ("100 × 75", (68, 68, 35), "CPF3"),
    ("100 × 100", (92, 70, 60), "CPF4"),
    ("150 × 100", (92, 70, 60), "CPF4"),
    ("150 × 150", (143, 70, 111), "CPF6"),
    ("200 × 150", (143, 70, 111), "CPF6"),
    ("200 × 200", (194, 70, 160), "CPF8"),
]
add(product(id="ct-cpf", cat="trunking", group="配件", zh="對裝槽駁片", en="Couple Connector", img="ct-cpf",
            blurb="對裝槽駁片。沒有的邊長以 - 表示，仍可改成數字。", edges=list("ABC"),
            sizes=[{"id": a, "label": a, "fit": a, "dims": dict(zip("ABC", map(str, d))), "code": c} for a, d, c in CPF_ROWS]))
CPUF_ROWS = [
    ("50 × 50", (45, 70, "-", 48), "CPUF2X2"),
    ("75 × 50", (45, 70, "-", 73), "CPUF3X2"),
    ("75 × 75", (68, 68, 35, 73), "CPUF3X3"),
    ("100 × 75", (68, 68, 35, 98), "CPUF4X3"),
    ("100 × 100", (95, 70, 60, 98), "CPUF4X4"),
    ("150 × 100", (95, 70, 60, 148), "CPUF6X4"),
    ("150 × 150", (145, 70, 111, 148), "CPUF6X6"),
    ("200 × 150", (145, 70, 111, 198), "CPUF8X6"),
    ("200 × 200", (195, 70, 160, 198), "CPUF8X8"),
]
add(product(id="ct-cpuf", cat="trunking", group="配件", zh="U 型槽駁片", en="U-shaped Connector", img="ct-cpuf",
            blurb="U 型槽駁片。", edges=list("ABCD"),
            sizes=[{"id": a, "label": a, "fit": a, "dims": dict(zip("ABCD", map(str, d))), "code": c} for a, d, c in CPUF_ROWS]))
EL_ROWS = [
    ("一般商用", (0.6, 14, 48, 35), "EL75"),
    ("建築署", (1, 14, 57, 35), "EL100"),
    ("房屋署", (2, 12, 57, 35), "EL120"),
    ("地鐵 MTRC", (3, 25, 58, 35), "EL150"),
]
add(product(id="ct-el", cat="trunking", group="配件", zh="銅水線片", en="Copper Earth Link", img="ct-el",
            blurb="按工程種類選用。T 為厚度 mm。", edges=list("TABC"),
            sizes=[{"id": a, "label": a, "fit": a, "dims": dict(zip("TABC", map(str, d))), "code": c} for a, d, c in EL_ROWS]))


def tray_th(w):
    if w <= 150:
        return "T12", "T12", "T12", "T12"
    if w <= 400:
        return "T15", "T16", "T15", "T15"
    return "T20", "T20", "T15", "T15"


def tray_straight(prefix, edges, cols, img, zh, en, blurb):
    codes = []
    for w, n in zip(TRAY_W, TRAY_N):
        gi, h, s, x = tray_th(w)
        codes.append({"GI": f"{prefix}{n}{gi}", "H": f"{prefix}{n}{h}", "S": f"{prefix}{n}{s}", "X": f"{prefix}{n}{x}"})
    add(product(
        id="tr-" + prefix.lower(), cat="tray", group="直身托盤", zh=zh, en=en, img=img, blurb=blurb,
        edges=list(edges), length=2.44, unit="條", mapKey="finish",
        options=[{"key": "finish", "label": "表面處理", "choices": FINISH},
                 {"key": "end", "label": "茜身", "choices": ENDSTYLE}],
        sizes=sizes(edges, [str(w) for w in TRAY_W], cols, codes, fits=[str(w) for w in TRAY_W]),
    ))


tray_straight("SG", "AB", [tuple(TRAY_W), tuple(13 if w <= 200 else 20 for w in TRAY_W)],
              "tr-sg", "電纜托盤 · 單摺邊", "Cable Tray · Single Flange",
              "標準長度 2.44 m。A 闊，B 邊高。200 mm 及以下 B=13，其餘 B=20。")
tray_straight("RG", "ABC", [tuple(TRAY_W), (20,) * 12, (13,) * 12],
              "tr-rg", "電纜托盤 · 勾摺邊", "Cable Tray · Return Flange",
              "標準長度 2.44 m。A 闊，B=20，C=13。")


def tray_fit(pid, zh, en, img, edges, cols, suffix):
    bodies = []
    for w, n in zip(TRAY_W, TRAY_N):
        th = tray_th(w)[1] + "H" if False else None
        gi, h, s, x = tray_th(w)
        bodies.append(f"{n}.{suffix}{h}H" if not str(h).endswith("H") else f"{n}.{suffix}{h}")
    # tray_th returns T12 / T16 / T20 without H. Fittings in the catalogue are published as T12H / T16H / T20H.
    bodies = []
    for w, n in zip(TRAY_W, TRAY_N):
        token = {150: "T12H", 400: "T16H"}.get(0)
        if w <= 150:
            token = "T12H"
        elif w <= 400:
            token = "T16H"
        else:
            token = "T20H"
        bodies.append(f"{n}.{suffix}{token}")
    add(product(
        id=pid, cat="tray", group="托盤曲" if "曲" in zh or "135" in zh else "三叉 / 十字",
        zh=zh, en=en, img=img, blurb="型號以所選摺邊 SG 或 RG 作字首，厚度按目錄。",
        edges=list(edges), prefixKey="flange",
        options=[{"key": "flange", "label": "摺邊", "choices": FLANGE}],
        sizes=sizes(edges, [str(w) for w in TRAY_W], cols, bodies),
    ))


T90_B = (125, 150, 175, 225, 300, 400, 525, 625, 750, 850, 950, 1050)
T90_C = (106, 106, 106, 106, 141, 141, 177, 177, 212, 212, 212, 212)
T90_D = (150, 150, 150, 150, 175, 225, 275, 275, 325, 325, 325, 325)
tray_fit("tr-90-f", "90° 斜角茜曲 · 正曲", "90° Mitre Bend · Flat", "tr-90-f", "ABCDE",
         [tuple(TRAY_W), T90_B, T90_C, T90_D, (106,) * 12], "1")
tray_fit("tr-90-i", "90° 斜角茜曲 · 內曲", "90° Mitre Bend · Internal", "tr-90-i", "ABCDE",
         [tuple(TRAY_W), T90_B, T90_C, T90_D, (106,) * 12], "2")
tray_fit("tr-90-e", "90° 斜角茜曲 · 外曲", "90° Mitre Bend · External", "tr-90-e", "ABCDE",
         [tuple(TRAY_W), T90_B, T90_C, T90_D, (106,) * 12], "4B")
T135_B = (95, 106, 116, 137, 158, 224, 366, 407, 548, 590, 631, 673)
T135_C = (75, 75, 75, 75, 75, 100, 200, 200, 300, 300, 300, 300)
tray_fit("tr-135-f", "135° 斜角茜曲 · 正曲", "135° Bend · Flat", "tr-135-f", "ABCD",
         [tuple(TRAY_W), T135_B, T135_C, T135_C], "11A")
tray_fit("tr-135-i", "135° 斜角茜曲 · 內曲", "135° Bend · Internal", "tr-135-i", "ABCD",
         [tuple(TRAY_W), T135_B, T135_C, T135_C], "11B")
tray_fit("tr-135-e", "135° 斜角茜曲 · 外曲", "135° Bend · External", "tr-135-e", "ABCD",
         [tuple(TRAY_W), T135_B, T135_C, T135_C], "11C")
tray_fit("tr-tee", "托盤斜角三叉", "Tray Mitre Tee", "tr-tee", "ABC",
         [tuple(TRAY_W), T90_B, (200, 225, 250, 300, 400, 500, 650, 750, 900, 1000, 1100, 1200)], "3")
tray_fit("tr-cross", "托盤十字曲", "Tray Mitre Cross", "tr-cross", "AB",
         [tuple(TRAY_W), (200, 225, 250, 300, 400, 500, 650, 750, 900, 1000, 1100, 1200)], "5")

# fix groups that tray_fit guessed wrong for tee/cross — set explicitly
for p in PRODUCTS:
    if p["id"] in ("tr-tee", "tr-cross"):
        p["group"] = "三叉 / 十字"
    if p["id"].startswith("tr-135") or p["id"].startswith("tr-90"):
        p["group"] = "托盤曲"

TR_RED = [
    ("75 → 50", (150, 50, 75), "3.6T12H"),
    ("100 → 75", (150, 75, 100), "4.6T12H"),
    ("150 → 100", (200, 100, 150), "6.6T12H"),
    ("150 → 75", (200, 75, 150), "6.6T12H"),
    ("200 → 150", (200, 150, 200), "8.6T16H"),
    ("200 → 100", (200, 100, 200), "8.6T16H"),
    ("300 → 200", (300, 200, 300), "12.6T16H"),
    ("300 → 150", (300, 150, 300), "12.6T16H"),
    ("400 → 300", (400, 300, 400), "16.6T16H"),
    ("600 → 400", (500, 400, 600), "24.6T20H"),
]
for key, zh, img in (("l", "左刁士", "tr-red-l"), ("e", "正刁士", "tr-red-e"), ("r", "右刁士", "tr-red-r")):
    add(product(
        id="tr-red-" + key, cat="tray", group="刁士 / 駁片", zh="托盤刁士 · " + zh,
        en="Tray Reducer · " + {"l": "Left", "e": "Equal", "r": "Right"}[key], img=img,
        blurb="左 / 正 / 右共用目錄型號。", edges=list("ABC"), prefixKey="flange",
        options=[{"key": "flange", "label": "摺邊", "choices": FLANGE}],
        sizes=[{"id": lab, "label": lab, "fit": lab, "dims": dict(zip("ABC", map(str, d))), "code": code} for lab, d, code in TR_RED],
    ))

SGC = [(50, 40, "2"), (75, 65, "3"), (100, 90, "4"), (150, 140, "6"), (200, 190, "8"),
       (300, 290, "12"), (400, 390, "16"), (500, 490, "20"), (600, 590, "24"), (900, 890, "36")]
add(product(
    id="tr-sgc", cat="tray", group="刁士 / 駁片", zh="托盤駁片 · 普通款", en="Tray Connector · Common",
    img="tr-sgc", blurb="普通款茜駁片。A 為駁片長度。", edges=["A"], mapKey="finish", length=None,
    options=[{"key": "finish", "label": "表面處理", "choices": FINISH}],
    sizes=[{"id": str(w), "label": str(w), "fit": str(w), "dims": {"A": str(a)},
            "code": {"GI": f"SGC{n}", "H": f"SGC{n}H", "S": f"SGC{n}S", "X": f"SGC{n}X"}} for w, a, n in SGC],
))
add(product(
    id="tr-rgtz", cat="tray", group="刁士 / 駁片", zh="水務處規格茜旁駁", en="WSD Tray Side Connector",
    img="tr-rgtz",     blurb="水務處規格茜旁駁。圖上標示長度 150 mm、高度 38 mm，可修改。",
    edges=["長", "高"], mapKey="finish",
    options=[{"key": "finish", "label": "表面處理", "choices": FINISH}],
    sizes=[{"id": "150x38", "label": "150 × 38", "fit": "150 × 38", "dims": {"長": "150", "高": "38"},
            "code": {"GI": "RGTZ", "H": "RGTZH", "S": "RGTZS", "X": "RGTZX"}}],
))


def lad_fit(pid, zh, en, img, group, edges, cols, suffix):
    add(product(
        id=pid, cat="ladder", group=group, zh=zh, en=en, img=img,
        blurb="梯格距離 300 mm。側邊為 25×8 mm 長孔。",
        edges=list(edges),
        sizes=sizes(edges, [str(w) for w in LAD_W], cols, [f"CL{w}.{suffix}T20H" for w in LAD_W]),
    ))


add(product(
    id="ld-straight", cat="ladder", group="直身梯架", zh="電纜梯架", en="Cable Ladder", img="ld-straight",
    blurb="標準長度 2.44 m，厚度 2 mm。A 闊，B 邊高 100 mm。", edges=list("AB"), length=2.44, unit="條",
    sizes=sizes("AB", [str(w) for w in LAD_W], [tuple(LAD_W), (100,) * 6], [f"CL{w}T20H" for w in LAD_W]),
))
lad_fit("ld-90-f", "90° 斜角曲 · 正曲", "90° Mitre · Flat", "ld-90-f", "梯架曲", "ABCDEF",
        [tuple(LAD_W), (78,) * 6, (136,) * 6, (172, 234, 296, 359, 483, 524), (164, 252, 340, 427, 603, 662), (150,) * 6], "1")
lad_fit("ld-90-i", "90° 斜角曲 · 內曲", "90° Mitre · Internal", "ld-90-i", "梯架曲", "ABCDEF",
        [tuple(LAD_W), (78,) * 6, (136,) * 6, (172, 234, 296, 359, 483, 524), (164, 252, 340, 427, 603, 662), (150,) * 6], "2")
lad_fit("ld-90-e", "90° 斜角曲 · 外曲", "90° Mitre · External", "ld-90-e", "梯架曲", "ABCDEF",
        [tuple(LAD_W), (78,) * 6, (136,) * 6, (172, 234, 296, 359, 483, 524), (164, 252, 340, 427, 603, 662), (150,) * 6], "4B")
lad_fit("ld-135-f", "135° 斜角曲 · 正曲", "135° Bend · Flat", "ld-135-f", "梯架曲", "ABC",
        [tuple(LAD_W), (172, 234, 296, 359, 483, 524), (150,) * 6], "11A")
lad_fit("ld-135-i", "135° 斜角曲 · 內曲", "135° Bend · Internal", "ld-135-i", "梯架曲", "ABC",
        [tuple(LAD_W), (172, 234, 296, 359, 483, 524), (150,) * 6], "11B")
lad_fit("ld-135-e", "135° 斜角曲 · 外曲", "135° Bend · External", "ld-135-e", "梯架曲", "ABC",
        [tuple(LAD_W), (172, 234, 296, 359, 483, 524), (150,) * 6], "11C")
lad_fit("ld-tee", "梯架斜角三叉", "Ladder Mitre Tee", "ld-tee", "三叉 / 十字", "ABC",
        [tuple(LAD_W), (310, 460, 610, 760, 1060, 1160), (470, 620, 770, 920, 1220, 1320)], "3")
lad_fit("ld-cross", "梯架十字曲", "Ladder Mitre Cross", "ld-cross", "三叉 / 十字", "AB",
        [tuple(LAD_W), (470, 620, 770, 920, 1220, 1320)], "5")
LD_RED = [
    ("300 → 150", (150, 295, 300, 370), "CL300.6T20H"),
    ("450 → 300", (300, 295, 450, 370), "CL450.6T20H"),
    ("600 → 450", (450, 295, 600, 370), "CL600.6T20H"),
    ("900 → 600", (600, 370, 900, 520), "CL900.6T20H"),
    ("1200 → 900", (900, 370, 1200, 520), "CL1200.6T20H"),
]
for key, zh, img in (("l", "左刁士", "ld-red-l"), ("e", "正刁士", "ld-red-e"), ("r", "右刁士", "ld-red-r")):
    add(product(
        id="ld-red-" + key, cat="ladder", group="刁士", zh="梯架刁士 · " + zh,
        en="Ladder Reducer · " + {"l": "Left", "e": "Equal", "r": "Right"}[key], img=img,
        blurb="左 / 正 / 右共用目錄型號。", edges=list("ABCD"),
        sizes=[{"id": lab, "label": lab, "fit": lab, "dims": dict(zip("ABCD", map(str, d))), "code": code} for lab, d, code in LD_RED],
    ))

BASK_W = [100, 150, 300, 450, 600, 900]
BASK_N = ["4X4", "6X4", "12X4", "18X4", "24X4", "36X4"]
add(product(
    id="bk-straight", cat="basket", group="直身線籃", zh="電線籃", en="Cable Basket", img="bk-straight",
    blurb="直身線籃。A 闊，B 高（目錄為 100，可改 50），C 為長度 2122 mm。網格 50×50，枝徑 4 mm。",
    edges=list("ABC"), unit="條",
    sizes=sizes("ABC", [str(w) for w in BASK_W], [tuple(BASK_W), (100,) * 6, (2122,) * 6], [f"CAB{n}" for n in BASK_N]),
))
add(product(
    id="bk-90", cat="basket", group="線籃曲", zh="90° 籃曲", en="90° Basket Bend", img="bk-90",
    blurb="A 闊，B 高，C 為外側長度。", edges=list("ABC"),
    sizes=sizes("ABC", [str(w) for w in BASK_W],
                [tuple(BASK_W), (100,) * 6, (200, 250, 400, 550, 700, 1000)],
                [f"CAB{n}.1" for n in BASK_N]),
))
add(product(
    id="bk-tee", cat="basket", group="線籃曲", zh="線籃三叉", en="Basket Tee", img="bk-tee",
    blurb="A 闊，B、C 為兩臂長度。", edges=list("ABC"),
    sizes=sizes("ABC", [str(w) for w in BASK_W],
                [tuple(BASK_W), (200, 250, 400, 550, 700, 1000), (300, 350, 500, 650, 800, 1100)],
                [f"CAB{n}.3" for n in BASK_N]),
))
add(product(
    id="bk-plate", cat="basket", group="駁片", zh="線籃旁駁", en="Basket Connecting Plate", img="bk-plate",
    blurb="每對計。高度對應線籃高度。", edges=["H"], unit="對",
    sizes=[
        {"id": "50", "label": "50 高", "fit": "高度 50", "dims": {"H": "50"}, "code": "CABB1"},
        {"id": "100", "label": "100 高", "fit": "高度 100", "dims": {"H": "100"}, "code": "CABB2"},
    ],
))
KITS = [
    ("bk-k90-100", "自組 90° 曲套裝 · 100 高", "Self-assembly 90° Bend 100 mm", "CABB4.1", "L 型 ×1、斜邊 ×1、雙孔 ×2、單孔 ×6、螺絲套裝 ×10"),
    ("bk-k90-50", "自組 90° 曲套裝 · 50 高", "Self-assembly 90° Bend 50 mm", "CABB2.1", "L 型 ×1、斜邊 ×1、雙孔 ×1、單孔 ×3、螺絲套裝 ×5"),
    ("bk-ktee-100", "自組三叉套裝 · 100 高", "Self-assembly Tee 100 mm", "CABB4.3", "斜邊 ×2、單孔 ×8、螺絲套裝 ×8"),
    ("bk-ktee-50", "自組三叉套裝 · 50 高", "Self-assembly Tee 50 mm", "CABB2.3", "斜邊 ×2、單孔 ×4、螺絲套裝 ×4"),
]
for pid, zh, en, code, blurb in KITS:
    add(product(id=pid, cat="basket", group="自組套裝", zh=zh, en=en, img="bk-kit", blurb="每套包含：" + blurb, unit="套",
                sizes=[{"id": "set", "label": "套裝", "fit": "套裝", "dims": {}, "code": code}]))
PARTS = [
    ("bk-l100", "L 型旁駁 · 100 高", "L Connector 100 mm", "CABB4.L", "bk-l"),
    ("bk-l50", "L 型旁駁 · 50 高", "L Connector 50 mm", "CABB2.L", "bk-l"),
    ("bk-g100", "斜邊旁駁 · 100 高", "Angle Connector 100 mm", "CABB4.G", "bk-g"),
    ("bk-g50", "斜邊旁駁 · 50 高", "Angle Connector 50 mm", "CABB2.G", "bk-g"),
    ("bk-sgc2", "雙孔波浪型駁片", "Double-hole Flat Connector", "CABBSGC2", "bk-d"),
    ("bk-sgc1", "單孔波浪型駁片", "Single-hole Flat Connector", "CABBSGC1", "bk-s"),
    ("bk-screw", "螺絲套裝", "Screw Set", "CABBTAS", "bk-screw"),
]
for pid, zh, en, code, img in PARTS:
    add(product(id=pid, cat="basket", group="自組零件", zh=zh, en=en, img=img, blurb="可單獨訂購，亦已包含在自組套裝內。",
                unit="套" if "螺絲" in zh else "件",
                sizes=[{"id": "std", "label": "標準", "fit": "標準", "dims": {}, "code": code}]))

WT_LABELS = [a for a, _, _ in WT]
WT_AB = [(75, 75, 100, 100, 150, 150, 200, 200), (50, 75, 75, 100, 100, 150, 150, 200)]
add(product(
    id="wt-straight", cat="water", group="直身防水槽", zh="防水線槽", en="Waterproof Trunking", img="wt-body",
    blurb="螺絲蓋，槽邊有防水膠。標準長度 2.44 m。A 闊、B 高。", edges=list("AB"), length=2.44, unit="條",
    mapKey="comp",
    options=[{"key": "comp", "label": "槽內間格", "choices": [{"id": "", "label": "標準"}, {"id": "D", "label": "分格 D"}]}],
    sizes=[{
        "id": lab, "label": lab, "fit": lab,
        "dims": {"A": str(WT_AB[0][i]), "B": str(WT_AB[1][i])},
        "code": {"": f"WT{c}{t}", "D": f"WT{c}{t}D"},
    } for i, (lab, c, t) in enumerate(WT)],
))
add(product(
    id="wt-90", cat="water", group="防水槽曲", zh="防水槽 90° 曲", en="Waterproof 90° Bend", img="wt-90",
    blurb="A、B 為所配線槽截面。", edges=list("AB"),
    sizes=sizes("AB", WT_LABELS, WT_AB, [f"WT{c}.1{t}" for _, c, t in WT]),
))
add(product(
    id="wt-tee", cat="water", group="防水槽曲", zh="防水槽三叉", en="Waterproof Tee", img="wt-tee",
    blurb="A、B 為所配線槽截面。", edges=list("AB"),
    sizes=sizes("AB", WT_LABELS, WT_AB, [f"WT{c}.3{t}" for _, c, t in WT]),
))

SK = [
    ("ST1551", (150, 50, 100, "-", 113)),
    ("ST1541", (150, 40, 100, "-", 113)),
    ("ST1542", (150, 40, 75, 38, 126)),
    ("ST2042", (200, 40, 100, 50, 163)),
]
add(product(
    id="sk-body", cat="skirting", group="牆邊線槽", zh="牆邊線槽", en="Skirting Trunking", img="sk-body",
    blurb="螺絲蓋。標準長度 2.44 m。A 高、B 深、C / D / E 為截面。", edges=list("ABCDE"), length=2.44, unit="條",
    sizes=[{"id": m, "label": m, "fit": m, "dims": dict(zip("ABCDE", map(str, d))), "code": m} for m, d in SK],
))
add(product(
    id="sk-in", cat="skirting", group="牆邊槽曲", zh="牆邊 90° 曲 · 內曲", en="Skirting 90° Internal Bend", img="sk-in",
    blurb="內曲。邊長跟所選線槽截面。", edges=list("ABCDE"),
    sizes=[{"id": m, "label": m, "fit": m, "dims": dict(zip("ABCDE", map(str, d))), "code": "IB" + m[2:]} for m, d in SK],
))
add(product(
    id="sk-ex", cat="skirting", group="牆邊槽曲", zh="牆邊 90° 曲 · 外曲", en="Skirting 90° External Bend", img="sk-ex",
    blurb="外曲。邊長跟所選線槽截面。", edges=list("ABCDE"),
    sizes=[{"id": m, "label": m, "fit": m, "dims": dict(zip("ABCDE", map(str, d))), "code": "EB" + m[2:]} for m, d in SK],
))
for pid, zh, en, img, prefix in (
    ("sk-1g", "單制位片", "Single Gang Outlet Plate", "sk-1g", "CCS"),
    ("sk-2g", "雙制位片", "Twin Gang Outlet Plate", "sk-2g", "CCD"),
    ("sk-cap", "牆邊槽尾封", "Skirting End Cap", "sk-cap", "FEC"),
    ("sk-cp", "牆邊槽駁碼", "Skirting Connecting Plate", "sk-cp", "CP"),
):
    add(product(
        id=pid, cat="skirting", group="牆邊配件", zh=zh, en=en, img=img,
        blurb="適用線槽的截面尺寸會一併帶出，方便核對。", edges=list("ABCDE"),
        sizes=[{"id": m, "label": m, "fit": m, "dims": dict(zip("ABCDE", map(str, d))), "code": prefix + m[2:]} for m, d in SK],
    ))

RF = [
    ("150 × 50", 150, 50, 250, "5015", "15"),
    ("200 × 50", 200, 50, 300, "5020", "20"),
    ("250 × 50", 250, 50, 350, "5025", "25"),
    ("300 × 50", 300, 50, 400, "5030", "30"),
    ("150 × 75", 150, 75, 250, "7515", "15"),
    ("200 × 75", 200, 75, 300, "7520", "20"),
    ("250 × 75", 250, 75, 350, "7525", "25"),
    ("300 × 75", 300, 75, 400, "7530", "30"),
]
add(product(
    id="rf-body", cat="raised", group="地台線槽", zh="地台線槽", en="Raised Floor Trunking", img="rf-body",
    blurb="標準長度 2.44 m。A 闊、B 高。型號分標準、2 倉、3 倉。", edges=list("AB"), length=2.44, unit="條", mapKey="comp",
    options=[{"key": "comp", "label": "倉數", "choices": COMP3},
             {"key": "cover", "label": "槽蓋", "choices": COVER}],
    sizes=[{"id": lab, "label": lab, "fit": lab, "dims": {"A": str(a), "B": str(b)},
            "code": {"": "RF" + code, "D": "RFD" + code, "T": "RFT" + code}} for lab, a, b, c, code, hb in RF],
))
add(product(
    id="rf-jb", cat="raised", group="地台箱", zh="地台線槽過路箱", en="Raised Floor Junction Box", img="rf-jb",
    blurb="A 闊、B 高、C 為箱長。可選標準、2 倉、3 倉。", edges=list("ABC"), mapKey="comp",
    options=[{"key": "comp", "label": "倉數", "choices": COMP3}],
    sizes=[{"id": lab, "label": lab, "fit": lab, "dims": {"A": str(a), "B": str(b), "C": str(c)},
            "code": {"": "RJB" + code, "D": "RJBD" + code, "T": "RJBT" + code}} for lab, a, b, c, code, hb in RF],
))
add(product(
    id="rf-hb", cat="raised", group="地台箱", zh="槽頂出線箱", en="Header Box", img="rf-hb",
    blurb="出線箱型號按闊度。A 闊、B 高、C 為配合長度。", edges=list("ABC"),
    sizes=[{"id": lab, "label": lab, "fit": lab, "dims": {"A": str(a), "B": str(b), "C": str(c)},
            "code": "BXHB" + hb} for lab, a, b, c, code, hb in RF],
))


def service(pid, cat, group, zh, en, img, blurb, dims, code, unit="件"):
    add(product(
        id=pid, cat=cat, group=group, zh=zh, en=en, img=img, blurb=blurb, unit=unit,
        edges=list(dims.keys()),
        sizes=[{"id": "std", "label": "標準", "fit": code, "dims": {k: str(v) for k, v in dims.items()}, "code": code}],
    ))


service("rf-fb6", "raised", "地台插座箱", "地台插座箱 · 6 位", "Raised Floor Service Box 6-way", "rf-fb6",
        "新型 LHFB2525R。面框、內框、底箱及 a / b / c 均可改。標準 13A ×3、空片 ×1。",
        {"面長": 361, "面闊": 262, "內長": 283, "內闊": 162, "底長": 335, "底闊": 235, "a": 53, "b": 32, "c": 20, "蓋厚": 2},
        "LHFB2525R")
service("rf-fb4", "raised", "地台插座箱", "地台插座箱 · 4 位", "Raised Floor Service Box 4-way", "rf-fb4",
        "新型 LHFB2020R。標準 13A ×2。",
        {"面長": 262, "面闊": 262, "內長": 185, "內闊": 162, "底長": 235, "底闊": 235, "a": 53, "b": 32, "c": 20, "蓋厚": 2},
        "LHFB2020R")
service("rf-fb9", "raised", "地台插座箱", "地台插座箱 · 9 位", "Raised Floor Service Box 9-way", "rf-fb9",
        "新型 LHFB3030R。標準 13A ×3、空片 ×1。",
        {"面長": 360, "面闊": 353, "內長": 283, "內闊": 252, "底長": 335, "底闊": 328, "a": 53, "b": 32, "c": 20, "蓋厚": 2},
        "LHFB3030R")
add(product(
    id="rf-sbx", cat="raised", group="地台插座箱", zh="地台插座箱 · 舊款", en="Previous Raised Floor Service Box",
    img="rf-sbx", blurb="舊款 SBX。蘇位數已寫在尺寸名稱。", edges=list("ABCDE"),
    sizes=[
        {"id": "6", "label": "6 位", "fit": "6 位", "dims": {"A": "260", "B": "270", "C": "75", "D": "280", "E": "280"}, "code": "SBX2525R"},
        {"id": "9", "label": "9 位", "fit": "9 位", "dims": {"A": "330", "B": "330", "C": "75", "D": "355", "E": "355"}, "code": "SBX3025R"},
    ],
))
for pid, zh, en, prefix in (
    ("rf-ps", "插座底片 · 標準單蘇", "Socket Plate · Standard", "LHFBPS"),
    ("rf-pd", "插座底片 · 孖位", "Socket Plate · Double Gang", "LHFBPD"),
    ("rf-pb", "插座底片 · 空片", "Blank Plate", "LHFBPB"),
    ("rf-pc", "插座底片 · 特款孔", "Custom Plate", "LHFBPC"),
):
    add(product(
        id=pid, cat="raised", group="插座底片", zh=zh, en=en, img="rf-plate",
        blurb="適用 4、6、9 位 LHFB。特款孔請在備註寫明。",
        sizes=[{"id": w, "label": w + " 位", "fit": w + " 位", "dims": {}, "code": prefix + w + "W"} for w in ("4", "6", "9")],
    ))

UF = [
    ("225 × 25", 225, 25, 257, 300, 225, 300, "2525"),
    ("225 × 32", 225, 32, 257, 300, 225, 300, "2532"),
    ("300 × 25", 300, 25, 332, 375, 300, 375, "3025"),
    ("300 × 32", 300, 32, 332, 375, 300, 375, "3032"),
]
add(product(
    id="uf-body", cat="under", group="藏地線槽", zh="藏地線槽", en="Underfloor Trunking", img="uf-body",
    blurb="標準長度 2.44 m。A 闊、B 高、C 外寬。可選密封蓋或活動蓋。", edges=list("ABC"), length=2.44, unit="條", mapKey="comp",
    options=[{"key": "comp", "label": "倉數", "choices": COMP3}, {"key": "lid", "label": "蓋型", "choices": LID_UF}],
    sizes=[{"id": lab, "label": lab, "fit": lab, "dims": {"A": str(a), "B": str(b), "C": str(c)},
            "code": {"": "UF" + code, "D": "UFD" + code, "T": "UFT" + code}} for lab, a, b, c, ba, bb, bd, code in UF],
))
add(product(
    id="uf-flat", cat="under", group="藏地槽曲", zh="藏地平面曲", en="Underfloor Flat Elbow", img="uf-flat",
    blurb="平面曲。", edges=list("ABCD"),
    sizes=[{"id": lab, "label": lab, "fit": lab, "dims": {"A": str(ba), "B": str(b), "C": str(bb), "D": str(bd)}, "code": "UBH" + code}
           for lab, a, b, c, ba, bb, bd, code in UF],
))
add(product(
    id="uf-vert", cat="under", group="藏地槽曲", zh="藏地垂直曲", en="Underfloor Vertical Elbow", img="uf-vert",
    blurb="垂直曲。", edges=list("ABCD"),
    sizes=[{"id": lab, "label": lab, "fit": lab, "dims": {"A": str(ba), "B": str(b), "C": str(bb), "D": str(bd)}, "code": "UBV" + code}
           for lab, a, b, c, ba, bb, bd, code in UF],
))
UF_NEW = [
    ("4 位", {"a": ">70", "b": "263", "c": "263", "d": "236", "e": "236", "蓋厚": "2"}, "LHFB2020U", "<230"),
    ("6 位", {"a": ">70", "b": "263", "c": "360", "d": "236", "e": "337", "蓋厚": "2"}, "LHFB2525U", "<320"),
    ("9 位", {"a": ">70", "b": "353", "c": "360", "d": "328", "e": "338", "蓋厚": "2"}, "LHFB3030U", "<320"),
]
add(product(
    id="uf-fb", cat="under", group="藏地插座箱", zh="藏地插座箱 · 新款", en="Underfloor Service Box", img="uf-fb",
    blurb="a 為可指定的安裝高度。可配 1 / 2 / 3 倉。臨時保護蓋請寫在備註。", edges=["a", "b", "c", "d", "e", "蓋厚"],
    options=[{"key": "comp", "label": "配槽格", "choices": [{"id": "1", "label": "1 倉"}, {"id": "2", "label": "2 倉"}, {"id": "3", "label": "3 倉"}]}],
    sizes=[{"id": lab, "label": lab, "fit": "槽闊 " + width, "dims": dims, "code": code} for lab, dims, code, width in UF_NEW],
))
add(product(
    id="uf-jb-new", cat="under", group="藏地槽箱", zh="藏地槽箱 · 新款", en="Underfloor Junction Box", img="uf-jb",
    blurb="四通、終尾、直通、轉角、三通為同一箱體的接駁形式。", edges=["a", "b", "c", "d", "e"],
    options=[{"key": "way", "label": "接駁", "choices": [
        {"id": "4", "label": "四通"}, {"id": "S", "label": "終尾"}, {"id": "T", "label": "直通"},
        {"id": "L", "label": "轉角"}, {"id": "3", "label": "三通"}]}],
    sizes=[
        {"id": "4", "label": "配 225 闊", "fit": "槽闊 <230", "dims": {"a": ">70", "b": "263", "c": "263", "d": "237", "e": "237"}, "code": "LHJB2020U"},
        {"id": "9", "label": "配 300 闊", "fit": "槽闊 <320", "dims": {"a": ">70", "b": "354", "c": "361", "d": "328", "e": "337"}, "code": "LHJB3030U"},
    ],
))
add(product(
    id="uf-sbx", cat="under", group="藏地插座箱", zh="藏地插座箱 · 舊款", en="Previous Underfloor Service Box", img="uf-old-s",
    blurb="舊款 SBX，蓋底有防水膠邊。", edges=list("ABC"),
    sizes=[
        {"id": "225x25", "label": "225 × 25 · 6 位", "fit": "225 × 25", "dims": {"A": "320", "B": "72", "C": "280"}, "code": "SBX2525"},
        {"id": "225x32", "label": "225 × 32 · 6 位", "fit": "225 × 32", "dims": {"A": "320", "B": "79", "C": "280"}, "code": "SBX2532"},
        {"id": "300x25", "label": "300 × 25 · 9 位", "fit": "300 × 25", "dims": {"A": "395", "B": "72", "C": "355"}, "code": "SBX3025"},
        {"id": "300x32", "label": "300 × 32 · 9 位", "fit": "300 × 32", "dims": {"A": "395", "B": "79", "C": "355"}, "code": "SBX3032"},
    ],
))
OLD_JB = [
    ("225 × 25", (320, 280, 230), "2525"),
    ("225 × 32", (320, 280, 230), "2532"),
    ("300 × 25", (395, 355, 305), "3025"),
    ("300 × 32", (395, 355, 305), "3032"),
]
for pid, zh, en, prefix in (
    ("uf-4", "藏地槽箱 · 四通", "4-way Junction", "4JB"),
    ("uf-s", "藏地槽箱 · 終尾", "Terminal Junction", "SJB"),
    ("uf-t", "藏地槽箱 · 直通", "Through Junction", "TJB"),
    ("uf-l", "藏地槽箱 · 轉角", "Elbow Junction", "LJB"),
    ("uf-3", "藏地槽箱 · 三通", "Tee Junction", "3JB"),
):
    add(product(
        id=pid, cat="under", group="藏地槽箱", zh=zh + " · 舊款", en=en, img="uf-old-j",
        blurb="舊款藏地槽箱。", edges=list("ABC"),
        sizes=[{"id": lab, "label": lab, "fit": lab, "dims": dict(zip("ABC", map(str, d))), "code": prefix + code} for lab, d, code in OLD_JB],
    ))

FF = [
    ("150 × 50", 150, 50, 47, 275, 150, 275, 250, 200, 155, "5015"),
    ("200 × 50", 200, 50, 47, 325, 200, 325, 300, 250, 205, "5020"),
    ("250 × 50", 250, 50, 47, 375, 250, 375, 350, 300, 255, "5025"),
    ("300 × 50", 300, 50, 47, 425, 300, 425, 400, 350, 305, "5030"),
    ("150 × 75", 150, 75, 72, 275, 150, 275, 250, 200, 155, "7515"),
    ("200 × 75", 200, 75, 72, 325, 200, 325, 300, 250, 205, "7520"),
    ("250 × 75", 250, 75, 72, 375, 250, 375, 350, 300, 255, "7525"),
    ("300 × 75", 300, 75, 72, 425, 300, 425, 400, 350, 305, "7530"),
]
add(product(
    id="ff-body", cat="flush", group="平地線槽", zh="平地線槽", en="Flush Floor Trunking", img="ff-body",
    blurb="螺絲蓋配防水膠邊。標準長度 2.44 m。槽蓋可選 3 mm 鍍鋅鋼或熱浸鋅花鐵，請在備註註明。",
    edges=list("ABC"), length=2.44, unit="條", mapKey="comp",
    options=[{"key": "comp", "label": "倉數", "choices": COMP3}],
    sizes=[{"id": lab, "label": lab, "fit": lab, "dims": {"A": str(a), "B": str(b), "C": str(c)},
            "code": {"": "FF" + code, "D": "FFD" + code, "T": "FFT" + code}} for lab, a, b, c, *_rest, code in ((r[0], r[1], r[2], r[3], r[-1]) for r in FF)],
))
add(product(
    id="ff-flat", cat="flush", group="平地槽曲", zh="平地平面曲", en="Flush Floor Flat Elbow", img="ff-flat",
    blurb="平面曲。", edges=list("ABCD"),
    sizes=[{"id": r[0], "label": r[0], "fit": r[0], "dims": {"A": str(r[4]), "B": str(r[2]), "C": str(r[5]), "D": str(r[6])}, "code": "FBH" + r[-1]} for r in FF],
))
add(product(
    id="ff-vert", cat="flush", group="平地槽曲", zh="平地垂直曲", en="Flush Floor Vertical Elbow", img="ff-vert",
    blurb="垂直曲。", edges=list("ABCD"),
    sizes=[{"id": r[0], "label": r[0], "fit": r[0], "dims": {"A": str(r[4]), "B": str(r[2]), "C": str(r[5]), "D": str(r[6])}, "code": "FBV" + r[-1]} for r in FF],
))
for pid, zh, en, prefix in (
    ("ff-4", "平地線槽箱 · 四通", "Flush 4-way Box", "4FB"),
    ("ff-s", "平地線槽箱 · 終尾", "Flush Terminal Box", "SFB"),
    ("ff-t", "平地線槽箱 · 直通", "Flush Through Box", "TFB"),
    ("ff-l", "平地線槽箱 · 轉角", "Flush Elbow Box", "LFB"),
    ("ff-3", "平地線槽箱 · 三通", "Flush Tee Box", "3FB"),
):
    add(product(
        id=pid, cat="flush", group="平地槽箱", zh=zh, en=en, img="ff-box",
        blurb="平地線槽箱。", edges=list("ABC"),
        sizes=[{"id": r[0], "label": r[0], "fit": r[0], "dims": {"A": str(r[7]), "B": str(r[8]), "C": str(r[9])}, "code": prefix + r[-1]} for r in FF],
    ))


# ---------- images ----------
# page, x0, y0, x1, y1 in PDF points
CROPS = {
    "ct-body": (8, 30, 95, 565, 530),
    "ct-m90-f": (9, 28, 125, 210, 250),
    "ct-m90-i": (9, 190, 115, 400, 250),
    "ct-m90-e": (9, 385, 115, 570, 250),
    "ct-s90-f": (9, 28, 455, 210, 590),
    "ct-s90-i": (9, 190, 448, 400, 590),
    "ct-s90-e": (9, 385, 448, 570, 590),
    "ct-mt-f": (10, 24, 118, 165, 250),
    "ct-mt-t1": (10, 150, 118, 300, 250),
    "ct-mt-t2": (10, 285, 118, 430, 250),
    "ct-mt-i": (10, 410, 118, 572, 250),
    "ct-st-f": (10, 24, 455, 165, 590),
    "ct-st-t1": (10, 150, 455, 300, 590),
    "ct-st-t2": (10, 285, 455, 430, 590),
    "ct-st-i": (10, 410, 455, 572, 590),
    "ct-135-f": (11, 28, 120, 210, 250),
    "ct-135-i": (11, 195, 115, 400, 250),
    "ct-135-e": (11, 385, 115, 570, 250),
    "ct-x-f": (11, 40, 470, 310, 585),
    "ct-x-i": (11, 300, 470, 565, 585),
    "ct-fl-top": (12, 30, 120, 210, 250),
    "ct-fl-90": (12, 190, 115, 400, 250),
    "ct-fl-side": (12, 390, 115, 570, 250),
    "ct-red-l": (12, 30, 475, 210, 610),
    "ct-red-e": (12, 200, 470, 390, 610),
    "ct-red-r": (12, 385, 470, 570, 610),
    "ct-end": (13, 36, 100, 250, 280),
    "ct-sup": (13, 36, 300, 270, 530),
    "ct-flg": (13, 36, 545, 270, 770),
    "ct-cpf": (14, 28, 95, 250, 250),
    "ct-cpuf": (14, 28, 310, 260, 520),
    "ct-el": (14, 28, 555, 280, 770),
    "tr-sg": (16, 36, 115, 560, 258),
    "tr-rg": (16, 36, 448, 560, 592),
    "tr-90-f": (17, 30, 120, 210, 248),
    "tr-90-i": (17, 195, 115, 400, 248),
    "tr-90-e": (17, 385, 115, 570, 248),
    "tr-135-f": (17, 30, 448, 210, 575),
    "tr-135-i": (17, 195, 445, 400, 575),
    "tr-135-e": (17, 385, 445, 570, 575),
    "tr-tee": (18, 70, 125, 520, 255),
    "tr-cross": (18, 70, 455, 520, 585),
    "tr-red-e": (19, 30, 125, 210, 252),
    "tr-red-l": (19, 190, 120, 380, 252),
    "tr-red-r": (19, 370, 120, 560, 252),
    "tr-sgc": (19, 36, 448, 330, 575),
    "tr-rgtz": (19, 330, 448, 568, 590),
    "ld-straight": (21, 40, 115, 400, 400),
    "ld-90-f": (21, 40, 500, 230, 620),
    "ld-90-i": (21, 210, 490, 400, 620),
    "ld-90-e": (21, 385, 490, 565, 620),
    "ld-135-f": (22, 30, 120, 210, 250),
    "ld-135-i": (22, 195, 115, 390, 250),
    "ld-135-e": (22, 380, 115, 565, 250),
    "ld-tee": (22, 50, 418, 520, 555),
    "ld-cross": (23, 50, 125, 500, 310),
    "ld-red-e": (23, 36, 488, 230, 625),
    "ld-red-l": (23, 210, 488, 385, 625),
    "ld-red-r": (23, 370, 488, 555, 625),
    "bk-straight": (25, 40, 115, 360, 400),
    "bk-90": (26, 30, 115, 250, 285),
    "bk-tee": (26, 30, 300, 270, 500),
    "bk-plate": (26, 30, 520, 230, 700),
    "bk-kit": (27, 30, 125, 565, 450),
    "bk-l": (27, 24, 150, 300, 430),
    "bk-g": (27, 280, 140, 568, 460),
    "bk-d": (27, 20, 490, 230, 675),
    "bk-screw": (27, 270, 470, 450, 650),
    "bk-s": (27, 430, 460, 572, 655),
    "wt-body": (29, 30, 95, 565, 540),
    "wt-90": (30, 40, 100, 300, 330),
    "wt-tee": (30, 300, 100, 565, 330),
    "sk-body": (32, 30, 110, 565, 350),
    "sk-in": (32, 40, 370, 300, 480),
    "sk-ex": (32, 300, 370, 560, 480),
    "sk-1g": (32, 36, 590, 180, 678),
    "sk-2g": (32, 168, 590, 310, 678),
    "sk-cap": (32, 300, 590, 400, 678),
    "sk-cp": (32, 390, 585, 545, 678),
    "rf-body": (35, 30, 115, 565, 270),
    "rf-jb": (35, 30, 430, 310, 630),
    "rf-hb": (35, 300, 430, 565, 630),
    "rf-fb6": (37, 40, 90, 450, 620),
    "rf-fb4": (38, 30, 90, 300, 560),
    "rf-fb9": (38, 290, 90, 565, 500),
    "rf-sbx": (39, 40, 390, 560, 700),
    "rf-plate": (39, 40, 110, 560, 340),
    "uf-body": (41, 30, 115, 565, 400),
    "uf-flat": (41, 30, 490, 280, 640),
    "uf-vert": (41, 290, 480, 565, 640),
    "uf-fb": (42, 40, 90, 400, 450),
    "uf-jb": (43, 40, 90, 560, 470),
    "uf-old-s": (44, 36, 115, 540, 390),
    "uf-old-j": (44, 30, 512, 568, 665),
    "ff-body": (46, 30, 100, 565, 340),
    "ff-flat": (47, 30, 120, 300, 270),
    "ff-vert": (47, 310, 115, 565, 270),
    "ff-box": (47, 30, 460, 565, 620),
}


def cover_brand(page, im, clip, scale):
    draw = ImageDraw.Draw(im)

    def paint(rect, pad=4):
        hit = pymupdf.Rect(rect) & clip
        if hit.is_empty or hit.width < 0.2 or hit.height < 0.2:
            return
        x0 = int((hit.x0 - clip.x0) * scale) - pad
        y0 = int((hit.y0 - clip.y0) * scale) - pad
        x1 = int((hit.x1 - clip.x0) * scale) + pad
        y1 = int((hit.y1 - clip.y0) * scale) + pad
        draw.rectangle([x0, y0, x1, y1], fill="white")

    for w in page.get_text("words"):
        token = w[4]
        low = token.lower()
        if "力雄" in token or "lik" in low or "hung" in low:
            paint(pymupdf.Rect(w[0], w[1], w[2], w[3]), 6)
    if page.number == 7:
        paint(pymupdf.Rect(268, 196, 320, 244), 8)


def render_crop(doc, rect, max_w=520):
    page = doc[rect[0] - 1]
    clip = pymupdf.Rect(rect[1], rect[2], rect[3], rect[4]) & page.rect
    scale = min(2.3, max(1.3, max_w / max(1, clip.width)))
    pix = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), clip=clip, alpha=False)
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    cover_brand(page, im, clip, scale)
    # trim near-white borders but keep a small margin
    gray = im.convert("L")
    mask = gray.point(lambda v: 255 if v < 245 else 0)
    bbox = mask.getbbox()
    if bbox:
        pad = 10
        x0 = max(0, bbox[0] - pad)
        y0 = max(0, bbox[1] - pad)
        x1 = min(im.width, bbox[2] + pad)
        y1 = min(im.height, bbox[3] + pad)
        im = im.crop((x0, y0, x1, y1))
    if im.width > max_w:
        nh = max(1, round(im.height * max_w / im.width))
        im = im.resize((max_w, nh), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=68, optimize=True)
    return buf.getvalue(), im


def placeholder(text):
    im = Image.new("RGB", (480, 320), "white")
    draw = ImageDraw.Draw(im)
    draw.rectangle((8, 8, 471, 311), outline=(180, 40, 32), width=3)
    draw.text((24, 140), text[:18], fill=(28, 23, 20))
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=70)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def main():
    doc = pymupdf.open(PDF)
    images = {}
    montage_tiles = []
    for key, rect in CROPS.items():
        data, im = render_crop(doc, rect)
        images[key] = "data:image/jpeg;base64," + base64.b64encode(data).decode()
        thumb = im.copy()
        thumb.thumbnail((160, 110))
        canvas = Image.new("RGB", (170, 140), (244, 239, 232))
        canvas.paste(thumb, (5, 5))
        montage_tiles.append((key, canvas))
    # montage for visual check
    cols = 8
    rows = (len(montage_tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 170, rows * 140), (255, 255, 255))
    for i, (key, tile) in enumerate(montage_tiles):
        sheet.paste(tile, ((i % cols) * 170, (i // cols) * 140))
    preview = ROOT / "_preview"
    preview.mkdir(exist_ok=True)
    sheet.save(preview / "montage.jpg", quality=60)

    missing = []
    for p in PRODUCTS:
        if p["img"] not in images:
            missing.append(p["img"])
            p["img"] = placeholder(p["zh"])
        else:
            p["img"] = images[p["img"]]
    if missing:
        print("MISSING IMAGES", sorted(set(missing)))

    catalog = {
        "categories": [
            {"id": "trunking", "zh": "電線槽", "en": "Cable Trunking"},
            {"id": "tray", "zh": "電纜托盤", "en": "Cable Tray"},
            {"id": "ladder", "zh": "電纜梯架", "en": "Cable Ladder"},
            {"id": "basket", "zh": "電線籃", "en": "Cable Basket"},
            {"id": "water", "zh": "防水線槽", "en": "Waterproof Trunking"},
            {"id": "skirting", "zh": "牆邊線槽", "en": "Skirting Trunking"},
            {"id": "raised", "zh": "地台線槽", "en": "Raised Floor"},
            {"id": "under", "zh": "藏地線槽", "en": "Underfloor"},
            {"id": "flush", "zh": "平地線槽", "en": "Flush Floor"},
        ],
        "products": PRODUCTS,
    }
    payload = json.dumps(catalog, ensure_ascii=False).replace("<", "\\u003c")
    html = TEMPLATE.read_text(encoding="utf-8").replace("__CATALOG_JSON__", payload)
    (ROOT / "index.html").write_text(html, encoding="utf-8")

    icon = Image.new("RGB", (180, 180), (180, 35, 28))
    d = ImageDraw.Draw(icon)
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/msjh.ttc", 96)
    except Exception:
        font = ImageFont.load_default()
    d.text((42, 32), "訂", font=font, fill="white")
    icon.save(ROOT / "icon-180.png")
    (ROOT / "manifest.webmanifest").write_text(json.dumps({
        "name": "線槽訂貨",
        "short_name": "線槽訂貨",
        "start_url": "./index.html",
        "display": "standalone",
        "background_color": "#f4efe8",
        "theme_color": "#9d1c1c",
        "lang": "zh-Hant",
        "icons": [{"src": "icon-180.png", "sizes": "180x180", "type": "image/png", "purpose": "any"}]
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print("products", len(PRODUCTS))
    print("html", (ROOT / "index.html").stat().st_size)


if __name__ == "__main__":
    main()
