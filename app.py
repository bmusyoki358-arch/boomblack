from flask import Flask, request, jsonify, send_file
import yt_dlp, os, uuid, re

app = Flask(__name__)

def clean_url(url):
    return url.split('?')[0] if 'tiktok.com' in url else url

@app.route("/")
def home():
    return """
    <h1 style='background:black;color:gold;padding:20px;text-align:center'>BOOM BLACK IS LIVE 🔥</h1>
    <input id=u placeholder='Paste TikTok link' style='width:80%;padding:15px'>
    <button onclick='go()' style='padding:15px;background:gold'>DOWNLOAD</button>
    <script>
    function go(){ fetch('/download?url='+document.getElementById('u').value).then(r=>r.json()).then(d=>{ if(d.video_url) window.location=d.video_url; else alert(d.error) }) }
    </script>
    """

@app.route("/download")
def download():
    url = request.args.get('url','').strip()
    if not url: return jsonify({"error":"No URL"})
    url = clean_url(url)
    try:
        ydl_opts = {'quiet':True,'no_warnings':True,'format':'best','noplaylist':True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({"video_url": info.get('url') or info['formats'][-1]['url'], "title": info.get('title')})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT",10000)))
