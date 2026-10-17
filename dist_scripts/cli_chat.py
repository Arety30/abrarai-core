import sys
import os

# Align paths to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.abrar_ai_1 import AbrarOrchestrator

def main():
    print("="*50)
    print(" 🚀 ABRARAI TERMINAL CLIENT INITIALIZING...")
    print("="*50)
    
    orchestrator = AbrarOrchestrator()
    print("\n[System] Type 'exit' or 'quit' to terminate the session.\n")

    while True:
        try:
            user_input = input("\n[You]: ")
            if user_input.strip().lower() in ['exit', 'quit']:
                print("\n[System] Shutting down ABRARAI session. Goodbye.")
                break
            if not user_input.strip():
                continue

            # For now, we route everything as a GENERAL intent. 
            # In the future, an NLP classifier will determine this automatically.
            result = orchestrator.execute_task("GENERAL", user_input)
            
            print(f"\n[{result['model']}]: {result['response']}")

        except KeyboardInterrupt:
            print("\n\n[System] Session interrupted. Exiting gracefully.")
            break
        except Exception as e:
            print(f"\n[Error] {str(e)}")

if __name__ == "__main__":
    main()
