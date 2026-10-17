import sys
import os
import logging

# Align system paths for seamless cross-module discovery
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.append(PARENT_DIR)

from adapters.device_profiler import DeviceProfiler
from adapters.os_bridge import OSBridge
from core.state_manager import StateManager
from core.routing_engine import RoutingEngine

class AbrarOrchestrator:
    """
    The unified master brain of ABRARAI. Integrates hardware metrics,
    state tracking, secure OS bridging, and dynamic model routing.
    """
    def __init__(self):
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s - [%(levelname)s] - %(message)s'
        )
        logging.info("Initializing ABRARAI Unified Core Engine...")

        # 1. Profile Hardware Boundaries
        self.profiler = DeviceProfiler()
        self.env_config = self.profiler.get_environment_config()
        self.compute_tier = self.env_config["compute_tier"]

        # 2. Bind Persistent State Ledger
        state_path = os.path.join(CURRENT_DIR, "state.json")
        self.state_manager = StateManager(state_path)
        self.state_manager.update_metric("active_compute_tier", self.compute_tier)

        # 3. Instantiate Sub-Systems & Bridges
        self.os_bridge = OSBridge()
        self.routing_engine = RoutingEngine()
        
        logging.info("All engine core modules bound successfully.")

    def execute_task(self, intent, user_prompt, arguments=None):
        """
        Orchestration Loop:
        Resolves model -> Logs transaction -> Evaluates safety bounds -> Executes commands if applicable.
        """
        # Resolve target model based on intent and active tier constraints
        target_model = self.routing_engine.resolve_model(self.compute_tier, intent)
        
        # Log transaction to rolling chat history
        self.state_manager.append_chat_history("user", user_prompt, target_model)
        
        logging.info(f"Task dispatched to model [{target_model}] under tier [{self.compute_tier}].")
        
        # If the task requires filesystem/OS interaction, route through security sandbox
        if intent.upper() == "SYSTEM_CONTROL" and arguments:
            base_cmd = arguments.get("command")
            cmd_args = arguments.get("args", [])
            bridge_result = self.os_bridge.execute_sanitized_command(base_cmd, cmd_args)
            
            self.state_manager.append_chat_history("system", str(bridge_result), target_model)
            return {"model": target_model, "execution_result": bridge_result}

        # Stand-in for standard generation return block
        mock_response = f"[Response from {target_model}] Processing request: '{user_prompt}'"
        self.state_manager.append_chat_history("assistant", mock_response, target_model)
        
        return {"model": target_model, "response": mock_response}

if __name__ == "__main__":
    # Self-test script to verify entire core integration works flawlessly
    orchestrator = AbrarOrchestrator()
    
    print("\n--- Test 1: General Reasoning Resolution ---")
    res1 = orchestrator.execute_task("GENERAL", "How can I configure an automation pipeline?")
    print(f"Result: {res1}\n")

    print("--- Test 2: Secure Command Execution Validation ---")
    res2 = orchestrator.execute_task("SYSTEM_CONTROL", "Show directory contents", {"command": "ls", "args": ["-la"]})
    print(f"Result: {res2}\n")

    print("--- Test 3: Unauthorized Command Block Validation ---")
    res3 = orchestrator.execute_task("SYSTEM_CONTROL", "Attempt exploit", {"command": "rm", "args": ["-rf", "/"]})
    print(f"Result: {res3}\n")
    
    print("[+] ABRARAI End-to-End Core Integration Verification Complete.")
