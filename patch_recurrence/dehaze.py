import cPickle
import logging
import os
import sys

from bunch import bunchify

from config.arguments import parser

import cv2

import steps

import yaml


logging.basicConfig(
    stream=sys.stdout,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def save(img_file, patches, pairs):
    with open(img_file.split('.')[0] + '.patches', 'wb') as f:
        cPickle.dump(patches, f)
    with open(img_file.split('.')[0] + '.pairs', 'wb') as f:
        cPickle.dump(pairs, f)


def load(img_file):
    if not os.path.exists(img_file.split('.')[0] + '.patches'):
        return None, None
    with open(img_file.split('.')[0] + '.patches', 'rb') as f:
        patches = cPickle.load(f)
    with open(img_file.split('.')[0] + '.pairs', 'rb') as f:
        pairs = cPickle.load(f)
    return patches, pairs


def main():
    args = parser.parse_args()
    with open(args.constants, 'r') as f:
        constants = bunchify(yaml.load(f))

    logger.info("Loading image %s ..." % args.input)
    img = cv2.imread(args.input, flags=cv2.IMREAD_COLOR)
    # image scaled in 0-1 range
    img = img / 255.0

    # Scale array must be in decreasing order
    scaled_imgs = steps.scale(
        img,
        [1, 300.0 / 384, 200.0 / 384, 150.0 / 384, 120.0 / 384, 100.0 / 384]
    )

    if not args.no_cache:
        patches, pairs = load(args.input)
    else:
        patches, pairs = None, None
    if patches is None and pairs is None:
        logger.info("Extracting all patches ...")
        patches = steps.generate_patches(scaled_imgs, constants, True)

        logger.info("Smoothening std deviations of patches ...")
        steps.smoothen(scaled_imgs, patches, constants)

        logger.info("Putting patches in buckets ...")
        steps.set_patch_buckets(patches, constants)

        logger.info("Generating pairs of patches ...")
        pairs = steps.generate_pairs(scaled_imgs, patches, constants)

        # logger.info("Saving patches and pairs ...")
        # save(args.input, patches, pairs)
    else:
        logger.info("Using saved patches and pairs ...")

    logger.info("Filtering pairs for checking normalized correlation ...")
    pairs = steps.filter_pairs(patches, pairs, constants)

    logger.info("Removing outliers ...")
    pairs = steps.remove_outliers(pairs, constants)

    logger.info("Estimating global airlight ...")
    airlight = steps.estimate_airlight(pairs)

    logger.info("Estimated airlight is ...%s", str(airlight))

if __name__ == '__main__':
    main()
