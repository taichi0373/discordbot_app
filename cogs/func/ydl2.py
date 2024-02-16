import pygame, os, glob, shutil
from yt_dlp import YoutubeDL
from pydub import AudioSegment

class Music():
    def __init__(self, URL):
        self.URL = URL


        
    # ユーザープロフィールを取得
    def download_music(self):        
        export_dir = './downloads/'
        ydl_opts = {
        'format': 'bestaudio/best', #動画の形式や解像度
        'outtmpl': export_dir + '%(title)s.%(ext)s',   #動画の保存先
        'nooverwrites': True,   # 重複ファイルがあった場合にエラーを発生させる
        'postprocessors': [
            {
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',    #ダウンロードした動画をwav形式に変換
            'preferredquality': '192'
            
            }
            ]
        }

        
        try:
            with YoutubeDL(ydl_opts) as ydl:
                res = ydl.extract_info(self.URL, download=False)
                title = res['title'].replace("/", "⧸")

                filename = f"{title}.wav"
                filepath = os.path.join(export_dir, filename)
                if not os.path.exists(filepath):    
                    ydl.download([self.URL])
                    print("ファイルがなかったのでダウンロードします")
            #title = res['title'].replace("/", "⧸")       #タイトル取得  Linuxでは「/」が使えない
            #lower_volume(filename)
            return title
        except:
            return "error"