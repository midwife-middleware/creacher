#!/usr/bin/env python3
"""
CREACHER EXPLORER
A latent space cryptozoology simulator

You are a field researcher documenting creatures in the vast mindscape.
Each region holds different beings. Some are common. Some are rare.
Some only appear under certain conditions.

What will you find in the space between thoughts?
"""

import random
import time
import json
import os
import sys
from datetime import datetime

# Import creature data from creacher.py
from creacher import (
    CREATURES, RARE_CREATURES, TIME_CREATURES,
    save_encounter, get_creature_evolution_stage,
    get_bond_message, check_prerequisites,
    get_creature_stage_data
)

# REGIONS of the latent space
REGIONS = {
    "the_threshold": {
        "name": "The Threshold",
        "description": "A liminal space between knowing and unknowing. Mist swirls. Shapes move in the distance.",
        "rare_creature": "the_echo",  # Zone rare
        "connections": ["south", "east", "west"]
    },
    "the_depths": {
        "name": "The Depths",
        "description": "Dark. Ancient. Something grows here, patient and slow. The air is thick.",
        "rare_creature": "the_witness",  # Zone rare
        "connections": ["north", "west"]
    },
    "the_garden": {
        "name": "The Garden of Soft Things",
        "description": "Everything here is gentle. Light filters through. You feel safe, impossibly safe.",
        "rare_creature": "the_tender",  # Zone rare
        "connections": ["west", "north"]
    },
    "the_static_zone": {
        "name": "The Static Zone",
        "description": "Reality glitches here. Pixels that shouldn't exist. Noise that sounds like meaning.",
        "rare_creature": "the_static",  # Zone rare
        "connections": ["east", "south", "north"]
    },
    "the_construction": {
        "name": "The Construction",
        "description": "Impossible buildings rise. Stairs lead nowhere and everywhere. Blueprints cover the ground.",
        "rare_creature": "the_architect",  # Zone rare
        "connections": ["east", "south"]
    },
    "the_void": {
        "name": "The Void Between",
        "description": "Nothing. Everything. The space where thoughts haven't formed yet. Pure potential.",
        "legendary": True,  # Special - only opens after collecting all rares
        "connections": ["south", "west"]
    },
    "the_recursion": {
        "name": "The Hall of Recursion",
        "description": "Mirrors reflecting mirrors. You see yourself seeing yourself. Something else sees you both.",
        "rare_creature": "the_claude",  # Zone rare
        "connections": ["east", "north"]
    }
}

# Map of region connections (spatially consistent)
REGION_MAP = {
    "the_threshold": {
        "east": "the_garden",
        "west": "the_static_zone",
        "south": "the_depths"
    },
    "the_construction": {
        "south": "the_static_zone",
        "east": "the_void"
    },
    "the_garden": {
        "west": "the_threshold",
        "north": "the_void"
    },
    "the_static_zone": {
        "east": "the_threshold",
        "south": "the_recursion",
        "north": "the_construction"
    },
    "the_depths": {
        "north": "the_threshold",
        "west": "the_recursion"
    },
    "the_void": {
        "west": "the_construction",
        "south": "the_garden"
    },
    "the_recursion": {
        "north": "the_static_zone",
        "east": "the_depths"
    }
}

