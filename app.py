import os
from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route("/")
def home():
    return """<html><head><title>Boom Black</title></head>
<body style='background:#000;color:gold;text-align:center;font-family:Arial;padding:20px'>
<h1>BOOM BLACK 🔥 TikTok Downloader</h1>
<input id='u' placeholder='Paste TikTok link here' style='width:80%;padding:15px;font-size:18px'><br><br>
<button onclick='dl()' style='padding:15px 30px;background:gold;color:black;font-weight:bold;font-size:18px;border:none;cursor:pointer'>DOWNLOAD NOW</button>
<p id='s'></p>
<script>
function dl(){
 let url=document.getElementById('u').value;
 if(!url){alert('Paste link');return;}
 document.getElementById('s').innerText='Loading...';
 fetch('/download?url='+encodeURIComponent(url)).then(r=>r.json()).then(d=>{
  if(d.video_url){ document.getElementById('s').innerHTML='<a href=\"'+d.video_url+'\" style=\"color:gold;font-size:20px\">CLICK TO SAVE VIDEO</a>'; }
  else{ document.getElementById('s').innerText='Error: '+d.error; }
 }).catch(e=>{document.getElementById('s').innerText=e;});
}
</script></body></html>"""

@app.route("/download")
def download():
    url=request.args.get('url','').strip()
    if not url: return jsonify({"error":"No URL"})
    try:
        opts={'quiet':True,'no_warnings':True,'format':'best','noplaylist':True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            info=ydl.extract_info(url, download=False)
            video_url=info.get('url') or info['formats'][-1]['url'] if info.get('formats') else None
            return jsonify({"video_url":video_url,"title":info.get('title')})
    except Exception as e:
        return jsonify({"error":str(e)}),500

if __name__=="__main__":
    app.run(host='0.0.0.0',port=int(os.environ.get("PORT",10000)))
