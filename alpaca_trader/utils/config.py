"""
Configuration utilities for the Alpaca trader application.
Handles loading and saving configuration values including API keys.
"""

import os
import json
import base64
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

# Define constants
DEFAULT_CONFIG_FILE = Path.home() / '.alpaca_trader' / 'config.json'
DEFAULT_KEY_FILE = Path.home() / '.alpaca_trader' / '.secret_key'
ENCRYPTION_KEY_SIZE = 32  # AES-256


class ConfigManager:
    """Manages configuration for the Alpaca trader application."""
    
    def __init__(self, config_file=None, key_file=None):
        """
        Initialize the configuration manager.
        
        Args:
            config_file (Path, optional): Path to the config file. Defaults to ~/.alpaca_trader/config.json.
            key_file (Path, optional): Path to the encryption key file. Defaults to ~/.alpaca_trader/.secret_key.
        """
        self.config_file = Path(config_file) if config_file else DEFAULT_CONFIG_FILE
        self.key_file = Path(key_file) if key_file else DEFAULT_KEY_FILE
        self.config = {}
        
        # Ensure directories exist
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Ensure encryption key exists
        if not self.key_file.exists():
            self._generate_encryption_key()
            
        # Load config if exists
        if self.config_file.exists():
            self.load_config()
    
    def _generate_encryption_key(self):
        """Generate a new encryption key and save it."""
        self.key_file.parent.mkdir(parents=True, exist_ok=True)
        key = get_random_bytes(ENCRYPTION_KEY_SIZE)
        with open(self.key_file, 'wb') as f:
            f.write(key)
        # Set restrictive permissions on key file
        os.chmod(self.key_file, 0o600)
    
    def _get_encryption_key(self):
        """Read encryption key from file."""
        with open(self.key_file, 'rb') as f:
            return f.read()
    
    def _encrypt_value(self, value):
        """
        Encrypt a string value.
        
        Args:
            value (str): The value to encrypt
            
        Returns:
            str: Base64 encoded encrypted value
        """
        key = self._get_encryption_key()
        iv = get_random_bytes(16)  # AES block size
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded_data = pad(value.encode('utf-8'), AES.block_size)
        encrypted_data = cipher.encrypt(padded_data)
        # Combine IV and encrypted data for storage
        result = base64.b64encode(iv + encrypted_data).decode('utf-8')
        return result
    
    def _decrypt_value(self, encrypted_value):
        """
        Decrypt an encrypted value.
        
        Args:
            encrypted_value (str): Base64 encoded encrypted value
            
        Returns:
            str: Decrypted value
        """
        key = self._get_encryption_key()
        try:
            raw_data = base64.b64decode(encrypted_value.encode('utf-8'))
            iv = raw_data[:16]
            encrypted_data = raw_data[16:]
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted_data = cipher.decrypt(encrypted_data)
            result = unpad(decrypted_data, AES.block_size).decode('utf-8')
            return result
        except Exception as e:
            print(f"Error decrypting value: {e}")
            return None
    
    def load_config(self):
        """Load configuration from file."""
        if not self.config_file.exists():
            self.config = {}
            return
        
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                
            # Decrypt sensitive values
            self.config = data.copy()
            if 'alpaca' in self.config:
                if 'api_key' in self.config['alpaca'] and self.config['alpaca']['api_key']:
                    self.config['alpaca']['api_key'] = self._decrypt_value(self.config['alpaca']['api_key'])
                if 'api_secret' in self.config['alpaca'] and self.config['alpaca']['api_secret']:
                    self.config['alpaca']['api_secret'] = self._decrypt_value(self.config['alpaca']['api_secret'])
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config = {}
    
    def save_config(self):
        """Save configuration to file."""
        # Create a copy to avoid modifying the original
        data_to_save = self.config.copy()
        
        # Encrypt sensitive values
        if 'alpaca' in data_to_save:
            if 'api_key' in data_to_save['alpaca'] and data_to_save['alpaca']['api_key']:
                data_to_save['alpaca']['api_key'] = self._encrypt_value(data_to_save['alpaca']['api_key'])
            if 'api_secret' in data_to_save['alpaca'] and data_to_save['alpaca']['api_secret']:
                data_to_save['alpaca']['api_secret'] = self._encrypt_value(data_to_save['alpaca']['api_secret'])
        
        # Ensure directory exists
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to file
        with open(self.config_file, 'w') as f:
            json.dump(data_to_save, f, indent=2)
        
        # Set restrictive permissions on config file
        os.chmod(self.config_file, 0o600)
    
    def get_alpaca_credentials(self):
        """
        Get Alpaca API credentials.
        
        Returns:
            tuple: (api_key, api_secret, base_url) or (None, None, None) if not configured
        """
        if 'alpaca' not in self.config:
            return None, None, None
        
        api_key = self.config['alpaca'].get('api_key')
        api_secret = self.config['alpaca'].get('api_secret')
        # Default to paper trading
        base_url = self.config['alpaca'].get('base_url', 'https://paper-api.alpaca.markets')
        
        return api_key, api_secret, base_url
    
    def set_alpaca_credentials(self, api_key, api_secret, paper_trading=True):
        """
        Set Alpaca API credentials.
        
        Args:
            api_key (str): Alpaca API key
            api_secret (str): Alpaca API secret
            paper_trading (bool, optional): Use paper trading environment. Defaults to True.
        """
        if 'alpaca' not in self.config:
            self.config['alpaca'] = {}
        
        self.config['alpaca']['api_key'] = api_key
        self.config['alpaca']['api_secret'] = api_secret
        
        # Set the appropriate base URL
        if paper_trading:
            self.config['alpaca']['base_url'] = 'https://paper-api.alpaca.markets'
        else:
            self.config['alpaca']['base_url'] = 'https://api.alpaca.markets'
        
        # Save immediately
        self.save_config()


# Singleton instance for global access
_config_manager = None

def get_config_manager():
    """
    Get or create the global ConfigManager instance.
    
    Returns:
        ConfigManager: The global configuration manager
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager 