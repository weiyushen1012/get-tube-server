import youtube_dl
import pathlib
import uuid
import time
import os
import logging

from flask import Flask, send_from_directory, request
from threading import Thread
from flask_cors import CORS
from pathlib import Path

application = Flask(__name__)
CORS(application)

video_temp_path = str(pathlib.Path(__file__).parent.absolute()) + "/temp"


def download_tube_to_local(url, video_temp_filename):
    global video_temp_path

    ydl_opts = {'outtmpl': f'{video_temp_path}/{video_temp_filename}'}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def delete_local_video(video_temp_filename, delete_after):
    global video_temp_path
    time.sleep(delete_after)
    logging.info(msg=f'deleting temp file {video_temp_filename}')
    os.remove(f'{video_temp_path}/{video_temp_filename}')


@application.route('/', methods=['GET'])
def home():
    return


@application.route('/download_from_tube', methods=['POST'])
def download_from_tube():
    data = request.get_json()
    url = data['url']
    video_temp_filename = f'{uuid.uuid1()}.mp4'

    download_thread = Thread(target=download_tube_to_local, args=(url, video_temp_filename,))
    download_thread.start()
    download_thread.join()

    delete_video_thread = Thread(target=delete_local_video, args=(video_temp_filename, 310,))
    delete_video_thread.start()

    return {'filename': video_temp_filename}, 200


@application.route('/send_video_file/<video_temp_filename>', methods=['GET'])
def send_video_file(video_temp_filename):
    global video_temp_path

    if not Path(f'{video_temp_path}/{video_temp_filename}').is_file():
        return f'Error: File {video_temp_filename} does not exist.', 404

    delete_video_thread = Thread(target=delete_local_video, args=(video_temp_filename, 20,))
    delete_video_thread.start()

    return send_from_directory(video_temp_path, filename=video_temp_filename, as_attachment=True)


@application.route('/is_temp_file_exists/<video_temp_filename>', methods=['GET'])
def is_temp_file_exists(video_temp_filename):
    if not Path(f'{video_temp_path}/{video_temp_filename}').is_file():
        return f'Error: File {video_temp_filename} does not exist.', 404

    return f'File {video_temp_filename} exists', 200


@application.route('/ping', methods=['GET'])
def ping():
    return 'pong', 200


if __name__ == '__main__':
    application.run()
