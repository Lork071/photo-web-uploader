import json
import os
from typing import List, Dict, Optional


class FTPConfig:
    """Třída pro správu FTP konfigurací"""
    
    def __init__(self, config_file: str = "ftp_configs.json"):
        self.config_file = config_file
        self.configs = self._load_configs()
    
    def _load_configs(self) -> List[Dict]:
        """Načte konfigurace ze souboru"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Chyba při načítání konfigurace: {e}")
                return []
        return []
    
    def _save_configs(self):
        """Uloží konfigurace do souboru"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.configs, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Chyba při ukládání konfigurace: {e}")
    
    def add_config(self, name: str, host: str, port: int, username: str, password: str) -> bool:
        """Přidá novou konfiguraci"""
        # Zkontroluj, zda název již neexistuje
        if any(cfg['name'] == name for cfg in self.configs):
            return False
        
        config = {
            'name': name,
            'host': host,
            'port': port,
            'username': username,
            'password': password
        }
        self.configs.append(config)
        self._save_configs()
        return True
    
    def remove_config(self, name: str) -> bool:
        """Odstraní konfiguraci podle názvu"""
        original_len = len(self.configs)
        self.configs = [cfg for cfg in self.configs if cfg['name'] != name]
        if len(self.configs) < original_len:
            self._save_configs()
            return True
        return False
    
    def update_config(self, old_name: str, name: str, host: str, port: int, 
                     username: str, password: str) -> bool:
        """Aktualizuje existující konfiguraci"""
        for cfg in self.configs:
            if cfg['name'] == old_name:
                cfg['name'] = name
                cfg['host'] = host
                cfg['port'] = port
                cfg['username'] = username
                cfg['password'] = password
                self._save_configs()
                return True
        return False
    
    def get_config(self, name: str) -> Optional[Dict]:
        """Vrátí konfiguraci podle názvu"""
        for cfg in self.configs:
            if cfg['name'] == name:
                return cfg
        return None
    
    def get_all_configs(self) -> List[Dict]:
        """Vrátí všechny konfigurace"""
        return self.configs
    
    def get_config_names(self) -> List[str]:
        """Vrátí seznam všech názvů konfigurací"""
        return [cfg['name'] for cfg in self.configs]
