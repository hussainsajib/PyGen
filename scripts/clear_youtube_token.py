import json
import os
import sys

# This assumes the script is run from the project root
TOKEN_STORE_FILE = "client_info.json"

def clear_token():
    if not os.path.exists(TOKEN_STORE_FILE):
        print(f"Token file '{TOKEN_STORE_FILE}' not found.")
        return

    with open(TOKEN_STORE_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"Could not read '{TOKEN_STORE_FILE}'. It might be corrupted.")
            return

    channels = {i+1: key for i, key in enumerate(data.keys()) if key != "web"}
    
    if not channels:
        print("No channel tokens found in the file.")
        return

    print("Select the channel token to clear:")
    for i, key in channels.items():
        print(f"  {i}: {key}")
    
    try:
        choice = int(input("Enter number: "))
        if choice not in channels:
            print("Invalid selection.")
            return
            
        key_to_delete = channels[choice]
        del data[key_to_delete]
        
        with open(TOKEN_STORE_FILE, "w") as f:
            json.dump(data, f, indent=4)
        
        print(f"Successfully removed token for channel: {key_to_delete}")

    except ValueError:
        print("Invalid input. Please enter a number.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    clear_token()
