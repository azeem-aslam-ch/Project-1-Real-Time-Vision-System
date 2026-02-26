import yaml
import os
from pathlib import Path

class Config:
    def __init__(self, config_path="config/config.yaml"):
        self.config_path = Path(config_path)
        self.data = self._load_config()

    def _load_config(self):
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, "r") as f:
            config = yaml.safe_load(f)
        
        # Override with environment variables if present
        # Pattern: APP_SECTION_KEY
        for section, values in config.items():
            if isinstance(values, dict):
                for key, value in values.items():
                    env_key = f"APP_{section.upper()}_{key.upper()}"
                    if env_key in os.environ:
                        config[section][key] = os.environ[env_key]
        
        return config

    @property
    def api(self): return self.data.get("api", {})
    
    @property
    def inference(self): return self.data.get("inference", {})
    
    @property
    def tracking(self): return self.data.get("tracking", {})
    
    @property
    def events(self): return self.data.get("events", {})
    
    @property
    def storage(self): return self.data.get("storage", {})
    
    @property
    def logging(self): return self.data.get("logging", {})

# Singleton instance
config = Config()
