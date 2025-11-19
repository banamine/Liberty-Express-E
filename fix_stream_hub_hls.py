#!/usr/bin/env python3
"""Fix the truncated HLS.js library in Stream Hub template"""

import re

# Read the complete HLS.js library from web-iptv-extension
with open('templates/web-iptv-extension/js/libs/hls.min.js', 'r', encoding='utf-8') as f:
    hls_content = f.read().strip()
    # Remove the source map comment if present
    hls_content = hls_content.replace('//# sourceMappingURL=hls.min.js.map', '')
    hls_content = hls_content.strip()

# Read the Stream Hub template
with open('templates/stream_hub_template.html', 'r', encoding='utf-8') as f:
    template_content = f.read()

# Find and replace the truncated HLS.js script block
# The pattern matches from the HLS.js script tag to the closing script tag
pattern = r'(<!-- HLS\.js Library \(Embedded\) -->[\s\S]*?<script>[\s\S]*?)(!function\(e\)[\s\S]*?)(</script>)'

def replacement(match):
    prefix = match.group(1)
    suffix = match.group(3)
    return prefix + '\n        ' + hls_content + '\n    ' + suffix

# Replace the truncated HLS.js with the complete library
new_content = re.sub(pattern, replacement, template_content)

# Write the fixed template
with open('templates/stream_hub_template.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Fixed Stream Hub template - HLS.js library replaced successfully!")
print("📦 HLS.js library size:", len(hls_content), "characters")
print("🎉 Stream Hub should now work properly with HLS streaming!")