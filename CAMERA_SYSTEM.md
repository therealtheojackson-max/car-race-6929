# Camera & Video System Documentation

## Overview

The City Car Race game now includes a fully functional camera and video recording system that allows players to:
- Record videos within their home
- Manage a video library
- Upload videos for currency rewards
- Track video statistics (views, likes)

## Features

### Computer Hardware
- **Location**: Corner of player's home (repositions with house upgrades)
- **Design**: Brown desk with green monitor screen
- **Interaction**: Click to launch Camera App
- **Visual Feedback**: Recording indicator (red dot when active)

### Camera App

#### Recording Interface
- **Start/Stop**: Press SPACE to toggle recording
- **Display**: Shows elapsed time while recording
- **Auto-Save**: Videos automatically saved with auto-generated titles
- **Preview**: Large black preview area showing recording status
- **Feedback**: Recording indicator shows "● RECORDING" in red

#### Video Library Interface
- **Access**: Press L to toggle library view
- **Display**: Shows up to 6 videos per screen
- **Metadata**: Title, duration (seconds), view count
- **Color Coding**: First video highlighted in green (selected)

### Video Management

#### Recording
```
Action: Press SPACE
Result: 
  - Recording starts (shows elapsed time)
  - Press SPACE again to stop
  - Video auto-saves to library with auto-generated title
  - Duration stored in seconds
```

#### Uploading
```
Action: Press Enter (in library view)
Result:
  - Video upload with currency reward
  - Views generated: random(10, 500)
  - Likes generated: random(0, views/3)
  - Earnings: max(50, duration_minutes * 10)
  - Video moves to end of library
  - Currency added to player account
```

#### Deleting
```
Action: Press Delete (in library view)
Result:
  - First video removed from library
  - Change persisted to videos.json
```

### Controls

| Action | Key | Effect |
|--------|-----|--------|
| Record | SPACE | Start/stop recording |
| Library | L | Toggle video library view |
| Upload | Enter | Upload selected video, earn currency |
| Delete | Delete | Remove selected video |
| Close | ESC | Exit camera app |

## Data Persistence

### videos.json Format
```json
[
  {
    "title": "Video 1",
    "duration": 15.5,
    "timestamp": 1764864000.123,
    "views": 245,
    "likes": 67,
    "description": ""
  },
  ...
]
```

### Storage
- **File**: `videos.json`
- **Location**: Project root directory
- **Creation**: Automatic on first video
- **Persistence**: Survives game restarts
- **Updates**: Saved after each operation (record, upload, delete)

## Currency Rewards

### Earning Formula
```
Base Earnings = max(50, floor(duration_in_minutes * 10))
```

### Examples
- 10 seconds: $50 (minimum)
- 30 seconds: $50 (minimum)
- 60 seconds (1 min): $60
- 120 seconds (2 min): $70
- 300 seconds (5 min): $100
- 600 seconds (10 min): $150

### View Generation
- **Range**: 10-500 random views per upload
- **Likes**: 0 to views÷3 random likes
- **Purpose**: Simulates social media engagement

## Integration with Game Systems

### Home System
- Computer appears in all house tiers
- Survives house upgrades and repositioning
- Capacity doesn't affect video limits
- Integrated with home decoration space

### Currency System
- Video uploads add to player.currency
- Earnings displayed on upload confirmation
- System message shows earnings: `"Uploaded video! Earned $XXX"`

### Chat System
- System notifications on video upload
- Videos not broadcast to other players
- Local-only feature (single-player social media sim)

## Technical Implementation

### Classes

#### Computer
- `start_recording()`: Begin recording session
- `stop_recording()`: End recording, return duration
- `draw(surface)`: Render desk and monitor

#### Video
- `to_dict()`: Convert to JSON-serializable format
- `from_dict(data)`: Reconstruct from JSON
- Fields: title, duration, timestamp, views, likes, description

#### VideoLibrary
- `add_video(title, duration)`: Create and save new video
- `upload_video(index, title, description)`: Upload and earn currency
- `delete_video(index)`: Remove video from library
- `save_videos()`: Persist to JSON
- `load_videos()`: Load from JSON on initialization

#### Home (Updated)
- `computer`: Computer instance positioned at (x+80, y+30)
- `video_library`: VideoLibrary instance for managing videos
- `draw()`: Renders computer with desk

### Game Loop Integration
- `camera_app_open`: Boolean flag tracking app visibility
- `camera_recording`: Boolean flag tracking recording state
- `video_library_view`: Boolean flag for library vs camera view
- Mouse click detection on computer.rect
- Keyboard event handling for all controls
- UI rendering for camera app window

## User Workflow

1. **Access**: Press H to enter home
2. **Open App**: Click on computer monitor
3. **Record**: 
   - See camera app interface
   - Press SPACE to start recording
   - Time counter shows elapsed seconds
   - Press SPACE again to stop
4. **View Library**: Press L to see all videos
5. **Upload**: 
   - Select video (first one highlighted)
   - Press Enter to upload
   - See earnings and view count
   - Video moves to end of list
6. **Manage**: 
   - Delete videos with Delete key
   - Reload library to see changes

## Future Enhancement Ideas

### Potential Additions
- Custom video titles/descriptions before upload
- Video duration limits (e.g., max 5 minutes)
- Video rating/favorites system
- Video sharing with other players
- Video categories/playlists
- Trending videos leaderboard
- Video comments section
- Multi-player video viewing
- Video thumbnails/previews
- Export/download videos

### Performance Considerations
- videos.json remains small (metadata only)
- No video file storage (timestamp-based sim)
- UI renders efficiently with text-based library
- No streaming/networking required

## Testing Checklist

- [ ] Record video and verify time counter
- [ ] Stop recording and verify auto-save
- [ ] View library and verify video appears
- [ ] Upload video and verify currency earned
- [ ] Check videos.json was created/updated
- [ ] Delete video and verify removal
- [ ] Restart game and verify persistence
- [ ] Upload same video multiple times
- [ ] Verify view/like counts generated
- [ ] Verify currency system integration
- [ ] Test house upgrade with computer
- [ ] Test with empty library
- [ ] Test with 6+ videos

## Conclusion

The camera and video system adds a fun meta-game layer to City Car Race, allowing players to:
- Document gameplay moments
- Earn additional currency
- Engage in social media simulation
- Build a video library within the game

The system is fully integrated, persistent, and ready for gameplay!
