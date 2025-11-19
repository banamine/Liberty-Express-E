# NDI Broadcast Output Guide
## Professional Network Device Interface Integration for M3U Matrix Pro

### Overview
M3U Matrix Pro now includes professional **NDI (Network Device Interface)** output capability, enabling broadcast-grade video-over-IP streaming to production systems like OBS Studio, vMix, Wirecast, and TriCaster. NDI allows you to send multiple high-quality video streams over your local network without cables or capture cards.

### What is NDI?
NDI is a royalty-free protocol developed by NewTek that enables video-compatible products to communicate, deliver, and receive high-quality video and audio over standard Ethernet networks. It's widely used in professional broadcast environments for:
- Live production switching
- Remote broadcasting
- Multi-camera setups
- Virtual production
- Church and event streaming

### Prerequisites

#### Required Software
1. **VLC Media Player** (v3.0 or higher) - Must be installed with NDI plugin
2. **NDI Tools** (v6.0 or higher) - Download from [ndi.tv](https://ndi.tv/tools/)
3. **M3U Matrix Pro** - Latest version with NDI support

#### Compatible Production Software
- **OBS Studio** (with NDI plugin)
- **vMix**
- **Wirecast**
- **TriCaster systems**
- **NDI Studio Monitor** (for testing)

### Setting Up NDI Output

#### From M3U Matrix Pro

1. **Load Your Playlist**
   - Open M3U Matrix Pro
   - Load your M3U playlist with channels

2. **Open NDI Control Center**
   - Click the **🔴 NDI** button in the toolbar (red button, Row 2)
   - The NDI Output Control Center window will open

3. **Start NDI Broadcasting**
   - Select a channel from the list
   - Click **▶ Start NDI Output**
   - The channel will begin broadcasting via NDI
   - Monitor status in the bottom panel

4. **Manage Multiple Streams**
   - Select different channels and start NDI for each
   - Each stream gets a unique NDI source name
   - Monitor all active streams in the status panel
   - Use **⏹ Stop All NDI** to terminate all streams

#### From Video Player Pro

1. **Open Video Player Pro**
   - Click **VIDEO** button in M3U Matrix Pro
   - Or launch directly from Video Player Workbench

2. **Enable NDI Output**
   - In the Workbench panel, locate the NDI Control section
   - Toggle **Enable NDI Output** to ON
   - Set your NDI source name (e.g., "Studio_Feed_1")
   - The video will broadcast via NDI when playing

3. **Monitor Status**
   - Check the NDI status indicator
   - Green = Broadcasting
   - Red = Inactive

### Receiving NDI in OBS Studio

1. **Install OBS NDI Plugin**
   ```
   Download from: https://github.com/obs-ndi/obs-ndi
   Install and restart OBS
   ```

2. **Add NDI Source**
   - Click **+** in Sources
   - Select **NDI™ Source**
   - Name your source

3. **Select NDI Stream**
   - In properties, click **Source Name** dropdown
   - Select your M3U Matrix NDI stream
   - Adjust settings as needed

4. **Configure Output**
   - Set bandwidth mode (Highest/Lowest)
   - Enable/disable audio
   - Apply color correction if needed

### NDI Stream Configuration

#### Default Settings
```
Resolution: 1920x1080 (Full HD)
Framerate: 30 FPS
Color Space: RGBA
Audio: Stereo 48kHz
Bandwidth: ~150 Mbps per stream
Protocol: TCP (reliable) or UDP (low latency)
```

#### Network Requirements
- **Gigabit Ethernet** recommended
- **Same network/VLAN** for sources and receivers
- **Firewall exceptions** for NDI ports (5960-5969 default)
- **Quality switches** for multiple streams

### Advanced Features

#### Multi-Channel Broadcasting
M3U Matrix Pro can broadcast multiple channels simultaneously:
1. Each channel becomes a separate NDI source
2. Production software can switch between sources
3. Create multi-view layouts with different channels
4. Perfect for control room monitoring

#### Naming Convention
NDI sources are named as:
```
[Channel_Name]_NDI
Example: CNN_International_NDI
Example: Sports_Channel_1_NDI
```

#### Bandwidth Management
Estimated bandwidth per stream:
- **Full NDI** (Best quality): ~150 Mbps
- **NDI|HX2** (Compressed): ~20 Mbps
- **NDI|HX3** (H.265): ~10 Mbps

For 4 simultaneous Full NDI streams: ~600 Mbps total

### Professional Workflows

#### Live Production Setup
```
M3U Matrix Pro → NDI → OBS/vMix → Streaming Platform
                  ↓
            NDI Recording
                  ↓
           Post Production
```

#### Multi-Camera Event
```
Camera 1 → NDI → 
Camera 2 → NDI → Production Switcher → Program Output
Camera 3 → NDI → 
M3U Matrix (Graphics/Lower Thirds) → NDI →
```

#### Remote Production
```
Location A: M3U Matrix → NDI → Internet → 
Location B: M3U Matrix → NDI → Internet → Central Control Room
Location C: M3U Matrix → NDI → Internet → 
```

### Troubleshooting

#### NDI Sources Not Visible
1. **Check NDI Tools Installation**
   - Run NDI Studio Monitor
   - Should see local NDI sources

2. **Verify Network**
   - Sources and receivers on same network
   - No VLAN isolation
   - Firewall allows NDI traffic

3. **Restart Services**
   - Close all NDI applications
   - Restart M3U Matrix Pro
   - Restart production software

#### Poor Quality or Dropped Frames
1. **Network Capacity**
   - Use Gigabit Ethernet (not WiFi)
   - Check network congestion
   - Use quality switches

2. **System Resources**
   - Close unnecessary applications
   - Check CPU usage (<80%)
   - Ensure adequate RAM

3. **Reduce Streams**
   - Lower simultaneous NDI outputs
   - Use NDI|HX for compression
   - Adjust resolution/framerate

#### VLC NDI Plugin Issues
1. **Install VLC NDI Support**
   ```
   Windows: Copy NDI plugin to VLC/plugins folder
   Mac: Install NDI Runtime and VLC plugin
   Linux: Install libndi and VLC plugin
   ```

2. **Verify Plugin Loading**
   - Open VLC → Tools → Plugins
   - Search for "NDI"
   - Should show NewTek NDI

### Best Practices

1. **Network Design**
   - Dedicate network/VLAN for NDI traffic
   - Use managed switches with QoS
   - Monitor bandwidth usage

2. **Source Management**
   - Use clear, consistent naming
   - Document IP addresses
   - Create source groups

3. **Quality Settings**
   - Match resolution to final output
   - Use appropriate compression
   - Test before going live

4. **Redundancy**
   - Keep backup streams ready
   - Have fallback sources
   - Test failover procedures

### Performance Optimization

#### System Requirements
**Minimum:**
- Intel i5 or AMD Ryzen 5
- 8GB RAM
- Gigabit Ethernet
- Windows 10/11, macOS 10.15+, Linux

**Recommended:**
- Intel i7/i9 or AMD Ryzen 7/9
- 16GB+ RAM
- Dedicated Gigabit network
- SSD storage
- Dedicated GPU (optional)

#### Optimization Tips
1. **Close unnecessary applications**
2. **Disable Windows updates during broadcast**
3. **Use wired connections only**
4. **Set process priority to High**
5. **Disable power saving modes**

### Integration Examples

#### OBS Studio Scene
```
Scene: Multi-Channel News
├── NDI Source 1: CNN_International_NDI (Main)
├── NDI Source 2: Weather_Channel_NDI (PiP)
├── NDI Source 3: Sports_Ticker_NDI (Lower Third)
└── Local Camera (Host)
```

#### vMix Input Setup
```
Input 1: M3U_Matrix_Channel_1 (NDI)
Input 2: M3U_Matrix_Channel_2 (NDI)  
Input 3: Graphics_Feed (NDI)
Input 4: Studio_Camera_1 (SDI)
```

### Security Considerations

1. **Network Isolation**
   - Keep NDI on private network
   - Use VPN for remote NDI
   - Implement access controls

2. **Stream Protection**
   - NDI is unencrypted by default
   - Use NDI|HX3 for encryption support
   - Monitor network access

3. **Content Rights**
   - Respect broadcast rights
   - Obtain necessary licenses
   - Document source permissions

### Future Enhancements

Planned features for NDI support:
- Native NDI SDK integration (better performance)
- NDI recording to file
- NDI metadata injection
- Tally light support
- PTZ camera control
- Alpha channel support
- 4K/UHD streaming
- NDI Bridge for WAN streaming

### Support and Resources

#### Official Resources
- **NDI Website**: [ndi.tv](https://ndi.tv)
- **NDI Tools**: [ndi.tv/tools](https://ndi.tv/tools)
- **NDI SDK**: [ndi.tv/sdk](https://ndi.tv/sdk)

#### Community
- **NDI Reddit**: r/NDI
- **OBS Forums**: obsproject.com/forum
- **vMix Forums**: forums.vmix.com

#### Troubleshooting Help
- Check M3U Matrix Pro logs
- Run NDI Test Patterns
- Use NDI Studio Monitor
- Contact support with diagnostics

### Quick Reference Card

```
┌─────────────────────────────────────┐
│         NDI QUICK COMMANDS          │
├─────────────────────────────────────┤
│ Start NDI:                          │
│   M3U Matrix → 🔴 NDI → Select →    │
│   ▶ Start NDI Output                │
│                                     │
│ View in OBS:                        │
│   Sources → + → NDI Source →       │
│   Select Stream → OK               │
│                                     │
│ Stop All:                           │
│   🔴 NDI → ⏹ Stop All NDI          │
│                                     │
│ Check Status:                       │
│   NDI Studio Monitor → Sources     │
│                                     │
│ Network Test:                       │
│   ping [device-ip] -t              │
│   Check <4ms latency               │
└─────────────────────────────────────┘
```

---

*NDI® is a registered trademark of Vizrt Group.*
*This guide is part of M3U Matrix Pro documentation.*
*Version 1.0 - Professional Broadcast Integration*