import youtube_dl
import pathlib
import uuid
import time
import os
import logging

from flask import Flask, send_from_directory, request
from threading import Thread
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

video_temp_path = str(pathlib.Path(__file__).parent.absolute()) + "/temp"


def download_tube_to_local(url, video_temp_filename):
    global video_temp_path

    ydl_opts = {'outtmpl': f'{video_temp_path}/{video_temp_filename}'}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def delete_local_video(video_temp_filename):
    global video_temp_path
    time.sleep(20)
    logging.info(msg=f'deleting temp file {video_temp_filename}')
    os.remove(f'{video_temp_path}/{video_temp_filename}')


@app.route('/download_from_tube', methods=['POST'])
def download_from_tube():
    data = request.get_json()
    url = data['url']
    video_temp_filename = f'{uuid.uuid1()}.mp4'

    download_thread = Thread(target=download_tube_to_local, args=(url, video_temp_filename,))
    download_thread.start()
    download_thread.join()

    return {'filename': video_temp_filename}


@app.route('/send_video_file/<video_temp_filename>', methods=['GET'])
def send_video_file(video_temp_filename):
    global video_temp_path

    delete_video_thread = Thread(target=delete_local_video, args=(video_temp_filename,))
    delete_video_thread.start()

    return send_from_directory(video_temp_path, filename=video_temp_filename, as_attachment=True)


@app.route('/ping', methods=['GET'])
def ping():
    return 'pong', 200


if __name__ == '__main__':
    app.run(debug=True)
