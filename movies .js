// playlist.js
// HLS.js Compatible Playlist: Archive.org 1970s Movies
// Uses free public MP4-to-HLS proxy: https://bitdash-a.akamaihd.net/webtools/mp4-to-hls/

const ARCHIVE_BASE = "https://archive.org/download/rocky-1976_202310";

const HLS_PROXY = "https://bitdash-a.akamaihd.net/webtools/mp4-to-hls/playlist.m3u8?src=";

const playlist = [
    {
        "title": "Airport (1970)",
        "start_time": "00:00:00",
        "duration": 8220, // ~137 min
        "media_path": HLS_PROXY + encodeURIComponent(ARCHIVE_BASE + "/Airport%20(1970).mp4")
    },
    {
        "title": "Star Wars Holiday Special (1978)",
        "start_time": "00:00:00",
        "duration": 5820, // ~97 min
        "media_path": HLS_PROXY + encodeURIComponent(ARCHIVE_BASE + "/Star%20Wars%20Holiday%20Special%20(1978).mp4")
    },
    {
        "title": "Ice Castles (1978)",
        "start_time": "00:00:00",
        "duration": 6780, // ~113 min
        "media_path": HLS_PROXY + encodeURIComponent(ARCHIVE_BASE + "/Ice%20Castles%20(1978).mp4")
    },
    {
        "title": "One Flew Over The Cuckoo's Nest (1975)",
        "start_time": "00:00:00",
        "duration": 7980, // ~133 min
        "media_path": HLS_PROXY + encodeURIComponent(ARCHIVE_BASE + "/One%20Flew%20Over%20The%20Cuckoo's%20Nest%20(1975).mp4")
    },
    {
        "title": "Freaky Friday (1976)",
        "start_time": "00:00:00",
        "duration": 5700, // ~95 min
        "media_path": HLS_PROXY + encodeURIComponent(ARCHIVE_BASE + "/Freaky%20Friday%20(1976).mp4")
    },
    {
        "title": "THX-1138 (1971, Director's Cut 2004)",
        "start_time": "00:00:00",
        "duration": 5280, // ~88 min
        "media_path": HLS_PROXY + encodeURIComponent(ARCHIVE_BASE + "/THX-1138%20(1971,%20Director's%20cut%202004).mp4")
    },
    {
        "title": "The Champ (1979)",
        "start_time": "00:00:00",
        "duration": 7320, // ~122 min
        "media_path": HLS_PROXY + encodeURIComponent(ARCHIVE_BASE + "/The%20Champ%20(1979).mp4")
    },
    {
        "title": "Grease (1978)",
        "start_time": "00:00:00",
        "duration": 6600, // ~110 min
        "media_path": HLS_PROXY + encodeURIComponent(ARCHIVE_BASE + "/Grease%20(1978).mp4")
    },
    {
        "title": "Escape from the Planet of the Apes (1971)",
        "start_time": "00:00:00",
        "duration": 5880, // ~98 min
        "media_path": HLS_PROXY + encodeURIComponent(ARCHIVE_BASE + "/Escape%20from%20the%20Planet%20of%20the%20Apes%20(1971).mp4")
    },
    {
        "title": "Rocky (1976)",
        "start_time": "00:00:00",
        "duration": 7140, // ~119 min
        "media_path": HLS_PROXY + encodeURIComponent(ARCHIVE_BASE + "/Rocky%20(1976).mp4")
    },
    {
        "title": "The Longest Yard (1974)",
        "start_time": "00:00:00",
        "duration": 7320, // ~122 min
        "media_path": HLS_PROXY + encodeURIComponent(ARCHIVE_BASE + "/The%20Longest%20Yard%20(1974).mp4")
    },
    {
        "title": "The Goodbye Girl (1977)",
        "start_time": "00:00:00",
        "duration": 6660, // ~111 min
        "media_path": HLS_PROXY + encodeURIComponent(ARCHIVE_BASE + "/The%20Goodbye%20Girl%20(1977).mp4")
    },
    {
        "title": "Heaven Can Wait (1978)",
        "start_time": "00:00:00",
        "duration": 6120, // ~102 min
        "media_path": HLS_PROXY + encodeURIComponent(ARCHIVE_BASE + "/Heaven%20Can%20Wait%20(1978).mp4")
    },
    {
        "title": "Man of La Mancha (1972)",
        "start_time": "00:00:00",
        "duration": 7800, // ~130 min
        "media_path": HLS_PROXY + encodeURIComponent(ARCHIVE_BASE + "/Man%20of%20La%20Mancha%20(1972).mp4")
    },
    {
        "title": "Survive (1976 Dubbed)",
        "start_time": "00:00:00",
        "duration": 5280, // ~88 min
        "media_path": HLS_PROXY + encodeURIComponent(ARCHIVE_BASE + "/Survive%20(1976%20Dubbed).mp4")
    },
    {
        "title": "Silent Running (1972)",
        "start_time": "00:00:00",
        "duration": 5340, // ~89 min
        "media_path": HLS_PROXY + encodeURIComponent(ARCHIVE_BASE + "/Silent%20Running%20(1972).mp4")
    },
    {
        "title": "Battle For The Planet of the Apes (1973)",
        "start_time": "00:00:00",
        "duration": 5160, // ~86 min
        "media_path": HLS_PROXY + encodeURIComponent(ARCHIVE_BASE + "/Battle%20For%20The%20Planet%20of%20the%20Apes%20(1973).mp4")
    },
    {
        "title": "The Rose (1979)",
        "start_time": "00:00:00",
        "duration": 7500, // ~125 min
        "media_path": HLS_PROXY + encodeURIComponent(ARCHIVE_BASE + "/The%20Rose%20(1979).mp4")
    },
    {
        "title": "Rocky 2 (1979)",
        "start_time": "00:00:00",
        "duration": 7140, // ~119 min
        "media_path": HLS_PROXY + encodeURIComponent(ARCHIVE_BASE + "/Rocky%202%20(1979).mp4")
    },
    {
        "title": "Superman (1978 Extended)",
        "start_time": "00:00:00",
        "duration": 8580, // ~143 min
        "media_path": HLS_PROXY + encodeURIComponent(ARCHIVE_BASE + "/Superman%20(1978%20Extended%20version).mp4")
    },
    {
        "title": "American Graffiti (1973)",
        "start_time": "00:00:00",
        "duration": 6720, // ~112 min
        "media_path": HLS_PROXY + encodeURIComponent(ARCHIVE_BASE + "/American%20Graffiti%20(1973).mp4")
    },
    {
        "title": "Blazing Saddles (1974)",
        "start_time": "00:00:00",
        "duration": 5580, // ~93 min
        "media_path": HLS_PROXY + encodeURIComponent(ARCHIVE_BASE + "/Blazing%20Saddles%20(1974).mp4")
    },
    {
        "title": "The Emperor's New Clothes (1972)",
        "start_time": "00:00:00",
        "duration": 4800, // ~80 min
        "media_path": HLS_PROXY + encodeURIComponent(ARCHIVE_BASE + "/The%20Emperors%20New%20Clothes%20(1972).mp4")
    },
    {
        "title": "Conquest of the Planet of the Apes (1972)",
        "start_time": "00:00:00",
        "duration": 5280, // ~88 min
        "media_path": HLS_PROXY + encodeURIComponent(ARCHIVE_BASE + "/Conquest%20of%20the%20Planet%20of%20the%20Apes%20(1972).mp4")
    },
    {
        "title": "The Sunshine Boys (1975)",
        "start_time": "00:00:00",
        "duration": 6660, // ~111 min
        "media_path": HLS_PROXY + encodeURIComponent(ARCHIVE_BASE + "/The%20Sunshine%20Boys%20(1975).mp4")
    },
    {
        "title": "Kramer vs Kramer (1979)",
        "start_time": "00:00:00",
        "duration": 6300, // ~105 min
        "media_path": HLS_PROXY + encodeURIComponent(ARCHIVE_BASE + "/Kramer%20vs%20Kramer%20(1979).mp4")
    },
    {
        "title": "Love Story (1970)",
        "start_time": "00:00:00",
        "duration": 6000, // ~100 min
        "media_path": HLS_PROXY + encodeURIComponent(ARCHIVE_BASE + "/Love%20Story%20(1970).mp4")
    },
    {
        "title": "The Stepford Wives (1975)",
        "start_time": "00:00:00",
        "duration": 6900, // ~115 min
        "media_path": HLS_PROXY + encodeURIComponent(ARCHIVE_BASE + "/The%20Stepford%20Wives%20(1975).mp4")
    },
    {
        "title": "Corvette Summer (1978)",
        "start_time": "00:00:00",
        "duration": 6300, // ~105 min
        "media_path": HLS_PROXY + encodeURIComponent(ARCHIVE_BASE + "/Corvette%20Summer%20(1978).mp4")
    },
    {
        "title": "Moonrunners (1975)",
        "start_time": "00:00:00",
        "duration": 6540, // ~109 min
        "media_path": HLS_PROXY + encodeURIComponent(ARCHIVE_BASE + "/Moonrunners%20(1975).mp4")
    },
    {
        "title": "Beneath the Planet of the Apes (1970)",
        "start_time": "00:00:00",
        "duration": 5700, // ~95 min
        "media_path": HLS_PROXY + encodeURIComponent(ARCHIVE_BASE + "/Beneath%20the%20Planet%20of%20the%20Apes%20(1970).mp4")
    },
    {
        "title": "Willy Wonka & the Chocolate Factory (1971)",
        "start_time": "00:00:00",
        "duration": 6000, // ~100 min
        "media_path": HLS_PROXY + encodeURIComponent(ARCHIVE_BASE + "/Willy%20Wonka%20&%20the%20Chocolate%20Factory%20(1971).mp4")
    }
];

// Optional: Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = playlist;
}