from werkzeug import Response

def main(request):
    return Response("404 not found: %s" % request.path, mimetype='text/html')

