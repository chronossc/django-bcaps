# Create your views here.
from django.http import HttpResponse
from django.utils import simplejson

def testview(request):
    dct=request.browser.getdict()
    dct['parent'] = request.browser.parent.browser
    return HttpResponse("""<html>
    <head>
        <title>Test BCAPS</title>
    </head>
    <body>
        %s<br>
        <pre>%s</pre>
    </body>
</html>""" % (request.META.get("HTTP_USER_AGENT"),
    simplejson.dumps(dct,indent=3)))