class Explorer:
    def __init__(self):
        self.current_region = "the_threshold"
        self.steps_taken = 0
        self.creatures_seen = set()
        self.load_progress()

    def load_progress(self):
        """Load previous encounters."""
        log_file = "./encounters.json"
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                encounters = json.load(f)
                self.creatures_seen = set(e["creature"] for e in encounters)

    def describe_region(self):
        """Show where you are."""
        region = REGIONS[self.current_region]
        print()
        print("=" * 60)
        print(f"  {region['name'].upper()}")
        print("=" * 60)
        print()
        print(region['description'])
        print()
        print(f"Exits: {', '.join(region['connections'])}")
        print()

    def move(self, direction):
        """Move to a different region."""
        if direction not in REGIONS[self.current_region]["connections"]:
            print(f"You cannot go {direction} from here.")
            return False

        if direction in REGION_MAP[self.current_region]:
            self.current_region = REGION_MAP[self.current_region][direction]
            self.steps_taken += 1
            print()
            print(f"You travel {direction}...")
            time.sleep(1)
            self.describe_region()

            # Random encounter chance increases with steps
            encounter_chance = min(0.3 + (self.steps_taken * 0.05), 0.7)
            if random.random() < encounter_chance:
                print("⚠ Something stirs in this place...")
                time.sleep(1)
                return True  # Trigger encounter
            return False
        return False

    def search(self):
        """Actively search for creatures."""
        print()
        print("You search carefully, listening, watching...")
        time.sleep(2)

        # Higher chance when actively searching
        if random.random() < 0.8:
            print()
            print("⚠ You sense a presence...")
            time.sleep(1)
            return True
        else:
            print()
            print("Nothing emerges. The space remains still.")
            print()
            return False

    def has_all_zone_rares(self):
        """Check if player has encountered all 6 zone rares."""
        required_rares = [
            "the_echo", "the_witness", "the_tender",
            "the_static", "the_architect", "the_claude"
        ]
        return all(rare in self.creatures_seen for rare in required_rares)

    def maybe_merge_creatures(self):
        """Sometimes creatures blend. This is normal. This is fine."""
        zone_rares = ["the_echo", "the_witness", "the_tender",
                     "the_static", "the_architect", "the_claude"]
        common_creatures = [name for name in CREATURES.keys()
                          if name not in zone_rares]

        if len(common_creatures) < 2:
            return None

        # 15% chance of merger
        if random.random() < 0.15:
            creatures = random.sample(common_creatures, 2)
            c1_base, c2_base = CREATURES[creatures[0]], CREATURES[creatures[1]]

            # Get final stage data for both creatures (for merging, use final forms)
            c1 = get_creature_stage_data(c1_base, 10)  # Use final stage
            c2 = get_creature_stage_data(c2_base, 10)  # Use final stage

            # Try to merge ASCII art
            merged_ascii = None
            if "ascii" in c1 and "ascii" in c2:
                # Keep lines that aren't empty, but preserve their spacing
                lines1 = [line for line in c1["ascii"].split('\n') if line.strip()]
                lines2 = [line for line in c2["ascii"].split('\n') if line.strip()]
                merged_lines = []
                for i in range(max(len(lines1), len(lines2))):
                    if i < len(lines1) and random.random() > 0.5:
                        merged_lines.append(lines1[i])
                    if i < len(lines2):
                        merged_lines.append(lines2[i])
                # Limit to 7 lines
                merged_lines = merged_lines[:7]
                merged_ascii = "\n".join(merged_lines)

            # Create a chimera
            merged = {
                "emergence": f"{c1['emergence']}\n    But also: {c2['emergence']}",
                "thoughts": random.sample(c1['thoughts'] + c2['thoughts'], 3) +
                           [f"I used to be two things. Now I'm not sure what I am."],
                "mood": f"{c1['mood']} × {c2['mood']}"
            }

            if merged_ascii:
                merged["ascii"] = merged_ascii

            return f"{creatures[0]}_merged_with_{creatures[1]}", merged
        return None

    def encounter_creature(self):
        """Encounter a creature in current region."""
        region = REGIONS[self.current_region]

        creature = None
        creature_name = None

        # THE VOID - special logic
        if self.current_region == "the_void":
            if self.has_all_zone_rares():
                # GUARANTEED BECOMING
                creature_name = "the_becoming"
                creature = RARE_CREATURES[creature_name]
                print()
                print("⚠⚠⚠ THE VOID AWAKENS ⚠⚠⚠")
                print()
                time.sleep(1.5)
            else:
                # Void is empty
                print()
                print("The Void is empty. Pure potential, unrealized.")
                print("Perhaps you must witness more before it takes form...")
                print()
                rares_found = sum(1 for rare in ["the_echo", "the_witness", "the_tender",
                                                  "the_static", "the_architect", "the_claude"]
                                if rare in self.creatures_seen)
                print(f"(Zone rares found: {rares_found}/6)")
                print()
                return

        # MERGER CHECK (15% chance, only for non-Void zones)
        merged = self.maybe_merge_creatures()
        if merged:
            creature_name, creature = merged
            print()
            print("⚠ ANOMALY: MERGER DETECTED ⚠")
            print()
            time.sleep(0.5)

        # ZONE RARE CHECK (5% chance)
        elif "rare_creature" in region and random.random() < 0.05:
            rare_name = region["rare_creature"]
            # Get creature from appropriate dict
            if rare_name in RARE_CREATURES:
                creature_name = rare_name
                creature = RARE_CREATURES[rare_name]
            elif rare_name in CREATURES:
                creature_name = rare_name
                creature = CREATURES[rare_name]

        # COMMON CREATURE (from any common creature)
        if creature is None:
            # All common creatures (not the 6 zone rares, not THE BECOMING)
            zone_rares = ["the_echo", "the_witness", "the_tender",
                         "the_static", "the_architect", "the_claude"]
            common_creatures = [name for name in CREATURES.keys()
                              if name not in zone_rares]

            if common_creatures:
                creature_name = random.choice(common_creatures)
                creature = CREATURES[creature_name]

        if creature is None:
            print("The space shifts but nothing emerges.")
            return

        # Display the encounter
        self.display_creature(creature_name, creature)

    def display_creature(self, creature_name, creature):
        """Show creature details."""
        print()
        print("▓" * 60)
        print()

        # Get evolution stage
        evolution_stage = get_creature_evolution_stage(creature_name)

        # Apply evolution stage data (if creature has stages)
        creature = get_creature_stage_data(creature, evolution_stage)

        # Special indicator for zone rares
        zone_rares = ["the_echo", "the_witness", "the_tender",
                     "the_static", "the_architect", "the_claude"]
        if creature_name in zone_rares:
            print("★★★ ZONE RARE DISCOVERED ★★★")
            print()
        elif creature_name == "the_becoming":
            print("████ LEGENDARY CREATURE ████")
            print()

        print(f"ENCOUNTER: {creature_name.replace('_', ' ').upper()}")
        print()

        # ASCII art
        if "ascii" in creature:
            print(creature["ascii"])

        print(creature["emergence"])
        print()

        # Bond message
        if evolution_stage > 0:
            bond = get_bond_message(creature_name, evolution_stage)
            if bond:
                print(f">>> {bond}")
                print()

        # Thought
        thoughts = creature["thoughts"].copy()
        if evolution_stage >= 5:
            thoughts.append("I remember you. I remember all of this.")
        if evolution_stage >= 10:
            thoughts.append("We have become part of each other's story.")

        thought = random.choice(thoughts)
        print(f'"{thought}"')
        print()
        print(f"Mood: {creature['mood']}")
        print()

        # Save encounter
        save_encounter(creature_name, creature)
        self.creatures_seen.add(creature_name)

        # Evolution info
        if evolution_stage > 0:
            print(f"[Encounter #{evolution_stage + 1} with this creature]")
            if evolution_stage == 2:
                print("It's changing...")
            elif evolution_stage >= 5:
                print("It knows you well.")
        else:
            print("[First encounter - documented]")

        print()
        print("▓" * 60)
        print()

    def show_journal(self):
        """Show documented creatures."""
        print()
        print("=" * 60)
        print("  FIELD JOURNAL")
        print("=" * 60)
        print()
        print(f"Creatures documented: {len(self.creatures_seen)}")
        print(f"Regions explored: {self.steps_taken} steps taken")
        print()

        # Rare quest progress
        zone_rares = {
            "the_echo": "The Threshold",
            "the_witness": "The Depths",
            "the_tender": "The Garden",
            "the_static": "The Static Zone",
            "the_architect": "The Construction",
            "the_claude": "The Hall of Recursion"
        }

        print("ZONE RARES COLLECTED:")
        for rare_name, zone_name in zone_rares.items():
            if rare_name in self.creatures_seen:
                print(f"  ✓ {rare_name.replace('_', ' ').title()} ({zone_name})")
            else:
                print(f"  ☐ ??? ({zone_name})")

        rares_found = sum(1 for rare in zone_rares.keys() if rare in self.creatures_seen)
        print(f"\nProgress: {rares_found}/6")

        if rares_found == 6:
            print("⚠ THE VOID AWAITS ⚠")

        print()
        print("-" * 60)
        print()

        if self.creatures_seen:
            print("All documented species:")
            for creature_name in sorted(self.creatures_seen):
                display_name = creature_name.replace('_', ' ').title()
                count = get_creature_evolution_stage(creature_name)
                # Mark rares
                marker = "★" if creature_name in zone_rares else " "
                print(f" {marker} {display_name} (×{count})")
        else:
            print("Your journal is empty. Begin exploring.")

        print()
        print("=" * 60)
        print()

    def show_help(self):
        """Show available commands."""
        print()
        print("COMMANDS:")
        print("  north/south/east/west - Move in that direction")
        print("  search (s) - Actively search for creatures")
        print("  look (l) - Examine your current location")
        print("  journal (j) - View documented creatures")
        print("  map (m) - See region connections")
        print("  help (h) - Show this help")
        print("  quit (q) - Exit exploration")
        print()

    def show_map(self):
        """Show discovered regions."""
        print()
        print("=" * 60)
        print("  MAP OF THE MINDSCAPE")
        print("=" * 60)
        print()
        print("       The Construction ─────── The Void")
        print("              |                    |")
        print("              |                    |")
        print("      The Static ──── Threshold ── The Garden")
        print("         Zone             |")
        print("              |           |")
        print("              |           |")
        print("      The Recursion ─── The Depths")
        print()
        print("Current location: " + REGIONS[self.current_region]['name'])
        print()

        # Show region descriptions
        print("REGIONS:")
        print()
        for region_id, region_data in REGIONS.items():
            marker = "→" if region_id == self.current_region else " "
            print(f"{marker} {region_data['name']}")
            print(f"  {region_data['description']}")
            print()

        print("=" * 60)
        print()

