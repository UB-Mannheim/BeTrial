from bs4 import BeautifulSoup
import requests
import random
import os
import argparse

p_fgetter = argparse.ArgumentParser()
#subparsers = parser.add_subparsers(help="subcommands",dest="subparser_name")

#p_fgetter = subparsers.add_parser("fgetter",help="Generates a set for the bernoulli trials out of xml and img files")
p_fgetter.add_argument('--url',default='')
p_fgetter.add_argument('-o','--outdir',default="./test/BeTrialGen/input/???/")
p_fgetter.add_argument('-x','--extension',default='xml')
p_fgetter.add_argument('--amount',default=525,type=int)

args = p_fgetter.parse_args()

def scrap_furls(url, ext=''):
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html.parser')
    ret = [node.string for node in soup.find_all('a') if node.string[-1] == "/" and node.string.split("_")[-1][0] == "1" and int(node.string.split("_")[-1][:4]) == 1931]
    furls = []
    for dir in ret:
        page = requests.get(url+dir+"abbyy/").text
        soup = BeautifulSoup(page, 'html.parser')
        furls.extend([url+dir+"abbyy/"+node.string for node in soup.find_all('a') if
               "."+ext in node.string])
        if len(furls) > 5000: break
    return furls

def select_furls(furls,amount):
    furls_sel = []
    while len(furls_sel) < amount:
        furls_sel.append(furls[random.randint(0,len(furls)-1)])
    return furls_sel

def dl_files(furls_sel,outdir):
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    for furl in furls_sel:
        r = requests.get(furl, allow_redirects=True)
        year = furl.split("/")[-3].split("_")[-1][:4]
        open(outdir+year+"_"+os.path.basename(furl), 'wb').write(r.content)
        imgurl = furl.replace("/abbyy/", "/max/").replace(".xml", ".jpg")
        r = requests.get(imgurl, allow_redirects=True)
        open(outdir +year+"_"+os.path.basename(imgurl), 'wb').write(r.content)

def main(args):
    furls = scrap_furls(args.url, args.extension)
    furls_sel = select_furls(furls, args.amount)
    dl_files(furls_sel, args.outdir)
    return 0

if __name__ == "__main__":
    main(args)



