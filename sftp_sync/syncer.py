"""
SFTP Synchronization module
"""

import os
import stat
import logging
import paramiko
from pathlib import Path
from typing import List, Tuple, Optional
from tqdm import tqdm

from .config import Config
from .filter import FileFilter


logger = logging.getLogger(__name__)


class SFTPSyncer:
    """SFTP synchronization handler"""
    
    def __init__(self, config: Config):
        """
        Initialize SFTP syncer
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.file_filter = FileFilter(
            config.include_patterns,
            config.exclude_patterns
        )
        self.ssh_client = None
        self.sftp_client = None
        self.stats = {
            "uploaded": 0,
            "skipped": 0,
            "deleted": 0,
            "errors": 0,
        }
        
    def connect(self):
        """Establish SFTP connection"""
        logger.info(f"Connecting to {self.config.username}@{self.config.host}:{self.config.port}")
        
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            connect_kwargs = {
                "hostname": self.config.host,
                "port": self.config.port,
                "username": self.config.username,
            }
            
            if self.config.private_key:
                # Use SSH key authentication
                logger.info(f"Using SSH key: {self.config.private_key}")
                pkey = paramiko.RSAKey.from_private_key_file(
                    self.config.private_key,
                    password=self.config.private_key_password
                )
                connect_kwargs["pkey"] = pkey
            else:
                # Use password authentication
                connect_kwargs["password"] = self.config.password
            
            self.ssh_client.connect(**connect_kwargs)
            self.sftp_client = self.ssh_client.open_sftp()
            logger.info("Connected successfully")
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            raise
    
    def disconnect(self):
        """Close SFTP connection"""
        if self.sftp_client:
            self.sftp_client.close()
        if self.ssh_client:
            self.ssh_client.close()
        logger.info("Disconnected")
    
    def sync(self):
        """
        Synchronize local directory to remote directory
        """
        try:
            self.connect()
            
            if self.config.dry_run:
                logger.info("DRY RUN MODE - No changes will be made")
            
            # Ensure remote directory exists
            self._ensure_remote_dir(self.config.remote_dir)
            
            # Get all files to sync
            local_files = self._get_local_files()
            logger.info(f"Found {len(local_files)} files to process")
            
            # Filter files
            files_to_sync = self.file_filter.filter_files(local_files)
            logger.info(f"After filtering: {len(files_to_sync)} files to sync")
            
            if self.config.verbose:
                logger.info("Files to sync:")
                for f in files_to_sync:
                    logger.info(f"  {f}")
            
            # Sync files with progress bar
            with tqdm(total=len(files_to_sync), desc="Syncing files", unit="file") as pbar:
                for rel_path in files_to_sync:
                    try:
                        self._sync_file(rel_path)
                        pbar.update(1)
                    except Exception as e:
                        logger.error(f"Error syncing {rel_path}: {e}")
                        self.stats["errors"] += 1
                        pbar.update(1)
            
            # Delete remote files if configured
            if self.config.delete_remote:
                self._delete_remote_files(files_to_sync)
            
            # Print statistics
            self._print_stats()
            
        finally:
            self.disconnect()
    
    def _get_local_files(self) -> List[str]:
        """
        Get list of all files in local directory
        
        Returns:
            List of relative file paths
        """
        files = []
        local_path = Path(self.config.local_dir)
        
        for root, dirs, filenames in os.walk(local_path, followlinks=self.config.follow_symlinks):
            # Filter out excluded directories to avoid walking them
            dirs[:] = [d for d in dirs if self.file_filter.should_include(
                os.path.relpath(os.path.join(root, d), local_path).replace(os.sep, "/")
            )]
            
            for filename in filenames:
                file_path = os.path.join(root, filename)
                rel_path = os.path.relpath(file_path, local_path)
                files.append(rel_path.replace(os.sep, "/"))
        
        return files
    
    def _sync_file(self, rel_path: str):
        """
        Sync a single file
        
        Args:
            rel_path: Relative path of the file
        """
        local_path = os.path.join(self.config.local_dir, rel_path)
        remote_path = self._get_remote_path(rel_path)
        
        # Check if file needs to be uploaded
        needs_upload = True
        
        try:
            remote_stat = self.sftp_client.stat(remote_path)
            local_stat = os.stat(local_path)
            
            # Compare modification times and sizes
            if (remote_stat.st_mtime >= local_stat.st_mtime and 
                remote_stat.st_size == local_stat.st_size):
                needs_upload = False
                if self.config.verbose:
                    logger.info(f"Skipping (up to date): {rel_path}")
                self.stats["skipped"] += 1
        except FileNotFoundError:
            # Remote file doesn't exist, needs upload
            pass
        
        if needs_upload:
            if self.config.backup_remote:
                self._backup_remote_file(remote_path)
            
            if not self.config.dry_run:
                # Ensure remote directory exists
                remote_dir = os.path.dirname(remote_path)
                self._ensure_remote_dir(remote_dir)
                
                # Upload file
                self.sftp_client.put(local_path, remote_path)
                
                # Preserve permissions
                if self.config.preserve_permissions:
                    local_mode = os.stat(local_path).st_mode
                    self.sftp_client.chmod(remote_path, stat.S_IMODE(local_mode))
                
                logger.info(f"Uploaded: {rel_path}")
            else:
                logger.info(f"[DRY RUN] Would upload: {rel_path}")
            
            self.stats["uploaded"] += 1
    
    def _ensure_remote_dir(self, remote_path: str):
        """
        Ensure remote directory exists
        
        Args:
            remote_path: Remote directory path
        """
        if not remote_path or remote_path == ".":
            return
        
        try:
            self.sftp_client.stat(remote_path)
        except FileNotFoundError:
            # Directory doesn't exist, create it
            parent_dir = os.path.dirname(remote_path)
            if parent_dir:
                self._ensure_remote_dir(parent_dir)
            
            if not self.config.dry_run:
                self.sftp_client.mkdir(remote_path)
                logger.debug(f"Created remote directory: {remote_path}")
    
    def _get_remote_path(self, rel_path: str) -> str:
        """
        Get full remote path for a relative path
        
        Args:
            rel_path: Relative file path
            
        Returns:
            Full remote path
        """
        # Use forward slashes for remote paths (Unix-style)
        return os.path.join(self.config.remote_dir, rel_path).replace(os.sep, "/")
    
    def _backup_remote_file(self, remote_path: str):
        """
        Backup remote file before overwriting
        
        Args:
            remote_path: Remote file path
        """
        try:
            self.sftp_client.stat(remote_path)
            backup_path = f"{remote_path}.backup"
            
            if not self.config.dry_run:
                # Remove old backup if exists
                try:
                    self.sftp_client.remove(backup_path)
                except FileNotFoundError:
                    pass
                
                # Rename current file to backup
                self.sftp_client.rename(remote_path, backup_path)
                logger.debug(f"Backed up: {remote_path} -> {backup_path}")
        except FileNotFoundError:
            # File doesn't exist, no backup needed
            pass
    
    def _delete_remote_files(self, local_files: List[str]):
        """
        Delete remote files that don't exist locally
        
        Args:
            local_files: List of local file paths
        """
        logger.info("Checking for files to delete on remote...")
        
        try:
            remote_files = self._get_remote_files(self.config.remote_dir, "")
            local_files_set = set(local_files)
            
            files_to_delete = [f for f in remote_files if f not in local_files_set]
            
            if files_to_delete:
                logger.info(f"Deleting {len(files_to_delete)} remote files...")
                for rel_path in files_to_delete:
                    remote_path = self._get_remote_path(rel_path)
                    if not self.config.dry_run:
                        self.sftp_client.remove(remote_path)
                        logger.info(f"Deleted: {rel_path}")
                    else:
                        logger.info(f"[DRY RUN] Would delete: {rel_path}")
                    self.stats["deleted"] += 1
        except Exception as e:
            logger.error(f"Error during remote file deletion: {e}")
    
    def _get_remote_files(self, remote_dir: str, prefix: str) -> List[str]:
        """
        Recursively get list of remote files
        
        Args:
            remote_dir: Remote directory to scan
            prefix: Prefix for relative paths
            
        Returns:
            List of relative file paths
        """
        files = []
        
        try:
            for item in self.sftp_client.listdir_attr(remote_dir):
                item_path = os.path.join(remote_dir, item.filename)
                rel_path = os.path.join(prefix, item.filename) if prefix else item.filename
                
                if stat.S_ISDIR(item.st_mode):
                    # Recursively scan subdirectory
                    files.extend(self._get_remote_files(item_path, rel_path))
                else:
                    files.append(rel_path.replace(os.sep, "/"))
        except Exception as e:
            logger.error(f"Error listing remote directory {remote_dir}: {e}")
        
        return files
    
    def _print_stats(self):
        """Print synchronization statistics"""
        logger.info("=" * 50)
        logger.info("Synchronization completed")
        logger.info(f"  Uploaded: {self.stats['uploaded']}")
        logger.info(f"  Skipped: {self.stats['skipped']}")
        logger.info(f"  Deleted: {self.stats['deleted']}")
        logger.info(f"  Errors: {self.stats['errors']}")
        logger.info("=" * 50)
