# Original script https://github.com/duckinator/xchat-mpris2 by Nick Markwell
# Revisions by Kai Huuhko <kai.huuhko@gmail.com>

import xchat, dbus, os

__module_name__ = "xchat-mpris2"
__module_version__ = "0.1"
__module_description__ = "Fetches information from MPRIS2-compliant music players"

bus = dbus.SessionBus()

dbusNamePrefix = 'org.mpris.MediaPlayer2.'
target = None
dbusObj = bus.get_object('org.freedesktop.DBus', '/')
for name in dbusObj.ListNames(dbus_interface='org.freedesktop.DBus'):
    if name.startswith(dbusNamePrefix):
        target = name
        break

assert target is not None

targetObject = bus.get_object(target, '/org/mpris/MediaPlayer2')
mpris = dbus.Interface(targetObject, dbus_interface='org.mpris.MediaPlayer2.Player')
properties = dbus.Interface(targetObject, dbus_interface='org.freedesktop.DBus.Properties')

def status(str):
    xchat.prnt("[%s] %s" % (getPlayerVersion(), str))

# Pass in milliseconds, get (minutes, seconds)
def parseSongPosition(time):
    return getMinutesAndSeconds(time / 1000000)

# Pass in just seconds, get (minutes, seconds)
def getMinutesAndSeconds(seconds):
    return (seconds / 60, seconds % 60)

# Pass in both minutes and seconds
def formatTime(time):
    if time > 0:
        return "%d:%02d" % time
    else:
        return "0:00"

def performAction(action):
    try:
        fn = getattr(mpris, action)
        if fn:
            return fn()
    except dbus.exceptions.DBusException:
        return False

def getProperty(interface, prop):
    try:
        return properties.Get(interface, prop)
    except dbus.exceptions.DBusException:
        return False

def getSongInfo():
    try:
        data = properties.Get("org.mpris.MediaPlayer2.Player", "Metadata", utf8_strings=True)

        titles = data["xesam:title"]
        title = ", ".join(data["xesam:title"]) if isinstance(titles, list) else titles

        albums = data["xesam:album"]
        album = ", ".join(data["xesam:album"]) if isinstance(albums, list) else albums

        artists = data["xesam:artist"]
        artist = ", ".join(data["xesam:artist"]) if isinstance(artists, list) else artists

        pos = getProperty("org.mpris.MediaPlayer2.Player", "Position")
        pos = formatTime(parseSongPosition(pos))
        length = formatTime(parseSongPosition(data["mpris:length"]))
        version = getProperty("org.mpris.MediaPlayer2", "Identity")

        return (artist, title, album, pos, length, version)
    except dbus.exceptions.DBusException:
        return False

def getPlayerVersion():
    try:
        return getProperty("org.mpris.MediaPlayer2", "Identity")
    except dbus.exceptions.DBusException:
        return "DBus Exception"

def mprisPlayerVersion(word, word_eol, userdata):
    xchat.prnt(str(getPlayerVersion()))
    return xchat.EAT_ALL

def mprisNp(word, word_eol, userdata):
    info = getSongInfo()
    if not info == False:
        s = "ME is listening to "
        s = s + info[1]
        if info[0] != "":
            s = s + " by " + info[0]
        if info[2] != "":
            s = s + " [" + info[2] + "]"
        s = s + " [{3}/{4}] with {5}".format(*info)
        xchat.command(s)
    else:
        xchat.prnt("Error in getSongInfo()")
    return xchat.EAT_ALL

def mprisPlay(word, word_eol, userdata):
    try:
        status('Playing')
        performAction('Play')
    except dbus.exceptions.DBusException:
        xchat.prnt("DBus Exception")
        pass
    return xchat.EAT_ALL

def mprisPause(word, word_eol, userdata):
    try:
        status('Paused')
        performAction('Pause')
    except dbus.exceptions.DBusException:
        xchat.prnt("DBus Exception")
        pass
    return xchat.EAT_ALL

def mprisStop(word, word_eol, userdata):
    try:
        status('Stopped')
        performAction('Stop')
    except dbus.exceptions.DBusException:
        xchat.prnt("DBus Exception")
        pass
    return xchat.EAT_ALL

def mprisPrev(word, word_eol, userdata):
    try:
        status('Playing previous song.')
        performAction('Previous')
    except dbus.exceptions.DBusException:
        xchat.prnt("DBus Exception")
        pass
    return xchat.EAT_ALL

def mprisNext(word, word_eol, userdata):
    try:
        status('Playing next song.')
        performAction('Next')
    except dbus.exceptions.DBusException:
        xchat.prnt("DBus Exception")
        pass
    return xchat.EAT_ALL

xchat.prnt("MPRIS2 now playing script initialized")

xchat.prnt("Current media player is %s" % getPlayerVersion())

xchat.prnt("Use /np to send information on the current song to the active channel.")
xchat.prnt("Also provides: /next, /prev, /play, /pause, /stop, /playerversion")
xchat.hook_command("NP",     mprisNp,     help="Usage: NP, send information on current song to the active channel")
xchat.hook_command("NEXT",   mprisNext,   help="Usage: NEXT, play next song")
xchat.hook_command("PREV",   mprisPrev,   help="Usage: PREV, play previous song")
xchat.hook_command("PLAY",   mprisPlay,   help="Usage: PLAY, play the music")
xchat.hook_command("PAUSE",  mprisPause,  help="Usage: PAUSE, pause the music")
xchat.hook_command("STOP",   mprisStop,   help="Usage: STOP, hammer time!")
xchat.hook_command("PLAYERVERSION", mprisPlayerVersion, help="Usage: PLAYERVERSION, version of the media player you are using")
