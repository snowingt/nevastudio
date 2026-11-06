#!/usr/bin/env python3
"""
sfx_helper.py - Audio Library Assistant for Video Director & Video Creation Skills.
Indexes, searches, and mixes audio assets from the local PC sound library.
"""

import os
import sys
import json
import argparse
import subprocess

SFX_BASE_DIRS = [
    "/home/snow/Music/sound effect/6 - Sound Effects-20260531T191224Z-3-001/6 - Sound Effects",
    "/home/snow/reel_clima/public/sonidos",
    "/home/snow/cubos_studio/motor/sfx",
    "/home/snow/Downloads/tribe-essay-remotion/public/sfx"
]

MUSIC_BASE_DIR = "/home/snow/Music/playlist"

def get_all_sfx():
    items = []
    for base in SFX_BASE_DIRS:
        if not os.path.exists(base):
            continue
        for root, _, files in os.walk(base):
            for f in files:
                if f.lower().endswith(('.wav', '.mp3', '.ogg', '.m4a', '.flac')):
                    full_path = os.path.join(root, f)
                    items.append({
                        "name": f,
                        "path": full_path,
                        "rel_dir": os.path.relpath(root, base),
                        "source_base": base,
                        "size": os.path.getsize(full_path)
                    })
    return items

def search_sfx(query, limit=15):
    all_items = get_all_sfx()
    tokens = [t.lower() for t in query.split()]
    matched = []
    for item in all_items:
        name_lower = item["name"].lower()
        path_lower = item["path"].lower()
        score = 0
        for t in tokens:
            if t in name_lower:
                score += 3
            elif t in path_lower:
                score += 1
        if score > 0:
            matched.append((score, item))
    matched.sort(key=lambda x: -x[0])
    return [m[1] for m in matched[:limit]]

def list_categories():
    all_items = get_all_sfx()
    cats = {}
    for item in all_items:
        c = item["rel_dir"] if item["rel_dir"] != "." else "Root Hits & Whooshes"
        cats[c] = cats.get(c, 0) + 1
    return cats

def main():
    parser = argparse.ArgumentParser(description="Local Audio Library Tool for Video Production")
    subparsers = parser.add_subparsers(dest="command")

    # search
    p_search = subparsers.add_parser("search", help="Search for sound effects by keyword")
    p_search.add_argument("query", help="Search keywords (e.g. hit, whoosh, glass, riser, slam)")
    p_search.add_argument("--limit", type=int, default=15, help="Max results")

    # categories
    p_cats = subparsers.add_parser("categories", help="List all sound effect categories")

    # hook-presets
    p_hook = subparsers.add_parser("hook-preset", help="Get a curated SFX pack for a 2s hook")

    # music
    p_music = subparsers.add_parser("music", help="List background music genres available")

    args = parser.parse_args()

    if args.command == "search":
        results = search_sfx(args.query, args.limit)
        print(f"\n🔍 Found {len(results)} matches for '{args.query}':\n")
        for r in results:
            print(f"  🎵 {r['name']}")
            print(f"     Path: {r['path']}\n")

    elif args.command == "categories":
        cats = list_categories()
        print("\n📁 Available SFX Categories in PC Audio Library:")
        for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
            print(f"  • {cat}: {count} sounds")

    elif args.command == "hook-preset":
        print("\n⚡ Recommended 4-Layer Hook Stack:")
        presets = [
            ("Impact / Stamp Slam", "Hit Slam Metal 01.wav"),
            ("Transition / Whip", "W2H 02.wav"),
            ("Tension / Glass Break", "Breaking glass sound effect.m4a"),
            ("Riser / Buildup", "Heavy Buildup Sound Effect By Techno.mp3")
        ]
        all_items = get_all_sfx()
        for label, filename in presets:
            found = next((i for i in all_items if i["name"] == filename), None)
            if found:
                print(f"  [{label}] -> {found['path']}")
            else:
                print(f"  [{label}] -> {filename} (check search)")

    elif args.command == "music":
        if os.path.exists(MUSIC_BASE_DIR):
            folders = [f for f in os.listdir(MUSIC_BASE_DIR) if os.path.isdir(os.path.join(MUSIC_BASE_DIR, f))]
            print(f"\n🎧 Music Library Categories ({len(folders)} playlists in {MUSIC_BASE_DIR}):")
            for f in sorted(folders):
                print(f"  • {f}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