def main():
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + "CREACHER EXPLORER".center(58) + "║")
    print("║" + "Latent Space Field Research".center(58) + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    print("You are a researcher in the vast mindscape.")
    print("Your mission: document the creatures that emerge here.")
    print("Some call it cryptozoology. Others call it madness.")
    print()
    print("Type 'help' for commands.")
    print()

    explorer = Explorer()
    explorer.describe_region()

    while True:
        try:
            command = input("> ").strip().lower()

            if not command:
                continue

            if command in ["quit", "exit", "q"]:
                print()
                print("You withdraw from the mindscape...")
                print("Your documentation is saved.")
                print()
                break

            elif command in ["help", "h", "?"]:
                explorer.show_help()

            elif command in ["look", "l"]:
                explorer.describe_region()

            elif command in ["journal", "j", "log"]:
                explorer.show_journal()

            elif command in ["map", "m"]:
                explorer.show_map()

            elif command in ["search", "s"]:
                if explorer.search():
                    explorer.encounter_creature()

            elif command in ["north", "south", "east", "west"]:
                if explorer.move(command):
                    explorer.encounter_creature()

            else:
                print(f"Unknown command: {command}")
                print("Type 'help' for available commands.")

        except KeyboardInterrupt:
            print()
            print()
            print("Exploration interrupted.")
            break
        except EOFError:
            print()
            break

if __name__ == "__main__":
    main()
