import logging

class RoutingEngine:
    """
    Dynamically maps user intents to specific local models 
    based on the system's active compute tier constraint.
    """
    def __init__(self):
        # Strict model assignments mapped by hardware capability tier
        self.tier_mappings = {
            "EXPERT": {
                "VOICE_LIVE": "gemma2:2b",      # Fast response latency for voice streaming
                "CODING": "deepseek-r1:7b",    # High-reasoning structural analysis
                "GENERAL": "llama3.2:3b"        # Versatile context orchestrator
            },
            "BALANCED": {
                "VOICE_LIVE": "gemma2:2b",
                "CODING": "qwen2.5:3b",        # Optimized performance-to-weight ratio
                "GENERAL": "llama3.2:3b"
            },
            "LITE": {
                "VOICE_LIVE": "gemma2:2b",     # Gemma remains highly active on mobile
                "CODING": "deepseek-r1:1.5b",  # Distilled reasoning variant for low footprint
                "GENERAL": "llama3.2:1b"       # Ultra-lightweight mobility baseline
            }
        }

    def resolve_model(self, compute_tier, intent):
        """Returns the exact local model identifier required to execute the task."""
        tier = compute_tier.upper()
        if tier not in self.tier_mappings:
            logging.warning(f"Unknown compute tier '{tier}', dropping to LITE constraints safely.")
            tier = "LITE"

        intent_map = self.tier_mappings[tier]
        selected_model = intent_map.get(intent.upper(), intent_map["GENERAL"])
        
        logging.info(f"RoutingEngine resolved action [{intent}] to target model [{selected_model}]")
        return selected_model
