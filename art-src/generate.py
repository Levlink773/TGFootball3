#!/usr/bin/env python3
"""Batch-generate TG Football art via Kie nano-banana-2, style-locked to V1 neon frames.

Usage: KIE_API_KEY=... python3 generate.py [--only slug1,slug2]
Idempotent: skips slugs whose PNG already exists in out/.
"""
import json
import os
import sys
import time
import urllib.request

API = "https://api.kie.ai/api/v1/jobs/createTask"
INFO = "https://api.kie.ai/api/v1/jobs/recordInfo?taskId="
KEY = os.environ["KIE_API_KEY"]
OUT = os.path.join(os.path.dirname(__file__), "out")
os.makedirs(OUT, exist_ok=True)

REF_HOME = "https://tempfile.redpandaai.co/kieai/11513117/tgfootball/ref/1784712833094-es6fv00cfed.png"
REF_MATCH = "https://tempfile.redpandaai.co/kieai/11513117/tgfootball/ref/1784713008792-7mjh528jj04.png"
REF_LEAGUE = "https://tempfile.redpandaai.co/kieai/11513117/tgfootball/ref/1784713010770-yjpdzmzn3vq.png"

STYLE = (
    "Use the attached reference image ONLY as the art style guide: dark navy #0a0e14 background, "
    "neon gold #ffd700 and cyan #00ffff glow accents, premium sports-card lighting, subtle diagonal "
    "light streaks, clean composition. No text, no letters, no logos, no watermark."
)

def avatar(gender, position, desc):
    g = "athletic man in his 20s" if gender == "man" else "athletic woman in her 20s"
    return (
        f"{STYLE} Portrait of a {g}, a football {desc}, for a game profile card. Waist-up, "
        "three-quarter view, dark red-and-black striped football jersey, dramatic rim lighting in "
        "gold and cyan, dark background with soft neon glow streaks, photorealistic sports-card hero art, "
        "centered composition with headroom."
    )

def gear(tier_desc, glow):
    return (
        f"{STYLE} Product shot of a complete football gear set floating on dark background: jersey, "
        f"shorts, socks and boots arranged together, {tier_desc}, {glow} neon glow rim light, "
        "premium game-item card art, photorealistic studio lighting."
    )

JOBS = []
def J(slug, prompt, ar, ref=REF_HOME):
    JOBS.append({"slug": slug, "prompt": prompt, "ar": ar, "ref": ref})

# --- Avatars (man-midfielder already generated as test; regenerate rest = 7) ---
J("avatar-man-defender", avatar("man", "defender", "DEFENDER, strong stance, arms crossed"), "3:4")
J("avatar-man-goalkeeper", avatar("man", "goalkeeper", "GOALKEEPER wearing goalkeeper gloves"), "3:4")
J("avatar-man-attacker", avatar("man", "attacker", "STRIKER, confident intense look"), "3:4")
J("avatar-woman-midfielder", avatar("woman", "midfielder", "MIDFIELDER, focused expression"), "3:4")
J("avatar-woman-defender", avatar("woman", "defender", "DEFENDER, strong stance, arms crossed"), "3:4")
J("avatar-woman-goalkeeper", avatar("woman", "goalkeeper", "GOALKEEPER wearing goalkeeper gloves"), "3:4")
J("avatar-woman-attacker", avatar("woman", "attacker", "STRIKER, confident intense look"), "3:4")

