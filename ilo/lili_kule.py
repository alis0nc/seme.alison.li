# image dithering script
# 2025: modified by seme Alison
# © 2022 Roel Roscam Abbing, released as AGPLv3
# see https://www.gnu.org/licenses/agpl-3.0.html
# Support your local low-tech magazine: https://solar.lowtechmagazine.com/donate.html 

import hitherdither
import os
import argparse
import shutil
from PIL import Image
import logging

parser = argparse.ArgumentParser(
    """
    This script recursively traverses folders and creates dithered versions of the images it finds.
    These are stored in the same folder as the images in a folder called "dithers".
    """
)

parser.add_argument(
    '-d', '--directory', help="Set the directory to traverse", default="." 
    )

parser.add_argument(
    '-rm', '--remove', help="Removes all the folders with dithers and their contents", action="store_true" 
    )

parser.add_argument(
    '-c', '--colorize', help="Colorizes the dithered images", action="store_true" 
    )

parser.add_argument(
    '-v', '--verbose', help="Print out more detailed information about what this script is doing", action="store_true" 
    )

args = parser.parse_args()

image_ext = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".tiff", ".bmp"]

nasin_kule = {
    'sewi': hitherdither.palette.Palette([(30,32,40), (11,21,71),(57,77,174),(158,168,218),(187,196,230),(243,244,250)]),
    'kasi': hitherdither.palette.Palette([(9,74,58), (58,136,118),(101,163,148),(144,189,179),(169,204,195),(242,247,246)]),
    'loje': hitherdither.palette.Palette([(86,9,6), (197,49,45),(228,130,124),(233,155,151),(242,193,190),(252,241,240)]),
    'kule_ala': hitherdither.palette.Palette([(25,25,25), (75,75,75),(125,125,125),(175,175,175),(225,225,225),(250,250,250)])
}

content_dir = args.directory
poki_pana = "lili_kule"

if args.verbose:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

exclude_dirs = set([poki_pana])


logging.info("Dithering all images in {} and subfolders".format(content_dir))
logging.debug("excluding directories: {}".format("".join(exclude_dirs)))

def colorize(source_image, category):
    """
    Picks a colored dithering palette based on the post category.
    """

    colors = {
            'sewi': hitherdither.palette.Palette([(30,32,40), (11,21,71),(57,77,174),(158,168,218),(187,196,230),(243,244,250)]),
            'kasi': hitherdither.palette.Palette([(9,74,58), (58,136,118),(101,163,148),(144,189,179),(169,204,195),(242,247,246)]),
            'loje': hitherdither.palette.Palette([(86,9,6), (197,49,45),(228,130,124),(233,155,151),(242,193,190),(252,241,240)]),
            'kule_ala': hitherdither.palette.Palette([(25,25,25), (75,75,75),(125,125,125),(175,175,175),(225,225,225),(250,250,250)])
        }


    if category:

        for i in colors.keys():
            if i in category.lower():
                color = colors[i]
                logging.info("Applying color palette '{}' for {}".format(i, category))
                break
            else:
                logging.info("No category for {}, {}".format(source_image, category))
                print("No category for {}, {}".format(source_image, category))
                color = colors['grayscale']

    else:
        logging.info("No category for {}, {}".format(source_image, category))
        print("No category for {}, {}".format(source_image, category))
        color = colors['grayscale']
        
    return color


def dither_image(source_image, output_image, nimi_pi_nasin_kule):
    #see hitherdither docs for different dithering algos and settings

    try:
        img= Image.open(source_image).convert('RGB')
        img.thumbnail((800,800), Image.LANCZOS)
        nasin = nasin_kule[nimi_pi_nasin_kule]
        img_dithered = hitherdither.ordered.bayer.bayer_dithering(img, nasin, [96, 96, 96], order=8) 
        img_dithered.save(output_image, optimize=True)

    except Exception as e:
        logging.debug("❌ failed to convert {}".format(source_image))
        logging.debug(e)

def delete_dithers(content_dir):
    logging.info("Deleting '{}' folders in {} and below".format(poki_pana, content_dir))
    for root, dirs, files in os.walk(content_dir, topdown=True):
        if root.endswith(poki_pana):
            shutil.rmtree(root)
            logging.info("Removed {}".format(root))

prev_root = None

if args.remove:
    delete_dithers(
        os.path.abspath(content_dir)
        )
else:
    for root, dirs, files in os.walk(os.path.abspath(content_dir), topdown=True):
        logging.debug("mi lukin e poki ni: {}".format(root))

        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        if prev_root is None:
            prev_root = root

        if prev_root is not root:
            if files:
                if any(x.endswith(tuple(image_ext)) for x in files):
                    for nimi_kule in nasin_kule.keys():
                        if not os.path.exists(os.path.join(root, poki_pana, nimi_kule)):
                            os.makedirs(os.path.join(root, poki_pana, nimi_kule), exist_ok=True )
                            logging.info("📁 mi pali e poki ni: {}".format(os.path.join(root, poki_pana, nimi_kule)))

        for fname in files:
            if fname.endswith(tuple(image_ext)):
                    file_, ext = os.path.splitext(fname)
                    source_image = os.path.join(root,fname)
                    for nimi_kule in nasin_kule.keys():
                      output_image = os.path.join(os.path.join(root, poki_pana, nimi_kule), file_+'_'+nimi_kule+'.png')
                      if not os.path.exists(output_image):
                          dither_image(source_image, output_image, nimi_kule)
                          logging.info("🖼 sitelen {} la mi lili e kule kepeken namako {}".format(fname, nimi_kule))
                          logging.debug(output_image)
                      else:
                          logging.debug("sitelen {} la sitelen pi kule lili li lon a. mi ni sin ala".format(fname))

        prev_root = root


logging.info("Done dithering")
