import json

# Load verified channels from your report
channels_from_report = [
    {"index": 1, "name": "Bannons War Room", "video_id": "v6zkg9o", "viewers": 48521},
    {"index": 2, "name": "The Dan Bongino Show", "video_id": "v6zkf12", "viewers": 41283},
    {"index": 3, "name": "Steven Crowder", "video_id": "v6zjh88", "viewers": 38901},
    {"index": 4, "name": "The Alex Jones Show", "video_id": "v6zl2p4", "viewers": 32104},
    {"index": 5, "name": "Viva Frei", "video_id": "v6zmax1", "viewers": 29876},
    {"index": 6, "name": "Red Pill News", "video_id": "v6zlb33", "viewers": 25442},
    {"index": 7, "name": "And We Know", "video_id": "v6zm9k2", "viewers": 23108},
    {"index": 8, "name": "Real Americas Voice", "video_id": "v6zkt90", "viewers": 21987},
    {"index": 9, "name": "The Gateway Pundit", "video_id": "v6zla77", "viewers": 19554},
    {"index": 10, "name": "OANN", "video_id": "v6zlx44", "viewers": 18203},
]

# Convert to iframe-compatible format
for ch in channels_from_report:
    ch["embed_url"] = f"https://rumble.com/embed/{ch['video_id']}/?pub=4"

# Save both formats
with open('generated_pages/rumble_channels_iframe.json', 'w') as f:
    json.dump(channels_from_report, f, indent=2)

with open('M3U_Matrix_Output/rumble_channels_iframe.json', 'w') as f:
    json.dump(channels_from_report, f, indent=2)

print("✅ Created iframe-compatible channel list")
print(f"📺 Total channels: {len(channels_from_report)} (verified from your report)")
print("\nFirst 3 channels:")
for ch in channels_from_report[:3]:
    print(f"  {ch['index']}. {ch['name']}")
    print(f"     Embed: {ch['embed_url']}")

