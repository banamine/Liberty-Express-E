// ============================================
// JAVASCRIPT EXAMPLES FOR SCHEDULEFLOW CAROUSEL
// ============================================

// Example 1: Simple Single Video
// ================================
const singleVideoExample = {
    url: 'https://commondatastorage.googleapis.com/gtv-videos-library/sample/BigBuckBunny.mp4',
    label: 'My Movie',
    description: '9 minute full-length video'
};

// Example 2: Short Video
// ================================
const shortVideoExample = {
    url: 'https://commondatastorage.googleapis.com/gtv-videos-library/sample/VolleyballShort.mp4',
    label: 'Volleyball Clip',
    description: '2 minute short video'
};

// Example 3: Rumble Video (iframe embedded)
// ================================
const rumbleVideoExample = {
    url: 'https://rumble.com/embed/v3t4m5f/',
    label: 'Rumble Video',
    description: 'Embedded Rumble video player'
};

// Example 4: HLS Stream (Live TV / Playlist)
// ================================
const hlsStreamExample = {
    url: 'https://a.files.bbci.co.uk/media/live/manifesto/audio/simulcast/hls/original/llnw/en/audio_aac_lc_128kbps.m3u8',
    label: 'Live Stream',
    description: 'HLS streaming playlist'
};

// Example 5: Create Multiple Videos Playlist
// ================================
const playlistExample = [
    {
        url: 'https://commondatastorage.googleapis.com/gtv-videos-library/sample/BigBuckBunny.mp4',
        label: 'Movie 1: Big Buck Bunny',
        description: 'Feature length film'
    },
    {
        url: 'https://commondatastorage.googleapis.com/gtv-videos-library/sample/ElephantsDream.mp4',
        label: 'Movie 2: Elephant\'s Dream',
        description: 'Animated feature'
    },
    {
        url: 'https://commondatastorage.googleapis.com/gtv-videos-library/sample/ForBiggerBlazes.mp4',
        label: 'Promo: Bigger Blazes',
        description: 'Marketing video'
    },
    {
        url: 'https://commondatastorage.googleapis.com/gtv-videos-library/sample/VolleyballShort.mp4',
        label: 'Short: Volleyball',
        description: '2 minute sports clip'
    }
];

// Example 6: Programmatically Add Videos to Carousel
// ================================
function addVideoToCarousel(url, label, description) {
    // This is how the carousel stores videos internally
    const video = {
        url: url,
        label: label || 'Video',
        description: description || url.substring(0, 50) + '...'
    };
    
    // The carousel uses localStorage to persist videos
    let videos = JSON.parse(localStorage.getItem('scheduleflow_videos') || '[]');
    videos.push(video);
    localStorage.setItem('scheduleflow_videos', JSON.stringify(videos));
    
    console.log('✅ Added:', label);
}

// Example 7: Import M3U Playlist (Copy-Paste Format)
// ================================
const m3uPlaylistExample = `#EXTM3U
#EXT-X-VERSION:3

#EXTINF:574, Movie: Big Buck Bunny
https://commondatastorage.googleapis.com/gtv-videos-library/sample/BigBuckBunny.mp4

#EXTINF:180, Short: Elephant's Dream
https://commondatastorage.googleapis.com/gtv-videos-library/sample/ElephantsDream.mp4

#EXTINF:300, Rumble Video
https://rumble.com/embed/v3t4m5f/

#EXTINF:120, Sports Clip
https://commondatastorage.googleapis.com/gtv-videos-library/sample/VolleyballShort.mp4`;

// Usage: Copy above into "Paste M3U playlist" text area and click "Import M3U Playlist"

// Example 8: Rumble Direct Link Formats
// ================================
const rumbleLinkFormats = {
    embedFormat: 'https://rumble.com/embed/VIDEO_ID/',
    directFormat: 'https://rumble.com/v123456-title/',
    videoIdOnly: 'VIDEO_ID' // Extract from URL for custom handling
};

