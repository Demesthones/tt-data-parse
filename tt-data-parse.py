import json
import yt_dlp
import os
import re
from typing import Optional, Dict, Any
from datetime import datetime
from alive_progress import alive_bar

class TTDataDownloader:
    def __init__(self, path):
            self.path = path
            self.create_save_directory()

    #Create directory to save downloaded videos
    def create_save_directory(self) -> None:
            if not os.path.exists(self.path):
                os.makedirs(self.path)

    #Validate that URL is a Tiktok video
    @staticmethod
    def validate_url(url: str) -> bool:
        tiktok_pattern = r'https?://((?:vm|vt|www)\.)?tiktok\.com/.*'
        return bool(re.match(tiktok_pattern, url))

    #Generate the filename for a given video
    def get_filename(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"tiktok_{timestamp}.mp4"

    #Call yt-dlp to download video
    def download_video(self, video_url):

            filename = self.get_filename()
            output_path = os.path.join(self.path, filename)
            
            #yt-dlp opts
            ydl_opts = {
                'outtmpl': output_path,
                'format': 'best',
                'noplaylist': True,
                'quiet': True,
                'extractor_args': {'tiktok': {'webpage_download': True}},
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            }

            #Attempt to download video
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
            #Catch errors
            except yt_dlp.utils.DownloadError as e:
                print(f"Error downloading video: {str(e)}")
            except Exception as e:
                print(f"An unexpected error occurred: {str(e)}")
            
            return None

def main():
    #Detect if data file exists in the same directory
    if(os.path.exists("user_data_tiktok.json")):
         print("Data file detected...")
         filepath = "user_data_tiktok.json"
    #Prompt user for path to data if not detected
    else:
        print("Data file not detected...")
        filepath = input("Enter path to data (.json file): ")
        if filepath[0] == '"':
            filepath = filepath [1: -1]
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    #Pull data from file for favorite videos, followers, and following users
    fav_vids = (data["Activity"]["Favorite Videos"]["FavoriteVideoList"])
    follower_list = (data["Activity"]["Follower List"]["FansList"])
    following_list = (data["Activity"]["Following List"]["Following"])

    #Prompt user to save followers/following users
    s = input("Save follower/follwing lists? Y/N: ")
    if(s == "Y" or s == "y"):
        save_list(follower_list, 'follower_list.csv')
        save_list(following_list, 'following_list.csv')

    #Prompt user to download favorite videos
    s = input("Download Favorites (" + str(len(fav_vids)) + ")? Y/N: ")
    if(s == "Y" or s == "y"):
        #Save each video in the favorites list
        #Update progress bar with each video
        title_str = "Downloading Favorites (" + str(len(fav_vids))+ ")..."
        with alive_bar(len(fav_vids), title=title_str, bar='smooth') as bar:
            for item in save_videos(fav_vids, 'TTData/downloaded_favorites'):
                bar()

#Save list of followers/following users
def save_list(data, filename):
    count = 0
    output = ""
    for i in data:
        if(count > 0):
                output += ","
        output += i["UserName"]
        count += 1
    
    f = open(filename, 'w')
    f.write(output)
    f.close()

#Call downloader for each video
def save_videos(data, path):
    for item in data:
        downloader = TTDataDownloader(path)
        downloader.download_video(item["Link"])
        yield

main()
