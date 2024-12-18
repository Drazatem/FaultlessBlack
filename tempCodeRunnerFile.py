import requests
import json
from typing import List, Dict, Union

# Constants
BASE_URL = "https://pokeapi.co/api/v2/pokemon/"
SPECIES_URL = "https://pokeapi.co/api/v2/pokemon-species/"
PLACEHOLDER = "ReplaceMe"
DEFAULT_STATS = {"HP": 0, "Atk": 0, "Def": 0, "SpAtk": 0, "SpDef": 0, "Speed": 0}

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
    return [a["ability"]["name"] for a in data.get("abilities", [])] or [PLACEHOLDER, PLACEHOLDER]

def get_stats(data: dict) -> Dict[str, int]:
    """Extract Pokémon stats."""
    stats = {stat["stat"]["name"]: stat["base_stat"] for stat in data.get("stats", [])}
    stats["BST"] = sum(stats.values())  # Base Stat Total
    return stats

def get_learnset(data: dict) -> List[dict]:
    """Extract learnable moves."""
    learnset = []
    for move in data.get("moves", []):
        details = [
            detail for detail in move["version_group_details"]
            if detail["level_learned_at"] > 0 and detail["version_group"]["name"] == "scarlet-violet"
        ]
        if details:
            learnset.append({
                "Move": move["move"]["name"],
                "Level": details[0]["level_learned_at"],
                "KEY": "",
                "Altered": ""
            })
    return sorted(learnset, key=lambda x: x["Level"])

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
                    "Method": evolution["evolution_details"][0].get("trigger", {}).get("name", "Unknown"),
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

def fetch_pokemon_data(poke_id: int) -> dict:
    """Fetch data for a single Pokémon."""
    pokemon_data = fetch_data(f"{BASE_URL}{poke_id}")
    if not pokemon_data:
        return {"Number": poke_id, "Name": PLACEHOLDER, "Type": [PLACEHOLDER, PLACEHOLDER], "Abilities": [PLACEHOLDER], "Stats": DEFAULT_STATS, "Evolution": [{"Method": "Error"}], "Learnset": []}

    species_data = fetch_data(f"{SPECIES_URL}{poke_id}")
    evolution_chain = get_evolution_chain(species_data) if species_data else [{"Method": "Error"}]

    return {
    "Number": poke_id,
    "Name": pokemon_data["name"].capitalize(),
    "Type": [t.capitalize() for t in get_types(pokemon_data)],
    "Abilities": [a.capitalize() for a in get_abilities(pokemon_data)],
    "Evolution": [
        {key.capitalize(): (value.capitalize() if isinstance(value, str) else value) for key, value in evo.items()}
        for evo in evolution_chain
    ],
    "Stats": {
        "Vanilla": {k.capitalize(): v for k, v in get_stats(pokemon_data).items()},
        "Updated": {k.capitalize(): v for k, v in get_stats(pokemon_data).items()},
        "Changes": DEFAULT_STATS
    },
    "Learnset": [
        {key.capitalize(): (value.capitalize() if isinstance(value, str) else value) for key, value in move.items()}
        for move in get_learnset(pokemon_data)
    ]
    }


# Main execution
def main():
    pokemon_data = []
    for poke_id in range(1, 5):  # Adjust range as needed
        print(f"Processing Pokémon ID {poke_id}...")
        data = fetch_pokemon_data(poke_id)
        pokemon_data.append(data)

    output_file = "pokemon_gen1-5.json"
    with open(output_file, "w") as file:
        json.dump(pokemon_data, file, indent=4)
    print(f"Data fetching complete! Saved to {output_file}")

if __name__ == "__main__":
    main()
