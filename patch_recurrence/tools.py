from __future__ import division
import cv2
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.font_manager import FontProperties
import numpy as np


def show_img(imgs):
    # setup the figure
    fig = plt.figure()
    # show first image
    for i, img in enumerate(imgs):
        ax = fig.add_subplot(1, len(imgs), i + 1)
        plt.imshow(cv2.cvtColor(np.array(np.abs(img) * 255, dtype=np.uint8), cv2.COLOR_BGR2RGB))
        plt.axis("off")
    # show the images
    plt.show()


def save_img(imgs):
    """ Save 2 images side-by-side."""
    img1 = np.array(np.abs(imgs[0]) * 255, dtype=np.uint8)
    img2 = np.array(np.abs(imgs[1]) * 255, dtype=np.uint8)
    vis = np.concatenate((img1, img2), axis=1)
    cv2.imwrite('final.png', vis)


def show_tmap(imgs):
    # setup the figure
    fig = plt.figure()
    for i, img in enumerate(imgs):
        ax = fig.add_subplot(1, len(imgs), i + 1)
        plt.imshow(cv2.cvtColor(np.array(np.abs(img) * 255, dtype=np.uint8), cv2.COLOR_GRAY2RGB))
        plt.axis("off")
    plt.show()


def show_patches(patches):
    img1 = np.copy(patches[0].img)
    patch_size = patches[0].patch_size
    for patch in patches:
        h1, h2 = patch.location[0], patch.location[0] + patch_size
        w1, w2 = patch.location[1], patch.location[1] + patch_size
        img1[h1:h2, w1:w2, :] = np.zeros((patch_size, patch_size, 3))
    show_img([img1])


def show_pair(pair):
    # setup the figure
    fig = plt.figure()
    # show first image
    l1 = (pair.first.location[1] - 1, pair.first.location[0] - 1)
    l2 = (pair.first.location[1] + 8, pair.first.location[0] + 8)
    img1 = cv2.rectangle(pair.first.img * 255, l1, l2, (255, 0, 0), 1)

    l1 = (pair.second.location[1] - 1, pair.second.location[0] - 1)
    l2 = (pair.second.location[1] + 8, pair.second.location[0] + 8)
    img2 = cv2.rectangle(pair.second.img * 255, l1, l2, (255, 0, 0), 1)

    imgs = [img1, img2]
    for i, img in enumerate(imgs):
        ax = fig.add_subplot(1, len(imgs), i + 1)
        plt.imshow(cv2.cvtColor(np.array(np.abs(img), dtype=np.uint8), cv2.COLOR_BGR2RGB))
        plt.axis("off")

    # show the images
    plt.show()


def set_buckets(img, patch, constants):
    """Assigning colors to each patch based on bucket number
    - also, resizing img
    """
    num_buckets = constants.NUM_BUCKETS
    patch_size = constants.PATCH_SIZE

    # new_height = img.shape[0] - patch_size
    # new_width = img.shape[1] - patch_size

    # For half patches
    new_width = new_height = 0
    for i in range(0, img.shape[0] - patch_size, 2):
        new_height += 1
    for i in range(0, img.shape[1] - patch_size, 2):
        new_width += 1

    img = img[0:new_height, 0:new_width]
    img = np.reshape(img, [-1, 3])

    bucket_colors = []
    l1 = [(0, 0, i * 2 / num_buckets) for i in range(int(num_buckets / 2))]
    l2 = [(i * 2 / num_buckets, i * 2 / num_buckets, 1) for i in range(int(num_buckets / 2))]
    bucket_colors = list(reversed(l1 + l2))

    for i in range(new_height * new_width):
        img[i] = bucket_colors[int(patch[i].bucket)]

    img = np.reshape(img, [new_height, new_width, 3])
    return img


def show_buckety_img(imgs, constants):
    """Display buckety image
    """
    num_buckets = constants.NUM_BUCKETS
    # setup the figure
    fig = plt.figure()
    # show first image
    for i, img in enumerate(imgs):
        ax = fig.add_subplot(1, len(imgs), i + 1)
        plt.imshow(cv2.cvtColor(np.array(np.abs(img) * 255, dtype=np.uint8), cv2.COLOR_BGR2RGB))
        plt.axis("off")

    ax = fig.add_subplot(3, 4, 4)
    plt.axis("off")
    bucket_colors = []
    l1 = [(0, 0, i * 2 / num_buckets) for i in range(int(num_buckets / 2))]
    l2 = [(i * 2 / num_buckets, i * 2 / num_buckets, 1) for i in range(int(num_buckets / 2))]
    bucket_colors = list(reversed(l1 + l2))

    legend_data = [(i + 1, list(reversed(bucket_colors[i])), i + 1) for i in range(num_buckets)]

    handles = [
        Rectangle((0, 0), 1, 1, color = [v for v in c]) for k, c, n in legend_data
    ]
    labels = [n for k, c, n in legend_data]

    fontP = FontProperties()
    fontP.set_size('small')
    plt.legend(handles,labels, prop=fontP)

    # show the images
    plt.show()


def histogram(pairs, i):
    """Plotting histogram of R, G, B (ith) airlight estimates
    """
    x = []
    for pair in pairs:
        x.append(pair.airlight[i])
    num_bins = 10
    u = [0.1, 1.0]

    if i == 0:
        t = 'blue'
    elif i == 1:
        t = 'green'
    else:
        t = 'red'

    n, bins, patches = plt.hist(x, num_bins, facecolor=t, alpha=0.5)

    plt.xlabel('Pairwise estimated airlight')
    plt.ylabel('Number of pairs')
    plt.title(r'$\mathrm{Histogram}$')
    plt.grid(True)
    plt.xlim(u)
    plt.show()


def show_patches_per_bucket(patches):
    """Plotting histogram to show number of patches in each bucket
    """
    scaled_imgs = len(patches)
    num_bins = 100
    x = []
    for k in range(scaled_imgs):
        for patch in patches[k]:
            x.append(patch.bucket)

    n, bins, patches = plt.hist(x, num_bins, facecolor='black', alpha=0.5)

    plt.xlabel('Bucket numbers')
    plt.ylabel('Number of patches')
    plt.title(r'$\mathrm{Histogram}$')
    plt.grid(True)
    plt.xlim([0, 10])
    plt.show()


def show_loss(loss, iterations, name):
    """Display loss across each iteration
    """
    index = [i for i in range(iterations)]

    plt.plot(index, loss, 'ro')
    plt.axis([0, 100, 1000, 7000])
    plt.xlabel('Iterations')
    plt.ylabel('Loss')
    plt.title(name)
    plt.grid(True)
    plt.show()
