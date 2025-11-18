"""
Dependency Checker for M3U Matrix
Auto-detects required dependencies and provides installation guidance
"""

import sys
import subprocess
import shutil
import platform
from pathlib import Path
from typing import Dict, List, Tuple

class DependencyStatus:
    """Represents the status of a single dependency"""
    def __init__(self, name: str, installed: bool, version: str = None, 
                 install_url: str = None, notes: str = None):
        self.name = name
        self.installed = installed
        self.version = version
        self.install_url = install_url
        self.notes = notes
    
    def __repr__(self):
        status = "✅" if self.installed else "❌"
        version_str = f" ({self.version})" if self.version else ""
        return f"{status} {self.name}{version_str}"


class DependencyChecker:
    """Comprehensive dependency checker for M3U Matrix"""
    
    def __init__(self):
        self.os_type = platform.system()  # Windows, Linux, Darwin (macOS)
        self.results = {}
    
    def check_python_version(self) -> DependencyStatus:
        """Check if Python version is 3.11+"""
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"
        meets_requirement = version >= (3, 11)
        
        return DependencyStatus(
            name="Python",
            installed=meets_requirement,
            version=version_str,
            install_url="https://www.python.org/downloads/" if not meets_requirement else None,
            notes="Python 3.11+ required" if not meets_requirement else "Version OK"
        )
    
    def check_python_package(self, package_name: str, import_name: str = None) -> DependencyStatus:
        """Check if a Python package is installed"""
        if import_name is None:
            import_name = package_name
        
        try:
            if import_name == "tkinterdnd2":
                from tkinterdnd2 import TkinterDnD
                version = "installed"
            elif import_name == "requests":
                import requests
                version = requests.__version__
            elif import_name == "PIL":
                from PIL import Image
                import PIL
                version = PIL.__version__
            elif import_name == "vlc":
                import vlc
                version = vlc.__version__ if hasattr(vlc, '__version__') else "installed"
            else:
                __import__(import_name)
                version = "installed"
            
            return DependencyStatus(
                name=package_name,
                installed=True,
                version=version,
                notes="Installed via pip"
            )
        except ImportError:
            install_cmd = f"pip install {package_name}"
            return DependencyStatus(
                name=package_name,
                installed=False,
                install_url=install_cmd,
                notes=f"Run: {install_cmd}"
            )
    
    def check_ffmpeg(self) -> Tuple[DependencyStatus, DependencyStatus]:
        """Check for FFmpeg and ffprobe"""
        ffmpeg_path = shutil.which("ffmpeg")
        ffprobe_path = shutil.which("ffprobe")
        
        ffmpeg_version = None
        ffprobe_version = None
        
        if ffmpeg_path:
            try:
                result = subprocess.run(
                    ['ffmpeg', '-version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    # Extract version from first line
                    first_line = result.stdout.split('\n')[0]
                    version_match = first_line.split('version')[1].split()[0] if 'version' in first_line else "found"
                    ffmpeg_version = version_match
            except:
                pass
        
        if ffprobe_path:
            try:
                result = subprocess.run(
                    ['ffprobe', '-version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    first_line = result.stdout.split('\n')[0]
                    version_match = first_line.split('version')[1].split()[0] if 'version' in first_line else "found"
                    ffprobe_version = version_match
            except:
                pass
        
        # Installation URLs based on OS
        if self.os_type == "Windows":
            install_url = "https://www.gyan.dev/ffmpeg/builds/ (download full build)"
        elif self.os_type == "Darwin":
            install_url = "brew install ffmpeg"
        else:  # Linux
            install_url = "sudo apt install ffmpeg (Ubuntu/Debian) or sudo dnf install ffmpeg (Fedora)"
        
        ffmpeg_status = DependencyStatus(
            name="FFmpeg",
            installed=ffmpeg_path is not None,
            version=ffmpeg_version,
            install_url=install_url if not ffmpeg_path else None,
            notes="Used for video metadata extraction" if not ffmpeg_path else f"Found at: {ffmpeg_path}"
        )
        
        ffprobe_status = DependencyStatus(
            name="ffprobe",
            installed=ffprobe_path is not None,
            version=ffprobe_version,
            install_url=install_url if not ffprobe_path else None,
            notes="Comes with FFmpeg" if not ffprobe_path else f"Found at: {ffprobe_path}"
        )
        
        return ffmpeg_status, ffprobe_status
    
    def check_vlc(self) -> DependencyStatus:
        """Check for VLC Media Player"""
        vlc_path = shutil.which("vlc")
        
        if not vlc_path and self.os_type == "Windows":
            # Check common Windows installation paths
            common_paths = [
                r"C:\Program Files\VideoLAN\VLC\vlc.exe",
                r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
            ]
            for path in common_paths:
                if Path(path).exists():
                    vlc_path = path
                    break
        
        # Installation URLs based on OS
        if self.os_type == "Windows":
            install_url = "https://www.videolan.org/vlc/download-windows.html"
        elif self.os_type == "Darwin":
            install_url = "https://www.videolan.org/vlc/download-macosx.html or brew install --cask vlc"
        else:  # Linux
            install_url = "sudo apt install vlc (Ubuntu/Debian) or sudo dnf install vlc (Fedora)"
        
        return DependencyStatus(
            name="VLC Media Player",
            installed=vlc_path is not None,
            version="found" if vlc_path else None,
            install_url=install_url if not vlc_path else None,
            notes="Required for embedded video playback" if not vlc_path else f"Found at: {vlc_path}"
        )
    
    def run_full_check(self) -> Dict[str, DependencyStatus]:
        """Run comprehensive dependency check"""
        results = {}
        
        # Check Python version
        results['python'] = self.check_python_version()
        
        # Check Python packages
        results['tkinterdnd2'] = self.check_python_package('tkinterdnd2')
        results['requests'] = self.check_python_package('requests')
        results['pillow'] = self.check_python_package('Pillow', 'PIL')
        results['python-vlc'] = self.check_python_package('python-vlc', 'vlc')
        
        # Check external binaries
        ffmpeg_status, ffprobe_status = self.check_ffmpeg()
        results['ffmpeg'] = ffmpeg_status
        results['ffprobe'] = ffprobe_status
        results['vlc'] = self.check_vlc()
        
        self.results = results
        return results
    
    def get_missing_dependencies(self) -> List[DependencyStatus]:
        """Get list of missing dependencies"""
        if not self.results:
            self.run_full_check()
        return [dep for dep in self.results.values() if not dep.installed]
    
    def get_critical_missing(self) -> List[DependencyStatus]:
        """Get critical missing dependencies (Python packages)"""
        critical = ['python', 'tkinterdnd2', 'requests', 'pillow']
        if not self.results:
            self.run_full_check()
        return [self.results[key] for key in critical if key in self.results and not self.results[key].installed]
    
    def get_optional_missing(self) -> List[DependencyStatus]:
        """Get optional missing dependencies (FFmpeg, VLC)"""
        optional = ['ffmpeg', 'ffprobe', 'vlc', 'python-vlc']
        if not self.results:
            self.run_full_check()
        return [self.results[key] for key in optional if key in self.results and not self.results[key].installed]
    
    def is_fully_functional(self) -> bool:
        """Check if all dependencies are installed"""
        if not self.results:
            self.run_full_check()
        return all(dep.installed for dep in self.results.values())
    
    def is_basic_functional(self) -> bool:
        """Check if critical dependencies are installed (app can run)"""
        critical = ['python', 'tkinterdnd2', 'requests']
        if not self.results:
            self.run_full_check()
        return all(self.results[key].installed for key in critical if key in self.results)
    
    def generate_report(self) -> str:
        """Generate detailed dependency report"""
        if not self.results:
            self.run_full_check()
        
        report = []
        report.append("=" * 70)
        report.append("M3U MATRIX DEPENDENCY CHECK REPORT")
        report.append("=" * 70)
        report.append(f"\nOS: {self.os_type} ({platform.platform()})")
        report.append(f"\n{'Dependency':<20} {'Status':<10} {'Version':<15} {'Notes'}")
        report.append("-" * 70)
        
        for name, dep in self.results.items():
            status = "✅ OK" if dep.installed else "❌ MISSING"
            version = dep.version or "-"
            notes = dep.notes or ""
            report.append(f"{dep.name:<20} {status:<10} {version:<15} {notes}")
        
        report.append("-" * 70)
        
        missing = self.get_missing_dependencies()
        if missing:
            report.append(f"\n⚠️  MISSING DEPENDENCIES: {len(missing)}")
            report.append("\nINSTALLATION INSTRUCTIONS:")
            report.append("-" * 70)
            for dep in missing:
                report.append(f"\n{dep.name}:")
                if dep.install_url:
                    report.append(f"  → {dep.install_url}")
                if dep.notes:
                    report.append(f"  ℹ️  {dep.notes}")
        else:
            report.append("\n✅ ALL DEPENDENCIES INSTALLED!")
        
        report.append("\n" + "=" * 70)
        
        # Feature availability
        report.append("\nFEATURE AVAILABILITY:")
        report.append("-" * 70)
        report.append(f"Core Functionality:    {'✅ Available' if self.is_basic_functional() else '❌ Unavailable'}")
        report.append(f"Full Functionality:    {'✅ Available' if self.is_fully_functional() else '⚠️  Limited'}")
        report.append(f"Video Metadata:        {'✅ Available' if self.results.get('ffmpeg', DependencyStatus('', False)).installed else '❌ Unavailable (FFmpeg missing)'}")
        report.append(f"Embedded Playback:     {'✅ Available' if self.results.get('python-vlc', DependencyStatus('', False)).installed else '❌ Unavailable (python-vlc missing)'}")
        report.append(f"Thumbnail Caching:     {'✅ Available' if self.results.get('pillow', DependencyStatus('', False)).installed else '❌ Unavailable (Pillow missing)'}")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def save_report(self, filename: str = "dependency_report.txt"):
        """Save dependency report to file"""
        report = self.generate_report()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        return filename


# Convenience function
def quick_check() -> bool:
    """Quick check if app can run (returns True if basic dependencies met)"""
    checker = DependencyChecker()
    checker.run_full_check()
    return checker.is_basic_functional()


def print_report():
    """Print dependency report to console"""
    checker = DependencyChecker()
    checker.run_full_check()
    print(checker.generate_report())


if __name__ == "__main__":
    print_report()
