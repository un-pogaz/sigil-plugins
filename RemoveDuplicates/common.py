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
        XmlHtmlEntityBuild1('spades', 9824),    # ♠
        XmlHtmlEntityBuild1('clubs', 9827),     # ♣
        XmlHtmlEntityBuild1('hearts', 9829),    # ♥
        XmlHtmlEntityBuild1('diams', 9830),     # ♦
        XmlHtmlEntityBuild1('lang', 10216),     # ⟨
        XmlHtmlEntityBuild1('rang', 10217),     # ⟩
    ]
    
    Html5 = [
        XmlHtmlEntityBuild1('Abreve', 258),                                                         # Ă
        XmlHtmlEntityBuild1('abreve', 259),                                                         # ă
        XmlHtmlEntityBuild1('ac', 8766),                                                            # ∾
        XmlHtmlEntityBuild1('acd', 8767),                                                           # ∿
        XmlHtmlEntityBuild2('acE', '∾̳'),                                                            # ∾̳
        XmlHtmlEntityBuild1('Acy', 1040),                                                           # А
        XmlHtmlEntityBuild1('acy', 1072),                                                           # а
        XmlHtmlEntityBuild1('af', 8289),                                                            # ⁡
        XmlHtmlEntityBuild1('Afr', 120068),                                                         # 𝔄
        XmlHtmlEntityBuild1('afr', 120094),                                                         # 𝔞
        XmlHtmlEntityBuild1('aleph', 8501),                                                         # ℵ
        XmlHtmlEntityBuild1('Amacr', 256),                                                          # Ā
        XmlHtmlEntityBuild1('amacr', 257),                                                          # ā
        XmlHtmlEntityBuild1('amalg', 10815),                                                        # ⨿
        XmlHtmlEntityBuild1('And', 10835),                                                          # ⩓
        XmlHtmlEntityBuild1('and', 8743),                                                           # ∧
        XmlHtmlEntityBuild1('andand', 10837),                                                       # ⩕
        XmlHtmlEntityBuild1('andd', 10844),                                                         # ⩜
        XmlHtmlEntityBuild1('andslope', 10840),                                                     # ⩘
        XmlHtmlEntityBuild1('andv', 10842),                                                         # ⩚
        XmlHtmlEntityBuild1('ang', 8736),                                                           # ∠
        XmlHtmlEntityBuild1('ange', 10660),                                                         # ⦤
        XmlHtmlEntityBuild1('angle', 8736),                                                         # ∠
        XmlHtmlEntityBuild1('angmsd', 8737),                                                        # ∡
        XmlHtmlEntityBuild1('angmsdaa', 10664),                                                     # ⦨
        XmlHtmlEntityBuild1('angmsdab', 10665),                                                     # ⦩
        XmlHtmlEntityBuild1('angmsdac', 10666),                                                     # ⦪
        XmlHtmlEntityBuild1('angmsdad', 10667),                                                     # ⦫
        XmlHtmlEntityBuild1('angmsdae', 10668),                                                     # ⦬
        XmlHtmlEntityBuild1('angmsdaf', 10669),                                                     # ⦭
        XmlHtmlEntityBuild1('angmsdag', 10670),                                                     # ⦮
        XmlHtmlEntityBuild1('angmsdah', 10671),                                                     # ⦯
        XmlHtmlEntityBuild1('angrt', 8735),                                                         # ∟
        XmlHtmlEntityBuild1('angrtvb', 8894),                                                       # ⊾
        XmlHtmlEntityBuild1('angrtvbd', 10653),                                                     # ⦝
        XmlHtmlEntityBuild1('angsph', 8738),                                                        # ∢
        XmlHtmlEntityBuild1('angst', 197),                                                          # Å
        XmlHtmlEntityBuild1('angzarr', 9084),                                                       # ⍼
        XmlHtmlEntityBuild1('Aogon', 260),                                                          # Ą
        XmlHtmlEntityBuild1('aogon', 261),                                                          # ą
        XmlHtmlEntityBuild1('Aopf', 120120),                                                        # 𝔸
        XmlHtmlEntityBuild1('aopf', 120146),                                                        # 𝕒
        XmlHtmlEntityBuild1('ap', 8776),                                                            # ≈
        XmlHtmlEntityBuild1('apacir', 10863),                                                       # ⩯
        XmlHtmlEntityBuild1('apE', 10864),                                                          # ⩰
        XmlHtmlEntityBuild1('ape', 8778),                                                           # ≊
        XmlHtmlEntityBuild1('apid', 8779),                                                          # ≋
        XmlHtmlEntityBuild1('apos', 39),                                                            # '
        XmlHtmlEntityBuild1('ApplyFunction', 8289),                                                 # ⁡
        XmlHtmlEntityBuild1('approx', 8776),                                                        # ≈
        XmlHtmlEntityBuild1('approxeq', 8778),                                                      # ≊
        XmlHtmlEntityBuild1('Ascr', 119964),                                                        # 𝒜
        XmlHtmlEntityBuild1('ascr', 119990),                                                        # 𝒶
        XmlHtmlEntityBuild1('Assign', 8788),                                                        # ≔
        XmlHtmlEntityBuild1('ast', 42),                                                             # *
        XmlHtmlEntityBuild1('asymp', 8776),                                                         # ≈
        XmlHtmlEntityBuild1('asympeq', 8781),                                                       # ≍
        XmlHtmlEntityBuild1('awconint', 8755),                                                      # ∳
        XmlHtmlEntityBuild1('awint', 10769),                                                        # ⨑
        XmlHtmlEntityBuild1('backcong', 8780),                                                      # ≌
        XmlHtmlEntityBuild1('backepsilon', 1014),                                                   # ϶
        XmlHtmlEntityBuild1('backprime', 8245),                                                     # ‵
        XmlHtmlEntityBuild1('backsim', 8765),                                                       # ∽
        XmlHtmlEntityBuild1('backsimeq', 8909),                                                     # ⋍
        XmlHtmlEntityBuild1('Backslash', 8726),                                                     # ∖
        XmlHtmlEntityBuild1('Barv', 10983),                                                         # ⫧
        XmlHtmlEntityBuild1('barvee', 8893),                                                        # ⊽
        XmlHtmlEntityBuild1('Barwed', 8966),                                                        # ⌆
        XmlHtmlEntityBuild1('barwed', 8965),                                                        # ⌅
        XmlHtmlEntityBuild1('barwedge', 8965),                                                      # ⌅
        XmlHtmlEntityBuild1('bbrk', 9141),                                                          # ⎵
        XmlHtmlEntityBuild1('bbrktbrk', 9142),                                                      # ⎶
        XmlHtmlEntityBuild1('bcong', 8780),                                                         # ≌
        XmlHtmlEntityBuild1('Bcy', 1041),                                                           # Б
        XmlHtmlEntityBuild1('bcy', 1073),                                                           # б
        XmlHtmlEntityBuild1('becaus', 8757),                                                        # ∵
        XmlHtmlEntityBuild1('Because', 8757),                                                       # ∵
        XmlHtmlEntityBuild1('because', 8757),                                                       # ∵
        XmlHtmlEntityBuild1('bemptyv', 10672),                                                      # ⦰
        XmlHtmlEntityBuild1('bepsi', 1014),                                                         # ϶
        XmlHtmlEntityBuild1('bernou', 8492),                                                        # ℬ
        XmlHtmlEntityBuild1('Bernoullis', 8492),                                                    # ℬ
        XmlHtmlEntityBuild1('beth', 8502),                                                          # ℶ
        XmlHtmlEntityBuild1('between', 8812),                                                       # ≬
        XmlHtmlEntityBuild1('Bfr', 120069),                                                         # 𝔅
        XmlHtmlEntityBuild1('bfr', 120095),                                                         # 𝔟
        XmlHtmlEntityBuild1('bigcap', 8898),                                                        # ⋂
        XmlHtmlEntityBuild1('bigcirc', 9711),                                                       # ◯
        XmlHtmlEntityBuild1('bigcup', 8899),                                                        # ⋃
        XmlHtmlEntityBuild1('bigodot', 10752),                                                      # ⨀
        XmlHtmlEntityBuild1('bigoplus', 10753),                                                     # ⨁
        XmlHtmlEntityBuild1('bigotimes', 10754),                                                    # ⨂
        XmlHtmlEntityBuild1('bigsqcup', 10758),                                                     # ⨆
        XmlHtmlEntityBuild1('bigstar', 9733),                                                       # ★
        XmlHtmlEntityBuild1('bigtriangledown', 9661),                                               # ▽
        XmlHtmlEntityBuild1('bigtriangleup', 9651),                                                 # △
        XmlHtmlEntityBuild1('biguplus', 10756),                                                     # ⨄
        XmlHtmlEntityBuild1('bigvee', 8897),                                                        # ⋁
        XmlHtmlEntityBuild1('bigwedge', 8896),                                                      # ⋀
        XmlHtmlEntityBuild1('bkarow', 10509),                                                       # ⤍
        XmlHtmlEntityBuild1('blacklozenge', 10731),                                                 # ⧫
        XmlHtmlEntityBuild1('blacksquare', 9642),                                                   # ▪
        XmlHtmlEntityBuild1('blacktriangle', 9652),                                                 # ▴
        XmlHtmlEntityBuild1('blacktriangledown', 9662),                                             # ▾
        XmlHtmlEntityBuild1('blacktriangleleft', 9666),                                             # ◂
        XmlHtmlEntityBuild1('blacktriangleright', 9656),                                            # ▸
        XmlHtmlEntityBuild1('blank', 9251),                                                         # ␣
        XmlHtmlEntityBuild1('blk12', 9618),                                                         # ▒
        XmlHtmlEntityBuild1('blk14', 9617),                                                         # ░
        XmlHtmlEntityBuild1('blk34', 9619),                                                         # ▓
        XmlHtmlEntityBuild1('block', 9608),                                                         # █
        XmlHtmlEntityBuild2('bne', '=⃥'),                                                            # =⃥
        XmlHtmlEntityBuild2('bnequiv', '≡⃥'),                                                        # ≡⃥
        XmlHtmlEntityBuild1('bNot', 10989),                                                         # ⫭
        XmlHtmlEntityBuild1('bnot', 8976),                                                          # ⌐
        XmlHtmlEntityBuild1('Bopf', 120121),                                                        # 𝔹
        XmlHtmlEntityBuild1('bopf', 120147),                                                        # 𝕓
        XmlHtmlEntityBuild1('bot', 8869),                                                           # ⊥
        XmlHtmlEntityBuild1('bottom', 8869),                                                        # ⊥
        XmlHtmlEntityBuild1('bowtie', 8904),                                                        # ⋈
        XmlHtmlEntityBuild1('boxbox', 10697),                                                       # ⧉
        XmlHtmlEntityBuild1('boxDL', 9559),                                                         # ╗
        XmlHtmlEntityBuild1('boxDl', 9558),                                                         # ╖
        XmlHtmlEntityBuild1('boxdL', 9557),                                                         # ╕
        XmlHtmlEntityBuild1('boxdl', 9488),                                                         # ┐
        XmlHtmlEntityBuild1('boxDR', 9556),                                                         # ╔
        XmlHtmlEntityBuild1('boxDr', 9555),                                                         # ╓
        XmlHtmlEntityBuild1('boxdR', 9554),                                                         # ╒
        XmlHtmlEntityBuild1('boxdr', 9484),                                                         # ┌
        XmlHtmlEntityBuild1('boxH', 9552),                                                          # ═
        XmlHtmlEntityBuild1('boxh', 9472),                                                          # ─
        XmlHtmlEntityBuild1('boxHD', 9574),                                                         # ╦
        XmlHtmlEntityBuild1('boxHd', 9572),                                                         # ╤
        XmlHtmlEntityBuild1('boxhD', 9573),                                                         # ╥
        XmlHtmlEntityBuild1('boxhd', 9516),                                                         # ┬
        XmlHtmlEntityBuild1('boxHU', 9577),                                                         # ╩
        XmlHtmlEntityBuild1('boxHu', 9575),                                                         # ╧
        XmlHtmlEntityBuild1('boxhU', 9576),                                                         # ╨
        XmlHtmlEntityBuild1('boxhu', 9524),                                                         # ┴
        XmlHtmlEntityBuild1('boxminus', 8863),                                                      # ⊟
        XmlHtmlEntityBuild1('boxplus', 8862),                                                       # ⊞
        XmlHtmlEntityBuild1('boxtimes', 8864),                                                      # ⊠
        XmlHtmlEntityBuild1('boxUL', 9565),                                                         # ╝
        XmlHtmlEntityBuild1('boxUl', 9564),                                                         # ╜
        XmlHtmlEntityBuild1('boxuL', 9563),                                                         # ╛
        XmlHtmlEntityBuild1('boxul', 9496),                                                         # ┘
        XmlHtmlEntityBuild1('boxUR', 9562),                                                         # ╚
        XmlHtmlEntityBuild1('boxUr', 9561),                                                         # ╙
        XmlHtmlEntityBuild1('boxuR', 9560),                                                         # ╘
        XmlHtmlEntityBuild1('boxur', 9492),                                                         # └
        XmlHtmlEntityBuild1('boxV', 9553),                                                          # ║
        XmlHtmlEntityBuild1('boxv', 9474),                                                          # │
        XmlHtmlEntityBuild1('boxVH', 9580),                                                         # ╬
        XmlHtmlEntityBuild1('boxVh', 9579),                                                         # ╫
        XmlHtmlEntityBuild1('boxvH', 9578),                                                         # ╪
        XmlHtmlEntityBuild1('boxvh', 9532),                                                         # ┼
        XmlHtmlEntityBuild1('boxVL', 9571),                                                         # ╣
        XmlHtmlEntityBuild1('boxVl', 9570),                                                         # ╢
        XmlHtmlEntityBuild1('boxvL', 9569),                                                         # ╡
        XmlHtmlEntityBuild1('boxvl', 9508),                                                         # ┤
        XmlHtmlEntityBuild1('boxVR', 9568),                                                         # ╠
        XmlHtmlEntityBuild1('boxVr', 9567),                                                         # ╟
        XmlHtmlEntityBuild1('boxvR', 9566),                                                         # ╞
        XmlHtmlEntityBuild1('boxvr', 9500),                                                         # ├
        XmlHtmlEntityBuild1('bprime', 8245),                                                        # ‵
        XmlHtmlEntityBuild1('Breve', 728),                                                          # ˘
        XmlHtmlEntityBuild1('breve', 728),                                                          # ˘
        XmlHtmlEntityBuild1('Bscr', 8492),                                                          # ℬ
        XmlHtmlEntityBuild1('bscr', 119991),                                                        # 𝒷
        XmlHtmlEntityBuild1('bsemi', 8271),                                                         # ⁏
        XmlHtmlEntityBuild1('bsim', 8765),                                                          # ∽
        XmlHtmlEntityBuild1('bsime', 8909),                                                         # ⋍
        XmlHtmlEntityBuild1('bsol', 92),                                                            # \
        XmlHtmlEntityBuild1('bsolb', 10693),                                                        # ⧅
        XmlHtmlEntityBuild1('bsolhsub', 10184),                                                     # ⟈
        XmlHtmlEntityBuild1('bullet', 8226),                                                        # •
        XmlHtmlEntityBuild1('bump', 8782),                                                          # ≎
        XmlHtmlEntityBuild1('bumpE', 10926),                                                        # ⪮
        XmlHtmlEntityBuild1('bumpe', 8783),                                                         # ≏
        XmlHtmlEntityBuild1('Bumpeq', 8782),                                                        # ≎
        XmlHtmlEntityBuild1('bumpeq', 8783),                                                        # ≏
        XmlHtmlEntityBuild1('Cacute', 262),                                                         # Ć
        XmlHtmlEntityBuild1('cacute', 263),                                                         # ć
        XmlHtmlEntityBuild1('Cap', 8914),                                                           # ⋒
        XmlHtmlEntityBuild1('cap', 8745),                                                           # ∩
        XmlHtmlEntityBuild1('capand', 10820),                                                       # ⩄
        XmlHtmlEntityBuild1('capbrcup', 10825),                                                     # ⩉
        XmlHtmlEntityBuild1('capcap', 10827),                                                       # ⩋
        XmlHtmlEntityBuild1('capcup', 10823),                                                       # ⩇
        XmlHtmlEntityBuild1('capdot', 10816),                                                       # ⩀
        XmlHtmlEntityBuild1('CapitalDifferentialD', 8517),                                          # ⅅ
        XmlHtmlEntityBuild2('caps', '∩︀'),                                                           # ∩︀
        XmlHtmlEntityBuild1('caret', 8257),                                                         # ⁁
        XmlHtmlEntityBuild1('caron', 711),                                                          # ˇ
        XmlHtmlEntityBuild1('Cayleys', 8493),                                                       # ℭ
        XmlHtmlEntityBuild1('ccaps', 10829),                                                        # ⩍
        XmlHtmlEntityBuild1('Ccaron', 268),                                                         # Č
        XmlHtmlEntityBuild1('ccaron', 269),                                                         # č
        XmlHtmlEntityBuild1('Ccirc', 264),                                                          # Ĉ
        XmlHtmlEntityBuild1('ccirc', 265),                                                          # ĉ
        XmlHtmlEntityBuild1('Cconint', 8752),                                                       # ∰
        XmlHtmlEntityBuild1('ccups', 10828),                                                        # ⩌
        XmlHtmlEntityBuild1('ccupssm', 10832),                                                      # ⩐
        XmlHtmlEntityBuild1('Cdot', 266),                                                           # Ċ
        XmlHtmlEntityBuild1('cdot', 267),                                                           # ċ
        XmlHtmlEntityBuild1('Cedilla', 184),                                                        # ¸
        XmlHtmlEntityBuild1('cemptyv', 10674),                                                      # ⦲
        XmlHtmlEntityBuild1('CenterDot', 183),                                                      # ·
        XmlHtmlEntityBuild1('centerdot', 183),                                                      # ·
        XmlHtmlEntityBuild1('Cfr', 8493),                                                           # ℭ
        XmlHtmlEntityBuild1('cfr', 120096),                                                         # 𝔠
        XmlHtmlEntityBuild1('CHcy', 1063),                                                          # Ч
        XmlHtmlEntityBuild1('chcy', 1095),                                                          # ч
        XmlHtmlEntityBuild1('check', 10003),                                                        # ✓
        XmlHtmlEntityBuild1('checkmark', 10003),                                                    # ✓
        XmlHtmlEntityBuild1('cir', 9675),                                                           # ○
        XmlHtmlEntityBuild1('circeq', 8791),                                                        # ≗
        XmlHtmlEntityBuild1('circlearrowleft', 8634),                                               # ↺
        XmlHtmlEntityBuild1('circlearrowright', 8635),                                              # ↻
        XmlHtmlEntityBuild1('circledast', 8859),                                                    # ⊛
        XmlHtmlEntityBuild1('circledcirc', 8858),                                                   # ⊚
        XmlHtmlEntityBuild1('circleddash', 8861),                                                   # ⊝
        XmlHtmlEntityBuild1('CircleDot', 8857),                                                     # ⊙
        XmlHtmlEntityBuild1('circledR', 174),                                                       # ®
        XmlHtmlEntityBuild1('circledS', 9416),                                                      # Ⓢ
        XmlHtmlEntityBuild1('CircleMinus', 8854),                                                   # ⊖
        XmlHtmlEntityBuild1('CirclePlus', 8853),                                                    # ⊕
        XmlHtmlEntityBuild1('CircleTimes', 8855),                                                   # ⊗
        XmlHtmlEntityBuild1('cirE', 10691),                                                         # ⧃
        XmlHtmlEntityBuild1('cire', 8791),                                                          # ≗
        XmlHtmlEntityBuild1('cirfnint', 10768),                                                     # ⨐
        XmlHtmlEntityBuild1('cirmid', 10991),                                                       # ⫯
        XmlHtmlEntityBuild1('cirscir', 10690),                                                      # ⧂
        XmlHtmlEntityBuild1('ClockwiseContourIntegral', 8754),                                      # ∲
        XmlHtmlEntityBuild1('CloseCurlyDoubleQuote', 8221),                                         # ”
        XmlHtmlEntityBuild1('CloseCurlyQuote', 8217),                                               # ’
        XmlHtmlEntityBuild1('clubsuit', 9827),                                                      # ♣
        XmlHtmlEntityBuild1('Colon', 8759),                                                         # ∷
        XmlHtmlEntityBuild1('colon', 58),                                                           # :
        XmlHtmlEntityBuild1('Colone', 10868),                                                       # ⩴
        XmlHtmlEntityBuild1('colone', 8788),                                                        # ≔
        XmlHtmlEntityBuild1('coloneq', 8788),                                                       # ≔
        XmlHtmlEntityBuild1('comma', 44),                                                           # ,
        XmlHtmlEntityBuild1('commat', 64),                                                          # @
        XmlHtmlEntityBuild1('comp', 8705),                                                          # ∁
        XmlHtmlEntityBuild1('compfn', 8728),                                                        # ∘
        XmlHtmlEntityBuild1('complement', 8705),                                                    # ∁
        XmlHtmlEntityBuild1('complexes', 8450),                                                     # ℂ
        XmlHtmlEntityBuild1('cong', 8773),                                                          # ≅
        XmlHtmlEntityBuild1('congdot', 10861),                                                      # ⩭
        XmlHtmlEntityBuild1('Congruent', 8801),                                                     # ≡
        XmlHtmlEntityBuild1('Conint', 8751),                                                        # ∯
        XmlHtmlEntityBuild1('conint', 8750),                                                        # ∮
        XmlHtmlEntityBuild1('ContourIntegral', 8750),                                               # ∮
        XmlHtmlEntityBuild1('Copf', 8450),                                                          # ℂ
        XmlHtmlEntityBuild1('copf', 120148),                                                        # 𝕔
        XmlHtmlEntityBuild1('coprod', 8720),                                                        # ∐
        XmlHtmlEntityBuild1('Coproduct', 8720),                                                     # ∐
        XmlHtmlEntityBuild1('COPY', 169),                                                           # ©
        XmlHtmlEntityBuild1('COPY', 169),                                                           # ©
        XmlHtmlEntityBuild1('copysr', 8471),                                                        # ℗
        XmlHtmlEntityBuild1('CounterClockwiseContourIntegral', 8755),                               # ∳
        XmlHtmlEntityBuild1('crarr', 8629),                                                         # ↵
        XmlHtmlEntityBuild1('Cross', 10799),                                                        # ⨯
        XmlHtmlEntityBuild1('cross', 10007),                                                        # ✗
        XmlHtmlEntityBuild1('Cscr', 119966),                                                        # 𝒞
        XmlHtmlEntityBuild1('cscr', 119992),                                                        # 𝒸
        XmlHtmlEntityBuild1('csub', 10959),                                                         # ⫏
        XmlHtmlEntityBuild1('csube', 10961),                                                        # ⫑
        XmlHtmlEntityBuild1('csup', 10960),                                                         # ⫐
        XmlHtmlEntityBuild1('csupe', 10962),                                                        # ⫒
        XmlHtmlEntityBuild1('ctdot', 8943),                                                         # ⋯
        XmlHtmlEntityBuild1('cudarrl', 10552),                                                      # ⤸
        XmlHtmlEntityBuild1('cudarrr', 10549),                                                      # ⤵
        XmlHtmlEntityBuild1('cuepr', 8926),                                                         # ⋞
        XmlHtmlEntityBuild1('cuesc', 8927),                                                         # ⋟
        XmlHtmlEntityBuild1('cularr', 8630),                                                        # ↶
        XmlHtmlEntityBuild1('cularrp', 10557),                                                      # ⤽
        XmlHtmlEntityBuild1('Cup', 8915),                                                           # ⋓
        XmlHtmlEntityBuild1('cup', 8746),                                                           # ∪
        XmlHtmlEntityBuild1('cupbrcap', 10824),                                                     # ⩈
        XmlHtmlEntityBuild1('CupCap', 8781),                                                        # ≍
        XmlHtmlEntityBuild1('cupcap', 10822),                                                       # ⩆
        XmlHtmlEntityBuild1('cupcup', 10826),                                                       # ⩊
        XmlHtmlEntityBuild1('cupdot', 8845),                                                        # ⊍
        XmlHtmlEntityBuild1('cupor', 10821),                                                        # ⩅
        XmlHtmlEntityBuild2('cups', '∪︀'),                                                           # ∪︀
        XmlHtmlEntityBuild1('curarr', 8631),                                                        # ↷
        XmlHtmlEntityBuild1('curarrm', 10556),                                                      # ⤼
        XmlHtmlEntityBuild1('curlyeqprec', 8926),                                                   # ⋞
        XmlHtmlEntityBuild1('curlyeqsucc', 8927),                                                   # ⋟
        XmlHtmlEntityBuild1('curlyvee', 8910),                                                      # ⋎
        XmlHtmlEntityBuild1('curlywedge', 8911),                                                    # ⋏
        XmlHtmlEntityBuild1('curvearrowleft', 8630),                                                # ↶
        XmlHtmlEntityBuild1('curvearrowright', 8631),                                               # ↷
        XmlHtmlEntityBuild1('cuvee', 8910),                                                         # ⋎
        XmlHtmlEntityBuild1('cuwed', 8911),                                                         # ⋏
        XmlHtmlEntityBuild1('cwconint', 8754),                                                      # ∲
        XmlHtmlEntityBuild1('cwint', 8753),                                                         # ∱
        XmlHtmlEntityBuild1('cylcty', 9005),                                                        # ⌭
        XmlHtmlEntityBuild1('Dagger', 8225),                                                        # ‡
        XmlHtmlEntityBuild1('daleth', 8504),                                                        # ℸ
        XmlHtmlEntityBuild1('Darr', 8609),                                                          # ↡
        XmlHtmlEntityBuild1('dArr', 8659),                                                          # ⇓
        XmlHtmlEntityBuild1('darr', 8595),                                                          # ↓
        XmlHtmlEntityBuild1('dash', 8208),                                                          # ‐
        XmlHtmlEntityBuild1('Dashv', 10980),                                                        # ⫤
        XmlHtmlEntityBuild1('dashv', 8867),                                                         # ⊣
        XmlHtmlEntityBuild1('dbkarow', 10511),                                                      # ⤏
        XmlHtmlEntityBuild1('dblac', 733),                                                          # ˝
        XmlHtmlEntityBuild1('Dcaron', 270),                                                         # Ď
        XmlHtmlEntityBuild1('dcaron', 271),                                                         # ď
        XmlHtmlEntityBuild1('Dcy', 1044),                                                           # Д
        XmlHtmlEntityBuild1('dcy', 1076),                                                           # д
        XmlHtmlEntityBuild1('DD', 8517),                                                            # ⅅ
        XmlHtmlEntityBuild1('dd', 8518),                                                            # ⅆ
        XmlHtmlEntityBuild1('ddarr', 8650),                                                         # ⇊
        XmlHtmlEntityBuild1('DDotrahd', 10513),                                                     # ⤑
        XmlHtmlEntityBuild1('ddotseq', 10871),                                                      # ⩷
        XmlHtmlEntityBuild1('Del', 8711),                                                           # ∇
        XmlHtmlEntityBuild1('demptyv', 10673),                                                      # ⦱
        XmlHtmlEntityBuild1('dfisht', 10623),                                                       # ⥿
        XmlHtmlEntityBuild1('Dfr', 120071),                                                         # 𝔇
        XmlHtmlEntityBuild1('dfr', 120097),                                                         # 𝔡
        XmlHtmlEntityBuild1('dHar', 10597),                                                         # ⥥
        XmlHtmlEntityBuild1('dharl', 8643),                                                         # ⇃
        XmlHtmlEntityBuild1('dharr', 8642),                                                         # ⇂
        XmlHtmlEntityBuild1('DiacriticalAcute', 180),                                               # ´
        XmlHtmlEntityBuild1('DiacriticalDot', 729),                                                 # ˙
        XmlHtmlEntityBuild1('DiacriticalDoubleAcute', 733),                                         # ˝
        XmlHtmlEntityBuild1('DiacriticalGrave', 96),                                                # `
        XmlHtmlEntityBuild1('DiacriticalTilde', 732),                                               # ˜
        XmlHtmlEntityBuild1('diam', 8900),                                                          # ⋄
        XmlHtmlEntityBuild1('Diamond', 8900),                                                       # ⋄
        XmlHtmlEntityBuild1('diamond', 8900),                                                       # ⋄
        XmlHtmlEntityBuild1('diamondsuit', 9830),                                                   # ♦
        XmlHtmlEntityBuild1('die', 168),                                                            # ¨
        XmlHtmlEntityBuild1('DifferentialD', 8518),                                                 # ⅆ
        XmlHtmlEntityBuild1('digamma', 989),                                                        # ϝ
        XmlHtmlEntityBuild1('disin', 8946),                                                         # ⋲
        XmlHtmlEntityBuild1('div', 247),                                                            # ÷
        XmlHtmlEntityBuild1('divideontimes', 8903),                                                 # ⋇
        XmlHtmlEntityBuild1('divonx', 8903),                                                        # ⋇
        XmlHtmlEntityBuild1('DJcy', 1026),                                                          # Ђ
        XmlHtmlEntityBuild1('djcy', 1106),                                                          # ђ
        XmlHtmlEntityBuild1('dlcorn', 8990),                                                        # ⌞
        XmlHtmlEntityBuild1('dlcrop', 8973),                                                        # ⌍
        XmlHtmlEntityBuild1('dollar', 36),                                                          # $
        XmlHtmlEntityBuild1('Dopf', 120123),                                                        # 𝔻
        XmlHtmlEntityBuild1('dopf', 120149),                                                        # 𝕕
        XmlHtmlEntityBuild1('Dot', 168),                                                            # ¨
        XmlHtmlEntityBuild1('dot', 729),                                                            # ˙
        XmlHtmlEntityBuild1('DotDot', 8412),                                                        #⃜ 
        XmlHtmlEntityBuild1('doteq', 8784),                                                         # ≐
        XmlHtmlEntityBuild1('doteqdot', 8785),                                                      # ≑
        XmlHtmlEntityBuild1('DotEqual', 8784),                                                      # ≐
        XmlHtmlEntityBuild1('dotminus', 8760),                                                      # ∸
        XmlHtmlEntityBuild1('dotplus', 8724),                                                       # ∔
        XmlHtmlEntityBuild1('dotsquare', 8865),                                                     # ⊡
        XmlHtmlEntityBuild1('doublebarwedge', 8966),                                                # ⌆
        XmlHtmlEntityBuild1('DoubleContourIntegral', 8751),                                         # ∯
        XmlHtmlEntityBuild1('DoubleDot', 168),                                                      # ¨
        XmlHtmlEntityBuild1('DoubleDownArrow', 8659),                                               # ⇓
        XmlHtmlEntityBuild1('DoubleLeftArrow', 8656),                                               # ⇐
        XmlHtmlEntityBuild1('DoubleLeftRightArrow', 8660),                                          # ⇔
        XmlHtmlEntityBuild1('DoubleLeftTee', 10980),                                                # ⫤
        XmlHtmlEntityBuild1('DoubleLongLeftArrow', 10232),                                          # ⟸
        XmlHtmlEntityBuild1('DoubleLongLeftRightArrow', 10234),                                     # ⟺
        XmlHtmlEntityBuild1('DoubleLongRightArrow', 10233),                                         # ⟹
        XmlHtmlEntityBuild1('DoubleRightArrow', 8658),                                              # ⇒
        XmlHtmlEntityBuild1('DoubleRightTee', 8872),                                                # ⊨
        XmlHtmlEntityBuild1('DoubleUpArrow', 8657),                                                 # ⇑
        XmlHtmlEntityBuild1('DoubleUpDownArrow', 8661),                                             # ⇕
        XmlHtmlEntityBuild1('DoubleVerticalBar', 8741),                                             # ∥
        XmlHtmlEntityBuild1('DownArrow', 8595),                                                     # ↓
        XmlHtmlEntityBuild1('Downarrow', 8659),                                                     # ⇓
        XmlHtmlEntityBuild1('downarrow', 8595),                                                     # ↓
        XmlHtmlEntityBuild1('DownArrowBar', 10515),                                                 # ⤓
        XmlHtmlEntityBuild1('DownArrowUpArrow', 8693),                                              # ⇵
        XmlHtmlEntityBuild1('DownBreve', 785),                                                      #̑ 
        XmlHtmlEntityBuild1('downdownarrows', 8650),                                                # ⇊
        XmlHtmlEntityBuild1('downharpoonleft', 8643),                                               # ⇃
        XmlHtmlEntityBuild1('downharpoonright', 8642),                                              # ⇂
        XmlHtmlEntityBuild1('DownLeftRightVector', 10576),                                          # ⥐
        XmlHtmlEntityBuild1('DownLeftTeeVector', 10590),                                            # ⥞
        XmlHtmlEntityBuild1('DownLeftVector', 8637),                                                # ↽
        XmlHtmlEntityBuild1('DownLeftVectorBar', 10582),                                            # ⥖
        XmlHtmlEntityBuild1('DownRightTeeVector', 10591),                                           # ⥟
        XmlHtmlEntityBuild1('DownRightVector', 8641),                                               # ⇁
        XmlHtmlEntityBuild1('DownRightVectorBar', 10583),                                           # ⥗
        XmlHtmlEntityBuild1('DownTee', 8868),                                                       # ⊤
        XmlHtmlEntityBuild1('DownTeeArrow', 8615),                                                  # ↧
        XmlHtmlEntityBuild1('drbkarow', 10512),                                                     # ⤐
        XmlHtmlEntityBuild1('drcorn', 8991),                                                        # ⌟
        XmlHtmlEntityBuild1('drcrop', 8972),                                                        # ⌌
        XmlHtmlEntityBuild1('Dscr', 119967),                                                        # 𝒟
        XmlHtmlEntityBuild1('dscr', 119993),                                                        # 𝒹
        XmlHtmlEntityBuild1('DScy', 1029),                                                          # Ѕ
        XmlHtmlEntityBuild1('dscy', 1109),                                                          # ѕ
        XmlHtmlEntityBuild1('dsol', 10742),                                                         # ⧶
        XmlHtmlEntityBuild1('Dstrok', 272),                                                         # Đ
        XmlHtmlEntityBuild1('dstrok', 273),                                                         # đ
        XmlHtmlEntityBuild1('dtdot', 8945),                                                         # ⋱
        XmlHtmlEntityBuild1('dtri', 9663),                                                          # ▿
        XmlHtmlEntityBuild1('dtrif', 9662),                                                         # ▾
        XmlHtmlEntityBuild1('duarr', 8693),                                                         # ⇵
        XmlHtmlEntityBuild1('duhar', 10607),                                                        # ⥯
        XmlHtmlEntityBuild1('dwangle', 10662),                                                      # ⦦
        XmlHtmlEntityBuild1('DZcy', 1039),                                                          # Џ
        XmlHtmlEntityBuild1('dzcy', 1119),                                                          # џ
        XmlHtmlEntityBuild1('dzigrarr', 10239),                                                     # ⟿
        XmlHtmlEntityBuild1('easter', 10862),                                                       # ⩮
        XmlHtmlEntityBuild1('Ecaron', 282),                                                         # Ě
        XmlHtmlEntityBuild1('ecaron', 283),                                                         # ě
        XmlHtmlEntityBuild1('ecir', 8790),                                                          # ≖
        XmlHtmlEntityBuild1('ecolon', 8789),                                                        # ≕
        XmlHtmlEntityBuild1('Ecy', 1069),                                                           # Э
        XmlHtmlEntityBuild1('ecy', 1101),                                                           # э
        XmlHtmlEntityBuild1('eDDot', 10871),                                                        # ⩷
        XmlHtmlEntityBuild1('Edot', 278),                                                           # Ė
        XmlHtmlEntityBuild1('eDot', 8785),                                                          # ≑
        XmlHtmlEntityBuild1('edot', 279),                                                           # ė
        XmlHtmlEntityBuild1('ee', 8519),                                                            # ⅇ
        XmlHtmlEntityBuild1('efDot', 8786),                                                         # ≒
        XmlHtmlEntityBuild1('Efr', 120072),                                                         # 𝔈
        XmlHtmlEntityBuild1('efr', 120098),                                                         # 𝔢
        XmlHtmlEntityBuild1('eg', 10906),                                                           # ⪚
        XmlHtmlEntityBuild1('egs', 10902),                                                          # ⪖
        XmlHtmlEntityBuild1('egsdot', 10904),                                                       # ⪘
        XmlHtmlEntityBuild1('el', 10905),                                                           # ⪙
        XmlHtmlEntityBuild1('Element', 8712),                                                       # ∈
        XmlHtmlEntityBuild1('elinters', 9191),                                                      # ⏧
        XmlHtmlEntityBuild1('ell', 8467),                                                           # ℓ
        XmlHtmlEntityBuild1('els', 10901),                                                          # ⪕
        XmlHtmlEntityBuild1('elsdot', 10903),                                                       # ⪗
        XmlHtmlEntityBuild1('Emacr', 274),                                                          # Ē
        XmlHtmlEntityBuild1('emacr', 275),                                                          # ē
        XmlHtmlEntityBuild1('empty', 8709),                                                         # ∅
        XmlHtmlEntityBuild1('emptyset', 8709),                                                      # ∅
        XmlHtmlEntityBuild1('EmptySmallSquare', 9723),                                              # ◻
        XmlHtmlEntityBuild1('emptyv', 8709),                                                        # ∅
        XmlHtmlEntityBuild1('EmptyVerySmallSquare', 9643),                                          # ▫
        XmlHtmlEntityBuild1('emsp13', 8196),                                                        #  
        XmlHtmlEntityBuild1('emsp14', 8197),                                                        #  
        XmlHtmlEntityBuild1('ENG', 330),                                                            # Ŋ
        XmlHtmlEntityBuild1('eng', 331),                                                            # ŋ
        XmlHtmlEntityBuild1('Eogon', 280),                                                          # Ę
        XmlHtmlEntityBuild1('eogon', 281),                                                          # ę
        XmlHtmlEntityBuild1('Eopf', 120124),                                                        # 𝔼
        XmlHtmlEntityBuild1('eopf', 120150),                                                        # 𝕖
        XmlHtmlEntityBuild1('epar', 8917),                                                          # ⋕
        XmlHtmlEntityBuild1('eparsl', 10723),                                                       # ⧣
        XmlHtmlEntityBuild1('eplus', 10865),                                                        # ⩱
        XmlHtmlEntityBuild1('epsiv', 1013),                                                         # ϵ
        XmlHtmlEntityBuild1('eqcirc', 8790),                                                        # ≖
        XmlHtmlEntityBuild1('eqcolon', 8789),                                                       # ≕
        XmlHtmlEntityBuild1('eqsim', 8770),                                                         # ≂
        XmlHtmlEntityBuild1('eqslantgtr', 10902),                                                   # ⪖
        XmlHtmlEntityBuild1('eqslantless', 10901),                                                  # ⪕
        XmlHtmlEntityBuild1('Equal', 10869),                                                        # ⩵
        XmlHtmlEntityBuild1('equals', 61),                                                          # =
        XmlHtmlEntityBuild1('EqualTilde', 8770),                                                    # ≂
        XmlHtmlEntityBuild1('equest', 8799),                                                        # ≟
        XmlHtmlEntityBuild1('Equilibrium', 8652),                                                   # ⇌
        XmlHtmlEntityBuild1('equiv', 8801),                                                         # ≡
        XmlHtmlEntityBuild1('equivDD', 10872),                                                      # ⩸
        XmlHtmlEntityBuild1('eqvparsl', 10725),                                                     # ⧥
        XmlHtmlEntityBuild1('erarr', 10609),                                                        # ⥱
        XmlHtmlEntityBuild1('erDot', 8787),                                                         # ≓
        XmlHtmlEntityBuild1('Escr', 8496),                                                          # ℰ
        XmlHtmlEntityBuild1('escr', 8495),                                                          # ℯ
        XmlHtmlEntityBuild1('esdot', 8784),                                                         # ≐
        XmlHtmlEntityBuild1('Esim', 10867),                                                         # ⩳
        XmlHtmlEntityBuild1('esim', 8770),                                                          # ≂
        XmlHtmlEntityBuild1('excl', 33),                                                            # !
        XmlHtmlEntityBuild1('exist', 8707),                                                         # ∃
        XmlHtmlEntityBuild1('Exists', 8707),                                                        # ∃
        XmlHtmlEntityBuild1('expectation', 8496),                                                   # ℰ
        XmlHtmlEntityBuild1('ExponentialE', 8519),                                                  # ⅇ
        XmlHtmlEntityBuild1('exponentiale', 8519),                                                  # ⅇ
        XmlHtmlEntityBuild1('fallingdotseq', 8786),                                                 # ≒
        XmlHtmlEntityBuild1('Fcy', 1060),                                                           # Ф
        XmlHtmlEntityBuild1('fcy', 1092),                                                           # ф
        XmlHtmlEntityBuild1('female', 9792),                                                        # ♀
        XmlHtmlEntityBuild1('ffilig', 64259),                                                       # ﬃ
        XmlHtmlEntityBuild1('fflig', 64256),                                                        # ﬀ
        XmlHtmlEntityBuild1('ffllig', 64260),                                                       # ﬄ
        XmlHtmlEntityBuild1('Ffr', 120073),                                                         # 𝔉
        XmlHtmlEntityBuild1('ffr', 120099),                                                         # 𝔣
        XmlHtmlEntityBuild1('filig', 64257),                                                        # ﬁ
        XmlHtmlEntityBuild1('FilledSmallSquare', 9724),                                             # ◼
        XmlHtmlEntityBuild1('FilledVerySmallSquare', 9642),                                         # ▪
        XmlHtmlEntityBuild2('fjlig', 'fj'),                                                         # fj
        XmlHtmlEntityBuild1('flat', 9837),                                                          # ♭
        XmlHtmlEntityBuild1('fllig', 64258),                                                        # ﬂ
        XmlHtmlEntityBuild1('fltns', 9649),                                                         # ▱
        XmlHtmlEntityBuild1('Fopf', 120125),                                                        # 𝔽
        XmlHtmlEntityBuild1('fopf', 120151),                                                        # 𝕗
        XmlHtmlEntityBuild1('ForAll', 8704),                                                        # ∀
        XmlHtmlEntityBuild1('forall', 8704),                                                        # ∀
        XmlHtmlEntityBuild1('fork', 8916),                                                          # ⋔
        XmlHtmlEntityBuild1('forkv', 10969),                                                        # ⫙
        XmlHtmlEntityBuild1('Fouriertrf', 8497),                                                    # ℱ
        XmlHtmlEntityBuild1('fpartint', 10765),                                                     # ⨍
        XmlHtmlEntityBuild1('frac13', 8531),                                                        # ⅓
        XmlHtmlEntityBuild1('frac15', 8533),                                                        # ⅕
        XmlHtmlEntityBuild1('frac16', 8537),                                                        # ⅙
        XmlHtmlEntityBuild1('frac18', 8539),                                                        # ⅛
        XmlHtmlEntityBuild1('frac23', 8532),                                                        # ⅔
        XmlHtmlEntityBuild1('frac25', 8534),                                                        # ⅖
        XmlHtmlEntityBuild1('frac35', 8535),                                                        # ⅗
        XmlHtmlEntityBuild1('frac38', 8540),                                                        # ⅜
        XmlHtmlEntityBuild1('frac45', 8536),                                                        # ⅘
        XmlHtmlEntityBuild1('frac56', 8538),                                                        # ⅚
        XmlHtmlEntityBuild1('frac58', 8541),                                                        # ⅝
        XmlHtmlEntityBuild1('frac78', 8542),                                                        # ⅞
        XmlHtmlEntityBuild1('frasl', 8260),                                                         # ⁄
        XmlHtmlEntityBuild1('frown', 8994),                                                         # ⌢
        XmlHtmlEntityBuild1('Fscr', 8497),                                                          # ℱ
        XmlHtmlEntityBuild1('fscr', 119995),                                                        # 𝒻
        XmlHtmlEntityBuild1('gacute', 501),                                                         # ǵ
        XmlHtmlEntityBuild1('Gammad', 988),                                                         # Ϝ
        XmlHtmlEntityBuild1('gammad', 989),                                                         # ϝ
        XmlHtmlEntityBuild1('gap', 10886),                                                          # ⪆
        XmlHtmlEntityBuild1('Gbreve', 286),                                                         # Ğ
        XmlHtmlEntityBuild1('gbreve', 287),                                                         # ğ
        XmlHtmlEntityBuild1('Gcedil', 290),                                                         # Ģ
        XmlHtmlEntityBuild1('Gcirc', 284),                                                          # Ĝ
        XmlHtmlEntityBuild1('gcirc', 285),                                                          # ĝ
        XmlHtmlEntityBuild1('Gcy', 1043),                                                           # Г
        XmlHtmlEntityBuild1('gcy', 1075),                                                           # г
        XmlHtmlEntityBuild1('Gdot', 288),                                                           # Ġ
        XmlHtmlEntityBuild1('gdot', 289),                                                           # ġ
        XmlHtmlEntityBuild1('gE', 8807),                                                            # ≧
        XmlHtmlEntityBuild1('ge', 8805),                                                            # ≥
        XmlHtmlEntityBuild1('gEl', 10892),                                                          # ⪌
        XmlHtmlEntityBuild1('gel', 8923),                                                           # ⋛
        XmlHtmlEntityBuild1('geq', 8805),                                                           # ≥
        XmlHtmlEntityBuild1('geqq', 8807),                                                          # ≧
        XmlHtmlEntityBuild1('geqslant', 10878),                                                     # ⩾
        XmlHtmlEntityBuild1('ges', 10878),                                                          # ⩾
        XmlHtmlEntityBuild1('gescc', 10921),                                                        # ⪩
        XmlHtmlEntityBuild1('gesdot', 10880),                                                       # ⪀
        XmlHtmlEntityBuild1('gesdoto', 10882),                                                      # ⪂
        XmlHtmlEntityBuild1('gesdotol', 10884),                                                     # ⪄
        XmlHtmlEntityBuild2('gesl', '⋛︀'),                                                           # ⋛︀
        XmlHtmlEntityBuild1('gesles', 10900),                                                       # ⪔
        XmlHtmlEntityBuild1('Gfr', 120074),                                                         # 𝔊
        XmlHtmlEntityBuild1('gfr', 120100),                                                         # 𝔤
        XmlHtmlEntityBuild1('Gg', 8921),                                                            # ⋙
        XmlHtmlEntityBuild1('gg', 8811),                                                            # ≫
        XmlHtmlEntityBuild1('ggg', 8921),                                                           # ⋙
        XmlHtmlEntityBuild1('gimel', 8503),                                                         # ℷ
        XmlHtmlEntityBuild1('GJcy', 1027),                                                          # Ѓ
        XmlHtmlEntityBuild1('gjcy', 1107),                                                          # ѓ
        XmlHtmlEntityBuild1('gl', 8823),                                                            # ≷
        XmlHtmlEntityBuild1('gla', 10917),                                                          # ⪥
        XmlHtmlEntityBuild1('glE', 10898),                                                          # ⪒
        XmlHtmlEntityBuild1('glj', 10916),                                                          # ⪤
        XmlHtmlEntityBuild1('gnap', 10890),                                                         # ⪊
        XmlHtmlEntityBuild1('gnapprox', 10890),                                                     # ⪊
        XmlHtmlEntityBuild1('gnE', 8809),                                                           # ≩
        XmlHtmlEntityBuild1('gne', 10888),                                                          # ⪈
        XmlHtmlEntityBuild1('gneq', 10888),                                                         # ⪈
        XmlHtmlEntityBuild1('gneqq', 8809),                                                         # ≩
        XmlHtmlEntityBuild1('gnsim', 8935),                                                         # ⋧
        XmlHtmlEntityBuild1('Gopf', 120126),                                                        # 𝔾
        XmlHtmlEntityBuild1('gopf', 120152),                                                        # 𝕘
        XmlHtmlEntityBuild1('grave', 96),                                                           # `
        XmlHtmlEntityBuild1('GreaterEqual', 8805),                                                  # ≥
        XmlHtmlEntityBuild1('GreaterEqualLess', 8923),                                              # ⋛
        XmlHtmlEntityBuild1('GreaterFullEqual', 8807),                                              # ≧
        XmlHtmlEntityBuild1('GreaterGreater', 10914),                                               # ⪢
        XmlHtmlEntityBuild1('GreaterLess', 8823),                                                   # ≷
        XmlHtmlEntityBuild1('GreaterSlantEqual', 10878),                                            # ⩾
        XmlHtmlEntityBuild1('GreaterTilde', 8819),                                                  # ≳
        XmlHtmlEntityBuild1('Gscr', 119970),                                                        # 𝒢
        XmlHtmlEntityBuild1('gscr', 8458),                                                          # ℊ
        XmlHtmlEntityBuild1('gsim', 8819),                                                          # ≳
        XmlHtmlEntityBuild1('gsime', 10894),                                                        # ⪎
        XmlHtmlEntityBuild1('gsiml', 10896),                                                        # ⪐
        XmlHtmlEntityBuild1('Gt', 8811),                                                            # ≫
        XmlHtmlEntityBuild1('gtcc', 10919),                                                         # ⪧
        XmlHtmlEntityBuild1('gtcir', 10874),                                                        # ⩺
        XmlHtmlEntityBuild1('gtdot', 8919),                                                         # ⋗
        XmlHtmlEntityBuild1('gtlPar', 10645),                                                       # ⦕
        XmlHtmlEntityBuild1('gtquest', 10876),                                                      # ⩼
        XmlHtmlEntityBuild1('gtrapprox', 10886),                                                    # ⪆
        XmlHtmlEntityBuild1('gtrarr', 10616),                                                       # ⥸
        XmlHtmlEntityBuild1('gtrdot', 8919),                                                        # ⋗
        XmlHtmlEntityBuild1('gtreqless', 8923),                                                     # ⋛
        XmlHtmlEntityBuild1('gtreqqless', 10892),                                                   # ⪌
        XmlHtmlEntityBuild1('gtrless', 8823),                                                       # ≷
        XmlHtmlEntityBuild1('gtrsim', 8819),                                                        # ≳
        XmlHtmlEntityBuild2('gvertneqq', '≩︀'),                                                      # ≩︀
        XmlHtmlEntityBuild2('gvnE', '≩︀'),                                                           # ≩︀
        XmlHtmlEntityBuild1('Hacek', 711),                                                          # ˇ
        XmlHtmlEntityBuild1('hairsp', 8202),                                                        #  
        XmlHtmlEntityBuild1('half', 189),                                                           # ½
        XmlHtmlEntityBuild1('hamilt', 8459),                                                        # ℋ
        XmlHtmlEntityBuild1('HARDcy', 1066),                                                        # Ъ
        XmlHtmlEntityBuild1('hardcy', 1098),                                                        # ъ
        XmlHtmlEntityBuild1('hArr', 8660),                                                          # ⇔
        XmlHtmlEntityBuild1('harr', 8596),                                                          # ↔
        XmlHtmlEntityBuild1('harrcir', 10568),                                                      # ⥈
        XmlHtmlEntityBuild1('harrw', 8621),                                                         # ↭
        XmlHtmlEntityBuild1('Hat', 94),                                                             # ^
        XmlHtmlEntityBuild1('hbar', 8463),                                                          # ℏ
        XmlHtmlEntityBuild1('Hcirc', 292),                                                          # Ĥ
        XmlHtmlEntityBuild1('hcirc', 293),                                                          # ĥ
        XmlHtmlEntityBuild1('heartsuit', 9829),                                                     # ♥
        XmlHtmlEntityBuild1('hercon', 8889),                                                        # ⊹
        XmlHtmlEntityBuild1('Hfr', 8460),                                                           # ℌ
        XmlHtmlEntityBuild1('hfr', 120101),                                                         # 𝔥
        XmlHtmlEntityBuild1('HilbertSpace', 8459),                                                  # ℋ
        XmlHtmlEntityBuild1('hksearow', 10533),                                                     # ⤥
        XmlHtmlEntityBuild1('hkswarow', 10534),                                                     # ⤦
        XmlHtmlEntityBuild1('hoarr', 8703),                                                         # ⇿
        XmlHtmlEntityBuild1('homtht', 8763),                                                        # ∻
        XmlHtmlEntityBuild1('hookleftarrow', 8617),                                                 # ↩
        XmlHtmlEntityBuild1('hookrightarrow', 8618),                                                # ↪
        XmlHtmlEntityBuild1('Hopf', 8461),                                                          # ℍ
        XmlHtmlEntityBuild1('hopf', 120153),                                                        # 𝕙
        XmlHtmlEntityBuild1('horbar', 8213),                                                        # ―
        XmlHtmlEntityBuild1('HorizontalLine', 9472),                                                # ─
        XmlHtmlEntityBuild1('Hscr', 8459),                                                          # ℋ
        XmlHtmlEntityBuild1('hscr', 119997),                                                        # 𝒽
        XmlHtmlEntityBuild1('hslash', 8463),                                                        # ℏ
        XmlHtmlEntityBuild1('Hstrok', 294),                                                         # Ħ
        XmlHtmlEntityBuild1('hstrok', 295),                                                         # ħ
        XmlHtmlEntityBuild1('HumpDownHump', 8782),                                                  # ≎
        XmlHtmlEntityBuild1('HumpEqual', 8783),                                                     # ≏
        XmlHtmlEntityBuild1('hybull', 8259),                                                        # ⁃
        XmlHtmlEntityBuild1('hyphen', 8208),                                                        # ‐
        XmlHtmlEntityBuild1('ic', 8291),                                                            # ⁣
        XmlHtmlEntityBuild1('Icy', 1048),                                                           # И
        XmlHtmlEntityBuild1('icy', 1080),                                                           # и
        XmlHtmlEntityBuild1('Idot', 304),                                                           # İ
        XmlHtmlEntityBuild1('IEcy', 1045),                                                          # Е
        XmlHtmlEntityBuild1('iecy', 1077),                                                          # е
        XmlHtmlEntityBuild1('iff', 8660),                                                           # ⇔
        XmlHtmlEntityBuild1('Ifr', 8465),                                                           # ℑ
        XmlHtmlEntityBuild1('ifr', 120102),                                                         # 𝔦
        XmlHtmlEntityBuild1('ii', 8520),                                                            # ⅈ
        XmlHtmlEntityBuild1('iiiint', 10764),                                                       # ⨌
        XmlHtmlEntityBuild1('iiint', 8749),                                                         # ∭
        XmlHtmlEntityBuild1('iinfin', 10716),                                                       # ⧜
        XmlHtmlEntityBuild1('iiota', 8489),                                                         # ℩
        XmlHtmlEntityBuild1('IJlig', 306),                                                          # Ĳ
        XmlHtmlEntityBuild1('ijlig', 307),                                                          # ĳ
        XmlHtmlEntityBuild1('Im', 8465),                                                            # ℑ
        XmlHtmlEntityBuild1('Imacr', 298),                                                          # Ī
        XmlHtmlEntityBuild1('imacr', 299),                                                          # ī
        XmlHtmlEntityBuild1('ImaginaryI', 8520),                                                    # ⅈ
        XmlHtmlEntityBuild1('imagline', 8464),                                                      # ℐ
        XmlHtmlEntityBuild1('imagpart', 8465),                                                      # ℑ
        XmlHtmlEntityBuild1('imath', 305),                                                          # ı
        XmlHtmlEntityBuild1('imof', 8887),                                                          # ⊷
        XmlHtmlEntityBuild1('imped', 437),                                                          # Ƶ
        XmlHtmlEntityBuild1('Implies', 8658),                                                       # ⇒
        XmlHtmlEntityBuild1('in', 8712),                                                            # ∈
        XmlHtmlEntityBuild1('incare', 8453),                                                        # ℅
        XmlHtmlEntityBuild1('infin', 8734),                                                         # ∞
        XmlHtmlEntityBuild1('infintie', 10717),                                                     # ⧝
        XmlHtmlEntityBuild1('inodot', 305),                                                         # ı
        XmlHtmlEntityBuild1('Int', 8748),                                                           # ∬
        XmlHtmlEntityBuild1('int', 8747),                                                           # ∫
        XmlHtmlEntityBuild1('intcal', 8890),                                                        # ⊺
        XmlHtmlEntityBuild1('integers', 8484),                                                      # ℤ
        XmlHtmlEntityBuild1('Integral', 8747),                                                      # ∫
        XmlHtmlEntityBuild1('intercal', 8890),                                                      # ⊺
        XmlHtmlEntityBuild1('Intersection', 8898),                                                  # ⋂
        XmlHtmlEntityBuild1('intlarhk', 10775),                                                     # ⨗
        XmlHtmlEntityBuild1('intprod', 10812),                                                      # ⨼
        XmlHtmlEntityBuild1('InvisibleComma', 8291),                                                # ⁣
        XmlHtmlEntityBuild1('InvisibleTimes', 8290),                                                # ⁢
        XmlHtmlEntityBuild1('IOcy', 1025),                                                          # Ё
        XmlHtmlEntityBuild1('iocy', 1105),                                                          # ё
        XmlHtmlEntityBuild1('Iogon', 302),                                                          # Į
        XmlHtmlEntityBuild1('iogon', 303),                                                          # į
        XmlHtmlEntityBuild1('Iopf', 120128),                                                        # 𝕀
        XmlHtmlEntityBuild1('iopf', 120154),                                                        # 𝕚
        XmlHtmlEntityBuild1('iprod', 10812),                                                        # ⨼
        XmlHtmlEntityBuild1('Iscr', 8464),                                                          # ℐ
        XmlHtmlEntityBuild1('iscr', 119998),                                                        # 𝒾
        XmlHtmlEntityBuild1('isin', 8712),                                                          # ∈
        XmlHtmlEntityBuild1('isindot', 8949),                                                       # ⋵
        XmlHtmlEntityBuild1('isinE', 8953),                                                         # ⋹
        XmlHtmlEntityBuild1('isins', 8948),                                                         # ⋴
        XmlHtmlEntityBuild1('isinsv', 8947),                                                        # ⋳
        XmlHtmlEntityBuild1('isinv', 8712),                                                         # ∈
        XmlHtmlEntityBuild1('it', 8290),                                                            # ⁢
        XmlHtmlEntityBuild1('Itilde', 296),                                                         # Ĩ
        XmlHtmlEntityBuild1('itilde', 297),                                                         # ĩ
        XmlHtmlEntityBuild1('Iukcy', 1030),                                                         # І
        XmlHtmlEntityBuild1('iukcy', 1110),                                                         # і
        XmlHtmlEntityBuild1('Jcirc', 308),                                                          # Ĵ
        XmlHtmlEntityBuild1('jcirc', 309),                                                          # ĵ
        XmlHtmlEntityBuild1('Jcy', 1049),                                                           # Й
        XmlHtmlEntityBuild1('jcy', 1081),                                                           # й
        XmlHtmlEntityBuild1('Jfr', 120077),                                                         # 𝔍
        XmlHtmlEntityBuild1('jfr', 120103),                                                         # 𝔧
        XmlHtmlEntityBuild1('jmath', 567),                                                          # ȷ
        XmlHtmlEntityBuild1('Jopf', 120129),                                                        # 𝕁
        XmlHtmlEntityBuild1('jopf', 120155),                                                        # 𝕛
        XmlHtmlEntityBuild1('Jscr', 119973),                                                        # 𝒥
        XmlHtmlEntityBuild1('jscr', 119999),                                                        # 𝒿
        XmlHtmlEntityBuild1('Jsercy', 1032),                                                        # Ј
        XmlHtmlEntityBuild1('jsercy', 1112),                                                        # ј
        XmlHtmlEntityBuild1('Jukcy', 1028),                                                         # Є
        XmlHtmlEntityBuild1('jukcy', 1108),                                                         # є
        XmlHtmlEntityBuild1('kappav', 1008),                                                        # ϰ
        XmlHtmlEntityBuild1('Kcedil', 310),                                                         # Ķ
        XmlHtmlEntityBuild1('kcedil', 311),                                                         # ķ
        XmlHtmlEntityBuild1('Kcy', 1050),                                                           # К
        XmlHtmlEntityBuild1('kcy', 1082),                                                           # к
        XmlHtmlEntityBuild1('Kfr', 120078),                                                         # 𝔎
        XmlHtmlEntityBuild1('kfr', 120104),                                                         # 𝔨
        XmlHtmlEntityBuild1('kgreen', 312),                                                         # ĸ
        XmlHtmlEntityBuild1('KHcy', 1061),                                                          # Х
        XmlHtmlEntityBuild1('khcy', 1093),                                                          # х
        XmlHtmlEntityBuild1('KJcy', 1036),                                                          # Ќ
        XmlHtmlEntityBuild1('kjcy', 1116),                                                          # ќ
        XmlHtmlEntityBuild1('Kopf', 120130),                                                        # 𝕂
        XmlHtmlEntityBuild1('kopf', 120156),                                                        # 𝕜
        XmlHtmlEntityBuild1('Kscr', 119974),                                                        # 𝒦
        XmlHtmlEntityBuild1('kscr', 120000),                                                        # 𝓀
        XmlHtmlEntityBuild1('lAarr', 8666),                                                         # ⇚
        XmlHtmlEntityBuild1('Lacute', 313),                                                         # Ĺ
        XmlHtmlEntityBuild1('lacute', 314),                                                         # ĺ
        XmlHtmlEntityBuild1('laemptyv', 10676),                                                     # ⦴
        XmlHtmlEntityBuild1('lagran', 8466),                                                        # ℒ
        XmlHtmlEntityBuild1('Lang', 10218),                                                         # ⟪
        XmlHtmlEntityBuild1('langd', 10641),                                                        # ⦑
        XmlHtmlEntityBuild1('langle', 10216),                                                       # ⟨
        XmlHtmlEntityBuild1('lap', 10885),                                                          # ⪅
        XmlHtmlEntityBuild1('Laplacetrf', 8466),                                                    # ℒ
        XmlHtmlEntityBuild1('Larr', 8606),                                                          # ↞
        XmlHtmlEntityBuild1('lArr', 8656),                                                          # ⇐
        XmlHtmlEntityBuild1('larr', 8592),                                                          # ←
        XmlHtmlEntityBuild1('larrb', 8676),                                                         # ⇤
        XmlHtmlEntityBuild1('larrbfs', 10527),                                                      # ⤟
        XmlHtmlEntityBuild1('larrfs', 10525),                                                       # ⤝
        XmlHtmlEntityBuild1('larrhk', 8617),                                                        # ↩
        XmlHtmlEntityBuild1('larrlp', 8619),                                                        # ↫
        XmlHtmlEntityBuild1('larrpl', 10553),                                                       # ⤹
        XmlHtmlEntityBuild1('larrsim', 10611),                                                      # ⥳
        XmlHtmlEntityBuild1('larrtl', 8610),                                                        # ↢
        XmlHtmlEntityBuild1('lat', 10923),                                                          # ⪫
        XmlHtmlEntityBuild1('lAtail', 10523),                                                       # ⤛
        XmlHtmlEntityBuild1('latail', 10521),                                                       # ⤙
        XmlHtmlEntityBuild1('late', 10925),                                                         # ⪭
        XmlHtmlEntityBuild2('lates', '⪭︀'),                                                          # ⪭︀
        XmlHtmlEntityBuild1('lBarr', 10510),                                                        # ⤎
        XmlHtmlEntityBuild1('lbarr', 10508),                                                        # ⤌
        XmlHtmlEntityBuild1('lbbrk', 10098),                                                        # ❲
        XmlHtmlEntityBuild1('lbrace', 123),                                                         # {
        XmlHtmlEntityBuild1('lbrack', 91),                                                          # [
        XmlHtmlEntityBuild1('lbrke', 10635),                                                        # ⦋
        XmlHtmlEntityBuild1('lbrksld', 10639),                                                      # ⦏
        XmlHtmlEntityBuild1('lbrkslu', 10637),                                                      # ⦍
        XmlHtmlEntityBuild1('Lcaron', 317),                                                         # Ľ
        XmlHtmlEntityBuild1('lcaron', 318),                                                         # ľ
        XmlHtmlEntityBuild1('Lcedil', 315),                                                         # Ļ
        XmlHtmlEntityBuild1('lcedil', 316),                                                         # ļ
        XmlHtmlEntityBuild1('lceil', 8968),                                                         # ⌈
        XmlHtmlEntityBuild1('lcub', 123),                                                           # {
        XmlHtmlEntityBuild1('Lcy', 1051),                                                           # Л
        XmlHtmlEntityBuild1('lcy', 1083),                                                           # л
        XmlHtmlEntityBuild1('ldca', 10550),                                                         # ⤶
        XmlHtmlEntityBuild1('ldquor', 8222),                                                        # „
        XmlHtmlEntityBuild1('ldrdhar', 10599),                                                      # ⥧
        XmlHtmlEntityBuild1('ldrushar', 10571),                                                     # ⥋
        XmlHtmlEntityBuild1('ldsh', 8626),                                                          # ↲
        XmlHtmlEntityBuild1('lE', 8806),                                                            # ≦
        XmlHtmlEntityBuild1('le', 8804),                                                            # ≤
        XmlHtmlEntityBuild1('LeftAngleBracket', 10216),                                             # ⟨
        XmlHtmlEntityBuild1('LeftArrow', 8592),                                                     # ←
        XmlHtmlEntityBuild1('Leftarrow', 8656),                                                     # ⇐
        XmlHtmlEntityBuild1('leftarrow', 8592),                                                     # ←
        XmlHtmlEntityBuild1('LeftArrowBar', 8676),                                                  # ⇤
        XmlHtmlEntityBuild1('LeftArrowRightArrow', 8646),                                           # ⇆
        XmlHtmlEntityBuild1('leftarrowtail', 8610),                                                 # ↢
        XmlHtmlEntityBuild1('LeftCeiling', 8968),                                                   # ⌈
        XmlHtmlEntityBuild1('LeftDoubleBracket', 10214),                                            # ⟦
        XmlHtmlEntityBuild1('LeftDownTeeVector', 10593),                                            # ⥡
        XmlHtmlEntityBuild1('LeftDownVector', 8643),                                                # ⇃
        XmlHtmlEntityBuild1('LeftDownVectorBar', 10585),                                            # ⥙
        XmlHtmlEntityBuild1('LeftFloor', 8970),                                                     # ⌊
        XmlHtmlEntityBuild1('leftharpoondown', 8637),                                               # ↽
        XmlHtmlEntityBuild1('leftharpoonup', 8636),                                                 # ↼
        XmlHtmlEntityBuild1('leftleftarrows', 8647),                                                # ⇇
        XmlHtmlEntityBuild1('LeftRightArrow', 8596),                                                # ↔
        XmlHtmlEntityBuild1('Leftrightarrow', 8660),                                                # ⇔
        XmlHtmlEntityBuild1('leftrightarrow', 8596),                                                # ↔
        XmlHtmlEntityBuild1('leftrightarrows', 8646),                                               # ⇆
        XmlHtmlEntityBuild1('leftrightharpoons', 8651),                                             # ⇋
        XmlHtmlEntityBuild1('leftrightsquigarrow', 8621),                                           # ↭
        XmlHtmlEntityBuild1('LeftRightVector', 10574),                                              # ⥎
        XmlHtmlEntityBuild1('LeftTee', 8867),                                                       # ⊣
        XmlHtmlEntityBuild1('LeftTeeArrow', 8612),                                                  # ↤
        XmlHtmlEntityBuild1('LeftTeeVector', 10586),                                                # ⥚
        XmlHtmlEntityBuild1('leftthreetimes', 8907),                                                # ⋋
        XmlHtmlEntityBuild1('LeftTriangle', 8882),                                                  # ⊲
        XmlHtmlEntityBuild1('LeftTriangleBar', 10703),                                              # ⧏
        XmlHtmlEntityBuild1('LeftTriangleEqual', 8884),                                             # ⊴
        XmlHtmlEntityBuild1('LeftUpDownVector', 10577),                                             # ⥑
        XmlHtmlEntityBuild1('LeftUpTeeVector', 10592),                                              # ⥠
        XmlHtmlEntityBuild1('LeftUpVector', 8639),                                                  # ↿
        XmlHtmlEntityBuild1('LeftUpVectorBar', 10584),                                              # ⥘
        XmlHtmlEntityBuild1('LeftVector', 8636),                                                    # ↼
        XmlHtmlEntityBuild1('LeftVectorBar', 10578),                                                # ⥒
        XmlHtmlEntityBuild1('lEg', 10891),                                                          # ⪋
        XmlHtmlEntityBuild1('leg', 8922),                                                           # ⋚
        XmlHtmlEntityBuild1('leq', 8804),                                                           # ≤
        XmlHtmlEntityBuild1('leqq', 8806),                                                          # ≦
        XmlHtmlEntityBuild1('leqslant', 10877),                                                     # ⩽
        XmlHtmlEntityBuild1('les', 10877),                                                          # ⩽
        XmlHtmlEntityBuild1('lescc', 10920),                                                        # ⪨
        XmlHtmlEntityBuild1('lesdot', 10879),                                                       # ⩿
        XmlHtmlEntityBuild1('lesdoto', 10881),                                                      # ⪁
        XmlHtmlEntityBuild1('lesdotor', 10883),                                                     # ⪃
        XmlHtmlEntityBuild2('lesg', '⋚︀'),                                                           # ⋚︀
        XmlHtmlEntityBuild1('lesges', 10899),                                                       # ⪓
        XmlHtmlEntityBuild1('lessapprox', 10885),                                                   # ⪅
        XmlHtmlEntityBuild1('lessdot', 8918),                                                       # ⋖
        XmlHtmlEntityBuild1('lesseqgtr', 8922),                                                     # ⋚
        XmlHtmlEntityBuild1('lesseqqgtr', 10891),                                                   # ⪋
        XmlHtmlEntityBuild1('LessEqualGreater', 8922),                                              # ⋚
        XmlHtmlEntityBuild1('LessFullEqual', 8806),                                                 # ≦
        XmlHtmlEntityBuild1('LessGreater', 8822),                                                   # ≶
        XmlHtmlEntityBuild1('lessgtr', 8822),                                                       # ≶
        XmlHtmlEntityBuild1('LessLess', 10913),                                                     # ⪡
        XmlHtmlEntityBuild1('lesssim', 8818),                                                       # ≲
        XmlHtmlEntityBuild1('LessSlantEqual', 10877),                                               # ⩽
        XmlHtmlEntityBuild1('LessTilde', 8818),                                                     # ≲
        XmlHtmlEntityBuild1('lfisht', 10620),                                                       # ⥼
        XmlHtmlEntityBuild1('lfloor', 8970),                                                        # ⌊
        XmlHtmlEntityBuild1('Lfr', 120079),                                                         # 𝔏
        XmlHtmlEntityBuild1('lfr', 120105),                                                         # 𝔩
        XmlHtmlEntityBuild1('lg', 8822),                                                            # ≶
        XmlHtmlEntityBuild1('lgE', 10897),                                                          # ⪑
        XmlHtmlEntityBuild1('lHar', 10594),                                                         # ⥢
        XmlHtmlEntityBuild1('lhard', 8637),                                                         # ↽
        XmlHtmlEntityBuild1('lharu', 8636),                                                         # ↼
        XmlHtmlEntityBuild1('lharul', 10602),                                                       # ⥪
        XmlHtmlEntityBuild1('lhblk', 9604),                                                         # ▄
        XmlHtmlEntityBuild1('LJcy', 1033),                                                          # Љ
        XmlHtmlEntityBuild1('ljcy', 1113),                                                          # љ
        XmlHtmlEntityBuild1('Ll', 8920),                                                            # ⋘
        XmlHtmlEntityBuild1('ll', 8810),                                                            # ≪
        XmlHtmlEntityBuild1('llarr', 8647),                                                         # ⇇
        XmlHtmlEntityBuild1('llcorner', 8990),                                                      # ⌞
        XmlHtmlEntityBuild1('Lleftarrow', 8666),                                                    # ⇚
        XmlHtmlEntityBuild1('llhard', 10603),                                                       # ⥫
        XmlHtmlEntityBuild1('lltri', 9722),                                                         # ◺
        XmlHtmlEntityBuild1('Lmidot', 319),                                                         # Ŀ
        XmlHtmlEntityBuild1('lmidot', 320),                                                         # ŀ
        XmlHtmlEntityBuild1('lmoust', 9136),                                                        # ⎰
        XmlHtmlEntityBuild1('lmoustache', 9136),                                                    # ⎰
        XmlHtmlEntityBuild1('lnap', 10889),                                                         # ⪉
        XmlHtmlEntityBuild1('lnapprox', 10889),                                                     # ⪉
        XmlHtmlEntityBuild1('lnE', 8808),                                                           # ≨
        XmlHtmlEntityBuild1('lne', 10887),                                                          # ⪇
        XmlHtmlEntityBuild1('lneq', 10887),                                                         # ⪇
        XmlHtmlEntityBuild1('lneqq', 8808),                                                         # ≨
        XmlHtmlEntityBuild1('lnsim', 8934),                                                         # ⋦
        XmlHtmlEntityBuild1('loang', 10220),                                                        # ⟬
        XmlHtmlEntityBuild1('loarr', 8701),                                                         # ⇽
        XmlHtmlEntityBuild1('lobrk', 10214),                                                        # ⟦
        XmlHtmlEntityBuild1('LongLeftArrow', 10229),                                                # ⟵
        XmlHtmlEntityBuild1('Longleftarrow', 10232),                                                # ⟸
        XmlHtmlEntityBuild1('longleftarrow', 10229),                                                # ⟵
        XmlHtmlEntityBuild1('LongLeftRightArrow', 10231),                                           # ⟷
        XmlHtmlEntityBuild1('Longleftrightarrow', 10234),                                           # ⟺
        XmlHtmlEntityBuild1('longleftrightarrow', 10231),                                           # ⟷
        XmlHtmlEntityBuild1('longmapsto', 10236),                                                   # ⟼
        XmlHtmlEntityBuild1('LongRightArrow', 10230),                                               # ⟶
        XmlHtmlEntityBuild1('Longrightarrow', 10233),                                               # ⟹
        XmlHtmlEntityBuild1('longrightarrow', 10230),                                               # ⟶
        XmlHtmlEntityBuild1('looparrowleft', 8619),                                                 # ↫
        XmlHtmlEntityBuild1('looparrowright', 8620),                                                # ↬
        XmlHtmlEntityBuild1('lopar', 10629),                                                        # ⦅
        XmlHtmlEntityBuild1('Lopf', 120131),                                                        # 𝕃
        XmlHtmlEntityBuild1('lopf', 120157),                                                        # 𝕝
        XmlHtmlEntityBuild1('loplus', 10797),                                                       # ⨭
        XmlHtmlEntityBuild1('lotimes', 10804),                                                      # ⨴
        XmlHtmlEntityBuild1('lowast', 8727),                                                        # ∗
        XmlHtmlEntityBuild1('lowbar', 95),                                                          # _
        XmlHtmlEntityBuild1('LowerLeftArrow', 8601),                                                # ↙
        XmlHtmlEntityBuild1('LowerRightArrow', 8600),                                               # ↘
        XmlHtmlEntityBuild1('lozenge', 9674),                                                       # ◊
        XmlHtmlEntityBuild1('lozf', 10731),                                                         # ⧫
        XmlHtmlEntityBuild1('lpar', 40),                                                            # (
        XmlHtmlEntityBuild1('lparlt', 10643),                                                       # ⦓
        XmlHtmlEntityBuild1('lrarr', 8646),                                                         # ⇆
        XmlHtmlEntityBuild1('lrcorner', 8991),                                                      # ⌟
        XmlHtmlEntityBuild1('lrhar', 8651),                                                         # ⇋
        XmlHtmlEntityBuild1('lrhard', 10605),                                                       # ⥭
        XmlHtmlEntityBuild1('lrtri', 8895),                                                         # ⊿
        XmlHtmlEntityBuild1('Lscr', 8466),                                                          # ℒ
        XmlHtmlEntityBuild1('lscr', 120001),                                                        # 𝓁
        XmlHtmlEntityBuild1('Lsh', 8624),                                                           # ↰
        XmlHtmlEntityBuild1('lsh', 8624),                                                           # ↰
        XmlHtmlEntityBuild1('lsim', 8818),                                                          # ≲
        XmlHtmlEntityBuild1('lsime', 10893),                                                        # ⪍
        XmlHtmlEntityBuild1('lsimg', 10895),                                                        # ⪏
        XmlHtmlEntityBuild1('lsqb', 91),                                                            # [
        XmlHtmlEntityBuild1('lsquor', 8218),                                                        # ‚
        XmlHtmlEntityBuild1('Lstrok', 321),                                                         # Ł
        XmlHtmlEntityBuild1('lstrok', 322),                                                         # ł
        XmlHtmlEntityBuild1('Lt', 8810),                                                            # ≪
        XmlHtmlEntityBuild1('ltcc', 10918),                                                         # ⪦
        XmlHtmlEntityBuild1('ltcir', 10873),                                                        # ⩹
        XmlHtmlEntityBuild1('ltdot', 8918),                                                         # ⋖
        XmlHtmlEntityBuild1('lthree', 8907),                                                        # ⋋
        XmlHtmlEntityBuild1('ltimes', 8905),                                                        # ⋉
        XmlHtmlEntityBuild1('ltlarr', 10614),                                                       # ⥶
        XmlHtmlEntityBuild1('ltquest', 10875),                                                      # ⩻
        XmlHtmlEntityBuild1('ltri', 9667),                                                          # ◃
        XmlHtmlEntityBuild1('ltrie', 8884),                                                         # ⊴
        XmlHtmlEntityBuild1('ltrif', 9666),                                                         # ◂
        XmlHtmlEntityBuild1('ltrPar', 10646),                                                       # ⦖
        XmlHtmlEntityBuild1('lurdshar', 10570),                                                     # ⥊
        XmlHtmlEntityBuild1('luruhar', 10598),                                                      # ⥦
        XmlHtmlEntityBuild2('lvertneqq', '≨︀'),                                                      # ≨︀
        XmlHtmlEntityBuild2('lvnE', '≨︀'),                                                           # ≨︀
        XmlHtmlEntityBuild1('male', 9794),                                                          # ♂
        XmlHtmlEntityBuild1('malt', 10016),                                                         # ✠
        XmlHtmlEntityBuild1('maltese', 10016),                                                      # ✠
        XmlHtmlEntityBuild1('Map', 10501),                                                          # ⤅
        XmlHtmlEntityBuild1('map', 8614),                                                           # ↦
        XmlHtmlEntityBuild1('mapsto', 8614),                                                        # ↦
        XmlHtmlEntityBuild1('mapstodown', 8615),                                                    # ↧
        XmlHtmlEntityBuild1('mapstoleft', 8612),                                                    # ↤
        XmlHtmlEntityBuild1('mapstoup', 8613),                                                      # ↥
        XmlHtmlEntityBuild1('marker', 9646),                                                        # ▮
        XmlHtmlEntityBuild1('mcomma', 10793),                                                       # ⨩
        XmlHtmlEntityBuild1('Mcy', 1052),                                                           # М
        XmlHtmlEntityBuild1('mcy', 1084),                                                           # м
        XmlHtmlEntityBuild1('mDDot', 8762),                                                         # ∺
        XmlHtmlEntityBuild1('measuredangle', 8737),                                                 # ∡
        XmlHtmlEntityBuild1('MediumSpace', 8287),                                                   #  
        XmlHtmlEntityBuild1('Mellintrf', 8499),                                                     # ℳ
        XmlHtmlEntityBuild1('Mfr', 120080),                                                         # 𝔐
        XmlHtmlEntityBuild1('mfr', 120106),                                                         # 𝔪
        XmlHtmlEntityBuild1('mho', 8487),                                                           # ℧
        XmlHtmlEntityBuild1('mid', 8739),                                                           # ∣
        XmlHtmlEntityBuild1('midast', 42),                                                          # *
        XmlHtmlEntityBuild1('midcir', 10992),                                                       # ⫰
        XmlHtmlEntityBuild1('minus', 8722),                                                         # −
        XmlHtmlEntityBuild1('minusb', 8863),                                                        # ⊟
        XmlHtmlEntityBuild1('minusd', 8760),                                                        # ∸
        XmlHtmlEntityBuild1('minusdu', 10794),                                                      # ⨪
        XmlHtmlEntityBuild1('MinusPlus', 8723),                                                     # ∓
        XmlHtmlEntityBuild1('mlcp', 10971),                                                         # ⫛
        XmlHtmlEntityBuild1('mldr', 8230),                                                          # …
        XmlHtmlEntityBuild1('mnplus', 8723),                                                        # ∓
        XmlHtmlEntityBuild1('models', 8871),                                                        # ⊧
        XmlHtmlEntityBuild1('Mopf', 120132),                                                        # 𝕄
        XmlHtmlEntityBuild1('mopf', 120158),                                                        # 𝕞
        XmlHtmlEntityBuild1('mp', 8723),                                                            # ∓
        XmlHtmlEntityBuild1('Mscr', 8499),                                                          # ℳ
        XmlHtmlEntityBuild1('mscr', 120002),                                                        # 𝓂
        XmlHtmlEntityBuild1('mstpos', 8766),                                                        # ∾
        XmlHtmlEntityBuild1('multimap', 8888),                                                      # ⊸
        XmlHtmlEntityBuild1('mumap', 8888),                                                         # ⊸
        XmlHtmlEntityBuild1('nabla', 8711),                                                         # ∇
        XmlHtmlEntityBuild1('Nacute', 323),                                                         # Ń
        XmlHtmlEntityBuild1('nacute', 324),                                                         # ń
        XmlHtmlEntityBuild2('nang', '∠⃒'),                                                           # ∠⃒
        XmlHtmlEntityBuild1('nap', 8777),                                                           # ≉
        XmlHtmlEntityBuild2('napE', '⩰̸'),                                                           # ⩰̸
        XmlHtmlEntityBuild2('napid', '≋̸'),                                                          # ≋̸
        XmlHtmlEntityBuild1('napos', 329),                                                          # ŉ
        XmlHtmlEntityBuild1('napprox', 8777),                                                       # ≉
        XmlHtmlEntityBuild1('natur', 9838),                                                         # ♮
        XmlHtmlEntityBuild1('natural', 9838),                                                       # ♮
        XmlHtmlEntityBuild1('naturals', 8469),                                                      # ℕ
        XmlHtmlEntityBuild2('nbump', '≎̸'),                                                          # ≎̸
        XmlHtmlEntityBuild2('nbumpe', '≏̸'),                                                         # ≏̸
        XmlHtmlEntityBuild1('ncap', 10819),                                                         # ⩃
        XmlHtmlEntityBuild1('Ncaron', 327),                                                         # Ň
        XmlHtmlEntityBuild1('ncaron', 328),                                                         # ň
        XmlHtmlEntityBuild1('Ncedil', 325),                                                         # Ņ
        XmlHtmlEntityBuild1('ncedil', 326),                                                         # ņ
        XmlHtmlEntityBuild1('ncong', 8775),                                                         # ≇
        XmlHtmlEntityBuild2('ncongdot', '⩭̸'),                                                       # ⩭̸
        XmlHtmlEntityBuild1('ncup', 10818),                                                         # ⩂
        XmlHtmlEntityBuild1('Ncy', 1053),                                                           # Н
        XmlHtmlEntityBuild1('ncy', 1085),                                                           # н
        XmlHtmlEntityBuild1('ne', 8800),                                                            # ≠
        XmlHtmlEntityBuild1('nearhk', 10532),                                                       # ⤤
        XmlHtmlEntityBuild1('neArr', 8663),                                                         # ⇗
        XmlHtmlEntityBuild1('nearr', 8599),                                                         # ↗
        XmlHtmlEntityBuild1('nearrow', 8599),                                                       # ↗
        XmlHtmlEntityBuild2('nedot', '≐̸'),                                                          # ≐̸
        XmlHtmlEntityBuild1('NegativeMediumSpace', 8203),                                           # ​
        XmlHtmlEntityBuild1('NegativeThickSpace', 8203),                                            # ​
        XmlHtmlEntityBuild1('NegativeThinSpace', 8203),                                             # ​
        XmlHtmlEntityBuild1('NegativeVeryThinSpace', 8203),                                         # ​
        XmlHtmlEntityBuild1('nequiv', 8802),                                                        # ≢
        XmlHtmlEntityBuild1('nesear', 10536),                                                       # ⤨
        XmlHtmlEntityBuild2('nesim', '≂̸'),                                                          # ≂̸
        XmlHtmlEntityBuild1('NestedGreaterGreater', 8811),                                          # ≫
        XmlHtmlEntityBuild1('NestedLessLess', 8810),                                                # ≪
        XmlHtmlEntityBuild1('NewLine', 10),                                                         # 
        XmlHtmlEntityBuild1('nexist', 8708),                                                        # ∄
        XmlHtmlEntityBuild1('nexists', 8708),                                                       # ∄
        XmlHtmlEntityBuild1('Nfr', 120081),                                                         # 𝔑
        XmlHtmlEntityBuild1('nfr', 120107),                                                         # 𝔫
        XmlHtmlEntityBuild2('ngE', '≧̸'),                                                            # ≧̸
        XmlHtmlEntityBuild1('nge', 8817),                                                           # ≱
        XmlHtmlEntityBuild1('ngeq', 8817),                                                          # ≱
        XmlHtmlEntityBuild2('ngeqq', '≧̸'),                                                          # ≧̸
        XmlHtmlEntityBuild2('ngeqslant', '⩾̸'),                                                      # ⩾̸
        XmlHtmlEntityBuild2('nges', '⩾̸'),                                                           # ⩾̸
        XmlHtmlEntityBuild2('nGg', '⋙̸'),                                                            # ⋙̸
        XmlHtmlEntityBuild1('ngsim', 8821),                                                         # ≵
        XmlHtmlEntityBuild2('nGt', '≫⃒'),                                                            # ≫⃒
        XmlHtmlEntityBuild1('ngt', 8815),                                                           # ≯
        XmlHtmlEntityBuild1('ngtr', 8815),                                                          # ≯
        XmlHtmlEntityBuild2('nGtv', '≫̸'),                                                           # ≫̸
        XmlHtmlEntityBuild1('nhArr', 8654),                                                         # ⇎
        XmlHtmlEntityBuild1('nharr', 8622),                                                         # ↮
        XmlHtmlEntityBuild1('nhpar', 10994),                                                        # ⫲
        XmlHtmlEntityBuild1('ni', 8715),                                                            # ∋
        XmlHtmlEntityBuild1('nis', 8956),                                                           # ⋼
        XmlHtmlEntityBuild1('nisd', 8954),                                                          # ⋺
        XmlHtmlEntityBuild1('niv', 8715),                                                           # ∋
        XmlHtmlEntityBuild1('NJcy', 1034),                                                          # Њ
        XmlHtmlEntityBuild1('njcy', 1114),                                                          # њ
        XmlHtmlEntityBuild1('nlArr', 8653),                                                         # ⇍
        XmlHtmlEntityBuild1('nlarr', 8602),                                                         # ↚
        XmlHtmlEntityBuild1('nldr', 8229),                                                          # ‥
        XmlHtmlEntityBuild2('nlE', '≦̸'),                                                            # ≦̸
        XmlHtmlEntityBuild1('nle', 8816),                                                           # ≰
        XmlHtmlEntityBuild1('nLeftarrow', 8653),                                                    # ⇍
        XmlHtmlEntityBuild1('nleftarrow', 8602),                                                    # ↚
        XmlHtmlEntityBuild1('nLeftrightarrow', 8654),                                               # ⇎
        XmlHtmlEntityBuild1('nleftrightarrow', 8622),                                               # ↮
        XmlHtmlEntityBuild1('nleq', 8816),                                                          # ≰
        XmlHtmlEntityBuild2('nleqq', '≦̸'),                                                          # ≦̸
        XmlHtmlEntityBuild2('nleqslant', '⩽̸'),                                                      # ⩽̸
        XmlHtmlEntityBuild2('nles', '⩽̸'),                                                           # ⩽̸
        XmlHtmlEntityBuild1('nless', 8814),                                                         # ≮
        XmlHtmlEntityBuild2('nLl', '⋘̸'),                                                            # ⋘̸
        XmlHtmlEntityBuild1('nlsim', 8820),                                                         # ≴
        XmlHtmlEntityBuild2('nLt', '≪⃒'),                                                            # ≪⃒
        XmlHtmlEntityBuild1('nlt', 8814),                                                           # ≮
        XmlHtmlEntityBuild1('nltri', 8938),                                                         # ⋪
        XmlHtmlEntityBuild1('nltrie', 8940),                                                        # ⋬
        XmlHtmlEntityBuild2('nLtv', '≪̸'),                                                           # ≪̸
        XmlHtmlEntityBuild1('nmid', 8740),                                                          # ∤
        XmlHtmlEntityBuild1('NoBreak', 8288),                                                       # ⁠
        XmlHtmlEntityBuild1('NonBreakingSpace', 160),                                               #  
        XmlHtmlEntityBuild1('Nopf', 8469),                                                          # ℕ
        XmlHtmlEntityBuild1('nopf', 120159),                                                        # 𝕟
        XmlHtmlEntityBuild1('Not', 10988),                                                          # ⫬
        XmlHtmlEntityBuild1('NotCongruent', 8802),                                                  # ≢
        XmlHtmlEntityBuild1('NotCupCap', 8813),                                                     # ≭
        XmlHtmlEntityBuild1('NotDoubleVerticalBar', 8742),                                          # ∦
        XmlHtmlEntityBuild1('NotElement', 8713),                                                    # ∉
        XmlHtmlEntityBuild1('NotEqual', 8800),                                                      # ≠
        XmlHtmlEntityBuild2('NotEqualTilde', '≂̸'),                                                  # ≂̸
        XmlHtmlEntityBuild1('NotExists', 8708),                                                     # ∄
        XmlHtmlEntityBuild1('NotGreater', 8815),                                                    # ≯
        XmlHtmlEntityBuild1('NotGreaterEqual', 8817),                                               # ≱
        XmlHtmlEntityBuild2('NotGreaterFullEqual', '≧̸'),                                            # ≧̸
        XmlHtmlEntityBuild2('NotGreaterGreater', '≫̸'),                                              # ≫̸
        XmlHtmlEntityBuild1('NotGreaterLess', 8825),                                                # ≹
        XmlHtmlEntityBuild2('NotGreaterSlantEqual', '⩾̸'),                                           # ⩾̸
        XmlHtmlEntityBuild1('NotGreaterTilde', 8821),                                               # ≵
        XmlHtmlEntityBuild2('NotHumpDownHump', '≎̸'),                                                # ≎̸
        XmlHtmlEntityBuild2('NotHumpEqual', '≏̸'),                                                   # ≏̸
        XmlHtmlEntityBuild1('notin', 8713),                                                         # ∉
        XmlHtmlEntityBuild2('notindot', '⋵̸'),                                                       # ⋵̸
        XmlHtmlEntityBuild2('notinE', '⋹̸'),                                                         # ⋹̸
        XmlHtmlEntityBuild1('notinva', 8713),                                                       # ∉
        XmlHtmlEntityBuild1('notinvb', 8951),                                                       # ⋷
        XmlHtmlEntityBuild1('notinvc', 8950),                                                       # ⋶
        XmlHtmlEntityBuild1('NotLeftTriangle', 8938),                                               # ⋪
        XmlHtmlEntityBuild2('NotLeftTriangleBar', '⧏̸'),                                             # ⧏̸
        XmlHtmlEntityBuild1('NotLeftTriangleEqual', 8940),                                          # ⋬
        XmlHtmlEntityBuild1('NotLess', 8814),                                                       # ≮
        XmlHtmlEntityBuild1('NotLessEqual', 8816),                                                  # ≰
        XmlHtmlEntityBuild1('NotLessGreater', 8824),                                                # ≸
        XmlHtmlEntityBuild2('NotLessLess', '≪̸'),                                                    # ≪̸
        XmlHtmlEntityBuild2('NotLessSlantEqual', '⩽̸'),                                              # ⩽̸
        XmlHtmlEntityBuild1('NotLessTilde', 8820),                                                  # ≴
        XmlHtmlEntityBuild2('NotNestedGreaterGreater', '⪢̸'),                                        # ⪢̸
        XmlHtmlEntityBuild2('NotNestedLessLess', '⪡̸'),                                              # ⪡̸
        XmlHtmlEntityBuild1('notni', 8716),                                                         # ∌
        XmlHtmlEntityBuild1('notniva', 8716),                                                       # ∌
        XmlHtmlEntityBuild1('notnivb', 8958),                                                       # ⋾
        XmlHtmlEntityBuild1('notnivc', 8957),                                                       # ⋽
        XmlHtmlEntityBuild1('NotPrecedes', 8832),                                                   # ⊀
        XmlHtmlEntityBuild2('NotPrecedesEqual', '⪯̸'),                                               # ⪯̸
        XmlHtmlEntityBuild1('NotPrecedesSlantEqual', 8928),                                         # ⋠
        XmlHtmlEntityBuild1('NotReverseElement', 8716),                                             # ∌
        XmlHtmlEntityBuild1('NotRightTriangle', 8939),                                              # ⋫
        XmlHtmlEntityBuild2('NotRightTriangleBar', '⧐̸'),                                            # ⧐̸
        XmlHtmlEntityBuild1('NotRightTriangleEqual', 8941),                                         # ⋭
        XmlHtmlEntityBuild2('NotSquareSubset', '⊏̸'),                                                # ⊏̸
        XmlHtmlEntityBuild1('NotSquareSubsetEqual', 8930),                                          # ⋢
        XmlHtmlEntityBuild2('NotSquareSuperset', '⊐̸'),                                              # ⊐̸
        XmlHtmlEntityBuild1('NotSquareSupersetEqual', 8931),                                        # ⋣
        XmlHtmlEntityBuild2('NotSubset', '⊂⃒'),                                                      # ⊂⃒
        XmlHtmlEntityBuild1('NotSubsetEqual', 8840),                                                # ⊈
        XmlHtmlEntityBuild1('NotSucceeds', 8833),                                                   # ⊁
        XmlHtmlEntityBuild2('NotSucceedsEqual', '⪰̸'),                                               # ⪰̸
        XmlHtmlEntityBuild1('NotSucceedsSlantEqual', 8929),                                         # ⋡
        XmlHtmlEntityBuild2('NotSucceedsTilde', '≿̸'),                                               # ≿̸
        XmlHtmlEntityBuild2('NotSuperset', '⊃⃒'),                                                    # ⊃⃒
        XmlHtmlEntityBuild1('NotSupersetEqual', 8841),                                              # ⊉
        XmlHtmlEntityBuild1('NotTilde', 8769),                                                      # ≁
        XmlHtmlEntityBuild1('NotTildeEqual', 8772),                                                 # ≄
        XmlHtmlEntityBuild1('NotTildeFullEqual', 8775),                                             # ≇
        XmlHtmlEntityBuild1('NotTildeTilde', 8777),                                                 # ≉
        XmlHtmlEntityBuild1('NotVerticalBar', 8740),                                                # ∤
        XmlHtmlEntityBuild1('npar', 8742),                                                          # ∦
        XmlHtmlEntityBuild1('nparallel', 8742),                                                     # ∦
        XmlHtmlEntityBuild2('nparsl', '⫽⃥'),                                                         # ⫽⃥
        XmlHtmlEntityBuild2('npart', '∂̸'),                                                          # ∂̸
        XmlHtmlEntityBuild1('npolint', 10772),                                                      # ⨔
        XmlHtmlEntityBuild1('npr', 8832),                                                           # ⊀
        XmlHtmlEntityBuild1('nprcue', 8928),                                                        # ⋠
        XmlHtmlEntityBuild2('npre', '⪯̸'),                                                           # ⪯̸
        XmlHtmlEntityBuild1('nprec', 8832),                                                         # ⊀
        XmlHtmlEntityBuild2('npreceq', '⪯̸'),                                                        # ⪯̸
        XmlHtmlEntityBuild1('nrArr', 8655),                                                         # ⇏
        XmlHtmlEntityBuild1('nrarr', 8603),                                                         # ↛
        XmlHtmlEntityBuild2('nrarrc', '⤳̸'),                                                         # ⤳̸
        XmlHtmlEntityBuild2('nrarrw', '↝̸'),                                                         # ↝̸
        XmlHtmlEntityBuild1('nRightarrow', 8655),                                                   # ⇏
        XmlHtmlEntityBuild1('nrightarrow', 8603),                                                   # ↛
        XmlHtmlEntityBuild1('nrtri', 8939),                                                         # ⋫
        XmlHtmlEntityBuild1('nrtrie', 8941),                                                        # ⋭
        XmlHtmlEntityBuild1('nsc', 8833),                                                           # ⊁
        XmlHtmlEntityBuild1('nsccue', 8929),                                                        # ⋡
        XmlHtmlEntityBuild2('nsce', '⪰̸'),                                                           # ⪰̸
        XmlHtmlEntityBuild1('Nscr', 119977),                                                        # 𝒩
        XmlHtmlEntityBuild1('nscr', 120003),                                                        # 𝓃
        XmlHtmlEntityBuild1('nshortmid', 8740),                                                     # ∤
        XmlHtmlEntityBuild1('nshortparallel', 8742),                                                # ∦
        XmlHtmlEntityBuild1('nsim', 8769),                                                          # ≁
        XmlHtmlEntityBuild1('nsime', 8772),                                                         # ≄
        XmlHtmlEntityBuild1('nsimeq', 8772),                                                        # ≄
        XmlHtmlEntityBuild1('nsmid', 8740),                                                         # ∤
        XmlHtmlEntityBuild1('nspar', 8742),                                                         # ∦
        XmlHtmlEntityBuild1('nsqsube', 8930),                                                       # ⋢
        XmlHtmlEntityBuild1('nsqsupe', 8931),                                                       # ⋣
        XmlHtmlEntityBuild1('nsub', 8836),                                                          # ⊄
        XmlHtmlEntityBuild2('nsubE', '⫅̸'),                                                          # ⫅̸
        XmlHtmlEntityBuild1('nsube', 8840),                                                         # ⊈
        XmlHtmlEntityBuild2('nsubset', '⊂⃒'),                                                        # ⊂⃒
        XmlHtmlEntityBuild1('nsubseteq', 8840),                                                     # ⊈
        XmlHtmlEntityBuild2('nsubseteqq', '⫅̸'),                                                     # ⫅̸
        XmlHtmlEntityBuild1('nsucc', 8833),                                                         # ⊁
        XmlHtmlEntityBuild2('nsucceq', '⪰̸'),                                                        # ⪰̸
        XmlHtmlEntityBuild1('nsup', 8837),                                                          # ⊅
        XmlHtmlEntityBuild2('nsupE', '⫆̸'),                                                          # ⫆̸
        XmlHtmlEntityBuild1('nsupe', 8841),                                                         # ⊉
        XmlHtmlEntityBuild2('nsupset', '⊃⃒'),                                                        # ⊃⃒
        XmlHtmlEntityBuild1('nsupseteq', 8841),                                                     # ⊉
        XmlHtmlEntityBuild2('nsupseteqq', '⫆̸'),                                                     # ⫆̸
        XmlHtmlEntityBuild1('ntgl', 8825),                                                          # ≹
        XmlHtmlEntityBuild1('ntlg', 8824),                                                          # ≸
        XmlHtmlEntityBuild1('ntriangleleft', 8938),                                                 # ⋪
        XmlHtmlEntityBuild1('ntrianglelefteq', 8940),                                               # ⋬
        XmlHtmlEntityBuild1('ntriangleright', 8939),                                                # ⋫
        XmlHtmlEntityBuild1('ntrianglerighteq', 8941),                                              # ⋭
        XmlHtmlEntityBuild1('num', 35),                                                             # #
        XmlHtmlEntityBuild1('numero', 8470),                                                        # №
        XmlHtmlEntityBuild1('numsp', 8199),                                                         #  
        XmlHtmlEntityBuild2('nvap', '≍⃒'),                                                           # ≍⃒
        XmlHtmlEntityBuild1('nVDash', 8879),                                                        # ⊯
        XmlHtmlEntityBuild1('nVdash', 8878),                                                        # ⊮
        XmlHtmlEntityBuild1('nvDash', 8877),                                                        # ⊭
        XmlHtmlEntityBuild1('nvdash', 8876),                                                        # ⊬
        XmlHtmlEntityBuild2('nvge', '≥⃒'),                                                           # ≥⃒
        XmlHtmlEntityBuild2('nvgt', '>⃒'),                                                           # >⃒
        XmlHtmlEntityBuild1('nvHarr', 10500),                                                       # ⤄
        XmlHtmlEntityBuild1('nvinfin', 10718),                                                      # ⧞
        XmlHtmlEntityBuild1('nvlArr', 10498),                                                       # ⤂
        XmlHtmlEntityBuild2('nvle', '≤⃒'),                                                           # ≤⃒
        XmlHtmlEntityBuild2('nvlt', '<⃒'),                                                           # <⃒
        XmlHtmlEntityBuild2('nvltrie', '⊴⃒'),                                                        # ⊴⃒
        XmlHtmlEntityBuild1('nvrArr', 10499),                                                           # ⤃
        XmlHtmlEntityBuild2('nvrtrie', '⊵⃒'),                                                        # ⊵⃒
        XmlHtmlEntityBuild2('nvsim', '∼⃒'),                                                          # ∼⃒
        XmlHtmlEntityBuild1('nwarhk', 10531),                                                       # ⤣
        XmlHtmlEntityBuild1('nwArr', 8662),                                                         # ⇖
        XmlHtmlEntityBuild1('nwarr', 8598),                                                         # ↖
        XmlHtmlEntityBuild1('nwarrow', 8598),                                                       # ↖
        XmlHtmlEntityBuild1('nwnear', 10535),                                                       # ⤧
        XmlHtmlEntityBuild1('oast', 8859),                                                          # ⊛
        XmlHtmlEntityBuild1('ocir', 8858),                                                          # ⊚
        XmlHtmlEntityBuild1('Ocy', 1054),                                                           # О
        XmlHtmlEntityBuild1('ocy', 1086),                                                           # о
        XmlHtmlEntityBuild1('odash', 8861),                                                         # ⊝
        XmlHtmlEntityBuild1('Odblac', 336),                                                         # Ő
        XmlHtmlEntityBuild1('odblac', 337),                                                         # ő
        XmlHtmlEntityBuild1('odiv', 10808),                                                         # ⨸
        XmlHtmlEntityBuild1('odot', 8857),                                                          # ⊙
        XmlHtmlEntityBuild1('odsold', 10684),                                                       # ⦼
        XmlHtmlEntityBuild1('ofcir', 10687),                                                        # ⦿
        XmlHtmlEntityBuild1('Ofr', 120082),                                                         # 𝔒
        XmlHtmlEntityBuild1('ofr', 120108),                                                         # 𝔬
        XmlHtmlEntityBuild1('ogon', 731),                                                           # ˛
        XmlHtmlEntityBuild1('ogt', 10689),                                                          # ⧁
        XmlHtmlEntityBuild1('ohbar', 10677),                                                        # ⦵
        XmlHtmlEntityBuild1('oint', 8750),                                                          # ∮
        XmlHtmlEntityBuild1('olarr', 8634),                                                         # ↺
        XmlHtmlEntityBuild1('olcir', 10686),                                                        # ⦾
        XmlHtmlEntityBuild1('olcross', 10683),                                                      # ⦻
        XmlHtmlEntityBuild1('olt', 10688),                                                          # ⧀
        XmlHtmlEntityBuild1('Omacr', 332),                                                          # Ō
        XmlHtmlEntityBuild1('omacr', 333),                                                          # ō
        XmlHtmlEntityBuild1('omid', 10678),                                                         # ⦶
        XmlHtmlEntityBuild1('ominus', 8854),                                                        # ⊖
        XmlHtmlEntityBuild1('Oopf', 120134),                                                        # 𝕆
        XmlHtmlEntityBuild1('oopf', 120160),                                                        # 𝕠
        XmlHtmlEntityBuild1('opar', 10679),                                                         # ⦷
        XmlHtmlEntityBuild1('OpenCurlyDoubleQuote', 8220),                                          # “
        XmlHtmlEntityBuild1('OpenCurlyQuote', 8216),                                                # ‘
        XmlHtmlEntityBuild1('operp', 10681),                                                        # ⦹
        XmlHtmlEntityBuild1('oplus', 8853),                                                         # ⊕
        XmlHtmlEntityBuild1('Or', 10836),                                                           # ⩔
        XmlHtmlEntityBuild1('or', 8744),                                                            # ∨
        XmlHtmlEntityBuild1('orarr', 8635),                                                         # ↻
        XmlHtmlEntityBuild1('ord', 10845),                                                          # ⩝
        XmlHtmlEntityBuild1('order', 8500),                                                         # ℴ
        XmlHtmlEntityBuild1('orderof', 8500),                                                       # ℴ
        XmlHtmlEntityBuild1('origof', 8886),                                                        # ⊶
        XmlHtmlEntityBuild1('oror', 10838),                                                         # ⩖
        XmlHtmlEntityBuild1('orslope', 10839),                                                      # ⩗
        XmlHtmlEntityBuild1('orv', 10843),                                                          # ⩛
        XmlHtmlEntityBuild1('oS', 9416),                                                            # Ⓢ
        XmlHtmlEntityBuild1('Oscr', 119978),                                                        # 𝒪
        XmlHtmlEntityBuild1('oscr', 8500),                                                          # ℴ
        XmlHtmlEntityBuild1('osol', 8856),                                                          # ⊘
        XmlHtmlEntityBuild1('Otimes', 10807),                                                       # ⨷
        XmlHtmlEntityBuild1('otimes', 8855),                                                        # ⊗
        XmlHtmlEntityBuild1('otimesas', 10806),                                                     # ⨶
        XmlHtmlEntityBuild1('ovbar', 9021),                                                         # ⌽
        XmlHtmlEntityBuild1('OverBar', 8254),                                                       # ‾
        XmlHtmlEntityBuild1('OverBrace', 9182),                                                     # ⏞
        XmlHtmlEntityBuild1('OverBracket', 9140),                                                   # ⎴
        XmlHtmlEntityBuild1('OverParenthesis', 9180),                                               # ⏜
        XmlHtmlEntityBuild1('par', 8741),                                                           # ∥
        XmlHtmlEntityBuild1('parallel', 8741),                                                      # ∥
        XmlHtmlEntityBuild1('parsim', 10995),                                                       # ⫳
        XmlHtmlEntityBuild1('parsl', 11005),                                                        # ⫽
        XmlHtmlEntityBuild1('part', 8706),                                                          # ∂
        XmlHtmlEntityBuild1('PartialD', 8706),                                                      # ∂
        XmlHtmlEntityBuild1('Pcy', 1055),                                                           # П
        XmlHtmlEntityBuild1('pcy', 1087),                                                           # п
        XmlHtmlEntityBuild1('percnt', 37),                                                          # %
        XmlHtmlEntityBuild1('period', 46),                                                          # .
        XmlHtmlEntityBuild1('perp', 8869),                                                          # ⊥
        XmlHtmlEntityBuild1('pertenk', 8241),                                                       # ‱
        XmlHtmlEntityBuild1('Pfr', 120083),                                                         # 𝔓
        XmlHtmlEntityBuild1('pfr', 120109),                                                         # 𝔭
        XmlHtmlEntityBuild1('phmmat', 8499),                                                        # ℳ
        XmlHtmlEntityBuild1('phone', 9742),                                                         # ☎
        XmlHtmlEntityBuild1('pitchfork', 8916),                                                     # ⋔
        XmlHtmlEntityBuild1('piv', 982),                                                            # ϖ
        XmlHtmlEntityBuild1('planck', 8463),                                                        # ℏ
        XmlHtmlEntityBuild1('planckh', 8462),                                                       # ℎ
        XmlHtmlEntityBuild1('plankv', 8463),                                                        # ℏ
        XmlHtmlEntityBuild1('plus', 43),                                                            # +
        XmlHtmlEntityBuild1('plusacir', 10787),                                                     # ⨣
        XmlHtmlEntityBuild1('plusb', 8862),                                                         # ⊞
        XmlHtmlEntityBuild1('pluscir', 10786),                                                      # ⨢
        XmlHtmlEntityBuild1('plusdo', 8724),                                                        # ∔
        XmlHtmlEntityBuild1('plusdu', 10789),                                                       # ⨥
        XmlHtmlEntityBuild1('pluse', 10866),                                                        # ⩲
        XmlHtmlEntityBuild1('PlusMinus', 177),                                                      # ±
        XmlHtmlEntityBuild1('plussim', 10790),                                                      # ⨦
        XmlHtmlEntityBuild1('plustwo', 10791),                                                      # ⨧
        XmlHtmlEntityBuild1('pm', 177),                                                             # ±
        XmlHtmlEntityBuild1('Poincareplane', 8460),                                                 # ℌ
        XmlHtmlEntityBuild1('pointint', 10773),                                                     # ⨕
        XmlHtmlEntityBuild1('Popf', 8473),                                                          # ℙ
        XmlHtmlEntityBuild1('popf', 120161),                                                        # 𝕡
        XmlHtmlEntityBuild1('Pr', 10939),                                                           # ⪻
        XmlHtmlEntityBuild1('pr', 8826),                                                            # ≺
        XmlHtmlEntityBuild1('prap', 10935),                                                         # ⪷
        XmlHtmlEntityBuild1('prcue', 8828),                                                         # ≼
        XmlHtmlEntityBuild1('prE', 10931),                                                          # ⪳
        XmlHtmlEntityBuild1('pre', 10927),                                                          # ⪯
        XmlHtmlEntityBuild1('prec', 8826),                                                          # ≺
        XmlHtmlEntityBuild1('precapprox', 10935),                                                   # ⪷
        XmlHtmlEntityBuild1('preccurlyeq', 8828),                                                   # ≼
        XmlHtmlEntityBuild1('Precedes', 8826),                                                      # ≺
        XmlHtmlEntityBuild1('PrecedesEqual', 10927),                                                # ⪯
        XmlHtmlEntityBuild1('PrecedesSlantEqual', 8828),                                            # ≼
        XmlHtmlEntityBuild1('PrecedesTilde', 8830),                                                 # ≾
        XmlHtmlEntityBuild1('preceq', 10927),                                                       # ⪯
        XmlHtmlEntityBuild1('precnapprox', 10937),                                                  # ⪹
        XmlHtmlEntityBuild1('precneqq', 10933),                                                     # ⪵
        XmlHtmlEntityBuild1('precnsim', 8936),                                                      # ⋨
        XmlHtmlEntityBuild1('precsim', 8830),                                                       # ≾
        XmlHtmlEntityBuild1('primes', 8473),                                                        # ℙ
        XmlHtmlEntityBuild1('prnap', 10937),                                                        # ⪹
        XmlHtmlEntityBuild1('prnE', 10933),                                                         # ⪵
        XmlHtmlEntityBuild1('prnsim', 8936),                                                        # ⋨
        XmlHtmlEntityBuild1('prod', 8719),                                                          # ∏
        XmlHtmlEntityBuild1('Product', 8719),                                                       # ∏
        XmlHtmlEntityBuild1('profalar', 9006),                                                      # ⌮
        XmlHtmlEntityBuild1('profline', 8978),                                                      # ⌒
        XmlHtmlEntityBuild1('profsurf', 8979),                                                      # ⌓
        XmlHtmlEntityBuild1('prop', 8733),                                                          # ∝
        XmlHtmlEntityBuild1('Proportion', 8759),                                                    # ∷
        XmlHtmlEntityBuild1('Proportional', 8733),                                                  # ∝
        XmlHtmlEntityBuild1('propto', 8733),                                                        # ∝
        XmlHtmlEntityBuild1('prsim', 8830),                                                         # ≾
        XmlHtmlEntityBuild1('prurel', 8880),                                                        # ⊰
        XmlHtmlEntityBuild1('Pscr', 119979),                                                        # 𝒫
        XmlHtmlEntityBuild1('pscr', 120005),                                                        # 𝓅
        XmlHtmlEntityBuild1('puncsp', 8200),                                                        #  
        XmlHtmlEntityBuild1('Qfr', 120084),                                                         # 𝔔
        XmlHtmlEntityBuild1('qfr', 120110),                                                         # 𝔮
        XmlHtmlEntityBuild1('qint', 10764),                                                         # ⨌
        XmlHtmlEntityBuild1('Qopf', 8474),                                                          # ℚ
        XmlHtmlEntityBuild1('qopf', 120162),                                                        # 𝕢
        XmlHtmlEntityBuild1('qprime', 8279),                                                        # ⁗
        XmlHtmlEntityBuild1('Qscr', 119980),                                                        # 𝒬
        XmlHtmlEntityBuild1('qscr', 120006),                                                        # 𝓆
        XmlHtmlEntityBuild1('quaternions', 8461),                                                   # ℍ
        XmlHtmlEntityBuild1('quatint', 10774),                                                      # ⨖
        XmlHtmlEntityBuild1('quest', 63),                                                           # ?
        XmlHtmlEntityBuild1('questeq', 8799),                                                       # ≟
        XmlHtmlEntityBuild1('rAarr', 8667),                                                         # ⇛
        XmlHtmlEntityBuild2('race', '∽̱'),                                                           # ∽̱
        XmlHtmlEntityBuild1('Racute', 340),                                                         # Ŕ
        XmlHtmlEntityBuild1('racute', 341),                                                         # ŕ
        XmlHtmlEntityBuild1('radic', 8730),                                                         # √
        XmlHtmlEntityBuild1('raemptyv', 10675),                                                     # ⦳
        XmlHtmlEntityBuild1('Rang', 10219),                                                         # ⟫
        XmlHtmlEntityBuild1('rangd', 10642),                                                        # ⦒
        XmlHtmlEntityBuild1('range', 10661),                                                        # ⦥
        XmlHtmlEntityBuild1('rangle', 10217),                                                       # ⟩
        XmlHtmlEntityBuild1('Rarr', 8608),                                                          # ↠
        XmlHtmlEntityBuild1('rArr', 8658),                                                          # ⇒
        XmlHtmlEntityBuild1('rarr', 8594),                                                          # →
        XmlHtmlEntityBuild1('rarrap', 10613),                                                       # ⥵
        XmlHtmlEntityBuild1('rarrb', 8677),                                                         # ⇥
        XmlHtmlEntityBuild1('rarrbfs', 10528),                                                      # ⤠
        XmlHtmlEntityBuild1('rarrc', 10547),                                                        # ⤳
        XmlHtmlEntityBuild1('rarrfs', 10526),                                                       # ⤞
        XmlHtmlEntityBuild1('rarrhk', 8618),                                                        # ↪
        XmlHtmlEntityBuild1('rarrlp', 8620),                                                        # ↬
        XmlHtmlEntityBuild1('rarrpl', 10565),                                                       # ⥅
        XmlHtmlEntityBuild1('rarrsim', 10612),                                                      # ⥴
        XmlHtmlEntityBuild1('Rarrtl', 10518),                                                       # ⤖
        XmlHtmlEntityBuild1('rarrtl', 8611),                                                        # ↣
        XmlHtmlEntityBuild1('rarrw', 8605),                                                         # ↝
        XmlHtmlEntityBuild1('rAtail', 10524),                                                       # ⤜
        XmlHtmlEntityBuild1('ratail', 10522),                                                       # ⤚
        XmlHtmlEntityBuild1('ratio', 8758),                                                         # ∶
        XmlHtmlEntityBuild1('rationals', 8474),                                                     # ℚ
        XmlHtmlEntityBuild1('RBarr', 10512),                                                        # ⤐
        XmlHtmlEntityBuild1('rBarr', 10511),                                                        # ⤏
        XmlHtmlEntityBuild1('rbarr', 10509),                                                        # ⤍
        XmlHtmlEntityBuild1('rbbrk', 10099),                                                        # ❳
        XmlHtmlEntityBuild1('rbrace', 125),                                                         # }
        XmlHtmlEntityBuild1('rbrack', 93),                                                          # ]
        XmlHtmlEntityBuild1('rbrke', 10636),                                                        # ⦌
        XmlHtmlEntityBuild1('rbrksld', 10638),                                                      # ⦎
        XmlHtmlEntityBuild1('rbrkslu', 10640),                                                      # ⦐
        XmlHtmlEntityBuild1('Rcaron', 344),                                                         # Ř
        XmlHtmlEntityBuild1('rcaron', 345),                                                         # ř
        XmlHtmlEntityBuild1('Rcedil', 342),                                                         # Ŗ
        XmlHtmlEntityBuild1('rcedil', 343),                                                         # ŗ
        XmlHtmlEntityBuild1('rceil', 8969),                                                         # ⌉
        XmlHtmlEntityBuild1('rcub', 125),                                                           # }
        XmlHtmlEntityBuild1('Rcy', 1056),                                                           # Р
        XmlHtmlEntityBuild1('rcy', 1088),                                                           # р
        XmlHtmlEntityBuild1('rdca', 10551),                                                         # ⤷
        XmlHtmlEntityBuild1('rdldhar', 10601),                                                      # ⥩
        XmlHtmlEntityBuild1('rdquor', 8221),                                                        # ”
        XmlHtmlEntityBuild1('rdsh', 8627),                                                          # ↳
        XmlHtmlEntityBuild1('Re', 8476),                                                            # ℜ
        XmlHtmlEntityBuild1('realine', 8475),                                                       # ℛ
        XmlHtmlEntityBuild1('realpart', 8476),                                                      # ℜ
        XmlHtmlEntityBuild1('reals', 8477),                                                         # ℝ
        XmlHtmlEntityBuild1('rect', 9645),                                                          # ▭
        XmlHtmlEntityBuild1('REG', 174),                                                            # ®
        XmlHtmlEntityBuild1('REG', 174),                                                            # ®
        XmlHtmlEntityBuild1('ReverseElement', 8715),                                                # ∋
        XmlHtmlEntityBuild1('ReverseEquilibrium', 8651),                                            # ⇋
        XmlHtmlEntityBuild1('ReverseUpEquilibrium', 10607),                                         # ⥯
        XmlHtmlEntityBuild1('rfisht', 10621),                                                       # ⥽
        XmlHtmlEntityBuild1('rfloor', 8971),                                                        # ⌋
        XmlHtmlEntityBuild1('Rfr', 8476),                                                           # ℜ
        XmlHtmlEntityBuild1('rfr', 120111),                                                         # 𝔯
        XmlHtmlEntityBuild1('rHar', 10596),                                                         # ⥤
        XmlHtmlEntityBuild1('rhard', 8641),                                                         # ⇁
        XmlHtmlEntityBuild1('rharu', 8640),                                                         # ⇀
        XmlHtmlEntityBuild1('rharul', 10604),                                                       # ⥬
        XmlHtmlEntityBuild1('rhov', 1009),                                                          # ϱ
        XmlHtmlEntityBuild1('RightAngleBracket', 10217),                                            # ⟩
        XmlHtmlEntityBuild1('RightArrow', 8594),                                                    # →
        XmlHtmlEntityBuild1('Rightarrow', 8658),                                                    # ⇒
        XmlHtmlEntityBuild1('rightarrow', 8594),                                                    # →
        XmlHtmlEntityBuild1('RightArrowBar', 8677),                                                 # ⇥
        XmlHtmlEntityBuild1('RightArrowLeftArrow', 8644),                                           # ⇄
        XmlHtmlEntityBuild1('rightarrowtail', 8611),                                                # ↣
        XmlHtmlEntityBuild1('RightCeiling', 8969),                                                  # ⌉
        XmlHtmlEntityBuild1('RightDoubleBracket', 10215),                                           # ⟧
        XmlHtmlEntityBuild1('RightDownTeeVector', 10589),                                           # ⥝
        XmlHtmlEntityBuild1('RightDownVector', 8642),                                               # ⇂
        XmlHtmlEntityBuild1('RightDownVectorBar', 10581),                                           # ⥕
        XmlHtmlEntityBuild1('RightFloor', 8971),                                                    # ⌋
        XmlHtmlEntityBuild1('rightharpoondown', 8641),                                              # ⇁
        XmlHtmlEntityBuild1('rightharpoonup', 8640),                                                # ⇀
        XmlHtmlEntityBuild1('rightleftarrows', 8644),                                               # ⇄
        XmlHtmlEntityBuild1('rightleftharpoons', 8652),                                             # ⇌
        XmlHtmlEntityBuild1('rightrightarrows', 8649),                                              # ⇉
        XmlHtmlEntityBuild1('rightsquigarrow', 8605),                                               # ↝
        XmlHtmlEntityBuild1('RightTee', 8866),                                                      # ⊢
        XmlHtmlEntityBuild1('RightTeeArrow', 8614),                                                 # ↦
        XmlHtmlEntityBuild1('RightTeeVector', 10587),                                               # ⥛
        XmlHtmlEntityBuild1('rightthreetimes', 8908),                                               # ⋌
        XmlHtmlEntityBuild1('RightTriangle', 8883),                                                 # ⊳
        XmlHtmlEntityBuild1('RightTriangleBar', 10704),                                             # ⧐
        XmlHtmlEntityBuild1('RightTriangleEqual', 8885),                                            # ⊵
        XmlHtmlEntityBuild1('RightUpDownVector', 10575),                                            # ⥏
        XmlHtmlEntityBuild1('RightUpTeeVector', 10588),                                             # ⥜
        XmlHtmlEntityBuild1('RightUpVector', 8638),                                                 # ↾
        XmlHtmlEntityBuild1('RightUpVectorBar', 10580),                                             # ⥔
        XmlHtmlEntityBuild1('RightVector', 8640),                                                   # ⇀
        XmlHtmlEntityBuild1('RightVectorBar', 10579),                                               # ⥓
        XmlHtmlEntityBuild1('ring', 730),                                                           # ˚
        XmlHtmlEntityBuild1('risingdotseq', 8787),                                                  # ≓
        XmlHtmlEntityBuild1('rlarr', 8644),                                                         # ⇄
        XmlHtmlEntityBuild1('rlhar', 8652),                                                         # ⇌
        XmlHtmlEntityBuild1('rmoust', 9137),                                                        # ⎱
        XmlHtmlEntityBuild1('rmoustache', 9137),                                                    # ⎱
        XmlHtmlEntityBuild1('rnmid', 10990),                                                        # ⫮
        XmlHtmlEntityBuild1('roang', 10221),                                                        # ⟭
        XmlHtmlEntityBuild1('roarr', 8702),                                                         # ⇾
        XmlHtmlEntityBuild1('robrk', 10215),                                                        # ⟧
        XmlHtmlEntityBuild1('ropar', 10630),                                                        # ⦆
        XmlHtmlEntityBuild1('Ropf', 8477),                                                          # ℝ
        XmlHtmlEntityBuild1('ropf', 120163),                                                        # 𝕣
        XmlHtmlEntityBuild1('roplus', 10798),                                                       # ⨮
        XmlHtmlEntityBuild1('rotimes', 10805),                                                      # ⨵
        XmlHtmlEntityBuild1('RoundImplies', 10608),                                                 # ⥰
        XmlHtmlEntityBuild1('rpar', 41),                                                            # )
        XmlHtmlEntityBuild1('rpargt', 10644),                                                       # ⦔
        XmlHtmlEntityBuild1('rppolint', 10770),                                                     # ⨒
        XmlHtmlEntityBuild1('rrarr', 8649),                                                         # ⇉
        XmlHtmlEntityBuild1('Rrightarrow', 8667),                                                   # ⇛
        XmlHtmlEntityBuild1('Rscr', 8475),                                                          # ℛ
        XmlHtmlEntityBuild1('rscr', 120007),                                                        # 𝓇
        XmlHtmlEntityBuild1('Rsh', 8625),                                                           # ↱
        XmlHtmlEntityBuild1('rsh', 8625),                                                           # ↱
        XmlHtmlEntityBuild1('rsqb', 93),                                                            # ]
        XmlHtmlEntityBuild1('rthree', 8908),                                                        # ⋌
        XmlHtmlEntityBuild1('rtimes', 8906),                                                        # ⋊
        XmlHtmlEntityBuild1('rtri', 9657),                                                          # ▹
        XmlHtmlEntityBuild1('rtrie', 8885),                                                         # ⊵
        XmlHtmlEntityBuild1('rtrif', 9656),                                                         # ▸
        XmlHtmlEntityBuild1('rtriltri', 10702),                                                     # ⧎
        XmlHtmlEntityBuild1('RuleDelayed', 10740),                                                  # ⧴
        XmlHtmlEntityBuild1('ruluhar', 10600),                                                      # ⥨
        XmlHtmlEntityBuild1('rx', 8478),                                                            # ℞
        XmlHtmlEntityBuild1('Sacute', 346),                                                         # Ś
        XmlHtmlEntityBuild1('sacute', 347),                                                         # ś
        XmlHtmlEntityBuild1('Sc', 10940),                                                           # ⪼
        XmlHtmlEntityBuild1('sc', 8827),                                                            # ≻
        XmlHtmlEntityBuild1('scap', 10936),                                                         # ⪸
        XmlHtmlEntityBuild1('sccue', 8829),                                                         # ≽
        XmlHtmlEntityBuild1('scE', 10932),                                                          # ⪴
        XmlHtmlEntityBuild1('sce', 10928),                                                          # ⪰
        XmlHtmlEntityBuild1('Scedil', 350),                                                         # Ş
        XmlHtmlEntityBuild1('scedil', 351),                                                         # ş
        XmlHtmlEntityBuild1('Scirc', 348),                                                          # Ŝ
        XmlHtmlEntityBuild1('scirc', 349),                                                          # ŝ
        XmlHtmlEntityBuild1('scnap', 10938),                                                        # ⪺
        XmlHtmlEntityBuild1('scnE', 10934),                                                         # ⪶
        XmlHtmlEntityBuild1('scnsim', 8937),                                                        # ⋩
        XmlHtmlEntityBuild1('scpolint', 10771),                                                     # ⨓
        XmlHtmlEntityBuild1('scsim', 8831),                                                         # ≿
        XmlHtmlEntityBuild1('Scy', 1057),                                                           # С
        XmlHtmlEntityBuild1('scy', 1089),                                                           # с
        XmlHtmlEntityBuild1('sdot', 8901),                                                          # ⋅
        XmlHtmlEntityBuild1('sdotb', 8865),                                                         # ⊡
        XmlHtmlEntityBuild1('sdote', 10854),                                                        # ⩦
        XmlHtmlEntityBuild1('searhk', 10533),                                                       # ⤥
        XmlHtmlEntityBuild1('seArr', 8664),                                                         # ⇘
        XmlHtmlEntityBuild1('searr', 8600),                                                         # ↘
        XmlHtmlEntityBuild1('searrow', 8600),                                                       # ↘
        XmlHtmlEntityBuild1('semi', 59),                                                            # ;
        XmlHtmlEntityBuild1('seswar', 10537),                                                       # ⤩
        XmlHtmlEntityBuild1('setminus', 8726),                                                      # ∖
        XmlHtmlEntityBuild1('setmn', 8726),                                                         # ∖
        XmlHtmlEntityBuild1('sext', 10038),                                                         # ✶
        XmlHtmlEntityBuild1('Sfr', 120086),                                                         # 𝔖
        XmlHtmlEntityBuild1('sfr', 120112),                                                         # 𝔰
        XmlHtmlEntityBuild1('sfrown', 8994),                                                        # ⌢
        XmlHtmlEntityBuild1('sharp', 9839),                                                         # ♯
        XmlHtmlEntityBuild1('SHCHcy', 1065),                                                        # Щ
        XmlHtmlEntityBuild1('shchcy', 1097),                                                        # щ
        XmlHtmlEntityBuild1('SHcy', 1064),                                                          # Ш
        XmlHtmlEntityBuild1('shcy', 1096),                                                          # ш
        XmlHtmlEntityBuild1('ShortDownArrow', 8595),                                                # ↓
        XmlHtmlEntityBuild1('ShortLeftArrow', 8592),                                                # ←
        XmlHtmlEntityBuild1('shortmid', 8739),                                                      # ∣
        XmlHtmlEntityBuild1('shortparallel', 8741),                                                 # ∥
        XmlHtmlEntityBuild1('ShortRightArrow', 8594),                                               # →
        XmlHtmlEntityBuild1('ShortUpArrow', 8593),                                                  # ↑
        XmlHtmlEntityBuild1('sim', 8764),                                                           # ∼
        XmlHtmlEntityBuild1('simdot', 10858),                                                       # ⩪
        XmlHtmlEntityBuild1('sime', 8771),                                                          # ≃
        XmlHtmlEntityBuild1('simeq', 8771),                                                         # ≃
        XmlHtmlEntityBuild1('simg', 10910),                                                         # ⪞
        XmlHtmlEntityBuild1('simgE', 10912),                                                        # ⪠
        XmlHtmlEntityBuild1('siml', 10909),                                                         # ⪝
        XmlHtmlEntityBuild1('simlE', 10911),                                                        # ⪟
        XmlHtmlEntityBuild1('simne', 8774),                                                         # ≆
        XmlHtmlEntityBuild1('simplus', 10788),                                                      # ⨤
        XmlHtmlEntityBuild1('simrarr', 10610),                                                      # ⥲
        XmlHtmlEntityBuild1('slarr', 8592),                                                         # ←
        XmlHtmlEntityBuild1('SmallCircle', 8728),                                                   # ∘
        XmlHtmlEntityBuild1('smallsetminus', 8726),                                                 # ∖
        XmlHtmlEntityBuild1('smashp', 10803),                                                       # ⨳
        XmlHtmlEntityBuild1('smeparsl', 10724),                                                     # ⧤
        XmlHtmlEntityBuild1('smid', 8739),                                                          # ∣
        XmlHtmlEntityBuild1('smile', 8995),                                                         # ⌣
        XmlHtmlEntityBuild1('smt', 10922),                                                          # ⪪
        XmlHtmlEntityBuild1('smte', 10924),                                                         # ⪬
        XmlHtmlEntityBuild2('smtes', '⪬︀'),                                                          # ⪬︀
        XmlHtmlEntityBuild1('SOFTcy', 1068),                                                        # Ь
        XmlHtmlEntityBuild1('softcy', 1100),                                                        # ь
        XmlHtmlEntityBuild1('sol', 47),                                                             # /
        XmlHtmlEntityBuild1('solb', 10692),                                                         # ⧄
        XmlHtmlEntityBuild1('solbar', 9023),                                                        # ⌿
        XmlHtmlEntityBuild1('Sopf', 120138),                                                        # 𝕊
        XmlHtmlEntityBuild1('sopf', 120164),                                                        # 𝕤
        XmlHtmlEntityBuild1('spadesuit', 9824),                                                     # ♠
        XmlHtmlEntityBuild1('spar', 8741),                                                          # ∥
        XmlHtmlEntityBuild1('sqcap', 8851),                                                         # ⊓
        XmlHtmlEntityBuild2('sqcaps', '⊓︀'),                                                         # ⊓︀
        XmlHtmlEntityBuild1('sqcup', 8852),                                                         # ⊔
        XmlHtmlEntityBuild2('sqcups', '⊔︀'),                                                         # ⊔︀
        XmlHtmlEntityBuild1('Sqrt', 8730),                                                          # √
        XmlHtmlEntityBuild1('sqsub', 8847),                                                         # ⊏
        XmlHtmlEntityBuild1('sqsube', 8849),                                                        # ⊑
        XmlHtmlEntityBuild1('sqsubset', 8847),                                                      # ⊏
        XmlHtmlEntityBuild1('sqsubseteq', 8849),                                                    # ⊑
        XmlHtmlEntityBuild1('sqsup', 8848),                                                         # ⊐
        XmlHtmlEntityBuild1('sqsupe', 8850),                                                        # ⊒
        XmlHtmlEntityBuild1('sqsupset', 8848),                                                      # ⊐
        XmlHtmlEntityBuild1('sqsupseteq', 8850),                                                    # ⊒
        XmlHtmlEntityBuild1('squ', 9633),                                                           # □
        XmlHtmlEntityBuild1('Square', 9633),                                                        # □
        XmlHtmlEntityBuild1('square', 9633),                                                        # □
        XmlHtmlEntityBuild1('SquareIntersection', 8851),                                            # ⊓
        XmlHtmlEntityBuild1('SquareSubset', 8847),                                                  # ⊏
        XmlHtmlEntityBuild1('SquareSubsetEqual', 8849),                                             # ⊑
        XmlHtmlEntityBuild1('SquareSuperset', 8848),                                                # ⊐
        XmlHtmlEntityBuild1('SquareSupersetEqual', 8850),                                           # ⊒
        XmlHtmlEntityBuild1('SquareUnion', 8852),                                                   # ⊔
        XmlHtmlEntityBuild1('squarf', 9642),                                                        # ▪
        XmlHtmlEntityBuild1('squf', 9642),                                                          # ▪
        XmlHtmlEntityBuild1('srarr', 8594),                                                         # →
        XmlHtmlEntityBuild1('Sscr', 119982),                                                        # 𝒮
        XmlHtmlEntityBuild1('sscr', 120008),                                                        # 𝓈
        XmlHtmlEntityBuild1('ssetmn', 8726),                                                        # ∖
        XmlHtmlEntityBuild1('ssmile', 8995),                                                        # ⌣
        XmlHtmlEntityBuild1('sstarf', 8902),                                                        # ⋆
        XmlHtmlEntityBuild1('Star', 8902),                                                          # ⋆
        XmlHtmlEntityBuild1('star', 9734),                                                          # ☆
        XmlHtmlEntityBuild1('starf', 9733),                                                         # ★
        XmlHtmlEntityBuild1('straightepsilon', 1013),                                               # ϵ
        XmlHtmlEntityBuild1('straightphi', 981),                                                    # ϕ
        XmlHtmlEntityBuild1('strns', 175),                                                          # ¯
        XmlHtmlEntityBuild1('Sub', 8912),                                                           # ⋐
        XmlHtmlEntityBuild1('sub', 8834),                                                           # ⊂
        XmlHtmlEntityBuild1('subdot', 10941),                                                       # ⪽
        XmlHtmlEntityBuild1('subE', 10949),                                                         # ⫅
        XmlHtmlEntityBuild1('sube', 8838),                                                          # ⊆
        XmlHtmlEntityBuild1('subedot', 10947),                                                      # ⫃
        XmlHtmlEntityBuild1('submult', 10945),                                                      # ⫁
        XmlHtmlEntityBuild1('subnE', 10955),                                                        # ⫋
        XmlHtmlEntityBuild1('subne', 8842),                                                         # ⊊
        XmlHtmlEntityBuild1('subplus', 10943),                                                      # ⪿
        XmlHtmlEntityBuild1('subrarr', 10617),                                                      # ⥹
        XmlHtmlEntityBuild1('Subset', 8912),                                                        # ⋐
        XmlHtmlEntityBuild1('subset', 8834),                                                        # ⊂
        XmlHtmlEntityBuild1('subseteq', 8838),                                                      # ⊆
        XmlHtmlEntityBuild1('subseteqq', 10949),                                                    # ⫅
        XmlHtmlEntityBuild1('SubsetEqual', 8838),                                                   # ⊆
        XmlHtmlEntityBuild1('subsetneq', 8842),                                                     # ⊊
        XmlHtmlEntityBuild1('subsetneqq', 10955),                                                   # ⫋
        XmlHtmlEntityBuild1('subsim', 10951),                                                       # ⫇
        XmlHtmlEntityBuild1('subsub', 10965),                                                       # ⫕
        XmlHtmlEntityBuild1('subsup', 10963),                                                       # ⫓
        XmlHtmlEntityBuild1('succ', 8827),                                                          # ≻
        XmlHtmlEntityBuild1('succapprox', 10936),                                                   # ⪸
        XmlHtmlEntityBuild1('succcurlyeq', 8829),                                                   # ≽
        XmlHtmlEntityBuild1('Succeeds', 8827),                                                      # ≻
        XmlHtmlEntityBuild1('SucceedsEqual', 10928),                                                # ⪰
        XmlHtmlEntityBuild1('SucceedsSlantEqual', 8829),                                            # ≽
        XmlHtmlEntityBuild1('SucceedsTilde', 8831),                                                 # ≿
        XmlHtmlEntityBuild1('succeq', 10928),                                                       # ⪰
        XmlHtmlEntityBuild1('succnapprox', 10938),                                                  # ⪺
        XmlHtmlEntityBuild1('succneqq', 10934),                                                     # ⪶
        XmlHtmlEntityBuild1('succnsim', 8937),                                                      # ⋩
        XmlHtmlEntityBuild1('succsim', 8831),                                                       # ≿
        XmlHtmlEntityBuild1('SuchThat', 8715),                                                      # ∋
        XmlHtmlEntityBuild1('Sum', 8721),                                                           # ∑
        XmlHtmlEntityBuild1('sum', 8721),                                                           # ∑
        XmlHtmlEntityBuild1('sung', 9834),                                                          # ♪
        XmlHtmlEntityBuild1('Sup', 8913),                                                           # ⋑
        XmlHtmlEntityBuild1('sup', 8835),                                                           # ⊃
        XmlHtmlEntityBuild1('supdot', 10942),                                                       # ⪾
        XmlHtmlEntityBuild1('supdsub', 10968),                                                      # ⫘
        XmlHtmlEntityBuild1('supE', 10950),                                                         # ⫆
        XmlHtmlEntityBuild1('supe', 8839),                                                          # ⊇
        XmlHtmlEntityBuild1('supedot', 10948),                                                      # ⫄
        XmlHtmlEntityBuild1('Superset', 8835),                                                      # ⊃
        XmlHtmlEntityBuild1('SupersetEqual', 8839),                                                 # ⊇
        XmlHtmlEntityBuild1('suphsol', 10185),                                                      # ⟉
        XmlHtmlEntityBuild1('suphsub', 10967),                                                      # ⫗
        XmlHtmlEntityBuild1('suplarr', 10619),                                                      # ⥻
        XmlHtmlEntityBuild1('supmult', 10946),                                                      # ⫂
        XmlHtmlEntityBuild1('supnE', 10956),                                                        # ⫌
        XmlHtmlEntityBuild1('supne', 8843),                                                         # ⊋
        XmlHtmlEntityBuild1('supplus', 10944),                                                      # ⫀
        XmlHtmlEntityBuild1('Supset', 8913),                                                        # ⋑
        XmlHtmlEntityBuild1('supset', 8835),                                                        # ⊃
        XmlHtmlEntityBuild1('supseteq', 8839),                                                      # ⊇
        XmlHtmlEntityBuild1('supseteqq', 10950),                                                    # ⫆
        XmlHtmlEntityBuild1('supsetneq', 8843),                                                     # ⊋
        XmlHtmlEntityBuild1('supsetneqq', 10956),                                                   # ⫌
        XmlHtmlEntityBuild1('supsim', 10952),                                                       # ⫈
        XmlHtmlEntityBuild1('supsub', 10964),                                                       # ⫔
        XmlHtmlEntityBuild1('supsup', 10966),                                                       # ⫖
        XmlHtmlEntityBuild1('swarhk', 10534),                                                       # ⤦
        XmlHtmlEntityBuild1('swArr', 8665),                                                         # ⇙
        XmlHtmlEntityBuild1('swarr', 8601),                                                         # ↙
        XmlHtmlEntityBuild1('swarrow', 8601),                                                       # ↙
        XmlHtmlEntityBuild1('swnwar', 10538),                                                       # ⤪
        XmlHtmlEntityBuild1('Tab', 9),                                                              # 	
        XmlHtmlEntityBuild1('target', 8982),                                                        # ⌖
        XmlHtmlEntityBuild1('tbrk', 9140),                                                          # ⎴
        XmlHtmlEntityBuild1('Tcaron', 356),                                                         # Ť
        XmlHtmlEntityBuild1('tcaron', 357),                                                         # ť
        XmlHtmlEntityBuild1('Tcedil', 354),                                                         # Ţ
        XmlHtmlEntityBuild1('tcedil', 355),                                                         # ţ
        XmlHtmlEntityBuild1('Tcy', 1058),                                                           # Т
        XmlHtmlEntityBuild1('tcy', 1090),                                                           # т
        XmlHtmlEntityBuild1('tdot', 8411),                                                          #⃛ 
        XmlHtmlEntityBuild1('telrec', 8981),                                                        # ⌕
        XmlHtmlEntityBuild1('Tfr', 120087),                                                         # 𝔗
        XmlHtmlEntityBuild1('tfr', 120113),                                                         # 𝔱
        XmlHtmlEntityBuild1('there4', 8756),                                                        # ∴
        XmlHtmlEntityBuild1('Therefore', 8756),                                                     # ∴
        XmlHtmlEntityBuild1('therefore', 8756),                                                     # ∴
        XmlHtmlEntityBuild1('thetasym', 977),                                                       # ϑ
        XmlHtmlEntityBuild1('thickapprox', 8776),                                                   # ≈
        XmlHtmlEntityBuild1('thicksim', 8764),                                                      # ∼
        XmlHtmlEntityBuild2('ThickSpace', '  '),                                                    #   
        XmlHtmlEntityBuild1('ThinSpace', 8201),                                                     #  
        XmlHtmlEntityBuild1('thkap', 8776),                                                         # ≈
        XmlHtmlEntityBuild1('thksim', 8764),                                                        # ∼
        XmlHtmlEntityBuild1('Tilde', 8764),                                                         # ∼
        XmlHtmlEntityBuild1('TildeEqual', 8771),                                                    # ≃
        XmlHtmlEntityBuild1('TildeFullEqual', 8773),                                                # ≅
        XmlHtmlEntityBuild1('TildeTilde', 8776),                                                    # ≈
        XmlHtmlEntityBuild1('timesb', 8864),                                                        # ⊠
        XmlHtmlEntityBuild1('timesbar', 10801),                                                     # ⨱
        XmlHtmlEntityBuild1('timesd', 10800),                                                       # ⨰
        XmlHtmlEntityBuild1('tint', 8749),                                                          # ∭
        XmlHtmlEntityBuild1('toea', 10536),                                                         # ⤨
        XmlHtmlEntityBuild1('top', 8868),                                                           # ⊤
        XmlHtmlEntityBuild1('topbot', 9014),                                                        # ⌶
        XmlHtmlEntityBuild1('topcir', 10993),                                                       # ⫱
        XmlHtmlEntityBuild1('Topf', 120139),                                                        # 𝕋
        XmlHtmlEntityBuild1('topf', 120165),                                                        # 𝕥
        XmlHtmlEntityBuild1('topfork', 10970),                                                      # ⫚
        XmlHtmlEntityBuild1('tosa', 10537),                                                         # ⤩
        XmlHtmlEntityBuild1('tprime', 8244),                                                        # ‴
        XmlHtmlEntityBuild1('TRADE', 8482),                                                         # ™
        XmlHtmlEntityBuild1('triangle', 9653),                                                      # ▵
        XmlHtmlEntityBuild1('triangledown', 9663),                                                  # ▿
        XmlHtmlEntityBuild1('triangleleft', 9667),                                                  # ◃
        XmlHtmlEntityBuild1('trianglelefteq', 8884),                                                # ⊴
        XmlHtmlEntityBuild1('triangleq', 8796),                                                     # ≜
        XmlHtmlEntityBuild1('triangleright', 9657),                                                 # ▹
        XmlHtmlEntityBuild1('trianglerighteq', 8885),                                               # ⊵
        XmlHtmlEntityBuild1('tridot', 9708),                                                        # ◬
        XmlHtmlEntityBuild1('trie', 8796),                                                          # ≜
        XmlHtmlEntityBuild1('triminus', 10810),                                                     # ⨺
        XmlHtmlEntityBuild1('TripleDot', 8411),                                                     #⃛ 
        XmlHtmlEntityBuild1('triplus', 10809),                                                      # ⨹
        XmlHtmlEntityBuild1('trisb', 10701),                                                        # ⧍
        XmlHtmlEntityBuild1('tritime', 10811),                                                      # ⨻
        XmlHtmlEntityBuild1('trpezium', 9186),                                                      # ⏢
        XmlHtmlEntityBuild1('Tscr', 119983),                                                        # 𝒯
        XmlHtmlEntityBuild1('tscr', 120009),                                                        # 𝓉
        XmlHtmlEntityBuild1('TScy', 1062),                                                          # Ц
        XmlHtmlEntityBuild1('tscy', 1094),                                                          # ц
        XmlHtmlEntityBuild1('TSHcy', 1035),                                                         # Ћ
        XmlHtmlEntityBuild1('tshcy', 1115),                                                         # ћ
        XmlHtmlEntityBuild1('Tstrok', 358),                                                         # Ŧ
        XmlHtmlEntityBuild1('tstrok', 359),                                                         # ŧ
        XmlHtmlEntityBuild1('twixt', 8812),                                                         # ≬
        XmlHtmlEntityBuild1('twoheadleftarrow', 8606),                                              # ↞
        XmlHtmlEntityBuild1('twoheadrightarrow', 8608),                                             # ↠
        XmlHtmlEntityBuild1('Uarr', 8607),                                                          # ↟
        XmlHtmlEntityBuild1('uArr', 8657),                                                          # ⇑
        XmlHtmlEntityBuild1('uarr', 8593),                                                          # ↑
        XmlHtmlEntityBuild1('Uarrocir', 10569),                                                     # ⥉
        XmlHtmlEntityBuild1('Ubrcy', 1038),                                                         # Ў
        XmlHtmlEntityBuild1('ubrcy', 1118),                                                         # ў
        XmlHtmlEntityBuild1('Ubreve', 364),                                                         # Ŭ
        XmlHtmlEntityBuild1('ubreve', 365),                                                         # ŭ
        XmlHtmlEntityBuild1('Ucy', 1059),                                                           # У
        XmlHtmlEntityBuild1('ucy', 1091),                                                           # у
        XmlHtmlEntityBuild1('udarr', 8645),                                                         # ⇅
        XmlHtmlEntityBuild1('Udblac', 368),                                                         # Ű
        XmlHtmlEntityBuild1('udblac', 369),                                                         # ű
        XmlHtmlEntityBuild1('udhar', 10606),                                                        # ⥮
        XmlHtmlEntityBuild1('ufisht', 10622),                                                       # ⥾
        XmlHtmlEntityBuild1('Ufr', 120088),                                                         # 𝔘
        XmlHtmlEntityBuild1('ufr', 120114),                                                         # 𝔲
        XmlHtmlEntityBuild1('uHar', 10595),                                                         # ⥣
        XmlHtmlEntityBuild1('uharl', 8639),                                                         # ↿
        XmlHtmlEntityBuild1('uharr', 8638),                                                         # ↾
        XmlHtmlEntityBuild1('uhblk', 9600),                                                         # ▀
        XmlHtmlEntityBuild1('ulcorn', 8988),                                                        # ⌜
        XmlHtmlEntityBuild1('ulcorner', 8988),                                                      # ⌜
        XmlHtmlEntityBuild1('ulcrop', 8975),                                                        # ⌏
        XmlHtmlEntityBuild1('ultri', 9720),                                                         # ◸
        XmlHtmlEntityBuild1('Umacr', 362),                                                          # Ū
        XmlHtmlEntityBuild1('umacr', 363),                                                          # ū
        XmlHtmlEntityBuild1('UnderBar', 95),                                                        # _
        XmlHtmlEntityBuild1('UnderBrace', 9183),                                                    # ⏟
        XmlHtmlEntityBuild1('UnderBracket', 9141),                                                  # ⎵
        XmlHtmlEntityBuild1('UnderParenthesis', 9181),                                              # ⏝
        XmlHtmlEntityBuild1('Union', 8899),                                                         # ⋃
        XmlHtmlEntityBuild1('UnionPlus', 8846),                                                     # ⊎
        XmlHtmlEntityBuild1('Uogon', 370),                                                          # Ų
        XmlHtmlEntityBuild1('uogon', 371),                                                          # ų
        XmlHtmlEntityBuild1('Uopf', 120140),                                                        # 𝕌
        XmlHtmlEntityBuild1('uopf', 120166),                                                        # 𝕦
        XmlHtmlEntityBuild1('UpArrow', 8593),                                                       # ↑
        XmlHtmlEntityBuild1('Uparrow', 8657),                                                       # ⇑
        XmlHtmlEntityBuild1('uparrow', 8593),                                                       # ↑
        XmlHtmlEntityBuild1('UpArrowBar', 10514),                                                   # ⤒
        XmlHtmlEntityBuild1('UpArrowDownArrow', 8645),                                              # ⇅
        XmlHtmlEntityBuild1('UpDownArrow', 8597),                                                   # ↕
        XmlHtmlEntityBuild1('Updownarrow', 8661),                                                   # ⇕
        XmlHtmlEntityBuild1('updownarrow', 8597),                                                   # ↕
        XmlHtmlEntityBuild1('UpEquilibrium', 10606),                                                # ⥮
        XmlHtmlEntityBuild1('upharpoonleft', 8639),                                                 # ↿
        XmlHtmlEntityBuild1('upharpoonright', 8638),                                                # ↾
        XmlHtmlEntityBuild1('uplus', 8846),                                                         # ⊎
        XmlHtmlEntityBuild1('UpperLeftArrow', 8598),                                                # ↖
        XmlHtmlEntityBuild1('UpperRightArrow', 8599),                                               # ↗
        XmlHtmlEntityBuild1('Upsi', 978),                                                           # ϒ
        XmlHtmlEntityBuild1('upsilon', 965),                                                        # υ
        XmlHtmlEntityBuild1('UpTee', 8869),                                                         # ⊥
        XmlHtmlEntityBuild1('UpTeeArrow', 8613),                                                    # ↥
        XmlHtmlEntityBuild1('upuparrows', 8648),                                                    # ⇈
        XmlHtmlEntityBuild1('urcorn', 8989),                                                        # ⌝
        XmlHtmlEntityBuild1('urcorner', 8989),                                                      # ⌝
        XmlHtmlEntityBuild1('urcrop', 8974),                                                        # ⌎
        XmlHtmlEntityBuild1('Uring', 366),                                                          # Ů
        XmlHtmlEntityBuild1('uring', 367),                                                          # ů
        XmlHtmlEntityBuild1('urtri', 9721),                                                         # ◹
        XmlHtmlEntityBuild1('Uscr', 119984),                                                        # 𝒰
        XmlHtmlEntityBuild1('uscr', 120010),                                                        # 𝓊
        XmlHtmlEntityBuild1('utdot', 8944),                                                         # ⋰
        XmlHtmlEntityBuild1('Utilde', 360),                                                         # Ũ
        XmlHtmlEntityBuild1('utilde', 361),                                                         # ũ
        XmlHtmlEntityBuild1('utri', 9653),                                                          # ▵
        XmlHtmlEntityBuild1('utrif', 9652),                                                         # ▴
        XmlHtmlEntityBuild1('uuarr', 8648),                                                         # ⇈
        XmlHtmlEntityBuild1('uwangle', 10663),                                                      # ⦧
        XmlHtmlEntityBuild1('vangrt', 10652),                                                       # ⦜
        XmlHtmlEntityBuild1('varepsilon', 1013),                                                    # ϵ
        XmlHtmlEntityBuild1('varkappa', 1008),                                                      # ϰ
        XmlHtmlEntityBuild1('varnothing', 8709),                                                    # ∅
        XmlHtmlEntityBuild1('varphi', 981),                                                         # ϕ
        XmlHtmlEntityBuild1('varpi', 982),                                                          # ϖ
        XmlHtmlEntityBuild1('varpropto', 8733),                                                     # ∝
        XmlHtmlEntityBuild1('vArr', 8661),                                                          # ⇕
        XmlHtmlEntityBuild1('varr', 8597),                                                          # ↕
        XmlHtmlEntityBuild1('varrho', 1009),                                                        # ϱ
        XmlHtmlEntityBuild1('varsigma', 962),                                                       # ς
        XmlHtmlEntityBuild2('varsubsetneq', '⊊︀'),                                                   # ⊊︀
        XmlHtmlEntityBuild2('varsubsetneqq', '⫋︀'),                                                  # ⫋︀
        XmlHtmlEntityBuild2('varsupsetneq', '⊋︀'),                                                   # ⊋︀
        XmlHtmlEntityBuild2('varsupsetneqq', '⫌︀'),                                                  # ⫌︀
        XmlHtmlEntityBuild1('vartheta', 977),                                                       # ϑ
        XmlHtmlEntityBuild1('vartriangleleft', 8882),                                               # ⊲
        XmlHtmlEntityBuild1('vartriangleright', 8883),                                              # ⊳
        XmlHtmlEntityBuild1('Vbar', 10987),                                                         # ⫫
        XmlHtmlEntityBuild1('vBar', 10984),                                                         # ⫨
        XmlHtmlEntityBuild1('vBarv', 10985),                                                        # ⫩
        XmlHtmlEntityBuild1('Vcy', 1042),                                                           # В
        XmlHtmlEntityBuild1('vcy', 1074),                                                           # в
        XmlHtmlEntityBuild1('VDash', 8875),                                                         # ⊫
        XmlHtmlEntityBuild1('Vdash', 8873),                                                         # ⊩
        XmlHtmlEntityBuild1('vDash', 8872),                                                         # ⊨
        XmlHtmlEntityBuild1('vdash', 8866),                                                         # ⊢
        XmlHtmlEntityBuild1('Vdashl', 10982),                                                       # ⫦
        XmlHtmlEntityBuild1('Vee', 8897),                                                           # ⋁
        XmlHtmlEntityBuild1('vee', 8744),                                                           # ∨
        XmlHtmlEntityBuild1('veebar', 8891),                                                        # ⊻
        XmlHtmlEntityBuild1('veeeq', 8794),                                                         # ≚
        XmlHtmlEntityBuild1('vellip', 8942),                                                        # ⋮
        XmlHtmlEntityBuild1('Verbar', 8214),                                                        # ‖
        XmlHtmlEntityBuild1('verbar', 124),                                                         # |
        XmlHtmlEntityBuild1('Vert', 8214),                                                          # ‖
        XmlHtmlEntityBuild1('vert', 124),                                                           # |
        XmlHtmlEntityBuild1('VerticalBar', 8739),                                                   # ∣
        XmlHtmlEntityBuild1('VerticalLine', 124),                                                   # |
        XmlHtmlEntityBuild1('VerticalSeparator', 10072),                                            # ❘
        XmlHtmlEntityBuild1('VerticalTilde', 8768),                                                 # ≀
        XmlHtmlEntityBuild1('VeryThinSpace', 8202),                                                 #  
        XmlHtmlEntityBuild1('Vfr', 120089),                                                         # 𝔙
        XmlHtmlEntityBuild1('vfr', 120115),                                                         # 𝔳
        XmlHtmlEntityBuild1('vltri', 8882),                                                         # ⊲
        XmlHtmlEntityBuild2('vnsub', '⊂⃒'),                                                          # ⊂⃒
        XmlHtmlEntityBuild2('vnsup', '⊃⃒'),                                                          # ⊃⃒
        XmlHtmlEntityBuild1('Vopf', 120141),                                                        # 𝕍
        XmlHtmlEntityBuild1('vopf', 120167),                                                        # 𝕧
        XmlHtmlEntityBuild1('vprop', 8733),                                                         # ∝
        XmlHtmlEntityBuild1('vrtri', 8883),                                                         # ⊳
        XmlHtmlEntityBuild1('Vscr', 119985),                                                        # 𝒱
        XmlHtmlEntityBuild1('vscr', 120011),                                                        # 𝓋
        XmlHtmlEntityBuild2('vsubnE', '⫋︀'),                                                         # ⫋︀
        XmlHtmlEntityBuild2('vsubne', '⊊︀'),                                                         # ⊊︀
        XmlHtmlEntityBuild2('vsupnE', '⫌︀'),                                                         # ⫌︀
        XmlHtmlEntityBuild2('vsupne', '⊋︀'),                                                         # ⊋︀
        XmlHtmlEntityBuild1('Vvdash', 8874),                                                        # ⊪
        XmlHtmlEntityBuild1('vzigzag', 10650),                                                      # ⦚
        XmlHtmlEntityBuild1('Wcirc', 372),                                                          # Ŵ
        XmlHtmlEntityBuild1('wcirc', 373),                                                          # ŵ
        XmlHtmlEntityBuild1('wedbar', 10847),                                                       # ⩟
        XmlHtmlEntityBuild1('Wedge', 8896),                                                         # ⋀
        XmlHtmlEntityBuild1('wedge', 8743),                                                         # ∧
        XmlHtmlEntityBuild1('wedgeq', 8793),                                                        # ≙
        XmlHtmlEntityBuild1('Wfr', 120090),                                                         # 𝔚
        XmlHtmlEntityBuild1('wfr', 120116),                                                         # 𝔴
        XmlHtmlEntityBuild1('Wopf', 120142),                                                        # 𝕎
        XmlHtmlEntityBuild1('wopf', 120168),                                                        # 𝕨
        XmlHtmlEntityBuild1('wp', 8472),                                                            # ℘
        XmlHtmlEntityBuild1('wr', 8768),                                                            # ≀
        XmlHtmlEntityBuild1('wreath', 8768),                                                        # ≀
        XmlHtmlEntityBuild1('Wscr', 119986),                                                        # 𝒲
        XmlHtmlEntityBuild1('wscr', 120012),                                                        # 𝓌
        XmlHtmlEntityBuild1('xcap', 8898),                                                          # ⋂
        XmlHtmlEntityBuild1('xcirc', 9711),                                                         # ◯
        XmlHtmlEntityBuild1('xcup', 8899),                                                          # ⋃
        XmlHtmlEntityBuild1('xdtri', 9661),                                                         # ▽
        XmlHtmlEntityBuild1('Xfr', 120091),                                                         # 𝔛
        XmlHtmlEntityBuild1('xfr', 120117),                                                         # 𝔵
        XmlHtmlEntityBuild1('xhArr', 10234),                                                        # ⟺
        XmlHtmlEntityBuild1('xharr', 10231),                                                        # ⟷
        XmlHtmlEntityBuild1('xlArr', 10232),                                                        # ⟸
        XmlHtmlEntityBuild1('xlarr', 10229),                                                        # ⟵
        XmlHtmlEntityBuild1('xmap', 10236),                                                         # ⟼
        XmlHtmlEntityBuild1('xnis', 8955),                                                          # ⋻
        XmlHtmlEntityBuild1('xodot', 10752),                                                        # ⨀
        XmlHtmlEntityBuild1('Xopf', 120143),                                                        # 𝕏
        XmlHtmlEntityBuild1('xopf', 120169),                                                        # 𝕩
        XmlHtmlEntityBuild1('xoplus', 10753),                                                       # ⨁
        XmlHtmlEntityBuild1('xotime', 10754),                                                       # ⨂
        XmlHtmlEntityBuild1('xrArr', 10233),                                                        # ⟹
        XmlHtmlEntityBuild1('xrarr', 10230),                                                        # ⟶
        XmlHtmlEntityBuild1('Xscr', 119987),                                                        # 𝒳
        XmlHtmlEntityBuild1('xscr', 120013),                                                        # 𝓍
        XmlHtmlEntityBuild1('xsqcup', 10758),                                                       # ⨆
        XmlHtmlEntityBuild1('xuplus', 10756),                                                       # ⨄
        XmlHtmlEntityBuild1('xutri', 9651),                                                         # △
        XmlHtmlEntityBuild1('xvee', 8897),                                                          # ⋁
        XmlHtmlEntityBuild1('xwedge', 8896),                                                        # ⋀
        XmlHtmlEntityBuild1('YAcy', 1071),                                                          # Я
        XmlHtmlEntityBuild1('yacy', 1103),                                                          # я
        XmlHtmlEntityBuild1('Ycirc', 374),                                                          # Ŷ
        XmlHtmlEntityBuild1('ycirc', 375),                                                          # ŷ
        XmlHtmlEntityBuild1('Ycy', 1067),                                                           # Ы
        XmlHtmlEntityBuild1('ycy', 1099),                                                           # ы
        XmlHtmlEntityBuild1('Yfr', 120092),                                                         # 𝔜
        XmlHtmlEntityBuild1('yfr', 120118),                                                         # 𝔶
        XmlHtmlEntityBuild1('YIcy', 1031),                                                          # Ї
        XmlHtmlEntityBuild1('yicy', 1111),                                                          # ї
        XmlHtmlEntityBuild1('Yopf', 120144),                                                        # 𝕐
        XmlHtmlEntityBuild1('yopf', 120170),                                                        # 𝕪
        XmlHtmlEntityBuild1('Yscr', 119988),                                                        # 𝒴
        XmlHtmlEntityBuild1('yscr', 120014),                                                        # 𝓎
        XmlHtmlEntityBuild1('YUcy', 1070),                                                          # Ю
        XmlHtmlEntityBuild1('yucy', 1102),                                                          # ю
        XmlHtmlEntityBuild1('Zacute', 377),                                                         # Ź
        XmlHtmlEntityBuild1('zacute', 378),                                                         # ź
        XmlHtmlEntityBuild1('Zcaron', 381),                                                         # Ž
        XmlHtmlEntityBuild1('zcaron', 382),                                                         # ž
        XmlHtmlEntityBuild1('Zcy', 1047),                                                           # З
        XmlHtmlEntityBuild1('zcy', 1079),                                                           # з
        XmlHtmlEntityBuild1('Zdot', 379),                                                           # Ż
        XmlHtmlEntityBuild1('zdot', 380),                                                           # ż
        XmlHtmlEntityBuild1('zeetrf', 8488),                                                        # ℨ
        XmlHtmlEntityBuild1('ZeroWidthSpace', 8203),                                                # ​
        XmlHtmlEntityBuild1('Zfr', 8488),                                                           # ℨ
        XmlHtmlEntityBuild1('zfr', 120119),                                                         # 𝔷
        XmlHtmlEntityBuild1('ZHcy', 1046),                                                          # Ж
        XmlHtmlEntityBuild1('zhcy', 1078),                                                          # ж
        XmlHtmlEntityBuild1('zigrarr', 8669),                                                       # ⇝
        XmlHtmlEntityBuild1('Zopf', 8484),                                                          # ℤ
        XmlHtmlEntityBuild1('zopf', 120171),                                                        # 𝕫
        XmlHtmlEntityBuild1('Zscr', 119989),                                                        # 𝒵
        XmlHtmlEntityBuild1('zscr', 120015),                                                        # 𝓏
    ]
    
    Html = Html2 + Html3 + Html4 + Html5

for e in Entitys.HtmlQuot + Entitys.HtmlApos + Entitys.HtmlBase + Entitys.Html:
    setattr(Entitys, e.name, e)


import html
lst = [n.name for n in Entitys.Html + Entitys.HtmlBase + Entitys.HtmlQuot + Entitys.HtmlApos ]
for k,v in html.entities.html5.items():
    k = k.replace(';', '')
    if k not in lst:
        if len(v) == 1:
            c = ord(v)
            print(f"XmlHtmlEntityBuild1('{k}', {c}),             # {v}")
        else:
            print(f"XmlHtmlEntity('{v}', '{k}', '&{k};', None, None),    # {v}")
