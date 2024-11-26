import requests
import json
from typing import List, Dict, Union
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq

# Constants
BASE_URL = "https://pokeapi.co/api/v2/pokemon/"
SPECIES_URL = "https://pokeapi.co/api/v2/pokemon-species/"
PLACEHOLDER = "ReplaceMe"
DEFAULT_STATS = {"Hp": 0, "Attack": 0, "Defense": 0, "Special-attack": 0, "Special-defense": 0, "Speed": 0, "Bst": 0}

def fetch_data(url: str) -> Union[dict, None]:
    """Fetch data from a given URL and handle exceptions."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return None

def get_types(data: dict) -> List[str]:
    """Extract Pokémon types."""
    return [t["type"]["name"] for t in data.get("types", [])] or [PLACEHOLDER, PLACEHOLDER]

def get_abilities(data: dict) -> List[str]:
    """Extract Pokémon abilities."""
    abilities = []
    for a in data.get("abilities", []):
        ability_name = a["ability"]["name"]
        if a.get("is_hidden", False):
            ability_name += " [HIDDEN]"
        abilities.append(ability_name)
    return abilities or [PLACEHOLDER, PLACEHOLDER]

def get_stats(data: dict) -> Dict[str, int]:
    """Extract Pokémon stats."""
    stats = {stat["stat"]["name"]: stat["base_stat"] for stat in data.get("stats", [])}
    stats["BST"] = sum(stats.values())  # Base Stat Total
    return stats

def get_learnset(data: dict) -> List[dict]:
    """Extract learnable moves."""
    def extract_moves_for_version(version_group_name: str) -> List[dict]:
        learnset = []
        for move in data.get("moves", []):
            details = [
                detail for detail in move["version_group_details"]
                if detail["level_learned_at"] > 0 and detail["version_group"]["name"] == version_group_name
            ]
            if details:
                learnset.append({
                    "Move": move["move"]["name"],
                    "Level": details[0]["level_learned_at"],
                    "Modification": ""
                })
        return sorted(learnset, key=lambda x: x["Level"])

    # First attempt with 'scarlet-violet'
    learnset = extract_moves_for_version("scarlet-violet")
    version_group = "scarlet-violet"

    # If still empty, attempt with 'sword-shield'
    if not learnset:
        learnset = extract_moves_for_version("sword-shield")
        version_group = "sword-shield"

    # If still empty, attempt with 'sun-moon'
    if not learnset:
        learnset = extract_moves_for_version("sun-moon")
        version_group = "sun-moon"

    return [{"Base Learnset Version": version_group}] + learnset

def get_evolution_chain(species_data: dict) -> List[dict]:
    """Fetch and parse evolution chain data for the specific Pokémon."""
    evolution_url = species_data.get("evolution_chain", {}).get("url")
    if not evolution_url:
        return [{"Method": "No evolution data available"}]
    
    chain_data = fetch_data(evolution_url)
    if not chain_data:
        return [{"Method": "Error fetching evolution chain"}]
    
    target_species = species_data["name"]
    
    def find_evolutions(chain: dict) -> List[dict]:
        """Find evolutions directly related to the target Pokémon."""
        if chain["species"]["name"] == target_species:
            return [
                {
                    "Evolves to": evolution["species"]["name"],
                    "Method": evolution["evolution_details"][0]["trigger"]["name"] if evolution["evolution_details"] else "Unknown",
                    "Level": evolution["evolution_details"][0].get("min_level") if evolution["evolution_details"] else None
                }
                for evolution in chain.get("evolves_to", [])
            ]
        for next_chain in chain.get("evolves_to", []):
            result = find_evolutions(next_chain)
            if result:
                return result
        return []

    return find_evolutions(chain_data["chain"])

def get_pokemon_sprite(poke_id: int):
    url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/{poke_id}.gif"
    return url

def apply_flow_style(data):
    """Recursively apply flow style to specified keys."""
    if isinstance(data, dict):
        cm = CommentedMap(data)
        for key, value in cm.items():
            if key in {"Type", "Old", "New"}:
                cm[key] = CommentedSeq(value)
                cm[key].fa.set_flow_style()
            elif key in {"Evolution", "Learnset", "Stats"}:
                cm[key] = CommentedSeq(
                    [apply_flow_style(item) for item in value if isinstance(item, dict)]
                )
                cm[key].fa.set_flow_style()
            else:
                cm[key] = apply_flow_style(value)
        return cm
    elif isinstance(data, list):
        cs = CommentedSeq(data)
        for i, item in enumerate(cs):
            cs[i] = apply_flow_style(item)
        return cs
    return data

def fetch_pokemon_data(poke_id: int) -> dict:
    """Fetch data for a single Pokémon."""
    pokemon_data = fetch_data(f"{BASE_URL}{poke_id}")
    if not pokemon_data:
        return {"Number": poke_id, "Name": PLACEHOLDER, "Type": [PLACEHOLDER, PLACEHOLDER], "Abilities": [PLACEHOLDER], "Stats": DEFAULT_STATS, "Evolution": [{"Method": "Error"}], "Learnset": []}

    species_data = fetch_data(f"{SPECIES_URL}{poke_id}")
    evolution_chain = get_evolution_chain(species_data) if species_data else [{"Method": "Error"}]

    return apply_flow_style({
        "Number": poke_id,
        "Name": pokemon_data["name"].capitalize(),
        "Type": [t.capitalize() for t in get_types(pokemon_data)],
        "Abilities": {
            "Old": [a.capitalize() for a in get_abilities(pokemon_data)],
            "New": ["", ""]
        },
        "Evolution": [
            {key.capitalize(): (value.capitalize() if isinstance(value, str) else value) for key, value in evo.items()}
            for evo in evolution_chain
        ],
        "Stats": [
            {"Vanilla": {k.capitalize(): v for k, v in get_stats(pokemon_data).items()}},
            {"Updated": {k.capitalize(): v for k, v in get_stats(pokemon_data).items()}},
            {"Changes": DEFAULT_STATS}
        ],
        "Learnset": [
            {key.capitalize(): (value.capitalize() if isinstance(value, str) else value) for key, value in move.items()}
            for move in get_learnset(pokemon_data)
        ],
        "sprite_url": get_pokemon_sprite(poke_id),
        "Location": [""],
        "Split": "",
        "Changelog": ""
    })

def main():
    pokemon_data = []
    for poke_id in range(1, 650):  # 649 max
        print(f"Processing Pokémon ID {poke_id}...")
        data = fetch_pokemon_data(poke_id)
        pokemon_data.append(data)

    output_file = "pokemon_gen1-5.yaml"
    yaml = YAML()
    yaml.default_flow_style = False
    with open(output_file, "w") as file:
        yaml.dump(pokemon_data, file)
    print(f"Data fetching complete! Saved to {output_file}")

if __name__ == "__main__":
    main()
