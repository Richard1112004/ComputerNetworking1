
# use to make .torrent files
#! working 
from torrentool.api import Torrent

# Reading and modifying an existing file.
my_torrent = Torrent.from_file('C:\\Users\\USER\\Downloads\\tam.torrent')
my_torrent.total_size  # Total files size in bytes.
my_torrent.magnet_link  # Magnet link for you.
my_torrent.comment = 'Your torrents are mine.'  # Set a comment.
my_torrent.to_file()  # Save changes.
print()

# Making torrent files
new_torrent = Torrent.create_from('C:\\Users\\USER\\Downloads\\7_DataStorageIndexingStructures (1).pptx')  # or it could have been a single file
new_torrent.announce_urls = 'udp://tracker.openbittorrent.com:80'
new_torrent.to_file('C:\\Users\\USER\\Downloads\\tam.torrent')