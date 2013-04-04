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

def get_item_quality(item):
    preset = None
    if item.format == u'MP3':
        audio_file = core.load(item.path)
        lt = audio_file.info.lame_tag
        if not audio_file or not audio_file.info.lame_tag:
            pass
        elif lt.has_key('preset'):
            preset = lt['preset']
    return {"preset": preset,
            "bitrate": item.bitrate,
            "format": item.format}

def get_album_quality(album):
    formats = []
    bitrates = []
    presets = []
    for track in album.items():
        q = get_item_quality(track)
        presets.append(q["preset"])
        formats.append(q["format"])
        bitrates.append(q["bitrate"])
    return {"bitrate": sum(bitrates)/len(bitrates),
            "format": formats[0] if formats.count(formats[0]) == len(formats) else "Mutt",
            "preset": presets[0] if presets.count(presets[0]) == len(presets) else "Mutt"}

fmt_cmd = ui.Subcommand('fmt', help="do some format nonsense")
def fmt(lib, opts, args):
    threads = 3
    ui.commands.list_items(lib, ui.decargs(args), opts.album, None)
    if opts.album:
        albums = lib.albums(ui.decargs(args))
    else:
        albums = []
        items = lib.items(ui.decargs(args))
    
    # Try to determine the quality of the album
    if albums:
        for album in albums:
            print album.album
            print get_album_quality(album)
            print _tmpl_quality(album.items().next())
    elif items:
        for item in items:
            print item.title
            print get_item_quality(item)
            print _tmpl_quality(item)

fmt_cmd.func = fmt
fmt_cmd.parser.add_option("-a", "--album", action="store_true", help="poop")

class QualityTrumper(BeetsPlugin):
    def commands(self):
        return [fmt_cmd]

@QualityTrumper.template_field('quality')
def _tmpl_quality(item):
    """Expand to the encode quality of the track. Anything but MP3s
    will expand to their media type (e.g. FLAC, AAC), or Mutt if they
    are a combination of multiple formats. MP3s will expand to 'MP3
    $preset', where $preset is the LAME preset, Mutt if the album
    consists of multiple presets, or None if the album has no preset
    data.
    """
    if item.album:
        q = get_item_quality(item)
    else:
        q = get_item_quality(item)

    if q["format"] == u'MP3':
        return u"MP3 %s"%("None" if not q["preset"] else q["preset"])
    else:
        return u"None" if not q["format"] else q["format"]
