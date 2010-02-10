#!/usr/bin/env python
# encoding: UTF-8
import os
import sys
import django
import shutil
import urllib2
import zipfile
import re
# in Py 3.0 ConfigParser was renamed to configparser
try:
    import ConfigParser as configparser
except ImportError:
    import configparser

SCRIPT_HOME=sys.path[0]
DOWNDIR=SCRIPT_HOME+'/download/'

# check if download path exist
if not os.path.isdir(DOWNDIR):
    os.mkdir(DOWNDIR)

directory = os.path.realpath('.')
while directory != '/':
  if os.path.isfile(directory+'/manage.py'): # application root
    break
  else:
    directory = os.path.split(directory)[0]
# if not found...
if not os.path.isfile(directory+'/manage.py'):
  raise ValueError("Project root not found!")
# add directory to system path, so you can use from app.models ... instead of
# project.app.models ... 
sys.path.insert(0,directory)
sys.path.insert(0,'/'.join(directory.split('/')[:-1]))
sys.path.insert(0,'.')
# set using directory name, django settings
os.environ['DJANGO_SETTINGS_MODULE'] = '%s.settings' % directory.split('/')[-1]


from django.utils.datastructures import SortedDict
from pprint import pprint
from bcaps.models import BrowserCapabilitiesData as BC
from django.utils import simplejson
from django.utils.encoding import *

INIURL="http://browsers.garykeith.com/stream.asp?BrowsCapZIP"

def convert_to_utf8(filename):
    # gather the encodings you think that the file may be
    # encoded inside a tuple
    encodings = ('ascii','iso-8859-1','windows-1253', 'iso-8859-7', 'macgreek')

    # try to open the file and exit if some IOError occurs
    try:
        f = open(filename, 'r').read()
    except Exception:
        sys.exit(1)

    # now start iterating in our encodings tuple and try to
    # decode the file
    for enc in encodings:
        try:
            # try to decode the file with the first encoding
            # from the tuple.
            # if it succeeds then it will reach break, so we
            # will be out of the loop (something we want on
            # success).
            # the data variable will hold our decoded text
            data = f.decode(enc)
            break
        except Exception:
            # if the first encoding fail, then with the continue
            # keyword will start again with the second encoding
            # from the tuple an so on.... until it succeeds.
            # if for some reason it reaches the last encoding of
            # our tuple without success, then exit the program.
            if enc == encodings[-1]:
                sys.exit(1)
            continue

    # now get the absolute path of our filename and append .bak
    # to the end of it (for our backup file)
    fpath = os.path.abspath(filename)
    newfilename = fpath + '.bak'
    # and make our backup file with shutil
    shutil.copy(filename, newfilename)

    # and at last convert it to utf-8
    f = open(filename, 'w')
    try:
        f.write(data.encode('utf-8'))
    except Exception, e:
        print e
    finally:
        f.close()


def getfile(iniurl=INIURL,keep=False):
    """ via urllib2 and zipfile libs get INI from zip file from url and returns
    a list of dict """
    if iniurl and not os.path.isfile("%sbrowscap.zip" % DOWNDIR) and not \
            os.path.isfile("%sbrowscap.ini" % DOWNDIR):
        fout = open("%sbrowscap.zip" % DOWNDIR,"w")
        fout.write(urllib2.urlopen(iniurl).read())
        fout.close()
    
    zip = zipfile.ZipFile("%sbrowscap.zip" % DOWNDIR)
    zip.extract("browscap.ini",DOWNDIR)
    convert_to_utf8("%sbrowscap.ini" % DOWNDIR)

    dctlist=[]
    config = configparser.ConfigParser(dict_type=SortedDict)
    config.readfp(open('%sbrowscap.ini' % DOWNDIR))
    for pattern in config.sections():
        dct=SortedDict()
        dct['pattern']=pattern
        for k,v in config.items(pattern):
            dct[k]=v
        dctlist.append(dct)

    if not keep:
        os.remove("%sbrowscap.zip" % DOWNDIR)
        os.remove("%sbrowscap.ini" % DOWNDIR)

    return dctlist


fields = SortedDict()
for n,v in [(x.name,True if x.__class__.__name__.find('Boolean') > -1 else \
    False) for x in BC._meta.fields]:
    fields[n]=v

# get dict list and run over
browsers=getfile(INIURL,keep=True)
for c,row in enumerate(browsers[1:]):
    dct=SortedDict()
    for fname,v in row.items():
        v = force_unicode(v)
        if fname == 'platform': fname = 'plataform'
        if fname == 'pattern':
            # transform in a python regex
            v = r'%s' % v.replace(".","\.").replace("?","\?").replace("(","\(").replace(")","\)").replace("*",".*")
        if fname == 'released':
            continue
            # transform in a datetime string know by django
            #v = datetime.datetime.strptime(v[:-6],r"%a, %d %b %Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
            #print v
        if fields[fname] is True and v.lower() in ('true','false',):
            # then is bool
            if v.lower() == 'true':
                v=True
            else:
                v=False
        dct[fname] = v
    try:
        try:
            bc = BC.objects.get(pattern=dct['pattern'])
            bc.update(dct)
        except BC.DoesNotExist:
            bc = BC(**dct)
        bc.save()
    except django.db.utils.DatabaseError,e:
        #print c,row
        raise
    except Exception,msg:
        raise
        try:
            print simplejson.dumps(dct,indent=3)
        except UnicodeDecodeError:
            pass
        else:
            sys.stderr.write(u"%s,%s :: %s" % (Exception,msg,dct))
    else:
        print \
(str(bc.id),bc.browser,bc.version,bc.majorver,bc.plataform,(bc.parent.browser,bc.parent.version,bc.parent.majorver) if bc.parent else 'no parent')
        pass