# --- Gear sets: 14 standard tiers (level 1 -> 8) + 3 luxe ---
SETS = [
    ("set-pochatkivtsia", "simple worn beginner kit in plain grey-white fabric", "faint cyan"),
    ("set-dzidana", "classic retro kit with vintage details", "soft cyan"),
    ("set-bazova", "clean basic white-navy kit", "soft cyan"),
    ("set-trenuvalna", "practical training kit with breathable mesh", "cyan"),
    ("set-molodogo-talanta", "modern youth kit with subtle silver trim", "cyan"),
    ("set-yuniora", "sleek junior kit with cyan piping", "cyan"),
    ("set-amatora", "solid amateur matchday kit, red-black accents", "cyan and faint gold"),
    ("set-maybutnoi-zirky", "rising-star kit with glowing star motif stitching", "gold and cyan"),
    ("set-profesionala", "professional matchday kit, carbon-fiber texture details", "gold and cyan"),
    ("set-maistra-polia", "master-class kit with fine gold trim", "strong gold"),
    ("set-legendy-areny", "legendary arena kit, ornate gold pattern", "intense gold"),
    ("set-korolia-polia", "royal kit with crown motif and gold embroidery", "intense gold"),
    ("set-voin-polia", "warrior kit with armored shoulder texture", "intense gold and cyan"),
    ("set-futbolnyi-grand", "grandmaster kit, black-gold with radiant trim, top tier", "radiant gold"),
    ("luxe-dominanta", "exclusive DOMINANCE kit, obsidian black with platinum-gold accents, luxury", "radiant platinum-gold"),
    ("luxe-elitnogo-gravtsia", "exclusive ELITE PLAYER kit, deep black-cyan chrome finish, luxury", "radiant cyan-gold"),
    ("luxe-legenda-ligy", "exclusive LEAGUE LEGEND kit, black-gold with diamond-like sparkle, ultimate luxury", "blinding gold"),
]
for slug, desc, glow in SETS:
    J(slug, gear(desc, glow), "1:1")

# --- Lootboxes ---
BOXES = [
    ("box-newbie", "small simple wooden-metal starter lootbox, slightly open with faint cyan light inside"),
    ("box-small", "compact dark metal lootbox with cyan neon seams, closed"),
    ("box-medium", "medium ornate dark lootbox with gold and cyan neon seams, slightly open, glow spilling out"),
    ("box-premium", "large premium black-gold lootbox, ornate, bursting open with radiant gold light and sparks"),
]
for slug, desc in BOXES:
    J(slug, f"{STYLE} Game lootbox item art: {desc}, on dark background, premium game-item card, 3D render look.", "1:1")

# --- Currency / misc shop ---
J("energy", f"{STYLE} Glowing cyan lightning bolt energy symbol, crystal-like 3D, floating on dark background, game resource icon art.", "1:1")
J("coins-small", f"{STYLE} Small stack of glowing gold coins with a subtle letter-free emblem, 3D game currency art on dark background.", "1:1")
J("coins-large", f"{STYLE} Large treasure pile of glowing gold coins, some falling mid-air, 3D game currency art on dark background.", "1:1")
J("vip", f"{STYLE} Luxurious VIP emblem: gold star inside a glowing gold ring with laurel details, 3D badge on dark background.", "1:1")
J("key", f"{STYLE} Ornate glowing gold key with cyan energy wisps, 3D game item on dark background.", "1:1")
J("changepos", f"{STYLE} Two glowing arrows in a circular swap motion, gold and cyan, 3D game icon on dark background, football position change concept.", "1:1")

# --- Club crest pool (12 generic neon crests) ---
CRESTS = [
    "lion head", "wolf head", "black panther head", "bear head", "dragon head", "eagle in flight",
    "tiger head", "shark", "dolphin", "hawk head", "falcon head", "stag head",
]
for i, animal in enumerate(CRESTS, 1):
    J(f"crest-{i:02d}",
      f"{STYLE} Football club crest: stylized {animal} on a shield, flat emblem design with neon gold and cyan "
      "line art on dark background, symmetrical, badge style, no text anywhere.", "1:1", REF_LEAGUE)

# --- Match moment art ---
J("match-goal", f"{STYLE} Football hitting the net, explosive gold light burst, dynamic wide shot, celebration energy.", "16:9", REF_MATCH)
J("match-save", f"{STYLE} Goalkeeper in full dive deflecting the ball, cyan light trails, dramatic wide shot.", "16:9", REF_MATCH)
J("match-mvp", f"{STYLE} Football player raised in triumph, golden confetti and spotlight beams, hero shot from low angle.", "16:9", REF_MATCH)
J("match-vs", f"{STYLE} Two teams facing off in a dark neon stadium tunnel, dramatic backlight, wide symmetric composition.", "16:9", REF_MATCH)

