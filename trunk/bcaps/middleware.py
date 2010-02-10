from models import BrowserCapabilitiesData as B
import re

ALLBROWSERS=B.objects.exclude(browser__in=("DefaultProperties","Default Browser",))

class BrowserMiddleware(object):

    def process_request(self,request):

        def search(blist):
            for b in blist:
                #print b.id,b.pattern
                r = re.compile(b.pattern)
                if r.findall(request.META.get('HTTP_USER_AGENT')):
                    break
                b = None
            print "search = ",b
            return b
        controle=ALLBROWSERS.count()/4
        inicial=0
        final=controle
        total = ALLBROWSERS.count()
        while total > final:
            b = search(ALLBROWSERS[inicial:final])
            print '%s:%s' % (inicial,final)
            inicial += controle
            final += controle
            if b: break
        print b
        #if not b:
        #    b = B.objects.get(browser='*')
        #try:
        #    b = B.objects.get(UserAgent=request.META.get('HTTP_USER_AGENT'))
        #except B.DoesNotExist:
        #    b = B.objects.get(Browser='*')
        request.browser = b
