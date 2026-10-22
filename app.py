import os
from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)
COOKIE_FILE = "cookies.txt" if os.path.exists("cookies.txt") else None

def get_ydl_opts():
    opts = {
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'extractor_args': {'youtube': {'player_client': ['android','web']}},
        'format': 'best',
    }
    if COOKIE_FILE:
        opts['cookiefile'] = COOKIE_FILE
    return opts

@app.route("/")
def home():
    return """
<html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
<body style="background:black;color:white;text-align:center;padding:15px;font-family:Arial">
<h1 style="color:gold">BOOM BLACK 🔥 V3</h1>
<p>TikTok ✅ YouTube ✅ FB ✅ Insta ✅ Movies ✅</p>
<input id="u" style="width:95%;padding:15px;border-radius:10px;border:none;font-size:18px" placeholder="Paste YouTube/TikTok link">
<br><br>
<button onclick="go()" style="width:95%;padding:15px;background:gold;color:black;font-weight:bold;font-size:20px;border:none;border-radius:10px">GET VIDEO</button>
<div style="margin-top:20px;background:#333;height:30px;border-radius:10px;display:none" id="bar"><div id="b" style="background:gold;height:100%;width:0%;color:black;text-align:center;line-height:30px;font-weight:bold">0%</div></div>
<p id="t"></p>
<div id="r"></div>
<script>
function go(){
 let url=document.getElementById('u').value;
 if(!url){alert('Paste link');return;}
 document.getElementById('bar').style.display='block';
 document.getElementById('b').style.width='20%';
 document.getElementById('t').innerText='Fetching... 20%';
 setTimeout(()=>{document.getElementById('b').style.width='60%';document.getElementById('t').innerText='Getting download link... 60%';},1000);
 fetch('/getlink?url='+encodeURIComponent(url)).then(r=>r.json()).then(d=>{
  document.getElementById('b').style.width='100%';
  document.getElementById('b').innerText='100%';
  if(d.direct_url){
   document.getElementById('t').innerText='Done!';
   document.getElementById('r').innerHTML='<p style="color:#0f0">'+d.title+'</p><a href="'+d.direct_url+'" target="_blank" download style="background:green;color:white;padding:15px;display:block;margin-top:15px;text-decoration:none;border-radius:10px;font-size:20px">✅ DOWNLOAD VIDEO NOW</a><p style="color:#aaa;font-size:12px">If not downloading, long press link -> Save</p>';
  } else {
   document.getElementById('t').innerText='Error: '+d.error;
  }
 }).catch(e=>{document.getElementById('t').innerText='Error: '+e});
}
</script>
</body></html>
"""

@app.route("/getlink")
def getlink():
    url = request.args.get('url','')
    if not url:
        return jsonify({"error":"No URL"})
    try:
        # First try with best format
        with yt_dlp.YoutubeDL(get_ydl_opts()) as ydl:
            info = ydl.extract_info(url, download=False)
            # Find best direct URL
            direct_url = None
            if info.get('url'):
                direct_url = info['url']
            elif info.get('formats'):
                # Get best format with both video and audio
                for f in reversed(info['formats']):
                    if f.get('url'):
                        # Prefer mp4
                        if 'mp4' in str(f.get('ext','')) or 'mp4' in str(f.get('format_id','')):
                            direct_url = f['url']
                            break
                if not direct_url:
                    direct_url = info['formats'][-1]['url']
            
            return jsonify({
                "title": info.get('title','Video'),
                "direct_url": direct_url,
                "thumbnail": info.get('thumbnail','')
            })
    except Exception as e:
        return jsonify({"error": str(e)[:500]})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT",10000)))
