import youtube_dl
import pathlib
import uuid
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


@app.route('/download_from_tube', methods=['POST'])
def download_from_tube():
    data = request.get_json()
    url = data['url']
    video_temp_filename = f'{uuid.uuid1()}.mp4'

    thread = Thread(target=download_tube_to_local, args=(url, video_temp_filename,))
    thread.start()
    thread.join()

    return {'filename': video_temp_filename}


@app.route('/send_video_file/<video_temp_filename>', methods=['GET'])
def send_video_file(video_temp_filename):
    global video_temp_path
    print(video_temp_path, video_temp_filename)
    return send_from_directory(video_temp_path, filename=video_temp_filename, as_attachment=True)


@app.route('/ping', methods=['GET'])
def ping():
    return 'pong', 200


if __name__ == '__main__':
    app.run(debug=True)
