#!/usr/bin/env python3
"""
FIXED Page Generator Module
Correctly handles paths when running as PyInstaller executable
"""

import sys
import os
from pathlib import Path

def get_application_path():
    """
    Get the correct application path whether running as script or PyInstaller executable
    
    When running as PyInstaller executable:
    - sys._MEIPASS contains the temporary extraction path
    - sys.argv[0] or __file__ points to the executable location
    
    When running as script:
    - Use the normal file path
    """
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller executable
        # Get the directory where the executable is located
        if hasattr(sys, '_MEIPASS'):
            # For onefile builds, we want the exe's directory, not the temp extraction
            exe_dir = Path(sys.executable).parent
        else:
            # For onedir builds
            exe_dir = Path(sys.argv[0]).parent
        
        # Create generated_pages next to the executable
        base_path = exe_dir
    else:
        # Running as Python script (development mode)
        # Use project root
        base_path = Path(__file__).resolve().parent.parent
    
    return base_path

def get_output_directory(subfolder=""):
    """
    Get the correct output directory for generated pages
    
    Args:
        subfolder: Optional subfolder within generated_pages (e.g., "nexus_tv")
    
    Returns:
        Path object pointing to the correct output directory
    """
    base = get_application_path()
    output_dir = base / "generated_pages"
    
    if subfolder:
        output_dir = output_dir / subfolder
    
    # Create directory if it doesn't exist
    output_dir.mkdir(exist_ok=True, parents=True)
    
    return output_dir

def get_template_path(template_name):
    """
    Get the correct template path whether running as script or executable
    
    Args:
        template_name: Name of the template file/folder
    
    Returns:
        Path object pointing to the template
    """
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller executable
        # Templates are bundled in the executable
        if hasattr(sys, '_MEIPASS'):
            # For onefile builds, templates are extracted to temp dir
            template_base = Path(sys._MEIPASS) / "templates"
        else:
            # For onedir builds, templates are in the dist folder
            template_base = Path(sys.argv[0]).parent / "templates"
    else:
        # Running as Python script
        template_base = Path(__file__).resolve().parent.parent / "templates"
    
    return template_base / template_name

# Monkey-patch the original page_generator module to fix paths
def fix_page_generator_paths():
    """
    Patches the page_generator module to use correct paths
    This should be called before importing the generators
    """
    import sys
    import importlib.util
    from pathlib import Path
    
    # Get the original page_generator module path
    pg_path = Path(__file__).resolve().parent / "page_generator.py"
    
    if pg_path.exists():
        # Load the module
        spec = importlib.util.spec_from_file_location("page_generator", pg_path)
        if spec and spec.loader:
            page_generator = importlib.util.module_from_spec(spec)
            
            # Inject our path helpers before executing
            page_generator.get_output_directory = get_output_directory
            page_generator.get_template_path = get_template_path
            page_generator.get_application_path = get_application_path
            
            # Execute the module
            spec.loader.exec_module(page_generator)
            
            # Replace in sys.modules
            sys.modules['page_generator'] = page_generator
            
            # Fix all generator classes
            if hasattr(page_generator, 'NexusTVPageGenerator'):
                _fix_nexus_tv_generator(page_generator.NexusTVPageGenerator)
            if hasattr(page_generator, 'WebIPTVGenerator'):
                _fix_web_iptv_generator(page_generator.WebIPTVGenerator)
            if hasattr(page_generator, 'SimplePlayerGenerator'):
                _fix_simple_player_generator(page_generator.SimplePlayerGenerator)
            if hasattr(page_generator, 'RumbleChannelGenerator'):
                _fix_rumble_generator(page_generator.RumbleChannelGenerator)
            if hasattr(page_generator, 'MultiChannelGenerator'):
                _fix_multi_channel_generator(page_generator.MultiChannelGenerator)
            if hasattr(page_generator, 'BufferTVGenerator'):
                _fix_buffer_tv_generator(page_generator.BufferTVGenerator)
            
            return page_generator
    
    return None

def _fix_nexus_tv_generator(cls):
    """Fix NexusTVPageGenerator to use correct paths"""
    original_init = cls.__init__
    
    def fixed_init(self, template_path=None):
        if template_path is None:
            template_path = get_template_path("nexus_tv_template.html")
        self.template_path = Path(template_path)
        self.output_dir = get_output_directory("nexus_tv")
        self.ffprobe_available = False  # Disable for packaged exe
    
    cls.__init__ = fixed_init

def _fix_web_iptv_generator(cls):
    """Fix WebIPTVGenerator to use correct paths"""
    original_init = cls.__init__
    
    def fixed_init(self, template_path=None):
        if template_path is None:
            template_path = get_template_path("web-iptv-extension")
        self.template_dir = Path(template_path)
        self.output_dir = get_output_directory("web_iptv")
    
    cls.__init__ = fixed_init

def _fix_simple_player_generator(cls):
    """Fix SimplePlayerGenerator to use correct paths"""
    original_init = cls.__init__
    
    def fixed_init(self, template_path=None):
        if template_path is None:
            template_path = get_template_path("simple-player")
        self.template_dir = Path(template_path)
        self.output_dir = get_output_directory("simple_player")
    
    cls.__init__ = fixed_init

def _fix_rumble_generator(cls):
    """Fix RumbleChannelGenerator to use correct paths"""
    original_init = cls.__init__
    
    def fixed_init(self, template_path=None):
        if template_path is None:
            template_path = get_template_path("rumble_channel_template.html")
        self.template_path = Path(template_path)
        self.output_dir = get_output_directory("rumble_channel")
        # Keep RumbleHelper initialization if it exists
        try:
            from rumble_helper import RumbleHelper
            self.rumble_helper = RumbleHelper()
        except ImportError:
            self.rumble_helper = None
    
    cls.__init__ = fixed_init

def _fix_multi_channel_generator(cls):
    """Fix MultiChannelGenerator to use correct paths"""
    original_init = cls.__init__
    
    def fixed_init(self, template_path=None):
        if template_path is None:
            template_path = get_template_path("multi_channel_template.html")
        self.template_path = Path(template_path)
        self.output_dir = get_output_directory("multi_channel")
    
    cls.__init__ = fixed_init

def _fix_buffer_tv_generator(cls):
    """Fix BufferTVGenerator to use correct paths"""
    original_init = cls.__init__
    
    def fixed_init(self, template_path=None):
        if template_path is None:
            template_path = get_template_path("buffer_tv_template.html")
        self.template_path = Path(template_path)
        self.output_dir = get_output_directory("buffer_tv")
    
    cls.__init__ = fixed_init

# Export the fix function
__all__ = ['fix_page_generator_paths', 'get_output_directory', 'get_template_path', 'get_application_path']