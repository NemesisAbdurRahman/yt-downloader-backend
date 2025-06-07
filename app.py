from flask import Flask, request, send_file, render_template
import yt_dlp
import os
import uuid

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

    # Safe yt_dlp options
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
                'preferedformat': 'mp4',
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
        
        # Return the file to user without saving permanently
        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return f"Download failed: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True)

