from bottle import Bottle, request, route, run, static_file
import os
import sys
import functools
import photorepo

query_id = 0

app = Bottle()


@app.route("/")
def index():
    return "<h1>Demo: Search by photo</h1>"


def search_internal(repo, n_results):
    query = request.files.get("queryImage")
    _, ext = os.path.splitext(query.filename)
    if ext.lower() not in ('.jpg', '.jpeg', '.png', 'gif'):
        return "<b>File extension not supported.</b>"

    global query_id
    query_id += 1

    temp_file = "query/query%d%s" % (query_id, ext)
    query.save(temp_file, overwrite=True)
    results = repo.get_similar_photos(temp_file, n_results)

    # TODO: Consider using template
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
<ol>""" % temp_file

    for result in results:
        output_html += """
    <li><img src="%s" width="100" height="100">Score: %d</li>\n
    """ % (result[0], result[1])

    output_html += "</ol>\n</body>\n</html>"
    return output_html


@app.route("/img/<file_path:path>")
def servePhotos(file_path):
    return static_file(file_path, root="./img")


@app.route("/query/<file_path:path>")
def serveQuery(file_path):
    return static_file(file_path, root="./query")


def usage():
    sys.stderr.write(
        """%s <hashfn> [n_results]
        Example: `python server.py ahash 2`
        """
        % sys.argv[0])
    sys.exit(1)


if __name__ == "__main__":
    hashfn = sys.argv[1] if len(sys.argv) > 1 else usage()
    n_results = int(sys.argv[2]) if len(sys.argv) > 2 else -1
    repo = photorepo.PhotoRepo("./img", hashfn)

    # search_handler = functools.partial(
    #     search_internal, repo=repo, n_results=n_results)
    # route("/search", ["POST"], search_handler)
    app.route("/search", ["POST"], functools.partial(search_internal,
                                                     repo=repo,
                                                     n_results=n_results))

    run(app, host="localhost", port=8080, debug=True)
