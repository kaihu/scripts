#!/usr/bin/env python2
#
# Original script https://bitbucket.org/whitelynx/pymprisr by David Bronke
# Revisions by Kai Huuhko <kai.huuhko@gmail.com>

import sys
import dbus

bus = dbus.SessionBus()

dbusNamePrefix = 'org.mpris.MediaPlayer2.'
target = None
dbusObj = bus.get_object('org.freedesktop.DBus', '/')
for name in dbusObj.ListNames(dbus_interface='org.freedesktop.DBus'):
    if name.startswith(dbusNamePrefix):
        print("Found media player: %s" % name[len(dbusNamePrefix):])
        target = name
        break

assert target is not None

targetObject = bus.get_object(target, '/org/mpris/MediaPlayer2')
mpris = dbus.Interface(targetObject, dbus_interface='org.mpris.MediaPlayer2.Player')
properties = dbus.Interface(targetObject, dbus_interface='org.freedesktop.DBus.Properties')

cmd = None
if len(sys.argv) > 1:
    cmd = sys.argv[1]
if len(sys.argv) > 2:
    args = sys.argv[2:]

if cmd == 'toggleplay':
    mpris.PlayPause()
elif cmd == 'play':
    mpris.Play()
elif cmd == 'pause':
    mpris.Pause()
elif cmd == 'stop':
    mpris.Stop()
elif cmd == 'next':
    mpris.Next()
elif cmd == 'previous':
    mpris.Previous()
elif cmd == 'seekto':
    mpris.Seek(args[0])
elif cmd == 'set':
    print(str(args[0]), str(args[1]))
    if args[0] == "Shuffle":
        args[1] = int(args[1])
    properties.Set('org.mpris.MediaPlayer2.Player', args[0], args[1])
else:
    props = properties.GetAll('org.mpris.MediaPlayer2.Player')
    props = dict(**props)
    metadata = props['Metadata']
    print("Now playing %s by %s from %s at pos %i" % (metadata["xesam:title"], metadata["xesam:artist"], metadata["xesam:album"], props["Position"]))
