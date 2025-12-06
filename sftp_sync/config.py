"""
Configuration module for SFTP Sync
"""

import os
import yaml
from typing import List, Dict, Optional


class Config:
    """Configuration class for SFTP synchronization"""
    
    def __init__(self, config_dict: Optional[Dict] = None):
        """
        Initialize configuration
        
        Args:
            config_dict: Dictionary containing configuration
        """
        if config_dict is None:
            config_dict = {}
        
        # Connection settings
        self.host = config_dict.get("host", "")
        self.port = config_dict.get("port", 22)
        self.username = config_dict.get("username", "")
        self.password = config_dict.get("password", None)
        self.private_key = config_dict.get("private_key", None)
        self.private_key_password = config_dict.get("private_key_password", None)
        
        # Directory settings
        self.local_dir = config_dict.get("local_dir", ".")
        self.remote_dir = config_dict.get("remote_dir", ".")
        
        # Synchronization settings
        self.include_patterns = config_dict.get("include_patterns", ["*"])
        self.exclude_patterns = config_dict.get("exclude_patterns", [])
        self.delete_remote = config_dict.get("delete_remote", False)
        self.preserve_permissions = config_dict.get("preserve_permissions", True)
        
        # Security settings
        self.auto_add_host_key = config_dict.get("auto_add_host_key", False)
        
        # Behavior settings
        self.dry_run = config_dict.get("dry_run", False)
        self.verbose = config_dict.get("verbose", False)
        self.follow_symlinks = config_dict.get("follow_symlinks", False)
        self.backup_remote = config_dict.get("backup_remote", False)
        
    @classmethod
    def from_yaml(cls, yaml_path: str) -> "Config":
        """
        Load configuration from YAML file
        
        Args:
            yaml_path: Path to YAML configuration file
            
        Returns:
            Config instance
        """
        with open(yaml_path, "r", encoding="utf-8") as f:
            config_dict = yaml.safe_load(f)
        return cls(config_dict)
    
    @classmethod
    def from_args(cls, args) -> "Config":
        """
        Create configuration from command-line arguments
        
        Args:
            args: Parsed command-line arguments
            
        Returns:
            Config instance
        """
        config_dict = {
            "host": args.host,
            "port": args.port,
            "username": args.username,
            "password": args.password,
            "private_key": args.private_key,
            "private_key_password": args.private_key_password,
            "local_dir": args.local_dir,
            "remote_dir": args.remote_dir,
            "include_patterns": args.include if args.include else ["*"],
            "exclude_patterns": args.exclude if args.exclude else [],
            "delete_remote": args.delete,
            "preserve_permissions": args.preserve_permissions,
            "auto_add_host_key": args.auto_add_host_key,
            "dry_run": args.dry_run,
            "verbose": args.verbose,
            "follow_symlinks": args.follow_symlinks,
            "backup_remote": args.backup,
        }
        return cls(config_dict)
    
    def validate(self) -> List[str]:
        """
        Validate configuration
        
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        if not self.host:
            errors.append("Host is required")
        if not self.username:
            errors.append("Username is required")
        if not self.password and not self.private_key:
            errors.append("Either password or private_key is required")
        if not self.local_dir:
            errors.append("Local directory is required")
        if not self.remote_dir:
            errors.append("Remote directory is required")
        if not os.path.exists(self.local_dir):
            errors.append(f"Local directory does not exist: {self.local_dir}")
        if self.private_key and not os.path.exists(self.private_key):
            errors.append(f"Private key file does not exist: {self.private_key}")
            
        return errors
    
    def to_dict(self) -> Dict:
        """
        Convert configuration to dictionary
        
        Returns:
            Dictionary representation of configuration
        """
        return {
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": "***" if self.password else None,
            "private_key": self.private_key,
            "local_dir": self.local_dir,
            "remote_dir": self.remote_dir,
            "include_patterns": self.include_patterns,
            "exclude_patterns": self.exclude_patterns,
            "delete_remote": self.delete_remote,
            "preserve_permissions": self.preserve_permissions,
            "auto_add_host_key": self.auto_add_host_key,
            "dry_run": self.dry_run,
            "verbose": self.verbose,
            "follow_symlinks": self.follow_symlinks,
            "backup_remote": self.backup_remote,
        }
