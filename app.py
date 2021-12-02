#app.py
from flask import Flask, request, send_file, render_template, redirect
from pytube import YouTube
from youtube_dl import YoutubeDL
import logging
import sys
import os
from io import BytesIO
from tempfile import TemporaryDirectory
import gunicorn
import uvicorn
import json

print("Server is running :)")
print(".....................")

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

APP_NAME = os.environ.get('APP_NAME')

@app.before_first_request
def initialize():
  print("Initializing...")

@app.route("/")
def runner():
  return {"Stats":"Server Running !!!"}

@app.route("/data",methods=['GET'])
async def get_ytdata():
  video = request.args.get('url')
  print(video)
  youtube_dl_opts={}

  with YoutubeDL(youtube_dl_opts) as ydl:
      info_dict = ydl.extract_info(video, download=False)
      video_url = info_dict.get("url", None)
      video_id = info_dict.get("id", None)
      video_title = info_dict.get('title', None)
      channel_id = info_dict.get('channel_id', None)
      channel = info_dict.get('channel', None)
      like_count = info_dict.get('like_count', None)
      duration = info_dict.get('duration', None)

      total_seconds = duration
      hours = (total_seconds - ( total_seconds % 3600))/3600
      seconds_minus_hours = (total_seconds - hours*3600)
      minutes = (seconds_minus_hours - (seconds_minus_hours % 60) )/60
      seconds = seconds_minus_hours - minutes*60

      time = '{}:{}:{}'.format(int(hours), int(minutes), int(seconds))


      view_count = info_dict.get('view_count', None)
      average_rating = info_dict.get('average_rating', None)
      upload_date = info_dict.get('upload_date', None)
      published_date = "{}-{}-{}".format(upload_date[0:4], upload_date[4:6], upload_date[6:])
      categories = info_dict.get('categories', None)
      thumbnails = info_dict.get('thumbnails', None)
      data = {'data': [{'ID': video_id, 'Title': video_title, 'Published': published_date, 'Duration': time, 'Views': view_count, 'Channel': channel, 'Categories': categories}],'Download_url':[{'audio': 'https://' + APP_NAME + '.herokuapp.com/audio?url='+video}],'Owned by':'DiyRex'}
     
  return data

@app.route("/audio", methods=['GET', 'POST'])
async def download_audio():
    youtube_url = request.args.get('url')
    print(youtube_url)

    with TemporaryDirectory() as tmp_dir:
        print(tmp_dir)
        yt = YouTube(str(youtube_url))
        audio = yt.streams.get_audio_only()
        download_path = audio.download(tmp_dir)

        base, ext = os.path.splitext(download_path)
        new_file = base + '.mp3'
        try:
            os.rename(download_path, new_file)
        except:
            pass

        faudio_name = new_file.split("\\")[-1]
        print(download_path)
        print(faudio_name)
        hpath, audio_name = os.path.split(faudio_name)
        print("filename is : " + audio_name)
        file_bytes = b""
        with open(new_file, "rb") as f:
            file_bytes = f.read()

        return send_file(BytesIO(file_bytes), attachment_filename=audio_name, as_attachment=True), {"Message":"Downlaoding"}

if __name__ == "__main__":
    app.run(threaded=True, port=5000, debug=True, use_reloader=False)
