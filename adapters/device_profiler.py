import platform
import psutil
import logging

class DeviceProfiler:
    """
    Detects the host OS and hardware capabilities to configure 
    the ABRARAI engine safely before any models are loaded.
    """
    def __init__(self):
        self.os_type = platform.system().lower()
        self.total_ram_gb = round(psutil.virtual_memory().total / (1024 ** 3), 2)
        
    def get_environment_config(self):
        """Returns the safe operating tier based on detected hardware."""
        tier = self._determine_tier()
        
        logging.info(f"Detected OS: {self.os_type}")
        logging.info(f"Available RAM: {self.total_ram_gb} GB")
        logging.info(f"Assigned Compute Tier: {tier}")
        
        return {
            "os": self.os_type,
            "ram_gb": self.total_ram_gb,
            "compute_tier": tier
        }

    def _determine_tier(self):
        # A simple memory-based tiering logic to protect device stability
        if self.total_ram_gb >= 16:
            return "EXPERT"   # Safe for Heavy DeepSeek models
        elif self.total_ram_gb >= 8:
            return "BALANCED" # Safe for 3B/8B models
        else:
            return "LITE"     # Strictly small/fast models for mobile/low-end
