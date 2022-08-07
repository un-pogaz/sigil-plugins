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
    
    def build1(name, codepoint):
        return XmlHtmlEntity(chr(codepoint), name, '&'+name+';', '&#'+str(codepoint)+';', codepoint)
    
    def build2(name, char):
        return XmlHtmlEntity(char, name, '&'+name+';', None, None)
    
    HtmlQuot = [ build1('quot', 34), build1('QUOT', 34) ]
    HtmlApos = [ build1('apos', 39), build1('APOS', 39) ]
    HtmlBase = [
        build1('amp', 38),  # &
        build1('AMP', 38),  # &
        build1('lt', 60),   # <
        build1('LT', 60),   # <
        build1('gt', 62),   # >
        build1('GT', 62),   # >
    ]
    
    Html2 = [
        build1('Agrave', 192),  # À
        build1('Aacute', 193),  # Á
        build1('Acirc', 194),   # Â
        build1('Atilde', 195),  # Ã
        build1('Auml', 196),    # Ä
        build1('Aring', 197),   # Å
        build1('AElig', 198),   # Æ
        build1('Ccedil', 199),  # Ç
        build1('Egrave', 200),  # È
        build1('Eacute', 201),  # É
        build1('Ecirc', 202),   # Ê
        build1('Euml', 203),    # Ë
        build1('Igrave', 204),  # Ì
        build1('Iacute', 205),  # Í
        build1('Icirc', 206),   # Î
        build1('Iuml', 207),    # Ï
        build1('ETH', 208),     # Ð
        build1('Ntilde', 209),  # Ñ
        build1('Ograve', 210),  # Ò
        build1('Oacute', 211),  # Ó
        build1('Ocirc', 212),   # Ô
        build1('Otilde', 213),  # Õ
        build1('Ouml', 214),    # Ö
        build1('Oslash', 216),  # Ø
        build1('Ugrave', 217),  # Ù
        build1('Uacute', 218),  # Ú
        build1('Ucirc', 219),   # Û
        build1('Uuml', 220),    # Ü
        build1('Yacute', 221),  # Ý
        
        build1('THORN', 222),   # Þ
        build1('szlig', 223),   # ß
        
        build1('agrave', 224),  # à
        build1('aacute', 225),  # á
        build1('acirc', 226),   # â
        build1('atilde', 227),  # ã
        build1('auml', 228),    # ä
        build1('aring', 229),   # å
        build1('aelig', 230),   # æ
        build1('ccedil', 231),  # ç
        build1('egrave', 232),  # è
        build1('eacute', 233),  # é
        build1('ecirc', 234),   # ê
        build1('euml', 235),    # ë
        build1('igrave', 236),  # ì
        build1('iacute', 237),  # í
        build1('icirc', 238),   # î
        build1('iuml', 239),    # ï
        build1('eth', 240),     # ð
        build1('ntilde', 241),  # ñ
        build1('ograve', 242),  # ò
        build1('oacute', 243),  # ó
        build1('ocirc', 244),   # ô
        build1('otilde', 245),  # õ
        build1('ouml', 246),    # ö
        build1('oslash', 248),  # ø
        build1('ugrave', 249),  # ù
        build1('uacute', 250),  # ú
        build1('ucirc', 251),   # û
        build1('uuml', 252),    # ü
        build1('yacute', 253),  # ý
        
        build1('thorn', 254),   # þ
        build1('yuml', 255),    # ÿ
    ]
    
    Html3 = [
        build1('nbsp', 160),    #  
        build1('iexcl', 161),   # ¡
        build1('cent', 162),    # ¢
        build1('pound', 163),   # £
        build1('curren', 164),  # ¤
        build1('yen', 165),     # ¥
        build1('brvbar', 166),  # ¦
        build1('sect', 167),    # §
        build1('uml', 168),     # ¨
        build1('copy', 169),    # ©
        build1('ordf', 170),    # ª
        build1('laquo', 171),   # «
        build1('not', 172),     # ¬
        build1('shy', 173),     # ­
        build1('reg', 174),     # ®
        build1('macr', 175),    # ¯
        build1('deg', 176),     # °
        build1('plusmn', 177),   # ±
        build1('sup2', 178),    # ²
        build1('sup3', 179),    # ³
        build1('acute', 180),   # ´
        build1('micro', 181),   # µ
        build1('para', 182),    # ¶
        build1('middot', 183),   # ·
        build1('cedil', 184),   # ¸
        build1('sup1', 185),    # ¹
        build1('ordm', 186),    # º
        build1('raquo', 187),   # »
        build1('frac14', 188),  # ¼
        build1('frac12', 189),  # ½
        build1('frac34', 190),  # ¾
        build1('iquest', 191),  # ¿
        
        build1('times', 215),   # ×
        
        build1('divide', 247),  # ÷
    ]
    
    Html4 = [
        build1('OElig', 338),       # Œ
        build1('oelig', 339),       # œ
        
        build1('Scaron', 352),      # Š
        build1('scaron', 353),      # š
        
        build1('Yuml', 376),        # Ÿ
        
        build1('fnof', 402),        # ƒ
        
        build1('circ', 710),        # ˆ
        
        build1('tilde', 732),       # ˜
        
        build1('Alpha', 913 ),      # Α
        build1('Beta', 914 ),       # Β
        build1('Gamma', 915 ),      # Γ
        build1('Delta', 916 ),      # Δ
        build1('Epsilon', 917 ),    # Ε
        build1('Zeta', 918 ),       # Ζ
        build1('Eta', 919 ),        # Η
        build1('Theta', 920 ),      # Θ
        build1('Iota', 921 ),       # Ι
        build1('Kappa', 922 ),      # Κ
        build1('Lambda', 923 ),     # Λ
        build1('Mu', 924 ),         # Μ
        build1('Nu', 925 ),         # Ν
        build1('Xi', 926 ),         # Ξ
        build1('Omicron', 927 ),    # Ο
        build1('Pi', 928 ),         # Π
        build1('Rho', 929 ),        # Ρ
        
        build1('Sigma', 931 ),      # Σ
        build1('Tau', 932 ),        # Τ
        build1('Upsilon', 933 ),    # Υ
        build1('Phi', 934 ),        # Φ
        build1('Chi', 935 ),        # Χ
        build1('Psi', 936 ),        # Ψ
        build1('Omega', 937 ),      # Ω
        build1('ohm', 937 ),        # Ω
        
        build1('alpha', 945 ),      # α
        build1('beta', 946 ),       # β
        build1('gamma', 947 ),      # γ
        build1('delta', 948 ),      # δ
        build1('epsi', 949 ),       # ε
        build1('epsilon', 949 ),    # ε
        build1('zeta', 950 ),       # ζ
        build1('eta', 951 ),        # η
        build1('theta', 952 ),      # θ
        build1('iota', 953 ),       # ι
        build1('kappa', 954 ),      # κ
        build1('lambda', 955 ),     # λ
        build1('mu', 956 ),         # μ
        build1('nu', 957 ),         # ν
        build1('xi', 958 ),         # ξ
        build1('omicron', 959 ),    # ο
        build1('pi', 960 ),         # π
        build1('rho', 961 ),        # ρ
        build1('sigmav', 962 ),     # ς
        build1('sigmaf', 962 ),     # ς
        build1('sigma', 963 ),      # σ
        build1('tau', 964 ),        # τ
        build1('upsi', 965 ),       # υ
        build1('phi', 966 ),        # φ
        build1('chi', 967 ),        # χ
        build1('psi', 968 ),        # ψ
        build1('omega', 969 ),      # ω
        
        build1('thetav', 977 ),     # ϑ
        build1('upsih', 978 ),      # ϒ
        
        build1('phiv', 981 ),       # ϕ
        
        build1('ensp', 8194),       #  
        build1('emsp', 8195),       #  
        
        build1('thinsp', 8201),     #  
        
        build1('zwnj', 8204),       # ‌
        build1('zwj', 8205),        # ‍
        build1('lrm', 8206),        # ‎
        build1('rlm', 8207),        # ‏
        
        build1('ndash', 8211),      # –
        build1('mdash', 8212),      # —
        
        build1('lsquo', 8216),      # ‘
        build1('rsquo', 8217),      # ’
        build1('rsquor', 8217),     # ’
        build1('sbquo', 8218),      # ‚
        build1('ldquo', 8220),      # “
        build1('rdquo', 8221 ),     # ”
        build1('bdquo', 8222),      # „
        
        build1('dagger', 8224),     # †
        build1('ddagger', 8225),    # ‡
        build1('bull', 8226),       # •
        
        build1('hellip', 8230),     # …
        
        build1('permil', 8240),     # ‰
        
        build1('prime', 8242),      # ′
        build1('Prime', 8243),      # ″
        
        build1('lsaquo', 8249),     # ‹
        build1('rsaquo', 8250),     # ›
        
        build1('oline', 8254),      # ‾
        
        build1('euro', 8364),       # €
        
        build1('image', 8465),      # ℑ
        
        build1('weierp', 8472),     # ℘
        
        build1('real', 8476),       # ℜ
        
        build1('trade', 8482),      # ™
        
        build1('alefsym', 8501),    # ℵ
        
        build1('rang', 10217),      # ⟩
        build1('loz', 9674),        # ◊
        build1('spades', 9824),     # ♠
        build1('clubs', 9827),      # ♣
        build1('hearts', 9829),     # ♥
        build1('diams', 9830),      # ♦
        build1('lang', 10216),      # ⟨
        build1('rang', 10217),      # ⟩
    ]
    
    Html5 = [
        build1('Abreve', 258),                          # Ă
        build1('abreve', 259),                          # ă
        build1('ac', 8766),                             # ∾
        build1('acd', 8767),                            # ∿
        build2('acE', '∾̳'),                             # ∾̳
        build1('Acy', 1040),                            # А
        build1('acy', 1072),                            # а
        build1('af', 8289),                             # ⁡
        build1('Afr', 120068),                          # 𝔄
        build1('afr', 120094),                          # 𝔞
        build1('aleph', 8501),                          # ℵ
        build1('Amacr', 256),                           # Ā
        build1('amacr', 257),                           # ā
        build1('amalg', 10815),                         # ⨿
        build1('And', 10835),                           # ⩓
        build1('and', 8743),                            # ∧
        build1('andand', 10837),                        # ⩕
        build1('andd', 10844),                          # ⩜
        build1('andslope', 10840),                      # ⩘
        build1('andv', 10842),                          # ⩚
        build1('ang', 8736),                            # ∠
        build1('ange', 10660),                          # ⦤
        build1('angle', 8736),                          # ∠
        build1('angmsd', 8737),                         # ∡
        build1('angmsdaa', 10664),                      # ⦨
        build1('angmsdab', 10665),                      # ⦩
        build1('angmsdac', 10666),                      # ⦪
        build1('angmsdad', 10667),                      # ⦫
        build1('angmsdae', 10668),                      # ⦬
        build1('angmsdaf', 10669),                      # ⦭
        build1('angmsdag', 10670),                      # ⦮
        build1('angmsdah', 10671),                      # ⦯
        build1('angrt', 8735),                          # ∟
        build1('angrtvb', 8894),                        # ⊾
        build1('angrtvbd', 10653),                      # ⦝
        build1('angsph', 8738),                         # ∢
        build1('angst', 197),                           # Å
        build1('angzarr', 9084),                        # ⍼
        build1('Aogon', 260),                           # Ą
        build1('aogon', 261),                           # ą
        build1('Aopf', 120120),                         # 𝔸
        build1('aopf', 120146),                         # 𝕒
        build1('ap', 8776),                             # ≈
        build1('apacir', 10863),                        # ⩯
        build1('apE', 10864),                           # ⩰
        build1('ape', 8778),                            # ≊
        build1('apid', 8779),                           # ≋
        build1('apos', 39),                             # '
        build1('ApplyFunction', 8289),                  # ⁡
        build1('approx', 8776),                         # ≈
        build1('approxeq', 8778),                       # ≊
        build1('Ascr', 119964),                         # 𝒜
        build1('ascr', 119990),                         # 𝒶
        build1('Assign', 8788),                         # ≔
        build1('ast', 42),                              # *
        build1('asymp', 8776),                          # ≈
        build1('asympeq', 8781),                        # ≍
        build1('awconint', 8755),                       # ∳
        build1('awint', 10769),                         # ⨑
        build1('backcong', 8780),                       # ≌
        build1('backepsilon', 1014),                    # ϶
        build1('backprime', 8245),                      # ‵
        build1('backsim', 8765),                        # ∽
        build1('backsimeq', 8909),                      # ⋍
        build1('Backslash', 8726),                      # ∖
        build1('Barv', 10983),                          # ⫧
        build1('barvee', 8893),                         # ⊽
        build1('Barwed', 8966),                         # ⌆
        build1('barwed', 8965),                         # ⌅
        build1('barwedge', 8965),                       # ⌅
        build1('bbrk', 9141),                           # ⎵
        build1('bbrktbrk', 9142),                       # ⎶
        build1('bcong', 8780),                          # ≌
        build1('Bcy', 1041),                            # Б
        build1('bcy', 1073),                            # б
        build1('becaus', 8757),                         # ∵
        build1('Because', 8757),                        # ∵
        build1('because', 8757),                        # ∵
        build1('bemptyv', 10672),                       # ⦰
        build1('bepsi', 1014),                          # ϶
        build1('bernou', 8492),                         # ℬ
        build1('Bernoullis', 8492),                     # ℬ
        build1('beth', 8502),                           # ℶ
        build1('between', 8812),                        # ≬
        build1('Bfr', 120069),                          # 𝔅
        build1('bfr', 120095),                          # 𝔟
        build1('bigcap', 8898),                         # ⋂
        build1('bigcirc', 9711),                        # ◯
        build1('bigcup', 8899),                         # ⋃
        build1('bigodot', 10752),                       # ⨀
        build1('bigoplus', 10753),                      # ⨁
        build1('bigotimes', 10754),                     # ⨂
        build1('bigsqcup', 10758),                      # ⨆
        build1('bigstar', 9733),                        # ★
        build1('bigtriangledown', 9661),                # ▽
        build1('bigtriangleup', 9651),                  # △
        build1('biguplus', 10756),                      # ⨄
        build1('bigvee', 8897),                         # ⋁
        build1('bigwedge', 8896),                       # ⋀
        build1('bkarow', 10509),                        # ⤍
        build1('blacklozenge', 10731),                  # ⧫
        build1('blacksquare', 9642),                    # ▪
        build1('blacktriangle', 9652),                  # ▴
        build1('blacktriangledown', 9662),              # ▾
        build1('blacktriangleleft', 9666),              # ◂
        build1('blacktriangleright', 9656),             # ▸
        build1('blank', 9251),                          # ␣
        build1('blk12', 9618),                          # ▒
        build1('blk14', 9617),                          # ░
        build1('blk34', 9619),                          # ▓
        build1('block', 9608),                          # █
        build2('bne', '=⃥'),                             # =⃥
        build2('bnequiv', '≡⃥'),                         # ≡⃥
        build1('bNot', 10989),                          # ⫭
        build1('bnot', 8976),                           # ⌐
        build1('Bopf', 120121),                         # 𝔹
        build1('bopf', 120147),                         # 𝕓
        build1('bot', 8869),                            # ⊥
        build1('bottom', 8869),                         # ⊥
        build1('bowtie', 8904),                         # ⋈
        build1('boxbox', 10697),                        # ⧉
        build1('boxDL', 9559),                          # ╗
        build1('boxDl', 9558),                          # ╖
        build1('boxdL', 9557),                          # ╕
        build1('boxdl', 9488),                          # ┐
        build1('boxDR', 9556),                          # ╔
        build1('boxDr', 9555),                          # ╓
        build1('boxdR', 9554),                          # ╒
        build1('boxdr', 9484),                          # ┌
        build1('boxH', 9552),                           # ═
        build1('boxh', 9472),                           # ─
        build1('boxHD', 9574),                          # ╦
        build1('boxHd', 9572),                          # ╤
        build1('boxhD', 9573),                          # ╥
        build1('boxhd', 9516),                          # ┬
        build1('boxHU', 9577),                          # ╩
        build1('boxHu', 9575),                          # ╧
        build1('boxhU', 9576),                          # ╨
        build1('boxhu', 9524),                          # ┴
        build1('boxminus', 8863),                       # ⊟
        build1('boxplus', 8862),                        # ⊞
        build1('boxtimes', 8864),                       # ⊠
        build1('boxUL', 9565),                          # ╝
        build1('boxUl', 9564),                          # ╜
        build1('boxuL', 9563),                          # ╛
        build1('boxul', 9496),                          # ┘
        build1('boxUR', 9562),                          # ╚
        build1('boxUr', 9561),                          # ╙
        build1('boxuR', 9560),                          # ╘
        build1('boxur', 9492),                          # └
        build1('boxV', 9553),                           # ║
        build1('boxv', 9474),                           # │
        build1('boxVH', 9580),                          # ╬
        build1('boxVh', 9579),                          # ╫
        build1('boxvH', 9578),                          # ╪
        build1('boxvh', 9532),                          # ┼
        build1('boxVL', 9571),                          # ╣
        build1('boxVl', 9570),                          # ╢
        build1('boxvL', 9569),                          # ╡
        build1('boxvl', 9508),                          # ┤
        build1('boxVR', 9568),                          # ╠
        build1('boxVr', 9567),                          # ╟
        build1('boxvR', 9566),                          # ╞
        build1('boxvr', 9500),                          # ├
        build1('bprime', 8245),                         # ‵
        build1('Breve', 728),                           # ˘
        build1('breve', 728),                           # ˘
        build1('Bscr', 8492),                           # ℬ
        build1('bscr', 119991),                         # 𝒷
        build1('bsemi', 8271),                          # ⁏
        build1('bsim', 8765),                           # ∽
        build1('bsime', 8909),                          # ⋍
        build1('bsol', 92),                             # \
        build1('bsolb', 10693),                         # ⧅
        build1('bsolhsub', 10184),                      # ⟈
        build1('bullet', 8226),                         # •
        build1('bump', 8782),                           # ≎
        build1('bumpE', 10926),                         # ⪮
        build1('bumpe', 8783),                          # ≏
        build1('Bumpeq', 8782),                         # ≎
        build1('bumpeq', 8783),                         # ≏
        build1('Cacute', 262),                          # Ć
        build1('cacute', 263),                          # ć
        build1('Cap', 8914),                            # ⋒
        build1('cap', 8745),                            # ∩
        build1('capand', 10820),                        # ⩄
        build1('capbrcup', 10825),                      # ⩉
        build1('capcap', 10827),                        # ⩋
        build1('capcup', 10823),                        # ⩇
        build1('capdot', 10816),                        # ⩀
        build1('CapitalDifferentialD', 8517),           # ⅅ
        build2('caps', '∩︀'),                            # ∩︀
        build1('caret', 8257),                          # ⁁
        build1('caron', 711),                           # ˇ
        build1('Cayleys', 8493),                        # ℭ
        build1('ccaps', 10829),                         # ⩍
        build1('Ccaron', 268),                          # Č
        build1('ccaron', 269),                          # č
        build1('Ccirc', 264),                           # Ĉ
        build1('ccirc', 265),                           # ĉ
        build1('Cconint', 8752),                        # ∰
        build1('ccups', 10828),                         # ⩌
        build1('ccupssm', 10832),                       # ⩐
        build1('Cdot', 266),                            # Ċ
        build1('cdot', 267),                            # ċ
        build1('Cedilla', 184),                         # ¸
        build1('cemptyv', 10674),                       # ⦲
        build1('CenterDot', 183),                       # ·
        build1('centerdot', 183),                       # ·
        build1('Cfr', 8493),                            # ℭ
        build1('cfr', 120096),                          # 𝔠
        build1('CHcy', 1063),                           # Ч
        build1('chcy', 1095),                           # ч
        build1('check', 10003),                         # ✓
        build1('checkmark', 10003),                     # ✓
        build1('cir', 9675),                            # ○
        build1('circeq', 8791),                         # ≗
        build1('circlearrowleft', 8634),                # ↺
        build1('circlearrowright', 8635),               # ↻
        build1('circledast', 8859),                     # ⊛
        build1('circledcirc', 8858),                    # ⊚
        build1('circleddash', 8861),                    # ⊝
        build1('CircleDot', 8857),                      # ⊙
        build1('circledR', 174),                        # ®
        build1('circledS', 9416),                       # Ⓢ
        build1('CircleMinus', 8854),                    # ⊖
        build1('CirclePlus', 8853),                     # ⊕
        build1('CircleTimes', 8855),                    # ⊗
        build1('cirE', 10691),                          # ⧃
        build1('cire', 8791),                           # ≗
        build1('cirfnint', 10768),                      # ⨐
        build1('cirmid', 10991),                        # ⫯
        build1('cirscir', 10690),                       # ⧂
        build1('ClockwiseContourIntegral', 8754),       # ∲
        build1('CloseCurlyDoubleQuote', 8221),          # ”
        build1('CloseCurlyQuote', 8217),                # ’
        build1('clubsuit', 9827),                       # ♣
        build1('Colon', 8759),                          # ∷
        build1('colon', 58),                            # :
        build1('Colone', 10868),                        # ⩴
        build1('colone', 8788),                         # ≔
        build1('coloneq', 8788),                        # ≔
        build1('comma', 44),                            # ,
        build1('commat', 64),                           # @
        build1('comp', 8705),                           # ∁
        build1('compfn', 8728),                         # ∘
        build1('complement', 8705),                     # ∁
        build1('complexes', 8450),                      # ℂ
        build1('cong', 8773),                           # ≅
        build1('congdot', 10861),                       # ⩭
        build1('Congruent', 8801),                      # ≡
        build1('Conint', 8751),                         # ∯
        build1('conint', 8750),                         # ∮
        build1('ContourIntegral', 8750),                # ∮
        build1('Copf', 8450),                           # ℂ
        build1('copf', 120148),                         # 𝕔
        build1('coprod', 8720),                         # ∐
        build1('Coproduct', 8720),                      # ∐
        build1('COPY', 169),                            # ©
        build1('COPY', 169),                            # ©
        build1('copysr', 8471),                         # ℗
        build1('CounterClockwiseContourIntegral', 8755),# ∳
        build1('crarr', 8629),                          # ↵
        build1('Cross', 10799),                         # ⨯
        build1('cross', 10007),                         # ✗
        build1('Cscr', 119966),                         # 𝒞
        build1('cscr', 119992),                         # 𝒸
        build1('csub', 10959),                          # ⫏
        build1('csube', 10961),                         # ⫑
        build1('csup', 10960),                          # ⫐
        build1('csupe', 10962),                         # ⫒
        build1('ctdot', 8943),                          # ⋯
        build1('cudarrl', 10552),                       # ⤸
        build1('cudarrr', 10549),                       # ⤵
        build1('cuepr', 8926),                          # ⋞
        build1('cuesc', 8927),                          # ⋟
        build1('cularr', 8630),                         # ↶
        build1('cularrp', 10557),                       # ⤽
        build1('Cup', 8915),                            # ⋓
        build1('cup', 8746),                            # ∪
        build1('cupbrcap', 10824),                      # ⩈
        build1('CupCap', 8781),                         # ≍
        build1('cupcap', 10822),                        # ⩆
        build1('cupcup', 10826),                        # ⩊
        build1('cupdot', 8845),                         # ⊍
        build1('cupor', 10821),                         # ⩅
        build2('cups', '∪︀'),                            # ∪︀
        build1('curarr', 8631),                         # ↷
        build1('curarrm', 10556),                       # ⤼
        build1('curlyeqprec', 8926),                    # ⋞
        build1('curlyeqsucc', 8927),                    # ⋟
        build1('curlyvee', 8910),                       # ⋎
        build1('curlywedge', 8911),                     # ⋏
        build1('curvearrowleft', 8630),                 # ↶
        build1('curvearrowright', 8631),                # ↷
        build1('cuvee', 8910),                          # ⋎
        build1('cuwed', 8911),                          # ⋏
        build1('cwconint', 8754),                       # ∲
        build1('cwint', 8753),                          # ∱
        build1('cylcty', 9005),                         # ⌭
        build1('Dagger', 8225),                         # ‡
        build1('daleth', 8504),                         # ℸ
        build1('Darr', 8609),                           # ↡
        build1('dArr', 8659),                           # ⇓
        build1('darr', 8595),                           # ↓
        build1('dash', 8208),                           # ‐
        build1('Dashv', 10980),                         # ⫤
        build1('dashv', 8867),                          # ⊣
        build1('dbkarow', 10511),                       # ⤏
        build1('dblac', 733),                           # ˝
        build1('Dcaron', 270),                          # Ď
        build1('dcaron', 271),                          # ď
        build1('Dcy', 1044),                            # Д
        build1('dcy', 1076),                            # д
        build1('DD', 8517),                             # ⅅ
        build1('dd', 8518),                             # ⅆ
        build1('ddarr', 8650),                          # ⇊
        build1('DDotrahd', 10513),                      # ⤑
        build1('ddotseq', 10871),                       # ⩷
        build1('Del', 8711),                            # ∇
        build1('demptyv', 10673),                       # ⦱
        build1('dfisht', 10623),                        # ⥿
        build1('Dfr', 120071),                          # 𝔇
        build1('dfr', 120097),                          # 𝔡
        build1('dHar', 10597),                          # ⥥
        build1('dharl', 8643),                          # ⇃
        build1('dharr', 8642),                          # ⇂
        build1('DiacriticalAcute', 180),                # ´
        build1('DiacriticalDot', 729),                  # ˙
        build1('DiacriticalDoubleAcute', 733),          # ˝
        build1('DiacriticalGrave', 96),                 # `
        build1('DiacriticalTilde', 732),                # ˜
        build1('diam', 8900),                           # ⋄
        build1('Diamond', 8900),                        # ⋄
        build1('diamond', 8900),                        # ⋄
        build1('diamondsuit', 9830),                    # ♦
        build1('die', 168),                             # ¨
        build1('DifferentialD', 8518),                  # ⅆ
        build1('digamma', 989),                         # ϝ
        build1('disin', 8946),                          # ⋲
        build1('div', 247),                             # ÷
        build1('divideontimes', 8903),                  # ⋇
        build1('divonx', 8903),                         # ⋇
        build1('DJcy', 1026),                           # Ђ
        build1('djcy', 1106),                           # ђ
        build1('dlcorn', 8990),                         # ⌞
        build1('dlcrop', 8973),                         # ⌍
        build1('dollar', 36),                           # $
        build1('Dopf', 120123),                         # 𝔻
        build1('dopf', 120149),                         # 𝕕
        build1('Dot', 168),                             # ¨
        build1('dot', 729),                             # ˙
        build1('DotDot', 8412),                         #⃜ 
        build1('doteq', 8784),                          # ≐
        build1('doteqdot', 8785),                       # ≑
        build1('DotEqual', 8784),                       # ≐
        build1('dotminus', 8760),                       # ∸
        build1('dotplus', 8724),                        # ∔
        build1('dotsquare', 8865),                      # ⊡
        build1('doublebarwedge', 8966),                 # ⌆
        build1('DoubleContourIntegral', 8751),          # ∯
        build1('DoubleDot', 168),                       # ¨
        build1('DoubleDownArrow', 8659),                # ⇓
        build1('DoubleLeftArrow', 8656),                # ⇐
        build1('DoubleLeftRightArrow', 8660),           # ⇔
        build1('DoubleLeftTee', 10980),                 # ⫤
        build1('DoubleLongLeftArrow', 10232),           # ⟸
        build1('DoubleLongLeftRightArrow', 10234),      # ⟺
        build1('DoubleLongRightArrow', 10233),          # ⟹
        build1('DoubleRightArrow', 8658),               # ⇒
        build1('DoubleRightTee', 8872),                 # ⊨
        build1('DoubleUpArrow', 8657),                  # ⇑
        build1('DoubleUpDownArrow', 8661),              # ⇕
        build1('DoubleVerticalBar', 8741),              # ∥
        build1('DownArrow', 8595),                      # ↓
        build1('Downarrow', 8659),                      # ⇓
        build1('downarrow', 8595),                      # ↓
        build1('DownArrowBar', 10515),                  # ⤓
        build1('DownArrowUpArrow', 8693),               # ⇵
        build1('DownBreve', 785),                       #̑ 
        build1('downdownarrows', 8650),                 # ⇊
        build1('downharpoonleft', 8643),                # ⇃
        build1('downharpoonright', 8642),               # ⇂
        build1('DownLeftRightVector', 10576),           # ⥐
        build1('DownLeftTeeVector', 10590),             # ⥞
        build1('DownLeftVector', 8637),                 # ↽
        build1('DownLeftVectorBar', 10582),             # ⥖
        build1('DownRightTeeVector', 10591),            # ⥟
        build1('DownRightVector', 8641),                # ⇁
        build1('DownRightVectorBar', 10583),            # ⥗
        build1('DownTee', 8868),                        # ⊤
        build1('DownTeeArrow', 8615),                   # ↧
        build1('drbkarow', 10512),                      # ⤐
        build1('drcorn', 8991),                         # ⌟
        build1('drcrop', 8972),                         # ⌌
        build1('Dscr', 119967),                         # 𝒟
        build1('dscr', 119993),                         # 𝒹
        build1('DScy', 1029),                           # Ѕ
        build1('dscy', 1109),                           # ѕ
        build1('dsol', 10742),                          # ⧶
        build1('Dstrok', 272),                          # Đ
        build1('dstrok', 273),                          # đ
        build1('dtdot', 8945),                          # ⋱
        build1('dtri', 9663),                           # ▿
        build1('dtrif', 9662),                          # ▾
        build1('duarr', 8693),                          # ⇵
        build1('duhar', 10607),                         # ⥯
        build1('dwangle', 10662),                       # ⦦
        build1('DZcy', 1039),                           # Џ
        build1('dzcy', 1119),                           # џ
        build1('dzigrarr', 10239),                      # ⟿
        build1('easter', 10862),                        # ⩮
        build1('Ecaron', 282),                          # Ě
        build1('ecaron', 283),                          # ě
        build1('ecir', 8790),                           # ≖
        build1('ecolon', 8789),                         # ≕
        build1('Ecy', 1069),                            # Э
        build1('ecy', 1101),                            # э
        build1('eDDot', 10871),                         # ⩷
        build1('Edot', 278),                            # Ė
        build1('eDot', 8785),                           # ≑
        build1('edot', 279),                            # ė
        build1('ee', 8519),                             # ⅇ
        build1('efDot', 8786),                          # ≒
        build1('Efr', 120072),                          # 𝔈
        build1('efr', 120098),                          # 𝔢
        build1('eg', 10906),                            # ⪚
        build1('egs', 10902),                           # ⪖
        build1('egsdot', 10904),                        # ⪘
        build1('el', 10905),                            # ⪙
        build1('Element', 8712),                        # ∈
        build1('elinters', 9191),                       # ⏧
        build1('ell', 8467),                            # ℓ
        build1('els', 10901),                           # ⪕
        build1('elsdot', 10903),                        # ⪗
        build1('Emacr', 274),                           # Ē
        build1('emacr', 275),                           # ē
        build1('empty', 8709),                          # ∅
        build1('emptyset', 8709),                       # ∅
        build1('EmptySmallSquare', 9723),               # ◻
        build1('emptyv', 8709),                         # ∅
        build1('EmptyVerySmallSquare', 9643),           # ▫
        build1('emsp13', 8196),                         #  
        build1('emsp14', 8197),                         #  
        build1('ENG', 330),                             # Ŋ
        build1('eng', 331),                             # ŋ
        build1('Eogon', 280),                           # Ę
        build1('eogon', 281),                           # ę
        build1('Eopf', 120124),                         # 𝔼
        build1('eopf', 120150),                         # 𝕖
        build1('epar', 8917),                           # ⋕
        build1('eparsl', 10723),                        # ⧣
        build1('eplus', 10865),                         # ⩱
        build1('epsiv', 1013),                          # ϵ
        build1('eqcirc', 8790),                         # ≖
        build1('eqcolon', 8789),                        # ≕
        build1('eqsim', 8770),                          # ≂
        build1('eqslantgtr', 10902),                    # ⪖
        build1('eqslantless', 10901),                   # ⪕
        build1('Equal', 10869),                         # ⩵
        build1('equals', 61),                           # =
        build1('EqualTilde', 8770),                     # ≂
        build1('equest', 8799),                         # ≟
        build1('Equilibrium', 8652),                    # ⇌
        build1('equiv', 8801),                          # ≡
        build1('equivDD', 10872),                       # ⩸
        build1('eqvparsl', 10725),                      # ⧥
        build1('erarr', 10609),                         # ⥱
        build1('erDot', 8787),                          # ≓
        build1('Escr', 8496),                           # ℰ
        build1('escr', 8495),                           # ℯ
        build1('esdot', 8784),                          # ≐
        build1('Esim', 10867),                          # ⩳
        build1('esim', 8770),                           # ≂
        build1('excl', 33),                             # !
        build1('exist', 8707),                          # ∃
        build1('Exists', 8707),                         # ∃
        build1('expectation', 8496),                    # ℰ
        build1('ExponentialE', 8519),                   # ⅇ
        build1('exponentiale', 8519),                   # ⅇ
        build1('fallingdotseq', 8786),                  # ≒
        build1('Fcy', 1060),                            # Ф
        build1('fcy', 1092),                            # ф
        build1('female', 9792),                         # ♀
        build1('ffilig', 64259),                        # ﬃ
        build1('fflig', 64256),                         # ﬀ
        build1('ffllig', 64260),                        # ﬄ
        build1('Ffr', 120073),                          # 𝔉
        build1('ffr', 120099),                          # 𝔣
        build1('filig', 64257),                         # ﬁ
        build1('FilledSmallSquare', 9724),              # ◼
        build1('FilledVerySmallSquare', 9642),          # ▪
        build2('fjlig', 'fj'),                          # fj
        build1('flat', 9837),                           # ♭
        build1('fllig', 64258),                         # ﬂ
        build1('fltns', 9649),                          # ▱
        build1('Fopf', 120125),                         # 𝔽
        build1('fopf', 120151),                         # 𝕗
        build1('ForAll', 8704),                         # ∀
        build1('forall', 8704),                         # ∀
        build1('fork', 8916),                           # ⋔
        build1('forkv', 10969),                         # ⫙
        build1('Fouriertrf', 8497),                     # ℱ
        build1('fpartint', 10765),                      # ⨍
        build1('frac13', 8531),                         # ⅓
        build1('frac15', 8533),                         # ⅕
        build1('frac16', 8537),                         # ⅙
        build1('frac18', 8539),                         # ⅛
        build1('frac23', 8532),                         # ⅔
        build1('frac25', 8534),                         # ⅖
        build1('frac35', 8535),                         # ⅗
        build1('frac38', 8540),                         # ⅜
        build1('frac45', 8536),                         # ⅘
        build1('frac56', 8538),                         # ⅚
        build1('frac58', 8541),                         # ⅝
        build1('frac78', 8542),                         # ⅞
        build1('frasl', 8260),                          # ⁄
        build1('frown', 8994),                          # ⌢
        build1('Fscr', 8497),                           # ℱ
        build1('fscr', 119995),                         # 𝒻
        build1('gacute', 501),                          # ǵ
        build1('Gammad', 988),                          # Ϝ
        build1('gammad', 989),                          # ϝ
        build1('gap', 10886),                           # ⪆
        build1('Gbreve', 286),                          # Ğ
        build1('gbreve', 287),                          # ğ
        build1('Gcedil', 290),                          # Ģ
        build1('Gcirc', 284),                           # Ĝ
        build1('gcirc', 285),                           # ĝ
        build1('Gcy', 1043),                            # Г
        build1('gcy', 1075),                            # г
        build1('Gdot', 288),                            # Ġ
        build1('gdot', 289),                            # ġ
        build1('gE', 8807),                             # ≧
        build1('ge', 8805),                             # ≥
        build1('gEl', 10892),                           # ⪌
        build1('gel', 8923),                            # ⋛
        build1('geq', 8805),                            # ≥
        build1('geqq', 8807),                           # ≧
        build1('geqslant', 10878),                      # ⩾
        build1('ges', 10878),                           # ⩾
        build1('gescc', 10921),                         # ⪩
        build1('gesdot', 10880),                        # ⪀
        build1('gesdoto', 10882),                       # ⪂
        build1('gesdotol', 10884),                      # ⪄
        build2('gesl', '⋛︀'),                            # ⋛︀
        build1('gesles', 10900),                        # ⪔
        build1('Gfr', 120074),                          # 𝔊
        build1('gfr', 120100),                          # 𝔤
        build1('Gg', 8921),                             # ⋙
        build1('gg', 8811),                             # ≫
        build1('ggg', 8921),                            # ⋙
        build1('gimel', 8503),                          # ℷ
        build1('GJcy', 1027),                           # Ѓ
        build1('gjcy', 1107),                           # ѓ
        build1('gl', 8823),                             # ≷
        build1('gla', 10917),                           # ⪥
        build1('glE', 10898),                           # ⪒
        build1('glj', 10916),                           # ⪤
        build1('gnap', 10890),                          # ⪊
        build1('gnapprox', 10890),                      # ⪊
        build1('gnE', 8809),                            # ≩
        build1('gne', 10888),                           # ⪈
        build1('gneq', 10888),                          # ⪈
        build1('gneqq', 8809),                          # ≩
        build1('gnsim', 8935),                          # ⋧
        build1('Gopf', 120126),                         # 𝔾
        build1('gopf', 120152),                         # 𝕘
        build1('grave', 96),                            # `
        build1('GreaterEqual', 8805),                   # ≥
        build1('GreaterEqualLess', 8923),               # ⋛
        build1('GreaterFullEqual', 8807),               # ≧
        build1('GreaterGreater', 10914),                # ⪢
        build1('GreaterLess', 8823),                    # ≷
        build1('GreaterSlantEqual', 10878),             # ⩾
        build1('GreaterTilde', 8819),                   # ≳
        build1('Gscr', 119970),                         # 𝒢
        build1('gscr', 8458),                           # ℊ
        build1('gsim', 8819),                           # ≳
        build1('gsime', 10894),                         # ⪎
        build1('gsiml', 10896),                         # ⪐
        build1('Gt', 8811),                             # ≫
        build1('gtcc', 10919),                          # ⪧
        build1('gtcir', 10874),                         # ⩺
        build1('gtdot', 8919),                          # ⋗
        build1('gtlPar', 10645),                        # ⦕
        build1('gtquest', 10876),                       # ⩼
        build1('gtrapprox', 10886),                     # ⪆
        build1('gtrarr', 10616),                        # ⥸
        build1('gtrdot', 8919),                         # ⋗
        build1('gtreqless', 8923),                      # ⋛
        build1('gtreqqless', 10892),                    # ⪌
        build1('gtrless', 8823),                        # ≷
        build1('gtrsim', 8819),                         # ≳
        build2('gvertneqq', '≩︀'),                       # ≩︀
        build2('gvnE', '≩︀'),                            # ≩︀
        build1('Hacek', 711),                           # ˇ
        build1('hairsp', 8202),                         #  
        build1('half', 189),                            # ½
        build1('hamilt', 8459),                         # ℋ
        build1('HARDcy', 1066),                         # Ъ
        build1('hardcy', 1098),                         # ъ
        build1('hArr', 8660),                           # ⇔
        build1('harr', 8596),                           # ↔
        build1('harrcir', 10568),                       # ⥈
        build1('harrw', 8621),                          # ↭
        build1('Hat', 94),                              # ^
        build1('hbar', 8463),                           # ℏ
        build1('Hcirc', 292),                           # Ĥ
        build1('hcirc', 293),                           # ĥ
        build1('heartsuit', 9829),                      # ♥
        build1('hercon', 8889),                         # ⊹
        build1('Hfr', 8460),                            # ℌ
        build1('hfr', 120101),                          # 𝔥
        build1('HilbertSpace', 8459),                   # ℋ
        build1('hksearow', 10533),                      # ⤥
        build1('hkswarow', 10534),                      # ⤦
        build1('hoarr', 8703),                          # ⇿
        build1('homtht', 8763),                         # ∻
        build1('hookleftarrow', 8617),                  # ↩
        build1('hookrightarrow', 8618),                 # ↪
        build1('Hopf', 8461),                           # ℍ
        build1('hopf', 120153),                         # 𝕙
        build1('horbar', 8213),                         # ―
        build1('HorizontalLine', 9472),                 # ─
        build1('Hscr', 8459),                           # ℋ
        build1('hscr', 119997),                         # 𝒽
        build1('hslash', 8463),                         # ℏ
        build1('Hstrok', 294),                          # Ħ
        build1('hstrok', 295),                          # ħ
        build1('HumpDownHump', 8782),                   # ≎
        build1('HumpEqual', 8783),                      # ≏
        build1('hybull', 8259),                         # ⁃
        build1('hyphen', 8208),                         # ‐
        build1('ic', 8291),                             # ⁣
        build1('Icy', 1048),                            # И
        build1('icy', 1080),                            # и
        build1('Idot', 304),                            # İ
        build1('IEcy', 1045),                           # Е
        build1('iecy', 1077),                           # е
        build1('iff', 8660),                            # ⇔
        build1('Ifr', 8465),                            # ℑ
        build1('ifr', 120102),                          # 𝔦
        build1('ii', 8520),                             # ⅈ
        build1('iiiint', 10764),                        # ⨌
        build1('iiint', 8749),                          # ∭
        build1('iinfin', 10716),                        # ⧜
        build1('iiota', 8489),                          # ℩
        build1('IJlig', 306),                           # Ĳ
        build1('ijlig', 307),                           # ĳ
        build1('Im', 8465),                             # ℑ
        build1('Imacr', 298),                           # Ī
        build1('imacr', 299),                           # ī
        build1('ImaginaryI', 8520),                     # ⅈ
        build1('imagline', 8464),                       # ℐ
        build1('imagpart', 8465),                       # ℑ
        build1('imath', 305),                           # ı
        build1('imof', 8887),                           # ⊷
        build1('imped', 437),                           # Ƶ
        build1('Implies', 8658),                        # ⇒
        build1('in', 8712),                             # ∈
        build1('incare', 8453),                         # ℅
        build1('infin', 8734),                          # ∞
        build1('infintie', 10717),                      # ⧝
        build1('inodot', 305),                          # ı
        build1('Int', 8748),                            # ∬
        build1('int', 8747),                            # ∫
        build1('intcal', 8890),                         # ⊺
        build1('integers', 8484),                       # ℤ
        build1('Integral', 8747),                       # ∫
        build1('intercal', 8890),                       # ⊺
        build1('Intersection', 8898),                   # ⋂
        build1('intlarhk', 10775),                      # ⨗
        build1('intprod', 10812),                       # ⨼
        build1('InvisibleComma', 8291),                 # ⁣
        build1('InvisibleTimes', 8290),                 # ⁢
        build1('IOcy', 1025),                           # Ё
        build1('iocy', 1105),                           # ё
        build1('Iogon', 302),                           # Į
        build1('iogon', 303),                           # į
        build1('Iopf', 120128),                         # 𝕀
        build1('iopf', 120154),                         # 𝕚
        build1('iprod', 10812),                         # ⨼
        build1('Iscr', 8464),                           # ℐ
        build1('iscr', 119998),                         # 𝒾
        build1('isin', 8712),                           # ∈
        build1('isindot', 8949),                        # ⋵
        build1('isinE', 8953),                          # ⋹
        build1('isins', 8948),                          # ⋴
        build1('isinsv', 8947),                         # ⋳
        build1('isinv', 8712),                          # ∈
        build1('it', 8290),                             # ⁢
        build1('Itilde', 296),                          # Ĩ
        build1('itilde', 297),                          # ĩ
        build1('Iukcy', 1030),                          # І
        build1('iukcy', 1110),                          # і
        build1('Jcirc', 308),                           # Ĵ
        build1('jcirc', 309),                           # ĵ
        build1('Jcy', 1049),                            # Й
        build1('jcy', 1081),                            # й
        build1('Jfr', 120077),                          # 𝔍
        build1('jfr', 120103),                          # 𝔧
        build1('jmath', 567),                           # ȷ
        build1('Jopf', 120129),                         # 𝕁
        build1('jopf', 120155),                         # 𝕛
        build1('Jscr', 119973),                         # 𝒥
        build1('jscr', 119999),                         # 𝒿
        build1('Jsercy', 1032),                         # Ј
        build1('jsercy', 1112),                         # ј
        build1('Jukcy', 1028),                          # Є
        build1('jukcy', 1108),                          # є
        build1('kappav', 1008),                         # ϰ
        build1('Kcedil', 310),                          # Ķ
        build1('kcedil', 311),                          # ķ
        build1('Kcy', 1050),                            # К
        build1('kcy', 1082),                            # к
        build1('Kfr', 120078),                          # 𝔎
        build1('kfr', 120104),                          # 𝔨
        build1('kgreen', 312),                          # ĸ
        build1('KHcy', 1061),                           # Х
        build1('khcy', 1093),                           # х
        build1('KJcy', 1036),                           # Ќ
        build1('kjcy', 1116),                           # ќ
        build1('Kopf', 120130),                         # 𝕂
        build1('kopf', 120156),                         # 𝕜
        build1('Kscr', 119974),                         # 𝒦
        build1('kscr', 120000),                         # 𝓀
        build1('lAarr', 8666),                          # ⇚
        build1('Lacute', 313),                          # Ĺ
        build1('lacute', 314),                          # ĺ
        build1('laemptyv', 10676),                      # ⦴
        build1('lagran', 8466),                         # ℒ
        build1('Lang', 10218),                          # ⟪
        build1('langd', 10641),                         # ⦑
        build1('langle', 10216),                        # ⟨
        build1('lap', 10885),                           # ⪅
        build1('Laplacetrf', 8466),                     # ℒ
        build1('Larr', 8606),                           # ↞
        build1('lArr', 8656),                           # ⇐
        build1('larr', 8592),                           # ←
        build1('larrb', 8676),                          # ⇤
        build1('larrbfs', 10527),                       # ⤟
        build1('larrfs', 10525),                        # ⤝
        build1('larrhk', 8617),                         # ↩
        build1('larrlp', 8619),                         # ↫
        build1('larrpl', 10553),                        # ⤹
        build1('larrsim', 10611),                       # ⥳
        build1('larrtl', 8610),                         # ↢
        build1('lat', 10923),                           # ⪫
        build1('lAtail', 10523),                        # ⤛
        build1('latail', 10521),                        # ⤙
        build1('late', 10925),                          # ⪭
        build2('lates', '⪭︀'),                           # ⪭︀
        build1('lBarr', 10510),                         # ⤎
        build1('lbarr', 10508),                         # ⤌
        build1('lbbrk', 10098),                         # ❲
        build1('lbrace', 123),                          # {
        build1('lbrack', 91),                           # [
        build1('lbrke', 10635),                         # ⦋
        build1('lbrksld', 10639),                       # ⦏
        build1('lbrkslu', 10637),                       # ⦍
        build1('Lcaron', 317),                          # Ľ
        build1('lcaron', 318),                          # ľ
        build1('Lcedil', 315),                          # Ļ
        build1('lcedil', 316),                          # ļ
        build1('lceil', 8968),                          # ⌈
        build1('lcub', 123),                            # {
        build1('Lcy', 1051),                            # Л
        build1('lcy', 1083),                            # л
        build1('ldca', 10550),                          # ⤶
        build1('ldquor', 8222),                         # „
        build1('ldrdhar', 10599),                       # ⥧
        build1('ldrushar', 10571),                      # ⥋
        build1('ldsh', 8626),                           # ↲
        build1('lE', 8806),                             # ≦
        build1('le', 8804),                             # ≤
        build1('LeftAngleBracket', 10216),              # ⟨
        build1('LeftArrow', 8592),                      # ←
        build1('Leftarrow', 8656),                      # ⇐
        build1('leftarrow', 8592),                      # ←
        build1('LeftArrowBar', 8676),                   # ⇤
        build1('LeftArrowRightArrow', 8646),            # ⇆
        build1('leftarrowtail', 8610),                  # ↢
        build1('LeftCeiling', 8968),                    # ⌈
        build1('LeftDoubleBracket', 10214),             # ⟦
        build1('LeftDownTeeVector', 10593),             # ⥡
        build1('LeftDownVector', 8643),                 # ⇃
        build1('LeftDownVectorBar', 10585),             # ⥙
        build1('LeftFloor', 8970),                      # ⌊
        build1('leftharpoondown', 8637),                # ↽
        build1('leftharpoonup', 8636),                  # ↼
        build1('leftleftarrows', 8647),                 # ⇇
        build1('LeftRightArrow', 8596),                 # ↔
        build1('Leftrightarrow', 8660),                 # ⇔
        build1('leftrightarrow', 8596),                 # ↔
        build1('leftrightarrows', 8646),                # ⇆
        build1('leftrightharpoons', 8651),              # ⇋
        build1('leftrightsquigarrow', 8621),            # ↭
        build1('LeftRightVector', 10574),               # ⥎
        build1('LeftTee', 8867),                        # ⊣
        build1('LeftTeeArrow', 8612),                   # ↤
        build1('LeftTeeVector', 10586),                 # ⥚
        build1('leftthreetimes', 8907),                 # ⋋
        build1('LeftTriangle', 8882),                   # ⊲
        build1('LeftTriangleBar', 10703),               # ⧏
        build1('LeftTriangleEqual', 8884),              # ⊴
        build1('LeftUpDownVector', 10577),              # ⥑
        build1('LeftUpTeeVector', 10592),               # ⥠
        build1('LeftUpVector', 8639),                   # ↿
        build1('LeftUpVectorBar', 10584),               # ⥘
        build1('LeftVector', 8636),                     # ↼
        build1('LeftVectorBar', 10578),                 # ⥒
        build1('lEg', 10891),                           # ⪋
        build1('leg', 8922),                            # ⋚
        build1('leq', 8804),                            # ≤
        build1('leqq', 8806),                           # ≦
        build1('leqslant', 10877),                      # ⩽
        build1('les', 10877),                           # ⩽
        build1('lescc', 10920),                         # ⪨
        build1('lesdot', 10879),                        # ⩿
        build1('lesdoto', 10881),                       # ⪁
        build1('lesdotor', 10883),                      # ⪃
        build2('lesg', '⋚︀'),                            # ⋚︀
        build1('lesges', 10899),                        # ⪓
        build1('lessapprox', 10885),                    # ⪅
        build1('lessdot', 8918),                        # ⋖
        build1('lesseqgtr', 8922),                      # ⋚
        build1('lesseqqgtr', 10891),                    # ⪋
        build1('LessEqualGreater', 8922),               # ⋚
        build1('LessFullEqual', 8806),                  # ≦
        build1('LessGreater', 8822),                    # ≶
        build1('lessgtr', 8822),                        # ≶
        build1('LessLess', 10913),                      # ⪡
        build1('lesssim', 8818),                        # ≲
        build1('LessSlantEqual', 10877),                # ⩽
        build1('LessTilde', 8818),                      # ≲
        build1('lfisht', 10620),                        # ⥼
        build1('lfloor', 8970),                         # ⌊
        build1('Lfr', 120079),                          # 𝔏
        build1('lfr', 120105),                          # 𝔩
        build1('lg', 8822),                             # ≶
        build1('lgE', 10897),                           # ⪑
        build1('lHar', 10594),                          # ⥢
        build1('lhard', 8637),                          # ↽
        build1('lharu', 8636),                          # ↼
        build1('lharul', 10602),                        # ⥪
        build1('lhblk', 9604),                          # ▄
        build1('LJcy', 1033),                           # Љ
        build1('ljcy', 1113),                           # љ
        build1('Ll', 8920),                             # ⋘
        build1('ll', 8810),                             # ≪
        build1('llarr', 8647),                          # ⇇
        build1('llcorner', 8990),                       # ⌞
        build1('Lleftarrow', 8666),                     # ⇚
        build1('llhard', 10603),                        # ⥫
        build1('lltri', 9722),                          # ◺
        build1('Lmidot', 319),                          # Ŀ
        build1('lmidot', 320),                          # ŀ
        build1('lmoust', 9136),                         # ⎰
        build1('lmoustache', 9136),                     # ⎰
        build1('lnap', 10889),                          # ⪉
        build1('lnapprox', 10889),                      # ⪉
        build1('lnE', 8808),                            # ≨
        build1('lne', 10887),                           # ⪇
        build1('lneq', 10887),                          # ⪇
        build1('lneqq', 8808),                          # ≨
        build1('lnsim', 8934),                          # ⋦
        build1('loang', 10220),                         # ⟬
        build1('loarr', 8701),                          # ⇽
        build1('lobrk', 10214),                         # ⟦
        build1('LongLeftArrow', 10229),                 # ⟵
        build1('Longleftarrow', 10232),                 # ⟸
        build1('longleftarrow', 10229),                 # ⟵
        build1('LongLeftRightArrow', 10231),            # ⟷
        build1('Longleftrightarrow', 10234),            # ⟺
        build1('longleftrightarrow', 10231),            # ⟷
        build1('longmapsto', 10236),                    # ⟼
        build1('LongRightArrow', 10230),                # ⟶
        build1('Longrightarrow', 10233),                # ⟹
        build1('longrightarrow', 10230),                # ⟶
        build1('looparrowleft', 8619),                  # ↫
        build1('looparrowright', 8620),                 # ↬
        build1('lopar', 10629),                         # ⦅
        build1('Lopf', 120131),                         # 𝕃
        build1('lopf', 120157),                         # 𝕝
        build1('loplus', 10797),                        # ⨭
        build1('lotimes', 10804),                       # ⨴
        build1('lowast', 8727),                         # ∗
        build1('lowbar', 95),                           # _
        build1('LowerLeftArrow', 8601),                 # ↙
        build1('LowerRightArrow', 8600),                # ↘
        build1('lozenge', 9674),                        # ◊
        build1('lozf', 10731),                          # ⧫
        build1('lpar', 40),                             # (
        build1('lparlt', 10643),                        # ⦓
        build1('lrarr', 8646),                          # ⇆
        build1('lrcorner', 8991),                       # ⌟
        build1('lrhar', 8651),                          # ⇋
        build1('lrhard', 10605),                        # ⥭
        build1('lrtri', 8895),                          # ⊿
        build1('Lscr', 8466),                           # ℒ
        build1('lscr', 120001),                         # 𝓁
        build1('Lsh', 8624),                            # ↰
        build1('lsh', 8624),                            # ↰
        build1('lsim', 8818),                           # ≲
        build1('lsime', 10893),                         # ⪍
        build1('lsimg', 10895),                         # ⪏
        build1('lsqb', 91),                             # [
        build1('lsquor', 8218),                         # ‚
        build1('Lstrok', 321),                          # Ł
        build1('lstrok', 322),                          # ł
        build1('Lt', 8810),                             # ≪
        build1('ltcc', 10918),                          # ⪦
        build1('ltcir', 10873),                         # ⩹
        build1('ltdot', 8918),                          # ⋖
        build1('lthree', 8907),                         # ⋋
        build1('ltimes', 8905),                         # ⋉
        build1('ltlarr', 10614),                        # ⥶
        build1('ltquest', 10875),                       # ⩻
        build1('ltri', 9667),                           # ◃
        build1('ltrie', 8884),                          # ⊴
        build1('ltrif', 9666),                          # ◂
        build1('ltrPar', 10646),                        # ⦖
        build1('lurdshar', 10570),                      # ⥊
        build1('luruhar', 10598),                       # ⥦
        build2('lvertneqq', '≨︀'),                       # ≨︀
        build2('lvnE', '≨︀'),                            # ≨︀
        build1('male', 9794),                           # ♂
        build1('malt', 10016),                          # ✠
        build1('maltese', 10016),                       # ✠
        build1('Map', 10501),                           # ⤅
        build1('map', 8614),                            # ↦
        build1('mapsto', 8614),                         # ↦
        build1('mapstodown', 8615),                     # ↧
        build1('mapstoleft', 8612),                     # ↤
        build1('mapstoup', 8613),                       # ↥
        build1('marker', 9646),                         # ▮
        build1('mcomma', 10793),                        # ⨩
        build1('Mcy', 1052),                            # М
        build1('mcy', 1084),                            # м
        build1('mDDot', 8762),                          # ∺
        build1('measuredangle', 8737),                  # ∡
        build1('MediumSpace', 8287),                    #  
        build1('Mellintrf', 8499),                      # ℳ
        build1('Mfr', 120080),                          # 𝔐
        build1('mfr', 120106),                          # 𝔪
        build1('mho', 8487),                            # ℧
        build1('mid', 8739),                            # ∣
        build1('midast', 42),                           # *
        build1('midcir', 10992),                        # ⫰
        build1('minus', 8722),                          # −
        build1('minusb', 8863),                         # ⊟
        build1('minusd', 8760),                         # ∸
        build1('minusdu', 10794),                       # ⨪
        build1('MinusPlus', 8723),                      # ∓
        build1('mlcp', 10971),                          # ⫛
        build1('mldr', 8230),                           # …
        build1('mnplus', 8723),                         # ∓
        build1('models', 8871),                         # ⊧
        build1('Mopf', 120132),                         # 𝕄
        build1('mopf', 120158),                         # 𝕞
        build1('mp', 8723),                             # ∓
        build1('Mscr', 8499),                           # ℳ
        build1('mscr', 120002),                         # 𝓂
        build1('mstpos', 8766),                         # ∾
        build1('multimap', 8888),                       # ⊸
        build1('mumap', 8888),                          # ⊸
        build1('nabla', 8711),                          # ∇
        build1('Nacute', 323),                          # Ń
        build1('nacute', 324),                          # ń
        build2('nang', '∠⃒'),                            # ∠⃒
        build1('nap', 8777),                            # ≉
        build2('napE', '⩰̸'),                            # ⩰̸
        build2('napid', '≋̸'),                           # ≋̸
        build1('napos', 329),                           # ŉ
        build1('napprox', 8777),                        # ≉
        build1('natur', 9838),                          # ♮
        build1('natural', 9838),                        # ♮
        build1('naturals', 8469),                       # ℕ
        build2('nbump', '≎̸'),                           # ≎̸
        build2('nbumpe', '≏̸'),                          # ≏̸
        build1('ncap', 10819),                          # ⩃
        build1('Ncaron', 327),                          # Ň
        build1('ncaron', 328),                          # ň
        build1('Ncedil', 325),                          # Ņ
        build1('ncedil', 326),                          # ņ
        build1('ncong', 8775),                          # ≇
        build2('ncongdot', '⩭̸'),                        # ⩭̸
        build1('ncup', 10818),                          # ⩂
        build1('Ncy', 1053),                            # Н
        build1('ncy', 1085),                            # н
        build1('ne', 8800),                             # ≠
        build1('nearhk', 10532),                        # ⤤
        build1('neArr', 8663),                          # ⇗
        build1('nearr', 8599),                          # ↗
        build1('nearrow', 8599),                        # ↗
        build2('nedot', '≐̸'),                           # ≐̸
        build1('NegativeMediumSpace', 8203),            # ​
        build1('NegativeThickSpace', 8203),             # ​
        build1('NegativeThinSpace', 8203),              # ​
        build1('NegativeVeryThinSpace', 8203),          # ​
        build1('nequiv', 8802),                         # ≢
        build1('nesear', 10536),                        # ⤨
        build2('nesim', '≂̸'),                           # ≂̸
        build1('NestedGreaterGreater', 8811),           # ≫
        build1('NestedLessLess', 8810),                 # ≪
        build1('NewLine', 10),                          # 
        build1('nexist', 8708),                         # ∄
        build1('nexists', 8708),                        # ∄
        build1('Nfr', 120081),                          # 𝔑
        build1('nfr', 120107),                          # 𝔫
        build2('ngE', '≧̸'),                             # ≧̸
        build1('nge', 8817),                            # ≱
        build1('ngeq', 8817),                           # ≱
        build2('ngeqq', '≧̸'),                           # ≧̸
        build2('ngeqslant', '⩾̸'),                       # ⩾̸
        build2('nges', '⩾̸'),                            # ⩾̸
        build2('nGg', '⋙̸'),                             # ⋙̸
        build1('ngsim', 8821),                          # ≵
        build2('nGt', '≫⃒'),                             # ≫⃒
        build1('ngt', 8815),                            # ≯
        build1('ngtr', 8815),                           # ≯
        build2('nGtv', '≫̸'),                            # ≫̸
        build1('nhArr', 8654),                          # ⇎
        build1('nharr', 8622),                          # ↮
        build1('nhpar', 10994),                         # ⫲
        build1('ni', 8715),                             # ∋
        build1('nis', 8956),                            # ⋼
        build1('nisd', 8954),                           # ⋺
        build1('niv', 8715),                            # ∋
        build1('NJcy', 1034),                           # Њ
        build1('njcy', 1114),                           # њ
        build1('nlArr', 8653),                          # ⇍
        build1('nlarr', 8602),                          # ↚
        build1('nldr', 8229),                           # ‥
        build2('nlE', '≦̸'),                             # ≦̸
        build1('nle', 8816),                            # ≰
        build1('nLeftarrow', 8653),                     # ⇍
        build1('nleftarrow', 8602),                     # ↚
        build1('nLeftrightarrow', 8654),                # ⇎
        build1('nleftrightarrow', 8622),                # ↮
        build1('nleq', 8816),                           # ≰
        build2('nleqq', '≦̸'),                           # ≦̸
        build2('nleqslant', '⩽̸'),                       # ⩽̸
        build2('nles', '⩽̸'),                            # ⩽̸
        build1('nless', 8814),                          # ≮
        build2('nLl', '⋘̸'),                             # ⋘̸
        build1('nlsim', 8820),                          # ≴
        build2('nLt', '≪⃒'),                             # ≪⃒
        build1('nlt', 8814),                            # ≮
        build1('nltri', 8938),                          # ⋪
        build1('nltrie', 8940),                         # ⋬
        build2('nLtv', '≪̸'),                            # ≪̸
        build1('nmid', 8740),                           # ∤
        build1('NoBreak', 8288),                        # ⁠
        build1('NonBreakingSpace', 160),                #  
        build1('Nopf', 8469),                           # ℕ
        build1('nopf', 120159),                         # 𝕟
        build1('Not', 10988),                           # ⫬
        build1('NotCongruent', 8802),                   # ≢
        build1('NotCupCap', 8813),                      # ≭
        build1('NotDoubleVerticalBar', 8742),           # ∦
        build1('NotElement', 8713),                     # ∉
        build1('NotEqual', 8800),                       # ≠
        build2('NotEqualTilde', '≂̸'),                   # ≂̸
        build1('NotExists', 8708),                      # ∄
        build1('NotGreater', 8815),                     # ≯
        build1('NotGreaterEqual', 8817),                # ≱
        build2('NotGreaterFullEqual', '≧̸'),             # ≧̸
        build2('NotGreaterGreater', '≫̸'),               # ≫̸
        build1('NotGreaterLess', 8825),                 # ≹
        build2('NotGreaterSlantEqual', '⩾̸'),            # ⩾̸
        build1('NotGreaterTilde', 8821),                # ≵
        build2('NotHumpDownHump', '≎̸'),                 # ≎̸
        build2('NotHumpEqual', '≏̸'),                    # ≏̸
        build1('notin', 8713),                          # ∉
        build2('notindot', '⋵̸'),                        # ⋵̸
        build2('notinE', '⋹̸'),                          # ⋹̸
        build1('notinva', 8713),                        # ∉
        build1('notinvb', 8951),                        # ⋷
        build1('notinvc', 8950),                        # ⋶
        build1('NotLeftTriangle', 8938),                # ⋪
        build2('NotLeftTriangleBar', '⧏̸'),              # ⧏̸
        build1('NotLeftTriangleEqual', 8940),           # ⋬
        build1('NotLess', 8814),                        # ≮
        build1('NotLessEqual', 8816),                   # ≰
        build1('NotLessGreater', 8824),                 # ≸
        build2('NotLessLess', '≪̸'),                     # ≪̸
        build2('NotLessSlantEqual', '⩽̸'),               # ⩽̸
        build1('NotLessTilde', 8820),                   # ≴
        build2('NotNestedGreaterGreater', '⪢̸'),         # ⪢̸
        build2('NotNestedLessLess', '⪡̸'),               # ⪡̸
        build1('notni', 8716),                          # ∌
        build1('notniva', 8716),                        # ∌
        build1('notnivb', 8958),                        # ⋾
        build1('notnivc', 8957),                        # ⋽
        build1('NotPrecedes', 8832),                    # ⊀
        build2('NotPrecedesEqual', '⪯̸'),                # ⪯̸
        build1('NotPrecedesSlantEqual', 8928),          # ⋠
        build1('NotReverseElement', 8716),              # ∌
        build1('NotRightTriangle', 8939),               # ⋫
        build2('NotRightTriangleBar', '⧐̸'),             # ⧐̸
        build1('NotRightTriangleEqual', 8941),          # ⋭
        build2('NotSquareSubset', '⊏̸'),                 # ⊏̸
        build1('NotSquareSubsetEqual', 8930),           # ⋢
        build2('NotSquareSuperset', '⊐̸'),               # ⊐̸
        build1('NotSquareSupersetEqual', 8931),         # ⋣
        build2('NotSubset', '⊂⃒'),                       # ⊂⃒
        build1('NotSubsetEqual', 8840),                 # ⊈
        build1('NotSucceeds', 8833),                    # ⊁
        build2('NotSucceedsEqual', '⪰̸'),                # ⪰̸
        build1('NotSucceedsSlantEqual', 8929),          # ⋡
        build2('NotSucceedsTilde', '≿̸'),                # ≿̸
        build2('NotSuperset', '⊃⃒'),                     # ⊃⃒
        build1('NotSupersetEqual', 8841),               # ⊉
        build1('NotTilde', 8769),                       # ≁
        build1('NotTildeEqual', 8772),                  # ≄
        build1('NotTildeFullEqual', 8775),              # ≇
        build1('NotTildeTilde', 8777),                  # ≉
        build1('NotVerticalBar', 8740),                 # ∤
        build1('npar', 8742),                           # ∦
        build1('nparallel', 8742),                      # ∦
        build2('nparsl', '⫽⃥'),                          # ⫽⃥
        build2('npart', '∂̸'),                           # ∂̸
        build1('npolint', 10772),                       # ⨔
        build1('npr', 8832),                            # ⊀
        build1('nprcue', 8928),                         # ⋠
        build2('npre', '⪯̸'),                            # ⪯̸
        build1('nprec', 8832),                          # ⊀
        build2('npreceq', '⪯̸'),                         # ⪯̸
        build1('nrArr', 8655),                          # ⇏
        build1('nrarr', 8603),                          # ↛
        build2('nrarrc', '⤳̸'),                          # ⤳̸
        build2('nrarrw', '↝̸'),                          # ↝̸
        build1('nRightarrow', 8655),                    # ⇏
        build1('nrightarrow', 8603),                    # ↛
        build1('nrtri', 8939),                          # ⋫
        build1('nrtrie', 8941),                         # ⋭
        build1('nsc', 8833),                            # ⊁
        build1('nsccue', 8929),                         # ⋡
        build2('nsce', '⪰̸'),                            # ⪰̸
        build1('Nscr', 119977),                         # 𝒩
        build1('nscr', 120003),                         # 𝓃
        build1('nshortmid', 8740),                      # ∤
        build1('nshortparallel', 8742),                 # ∦
        build1('nsim', 8769),                           # ≁
        build1('nsime', 8772),                          # ≄
        build1('nsimeq', 8772),                         # ≄
        build1('nsmid', 8740),                          # ∤
        build1('nspar', 8742),                          # ∦
        build1('nsqsube', 8930),                        # ⋢
        build1('nsqsupe', 8931),                        # ⋣
        build1('nsub', 8836),                           # ⊄
        build2('nsubE', '⫅̸'),                           # ⫅̸
        build1('nsube', 8840),                          # ⊈
        build2('nsubset', '⊂⃒'),                         # ⊂⃒
        build1('nsubseteq', 8840),                      # ⊈
        build2('nsubseteqq', '⫅̸'),                      # ⫅̸
        build1('nsucc', 8833),                          # ⊁
        build2('nsucceq', '⪰̸'),                         # ⪰̸
        build1('nsup', 8837),                           # ⊅
        build2('nsupE', '⫆̸'),                           # ⫆̸
        build1('nsupe', 8841),                          # ⊉
        build2('nsupset', '⊃⃒'),                         # ⊃⃒
        build1('nsupseteq', 8841),                      # ⊉
        build2('nsupseteqq', '⫆̸'),                      # ⫆̸
        build1('ntgl', 8825),                           # ≹
        build1('ntlg', 8824),                           # ≸
        build1('ntriangleleft', 8938),                  # ⋪
        build1('ntrianglelefteq', 8940),                # ⋬
        build1('ntriangleright', 8939),                 # ⋫
        build1('ntrianglerighteq', 8941),               # ⋭
        build1('num', 35),                              # #
        build1('numero', 8470),                         # №
        build1('numsp', 8199),                          #  
        build2('nvap', '≍⃒'),                            # ≍⃒
        build1('nVDash', 8879),                         # ⊯
        build1('nVdash', 8878),                         # ⊮
        build1('nvDash', 8877),                         # ⊭
        build1('nvdash', 8876),                         # ⊬
        build2('nvge', '≥⃒'),                            # ≥⃒
        build2('nvgt', '>⃒'),                            # >⃒
        build1('nvHarr', 10500),                        # ⤄
        build1('nvinfin', 10718),                       # ⧞
        build1('nvlArr', 10498),                        # ⤂
        build2('nvle', '≤⃒'),                            # ≤⃒
        build2('nvlt', '<⃒'),                            # <⃒
        build2('nvltrie', '⊴⃒'),                         # ⊴⃒
        build1('nvrArr', 10499),                            # ⤃
        build2('nvrtrie', '⊵⃒'),                         # ⊵⃒
        build2('nvsim', '∼⃒'),                           # ∼⃒
        build1('nwarhk', 10531),                        # ⤣
        build1('nwArr', 8662),                          # ⇖
        build1('nwarr', 8598),                          # ↖
        build1('nwarrow', 8598),                        # ↖
        build1('nwnear', 10535),                        # ⤧
        build1('oast', 8859),                           # ⊛
        build1('ocir', 8858),                           # ⊚
        build1('Ocy', 1054),                            # О
        build1('ocy', 1086),                            # о
        build1('odash', 8861),                          # ⊝
        build1('Odblac', 336),                          # Ő
        build1('odblac', 337),                          # ő
        build1('odiv', 10808),                          # ⨸
        build1('odot', 8857),                           # ⊙
        build1('odsold', 10684),                        # ⦼
        build1('ofcir', 10687),                         # ⦿
        build1('Ofr', 120082),                          # 𝔒
        build1('ofr', 120108),                          # 𝔬
        build1('ogon', 731),                            # ˛
        build1('ogt', 10689),                           # ⧁
        build1('ohbar', 10677),                         # ⦵
        build1('oint', 8750),                           # ∮
        build1('olarr', 8634),                          # ↺
        build1('olcir', 10686),                         # ⦾
        build1('olcross', 10683),                       # ⦻
        build1('olt', 10688),                           # ⧀
        build1('Omacr', 332),                           # Ō
        build1('omacr', 333),                           # ō
        build1('omid', 10678),                          # ⦶
        build1('ominus', 8854),                         # ⊖
        build1('Oopf', 120134),                         # 𝕆
        build1('oopf', 120160),                         # 𝕠
        build1('opar', 10679),                          # ⦷
        build1('OpenCurlyDoubleQuote', 8220),           # “
        build1('OpenCurlyQuote', 8216),                 # ‘
        build1('operp', 10681),                         # ⦹
        build1('oplus', 8853),                          # ⊕
        build1('Or', 10836),                            # ⩔
        build1('or', 8744),                             # ∨
        build1('orarr', 8635),                          # ↻
        build1('ord', 10845),                           # ⩝
        build1('order', 8500),                          # ℴ
        build1('orderof', 8500),                        # ℴ
        build1('origof', 8886),                         # ⊶
        build1('oror', 10838),                          # ⩖
        build1('orslope', 10839),                       # ⩗
        build1('orv', 10843),                           # ⩛
        build1('oS', 9416),                             # Ⓢ
        build1('Oscr', 119978),                         # 𝒪
        build1('oscr', 8500),                           # ℴ
        build1('osol', 8856),                           # ⊘
        build1('Otimes', 10807),                        # ⨷
        build1('otimes', 8855),                         # ⊗
        build1('otimesas', 10806),                      # ⨶
        build1('ovbar', 9021),                          # ⌽
        build1('OverBar', 8254),                        # ‾
        build1('OverBrace', 9182),                      # ⏞
        build1('OverBracket', 9140),                    # ⎴
        build1('OverParenthesis', 9180),                # ⏜
        build1('par', 8741),                            # ∥
        build1('parallel', 8741),                       # ∥
        build1('parsim', 10995),                        # ⫳
        build1('parsl', 11005),                         # ⫽
        build1('part', 8706),                           # ∂
        build1('PartialD', 8706),                       # ∂
        build1('Pcy', 1055),                            # П
        build1('pcy', 1087),                            # п
        build1('percnt', 37),                           # %
        build1('period', 46),                           # .
        build1('perp', 8869),                           # ⊥
        build1('pertenk', 8241),                        # ‱
        build1('Pfr', 120083),                          # 𝔓
        build1('pfr', 120109),                          # 𝔭
        build1('phmmat', 8499),                         # ℳ
        build1('phone', 9742),                          # ☎
        build1('pitchfork', 8916),                      # ⋔
        build1('piv', 982),                             # ϖ
        build1('planck', 8463),                         # ℏ
        build1('planckh', 8462),                        # ℎ
        build1('plankv', 8463),                         # ℏ
        build1('plus', 43),                             # +
        build1('plusacir', 10787),                      # ⨣
        build1('plusb', 8862),                          # ⊞
        build1('pluscir', 10786),                       # ⨢
        build1('plusdo', 8724),                         # ∔
        build1('plusdu', 10789),                        # ⨥
        build1('pluse', 10866),                         # ⩲
        build1('PlusMinus', 177),                       # ±
        build1('plussim', 10790),                       # ⨦
        build1('plustwo', 10791),                       # ⨧
        build1('pm', 177),                              # ±
        build1('Poincareplane', 8460),                  # ℌ
        build1('pointint', 10773),                      # ⨕
        build1('Popf', 8473),                           # ℙ
        build1('popf', 120161),                         # 𝕡
        build1('Pr', 10939),                            # ⪻
        build1('pr', 8826),                             # ≺
        build1('prap', 10935),                          # ⪷
        build1('prcue', 8828),                          # ≼
        build1('prE', 10931),                           # ⪳
        build1('pre', 10927),                           # ⪯
        build1('prec', 8826),                           # ≺
        build1('precapprox', 10935),                    # ⪷
        build1('preccurlyeq', 8828),                    # ≼
        build1('Precedes', 8826),                       # ≺
        build1('PrecedesEqual', 10927),                 # ⪯
        build1('PrecedesSlantEqual', 8828),             # ≼
        build1('PrecedesTilde', 8830),                  # ≾
        build1('preceq', 10927),                        # ⪯
        build1('precnapprox', 10937),                   # ⪹
        build1('precneqq', 10933),                      # ⪵
        build1('precnsim', 8936),                       # ⋨
        build1('precsim', 8830),                        # ≾
        build1('primes', 8473),                         # ℙ
        build1('prnap', 10937),                         # ⪹
        build1('prnE', 10933),                          # ⪵
        build1('prnsim', 8936),                         # ⋨
        build1('prod', 8719),                           # ∏
        build1('Product', 8719),                        # ∏
        build1('profalar', 9006),                       # ⌮
        build1('profline', 8978),                       # ⌒
        build1('profsurf', 8979),                       # ⌓
        build1('prop', 8733),                           # ∝
        build1('Proportion', 8759),                     # ∷
        build1('Proportional', 8733),                   # ∝
        build1('propto', 8733),                         # ∝
        build1('prsim', 8830),                          # ≾
        build1('prurel', 8880),                         # ⊰
        build1('Pscr', 119979),                         # 𝒫
        build1('pscr', 120005),                         # 𝓅
        build1('puncsp', 8200),                         #  
        build1('Qfr', 120084),                          # 𝔔
        build1('qfr', 120110),                          # 𝔮
        build1('qint', 10764),                          # ⨌
        build1('Qopf', 8474),                           # ℚ
        build1('qopf', 120162),                         # 𝕢
        build1('qprime', 8279),                         # ⁗
        build1('Qscr', 119980),                         # 𝒬
        build1('qscr', 120006),                         # 𝓆
        build1('quaternions', 8461),                    # ℍ
        build1('quatint', 10774),                       # ⨖
        build1('quest', 63),                            # ?
        build1('questeq', 8799),                        # ≟
        build1('rAarr', 8667),                          # ⇛
        build2('race', '∽̱'),                            # ∽̱
        build1('Racute', 340),                          # Ŕ
        build1('racute', 341),                          # ŕ
        build1('radic', 8730),                          # √
        build1('raemptyv', 10675),                      # ⦳
        build1('Rang', 10219),                          # ⟫
        build1('rangd', 10642),                         # ⦒
        build1('range', 10661),                         # ⦥
        build1('rangle', 10217),                        # ⟩
        build1('Rarr', 8608),                           # ↠
        build1('rArr', 8658),                           # ⇒
        build1('rarr', 8594),                           # →
        build1('rarrap', 10613),                        # ⥵
        build1('rarrb', 8677),                          # ⇥
        build1('rarrbfs', 10528),                       # ⤠
        build1('rarrc', 10547),                         # ⤳
        build1('rarrfs', 10526),                        # ⤞
        build1('rarrhk', 8618),                         # ↪
        build1('rarrlp', 8620),                         # ↬
        build1('rarrpl', 10565),                        # ⥅
        build1('rarrsim', 10612),                       # ⥴
        build1('Rarrtl', 10518),                        # ⤖
        build1('rarrtl', 8611),                         # ↣
        build1('rarrw', 8605),                          # ↝
        build1('rAtail', 10524),                        # ⤜
        build1('ratail', 10522),                        # ⤚
        build1('ratio', 8758),                          # ∶
        build1('rationals', 8474),                      # ℚ
        build1('RBarr', 10512),                         # ⤐
        build1('rBarr', 10511),                         # ⤏
        build1('rbarr', 10509),                         # ⤍
        build1('rbbrk', 10099),                         # ❳
        build1('rbrace', 125),                          # }
        build1('rbrack', 93),                           # ]
        build1('rbrke', 10636),                         # ⦌
        build1('rbrksld', 10638),                       # ⦎
        build1('rbrkslu', 10640),                       # ⦐
        build1('Rcaron', 344),                          # Ř
        build1('rcaron', 345),                          # ř
        build1('Rcedil', 342),                          # Ŗ
        build1('rcedil', 343),                          # ŗ
        build1('rceil', 8969),                          # ⌉
        build1('rcub', 125),                            # }
        build1('Rcy', 1056),                            # Р
        build1('rcy', 1088),                            # р
        build1('rdca', 10551),                          # ⤷
        build1('rdldhar', 10601),                       # ⥩
        build1('rdquor', 8221),                         # ”
        build1('rdsh', 8627),                           # ↳
        build1('Re', 8476),                             # ℜ
        build1('realine', 8475),                        # ℛ
        build1('realpart', 8476),                       # ℜ
        build1('reals', 8477),                          # ℝ
        build1('rect', 9645),                           # ▭
        build1('REG', 174),                             # ®
        build1('REG', 174),                             # ®
        build1('ReverseElement', 8715),                 # ∋
        build1('ReverseEquilibrium', 8651),             # ⇋
        build1('ReverseUpEquilibrium', 10607),          # ⥯
        build1('rfisht', 10621),                        # ⥽
        build1('rfloor', 8971),                         # ⌋
        build1('Rfr', 8476),                            # ℜ
        build1('rfr', 120111),                          # 𝔯
        build1('rHar', 10596),                          # ⥤
        build1('rhard', 8641),                          # ⇁
        build1('rharu', 8640),                          # ⇀
        build1('rharul', 10604),                        # ⥬
        build1('rhov', 1009),                           # ϱ
        build1('RightAngleBracket', 10217),             # ⟩
        build1('RightArrow', 8594),                     # →
        build1('Rightarrow', 8658),                     # ⇒
        build1('rightarrow', 8594),                     # →
        build1('RightArrowBar', 8677),                  # ⇥
        build1('RightArrowLeftArrow', 8644),            # ⇄
        build1('rightarrowtail', 8611),                 # ↣
        build1('RightCeiling', 8969),                   # ⌉
        build1('RightDoubleBracket', 10215),            # ⟧
        build1('RightDownTeeVector', 10589),            # ⥝
        build1('RightDownVector', 8642),                # ⇂
        build1('RightDownVectorBar', 10581),            # ⥕
        build1('RightFloor', 8971),                     # ⌋
        build1('rightharpoondown', 8641),               # ⇁
        build1('rightharpoonup', 8640),                 # ⇀
        build1('rightleftarrows', 8644),                # ⇄
        build1('rightleftharpoons', 8652),              # ⇌
        build1('rightrightarrows', 8649),               # ⇉
        build1('rightsquigarrow', 8605),                # ↝
        build1('RightTee', 8866),                       # ⊢
        build1('RightTeeArrow', 8614),                  # ↦
        build1('RightTeeVector', 10587),                # ⥛
        build1('rightthreetimes', 8908),                # ⋌
        build1('RightTriangle', 8883),                  # ⊳
        build1('RightTriangleBar', 10704),              # ⧐
        build1('RightTriangleEqual', 8885),             # ⊵
        build1('RightUpDownVector', 10575),             # ⥏
        build1('RightUpTeeVector', 10588),              # ⥜
        build1('RightUpVector', 8638),                  # ↾
        build1('RightUpVectorBar', 10580),              # ⥔
        build1('RightVector', 8640),                    # ⇀
        build1('RightVectorBar', 10579),                # ⥓
        build1('ring', 730),                            # ˚
        build1('risingdotseq', 8787),                   # ≓
        build1('rlarr', 8644),                          # ⇄
        build1('rlhar', 8652),                          # ⇌
        build1('rmoust', 9137),                         # ⎱
        build1('rmoustache', 9137),                     # ⎱
        build1('rnmid', 10990),                         # ⫮
        build1('roang', 10221),                         # ⟭
        build1('roarr', 8702),                          # ⇾
        build1('robrk', 10215),                         # ⟧
        build1('ropar', 10630),                         # ⦆
        build1('Ropf', 8477),                           # ℝ
        build1('ropf', 120163),                         # 𝕣
        build1('roplus', 10798),                        # ⨮
        build1('rotimes', 10805),                       # ⨵
        build1('RoundImplies', 10608),                  # ⥰
        build1('rpar', 41),                             # )
        build1('rpargt', 10644),                        # ⦔
        build1('rppolint', 10770),                      # ⨒
        build1('rrarr', 8649),                          # ⇉
        build1('Rrightarrow', 8667),                    # ⇛
        build1('Rscr', 8475),                           # ℛ
        build1('rscr', 120007),                         # 𝓇
        build1('Rsh', 8625),                            # ↱
        build1('rsh', 8625),                            # ↱
        build1('rsqb', 93),                             # ]
        build1('rthree', 8908),                         # ⋌
        build1('rtimes', 8906),                         # ⋊
        build1('rtri', 9657),                           # ▹
        build1('rtrie', 8885),                          # ⊵
        build1('rtrif', 9656),                          # ▸
        build1('rtriltri', 10702),                      # ⧎
        build1('RuleDelayed', 10740),                   # ⧴
        build1('ruluhar', 10600),                       # ⥨
        build1('rx', 8478),                             # ℞
        build1('Sacute', 346),                          # Ś
        build1('sacute', 347),                          # ś
        build1('Sc', 10940),                            # ⪼
        build1('sc', 8827),                             # ≻
        build1('scap', 10936),                          # ⪸
        build1('sccue', 8829),                          # ≽
        build1('scE', 10932),                           # ⪴
        build1('sce', 10928),                           # ⪰
        build1('Scedil', 350),                          # Ş
        build1('scedil', 351),                          # ş
        build1('Scirc', 348),                           # Ŝ
        build1('scirc', 349),                           # ŝ
        build1('scnap', 10938),                         # ⪺
        build1('scnE', 10934),                          # ⪶
        build1('scnsim', 8937),                         # ⋩
        build1('scpolint', 10771),                      # ⨓
        build1('scsim', 8831),                          # ≿
        build1('Scy', 1057),                            # С
        build1('scy', 1089),                            # с
        build1('sdot', 8901),                           # ⋅
        build1('sdotb', 8865),                          # ⊡
        build1('sdote', 10854),                         # ⩦
        build1('searhk', 10533),                        # ⤥
        build1('seArr', 8664),                          # ⇘
        build1('searr', 8600),                          # ↘
        build1('searrow', 8600),                        # ↘
        build1('semi', 59),                             # ;
        build1('seswar', 10537),                        # ⤩
        build1('setminus', 8726),                       # ∖
        build1('setmn', 8726),                          # ∖
        build1('sext', 10038),                          # ✶
        build1('Sfr', 120086),                          # 𝔖
        build1('sfr', 120112),                          # 𝔰
        build1('sfrown', 8994),                         # ⌢
        build1('sharp', 9839),                          # ♯
        build1('SHCHcy', 1065),                         # Щ
        build1('shchcy', 1097),                         # щ
        build1('SHcy', 1064),                           # Ш
        build1('shcy', 1096),                           # ш
        build1('ShortDownArrow', 8595),                 # ↓
        build1('ShortLeftArrow', 8592),                 # ←
        build1('shortmid', 8739),                       # ∣
        build1('shortparallel', 8741),                  # ∥
        build1('ShortRightArrow', 8594),                # →
        build1('ShortUpArrow', 8593),                   # ↑
        build1('sim', 8764),                            # ∼
        build1('simdot', 10858),                        # ⩪
        build1('sime', 8771),                           # ≃
        build1('simeq', 8771),                          # ≃
        build1('simg', 10910),                          # ⪞
        build1('simgE', 10912),                         # ⪠
        build1('siml', 10909),                          # ⪝
        build1('simlE', 10911),                         # ⪟
        build1('simne', 8774),                          # ≆
        build1('simplus', 10788),                       # ⨤
        build1('simrarr', 10610),                       # ⥲
        build1('slarr', 8592),                          # ←
        build1('SmallCircle', 8728),                    # ∘
        build1('smallsetminus', 8726),                  # ∖
        build1('smashp', 10803),                        # ⨳
        build1('smeparsl', 10724),                      # ⧤
        build1('smid', 8739),                           # ∣
        build1('smile', 8995),                          # ⌣
        build1('smt', 10922),                           # ⪪
        build1('smte', 10924),                          # ⪬
        build2('smtes', '⪬︀'),                           # ⪬︀
        build1('SOFTcy', 1068),                         # Ь
        build1('softcy', 1100),                         # ь
        build1('sol', 47),                              # /
        build1('solb', 10692),                          # ⧄
        build1('solbar', 9023),                         # ⌿
        build1('Sopf', 120138),                         # 𝕊
        build1('sopf', 120164),                         # 𝕤
        build1('spadesuit', 9824),                      # ♠
        build1('spar', 8741),                           # ∥
        build1('sqcap', 8851),                          # ⊓
        build2('sqcaps', '⊓︀'),                          # ⊓︀
        build1('sqcup', 8852),                          # ⊔
        build2('sqcups', '⊔︀'),                          # ⊔︀
        build1('Sqrt', 8730),                           # √
        build1('sqsub', 8847),                          # ⊏
        build1('sqsube', 8849),                         # ⊑
        build1('sqsubset', 8847),                       # ⊏
        build1('sqsubseteq', 8849),                     # ⊑
        build1('sqsup', 8848),                          # ⊐
        build1('sqsupe', 8850),                         # ⊒
        build1('sqsupset', 8848),                       # ⊐
        build1('sqsupseteq', 8850),                     # ⊒
        build1('squ', 9633),                            # □
        build1('Square', 9633),                         # □
        build1('square', 9633),                         # □
        build1('SquareIntersection', 8851),             # ⊓
        build1('SquareSubset', 8847),                   # ⊏
        build1('SquareSubsetEqual', 8849),              # ⊑
        build1('SquareSuperset', 8848),                 # ⊐
        build1('SquareSupersetEqual', 8850),            # ⊒
        build1('SquareUnion', 8852),                    # ⊔
        build1('squarf', 9642),                         # ▪
        build1('squf', 9642),                           # ▪
        build1('srarr', 8594),                          # →
        build1('Sscr', 119982),                         # 𝒮
        build1('sscr', 120008),                         # 𝓈
        build1('ssetmn', 8726),                         # ∖
        build1('ssmile', 8995),                         # ⌣
        build1('sstarf', 8902),                         # ⋆
        build1('Star', 8902),                           # ⋆
        build1('star', 9734),                           # ☆
        build1('starf', 9733),                          # ★
        build1('straightepsilon', 1013),                # ϵ
        build1('straightphi', 981),                     # ϕ
        build1('strns', 175),                           # ¯
        build1('Sub', 8912),                            # ⋐
        build1('sub', 8834),                            # ⊂
        build1('subdot', 10941),                        # ⪽
        build1('subE', 10949),                          # ⫅
        build1('sube', 8838),                           # ⊆
        build1('subedot', 10947),                       # ⫃
        build1('submult', 10945),                       # ⫁
        build1('subnE', 10955),                         # ⫋
        build1('subne', 8842),                          # ⊊
        build1('subplus', 10943),                       # ⪿
        build1('subrarr', 10617),                       # ⥹
        build1('Subset', 8912),                         # ⋐
        build1('subset', 8834),                         # ⊂
        build1('subseteq', 8838),                       # ⊆
        build1('subseteqq', 10949),                     # ⫅
        build1('SubsetEqual', 8838),                    # ⊆
        build1('subsetneq', 8842),                      # ⊊
        build1('subsetneqq', 10955),                    # ⫋
        build1('subsim', 10951),                        # ⫇
        build1('subsub', 10965),                        # ⫕
        build1('subsup', 10963),                        # ⫓
        build1('succ', 8827),                           # ≻
        build1('succapprox', 10936),                    # ⪸
        build1('succcurlyeq', 8829),                    # ≽
        build1('Succeeds', 8827),                       # ≻
        build1('SucceedsEqual', 10928),                 # ⪰
        build1('SucceedsSlantEqual', 8829),             # ≽
        build1('SucceedsTilde', 8831),                  # ≿
        build1('succeq', 10928),                        # ⪰
        build1('succnapprox', 10938),                   # ⪺
        build1('succneqq', 10934),                      # ⪶
        build1('succnsim', 8937),                       # ⋩
        build1('succsim', 8831),                        # ≿
        build1('SuchThat', 8715),                       # ∋
        build1('Sum', 8721),                            # ∑
        build1('sum', 8721),                            # ∑
        build1('sung', 9834),                           # ♪
        build1('Sup', 8913),                            # ⋑
        build1('sup', 8835),                            # ⊃
        build1('supdot', 10942),                        # ⪾
        build1('supdsub', 10968),                       # ⫘
        build1('supE', 10950),                          # ⫆
        build1('supe', 8839),                           # ⊇
        build1('supedot', 10948),                       # ⫄
        build1('Superset', 8835),                       # ⊃
        build1('SupersetEqual', 8839),                  # ⊇
        build1('suphsol', 10185),                       # ⟉
        build1('suphsub', 10967),                       # ⫗
        build1('suplarr', 10619),                       # ⥻
        build1('supmult', 10946),                       # ⫂
        build1('supnE', 10956),                         # ⫌
        build1('supne', 8843),                          # ⊋
        build1('supplus', 10944),                       # ⫀
        build1('Supset', 8913),                         # ⋑
        build1('supset', 8835),                         # ⊃
        build1('supseteq', 8839),                       # ⊇
        build1('supseteqq', 10950),                     # ⫆
        build1('supsetneq', 8843),                      # ⊋
        build1('supsetneqq', 10956),                    # ⫌
        build1('supsim', 10952),                        # ⫈
        build1('supsub', 10964),                        # ⫔
        build1('supsup', 10966),                        # ⫖
        build1('swarhk', 10534),                        # ⤦
        build1('swArr', 8665),                          # ⇙
        build1('swarr', 8601),                          # ↙
        build1('swarrow', 8601),                        # ↙
        build1('swnwar', 10538),                        # ⤪
        build1('Tab', 9),                               # 	
        build1('target', 8982),                         # ⌖
        build1('tbrk', 9140),                           # ⎴
        build1('Tcaron', 356),                          # Ť
        build1('tcaron', 357),                          # ť
        build1('Tcedil', 354),                          # Ţ
        build1('tcedil', 355),                          # ţ
        build1('Tcy', 1058),                            # Т
        build1('tcy', 1090),                            # т
        build1('tdot', 8411),                           #⃛ 
        build1('telrec', 8981),                         # ⌕
        build1('Tfr', 120087),                          # 𝔗
        build1('tfr', 120113),                          # 𝔱
        build1('there4', 8756),                         # ∴
        build1('Therefore', 8756),                      # ∴
        build1('therefore', 8756),                      # ∴
        build1('thetasym', 977),                        # ϑ
        build1('thickapprox', 8776),                    # ≈
        build1('thicksim', 8764),                       # ∼
        build2('ThickSpace', '  '),                     #   
        build1('ThinSpace', 8201),                      #  
        build1('thkap', 8776),                          # ≈
        build1('thksim', 8764),                         # ∼
        build1('Tilde', 8764),                          # ∼
        build1('TildeEqual', 8771),                     # ≃
        build1('TildeFullEqual', 8773),                 # ≅
        build1('TildeTilde', 8776),                     # ≈
        build1('timesb', 8864),                         # ⊠
        build1('timesbar', 10801),                      # ⨱
        build1('timesd', 10800),                        # ⨰
        build1('tint', 8749),                           # ∭
        build1('toea', 10536),                          # ⤨
        build1('top', 8868),                            # ⊤
        build1('topbot', 9014),                         # ⌶
        build1('topcir', 10993),                        # ⫱
        build1('Topf', 120139),                         # 𝕋
        build1('topf', 120165),                         # 𝕥
        build1('topfork', 10970),                       # ⫚
        build1('tosa', 10537),                          # ⤩
        build1('tprime', 8244),                         # ‴
        build1('TRADE', 8482),                          # ™
        build1('triangle', 9653),                       # ▵
        build1('triangledown', 9663),                   # ▿
        build1('triangleleft', 9667),                   # ◃
        build1('trianglelefteq', 8884),                 # ⊴
        build1('triangleq', 8796),                      # ≜
        build1('triangleright', 9657),                  # ▹
        build1('trianglerighteq', 8885),                # ⊵
        build1('tridot', 9708),                         # ◬
        build1('trie', 8796),                           # ≜
        build1('triminus', 10810),                      # ⨺
        build1('TripleDot', 8411),                      #⃛ 
        build1('triplus', 10809),                       # ⨹
        build1('trisb', 10701),                         # ⧍
        build1('tritime', 10811),                       # ⨻
        build1('trpezium', 9186),                       # ⏢
        build1('Tscr', 119983),                         # 𝒯
        build1('tscr', 120009),                         # 𝓉
        build1('TScy', 1062),                           # Ц
        build1('tscy', 1094),                           # ц
        build1('TSHcy', 1035),                          # Ћ
        build1('tshcy', 1115),                          # ћ
        build1('Tstrok', 358),                          # Ŧ
        build1('tstrok', 359),                          # ŧ
        build1('twixt', 8812),                          # ≬
        build1('twoheadleftarrow', 8606),               # ↞
        build1('twoheadrightarrow', 8608),              # ↠
        build1('Uarr', 8607),                           # ↟
        build1('uArr', 8657),                           # ⇑
        build1('uarr', 8593),                           # ↑
        build1('Uarrocir', 10569),                      # ⥉
        build1('Ubrcy', 1038),                          # Ў
        build1('ubrcy', 1118),                          # ў
        build1('Ubreve', 364),                          # Ŭ
        build1('ubreve', 365),                          # ŭ
        build1('Ucy', 1059),                            # У
        build1('ucy', 1091),                            # у
        build1('udarr', 8645),                          # ⇅
        build1('Udblac', 368),                          # Ű
        build1('udblac', 369),                          # ű
        build1('udhar', 10606),                         # ⥮
        build1('ufisht', 10622),                        # ⥾
        build1('Ufr', 120088),                          # 𝔘
        build1('ufr', 120114),                          # 𝔲
        build1('uHar', 10595),                          # ⥣
        build1('uharl', 8639),                          # ↿
        build1('uharr', 8638),                          # ↾
        build1('uhblk', 9600),                          # ▀
        build1('ulcorn', 8988),                         # ⌜
        build1('ulcorner', 8988),                       # ⌜
        build1('ulcrop', 8975),                         # ⌏
        build1('ultri', 9720),                          # ◸
        build1('Umacr', 362),                           # Ū
        build1('umacr', 363),                           # ū
        build1('UnderBar', 95),                         # _
        build1('UnderBrace', 9183),                     # ⏟
        build1('UnderBracket', 9141),                   # ⎵
        build1('UnderParenthesis', 9181),               # ⏝
        build1('Union', 8899),                          # ⋃
        build1('UnionPlus', 8846),                      # ⊎
        build1('Uogon', 370),                           # Ų
        build1('uogon', 371),                           # ų
        build1('Uopf', 120140),                         # 𝕌
        build1('uopf', 120166),                         # 𝕦
        build1('UpArrow', 8593),                        # ↑
        build1('Uparrow', 8657),                        # ⇑
        build1('uparrow', 8593),                        # ↑
        build1('UpArrowBar', 10514),                    # ⤒
        build1('UpArrowDownArrow', 8645),               # ⇅
        build1('UpDownArrow', 8597),                    # ↕
        build1('Updownarrow', 8661),                    # ⇕
        build1('updownarrow', 8597),                    # ↕
        build1('UpEquilibrium', 10606),                 # ⥮
        build1('upharpoonleft', 8639),                  # ↿
        build1('upharpoonright', 8638),                 # ↾
        build1('uplus', 8846),                          # ⊎
        build1('UpperLeftArrow', 8598),                 # ↖
        build1('UpperRightArrow', 8599),                # ↗
        build1('Upsi', 978),                            # ϒ
        build1('upsilon', 965),                         # υ
        build1('UpTee', 8869),                          # ⊥
        build1('UpTeeArrow', 8613),                     # ↥
        build1('upuparrows', 8648),                     # ⇈
        build1('urcorn', 8989),                         # ⌝
        build1('urcorner', 8989),                       # ⌝
        build1('urcrop', 8974),                         # ⌎
        build1('Uring', 366),                           # Ů
        build1('uring', 367),                           # ů
        build1('urtri', 9721),                          # ◹
        build1('Uscr', 119984),                         # 𝒰
        build1('uscr', 120010),                         # 𝓊
        build1('utdot', 8944),                          # ⋰
        build1('Utilde', 360),                          # Ũ
        build1('utilde', 361),                          # ũ
        build1('utri', 9653),                           # ▵
        build1('utrif', 9652),                          # ▴
        build1('uuarr', 8648),                          # ⇈
        build1('uwangle', 10663),                       # ⦧
        build1('vangrt', 10652),                        # ⦜
        build1('varepsilon', 1013),                     # ϵ
        build1('varkappa', 1008),                       # ϰ
        build1('varnothing', 8709),                     # ∅
        build1('varphi', 981),                          # ϕ
        build1('varpi', 982),                           # ϖ
        build1('varpropto', 8733),                      # ∝
        build1('vArr', 8661),                           # ⇕
        build1('varr', 8597),                           # ↕
        build1('varrho', 1009),                         # ϱ
        build1('varsigma', 962),                        # ς
        build2('varsubsetneq', '⊊︀'),                    # ⊊︀
        build2('varsubsetneqq', '⫋︀'),                   # ⫋︀
        build2('varsupsetneq', '⊋︀'),                    # ⊋︀
        build2('varsupsetneqq', '⫌︀'),                   # ⫌︀
        build1('vartheta', 977),                        # ϑ
        build1('vartriangleleft', 8882),                # ⊲
        build1('vartriangleright', 8883),               # ⊳
        build1('Vbar', 10987),                          # ⫫
        build1('vBar', 10984),                          # ⫨
        build1('vBarv', 10985),                         # ⫩
        build1('Vcy', 1042),                            # В
        build1('vcy', 1074),                            # в
        build1('VDash', 8875),                          # ⊫
        build1('Vdash', 8873),                          # ⊩
        build1('vDash', 8872),                          # ⊨
        build1('vdash', 8866),                          # ⊢
        build1('Vdashl', 10982),                        # ⫦
        build1('Vee', 8897),                            # ⋁
        build1('vee', 8744),                            # ∨
        build1('veebar', 8891),                         # ⊻
        build1('veeeq', 8794),                          # ≚
        build1('vellip', 8942),                         # ⋮
        build1('Verbar', 8214),                         # ‖
        build1('verbar', 124),                          # |
        build1('Vert', 8214),                           # ‖
        build1('vert', 124),                            # |
        build1('VerticalBar', 8739),                    # ∣
        build1('VerticalLine', 124),                    # |
        build1('VerticalSeparator', 10072),             # ❘
        build1('VerticalTilde', 8768),                  # ≀
        build1('VeryThinSpace', 8202),                  #  
        build1('Vfr', 120089),                          # 𝔙
        build1('vfr', 120115),                          # 𝔳
        build1('vltri', 8882),                          # ⊲
        build2('vnsub', '⊂⃒'),                           # ⊂⃒
        build2('vnsup', '⊃⃒'),                           # ⊃⃒
        build1('Vopf', 120141),                         # 𝕍
        build1('vopf', 120167),                         # 𝕧
        build1('vprop', 8733),                          # ∝
        build1('vrtri', 8883),                          # ⊳
        build1('Vscr', 119985),                         # 𝒱
        build1('vscr', 120011),                         # 𝓋
        build2('vsubnE', '⫋︀'),                          # ⫋︀
        build2('vsubne', '⊊︀'),                          # ⊊︀
        build2('vsupnE', '⫌︀'),                          # ⫌︀
        build2('vsupne', '⊋︀'),                          # ⊋︀
        build1('Vvdash', 8874),                         # ⊪
        build1('vzigzag', 10650),                       # ⦚
        build1('Wcirc', 372),                           # Ŵ
        build1('wcirc', 373),                           # ŵ
        build1('wedbar', 10847),                        # ⩟
        build1('Wedge', 8896),                          # ⋀
        build1('wedge', 8743),                          # ∧
        build1('wedgeq', 8793),                         # ≙
        build1('Wfr', 120090),                          # 𝔚
        build1('wfr', 120116),                          # 𝔴
        build1('Wopf', 120142),                         # 𝕎
        build1('wopf', 120168),                         # 𝕨
        build1('wp', 8472),                             # ℘
        build1('wr', 8768),                             # ≀
        build1('wreath', 8768),                         # ≀
        build1('Wscr', 119986),                         # 𝒲
        build1('wscr', 120012),                         # 𝓌
        build1('xcap', 8898),                           # ⋂
        build1('xcirc', 9711),                          # ◯
        build1('xcup', 8899),                           # ⋃
        build1('xdtri', 9661),                          # ▽
        build1('Xfr', 120091),                          # 𝔛
        build1('xfr', 120117),                          # 𝔵
        build1('xhArr', 10234),                         # ⟺
        build1('xharr', 10231),                         # ⟷
        build1('xlArr', 10232),                         # ⟸
        build1('xlarr', 10229),                         # ⟵
        build1('xmap', 10236),                          # ⟼
        build1('xnis', 8955),                           # ⋻
        build1('xodot', 10752),                         # ⨀
        build1('Xopf', 120143),                         # 𝕏
        build1('xopf', 120169),                         # 𝕩
        build1('xoplus', 10753),                        # ⨁
        build1('xotime', 10754),                        # ⨂
        build1('xrArr', 10233),                         # ⟹
        build1('xrarr', 10230),                         # ⟶
        build1('Xscr', 119987),                         # 𝒳
        build1('xscr', 120013),                         # 𝓍
        build1('xsqcup', 10758),                        # ⨆
        build1('xuplus', 10756),                        # ⨄
        build1('xutri', 9651),                          # △
        build1('xvee', 8897),                           # ⋁
        build1('xwedge', 8896),                         # ⋀
        build1('YAcy', 1071),                           # Я
        build1('yacy', 1103),                           # я
        build1('Ycirc', 374),                           # Ŷ
        build1('ycirc', 375),                           # ŷ
        build1('Ycy', 1067),                            # Ы
        build1('ycy', 1099),                            # ы
        build1('Yfr', 120092),                          # 𝔜
        build1('yfr', 120118),                          # 𝔶
        build1('YIcy', 1031),                           # Ї
        build1('yicy', 1111),                           # ї
        build1('Yopf', 120144),                         # 𝕐
        build1('yopf', 120170),                         # 𝕪
        build1('Yscr', 119988),                         # 𝒴
        build1('yscr', 120014),                         # 𝓎
        build1('YUcy', 1070),                           # Ю
        build1('yucy', 1102),                           # ю
        build1('Zacute', 377),                          # Ź
        build1('zacute', 378),                          # ź
        build1('Zcaron', 381),                          # Ž
        build1('zcaron', 382),                          # ž
        build1('Zcy', 1047),                            # З
        build1('zcy', 1079),                            # з
        build1('Zdot', 379),                            # Ż
        build1('zdot', 380),                            # ż
        build1('zeetrf', 8488),                         # ℨ
        build1('ZeroWidthSpace', 8203),                 # ​
        build1('Zfr', 8488),                            # ℨ
        build1('zfr', 120119),                          # 𝔷
        build1('ZHcy', 1046),                           # Ж
        build1('zhcy', 1078),                           # ж
        build1('zigrarr', 8669),                        # ⇝
        build1('Zopf', 8484),                           # ℤ
        build1('zopf', 120171),                         # 𝕫
        build1('Zscr', 119989),                         # 𝒵
        build1('zscr', 120015),                         # 𝓏
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
            print(f"build1('{k}', {c}),     # {v}")
        else:
            print(f"build2('{v}', '{k}'),   # {v}")
