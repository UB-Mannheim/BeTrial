#!/usr/bin/env python

from __future__ import print_function

import argparse
import codecs
import re
import os.path
import base64
import urllib2
import glob
from PIL import Image
import io

import btlib

p_betrial = argparse.ArgumentParser()
#subparsers = parser.add_subparsers(help="subcommands",dest="subparser_name")

#p_betrial = subparsers.add_parser("betrial",help="generate a betrial.html")
p_betrial.add_argument('-t','--template',default="./template/template_01.html")
p_betrial.add_argument('-r','--rescale',action="store_true")
p_betrial.add_argument('-d','--debug',action="store_true")
p_betrial.add_argument('-o','--output',default="./test/BeTrial/output/betrial.html")
p_betrial.add_argument('-x','--extension',default='.txt')
p_betrial.add_argument('-f','--fontsize',default=20,type=int)
p_betrial.add_argument('-H','--height',default=24,type=int)
p_betrial.add_argument('-W','--width',default=500,type=int)
p_betrial.add_argument("-M","--maxsize",default=10000,type=int)
p_betrial.add_argument('files',nargs='+')

stream = None

def P(x,*args):
    stream.write(x%args)
    stream.write("\n")

args = p_betrial.parse_args()

def approx_split_range(n,k):
    if n%k==0:
        chunks = [n//k]*k
    else:
        l = n//k+1
        d = n-k*(l-1)
        chunks = [l-1+(i<d) for i in range(k)]
    print(chunks)
    return chunks

def approx_split(l,k):
    chunks = approx_split_range(len(l),k)
    start = 0
    for c in chunks:
        yield l[start:start+c]
        start += c

def url_decode(image):
    prefix = "data:image/png;base64,"
    if image.startswith(prefix):
        data = image[len(prefix):]
        data = base64.b64decode(data)
    else:
        data = urllib2.urlopen(image).read()
    return data

def main(args):
    # ocropus-gtedit html temp/????/??????.bin.png -o temp-correction.html
    if args.files is None:
        files = ["./test/BeTrial/input/*.png"]
    else:
        files = args.files[:]
    for i, fname in enumerate(files):
        #assert not os.path.isabs(fname), "absolute file names not allowed"
        if "*" in fname:
            del args.files[i]
            args.files.extend(sorted(glob.glob(fname)))
    if len(args.files) <= args.maxsize:
        chunks = [(args.output, args.files)]
    else:
        print("# too many lines for one output file; splitting")
        chunks = approx_split(args.files, len(args.files) // args.maxsize)
        base = re.sub(r'\..*?$', '', args.output)
        chunks = [(base + "-%03d" % i + ".html", c) for i, c in enumerate(chunks)]
        chunks[0] = (args.output, chunks[0][1])
    if not os.path.exists(os.path.dirname(args.output)):
        os.makedirs(os.path.dirname(args.output))
    for oname, files in chunks:
        print("# writing", oname)
        if args.template != '':
            template = codecs.open(args.template, "r", "utf-8").read().replace("@TITLE@", os.path.basename(oname))
            stream = codecs.open(oname, "w", "utf-8")
            global stream
            stream.write(template)
            P("<table>")
        else:
            stream = codecs.open(oname, "w", "utf-8")
            global stream
            # P("<!DOCTYPE html>")
            P('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">')
            P("<html>")
            P("<head>")
            P('<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />')
            P('<title>%s</title>', oname)
            P("</head>")
            P("<body>")
        for i, fname in enumerate(args.files):
            base, _ = btlib.allsplitext(fname)
            value = "NA"
            if os.path.exists(base + args.extension):
                text = btlib.read_text(base + args.extension)
                if "<@>" in text:
                    textsplits = text.split("<@>")
                    if len(textsplits) == 3:
                        replacement = "<span style='border:2px solid red'>"
                        value = textsplits[1]
                        text = textsplits[0] + replacement + value + "</span>" + textsplits[2]
            else:
                text = u""
            print(fname)
            with open(fname, "rb") as pngstream:
                png = pngstream.read()

            im = Image.open(io.BytesIO(png))
            im.resize([int(0.5 * s) for s in im.size], Image.ANTIALIAS)
            width, height = im.size
            png = base64.b64encode(png)
            png = "data:image/png;base64," + png
            P("<table>")
            P("<tr><td style='border:0px;color:#808080;font-size:12px'>%s</td></tr>", fname)
            P("<tr><td><img alt='line' src='%s' width='%d' /></td></tr>", png, width)
            P("<tr><td style='font-size:36px'>%s</td></tr>", text)
            P("</table>")
            P("<p />")
            P('<form>')
            name = fname.split("/")[-1].rsplit(".", 1)[0] + "_" + value
            name = name.replace("%","?")
            print(name)
            P('<fieldset style="font-size: 20px;order-bottom: 2px solid black;border-top: 2px solid white;border-left: 2px solid white;border-right: 2px solid white;">')
            P('<input type="radio" id="ok" name="' + name + '" value="ok"><label for="ok"> Ok</label>')
            P('<input type="radio" id="false" name="' + name + '" value="false"><label for="false"> Falsch</label>')
            P(
                '<input type="radio" id="diacritic" name="' + name + '" value="diacritic"><label for="diacritic"> Diakritischer Fehler</label>')
            P(
                '<input type="radio" id="misplaced" name="' + name + '" value="misplaced"><label for="misplaced"> Verschoben</label>')
            P(
                '<input type="radio" id="missing" name="' + name + '" value="missing"><label for="missing"> Fehlt</label>')
            P(
                '<input type="radio" id="tnmi" name="' + name + '" value="tnmi"><label for="tnmi"> Darstellungsfehler</label>')
            P('</fieldset>')
            P('</form>')
        P("</body>")
        P("</html>")
        stream.close()

if __name__ == "__main__" or args.subparser_name=="betrial":
    main(args)



