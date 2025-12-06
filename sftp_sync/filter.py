"""
File filtering module for pattern-based include/exclude
"""

import os
import fnmatch
from typing import List


class FileFilter:
    """File filter using glob-style patterns"""
    
    def __init__(self, include_patterns: List[str] = None, exclude_patterns: List[str] = None):
        """
        Initialize file filter
        
        Args:
            include_patterns: List of patterns to include (e.g., ['*.py', '*.txt'])
            exclude_patterns: List of patterns to exclude (e.g., ['*.pyc', '__pycache__'])
        """
        self.include_patterns = include_patterns or ["*"]
        self.exclude_patterns = exclude_patterns or []
        
    def should_include(self, path: str) -> bool:
        """
        Check if a file should be included based on patterns
        
        Args:
            path: Relative file path to check
            
        Returns:
            True if file should be included, False otherwise
        """
        # Normalize path separators
        path = path.replace(os.sep, "/")
        
        # Check exclude patterns first (they take precedence)
        for pattern in self.exclude_patterns:
            if self._match_pattern(path, pattern):
                return False
        
        # Check include patterns
        for pattern in self.include_patterns:
            if self._match_pattern(path, pattern):
                return True
        
        # If include patterns are specified but none matched, exclude
        if self.include_patterns and self.include_patterns != ["*"]:
            return False
            
        return True
    
    def _match_pattern(self, path: str, pattern: str) -> bool:
        """
        Match a path against a pattern
        
        Args:
            path: File path to match
            pattern: Pattern to match against
            
        Returns:
            True if pattern matches, False otherwise
        """
        # Normalize pattern
        pattern = pattern.replace(os.sep, "/")
        
        # Direct match
        if fnmatch.fnmatch(path, pattern):
            return True
        
        # Match any part of the path (for directory patterns)
        path_parts = path.split("/")
        for i in range(len(path_parts)):
            sub_path = "/".join(path_parts[i:])
            if fnmatch.fnmatch(sub_path, pattern):
                return True
            
        # Check if any parent directory matches the pattern
        for i in range(len(path_parts)):
            dir_path = "/".join(path_parts[:i+1])
            if fnmatch.fnmatch(dir_path, pattern):
                return True
                
        return False
    
    def filter_files(self, files: List[str]) -> List[str]:
        """
        Filter a list of files based on patterns
        
        Args:
            files: List of file paths
            
        Returns:
            Filtered list of file paths
        """
        return [f for f in files if self.should_include(f)]
