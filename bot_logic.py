import sys
import json
import os

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chat_states.json')

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=4)

def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Missing arguments. Usage: python bot_logic.py <chat_id> <message>"}))
        return

    chat_id = sys.argv[1]
    message = sys.argv[2].strip().lower()

    states = load_state()
    
    # Initialize state for new user or if they typed /start
    if chat_id not in states or message in ["/start", "restart", "cancel"]:
        states[chat_id] = {"step": "ask_ram", "params": {"query": ""}}
        save_state(states)
        print(json.dumps({
            "action": "REPLY",
            "chat_id": chat_id,
            "message": "👋 Welcome to Zezo's Laptop Deal Scraper!\n\nHow much RAM do you need in GB? (e.g., '16', '32', or type 'skip' if you don't care)"
        }))
        return

    user_state = states[chat_id]
    step = user_state.get("step")

    if step == "ask_ram":
        if message != 'skip' and not message.isdigit():
            print(json.dumps({
                "action": "REPLY",
                "chat_id": chat_id,
                "message": "Please enter a valid number for RAM (e.g., 16) or type 'skip'."
            }))
            return
            
        user_state["params"]["ram"] = message if message != 'skip' else ""
        user_state["step"] = "ask_hard_disk"
        save_state(states)
        print(json.dumps({
            "action": "REPLY",
            "chat_id": chat_id,
            "message": "Got it.\n\nHow much Hard Disk storage do you need? (e.g., '512', '1', '1tb', or type 'skip')"
        }))
        return

    elif step == "ask_hard_disk":
        user_state["params"]["hard_disk"] = sys.argv[2].strip() if message != 'skip' else ""
        user_state["step"] = "ask_gpu"
        save_state(states)
        print(json.dumps({
            "action": "REPLY",
            "chat_id": chat_id,
            "message": "Perfect.\n\nWhat GPU/Graphics Card are you looking for? (e.g., 'rtx 3050', 'rtx 4060', or type 'skip')"
        }))
        return

    elif step == "ask_gpu":
        user_state["params"]["gpu"] = sys.argv[2].strip() if message != 'skip' else ""
        user_state["step"] = "ask_budget"
        save_state(states)
        print(json.dumps({
            "action": "REPLY",
            "chat_id": chat_id,
            "message": "Almost done!\n\nWhat is your MAXIMUM budget in EGP? (e.g., '60000', or type 'skip')"
        }))
        return

    elif step == "ask_budget":
        if message != 'skip' and not message.isdigit():
            print(json.dumps({
                "action": "REPLY",
                "chat_id": chat_id,
                "message": "Please enter a valid number for Budget (e.g., 60000) or type 'skip'."
            }))
            return
            
        user_state["params"]["max_price"] = message if message != 'skip' else ""
        user_state["step"] = "ask_speed"
        save_state(states)
        print(json.dumps({
            "action": "REPLY",
            "chat_id": chat_id,
            "message": "How deep do you want to search?\n1. Fast (40 items, ~40 seconds)\n2. Medium (120 items, ~2 minutes)\n3. Deep (300 items, ~5 minutes)\n\nType 1, 2, or 3:"
        }))
        return

    elif step == "ask_speed":
        if message not in ["1", "2", "3"]:
            print(json.dumps({
                "action": "REPLY",
                "chat_id": chat_id,
                "message": "Please enter exactly 1, 2, or 3."
            }))
            return
            
        speed_map = {
            "1": {"count": 40, "eta": "40 seconds"},
            "2": {"count": 120, "eta": "2 minutes"},
            "3": {"count": 300, "eta": "5 minutes"}
        }
        
        user_state["params"]["item_count"] = speed_map[message]["count"]
        eta = speed_map[message]["eta"]
        
        # We have all the parameters! We send EXECUTE and delete the state so they can start over next time.
        final_params = user_state["params"]
        
        # Smart Search Query: Append RAM, Hard Disk, and GPU to the search query so scrapers find highly relevant results immediately
        search_query = final_params["query"]
        if final_params.get("ram"):
            search_query += f" {final_params['ram']}gb"
        if final_params.get("hard_disk"):
            search_query += f" {final_params['hard_disk']}"
        if final_params.get("gpu"):
            search_query += f" {final_params['gpu']}"
            
        final_params["query"] = search_query
        
        del states[chat_id]
        save_state(states)
        
        print(json.dumps({
            "action": "EXECUTE",
            "chat_id": chat_id,
            "message": f"🚀 Awesome! I am scraping the web and filtering the best deals for you now.\n\nThis will take approximately {eta}...",
            "parameters": final_params
        }))
        return

    else:
        # Fallback
        del states[chat_id]
        save_state(states)
        print(json.dumps({
            "action": "REPLY",
            "chat_id": chat_id,
            "message": "Oops, something went wrong. Let's start over. What are you searching for?"
        }))

if __name__ == "__main__":
    main()
