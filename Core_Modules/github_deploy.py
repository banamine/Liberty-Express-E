#!/usr/bin/env python3
"""
GitHub Auto-Deploy Module
Pushes generated pages to Liberty-Express- "Ready Made" folder
"""

import subprocess
import json
import os
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class GitHubDeploy:
    """Handles automated deployment to GitHub"""
    
    def __init__(self, repo_path=None):
        """
        Initialize GitHub deploy handler
        
        Args:
            repo_path: Path to local git repository (default from Environment)
        """
        if repo_path is None:
            # Default Windows path
            repo_path = Path(r"C:\Users\banamine\Documents\GitHub\Liberty-Express-")
        
        self.repo_path = Path(repo_path)
        self.ready_made_path = self.repo_path / "Ready Made"
        self.branch = "main"
        
    def is_repo_ready(self):
        """Check if repo path exists and is a git repository"""
        if not self.repo_path.exists():
            logger.warning(f"Repository path not found: {self.repo_path}")
            return False
        
        git_dir = self.repo_path / ".git"
        if not git_dir.exists():
            logger.warning(f"Not a git repository: {self.repo_path}")
            return False
        
        return True
    
    def ensure_ready_made_folder(self):
        """Ensure Ready Made folder exists"""
        try:
            self.ready_made_path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Failed to create Ready Made folder: {e}")
            return False
    
    def copy_pages(self, source_dir, subfolder_name=None):
        """
        Copy generated pages to Ready Made folder
        
        Args:
            source_dir: Source directory with generated pages
            subfolder_name: Optional subfolder (e.g., "nexus_tv")
        
        Returns:
            List of copied files
        """
        import shutil
        
        source_path = Path(source_dir)
        if not source_path.exists():
            logger.error(f"Source directory not found: {source_dir}")
            return []
        
        copied_files = []
        
        try:
            # Determine target path
            if subfolder_name:
                target_path = self.ready_made_path / subfolder_name
            else:
                target_path = self.ready_made_path
            
            target_path.mkdir(parents=True, exist_ok=True)
            
            # Copy all HTML files
            for html_file in source_path.glob("*.html"):
                try:
                    dest = target_path / html_file.name
                    shutil.copy2(html_file, dest)
                    copied_files.append(str(dest))
                    logger.info(f"Copied: {html_file.name} → {dest}")
                except Exception as e:
                    logger.error(f"Failed to copy {html_file.name}: {e}")
            
            # Copy subdirectories (e.g., nexus_tv/)
            for subdir in source_path.iterdir():
                if subdir.is_dir() and not subdir.name.startswith('.'):
                    target_subdir = target_path / subdir.name
                    target_subdir.mkdir(parents=True, exist_ok=True)
                    
                    for file in subdir.rglob("*"):
                        if file.is_file():
                            rel_path = file.relative_to(subdir)
                            dest = target_subdir / rel_path
                            dest.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(file, dest)
                            copied_files.append(str(dest))
                            logger.info(f"Copied: {file.name} → {dest}")
        
        except Exception as e:
            logger.error(f"Error copying pages: {e}")
        
        return copied_files
    
    def git_add(self, file_path=None):
        """
        Git add files
        
        Args:
            file_path: Specific file to add (default: all in Ready Made)
        """
        try:
            os.chdir(self.repo_path)
            
            if file_path:
                cmd = ["git", "add", file_path]
            else:
                cmd = ["git", "add", "Ready Made/"]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                logger.error(f"Git add failed: {result.stderr}")
                return False
            
            logger.info("Files staged for commit")
            return True
        
        except Exception as e:
            logger.error(f"Git add error: {e}")
            return False
    
    def git_commit(self, message=None):
        """
        Git commit changes
        
        Args:
            message: Commit message (default: auto-generated)
        """
        try:
            os.chdir(self.repo_path)
            
            if message is None:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                message = f"feat: Auto-deploy generated pages ({timestamp})"
            
            cmd = ["git", "commit", "-m", message]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                # Check if there's nothing to commit
                if "nothing to commit" in result.stderr:
                    logger.info("No changes to commit")
                    return True
                
                logger.error(f"Git commit failed: {result.stderr}")
                return False
            
            logger.info(f"Committed: {message}")
            return True
        
        except Exception as e:
            logger.error(f"Git commit error: {e}")
            return False
    
    def git_push(self, branch=None):
        """
        Git push to remote
        
        Args:
            branch: Branch to push (default: main)
        """
        try:
            os.chdir(self.repo_path)
            
            if branch is None:
                branch = self.branch
            
            cmd = ["git", "push", "origin", branch]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                logger.error(f"Git push failed: {result.stderr}")
                return False
            
            logger.info(f"Pushed to {branch}")
            return True
        
        except Exception as e:
            logger.error(f"Git push error: {e}")
            return False
    
    def deploy(self, source_dir, subfolder_name=None, commit_message=None, auto_push=True):
        """
        Full deployment workflow
        
        Args:
            source_dir: Source directory with generated pages
            subfolder_name: Optional subfolder (e.g., "nexus_tv")
            commit_message: Custom commit message
            auto_push: Whether to push to remote
        
        Returns:
            Dictionary with deployment result
        """
        result = {
            'success': False,
            'copied_files': [],
            'commit_hash': None,
            'error': None
        }
        
        try:
            # Check prerequisites
            if not self.is_repo_ready():
                result['error'] = "Repository not ready"
                return result
            
            # Create Ready Made folder
            if not self.ensure_ready_made_folder():
                result['error'] = "Failed to create Ready Made folder"
                return result
            
            # Copy files
            copied = self.copy_pages(source_dir, subfolder_name)
            if not copied:
                result['error'] = "No files copied"
                return result
            
            result['copied_files'] = copied
            
            # Git operations
            if not self.git_add():
                result['error'] = "Failed to stage files"
                return result
            
            if not self.git_commit(commit_message):
                result['error'] = "Failed to commit"
                return result
            
            # Push if requested
            if auto_push:
                if not self.git_push():
                    result['error'] = "Failed to push"
                    return result
            
            result['success'] = True
            logger.info(f"✅ Deployment complete: {len(copied)} files")
        
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Deployment failed: {e}")
        
        return result


def deploy_generated_pages(source_dir, repo_path=None, subfolder_name=None):
    """
    Convenience function for deploying generated pages
    
    Args:
        source_dir: Source directory with generated pages
        repo_path: Path to Liberty-Express- repository
        subfolder_name: Optional subfolder name
    
    Returns:
        Deployment result dictionary
    """
    deployer = GitHubDeploy(repo_path)
    return deployer.deploy(source_dir, subfolder_name=subfolder_name)


if __name__ == "__main__":
    # Test deployment
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    deployer = GitHubDeploy()
    
    print("Testing GitHub deployment...")
    print(f"Repo path: {deployer.repo_path}")
    print(f"Ready Made path: {deployer.ready_made_path}")
    print(f"Repo ready: {deployer.is_repo_ready()}")
