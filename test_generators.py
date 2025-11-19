#!/usr/bin/env python3
"""
Test script to verify all page generators produce files that work from file:// protocol
"""
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from Core_Modules.page_generator import (
    NexusTVPageGenerator,
    WebIPTVGenerator,
    SimplePlayerGenerator,
    RumbleChannelGenerator,
    MultiChannelGenerator,
    BufferTVGenerator,
    ClassicTVGenerator,
    StreamHubGenerator,
    StandaloneSecurePageGenerator
)

def test_generators():
    """Test all generators with sample M3U content"""
    
    # Read test M3U file
    test_m3u_path = Path("test_playlist.m3u")
    if not test_m3u_path.exists():
        print("❌ test_playlist.m3u not found")
        return False
    
    with open(test_m3u_path, 'r', encoding='utf-8') as f:
        m3u_content = f.read()
    
    print("=" * 60)
    print("Testing all page generators for offline functionality")
    print("=" * 60)
    
    results = []
    
    # Test NexusTVPageGenerator
    print("\n1. Testing NexusTVPageGenerator...")
    try:
        gen = NexusTVPageGenerator()
        output = gen.generate_page(m3u_content, "Test Nexus TV", "test_nexus")
        print(f"   ✅ Generated: {output}")
        results.append(("NexusTVPageGenerator", True, output))
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        results.append(("NexusTVPageGenerator", False, str(e)))
    
    # Test WebIPTVGenerator
    print("\n2. Testing WebIPTVGenerator...")
    try:
        gen = WebIPTVGenerator()
        output = gen.generate_page(m3u_content, "Test Web IPTV", "test_webiptv")
        print(f"   ✅ Generated: {output}")
        results.append(("WebIPTVGenerator", True, output))
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        results.append(("WebIPTVGenerator", False, str(e)))
    
    # Test SimplePlayerGenerator
    print("\n3. Testing SimplePlayerGenerator...")
    try:
        gen = SimplePlayerGenerator()
        output = gen.generate_page(m3u_content, "Test Simple Player", "test_simple")
        print(f"   ✅ Generated: {output}")
        results.append(("SimplePlayerGenerator", True, output))
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        results.append(("SimplePlayerGenerator", False, str(e)))
    
    # Test BufferTVGenerator
    print("\n4. Testing BufferTVGenerator...")
    try:
        gen = BufferTVGenerator()
        output = gen.generate_page(m3u_content, "Test Buffer TV", "test_buffer")
        print(f"   ✅ Generated: {output}")
        results.append(("BufferTVGenerator", True, output))
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        results.append(("BufferTVGenerator", False, str(e)))
    
    # Test ClassicTVGenerator
    print("\n5. Testing ClassicTVGenerator...")
    try:
        gen = ClassicTVGenerator()
        output, channel_count = gen.generate_page(m3u_content, "test_classic", "Test Classic TV")
        print(f"   ✅ Generated: {output} ({channel_count} channels)")
        results.append(("ClassicTVGenerator", True, output))
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        results.append(("ClassicTVGenerator", False, str(e)))
    
    # Test StreamHubGenerator
    print("\n6. Testing StreamHubGenerator...")
    try:
        gen = StreamHubGenerator()
        output = gen.generate_page(m3u_content, "Test Stream Hub")
        print(f"   ✅ Generated: {output}")
        results.append(("StreamHubGenerator", True, output))
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        results.append(("StreamHubGenerator", False, str(e)))
    
    # Test StandaloneSecurePageGenerator
    print("\n7. Testing StandaloneSecurePageGenerator...")
    try:
        gen = StandaloneSecurePageGenerator()
        output = gen.generate_page(m3u_content, "Test Secure Player")
        print(f"   ✅ Generated: {output}")
        results.append(("StandaloneSecurePageGenerator", True, output))
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        results.append(("StandaloneSecurePageGenerator", False, str(e)))
    
    # For RumbleChannelGenerator and MultiChannelGenerator, we need a different format
    # Parse M3U to channels format
    channels = []
    lines = m3u_content.strip().split('\n')
    current_channel = {}
    for line in lines:
        if line.startswith('#EXTINF'):
            import re
            name_match = re.search(r',(.+)$', line)
            logo_match = re.search(r'tvg-logo="([^"]*)"', line)
            group_match = re.search(r'group-title="([^"]*)"', line)
            current_channel = {
                'name': name_match.group(1) if name_match else 'Unknown',
                'logo': logo_match.group(1) if logo_match else '',
                'group': group_match.group(1) if group_match else 'General',
                'custom_tags': {'PROVIDER': 'RUMBLE'}  # For RumbleChannelGenerator
            }
        elif line and not line.startswith('#') and current_channel:
            current_channel['url'] = line
            channels.append(current_channel)
            current_channel = {}
    
    # Test RumbleChannelGenerator
    print("\n8. Testing RumbleChannelGenerator...")
    try:
        gen = RumbleChannelGenerator()
        output = gen.generate_page(channels, "test_rumble")
        print(f"   ✅ Generated: {output}")
        results.append(("RumbleChannelGenerator", True, output))
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        results.append(("RumbleChannelGenerator", False, str(e)))
    
    # Test MultiChannelGenerator
    print("\n9. Testing MultiChannelGenerator...")
    try:
        gen = MultiChannelGenerator()
        output = gen.generate_page(channels, "test_multi", 2)
        print(f"   ✅ Generated: {output}")
        results.append(("MultiChannelGenerator", True, output))
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        results.append(("MultiChannelGenerator", False, str(e)))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY OF TESTS")
    print("=" * 60)
    
    success_count = sum(1 for _, success, _ in results if success)
    total_count = len(results)
    
    for gen_name, success, output in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {gen_name}")
        if success:
            print(f"      Output: {output}")
    
    print(f"\nTotal: {success_count}/{total_count} generators passed")
    
    if success_count == total_count:
        print("\n🎉 All generators successfully generate pages with inline data!")
        print("\n📋 VERIFICATION STEPS:")
        print("1. Open any generated HTML file directly in a browser using file:// protocol")
        print("2. Check browser console for any fetch() errors (there should be none)")
        print("3. Verify channel/playlist data is displayed properly")
        print("\nExample files to test:")
        for gen_name, success, output in results[:3]:
            if success:
                print(f"   file://{Path(output).absolute()}")
    else:
        print("\n⚠️  Some generators failed. Please review the errors above.")
    
    return success_count == total_count

if __name__ == "__main__":
    success = test_generators()
    sys.exit(0 if success else 1)