"""
Command-line interface for SFTP Sync
"""

import argparse
import logging
import sys
from pathlib import Path

from .config import Config
from .syncer import SFTPSyncer


def setup_logging(verbose: bool = False):
    """
    Setup logging configuration
    
    Args:
        verbose: Enable verbose logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def main():
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(
        description="SFTP Sync - 同步本地代码到远程服务器 (Sync local code to remote server)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic sync with password
  sftp-sync --host 192.168.1.100 --username user --password pass \\
            --local-dir /path/to/local --remote-dir /path/to/remote
  
  # Sync with SSH key
  sftp-sync --host example.com --username user --private-key ~/.ssh/id_rsa \\
            --local-dir ./my-project --remote-dir /var/www/html
  
  # Dry run with exclude patterns
  sftp-sync --host example.com --username user --password pass \\
            --local-dir . --remote-dir /app \\
            --exclude "*.pyc" --exclude "__pycache__" --exclude ".git" \\
            --dry-run
  
  # Use config file
  sftp-sync --config config.yaml
        """
    )
    
    # Configuration file
    parser.add_argument(
        "-c", "--config",
        help="Path to YAML configuration file"
    )
    
    # Connection settings
    parser.add_argument(
        "--host",
        help="Remote host (IP or hostname)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=22,
        help="SSH port (default: 22)"
    )
    parser.add_argument(
        "--username",
        help="SSH username"
    )
    parser.add_argument(
        "--password",
        help="SSH password (not recommended, use SSH key instead)"
    )
    parser.add_argument(
        "--private-key",
        help="Path to SSH private key file"
    )
    parser.add_argument(
        "--private-key-password",
        help="Password for encrypted private key"
    )
    
    # Directory settings
    parser.add_argument(
        "--local-dir",
        default=".",
        help="Local directory to sync (default: current directory)"
    )
    parser.add_argument(
        "--remote-dir",
        help="Remote directory path"
    )
    
    # Filter settings
    parser.add_argument(
        "--include",
        action="append",
        help="Include pattern (can be specified multiple times, e.g., '*.py')"
    )
    parser.add_argument(
        "--exclude",
        action="append",
        help="Exclude pattern (can be specified multiple times, e.g., '*.pyc', '__pycache__')"
    )
    
    # Security settings
    parser.add_argument(
        "--auto-add-host-key",
        action="store_true",
        help="Automatically add unknown host keys (less secure, for testing/development only)"
    )
    
    # Behavior settings
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete remote files that don't exist locally"
    )
    parser.add_argument(
        "--no-preserve-permissions",
        dest="preserve_permissions",
        action="store_false",
        default=True,
        help="Don't preserve file permissions"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a trial run with no changes made"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--follow-symlinks",
        action="store_true",
        help="Follow symbolic links"
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Backup remote files before overwriting"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        if args.config:
            logger.info(f"Loading configuration from: {args.config}")
            config = Config.from_yaml(args.config)
        else:
            # Validate required arguments
            if not args.host or not args.username or not args.remote_dir:
                parser.error("--host, --username, and --remote-dir are required (or use --config)")
            config = Config.from_args(args)
        
        # Validate configuration
        errors = config.validate()
        if errors:
            logger.error("Configuration errors:")
            for error in errors:
                logger.error(f"  - {error}")
            sys.exit(1)
        
        # Print configuration
        if config.verbose:
            logger.info("Configuration:")
            for key, value in config.to_dict().items():
                logger.info(f"  {key}: {value}")
        
        # Perform synchronization
        syncer = SFTPSyncer(config)
        syncer.sync()
        
        logger.info("Synchronization completed successfully")
        sys.exit(0)
        
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
