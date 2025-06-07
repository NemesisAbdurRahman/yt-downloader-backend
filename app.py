
from flask import Flask, request, send_file, render_template
import yt_dlp
import os
import uuid
import traceback  # ← added this

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url")
    format_type = request.form.get("format")  # "mp3" or "mp4"

    if not url or not format_type:
        return "Missing URL or format", 400

    # Create unique filename
    video_id = str(uuid.uuid4())
    output_path = os.path.join(DOWNLOAD_FOLDER, f"{video_id}.%(ext)s")

    # yt_dlp options
    if format_type == "mp3":
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'noplaylist': True,
            'nocheckcertificate': True,
        }
        final_ext = 'mp3'
    else:
        ydl_opts = {
            'format': '137+140/bestvideo+bestaudio',
            'outtmpl': output_path,
            'merge_output_format': 'mp4',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferredformat': 'mp4',
            }],
            'quiet': True,
            'noplaylist': True,
            'nocheckcertificate': True,
        }
        final_ext = 'mp4'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        file_path = os.path.join(DOWNLOAD_FOLDER, f"{video_id}.{final_ext}")

        return send_file(file_path, as_attachment=True)

    except Exception as e:
        traceback.print_exc()  # ← this will print full error to logs
        return f"Download failed: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
