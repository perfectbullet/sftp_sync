"""
SFTP Sync - 同步本地代码到远程服务器
A tool for synchronizing local code to remote servers via SFTP
"""

__version__ = "1.0.0"
__author__ = "perfectbullet"

from .syncer import SFTPSyncer
from .config import Config

__all__ = ["SFTPSyncer", "Config"]
