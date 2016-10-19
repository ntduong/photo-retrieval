from PIL import Image
import imagehash
import os
from collections import defaultdict
import io

# Hash functions supported in imagehash library
available_hashfuncs = {
    "ahash": imagehash.average_hash,
    "phash": imagehash.phash,
    "dhash": imagehash.dhash,
    "whash-haar": imagehash.whash,
    "whash-db4": lambda img: imagehash.whash(img, mode='db4')
}


class PhotoRepo(object):

    def __init__(self, repo_path, hashfn="ahash"):
        if hashfn not in available_hashfuncs:
            # Use average hash as default
            self.hashfn = available_hashfuncs["ahash"]
        self.hashfn = available_hashfuncs[hashfn]

        self.photo_filenames = [os.path.join(repo_path, name)
                                for name in os.listdir(repo_path)
                                if is_photo(name)]
        self.photo_hash = defaultdict(list)
        for photo in self.photo_filenames:
            self.photo_hash[self.hashfn(Image.open(photo))].append(photo)

    def get_similar_photos(self, query_photo, num_results=-1):
        """Return photos which are most similar to the query photo.

        When num_results = -1, return all photos in the repo in
        descending order of similarity score. Otherwise, return top
        num_results photos.
        """

        if num_results == -1:
            num_results = len(self.photo_filenames)

        query_hash = self.hashfn(Image.open(query_photo))
        hamming_dists = defaultdict(list)
        for h in self.photo_hash:
            hamming_dists[h - query_hash].extend(self.photo_hash[h])

        res, cnt = [], 0
        for dist in sorted(hamming_dists):
            if cnt >= num_results:
                break
            added = min(num_results - cnt, len(hamming_dists[dist]))
            # res.extend(hamming_dists[dist][:added])
            for photo in hamming_dists[dist][:added]:
                res.append((photo, dist))

            cnt += added

        return res

    def get_similar_photos_for_bytes(self,
                                     query_photo_in_bytes,
                                     num_results=-1):
        """Return photos which are most similar to the query photo.

        When num_results = -1, return all photos in the repo in
        descending order of similarity score. Otherwise, return top
        num_results photos.
        """

        if num_results == -1:
            num_results = len(self.photo_filenames)

        query_hash = self.hashfn(Image.open(io.BytesIO(query_photo_in_bytes)))
        hamming_dists = defaultdict(list)
        for h in self.photo_hash:
            hamming_dists[h - query_hash].extend(self.photo_hash[h])

        res, cnt = [], 0
        for dist in sorted(hamming_dists):
            if cnt >= num_results:
                break
            added = min(num_results - cnt, len(hamming_dists[dist]))
            # res.extend(hamming_dists[dist][:added])
            for photo in hamming_dists[dist][:added]:
                res.append((photo, dist))

            cnt += added

        return res

    def add_photo(self, filename):
        """Add a new photo to the repository, assumed the input filename is valid.
        """
        if not is_photo(filename):
            return False

        if self.photo_filenames.count(filename) > 0:
            return False

        self.photo_filenames.append(filename)
        self.photo_hash[self.hashfn(Image.open(filename))].append(filename)
        return True

    def remove_photo(self, filename):
        """Remove the photo given by the filename from the repository if it
        exists.  Assume the input filename is valid.
        """
        if not is_photo(filename):
            return False

        if self.photo_filenames.count(filename) == 0:
            return False

        self.photo_filenames.remove(filename)
        self.photo_hash[self.hashfn(Image.open(filename))].remove(filename)
        return True


def is_photo(filename):
    f = filename.lower()
    return f.endswith(".png") or f.endswith(".jpg") or \
        f.endswith(".jpeg") or f.endswith(".gif") or f.endswith(".bmp")
