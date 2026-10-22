import os
from flask import Flask, request, send_from_directory, render_template_string, jsonify
import yt_dlp

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Global status for % bar
download_status = {"status": "idle", "percent": "0%", "speed": "", "title": ""}

def progress_hook(d):
    global download_status
    if d['status'] == 'downloading':
        download_status['status'] = 'downloading'
        download_status['percent'] = d.get('_percent_str', '0%').strip()
        download_status['speed'] = d.get('_speed_str', '')
        download_status['title'] = d.get('info_dict', {}).get('title', '')[:40]
    elif d['status'] == 'finished':
        download_status['status'] = 'finished'
        download_status['percent'] = '100%'
        download_status['speed'] = 'Done'

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BOOM BLACK 🔥</title>
<style>
body{background:#000;color:#fff;text-align:center;font-family:Arial;padding:15px}
input{width:75%;padding:14px;border-radius:12px;border:none;font-size:16px}
button{padding:14px 25px;background:#ff0000;color:#fff;border:none;border-radius:12px;font-weight:bold;margin-left:5px}
#progressBox{display:none;background:#111;border:1px solid #333;padding:15px;border-radius:12px;margin:15px auto;max-width:500px}
#barBg{width:100%;background:#333;height:22px;border-radius:10px;overflow:hidden}
#bar{width:0%;height:100%;background:linear-gradient(90deg, red, orange);transition:width 0.3s}
.video{background:#111;margin:12px auto;padding:10px;border-radius:12px;max-width:400px}
video{width:100%;border-radius:8px}
.msg{color:#0f0;margin:10px}
</style>
</head>
<body>
<h1>BOOM BLACK 🔥 V4</h1>
<form method="POST" onsubmit="startPoll()">
<input name="url" id="urlInput" placeholder="Paste YouTube link here" required>
<button>DOWNLOAD</button>
</form>

<div id="progressBox">
<h3 id="titleText">Downloading...</h3>
<div id="barBg"><div id="bar"></div></div>
<p id="percentText">0%</p><p id="speedText"></p>
</div>

<p class="msg">{{ msg }}</p>
<hr>
<h2>Your Downloads Gallery</h2>
{% for f in files %}
<div class="video">{{ f }}<br>
<video controls><source src="/downloads/{{ f }}"></video><br>
<a href="/downloads/{{ f }}" download style="color:red">⬇ Download File</a>
</div>
{% endfor %}

<script>
let polling;
function startPoll(){
 document.getElementById('progressBox').style.display='block';
 polling = setInterval(async ()=>{
  let r = await fetch('/status');
  let j = await r.json();
  document.getElementById('percentText').innerText = j.percent + ' - ' + j.speed;
  document.getElementById('titleText').innerText = j.title || 'Downloading...';
  let p = parseFloat(j.percent) || 0;
  document.getElementById('bar').style.width = p + '%';
  if(j.status=='finished'){ clearInterval(polling); document.getElementById('titleText').innerText='✅ Finished! Reload page'; }
 }, 600);
}
</script>
</body>
</html>
"""

@app.route("/", methods=["GET","POST"])
def home():
    global download_status
    msg=""
    if request.method=="POST":
        url=request.form.get("url")
        download_status = {"status":"downloading","percent":"0%","speed":"Starting...","title":"Starting"}
        try:
            ydl_opts={
                'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestaudio/best',
                'merge_output_format': 'mp4',
                'noplaylist': True,
                'progress_hooks': [progress_hook],
                'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
                'extractor_args': {'youtube': {'player_client': ['android','web']}},
                'quiet': True,
                'no_warnings': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            msg="✅ Downloaded! Scroll down to gallery"
            download_status['status']='finished'
        except Exception as e:
            msg=f"❌ Error: {e}"
            download_status={'status':'error','percent':'0%','speed':str(e),'title':'Error'}
    files=sorted(os.listdir(DOWNLOAD_FOLDER), reverse=True) if os.path.exists(DOWNLOAD_FOLDER) else []
    return render_template_string(HTML, msg=msg, files=files)

@app.route("/status")
def status():
    return jsonify(download_status)

@app.route("/downloads/<path:filename>")
def dl(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
