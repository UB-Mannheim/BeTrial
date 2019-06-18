# -*- coding: utf-8 -*-
################################################################
### common functions for data structures, file name manipulation, etc.
################################################################

from __future__ import print_function

import os
import os.path
import re
import sys
import unicodedata
import inspect
import glob
from btlib.exceptions import FileNotFound
from toplevel import checks
import chars
import codecs

pickle_mode = 2


################################################################
# text normalization
################################################################

def normalize_text(s):
    """Apply standard Unicode normalizations for OCR.
    This eliminates common ambiguities and weird unicode
    characters."""
    s = unicode(s)
    s = unicodedata.normalize('NFC',s)
    s = re.sub(ur'\s+(?u)',' ',s)
    s = re.sub(ur'\n(?u)','',s)
    s = re.sub(ur'^\s+(?u)','',s)
    s = re.sub(ur'\s+$(?u)','',s)
    for m,r in chars.replacements:
        s = re.sub(unicode(m),unicode(r),s)
    return s

################################################################
### Text I/O
################################################################

def read_text(fname,nonl=1,normalize=1):
    """Read text. This assumes files are in unicode.
    By default, it removes newlines and normalizes the
    text for OCR processing with `normalize_text`"""
    with codecs.open(fname,"r","utf-8") as stream:
        result = stream.read()
    if nonl and len(result)>0 and result[-1]=='\n':
        result = result[:-1]
    if normalize:
        result = normalize_text(result)
    return result

def write_text(fname,text,nonl=0,normalize=1):
    """Write text. This assumes files are in unicode.
    By default, it removes newlines and normalizes the
    text for OCR processing with `normalize_text`"""
    if normalize:
        text = normalize_text(text)
    with codecs.open(fname,"w","utf-8") as stream:
        stream.write(text)
        if not nonl and (len(text) == 0 or text[-1] != '\n'):
            stream.write('\n')

################################################################
### Image I/O
################################################################

################################################################
### file name manipulation
################################################################

@checks(str,_=str)
def findfile(name,error=1):
    result = ocropus_find_file(name)
    return result

@checks(str)
def finddir(name):
    """Find some OCRopus-related resource by looking in a bunch off standard places.
    (This needs to be integrated better with setup.py and the build system.)"""
    local = os.getcwd()
    path = name
    if os.path.exists(path) and os.path.isdir(path): return path
    path = local+name
    if os.path.exists(path) and os.path.isdir(path): return path
    _,tail = os.path.split(name)
    path = tail
    if os.path.exists(path) and os.path.isdir(path): return path
    path = local+tail
    if os.path.exists(path) and os.path.isdir(path): return path
    raise FileNotFound("file '"+path+"' not found in . or /usr/local/share/ocropus/")

@checks(str)
def allsplitext(path):
    """Split all the pathname extensions, so that "a/b.c.d" -> "a/b", ".c.d" """
    match = re.search(r'((.*/)*[^.]*)([^/]*)',path)
    if not match:
        return path,""
    else:
        return match.group(1),match.group(3)

@checks(str)
def base(path):
    return allsplitext(path)[0]

@checks(str,{str,unicode})
def write_text_simple(file,s):
    """Write the given string s to the output file."""
    with open(file,"w") as stream:
        if type(s)==unicode: s = s.encode("utf-8")
        stream.write(s)

@checks([str])
def glob_all(args):
    """Given a list of command line arguments, expand all of them with glob."""
    result = []
    for arg in args:
        if arg[0]=="@":
            with open(arg[1:],"r") as stream:
                expanded = stream.read().split("\n")
            expanded = [s for s in expanded if s!=""]
        else:
            expanded = sorted(glob.glob(arg))
        if len(expanded)<1:
            raise FileNotFound("%s: expansion did not yield any files"%arg)
        result += expanded
    return result

@checks([str])
def expand_args(args):
    """Given a list of command line arguments, if the
    length is one, assume it's a book directory and expands it.
    Otherwise returns the arguments unchanged."""
    if len(args)==1 and os.path.isdir(args[0]):
        return sorted(glob.glob(args[0]+"/????/??????.png"))
    else:
        return args

################################################################
### Utility for setting "parameters" on an object: a list of keywords for
### changing instance variables.
################################################################

################################################################
### warning and logging
################################################################

def caller():
    """Just returns info about the caller in string for (for error messages)."""
    frame = sys._getframe(2)
    info = inspect.getframeinfo(frame)
    result = "%s:%d (%s)"%(info.filename,info.lineno,info.function)
    del frame
    return result

def die(message,*args):
    """Die with an error message."""
    message = message%args
    message = caller()+" FATAL "+message+"\n"
    sys.stderr.write(message)
    sys.exit(1)

def warn(message,*args):
    """Give a warning message."""
    message = message%args
    message = caller()+" WARNING "+message+"\n"
    sys.stderr.write(message)

already_warned = {}

def warn_once(message,*args):
    """Give a warning message, but just once."""
    c = caller()
    if c in already_warned: return
    already_warned[c] = 1
    message = message%args
    message = c+" WARNING "+message+"\n"
    sys.stderr.write(message)

def quick_check_page_components(page_bin,dpi):
    """Quickly check whether the components of page_bin are
    reasonable.  Returns a value between 0 and 1; <0.5 means that
    there is probably something wrong."""
    return 1.0

def quick_check_line_components(line_bin,dpi):
    """Quickly check whether the components of line_bin are
    reasonable.  Returns a value between 0 and 1; <0.5 means that
    there is probably something wrong."""
    return 1.0

################################################################
### loading and saving components
################################################################
