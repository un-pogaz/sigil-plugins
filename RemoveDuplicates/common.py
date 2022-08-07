#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os, re

# Simple Regex
class regex():
    
    # import the Python regex flag
    locals().update(re.RegexFlag.__members__)
    
    flag = ASCII + MULTILINE + DOTALL
    
        # re.A
        # re.ASCII
        # re.DEBUG
        # re.I
        # re.IGNORECASE
        # re.L
        # re.LOCALE
        # re.M
        # re.MULTILINE
        # re.S
        # re.DOTALL
        # re.X
        # re.VERBOSE
    
    def match(pattern, string, f=flag):
        return re.fullmatch(pattern, string, f)
    
    def search(pattern, string, f=flag):
        return re.search(pattern, string, f)
    
    def searchall(pattern, string, f=flag):
        if regex.search(pattern, string, f):
            return re.finditer(pattern, string, f)
        else:
            return None
    
    def split(pattern, string, maxsplit=0, f=flag):
        return re.split(pattern, string, maxsplit, f)
    
    def simple(pattern, repl, string, f=flag):
        return re.sub(pattern, repl, string, 0, f)
    
    def loop(pattern, repl, string, f=flag):
        i = 0
        while regex.search(pattern, string, f):
            if i > 1000:
                raise regexException('the pattern and substitution string caused an infinite loop', pattern, repl)
            string = regex.simple(pattern, repl, string, f)
            i+=1
            
        return string

class regexException(BaseException):
    def __init__(self, msg, pattern=None, repl=None):
        self.pattern = pattern
        self.repl = repl
        self.msg = msg
        self.name = 'RegeError:'
    
    def __str__(self):
        return self.msg