// Example 9: Testing with Public Domain Movies
// ================================
const publicDomainMovies = [
    {
        url: 'https://archive.org/download/ElephantsDream/Elephants_Dream_1080p_H.264.mp4',
        label: 'Elephant\'s Dream (Full)',
        description: 'Animated feature - Public Domain'
    },
    {
        url: 'https://commondatastorage.googleapis.com/gtv-videos-library/sample/BigBuckBunny.mp4',
        label: 'Big Buck Bunny',
        description: 'Creative Commons licensed'
    },
    {
        url: 'https://commondatastorage.googleapis.com/gtv-videos-library/sample/ForBiggerBlazes.mp4',
        label: 'For Bigger Blazes',
        description: 'Sample video'
    }
];

// Example 10: Create Shareable Clip Link
// ================================
function generateClipShareLink(videoTitle, startTimeSeconds, endTimeSeconds) {
    // The carousel generates shareable URLs like:
    // http://your-app/scheduleflow_carousel.html?title=VideoTitle&start=123&end=456
    
    const params = new URLSearchParams({
        title: videoTitle,
        start: startTimeSeconds,
        end: endTimeSeconds
    });
    
    const shareUrl = `${window.location.origin}/scheduleflow_carousel.html?${params}`;
    console.log('Share this clip:', shareUrl);
    return shareUrl;
}

// Example Usage:
// generateClipShareLink('Movie Scene', 120, 300); // Share 2:00-5:00 segment

// ============================================
// QUICK START: How to Use
// ============================================

/*
OPTION 1: Add Single Video
1. Go to http://your-app/scheduleflow_carousel.html
2. Click "➕ Add URL"
3. Paste: https://commondatastorage.googleapis.com/gtv-videos-library/sample/BigBuckBunny.mp4
4. Click "Add Video"
5. Click "▶️ PLAY"

OPTION 2: Import M3U Playlist
1. Copy the playlistExample M3U text above
2. Go to carousel page
3. Click "➕ Add URL"
4. Paste into "Paste M3U playlist" box
5. Click "Import M3U Playlist"
6. Use arrows to browse videos
7. Click "▶️ PLAY" on any video

OPTION 3: Add Rumble Video
1. Find video ID from Rumble URL
2. Use: https://rumble.com/embed/VIDEO_ID/
3. Add to carousel same way as other videos

OPTION 4: Use Clip Mode
1. Play a video
2. Click "✂️ Clip Mode"
3. Click "Mark Start" at desired start time
4. Click "Mark End" at desired end time
5. Click "▶️ Play Clip"
6. Click "🔗 Share" to generate shareable link with timestamps
*/

// ============================================
// RUMBLE INTEGRATION NOTES
// ============================================

/*
Rumble videos work in two ways:

1. EMBED FORMAT (Recommended)
   - Use: https://rumble.com/embed/VIDEOID/
   - The carousel detects .com/embed/ and uses iframe
   - Full Rumble player functionality
   
2. DIRECT LINK
   - If Rumble provides direct MP4 URL
   - Just paste the direct URL instead

HOW TO GET RUMBLE VIDEO ID:
1. Go to video on Rumble.com
2. Look at URL: https://rumble.com/v3t4m5f-title/
3. Extract: v3t4m5f
4. Use embed: https://rumble.com/embed/v3t4m5f/
*/

// ============================================
// COMMON VIDEO FORMATS SUPPORTED
// ============================================

const supportedFormats = {
    'MP4': '.mp4 files (H.264 codec)',
    'M3U Playlist': '.m3u or .m3u8 files (HLS streams)',
    'HLS': 'HTTP Live Streaming playlists',
    'Rumble': 'Rumble.com embed links',
    'WebM': '.webm files (VP8/VP9 codec)',
    'Ogg': '.ogg files (Theora codec)'
};

// ============================================
// FILE SIZE REFERENCE
// ============================================

/*
Big Buck Bunny MP4:  ~175 MB (9 minutes)
Elephant's Dream:    ~120 MB (11 minutes)
Short Clips:         ~5-50 MB (30 seconds - 2 minutes)

For streaming, use HLS (.m3u8) instead of downloading full files
*/

// ============================================
// KEYBOARD SHORTCUTS IN CAROUSEL
// ============================================

/*
← / → : Previous/Next video
ENTER : Play current video
C     : Toggle Clip Mode
S     : Share current video
*/
