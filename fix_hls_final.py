#!/usr/bin/env python3
"""Replace the broken HLS.js in Stream Hub template with working version"""

import re

# Read the correct HLS.js library
with open('/tmp/hls.min.js', 'r', encoding='utf-8') as f:
    hls_content = f.read().strip()
    # Remove source map comment if present
    hls_content = hls_content.replace('//# sourceMappingURL=hls.min.js.map', '')
    hls_content = hls_content.strip()

print(f"✅ Loaded HLS.js library: {len(hls_content):,} characters")

# Read the Stream Hub template
with open('templates/stream_hub_template.html', 'r', encoding='utf-8') as f:
    template_content = f.read()

# Find and replace the HLS.js script section
# Look for the pattern from the HLS comment to the closing script tag
pattern = r'(<!-- HLS\.js Library \(Embedded\) -->[\s\S]*?<script>)([\s\S]*?)(</script>)'

def replacement(match):
    prefix = match.group(1)
    suffix = match.group(3)
    # Add comment about the correct version
    new_content = prefix + '\n        // HLS.js v1.x - Complete Library from CDN\n        ' + hls_content + '\n    ' + suffix
    return new_content

# Replace the truncated HLS.js with the complete library
new_template = re.sub(pattern, replacement, template_content)

# Verify the replacement worked
if 'Hls.isSupported' in new_template and len(new_template) > len(template_content):
    print("✅ Successfully replaced HLS.js in template!")
    print(f"📊 Template size: {len(template_content):,} → {len(new_template):,} characters")
    
    # Save the fixed template
    with open('templates/stream_hub_template.html', 'w', encoding='utf-8') as f:
        f.write(new_template)
    
    print("💾 Saved fixed Stream Hub template")
    print("🎉 Stream Hub HLS.js is now fully functional!")
else:
    print("❌ Failed to replace HLS.js properly")
    print("Check the pattern matching in the script")