# Copyright (C) 2005  Michael Urman
# -*- coding: utf-8 -*-
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of version 2 of the GNU General Public License as
# published by the Free Software Foundation.

import warnings

from mutagen._util import DictMixin, loadfile
from mutagen._compat import izip


class FileType(DictMixin):
    """An abstract object wrapping tags and audio stream information.

    Attributes:

    * info -- :class:`StreamInfo` -- (length, bitrate, sample rate)
    * tags -- :class:`Tags` -- metadata tags, if any

    Each file format has different potential tags and stream
    information.

    FileTypes implement an interface very similar to Metadata; the
    dict interface, save, load, and delete calls on a FileType call
    the appropriate methods on its tag data.
    """

    __module__ = "mutagen"

    info = None
    tags = None
    filename = None
    _mimes = ["application/octet-stream"]

    def __init__(self, *args, **kwargs):
        if not args and not kwargs:
            warnings.warn("FileType constructor requires a filename",
                          DeprecationWarning)
        else:
            self.load(*args, **kwargs)

    def load(self, filename, *args, **kwargs):
        raise NotImplementedError

    def __getitem__(self, key):
        """Look up a metadata tag key.

        If the file has no tags at all, a KeyError is raised.
        """

        if self.tags is None:
            raise KeyError(key)
        else:
            return self.tags[key]

    def __setitem__(self, key, value):
        """Set a metadata tag.

        If the file has no tags, an appropriate format is added (but
        not written until save is called).
        """

        if self.tags is None:
            self.add_tags()
        self.tags[key] = value

    def __delitem__(self, key):
        """Delete a metadata tag key.

        If the file has no tags at all, a KeyError is raised.
        """

        if self.tags is None:
            raise KeyError(key)
        else:
            del(self.tags[key])

    def keys(self):
        """Return a list of keys in the metadata tag.

        If the file has no tags at all, an empty list is returned.
        """

        if self.tags is None:
            return []
        else:
            return self.tags.keys()

    def delete(self, filename=None):
        """Remove tags from a file.

        In cases where the tagging format is independent of the file type
        (for example `mutagen.ID3`) all traces of the tagging format will
        be removed.
        In cases where the tag is part of the file type, all tags and
        padding will be removed.

        The tags attribute will be cleared as well if there is one.

        Does nothing if the file has no tags.

        :raises mutagen.MutagenError: if deleting wasn't possible
        """

        if self.tags is not None:
            if filename is None:
                filename = self.filename
            else:
                warnings.warn(
                    "delete(filename=...) is deprecated, reload the file",
                    DeprecationWarning)
            return self.tags.delete(filename)

    def save(self, filename=None, **kwargs):
        """Save metadata tags.

        :raises mutagen.MutagenError: if saving wasn't possible
        """

        if filename is None:
            filename = self.filename
        else:
            warnings.warn(
                "save(filename=...) is deprecated, reload the file",
                DeprecationWarning)

        if self.tags is not None:
            return self.tags.save(filename, **kwargs)

    def pprint(self):
        """Print stream information and comment key=value pairs."""

        stream = "%s (%s)" % (self.info.pprint(), self.mime[0])
        try:
            tags = self.tags.pprint()
        except AttributeError:
            return stream
        else:
            return stream + ((tags and "\n" + tags) or "")

    def add_tags(self):
        """Adds new tags to the file.

        :raises mutagen.MutagenError: if tags already exist or adding is not
            possible.
        """

        raise NotImplementedError

    @property
    def mime(self):
        """A list of mime types"""

        mimes = []
        for Kind in type(self).__mro__:
            for mime in getattr(Kind, '_mimes', []):
                if mime not in mimes:
                    mimes.append(mime)
        return mimes

    @staticmethod
    def score(filename, fileobj, header):
        """Returns a score for how likely the file can be parsed by this type.

        Args:
            filename (path): a file path
            fileobj: a file object open in rb mode. Position is undefined
            header (bytes): data of undefined length, starts with the start of
                the file.

        Returns:
            int: negative if definitely not a matching type, otherwise a score,
                the bigger the more certain that the file can be loaded.
        """

        raise NotImplementedError


class StreamInfo(object):
    """Abstract stream information object.

    Provides attributes for length, bitrate, sample rate etc.

    See the implementations for details.
    """

    __module__ = "mutagen"

    def pprint(self):
        """Print stream information"""

        raise NotImplementedError


@loadfile(method=False)
def File(filething, options=None, easy=False):
    """File(filename, options=None, easy=False)

    Guess the type of the file and try to open it.

    The file type is decided by several things, such as the first 128
    bytes (which usually contains a file type identifier), the
    filename extension, and the presence of existing tags.

    If no appropriate type could be found, None is returned.

    Args:
        filename: A filename or file-like object
        options: Sequence of :class:`FileType` implementations,
            defaults to all included ones.
        easy (bool):  If the easy wrappers should be returnd if available.
            For example :class:`EasyMP3 <mp3.EasyMP3>` instead of
            :class:`MP3 <mp3.MP3>`.

    Returns:
        FileType: A FileType instance for the detected type or `None` in case
            the type couln't be determined.

    Raises:
        MutagenError: in case the detected type fails to load the file.
    """

    if options is None:
        from mutagen.asf import ASF
        from mutagen.apev2 import APEv2File
        from mutagen.flac import FLAC
        if easy:
            from mutagen.easyid3 import EasyID3FileType as ID3FileType
        else:
            from mutagen.id3 import ID3FileType
        if easy:
            from mutagen.mp3 import EasyMP3 as MP3
        else:
            from mutagen.mp3 import MP3
        from mutagen.oggflac import OggFLAC
        from mutagen.oggspeex import OggSpeex
        from mutagen.oggtheora import OggTheora
        from mutagen.oggvorbis import OggVorbis
        from mutagen.oggopus import OggOpus
        if easy:
            from mutagen.trueaudio import EasyTrueAudio as TrueAudio
        else:
            from mutagen.trueaudio import TrueAudio
        from mutagen.wavpack import WavPack
        if easy:
            from mutagen.easymp4 import EasyMP4 as MP4
        else:
            from mutagen.mp4 import MP4
        from mutagen.musepack import Musepack
        from mutagen.monkeysaudio import MonkeysAudio
        from mutagen.optimfrog import OptimFROG
        from mutagen.aiff import AIFF
        from mutagen.aac import AAC
        from mutagen.smf import SMF
        options = [MP3, TrueAudio, OggTheora, OggSpeex, OggVorbis, OggFLAC,
                   FLAC, AIFF, APEv2File, MP4, ID3FileType, WavPack,
                   Musepack, MonkeysAudio, OptimFROG, ASF, OggOpus, AAC,
                   SMF]

    if not options:
        return None

    fileobj = filething.fileobj

    try:
        header = fileobj.read(128)
    except IOError:
        header = b""

    # Sort by name after score. Otherwise import order affects
    # Kind sort order, which affects treatment of things with
    # equals scores.
    results = [(Kind.score(filething.name, fileobj, header), Kind.__name__)
               for Kind in options]

    results = list(izip(results, options))
    results.sort()
    (score, name), Kind = results[-1]
    if score > 0:
        try:
            fileobj.seek(0, 0)
        except IOError:
            pass
        return Kind(fileobj)
    else:
        return None