##
## Common
##
def CleanBasic(text):
    
    text = regex.loop(r'\s+</(p|h\d)', r'</\1', text)
    text = regex.loop(r"><(p|div|h\d|li|ul|ol|blockquote)", r">\n<\1", text)
    
    # line
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = regex.loop(r"( |\t|\n\n)+\n", "\n", text)
    
    # entity
    text = parseXMLentity(text)
    
    # xml format
    text = regex.loop(r"<([^<>]+)\s{2,}([^<>]+)>", r"<\1 \2>", text)
    text = regex.loop(r"\s+(|/|\?)\s*>", r"\1>", text)
    text = regex.loop(r"<\s*(|/|!|\?)\s+", r"<\1", text)
    
    text = regex.simple(r"(&#160;|\s)+</body>", r"\n</body>", text)
    
    # inline empty 
    inlineSpace = r'<(i|b|em|strong|sup|sub|span)(| [^>]*)>\s+</\1>'
    inlineEmpty = r'<(i|b|em|strong|sup|sub|span)(| [^>]*)></\1>'
    # same inline
    sameSpace = r'<(i|b|em|strong|sup|sub|span)(| [^>]*)>([^<]*)</\1>\s+<\1\2>'
    sameEmpty = r'<(i|b|em|strong|sup|sub|span)(| [^>]*)>([^<]*)</\1><\1\2>'
    # fusion inline 
    fusionSpace = r"</(i|b|em|strong|sup|sub)>\s+<\1(| [^>]*)>"
    fusionEmpty = r"</(i|b|em|strong|sup|sub)><\1(| [^>]*)>"
    
    while (regex.search(inlineSpace, text) or
        regex.search(inlineEmpty, text) or
        regex.search(sameSpace, text) or
        regex.search(sameEmpty, text) or
        regex.search(fusionSpace, text) or
        regex.search(fusionEmpty, text)):
        
        text = regex.loop(inlineSpace, r' ', text)
        text = regex.loop(inlineEmpty, r'', text)
        
        text = regex.loop(sameSpace, r'<\1\2>\3  ', text)
        text = regex.loop(sameEmpty, r'<\1\2>\3', text)
        
        text = regex.loop(fusionSpace, r" ", text)
        text = regex.loop(fusionEmpty, r"", text)
    
    # space inline
    text = regex.loop(r'\s+(<(i|b|em|strong|sup|sub|u|s|del|span|a)(| [^>]*)>)\s+', r' \1', text)
    text = regex.loop(r'\s+(</(i|b|em|strong|sup|sub|u|s|del|span|a)>)\s+', r'\1 ', text)
    
    # double espace et tab dans paragraphe
    text = regex.loop(r'(<(p|h\d)(| [^>]*)>(?:(?!</\2).)*?)(\t| {2,})', r'\1 ', text)
    # tab pour l'indentation
    text = regex.loop(r"^( *)\t(\s*<)", r"\1  \2", text)
    
    
    # style: del double 
    text = regex.loop(r' style="([^"]*);\s+;([^"]*)"', r' style="\1;\2"', text)
    # style: clean space before : 
    text = regex.loop(r' style="([^"]*)\s+(;|:)([^"]*)"', r' style="\1\2\3"', text)
    # style: clean space after : 
    text = regex.loop(r' style="([^"]*(?:;|:))\s{2,}([^"]*)"', r' style="\1 \2"', text)
    # style: insert space after : 
    text = regex.loop(r' style="([^"]*(?:;|:))([^ "])', r' style="\1 \2', text)
    
    # clean space in attribut
    text = regex.loop(r' ([^"=<>]+)="\s+([^"]*)"', r' \1="\2"', text)
    text = regex.loop(r' ([^"=<>]+)="([^"]*)\s+"', r' \1="\2"', text)
    
    #
    text = regex.loop(r'<a\s*>(((?!<a).)*?)</a>', r'\1', text)
    
    #strip <span>
    text = regex.loop(r'<span\s*>(((?!<span).)*?)</span>', r'\1', text)
    text = regex.loop(r'<span\s*>(((?!<span).)*?(<span[^>]*>((?!</?span).)*?</span>((?!</?span).)*?)+)</span>', r'\1', text)
    
    # remplace les triple point invalide
    text = regex.loop(r'\.\s+\.\s*\.', r'…', text)
    text = regex.loop(r'\.\s*\.\s+\.', r'…', text)
    text = regex.loop(r'\.\.\.', r'…', text)
    
    return text


from collections import namedtuple
XmlHtmlEntity = namedtuple('XmlHtmlEntity', ['char','name','html','xml','codepoint'])

def XmlHtmlEntityBuild1(name, codepoint):
    return XmlHtmlEntity(chr(codepoint), name, '&'+name+';', '&#'+str(codepoint)+';', codepoint)

def XmlHtmlEntityBuild2(name, char):
    return XmlHtmlEntity(char, name, '&'+name+';', None, None)


def parseXMLentity(text):
    # " & ' < >
    regx = r'&#x0*(22|26|27|3C|3E);'
    while regex.search(regx, text):
        m = regex.search(regx, text).group(1)
        text = text.replace('&#x'+m+';', '&#'+str(int(m, base=16))+';')
    
    # &#38; => &amp
    for e in Entitys.HtmlBase + Entitys.HtmlQuot + Entitys.HtmlApos:
        text = text.replace(e.xml, e.html)
    
    # &Agrave; &#192; => À
    for e in Entitys.Html:
        text = text.replace(e.html, e.char)
        if e.xml:
            text = text.replace(e.xml, e.char)
    
    regx = r'&#(\d+);'
    while regex.search(regx, text):
        m = regex.search(regx, text).group(1)
        text = text.replace('&#'+m+';', chr(int(m)))
    
    regx = r'&#x([0-9a-fA-F]+);'
    while regex.search(regx, text):
        m = regex.search(regx, text).group(1)
        text = text.replace('&#x'+m+';', chr(int(m, base=16)))
    
    text = regex.loop(r'(>[^<>]*)&quot;([^<>]*<)', r'\1"\2',text)
    text = regex.loop(r'(>[^<>]*)&apos;([^<>]*<)', r"\1'\2",text)
    
    text = regex.loop(r'(<[^<>]*="[^"]*)&apos;([^"]*"[^<>]*>)', r"\1'\2",text)
    
    text = text.replace(Entitys.nbsp.char, Entitys.nbsp.xml)
    
    return text

