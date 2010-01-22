def main(request):
    return "404 not found: %s" % request.path, 'text/html'

