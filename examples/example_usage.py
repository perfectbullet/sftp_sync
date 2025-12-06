#!/usr/bin/env python3
"""
Example script demonstrating SFTP Sync usage
示例脚本演示SFTP同步使用
"""

from sftp_sync import SFTPSyncer, Config
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def main():
    # Example 1: Basic sync with password
    print("Example 1: Basic sync with password authentication")
    config1 = Config({
        "host": "192.168.1.100",
        "port": 22,
        "username": "myuser",
        "password": "mypassword",
        "local_dir": "./my-project",
        "remote_dir": "/var/www/html",
        "exclude_patterns": [
            "*.pyc",
            "__pycache__",
            ".git",
            "node_modules",
            ".env"
        ],
        "dry_run": True,  # Preview mode
        "verbose": True
    })
    
    # Validate configuration
    errors = config1.validate()
    if errors:
        print("Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        return
    
    # Uncomment to actually run the sync
    # syncer1 = SFTPSyncer(config1)
    # syncer1.sync()
    
    print("\n" + "="*50 + "\n")
    
    # Example 2: Sync with SSH key (more secure)
    print("Example 2: Sync with SSH key authentication")
    config2 = Config({
        "host": "example.com",
        "port": 22,
        "username": "myuser",
        "private_key": "/home/user/.ssh/id_rsa",
        "local_dir": "./src",
        "remote_dir": "/var/www/html",
        "include_patterns": ["*.py", "*.txt", "*.html"],
        "dry_run": True,
        "verbose": True
    })
    
    # Uncomment to actually run the sync
    # syncer2 = SFTPSyncer(config2)
    # syncer2.sync()
    
    print("\n" + "="*50 + "\n")
    
    # Example 3: Sync with deletion of remote files
    print("Example 3: Sync with deletion (mirror mode)")
    config3 = Config({
        "host": "192.168.1.100",
        "username": "myuser",
        "password": "mypassword",
        "local_dir": "./dist",
        "remote_dir": "/var/www/html",
        "delete_remote": True,  # Delete remote files not in local
        "backup_remote": True,  # Backup before overwriting
        "dry_run": True,
        "verbose": True
    })
    
    # Uncomment to actually run the sync
    # syncer3 = SFTPSyncer(config3)
    # syncer3.sync()
    
    print("\nExamples completed. Set dry_run=False to execute actual sync.")


if __name__ == "__main__":
    main()
