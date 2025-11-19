#!/usr/bin/env python3
"""
Fix autoplay issues in all video player templates.
Browsers block autoplay with sound - we need to either:
1. Start muted and show unmute button
2. Add click-to-play overlay
"""

import re
from pathlib import Path

def fix_autoplay_in_template(template_path, template_name):
    """Fix autoplay issues in a template file"""
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    changes_made = False
    
    # Fix 1: Ensure videos start muted for autoplay to work
    if '<video' in content and 'muted' not in content[:content.find('</video>')]:
        # Add muted attribute to video tags
        content = re.sub(
            r'(<video[^>]*)(autoplay)([^>]*>)',
            r'\1autoplay muted\3',
            content
        )
        changes_made = True
        print(f"  ✓ Added muted attribute to {template_name}")
    
    # Fix 2: Add proper play() error handling
    if '.play()' in content and '.play().catch' not in content:
        # Replace bare .play() with error handling
        content = re.sub(
            r'(\w+)\.play\(\);',
            r'''\1.play().catch(e => {
                console.log('Autoplay blocked, waiting for user interaction');
                // Show play button or instructions
            });''',
            content
        )
        changes_made = True
        print(f"  ✓ Added play() error handling to {template_name}")
    
    # Fix 3: Add click-to-play overlay for templates without it
    if template_name in ['nexus_tv_template.html', 'stream_hub_template.html', 'buffer_tv_template.html']:
        if 'click-to-play' not in content and 'playOverlay' not in content:
            # Add click-to-play overlay CSS
            overlay_css = """
    /* Click to Play Overlay */
    .play-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
        display: flex;
        justify-content: center;
        align-items: center;
        cursor: pointer;
        z-index: 1000;
        transition: opacity 0.3s;
    }
    
    .play-overlay.hidden {
        opacity: 0;
        pointer-events: none;
    }
    
    .play-button {
        width: 80px;
        height: 80px;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        transition: transform 0.3s;
    }
    
    .play-button:hover {
        transform: scale(1.1);
    }
    
    .play-button::after {
        content: '▶';
        font-size: 36px;
        color: #333;
        margin-left: 5px;
    }
"""
            
            # Add overlay HTML
            overlay_html = """
    <!-- Click to Play Overlay -->
    <div id="playOverlay" class="play-overlay">
        <div class="play-button"></div>
    </div>"""
            
            # Add overlay JavaScript
            overlay_js = """
        // Handle click-to-play for autoplay restrictions
        const playOverlay = document.getElementById('playOverlay');
        const videoElement = document.getElementById('main-video') || document.querySelector('video');
        
        if (playOverlay && videoElement) {
            // Try autoplay first
            videoElement.muted = true; // Start muted for autoplay to work
            videoElement.play().then(() => {
                // Autoplay worked, hide overlay
                playOverlay.classList.add('hidden');
            }).catch(() => {
                // Autoplay blocked, show overlay
                playOverlay.classList.remove('hidden');
            });
            
            // Handle click to play
            playOverlay.addEventListener('click', () => {
                videoElement.muted = false; // Unmute on user interaction
                videoElement.play().then(() => {
                    playOverlay.classList.add('hidden');
                }).catch(e => {
                    console.error('Playback failed:', e);
                });
            });
        }
"""
            
            # Insert CSS before closing style tag
            if '</style>' in content:
                content = content.replace('</style>', overlay_css + '\n</style>')
                changes_made = True
                print(f"  ✓ Added click-to-play CSS to {template_name}")
            
            # Insert HTML after video element
            if '<video' in content:
                video_end = content.find('</video>') + 8
                content = content[:video_end] + '\n' + overlay_html + content[video_end:]
                changes_made = True
                print(f"  ✓ Added click-to-play overlay HTML to {template_name}")
            
            # Insert JavaScript before closing script tag
            last_script_close = content.rfind('</script>')
            if last_script_close > 0:
                content = content[:last_script_close] + '\n' + overlay_js + '\n' + content[last_script_close:]
                changes_made = True
                print(f"  ✓ Added click-to-play JavaScript to {template_name}")
    
    if changes_made:
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def main():
    print("🔧 Fixing autoplay issues in video player templates...")
    print("=" * 50)
    
    templates_to_fix = [
        'templates/nexus_tv_template.html',
        'templates/stream_hub_template.html',
        'templates/buffer_tv_template.html',
        'templates/multi_channel_template.html',
        'templates/simple-player/index.html',
        'templates/web-iptv-extension/index.html'
    ]
    
    fixed_count = 0
    
    for template_path_str in templates_to_fix:
        template_path = Path(template_path_str)
        if template_path.exists():
            print(f"\n📄 Processing {template_path.name}...")
            if fix_autoplay_in_template(template_path, template_path.name):
                fixed_count += 1
                print(f"  ✅ Fixed autoplay issues")
            else:
                print(f"  ℹ️ Already properly configured")
        else:
            print(f"\n⚠️ Template not found: {template_path_str}")
    
    print("\n" + "=" * 50)
    print(f"✅ AUTOPLAY FIX COMPLETE!")
    print(f"📊 Fixed {fixed_count} templates")
    print("\n🎯 Solutions implemented:")
    print("  1. Videos start muted (allows autoplay)")
    print("  2. Click-to-play overlay for user interaction")
    print("  3. Proper error handling for play() promises")
    print("\n💡 Users will see a play button if autoplay is blocked")

if __name__ == "__main__":
    main()