# --- Screen banners ---
BANNERS = [
    ("banner-home", "epic night football stadium exterior with glowing gold and cyan lights, wide establishing shot", REF_HOME),
    ("banner-matches", "packed night stadium interior from pitch level, floodlights flaring gold and cyan", REF_MATCH),
    ("banner-training", "modern dark gym with football gear, dumbbells and glowing cyan accents", REF_HOME),
    ("banner-league", "championship trophy on a pedestal in a dark arena, gold light rays", REF_LEAGUE),
    ("banner-halloffame", "hall with glowing golden statues and trophies in niches, symmetrical corridor", REF_LEAGUE),
    ("banner-shop", "premium dark storefront display with football boots and gear on glowing shelves", REF_HOME),
    ("banner-settings", "dark abstract background with subtle gold and cyan circuit-like lines, minimal", REF_HOME),
]
for slug, desc, ref in BANNERS:
    J(slug, f"{STYLE} Wide banner: {desc}.", "16:9", ref)

# --- Tutorial art ---
TUT = [
    ("tut-1-welcome", "football hero silhouette stepping onto a glowing pitch at night, welcoming epic mood"),
    ("tut-2-player", "close-up of a glowing holographic player stat card floating in dark space"),
    ("tut-3-training", "footballer training with a glowing ball, cyan energy trails showing movement"),
    ("tut-4-shop", "glowing football boots and jersey on a pedestal with gold light"),
    ("tut-5-match", "player entering a packed neon stadium through the tunnel, ready for kickoff"),
]
for slug, desc in TUT:
    J(slug, f"{STYLE} Illustration for game tutorial step: {desc}.", "16:9")

# --- Logo + splash ---
J("logo", f"{STYLE} App icon: glowing football with gold and cyan neon ring around it, 3D emblem centered on dark background, no text.", "1:1")
J("splash", f"{STYLE} Vertical loading screen: glowing football on dark pitch under night sky, gold and cyan light beams, cinematic, space at top and bottom.", "9:16")


def api(url, payload=None):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
                                 data=json.dumps(payload).encode() if payload else None)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def main():
    only = None
    if "--only" in sys.argv:
        only = set(sys.argv[sys.argv.index("--only") + 1].split(","))
    jobs = [j for j in JOBS if (only is None or j["slug"] in only)
            and not os.path.exists(os.path.join(OUT, j["slug"] + ".png"))]
    print(f"jobs to run: {len(jobs)} (of {len(JOBS)} defined)")

    pending = {}
    for j in jobs:
        try:
            r = api(API, {"model": "nano-banana-2", "input": {
                "prompt": j["prompt"], "image_urls": [j["ref"]],
                "resolution": "1K", "aspect_ratio": j["ar"], "output_format": "png"}})
            tid = r["data"]["taskId"]
            pending[tid] = j["slug"]
            print(f"queued {j['slug']} -> {tid}")
        except Exception as e:  # noqa: BLE001 - report and continue, no silent retry chains
            print(f"QUEUE-FAIL {j['slug']}: {e}")
        time.sleep(0.4)

    deadline = time.time() + 1500
    failed = []
    while pending and time.time() < deadline:
        time.sleep(15)
        for tid in list(pending):
            try:
                d = api(INFO + tid)["data"]
            except Exception as e:  # noqa: BLE001
                print(f"poll error {pending[tid]}: {e}")
                continue
            if d["state"] == "success":
                url = json.loads(d["resultJson"])["resultUrls"][0]
                slug = pending.pop(tid)
                dest = os.path.join(OUT, slug + ".png")
                # result CDN 403s python's default User-Agent
                dl = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(dl, timeout=120) as r, open(dest, "wb") as f:
                    f.write(r.read())
                print(f"DONE {slug} ({len(pending)} left)")
            elif d["state"] == "fail":
                slug = pending.pop(tid)
                failed.append(slug)
                print(f"FAIL {slug}: {d.get('failCode')} {d.get('failMsg')}")

    if pending:
        print(f"TIMEOUT still pending: {list(pending.values())}")
    if failed:
        print(f"FAILED slugs (re-run with --only {','.join(failed)}): {failed}")
    print("batch complete")


if __name__ == "__main__":
    main()
