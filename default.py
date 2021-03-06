import xbmc, xbmcgui, xbmcplugin, urllib2, urllib, re, string, sys, os, traceback, xbmcaddon

__plugin__ =  'EEVblog'
__author__ = 'Clumsy <clumsy@xbmc.org>'
__date__ = '20-06-2014'
__version__ = '0.2.6'
__settings__ = xbmcaddon.Addon(id='plugin.video.eevblog')

# Thanks to some of the other plugin authors, where I borrowed some ideas from !
EEV_URL='http://www.eevblog.com'

REMOTE_DBG = False

# append pydev remote debugger
if REMOTE_DBG:
  # Make pydev debugger works for auto reload.
  # Note pydevd module need to be copied in XBMC\system\python\Lib\pysrc
  try:
    import pysrc.pydevd as pydevd
  # stdoutToServer and stderrToServer redirect stdout and stderr to eclipse console
    pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True)
  except ImportError:
    sys.stderr.write("Error: " +
      "You must add org.python.pydev.debug.pysrc to your PYTHONPATH.")
    sys.exit(1)
    
def open_url(url):
  req = urllib2.Request(url)
  req.add_header("user-agent","Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)")
  content = urllib2.urlopen(req)
  data = content.read()
  content.close()
  return data

def build_main_directory():
  image = "icon.png"
  listitem = xbmcgui.ListItem(label = "Episode Listing", iconImage = image, thumbnailImage = image)
  u = sys.argv[0] + "?mode=1"
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = u, listitem = listitem, isFolder = True)

def build_episodes_directory():
  url = EEV_URL + '/episodes/'
  data = open_url(url)
  match = re.compile('<body>(.+?)</body>', re.DOTALL).findall(data)
  youtube_url_name = re.compile(r'<a href.?="(.+?)" title="(EEVblog #.+?)">', re.IGNORECASE).findall(match[0])
  for ep_url, name in youtube_url_name:
    listitem = xbmcgui.ListItem(label = name, iconImage = "", thumbnailImage = "")
    #listitem.setInfo( type = "Video", infoLabels = { "Title": name, "Director": __plugin__, "Studio": __plugin__, "Genre": "Video Blog", "Plot": plot[0], "Episode": "" } )
    if ep_url:
      u = sys.argv[0] + "?mode=2&url=" + ep_url + "&name=" + name
      xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = u, listitem = listitem, isFolder = False)
      xbmcplugin.addSortMethod( handle = int(sys.argv[ 1 ]), sortMethod = xbmcplugin.SORT_METHOD_NONE )
    
def clean(name):
  remove = [('&amp;','&'), ('&quot;','"'), ('&#039;','\''), ('\r\n',''), ('&apos;','\''), ('.','')]
  for trash, crap in remove:
    name = name.replace(trash,crap)
  return name
      
def play_video(ep_url):
  xbmc.executebuiltin('ActivateWindow(busydialog)')
  try:
    if ep_url[:22]== EEV_URL:
        ep_data = open_url(ep_url)
    else:
        ep_data = open_url(EEV_URL + ep_url)
    plot = re.compile('<div class="info">.+?<p>(.+?)</p>.', re.DOTALL).findall(ep_data)
    youtube_video_id = re.compile('<param name="movie" value=".*?/v/(.+?)[&\?].').findall(ep_data)
    
    # Ugly hack for a change in the page src from videos 140 onwards. 
    if not youtube_video_id:
      youtube_video_id = re.compile('youtube.com/embed/(.*?)"').findall(ep_data)
  
    # Close the busy waiting dialog, if the youtube url wasn't parsed correctly.
    if not youtube_video_id:
      xbmc.executebuiltin('Dialog.Close(busydialog)')
      return

    url = "plugin://plugin.video.youtube/?path=/root/search&action=play_video&videoid="+youtube_video_id[0]

    listitem = xbmcgui.ListItem(label = name if name else '' , iconImage = 'DefaultVideo.png', thumbnailImage = '')
    listitem.setInfo( type = "Video", infoLabels={ "Title": name, "Director": __plugin__, "Studio": __plugin__, "Genre": genre, "Plot": plot, "Episode": int(0)  } )
  except:
    xbmc.executebuiltin( "Dialog.Close(busydialog)" )
    xbmc.executebuiltin('Notification(Error,Something went wrong,2000)')
    return
  xbmc.Player().play(item=url, listitem=listitem)

def get_params():
  param=[]
  paramstring=sys.argv[2]
  if len(paramstring)>=2:
    params=sys.argv[2]
    cleanedparams=params.replace('?','')
    if (params[len(params)-1]=='/'):
      params=params[0:len(params)-2]
    pairsofparams=cleanedparams.split('&')
    param={}
    for i in range(len(pairsofparams)):
      splitparams={}
      splitparams=pairsofparams[i].split('=')
      if (len(splitparams))==2:
        param[splitparams[0]]=splitparams[1]
                          
  return param

params = get_params()
url = None
name = None
mode = None
page = 1
plot = None
genre = None
episode = None

try:
  url = urllib.unquote_plus(params["url"])
except:
  pass
try:
  name = urllib.unquote_plus(params["name"])
except:
  pass
try:
  mode = int(params["mode"])
except:
  pass
try:
  page = int(params["page"])
except:
  pass
try:
  plot = urllib.unquote_plus(params["plot"])
except:
  pass
try:
  genre = urllib.unquote_plus(params["genre"])
except:
  pass
try:
  episode = int(params["episode"])
except:
  pass

if mode == None:
  build_main_directory()
elif mode == 1:
  build_episodes_directory()
elif mode == 2:
  play_video(url)

try:
  xbmcplugin.addSortMethod( handle = int(sys.argv[ 1 ]), sortMethod = xbmcplugin.SORT_METHOD_NONE )
except:
  pass
try:
  xbmcplugin.endOfDirectory(int(sys.argv[1]))
except:
  pass
