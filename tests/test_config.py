"""
Unit tests for configuration module
"""

import unittest
import tempfile
import os
from sftp_sync.config import Config


class TestConfig(unittest.TestCase):
    """Test cases for Config class"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = Config()
        self.assertEqual(config.port, 22)
        self.assertEqual(config.local_dir, ".")
        self.assertEqual(config.remote_dir, ".")
        self.assertEqual(config.include_patterns, ["*"])
        self.assertEqual(config.exclude_patterns, [])
        self.assertFalse(config.delete_remote)
        self.assertTrue(config.preserve_permissions)
        self.assertFalse(config.dry_run)
    
    def test_config_from_dict(self):
        """Test creating config from dictionary"""
        config_dict = {
            "host": "example.com",
            "port": 2222,
            "username": "testuser",
            "password": "testpass",
            "local_dir": "/tmp/local",
            "remote_dir": "/tmp/remote",
            "exclude_patterns": ["*.pyc", ".git"],
            "dry_run": True,
            "verbose": True,
        }
        config = Config(config_dict)
        self.assertEqual(config.host, "example.com")
        self.assertEqual(config.port, 2222)
        self.assertEqual(config.username, "testuser")
        self.assertEqual(config.password, "testpass")
        self.assertEqual(config.local_dir, "/tmp/local")
        self.assertEqual(config.remote_dir, "/tmp/remote")
        self.assertEqual(config.exclude_patterns, ["*.pyc", ".git"])
        self.assertTrue(config.dry_run)
        self.assertTrue(config.verbose)
    
    def test_config_validation_missing_host(self):
        """Test validation fails when host is missing"""
        config = Config({"username": "user", "password": "pass"})
        errors = config.validate()
        self.assertIn("Host is required", errors)
    
    def test_config_validation_missing_username(self):
        """Test validation fails when username is missing"""
        config = Config({"host": "example.com", "password": "pass"})
        errors = config.validate()
        self.assertIn("Username is required", errors)
    
    def test_config_validation_missing_auth(self):
        """Test validation fails when both password and key are missing"""
        config = Config({"host": "example.com", "username": "user"})
        errors = config.validate()
        self.assertIn("Either password or private_key is required", errors)
    
    def test_config_validation_nonexistent_local_dir(self):
        """Test validation fails when local directory doesn't exist"""
        config = Config({
            "host": "example.com",
            "username": "user",
            "password": "pass",
            "local_dir": "/nonexistent/directory",
            "remote_dir": "/tmp"
        })
        errors = config.validate()
        self.assertTrue(any("does not exist" in error for error in errors))
    
    def test_config_validation_success(self):
        """Test validation succeeds with valid config"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config({
                "host": "example.com",
                "username": "user",
                "password": "pass",
                "local_dir": tmpdir,
                "remote_dir": "/tmp"
            })
            errors = config.validate()
            self.assertEqual(errors, [])
    
    def test_config_to_dict(self):
        """Test converting config to dictionary"""
        config = Config({
            "host": "example.com",
            "username": "user",
            "password": "secret",
        })
        config_dict = config.to_dict()
        self.assertEqual(config_dict["host"], "example.com")
        self.assertEqual(config_dict["username"], "user")
        self.assertEqual(config_dict["password"], "***")  # Password should be masked
    
    def test_config_from_yaml(self):
        """Test loading config from YAML file"""
        yaml_content = """
host: example.com
port: 2222
username: testuser
password: testpass
local_dir: /tmp/local
remote_dir: /tmp/remote
exclude_patterns:
  - "*.pyc"
  - ".git"
dry_run: true
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            yaml_path = f.name
        
        try:
            config = Config.from_yaml(yaml_path)
            self.assertEqual(config.host, "example.com")
            self.assertEqual(config.port, 2222)
            self.assertEqual(config.username, "testuser")
            self.assertEqual(config.password, "testpass")
            self.assertTrue(config.dry_run)
            self.assertEqual(config.exclude_patterns, ["*.pyc", ".git"])
        finally:
            os.unlink(yaml_path)


if __name__ == "__main__":
    unittest.main()
