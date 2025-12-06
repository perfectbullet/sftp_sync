"""
Unit tests for file filter module
"""

import unittest
from sftp_sync.filter import FileFilter


class TestFileFilter(unittest.TestCase):
    """Test cases for FileFilter class"""
    
    def test_include_all_by_default(self):
        """Test that all files are included by default"""
        filter = FileFilter()
        self.assertTrue(filter.should_include("test.py"))
        self.assertTrue(filter.should_include("src/main.py"))
        self.assertTrue(filter.should_include("data.txt"))
    
    def test_exclude_patterns(self):
        """Test exclude patterns"""
        filter = FileFilter(exclude_patterns=["*.pyc", "__pycache__"])
        self.assertTrue(filter.should_include("test.py"))
        self.assertFalse(filter.should_include("test.pyc"))
        self.assertFalse(filter.should_include("src/__pycache__"))
        self.assertFalse(filter.should_include("__pycache__/test.pyc"))
    
    def test_include_patterns(self):
        """Test include patterns"""
        filter = FileFilter(include_patterns=["*.py", "*.txt"])
        self.assertTrue(filter.should_include("test.py"))
        self.assertTrue(filter.should_include("data.txt"))
        self.assertFalse(filter.should_include("image.png"))
    
    def test_exclude_takes_precedence(self):
        """Test that exclude patterns take precedence over include"""
        filter = FileFilter(
            include_patterns=["*.py"],
            exclude_patterns=["test_*.py"]
        )
        self.assertTrue(filter.should_include("main.py"))
        self.assertFalse(filter.should_include("test_main.py"))
    
    def test_directory_patterns(self):
        """Test directory pattern matching"""
        filter = FileFilter(exclude_patterns=[".git", "node_modules"])
        self.assertTrue(filter.should_include("src/main.py"))
        self.assertFalse(filter.should_include(".git/config"))
        self.assertFalse(filter.should_include("node_modules/package/index.js"))
    
    def test_wildcard_patterns(self):
        """Test wildcard patterns"""
        filter = FileFilter(exclude_patterns=["*.log", "temp*"])
        self.assertTrue(filter.should_include("main.py"))
        self.assertFalse(filter.should_include("app.log"))
        self.assertFalse(filter.should_include("temp.txt"))
        self.assertFalse(filter.should_include("tempfile.dat"))
    
    def test_filter_files_list(self):
        """Test filtering a list of files"""
        filter = FileFilter(
            include_patterns=["*.py"],
            exclude_patterns=["test_*.py"]
        )
        files = [
            "main.py",
            "test_main.py",
            "utils.py",
            "test_utils.py",
            "data.txt"
        ]
        filtered = filter.filter_files(files)
        self.assertEqual(set(filtered), {"main.py", "utils.py"})


if __name__ == "__main__":
    unittest.main()
