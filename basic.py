import photorepo
import sys


def usage():
    sys.stderr.write(
        """%s <hash_method> <photo_repo> <query_photo> <num_results>"""
        % sys.argv[0])
    sys.exit(1)

if __name__ == "__main__":
    hash_method = sys.argv[1] if len(sys.argv) > 1 else usage()
    photo_repo = sys.argv[2] if len(sys.argv) > 2 else usage()
    query_photo = sys.argv[3] if len(sys.argv) > 3 else usage()
    num_results = sys.argv[4] if len(sys.argv) > 4 else usage()

    repo = photorepo.PhotoRepo(photo_repo, hash_method)
    results = repo.get_similar_photos(
        query_photo, num_results=int(num_results))

    # TODO(duongnt): Consider using HTML template
    output_html = """
<!DOCTYPE html>
<html>
<head>
<title>Image retrieval</title>
</head>
<body>
<div>Query photo:</div>
<img src="%s" alt="query" width="100" height="100">
<div>Search results:</div>
<ul>""" % query_photo

    for result in results:
        output_html += """
    <li><img src="%s" width="100" height="100">Score: %d</li>\n
    """ % (result[0], result[1])

    output_html += "</ul>\n</body>\n</html>"
    print output_html
