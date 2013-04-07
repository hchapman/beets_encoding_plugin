beets_encoding_plugin
=====================
A beetsplug which allows for additional management of mp3s w.r.t. their LAME encoding data.

Presently just adds a $quality preset variable which returns either the format of the track, 
_or_ the format of the track and its encoding preset (e.g. MP3 V0). Presently presets 
are only detected for MP3s with Xing headers.
