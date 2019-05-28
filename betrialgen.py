import glob
import os
import ocrolib
from PIL import ImageDraw, Image
import random
import argparse

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(help="subcommands",dest="subparser_name")

p_btgen = subparsers.add_parser("btgen",help="Generates a set for the bernoulli trials out of xml and img files")
p_btgen.add_argument('-p','--path',default='./test/BeTrialGen/input/*.xml')
p_btgen.add_argument('-o','--output',default='./test/BeTrial/input/')
p_btgen.add_argument('-x','--extension',default='jpg')
p_btgen.add_argument('-f','--imgfolder',default='')
p_btgen.add_argument('--minchar',default=3,type=int)
p_btgen.add_argument('--maxcount',default=25, type=int)
p_btgen.add_argument('-l','--toplevel',default="line")

args = parser.parse_args()

### Init ####
#img_extension = "jpg"
#img_path = ""
#maxcount = 30
#mincharlen = 3
#xmlfiles = glob.glob()
#LINEWISE = True


def main(args):
    xmlfiles = glob.glob(args.path)
    count = 0
    while count != args.maxcount:
        xmlfname = xmlfiles[random.randint(0,len(xmlfiles)-1)]
        fbase = xmlfname.rsplit(".",1)[0]
        try:
            #if img_path == "":
            img = Image.open(fbase+"."+args.extension)
        except Exception as e:
            print "No image found! Please put the images in the same folder!"
            continue
        data = ocrolib.get_xml_document(xmlfname, level=args.toplevel)
        if len(data.page) < 2: continue
        lidx = random.randint(0, len(data.page)-1)
        ldata = data.page[lidx]
        charlen = sum([len(word.ocr_text) for word in ldata.words])
        if charlen <= args.minchar: continue
        charidx = random.randint(1, charlen)
        cidx = charidx
        txtline = ""
        wcoords = None
        for word in ldata.words:
            if charidx <= 0 or len(word.ocr_text) < charidx:
                charidx -= len(word.ocr_text)
                txtline += "".join(word.ocr_text)+" "
            else:
                txtline += "".join(word.ocr_text[:charidx-1])+"<@>"+word.ocr_text[charidx-1]+"<@>"+"".join(word.ocr_text[charidx:])+" "
                print(word.ocr_text[charidx-1])
                wcoords = word.coordinates
                charidx = 0
        if args.toplevel == "wordwise":
            draw = ImageDraw.Draw(img)
            draw.rectangle([int(wcoord) for wcoord in wcoords], outline=(230, 50, 120),width=3)
            del draw
        img = img.crop([int(coord) for coord in ldata.coordinates])

        ### STORE IMG & TXT #####
        #fname= os.path.basename(xmlfname).split("_")[0]+"-"+os.path.basename(xmlfname).split("_")[1]+"_"+os.path.basename(xmlfname).split("_")[-1].rsplit(".",1)[0]+"_"+str(lidx)+"_"+str(cidx)
        fname= os.path.basename(xmlfname).split("_")[0]+"_"+os.path.basename(xmlfname).split("_")[-1].rsplit(".",1)[0]+"_"+str(lidx)+"_"+str(cidx)
        img.save(args.output+fname+".png","PNG")
        import codecs
        with codecs.open(args.output+fname+".txt","w","utf-8") as fout:
            fout.write(txtline.strip())
        count += 1

if __name__ == "__main__":
    args.subparser_name = "btgen"
    main(args)
