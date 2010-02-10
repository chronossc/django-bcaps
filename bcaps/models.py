# -*- coding: utf-8 -*-
from django.db import models
Q=models.Q
from django.utils.translation import ugettext_lazy as _
from pprint import pprint

class UserAgent(models.Model):
    useragent = models.CharField(max_length=500,help_text=_("UserAgent string of the browser."))
    browsercap = models.ForeignKey('BrowserCapabilitiesData',related_name='useragents')

class BrowserCapabilitiesData(models.Model):
    pattern             = models.CharField(max_length=500)
    parent              = models.ForeignKey('self',help_text=_("Inherith data from parent."),null=True)
    # useragent is a fk to UserAgent model
    browser             = models.CharField(max_length=500,help_text=_("Name of the browser."))
    activexcontrols     = models.BooleanField(help_text=_("Gets a true/false value indicating if the browser supports Microsoft's ActiveX control technologies. This value does not indicate if ActiveX is actually enabled."))
    alpha               = models.BooleanField(help_text=_("Gets a true/false value indicating if the browser is an alpha version and still under development."))
    aol                 = models.BooleanField(help_text=_("Gets a true/false value indicating if an America Online browser is being used."))
    aolversion          = models.CharField(max_length=10,help_text=_("Gets a number value indicating what version, if any, of the America Online browser is being used."),null=True)
    backgroundsounds    = models.BooleanField(help_text=_("Gets a true/false value indicating if the browser supports playing streaming music in the background on website pages."))
    beta                = models.BooleanField(help_text=_("Gets a true/false value indicating if the browser is an beta version and still under development."))
    cdf                 = models.BooleanField()
    cookies             = models.BooleanField(help_text=_("Gets a true/false value indicating if the browser supports Cookies. This value does not indicate if any cookies have been set."))
    crawler             = models.BooleanField(help_text=_("Gets a true/false value indicating if the browser is actually automated software crawling the website."))
    cssversion          = models.CharField(max_length=10,help_text=_("Gets a number indicating the version of CSS supported by the browser."),null=True)
    frames              = models.BooleanField(help_text=_("Gets a true/false value indicating if the browser supports Frames."))
    iframes             = models.BooleanField(help_text=_("Gets a true/false value indicating if the browser supports IFrames."))
    isbanned            = models.BooleanField(default=False,help_text=_("Gets a true/false value indicating if the user agent should be banned from accessing a website, typically for documented abuse or a reputation for abuse."))
    ismobiledevice      = models.BooleanField(help_text=_("Gets a true/false value indicating if the browser is a mobile device such as a cellphone or a PDA."))
    issyndicationreader = models.BooleanField(help_text=_("Gets a true/false value indicating if the browser is actually an RSS, Atom, or other XML-based feed reader or aggregator."))
    javaapplets         = models.BooleanField(help_text=_("Gets a true/false value indicating if the browser supports JAVA Applets. This value does not indicate if JAVA is actually enabled."))
    javascript          = models.BooleanField(help_text=_("Gets a true/false value indicating if the browser supports JavaScript. This value does not indicate if JavaScript is actually enabled."))
    majorver            = models.CharField(max_length=10,help_text=_("Major version number of the browser."),null=True)
    minorver            = models.CharField(max_length=10,help_text=_("Minor version number of the browser."),null=True)
    plataform           = models.CharField(max_length=500,help_text=_("Operating system the browser is running in."),null=True)
    supportscss         = models.BooleanField(help_text=_("Gets a true/false value indicating if the browser supports CSS."))
    tables              = models.BooleanField(help_text=_("Gets a true/false value indicating if the browser supports Tables."))
    vbscript            = models.BooleanField(help_text=_("Gets a true/false value indicating if the browser supports VBScript. This value does not indicate if VBScript is actually enabled."))
    version             = models.CharField(max_length=10,help_text=_("Full version number of the browser."),null=True)
    win16               = models.BooleanField(help_text=_("Gets a true/false value indicating if the browser's operating system supports 16-bit versions of Microsoft Windows."))
    win32               = models.BooleanField(help_text=_("Gets a true/false value indicating if the browser's operating system supports 32-bit versions of Microsoft Windows."))
    win64               = models.BooleanField(help_text=_("Gets a true/false value indicating if the browser's operating system supports 64-bit versions of Microsoft Windows."))

    class Meta:
        unique_together=('pattern','browser','parent')

    def __unicode__(self):
        return u"%s" % (self.browser)

    def __init__(self,*args,**kwargs):
        #print "\n"
        # clean default values from kwargs
        for k,v in kwargs.items():
            if v in ("default",""):
                kwargs.pop(k)

        # Parent means from what browser this browser get all data, like
        # inheritance, developer that maintains BCAPs project probabily do that
        # because size of csv/xml/ini files
        if kwargs.has_key('parent'):
            browser = kwargs.get('browser')

            parent = kwargs.get('parent')

            # try get parent data if parent isn't DefaultProperties
            #print '(66) DEBUG:::(parent,browser,version,pattern)',(kwargs.get('parent'),kwargs.get('browser'),kwargs.get('version') or kwargs.get('majorver'),kwargs.get('pattern'),)
            if browser != "DefaultProperties":# and parent != kwargs.get('browser'):
                parent = BrowserCapabilitiesData.objects.filter(
                    Q(browser=parent) | Q(pattern=parent) | Q(browser__istartswith=parent.split(' ')[0])
                )
                
                if parent.count()>1:
                    # Try some additional filters
                    q = Q(version=kwargs.get('version',''))
                    try:
                        q |= Q(version=kwargs['parent'].split(' ')[1])
                    except:
                        pass
                    tmp = parent.filter(q)
                    if tmp.count() != parent.count() and tmp.count() < parent.count():
                        parent = tmp
                if parent.count()>1:
                    tmp = parent.filter(Q(plataform=kwargs.get('plataform',''))|Q(plataform='unknown'))
                    if tmp.count() != parent.count() and tmp.count() < parent.count():
                        parent = tmp

                if parent:
                    parent = parent[0]
                else:
                    try:
                        parent = BrowserCapabilitiesData.objects.get(browser="DefaultProperties")
                    except BrowserCapabilitiesData.DoesNotExist:
                        # Parent not found, check if parent isn't = browser +
                        # version
                        parent = None
                        if kwargs['parent'] == ' '.join([
                                kwargs.get('browser',''),kwargs.get('version','')]):
                            kwargs['browser'] = ' '.join([kwargs.get('browser',''),kwargs.get('version','')])
                            parent = BrowserCapabilitiesData.objects.get(Browser="DefaultProperties")
                            
                        elif kwargs['parent'] == ' '.join([
                                kwargs.get('browser',''),kwargs.get('majorver','')]):
                            kwargs['browser'] = ' '.join([kwargs.get('browser',''),kwargs.get('majorver','')])
                            parent = BrowserCapabilitiesData.objects.get(Browser="DefaultProperties")

                        elif kwargs['parent'] == kwargs['pattern']:
                            try:
                                kwargs['browser'] = ' '.join([
                                    kwargs.get('parent',''),
                                    kwargs.get('majorver') or kwargs.get('version')
                                ])
                            except:
                                if kwargs.get('parent') and kwargs.get('parent') != "DefaultProperties":
                                    kwargs['browser'] = kwargs.get('parent')
                                else:
                                    kwargs['browser'] = kwargs['pattern']
                            parent = BrowserCapabilitiesData.objects.get(Browser="DefaultProperties")

                    #lse:
                    #    pass
                    #    #print '::: ',kwargs['parent']
                    #    #raise BrowserCapabilitiesData.DoesNotExist"""
            else:
                try:
                    parent = BrowserCapabilitiesData.objects.get(browser="DefaultProperties")
                except BrowserCapabilitiesData.DoesNotExist:
                    # This case cover DefaultProperties insert
                    pass

            if isinstance(parent,BrowserCapabilitiesData):


                if not kwargs.get('browser') and parent.browser != "DefaultProperties":
                    kwargs['browser'] = parent.browser
                elif not kwargs.get('browser'):
                    try:
                        kwargs['browser'] = ' '.join([
                            kwargs.get('parent',''),
                            kwargs.get('majorver') or kwargs.get('version')
                        ])
                    except:
                        if kwargs.get('parent') and kwargs.get('parent') != "DefaultProperties":
                            kwargs['browser'] = kwargs.get('parent')
                        else:
                            kwargs['browser'] = kwargs['pattern']
                
                

                #print '(134)DEBUG:::(parent,browser,version,pattern)',(kwargs.get('parent'),kwargs.get('browser'),kwargs.get('version') or kwargs.get('majorver'),kwargs.get('pattern'),)
                new_kwargs = parent.getdict()
                new_kwargs.update(kwargs)
                kwargs = new_kwargs
                #print '(138)DEBUG:::(parent,browser,version,pattern)',(kwargs.get('parent'),kwargs.get('browser'),kwargs.get('version') or kwargs.get('majorver'),kwargs.get('pattern'),)
                kwargs['parent'] = parent
                #print '(140)DEBUG:::(parent,browser,version,pattern)',(kwargs.get('parent'),kwargs.get('browser'),kwargs.get('version') or kwargs.get('majorver'),kwargs.get('pattern'),)
            else:
                kwargs.pop('parent')
        
        super(BrowserCapabilitiesData,self).__init__(*args,**kwargs)

    def getdict(self):
        return dict(
            pattern = self.pattern,
            parent = self.parent,
            browser = self.browser,
            activexcontrols = self.activexcontrols,
            alpha = self.alpha,
            aol = self.aol,
            aolversion = self.aolversion,
            backgroundsounds = self.backgroundsounds,
            beta = self.beta,
            cdf = self.cdf,
            cookies = self.cookies,
            crawler = self.crawler,
            cssversion = self.cssversion,
            frames = self.frames,
            iframes = self.iframes,
            isbanned = self.isbanned,
            ismobiledevice = self.ismobiledevice,
            issyndicationreader = self.issyndicationreader,
            javaapplets = self.javaapplets,
            javascript = self.javascript,
            majorver = self.majorver,
            minorver = self.minorver,
            plataform = self.plataform,
            supportscss = self.supportscss,
            tables = self.tables,
            vbscript = self.vbscript,
            version = self.version,
            win16 = self.win16,
            win32 = self.win32,
            win64 = self.win64
        )
