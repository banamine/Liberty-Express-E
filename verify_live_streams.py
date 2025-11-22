import json
import requests
import re
from urllib.parse import urlparse
import time

print("🔍 Verifying HLS streams from rumble_hls_channels.json...")
print("=" * 70)

# Load channels
with open('generated_pages/rumble_hls_channels.json', 'r') as f:
    channels = json.load(f)

verified_live = []
dead_vod = []

for idx, channel in enumerate(channels):
    name = channel['name']
    hls_url = channel['hls_url']
    viewers = channel['viewers']
    
    # Test if HLS stream is live or dead/VOD
    try:
        # Fetch the M3U8 playlist
        response = requests.head(hls_url, timeout=3, allow_redirects=True)
        
        if response.status_code == 200:
            # Now fetch actual content to check if LIVE or VOD
            response = requests.get(hls_url, timeout=5)
            if response.status_code == 200:
                content = response.text
                
                # Check for VOD indicators
                is_vod = '#EXT-X-ENDLIST' in content  # ENDLIST = VOD (finished)
                is_live = '#EXT-X-MEDIA-SEQUENCE' in content and '#EXT-X-ENDLIST' not in content
                
                if is_live:
                    verified_live.append(channel)
                    print(f"✅ [{idx+1}] {name:<35} - LIVE ({viewers} viewers)")
                else:
                    dead_vod.append((name, "VOD/OFFLINE"))
                    print(f"❌ [{idx+1}] {name:<35} - VOD or OFFLINE")
            else:
                dead_vod.append((name, f"HTTP {response.status_code}"))
                print(f"❌ [{idx+1}] {name:<35} - HTTP {response.status_code}")
        else:
            dead_vod.append((name, f"HTTP {response.status_code}"))
            print(f"❌ [{idx+1}] {name:<35} - HTTP {response.status_code}")
            
    except requests.Timeout:
        dead_vod.append((name, "TIMEOUT"))
        print(f"⏱️  [{idx+1}] {name:<35} - TIMEOUT (dead)")
    except Exception as e:
        dead_vod.append((name, str(e)[:20]))
        print(f"⚠️  [{idx+1}] {name:<35} - ERROR ({str(e)[:20]}...)")
    
    time.sleep(0.1)  # Be polite to servers

print("\n" + "=" * 70)
print(f"📊 RESULTS:")
print(f"   ✅ LIVE & WORKING: {len(verified_live)}")
print(f"   ❌ DEAD/VOD/OFFLINE: {len(dead_vod)}")
print(f"   📺 Total verified for carousel: {len(verified_live)}")

# Save verified LIVE channels
if verified_live:
    with open('generated_pages/rumble_hls_channels_verified.json', 'w') as f:
        json.dump(verified_live, f, indent=2)
    print(f"\n✅ Saved {len(verified_live)} verified LIVE channels to rumble_hls_channels_verified.json")
else:
    print("\n⚠️  No LIVE channels found!")

