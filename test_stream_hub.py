#!/usr/bin/env python3
"""Test Stream Hub generation with fixed HLS.js library"""

import json
import os

# Create a simple test playlist
test_playlist = {
    "channels": [
        {
            "name": "Test Stream 1",
            "url": "https://test.m3u8",
            "group": "Test",
            "logo": "",
            "epg": ""
        }
    ]
}

# Read the Stream Hub template
with open('templates/stream_hub_template.html', 'r', encoding='utf-8') as f:
    template_content = f.read()

# Replace the placeholder with our test playlist
page_content = template_content.replace(
    '{{playlist_json}}',
    json.dumps(test_playlist, ensure_ascii=False, indent=2)
)

# Check if HLS.js is properly embedded
if '!function e(t){var r,i;r=this,i=function()' in page_content:
    print("✅ HLS.js library is properly embedded!")
    
    # Check for key HLS methods
    if 'isSupported' in page_content and 'loadSource' in page_content:
        print("✅ HLS.js methods (isSupported, loadSource) are present!")
    else:
        print("⚠️ Some HLS.js methods may be missing")
else:
    print("❌ HLS.js library not found or truncated!")

# Save test page
os.makedirs('generated_pages/stream_hub', exist_ok=True)
test_file = 'generated_pages/stream_hub/test_page.html'
with open(test_file, 'w', encoding='utf-8') as f:
    f.write(page_content)

print(f"📁 Test page saved to: {test_file}")
print(f"📊 Page size: {len(page_content):,} characters")
print("🌐 Access at: http://localhost:5000/generated_pages/stream_hub/test_page.html")