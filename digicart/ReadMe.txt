Install VLC. This program has hooks into a standard VLC installation and uses VLC codecsto playback


Configuration is in Player.config

HOST
Music Player mounts to the first IP address on the PC. If there are multiple IP addresses, uncomment HOST and add the IP to listen to.

PORT
Supports listening on one or more ports. This allows multiple devices to send commands to a shared device. Multiple ports should be comma separated. Formatting is important. Don't add a trailing comma
Example:
PORTS = 8000
PORTS = 8001,8002


#//*** Music Folder Path
The Music path defaults to a Music subfolder. This can be changed, but recommend leaving it as is.

#//*** Music File Types
VLC can play many media types. To filter it down, add comma separated filetypes here. These are the files the program will make available. Only use applicable file extension types.
music_file_types= .mp3,.wav,.aiff

There is basic capability to play video. It's rough. It's been ignored but it's there. 
video_file_types= .mp4


File Naming
All Music Files are placed in the Music folder. The filename determines the Digicart cut number. Files must adopt the following format

'Folder_Directory_Cut Filename (with no Underscores (_)' <--- The space between Folder_Directory_Cut is important
Example:
'1_0_0 Llama.mp3' - Digicart Drive 1, Directory 0, Cut 0

Playlist Folders
If a folder is made using the Folder_Directory_Cut Methodology, all music placed in the folder will be collected into a playlist. Every time the folder is called via digicart the next song is cued and played. This allows for different music cuts to be played with the same Digicart command. This is a great way to add variety and consistency to a show. 


Keyboard Controls for manual control and Testing.
Up/Down:    Prev/Next Track
Right/Left: Prev/Next Playlist Item
Space:      Play/Pause
ESC:        Quit 