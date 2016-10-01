from PIL import Image
import imagehash
import os
import sys
from collections import defaultdict
import matplotlib.pyplot as plt

def is_image(filename):
    f = filename.lower()
    return f.endswith(".png") or f.endswith(".jpg") or \
        f.endswith(".jpeg") or f.endswith(".gif") or f.endswith(".bmp")

def find_similar_images(image_repo, hashfunc=imagehash.average_hash):
    image_filenames = [os.path.join(image_repo, path) for path in os.listdir(image_repo) if is_image(path)]
    hash_to_images = defaultdict(list)
    for img in image_filenames:
        hash = hashfunc(Image.open(img))
        hash_to_images[hash].append(img)

    return hash_to_images

def usage():
    sys.stderr.write("%s [ahash|phash|dhash|...] <image_repo> <query_image>" %sys.argv[0])
    sys.exit(1)

if __name__ == "__main__":
    hash_method = sys.argv[1] if len(sys.argv) > 1 else usage()
    image_repo = sys.argv[2] if len(sys.argv) > 2 else usage()
    query_image = sys.argv[3] if len(sys.argv) > 3 else usage()
    
    if hash_method == 'ahash':
        hash_fn = imagehash.average_hash
    elif hash_method == 'phash':
        hash_fn = imagehash.phash
    elif hash_method == 'dhash':
        hash_fn = imagehash.dhash
    elif hash_method == 'whash-haar':
        hash_fn = imagehash.whash
    elif hash_method == 'whash-db4':
        hash_fn = lambda img: imagehash.whash(img, mode='db4')
    else:
        usage()

    output_html = """
<!doctype html>
<head>
<title>Image retrieval</title>
</head>
<body>
<div>Query image:</div>
<img src="%s" alt="query" width="100" height="100">
<div>Search results:</div>
<ul>""" %query_image
        
    query_hash = hash_fn(Image.open(query_image))
    repo_images = [os.path.join(image_repo, f) for f in os.listdir(image_repo) if is_image(f)]
    repo_hashes = defaultdict(list)
    for img in repo_images:
        img_hash = hash_fn(Image.open(img))
        repo_hashes[img_hash-query_hash].append(img)

    for h in sorted(repo_hashes):
        for im in repo_hashes[h]:
            #print im
            output_html += "<li><img src=%s width=\"100\" height=\"100\"></li>\n" %im

    output_html += "</ul>\n</body>\n</html>"

    print output_html

    
