import json
import sys
import os


class FamiliarUnlockChecker:
    def __init__(self, config_file, json_char_file):
        self.config_file = config_file
        self.json_char_file = json_char_file
        self.banned_units = self.get_banned_units()
        self.player_file_data = r'BepInEx\config\Bloodcraft\Familiars\FamiliarUnlocks'

    def get_banned_units(self):
        """Loads the banned units from the configuration file."""
        with open(self.config_file, 'r') as file:
            for line in file:
                if 'BannedUnits =' in line:
                    line = line.strip()
                    print(f"Found line: {line}")
                    parts = line.split('=', 1)
                    if len(parts) > 1:
                        banned_units = set(
                            int(unit) for unit in parts[1].strip().split(',')
                            if unit
                        )
                        print(f"Banned units found: {banned_units}")
                        return banned_units
        print("BannedUnits value not found or is empty")
        return set()

    def compare_to_char_json(self):
        """Compares the banned units with the units in the character JSON file."""
        if not self.banned_units:
            return False

        with open(self.json_char_file, 'r') as file:
            data = json.load(file)
            reverse_lookup = {v: k for k, v in data.items()}  # Creates a reverse lookup dictionary

            found_any = False
            for unit in self.banned_units:
                if unit in reverse_lookup:
                    print(f"Unit {unit} ({reverse_lookup[unit]}) is banned")
                    found_any = True

            if not found_any:
                print("No banned units found in the JSON data.")
            
            return found_any

    def process_player_data(self, operation):
        """Processes the player data files based on the provided operation."""
        total_players = 0

        for file in os.listdir(self.player_file_data):
            
            if file.endswith('_familiar_unlocks.json'):
                file_path = os.path.join(self.player_file_data, file)
                
                with open(file_path, 'r') as json_file:
                    data = json.load(json_file)
                    unlocked_familiars = data.get("UnlockedFamiliars", {})
                    modified = False

                    for box, units in unlocked_familiars.items():
                        
                        if operation == "count":
                            banned_count = sum(1 for unit in units if unit in self.banned_units)
                            if banned_count > 0:
                                print(f"File: {file}, Box: {box}, Players with banned familiar unlocked: {banned_count}")
                            total_players += banned_count
                        
                        elif operation == "delete":
                            original_count = len(units)
                            units[:] = [unit for unit in units if unit not in self.banned_units]
                            
                            if len(units) < original_count:
                                modified = True
                                print(f"File: {file}, Box: {box} - Banned units removed.")

                    if modified and operation == "delete":
                        with open(file_path, 'w') as json_file:
                            json.dump(data, json_file, ensure_ascii=False, indent=2)
                        print(f"File {file} updated and saved successfully.")

        if operation == "count":
            print(f"Total of players that have unlocked the Banned familiar across all boxes in players json files: {total_players}")

    def get_player_data(self):
        """Counts how many players have unlocked banned familiars."""
        self.process_player_data(operation="count")

    def delete_banned_units_from_player_data(self):
        """Removes banned units from player data."""
        self.process_player_data(operation="delete")

def main():
    config_file_path = os.path.join(r'BepInEx\config\io.zfolmt.Bloodcraft.cfg')
    json_char_file = os.path.join(r'jsonfilter\CHAR.json')
    
    famcheck = FamiliarUnlockChecker(config_file_path, json_char_file)
    famcheck.get_player_data()
    famcheck.delete_banned_units_from_player_data()

if __name__ == "__main__":
    main()
