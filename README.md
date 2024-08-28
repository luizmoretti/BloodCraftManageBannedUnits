# BloodCraftManageBannedUnits
This Python script is designed for **V Rising** servers using **Bloodcraft** mod. The script automates the process of verifying and removing banned familiars from each player's JSON database before the server starts. It reads a list of banned units from the mod's configuration file and compares these with the data in a character JSON file. The script then removes any banned familiars from each player's database, saving the modified files and providing a report on the changes made.

## How It Works

1. **Initialization**:
   - The script begins by initializing the `FamiliarUnlockChecker` class, which takes two parameters: the path to the configuration file and the path to the character JSON file. It also loads the list of banned units from the configuration file.

    ```python
    class FamiliarUnlockChecker:
        def __init__(self, config_file, json_char_file):
            self.config_file = config_file
            self.json_char_file = json_char_file
            self.banned_units = self.get_banned_units()
            self.player_file_data = r'BepInEx\config\Bloodcraft\Familiars\FamiliarUnlocks'
    ```

2. **Check for Banned Units**:
   - The method `get_banned_units` loads the banned units from the configuration file. It looks for the `BannedUnits =` line and parses the units listed there into a set.

    ```python
    def get_banned_units(self):
        """Loads the banned units from the configuration file."""
        with open(self.config_file, 'r') as file:
            for line in file:
                if line.strip().startswith('BannedUnits ='):
                    return set(
                        int(unit) for unit in line.split('=')[1].strip().split(',')
                        if unit
                    )
        print("BannedUnits value not found or is empty")
        return set()
    ```

3. **Comparison with Character Data**:
   - The method `compare_to_char_json` compares the banned units with the units in the CHAR.JSON file. It creates a reverse lookup dictionary to match unit IDs with their corresponding names. This method also prints out any banned units found in the character data.

    ```python
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
    ```

4. **Database Modification**:
   - The `process_player_data` method processes each player's data file. Depending on the operation specified (`count` or `delete`), it either counts the number of banned units or removes them from the player's database. It also updates and saves any modified files.

    ```python
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
    ```

5. **Counting Banned Units**:
   - The `get_player_data` method calls `process_player_data` with the `count` operation to tally how many players have banned familiars.

    ```python
    def get_player_data(self):
        """Counts how many players have unlocked banned familiars."""
        self.process_player_data(operation="count")
    ```

6. **Removing Banned Units**:
   - The `delete_banned_units_from_player_data` method calls `process_player_data` with the `delete` operation to remove any banned units from the player data.

    ```python
    def delete_banned_units_from_player_data(self):
        """Removes banned units from player data."""
        self.process_player_data(operation="delete")
    ```

7. **Main Execution**:
   - The `main` function sets up the paths for the configuration and character JSON files, instantiates the `FamiliarUnlockChecker` class, and calls the methods to check and remove banned units.

    ```python
    def main():
        config_file_path = os.path.join(r'BepInEx\config\io.zfolmt.Bloodcraft.cfg')
        json_char_file = os.path.join(r'jsonfilter\CHAR.json')
        
        famcheck = FamiliarUnlockChecker(config_file_path, json_char_file)
        famcheck.get_player_data()
        famcheck.delete_banned_units_from_player_data()

    if __name__ == "__main__":
        main()
    ```

## Script Execution

This script is intended to be run **before** starting the V Rising server.

- **Included in this repository** is a `serverstartexemple.txt` file that can be renamed to `.bat` or modified to suit your existing server startup script. Place this script in your server's directory and ensure it runs prior to server initialization.

## Usage Instructions

1. **Setup**:
   - Ensure the Bloodcraft mod's configuration file (`io.zfolmt.Bloodcraft.cfg`) and the `CHAR.json` file are in their correct directories.
   - Modify the script paths if necessary to match your server's directory structure.

2. **Running the Script**:
   - Before starting your server, run the script with Python:
     ```sh
     python familiar_unlock_checker.py
     ```
   - The script will automatically check for banned units, modify the player databases, and output a summary of the actions taken.

3. **Server Startup**:
   - After the script has completed, start your V Rising server using the modified `.bat` file or your preferred startup method.

## Summary

The `FamiliarUnlockChecker` script is a critical tool for administrators of V Rising servers using the Bloodcraft mod. It ensures compliance with server rules by removing banned familiars from player databases before the server starts. The script provides a clear and concise report on the modifications made, helping server administrators maintain a fair and balanced gaming environment.
