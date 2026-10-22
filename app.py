import os
from flask import Flask, request, send_from_directory, render_template_string
import yt_dlp

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

HTML = """
<!DOCTYPE html><html><head><title>BOOM BLACK</title>
<style>body{background:#000;color:#fff;text-align:center;font-family:Arial;padding:20px}
input{width:70%;padding:12px;border-radius:10px}button{padding:12px 20px;background:red;color:#fff;border:none;border-radius:10px}
.video{background:#111;margin:10px;padding:10px;border-radius:10px}</style></head>
<body><h1>BOOM BLACK 🔥 V4</h1>
<form method="POST"><input name="url" placeholder="Paste YouTube link" required><button>DOWNLOAD</button></form>
<p>{{ msg }}</p><hr><h2>Your Downloads Gallery</h2>
{% for f in files %}
<div class="video">{{ f }}<br><video width="320" controls><source src="/downloads/{{ f }}"></video><br>
<a href="/downloads/{{ f }}" download>Download</a></div>
{% endfor %}
</body></html>
"""

@app.route("/", methods=["GET","POST"])
def home():
    msg=""
    if request.method=="POST":
        url=request.form.get("url")
        try:
            ydl_opts={'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s','format':'best','cookiefile':'cookies.txt' if os.path.exists('cookies.txt') else None}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            msg="✅ Downloaded!"
        except Exception as e:
            msg=f"❌ Error: {e}"
    files=os.listdir(DOWNLOAD_FOLDER) if os.path.exists(DOWNLOAD_FOLDER) else []
    return render_template_string(HTML, msg=msg, files=files)

@app.route("/downloads/<path:filename>")
def dl(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
