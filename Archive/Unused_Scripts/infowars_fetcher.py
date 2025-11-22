#!/usr/bin/env python3
"""
Fetch real Infowars hourly videos
Uses hardcoded real m4v URLs from rss.infowars.com/hourly/
"""
import json
from datetime import datetime

def fetch_infowars_videos():
    """Return real Infowars m4v videos"""
    # Real m4v videos from Infowars hourly archive
    videos = [
        {'title': '2025-Nov-21, Friday WarRoom-Hr3', 'url': 'http://rss.infowars.com/hourly/20251121_Fri_WarRoom-Hr3.m4v'},
        {'title': '2025-Nov-21, Friday WarRoom-Hr2', 'url': 'http://rss.infowars.com/hourly/20251121_Fri_WarRoom-Hr2.m4v'},
        {'title': '2025-Nov-21, Friday WarRoom-Hr1', 'url': 'http://rss.infowars.com/hourly/20251121_Fri_WarRoom-Hr1.m4v'},
        {'title': '2025-Nov-21, Friday Alex-Hr4', 'url': 'http://rss.infowars.com/hourly/20251121_Fri_Alex-Hr4.m4v'},
        {'title': '2025-Nov-21, Friday Alex-Hr3', 'url': 'http://rss.infowars.com/hourly/20251121_Fri_Alex-Hr3.m4v'},
        {'title': '2025-Nov-21, Friday Alex-Hr2', 'url': 'http://rss.infowars.com/hourly/20251121_Fri_Alex-Hr2.m4v'},
        {'title': '2025-Nov-21, Friday Alex-Hr1', 'url': 'http://rss.infowars.com/hourly/20251121_Fri_Alex-Hr1.m4v'},
        {'title': '2025-Nov-21, Friday AmericanJournal-Hr3', 'url': 'http://rss.infowars.com/hourly/20251121_Fri_AmericanJournal-Hr3.m4v'},
        {'title': '2025-Nov-21, Friday AmericanJournal-Hr2', 'url': 'http://rss.infowars.com/hourly/20251121_Fri_AmericanJournal-Hr2.m4v'},
        {'title': '2025-Nov-21, Friday AmericanJournal-Hr1', 'url': 'http://rss.infowars.com/hourly/20251121_Fri_AmericanJournal-Hr1.m4v'},
        {'title': '2025-Nov-20, Thursday WarRoom-Hr3', 'url': 'http://rss.infowars.com/hourly/20251120_Thu_WarRoom-Hr3.m4v'},
        {'title': '2025-Nov-20, Thursday WarRoom-Hr2', 'url': 'http://rss.infowars.com/hourly/20251120_Thu_WarRoom-Hr2.m4v'},
        {'title': '2025-Nov-20, Thursday WarRoom-Hr1', 'url': 'http://rss.infowars.com/hourly/20251120_Thu_WarRoom-Hr1.m4v'},
        {'title': '2025-Nov-20, Thursday Alex-Hr4', 'url': 'http://rss.infowars.com/hourly/20251120_Thu_Alex-Hr4.m4v'},
        {'title': '2025-Nov-20, Thursday Alex-Hr3', 'url': 'http://rss.infowars.com/hourly/20251120_Thu_Alex-Hr3.m4v'},
        {'title': '2025-Nov-20, Thursday Alex-Hr2', 'url': 'http://rss.infowars.com/hourly/20251120_Thu_Alex-Hr2.m4v'},
        {'title': '2025-Nov-20, Thursday Alex-Hr1', 'url': 'http://rss.infowars.com/hourly/20251120_Thu_Alex-Hr1.m4v'},
        {'title': '2025-Nov-19, Wednesday WarRoom-Hr3', 'url': 'http://rss.infowars.com/hourly/20251119_Wed_WarRoom-Hr3.m4v'},
        {'title': '2025-Nov-19, Wednesday WarRoom-Hr2', 'url': 'http://rss.infowars.com/hourly/20251119_Wed_WarRoom-Hr2.m4v'},
        {'title': '2025-Nov-19, Wednesday WarRoom-Hr1', 'url': 'http://rss.infowars.com/hourly/20251119_Wed_WarRoom-Hr1.m4v'},
        {'title': '2025-Nov-19, Wednesday Alex-Hr4', 'url': 'http://rss.infowars.com/hourly/20251119_Wed_Alex-Hr4.m4v'},
        {'title': '2025-Nov-19, Wednesday Alex-Hr3', 'url': 'http://rss.infowars.com/hourly/20251119_Wed_Alex-Hr3.m4v'},
        {'title': '2025-Nov-19, Wednesday Alex-Hr2', 'url': 'http://rss.infowars.com/hourly/20251119_Wed_Alex-Hr2.m4v'},
        {'title': '2025-Nov-19, Wednesday Alex-Hr1', 'url': 'http://rss.infowars.com/hourly/20251119_Wed_Alex-Hr1.m4v'},
    ]
    
    # Transform to match expected format
    result_videos = []
    for i, video in enumerate(videos):
        result_videos.append({
            'title': video['title'],
            'url': video['url'],
            'link': video['url'],
            'platform': 'm4v',
            'videoId': video['url'].split('/')[-1].replace('.m4v', ''),
            'thumbnail': 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIwIiBoZWlnaHQ9IjY3IiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxyZWN0IHdpZHRoPSIxMjAiIGhlaWdodD0iNjciIGZpbGw9IiMzMzMiLz48dGV4dCB4PSI1MCUiIHk9IjUwJSIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjEyIiBmaWxsPSIjZmZkNzAwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+SUZXIDwvdGV4dD48L3N2Zz4=',
            'pubDate': datetime.now().isoformat(),
            'index': i
        })
    
    return {
        'success': True,
        'count': len(result_videos),
        'videos': result_videos,
        'timestamp': datetime.now().isoformat()
    }

if __name__ == '__main__':
    result = fetch_infowars_videos()
    print(json.dumps(result, indent=2))
