#!/usr/bin/env python3
"""
Tests for review tools
"""

import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock

from openssl_tools.review_tools import AddRevTool, GitAddRevTool, GhMergeTool


class TestAddRevTool(unittest.TestCase):
    """Test AddRevTool"""
    
    def setUp(self):
        self.tool = AddRevTool()
    
    def test_parse_arguments(self):
        """Test argument parsing"""
        args = self.tool.parse_arguments(['--prnum=1234', 'steve', 'levitte'])
        self.assertEqual(args.prnum, 1234)
        self.assertEqual(args.reviewers, ['steve', 'levitte'])
    
    def test_parse_arguments_with_positional(self):
        """Test argument parsing with positional arguments"""
        args = self.tool.parse_arguments(['1234', 'steve', '@levitte'])
        self.assertEqual(args.prnum, 1234)
        self.assertEqual(args.positional, ['steve', '@levitte'])
    
    def test_get_my_email(self):
        """Test getting git email"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = 'test@example.com\n'
            
            email = self.tool.get_my_email()
            self.assertEqual(email, 'test@example.com')
    
    def test_determine_repository_type(self):
        """Test repository type determination"""
        args = MagicMock()
        args.web = True
        args.tools = False
        args.fuzz_corpora = False
        args.perftools = False
        args.installer = False
        
        repo_type = self.tool.determine_repository_type(args)
        self.assertEqual(repo_type, 'web')


class TestGitAddRevTool(unittest.TestCase):
    """Test GitAddRevTool"""
    
    def setUp(self):
        self.tool = GitAddRevTool()
    
    def test_parse_arguments(self):
        """Test argument parsing"""
        args = self.tool.parse_arguments(['--reviewer=steve', '--prnum=1234'])
        self.assertEqual(args.reviewer, ['steve'])
        self.assertEqual(args.prnum, 1234)
    
    def test_validate_reviewers(self):
        """Test reviewer validation"""
        # Test with valid reviewers
        self.tool.reviewers = [
            MagicMock(has_cla=True, is_author=False),
            MagicMock(has_cla=True, is_author=False)
        ]
        self.tool.unknown_reviewers = []
        self.tool.nocla_reviewers = []
        
        result = self.tool.validate_reviewers()
        self.assertTrue(result)
    
    def test_validate_reviewers_insufficient(self):
        """Test reviewer validation with insufficient reviewers"""
        self.tool.reviewers = []
        self.tool.unknown_reviewers = []
        self.tool.nocla_reviewers = []
        
        result = self.tool.validate_reviewers()
        self.assertFalse(result)


class TestGhMergeTool(unittest.TestCase):
    """Test GhMergeTool"""
    
    def setUp(self):
        self.tool = GhMergeTool()
    
    def test_parse_arguments(self):
        """Test argument parsing"""
        args = self.tool.parse_arguments(['1234', 'steve', 'levitte'])
        self.assertEqual(args.prnum, 1234)
        self.assertEqual(args.reviewers, ['steve', 'levitte'])
    
    def test_get_repository_name(self):
        """Test repository name determination"""
        args = MagicMock()
        args.web = False
        args.tools = False
        
        repo_name = self.tool.get_repository_name(args)
        self.assertEqual(repo_name, 'openssl/openssl')
    
    def test_get_repository_name_tools(self):
        """Test repository name determination for tools"""
        args = MagicMock()
        args.web = False
        args.tools = True
        
        repo_name = self.tool.get_repository_name(args)
        self.assertEqual(repo_name, 'openssl/tools')


if __name__ == '__main__':
    unittest.main()