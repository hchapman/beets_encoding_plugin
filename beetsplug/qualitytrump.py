from beets.plugins import BeetsPlugin
from beets import ui, util
from beets import config

from eyed3 import core

from pprint import pprint

# Source: hydrogenaudio.org's LAME article
mp3_br_ranges = {"320": (320, 320),
                 "v0": (220, 260),
                 "v2": (170, 210),
                 "bigv0": (220, 319)}
def guess_bitrate(abr):
    for bitrate, rng in mp3_br_ranges.iteritems():
        if abr >= rng[0] and abr <= rng[1]:
            return bitrate
    return "???"

def f():
    while True:
        item = yield
        print item

fmt_cmd = ui.Subcommand('fmt', help="do some format nonsense")
def fmt(lib, opts, args):
    threads = 3
    ui.commands.list_items(lib, ui.decargs(args), opts.album, None)
    if opts.album:
        albums = lib.albums(ui.decargs(args))
    else:
        items = lib.items(ui.decargs(args))
    
    # Try to determine the quality of the album
    if albums:
        for album in albums:
            formats = []
            bitrates = []
            presets = []
            for track in album.items():
                if track.format == u'MP3':
                    audio_file = core.load(track.path)
                    lt = audio_file.info.lame_tag
                    if not audio_file or not audio_file.info.lame_tag:
                        presets.append(None)
                    elif lt.has_key('preset'):
                        preset = lt['preset']
                        presets.append(preset)
                formats.append(track.format)
                bitrates.append(track.bitrate)
            print
            print album.album
            print formats
            print bitrates
            print "======="
            album_is_mp3 = False
            if formats.count(formats[0]) == len(formats):
                print "The album is %s encoded" %formats[0]
                album_is_mp3 = formats[0] == "MP3"
            else:
                print "This is a mutt: format mismatch"
                print formats
            if album_is_mp3:
                abr = sum(bitrates)/len(bitrates)
                print "The average bitrate of the mp3s is %s"%abr
                print "It was probably encoded as %s"%guess_bitrate(abr/1000)
                if presets.count(presets[0]) == len(presets):
                    if presets[0]:
                        print "LAME header says it was encoded with preset %s"%presets[0]
                    else:
                        print "No LAME header or not encoded with a preset"
                else:
                    print "This is a mutt: preset mismatch"
                    print presets

fmt_cmd.func = fmt
fmt_cmd.parser.add_option("-a", "--album", action="store_true", help="poop")

class QualityTrumper(BeetsPlugin):
    def commands(self):
        return [fmt_cmd]