class Entitys:
    HtmlQuot = [ XmlHtmlEntityBuild1('quot', 34), XmlHtmlEntityBuild1('QUOT', 34) ]
    HtmlApos = [ XmlHtmlEntityBuild1('apos', 39), XmlHtmlEntityBuild1('APOS', 39) ]
    HtmlBase = [
        XmlHtmlEntityBuild1('amp', 38), # &
        XmlHtmlEntityBuild1('AMP', 38), # &
        XmlHtmlEntityBuild1('lt', 60),  # <
        XmlHtmlEntityBuild1('LT', 60),  # <
        XmlHtmlEntityBuild1('gt', 62),  # >
        XmlHtmlEntityBuild1('GT', 62),  # >
    ]
    
    Html2 = [
        XmlHtmlEntityBuild1('Agrave', 192), # À
        XmlHtmlEntityBuild1('Aacute', 193), # Á
        XmlHtmlEntityBuild1('Acirc', 194),  # Â
        XmlHtmlEntityBuild1('Atilde', 195), # Ã
        XmlHtmlEntityBuild1('Auml', 196),   # Ä
        XmlHtmlEntityBuild1('Aring', 197),  # Å
        XmlHtmlEntityBuild1('AElig', 198),  # Æ
        XmlHtmlEntityBuild1('Ccedil', 199), # Ç
        XmlHtmlEntityBuild1('Egrave', 200), # È
        XmlHtmlEntityBuild1('Eacute', 201), # É
        XmlHtmlEntityBuild1('Ecirc', 202),  # Ê
        XmlHtmlEntityBuild1('Euml', 203),   # Ë
        XmlHtmlEntityBuild1('Igrave', 204), # Ì
        XmlHtmlEntityBuild1('Iacute', 205), # Í
        XmlHtmlEntityBuild1('Icirc', 206),  # Î
        XmlHtmlEntityBuild1('Iuml', 207),   # Ï
        XmlHtmlEntityBuild1('ETH', 208),    # Ð
        XmlHtmlEntityBuild1('Ntilde', 209), # Ñ
        XmlHtmlEntityBuild1('Ograve', 210), # Ò
        XmlHtmlEntityBuild1('Oacute', 211), # Ó
        XmlHtmlEntityBuild1('Ocirc', 212),  # Ô
        XmlHtmlEntityBuild1('Otilde', 213), # Õ
        XmlHtmlEntityBuild1('Ouml', 214),   # Ö
        XmlHtmlEntityBuild1('Oslash', 216), # Ø
        XmlHtmlEntityBuild1('Ugrave', 217), # Ù
        XmlHtmlEntityBuild1('Uacute', 218), # Ú
        XmlHtmlEntityBuild1('Ucirc', 219),  # Û
        XmlHtmlEntityBuild1('Uuml', 220),   # Ü
        XmlHtmlEntityBuild1('Yacute', 221), # Ý
        
        XmlHtmlEntityBuild1('THORN', 222),  # Þ
        XmlHtmlEntityBuild1('szlig', 223),  # ß
        
        XmlHtmlEntityBuild1('agrave', 224), # à
        XmlHtmlEntityBuild1('aacute', 225), # á
        XmlHtmlEntityBuild1('acirc', 226),  # â
        XmlHtmlEntityBuild1('atilde', 227), # ã
        XmlHtmlEntityBuild1('auml', 228),   # ä
        XmlHtmlEntityBuild1('aring', 229),  # å
        XmlHtmlEntityBuild1('aelig', 230),  # æ
        XmlHtmlEntityBuild1('ccedil', 231), # ç
        XmlHtmlEntityBuild1('egrave', 232), # è
        XmlHtmlEntityBuild1('eacute', 233), # é
        XmlHtmlEntityBuild1('ecirc', 234),  # ê
        XmlHtmlEntityBuild1('euml', 235),   # ë
        XmlHtmlEntityBuild1('igrave', 236), # ì
        XmlHtmlEntityBuild1('iacute', 237), # í
        XmlHtmlEntityBuild1('icirc', 238),  # î
        XmlHtmlEntityBuild1('iuml', 239),   # ï
        XmlHtmlEntityBuild1('eth', 240),    # ð
        XmlHtmlEntityBuild1('ntilde', 241), # ñ
        XmlHtmlEntityBuild1('ograve', 242), # ò
        XmlHtmlEntityBuild1('oacute', 243), # ó
        XmlHtmlEntityBuild1('ocirc', 244),  # ô
        XmlHtmlEntityBuild1('otilde', 245), # õ
        XmlHtmlEntityBuild1('ouml', 246),   # ö
        XmlHtmlEntityBuild1('oslash', 248), # ø
        XmlHtmlEntityBuild1('ugrave', 249), # ù
        XmlHtmlEntityBuild1('uacute', 250), # ú
        XmlHtmlEntityBuild1('ucirc', 251),  # û
        XmlHtmlEntityBuild1('uuml', 252),   # ü
        XmlHtmlEntityBuild1('yacute', 253), # ý
        
        XmlHtmlEntityBuild1('thorn', 254),  # þ
        XmlHtmlEntityBuild1('yuml', 255),   # ÿ
    ]
    
    Html3 = [
        XmlHtmlEntityBuild1('nbsp', 160),   #  
        XmlHtmlEntityBuild1('iexcl', 161),  # ¡
        XmlHtmlEntityBuild1('cent', 162),   # ¢
        XmlHtmlEntityBuild1('pound', 163),  # £
        XmlHtmlEntityBuild1('curren', 164),  # ¤
        XmlHtmlEntityBuild1('yen', 165),    # ¥
        XmlHtmlEntityBuild1('brvbar', 166),  # ¦
        XmlHtmlEntityBuild1('sect', 167),   # §
        XmlHtmlEntityBuild1('uml', 168),    # ¨
        XmlHtmlEntityBuild1('copy', 169),   # ©
        XmlHtmlEntityBuild1('ordf', 170),   # ª
        XmlHtmlEntityBuild1('laquo', 171),  # «
        XmlHtmlEntityBuild1('not', 172),    # ¬
        XmlHtmlEntityBuild1('shy', 173),    # ­
        XmlHtmlEntityBuild1('reg', 174),    # ®
        XmlHtmlEntityBuild1('macr', 175),   # ¯
        XmlHtmlEntityBuild1('deg', 176),    # °
        XmlHtmlEntityBuild1('plusmn', 177),  # ±
        XmlHtmlEntityBuild1('sup2', 178),   # ²
        XmlHtmlEntityBuild1('sup3', 179),   # ³
        XmlHtmlEntityBuild1('acute', 180),  # ´
        XmlHtmlEntityBuild1('micro', 181),  # µ
        XmlHtmlEntityBuild1('para', 182),   # ¶
        XmlHtmlEntityBuild1('middot', 183),  # ·
        XmlHtmlEntityBuild1('cedil', 184),  # ¸
        XmlHtmlEntityBuild1('sup1', 185),   # ¹
        XmlHtmlEntityBuild1('ordm', 186),   # º
        XmlHtmlEntityBuild1('raquo', 187),  # »
        XmlHtmlEntityBuild1('frac14', 188),  # ¼
        XmlHtmlEntityBuild1('frac12', 189),  # ½
        XmlHtmlEntityBuild1('frac34', 190),  # ¾
        XmlHtmlEntityBuild1('iquest', 191),  # ¿
        
        XmlHtmlEntityBuild1('times', 215),  # ×
        
        XmlHtmlEntityBuild1('divide', 247), # ÷
    ]
    
    Html4 = [
        XmlHtmlEntityBuild1('OElig', 338),      # Œ
        XmlHtmlEntityBuild1('oelig', 339),      # œ
        
        XmlHtmlEntityBuild1('Scaron', 352),     # Š
        XmlHtmlEntityBuild1('scaron', 353),     # š
        
        XmlHtmlEntityBuild1('Yuml', 376),       # Ÿ
        
        XmlHtmlEntityBuild1('fnof', 402),       # ƒ
        
        XmlHtmlEntityBuild1('circ', 710),       # ˆ
        
        XmlHtmlEntityBuild1('tilde', 732),      # ˜
        
        XmlHtmlEntityBuild1('Alpha', 913 ),     # Α
        XmlHtmlEntityBuild1('Beta', 914 ),      # Β
        XmlHtmlEntityBuild1('Gamma', 915 ),     # Γ
        XmlHtmlEntityBuild1('Delta', 916 ),     # Δ
        XmlHtmlEntityBuild1('Epsilon', 917 ),   # Ε
        XmlHtmlEntityBuild1('Zeta', 918 ),      # Ζ
        XmlHtmlEntityBuild1('Eta', 919 ),       # Η
        XmlHtmlEntityBuild1('Theta', 920 ),     # Θ
        XmlHtmlEntityBuild1('Iota', 921 ),      # Ι
        XmlHtmlEntityBuild1('Kappa', 922 ),     # Κ
        XmlHtmlEntityBuild1('Lambda', 923 ),    # Λ
        XmlHtmlEntityBuild1('Mu', 924 ),        # Μ
        XmlHtmlEntityBuild1('Nu', 925 ),        # Ν
        XmlHtmlEntityBuild1('Xi', 926 ),        # Ξ
        XmlHtmlEntityBuild1('Omicron', 927 ),   # Ο
        XmlHtmlEntityBuild1('Pi', 928 ),        # Π
        XmlHtmlEntityBuild1('Rho', 929 ),       # Ρ
        
        XmlHtmlEntityBuild1('Sigma', 931 ),     # Σ
        XmlHtmlEntityBuild1('Tau', 932 ),       # Τ
        XmlHtmlEntityBuild1('Upsilon', 933 ),   # Υ
        XmlHtmlEntityBuild1('Phi', 934 ),       # Φ
        XmlHtmlEntityBuild1('Chi', 935 ),       # Χ
        XmlHtmlEntityBuild1('Psi', 936 ),       # Ψ
        XmlHtmlEntityBuild1('Omega', 937 ),     # Ω
        XmlHtmlEntityBuild1('ohm', 937 ),       # Ω
        
        XmlHtmlEntityBuild1('alpha', 945 ),     # α
        XmlHtmlEntityBuild1('beta', 946 ),      # β
        XmlHtmlEntityBuild1('gamma', 947 ),     # γ
        XmlHtmlEntityBuild1('delta', 948 ),     # δ
        XmlHtmlEntityBuild1('epsi', 949 ),      # ε
        XmlHtmlEntityBuild1('epsilon', 949 ),   # ε
        XmlHtmlEntityBuild1('zeta', 950 ),      # ζ
        XmlHtmlEntityBuild1('eta', 951 ),       # η
        XmlHtmlEntityBuild1('theta', 952 ),     # θ
        XmlHtmlEntityBuild1('iota', 953 ),      # ι
        XmlHtmlEntityBuild1('kappa', 954 ),     # κ
        XmlHtmlEntityBuild1('lambda', 955 ),    # λ
        XmlHtmlEntityBuild1('mu', 956 ),        # μ
        XmlHtmlEntityBuild1('nu', 957 ),        # ν
        XmlHtmlEntityBuild1('xi', 958 ),        # ξ
        XmlHtmlEntityBuild1('omicron', 959 ),   # ο
        XmlHtmlEntityBuild1('pi', 960 ),        # π
        XmlHtmlEntityBuild1('rho', 961 ),       # ρ
        XmlHtmlEntityBuild1('sigmav', 962 ),    # ς
        XmlHtmlEntityBuild1('sigmaf', 962 ),    # ς
        XmlHtmlEntityBuild1('sigma', 963 ),     # σ
        XmlHtmlEntityBuild1('tau', 964 ),       # τ
        XmlHtmlEntityBuild1('upsi', 965 ),      # υ
        XmlHtmlEntityBuild1('phi', 966 ),       # φ
        XmlHtmlEntityBuild1('chi', 967 ),       # χ
        XmlHtmlEntityBuild1('psi', 968 ),       # ψ
        XmlHtmlEntityBuild1('omega', 969 ),     # ω
        
        XmlHtmlEntityBuild1('thetav', 977 ),    # ϑ
        XmlHtmlEntityBuild1('upsih', 978 ),     # ϒ
        
        XmlHtmlEntityBuild1('phiv', 981 ),      # ϕ
        
        XmlHtmlEntityBuild1('ensp', 8194),      #  
        XmlHtmlEntityBuild1('emsp', 8195),      #  
        
        XmlHtmlEntityBuild1('thinsp', 8201),    #  
        
        XmlHtmlEntityBuild1('zwnj', 8204),      # ‌
        XmlHtmlEntityBuild1('zwj', 8205),       # ‍
        XmlHtmlEntityBuild1('lrm', 8206),       # ‎
        XmlHtmlEntityBuild1('rlm', 8207),       # ‏
        
        XmlHtmlEntityBuild1('ndash', 8211),     # –
        XmlHtmlEntityBuild1('mdash', 8212),     # —
        
        XmlHtmlEntityBuild1('lsquo', 8216),     # ‘
        XmlHtmlEntityBuild1('rsquo', 8217),     # ’
        XmlHtmlEntityBuild1('rsquor', 8217),    # ’
        XmlHtmlEntityBuild1('sbquo', 8218),     # ‚
        XmlHtmlEntityBuild1('ldquo', 8220),     # “
        XmlHtmlEntityBuild1('rdquo', 8221 ),    # ”
        XmlHtmlEntityBuild1('bdquo', 8222),     # „
        
        XmlHtmlEntityBuild1('dagger', 8224),    # †
        XmlHtmlEntityBuild1('ddagger', 8225),   # ‡
        XmlHtmlEntityBuild1('bull', 8226),      # •
        
        XmlHtmlEntityBuild1('hellip', 8230),    # …
        
        XmlHtmlEntityBuild1('permil', 8240),    # ‰
        
        XmlHtmlEntityBuild1('prime', 8242),     # ′
        XmlHtmlEntityBuild1('Prime', 8243),     # ″
        
        XmlHtmlEntityBuild1('lsaquo', 8249),    # ‹
        XmlHtmlEntityBuild1('rsaquo', 8250),    # ›
        
        XmlHtmlEntityBuild1('oline', 8254),     # ‾
        
        XmlHtmlEntityBuild1('euro', 8364),      # €
        
        XmlHtmlEntityBuild1('image', 8465),     # ℑ
        
        XmlHtmlEntityBuild1('weierp', 8472),    # ℘
        
        XmlHtmlEntityBuild1('real', 8476),      # ℜ
        
        XmlHtmlEntityBuild1('trade', 8482),     # ™
        
        XmlHtmlEntityBuild1('alefsym', 8501),   # ℵ
        
        XmlHtmlEntityBuild1('rang', 10217),     # ⟩
        XmlHtmlEntityBuild1('loz', 9674),       # ◊
        XmlHtmlE