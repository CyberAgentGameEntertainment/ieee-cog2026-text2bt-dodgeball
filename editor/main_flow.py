from winsound import Beep
import os
import pathlib
from dotenv import load_dotenv
from editor_agent.Config import CONFIG
from editor_agent.Logging import LOGGER
from editor_agent.Agent import run_agent

dotenv_path = pathlib.Path(__file__).parent / ".env"
load_dotenv(dotenv_path)

if __name__ == "__main__":
    project_dir = os.getenv("PROJECT_DIRECTORY")
    CONFIG.PROJECT_DIRECTORY = pathlib.Path(project_dir)

    user_input = "Create behavior tree that can validly play the dodgeball game well"
    # user_input = input("Enter your request: ")

    try:
        output = run_agent(user_input=user_input)
        print("\n" + "="*50)
        print("FINAL OUTPUT:")
        print("="*50)
        print(f"Messages: {len(output['messages'])} messages")
        print(f"C# Errors: {output.get('csharp_error', 'N/A')}")
        print(f"BT Generated: {output.get('bt_generated', 'N/A')}")
        print(f"BT Errors: {output.get('bt_error', 'N/A')}")
        print("="*50)
        
        LOGGER.log("=== FINAL STATE ===")
        LOGGER.log(f"C# Errors: {output.get('csharp_error', 'N/A')}")
        LOGGER.log(f"BT Generated: {output.get('bt_generated', 'N/A')}")
        LOGGER.log(f"BT Errors: {output.get('bt_error', 'N/A')}")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        LOGGER.log(f"ERROR: {e}")
        import traceback
        LOGGER.log(traceback.format_exc())
        Beep(500, 1000)

    LOGGER.wrap_result()

    # Beep to notify completion
    Beep(1000, 1000)

