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
    
    def build(name, codepoint):
        if isinstance(codepoint, int):
             return XmlHtmlEntity(chr(codepoint), name, '&'+name+';', '&#'+str(codepoint)+';', codepoint)
        else:
            return XmlHtmlEntity(codepoint, name, '&'+name+';', None, None)
    
    HtmlQuot = [ build('quot', 34), build('QUOT', 34) ]
    HtmlApos = [ build('apos', 39), build('APOS', 39) ]
    HtmlBase = [
        build('amp', 38),  # &
        build('AMP', 38),  # &
        build('lt', 60),   # <
        build('LT', 60),   # <
        build('gt', 62),   # >
        build('GT', 62),   # >
    ]
    
    Html2 = [
        build('Agrave', 192),  # À
        build('Aacute', 193),  # Á
        build('Acirc', 194),   # Â
        build('Atilde', 195),  # Ã
        build('Auml', 196),    # Ä
        build('Aring', 197),   # Å
        build('AElig', 198),   # Æ
        build('Ccedil', 199),  # Ç
        build('Egrave', 200),  # È
        build('Eacute', 201),  # É
        build('Ecirc', 202),   # Ê
        build('Euml', 203),    # Ë
        build('Igrave', 204),  # Ì
        build('Iacute', 205),  # Í
        build('Icirc', 206),   # Î
        build('Iuml', 207),    # Ï
        build('ETH', 208),     # Ð
        build('Ntilde', 209),  # Ñ
        build('Ograve', 210),  # Ò
        build('Oacute', 211),  # Ó
        build('Ocirc', 212),   # Ô
        build('Otilde', 213),  # Õ
        build('Ouml', 214),    # Ö
        build('Oslash', 216),  # Ø
        build('Ugrave', 217),  # Ù
        build('Uacute', 218),  # Ú
        build('Ucirc', 219),   # Û
        build('Uuml', 220),    # Ü
        build('Yacute', 221),  # Ý
        
        build('THORN', 222),   # Þ
        build('szlig', 223),   # ß
        
        build('agrave', 224),  # à
        build('aacute', 225),  # á
        build('acirc', 226),   # â
        build('atilde', 227),  # ã
        build('auml', 228),    # ä
        build('aring', 229),   # å
        build('aelig', 230),   # æ
        build('ccedil', 231),  # ç
        build('egrave', 232),  # è
        build('eacute', 233),  # é
        build('ecirc', 234),   # ê
        build('euml', 235),    # ë
        build('igrave', 236),  # ì
        build('iacute', 237),  # í
        build('icirc', 238),   # î
        build('iuml', 239),    # ï
        build('eth', 240),     # ð
        build('ntilde', 241),  # ñ
        build('ograve', 242),  # ò
        build('oacute', 243),  # ó
        build('ocirc', 244),   # ô
        build('otilde', 245),  # õ
        build('ouml', 246),    # ö
        build('oslash', 248),  # ø
        build('ugrave', 249),  # ù
        build('uacute', 250),  # ú
        build('ucirc', 251),   # û
        build('uuml', 252),    # ü
        build('yacute', 253),  # ý
        
        build('thorn', 254),   # þ
        build('yuml', 255),    # ÿ
    ]
    
    Html3 = [
        build('nbsp', 160),    #  
        build('iexcl', 161),   # ¡
        build('cent', 162),    # ¢
        build('pound', 163),   # £
        build('curren', 164),  # ¤
        build('yen', 165),     # ¥
        build('brvbar', 166),  # ¦
        build('sect', 167),    # §
        build('uml', 168),     # ¨
        build('copy', 169),    # ©
        build('ordf', 170),    # ª
        build('laquo', 171),   # «
        build('not', 172),     # ¬
        build('shy', 173),     # ­
        build('reg', 174),     # ®
        build('macr', 175),    # ¯
        build('deg', 176),     # °
        build('plusmn', 177),   # ±
        build('sup2', 178),    # ²
        build('sup3', 179),    # ³
        build('acute', 180),   # ´
        build('micro', 181),   # µ
        build('para', 182),    # ¶
        build('middot', 183),   # ·
        build('cedil', 184),   # ¸
        build('sup1', 185),    # ¹
        build('ordm', 186),    # º
        build('raquo', 187),   # »
        build('frac14', 188),  # ¼
        build('frac12', 189),  # ½
        build('frac34', 190),  # ¾
        build('iquest', 191),  # ¿
        
        build('times', 215),   # ×
        
        build('divide', 247),  # ÷
    ]
    
    Html4 = [
        build('OElig', 338),       # Œ
        build('oelig', 339),       # œ
        
        build('Scaron', 352),      # Š
        build('scaron', 353),      # š
        
        build('Yuml', 376),        # Ÿ
        
        build('fnof', 402),        # ƒ
        
        build('circ', 710),        # ˆ
        
        build('tilde', 732),       # ˜
        
        build('Alpha', 913 ),      # Α
        build('Beta', 914 ),       # Β
        build('Gamma', 915 ),      # Γ
        build('Delta', 916 ),      # Δ
        build('Epsilon', 917 ),    # Ε
        build('Zeta', 918 ),       # Ζ
        build('Eta', 919 ),        # Η
        build('Theta', 920 ),      # Θ
        build('Iota', 921 ),       # Ι
        build('Kappa', 922 ),      # Κ
        build('Lambda', 923 ),     # Λ
        build('Mu', 924 ),         # Μ
        build('Nu', 925 ),         # Ν
        build('Xi', 926 ),         # Ξ
        build('Omicron', 927 ),    # Ο
        build('Pi', 928 ),         # Π
        build('Rho', 929 ),        # Ρ
        
        build('Sigma', 931 ),      # Σ
        build('Tau', 932 ),        # Τ
        build('Upsilon', 933 ),    # Υ
        build('Phi', 934 ),        # Φ
        build('Chi', 935 ),        # Χ
        build('Psi', 936 ),        # Ψ
        build('Omega', 937 ),      # Ω
        build('ohm', 937 ),        # Ω
        
        build('alpha', 945 ),      # α
        build('beta', 946 ),       # β
        build('gamma', 947 ),      # γ
        build('delta', 948 ),      # δ
        build('epsi', 949 ),       # ε
        build('epsilon', 949 ),    # ε
        build('zeta', 950 ),       # ζ
        build('eta', 951 ),        # η
        build('theta', 952 ),      # θ
        build('iota', 953 ),       # ι
        build('kappa', 954 ),      # κ
        build('lambda', 955 ),     # λ
        build('mu', 956 ),         # μ
        build('nu', 957 ),         # ν
        build('xi', 958 ),         # ξ
        build('omicron', 959 ),    # ο
        build('pi', 960 ),         # π
        build('rho', 961 ),        # ρ
        build('sigmav', 962 ),     # ς
        build('sigmaf', 962 ),     # ς
        build('sigma', 963 ),      # σ
        build('tau', 964 ),        # τ
        build('upsi', 965 ),       # υ
        build('phi', 966 ),        # φ
        build('chi', 967 ),        # χ
        build('psi', 968 ),        # ψ
        build('omega', 969 ),      # ω
        
        build('thetav', 977 ),     # ϑ
        build('upsih', 978 ),      # ϒ
        
        build('phiv', 981 ),       # ϕ
        
        build('ensp', 8194),       #  
        build('emsp', 8195),       #  
        
        build('thinsp', 8201),     #  
        
        build('zwnj', 8204),       # ‌
        build('zwj', 8205),        # ‍
        build('lrm', 8206),        # ‎
        build('rlm', 8207),        # ‏
        
        build('ndash', 8211),      # –
        build('mdash', 8212),      # —
        
        build('lsquo', 8216),      # ‘
        build('rsquo', 8217),      # ’
        build('rsquor', 8217),     # ’
        build('sbquo', 8218),      # ‚
        build('ldquo', 8220),      # “
        build('rdquo', 8221 ),     # ”
        build('bdquo', 8222),      # „
        
        build('dagger', 8224),     # †
        build('ddagger', 8225),    # ‡
        build('bull', 8226),       # •
        
        build('hellip', 8230),     # …
        
        build('permil', 8240),     # ‰
        
        build('prime', 8242),      # ′
        build('Prime', 8243),      # ″
        
        build('lsaquo', 8249),     # ‹
        build('rsaquo', 8250),     # ›
        
        build('oline', 8254),      # ‾
        
        build('euro', 8364),       # €
        
        build('image', 8465),      # ℑ
        
        build('weierp', 8472),     # ℘
        
        build('real', 8476),       # ℜ
        
        build('trade', 8482),      # ™
        
        build('alefsym', 8501),    # ℵ
        
        build('rang', 10217),      # ⟩
        build('loz', 9674),        # ◊
        build('spades', 9824),     # ♠
        build('clubs', 9827),      # ♣
        build('hearts', 9829),     # ♥
        build('diams', 9830),      # ♦
        build('lang', 10216),      # ⟨
        build('rang', 10217),      # ⟩
    ]
    
    Html5 = [
        build('Abreve', 258),                          # Ă
        build('abreve', 259),                          # ă
        build('ac', 8766),                             # ∾
        build('acd', 8767),                            # ∿
        build('acE', '∾̳'),                             # ∾̳
        build('Acy', 1040),                            # А
        build('acy', 1072),                            # а
        build('af', 8289),                             # ⁡
        build('Afr', 120068),                          # 𝔄
        build('afr', 120094),                          # 𝔞
        build('aleph', 8501),                          # ℵ
        build('Amacr', 256),                           # Ā
        build('amacr', 257),                           # ā
        build('amalg', 10815),                         # ⨿
        build('And', 10835),                           # ⩓
        build('and', 8743),                            # ∧
        build('andand', 10837),                        # ⩕
        build('andd', 10844),                          # ⩜
        build('andslope', 10840),                      # ⩘
        build('andv', 10842),                          # ⩚
        build('ang', 8736),                            # ∠
        build('ange', 10660),                          # ⦤
        build('angle', 8736),                          # ∠
        build('angmsd', 8737),                         # ∡
        build('angmsdaa', 10664),                      # ⦨
        build('angmsdab', 10665),                      # ⦩
        build('angmsdac', 10666),                      # ⦪
        build('angmsdad', 10667),                      # ⦫
        build('angmsdae', 10668),                      # ⦬
        build('angmsdaf', 10669),                      # ⦭
        build('angmsdag', 10670),                      # ⦮
        build('angmsdah', 10671),                      # ⦯
        build('angrt', 8735),                          # ∟
        build('angrtvb', 8894),                        # ⊾
        build('angrtvbd', 10653),                      # ⦝
        build('angsph', 8738),                         # ∢
        build('angst', 197),                           # Å
        build('angzarr', 9084),                        # ⍼
        build('Aogon', 260),                           # Ą
        build('aogon', 261),                           # ą
        build('Aopf', 120120),                         # 𝔸
        build('aopf', 120146),                         # 𝕒
        build('ap', 8776),                             # ≈
        build('apacir', 10863),                        # ⩯
        build('apE', 10864),                           # ⩰
        build('ape', 8778),                            # ≊
        build('apid', 8779),                           # ≋
        build('apos', 39),                             # '
        build('ApplyFunction', 8289),                  # ⁡
        build('approx', 8776),                         # ≈
        build('approxeq', 8778),                       # ≊
        build('Ascr', 119964),                         # 𝒜
        build('ascr', 119990),                         # 𝒶
        build('Assign', 8788),                         # ≔
        build('ast', 42),                              # *
        build('asymp', 8776),                          # ≈
        build('asympeq', 8781),                        # ≍
        build('awconint', 8755),                       # ∳
        build('awint', 10769),                         # ⨑
        build('backcong', 8780),                       # ≌
        build('backepsilon', 1014),                    # ϶
        build('backprime', 8245),                      # ‵
        build('backsim', 8765),                        # ∽
        build('backsimeq', 8909),                      # ⋍
        build('Backslash', 8726),                      # ∖
        build('Barv', 10983),                          # ⫧
        build('barvee', 8893),                         # ⊽
        build('Barwed', 8966),                         # ⌆
        build('barwed', 8965),                         # ⌅
        build('barwedge', 8965),                       # ⌅
        build('bbrk', 9141),                           # ⎵
        build('bbrktbrk', 9142),                       # ⎶
        build('bcong', 8780),                          # ≌
        build('Bcy', 1041),                            # Б
        build('bcy', 1073),                            # б
        build('becaus', 8757),                         # ∵
        build('Because', 8757),                        # ∵
        build('because', 8757),                        # ∵
        build('bemptyv', 10672),                       # ⦰
        build('bepsi', 1014),                          # ϶
        build('bernou', 8492),                         # ℬ
        build('Bernoullis', 8492),                     # ℬ
        build('beth', 8502),                           # ℶ
        build('between', 8812),                        # ≬
        build('Bfr', 120069),                          # 𝔅
        build('bfr', 120095),                          # 𝔟
        build('bigcap', 8898),                         # ⋂
        build('bigcirc', 9711),                        # ◯
        build('bigcup', 8899),                         # ⋃
        build('bigodot', 10752),                       # ⨀
        build('bigoplus', 10753),                      # ⨁
        build('bigotimes', 10754),                     # ⨂
        build('bigsqcup', 10758),                      # ⨆
        build('bigstar', 9733),                        # ★
        build('bigtriangledown', 9661),                # ▽
        build('bigtriangleup', 9651),                  # △
        build('biguplus', 10756),                      # ⨄
        build('bigvee', 8897),                         # ⋁
        build('bigwedge', 8896),                       # ⋀
        build('bkarow', 10509),                        # ⤍
        build('blacklozenge', 10731),                  # ⧫
        build('blacksquare', 9642),                    # ▪
        build('blacktriangle', 9652),                  # ▴
        build('blacktriangledown', 9662),              # ▾
        build('blacktriangleleft', 9666),              # ◂
        build('blacktriangleright', 9656),             # ▸
        build('blank', 9251),                          # ␣
        build('blk12', 9618),                          # ▒
        build('blk14', 9617),                          # ░
        build('blk34', 9619),                          # ▓
        build('block', 9608),                          # █
        build('bne', '=⃥'),                             # =⃥
        build('bnequiv', '≡⃥'),                         # ≡⃥
        build('bNot', 10989),                          # ⫭
        build('bnot', 8976),                           # ⌐
        build('Bopf', 120121),                         # 𝔹
        build('bopf', 120147),                         # 𝕓
        build('bot', 8869),                            # ⊥
        build('bottom', 8869),                         # ⊥
        build('bowtie', 8904),                         # ⋈
        build('boxbox', 10697),                        # ⧉
        build('boxDL', 9559),                          # ╗
        build('boxDl', 9558),                          # ╖
        build('boxdL', 9557),                          # ╕
        build('boxdl', 9488),                          # ┐
        build('boxDR', 9556),                          # ╔
        build('boxDr', 9555),                          # ╓
        build('boxdR', 9554),                          # ╒
        build('boxdr', 9484),                          # ┌
        build('boxH', 9552),                           # ═
        build('boxh', 9472),                           # ─
        build('boxHD', 9574),                          # ╦
        build('boxHd', 9572),                          # ╤
        build('boxhD', 9573),                          # ╥
        build('boxhd', 9516),                          # ┬
        build('boxHU', 9577),                          # ╩
        build('boxHu', 9575),                          # ╧
        build('boxhU', 9576),                          # ╨
        build('boxhu', 9524),                          # ┴
        build('boxminus', 8863),                       # ⊟
        build('boxplus', 8862),                        # ⊞
        build('boxtimes', 8864),                       # ⊠
        build('boxUL', 9565),                          # ╝
        build('boxUl', 9564),                          # ╜
        build('boxuL', 9563),                          # ╛
        build('boxul', 9496),                          # ┘
        build('boxUR', 9562),                          # ╚
        build('boxUr', 9561),                          # ╙
        build('boxuR', 9560),                          # ╘
        build('boxur', 9492),                          # └
        build('boxV', 9553),                           # ║
        build('boxv', 9474),                           # │
        build('boxVH', 9580),                          # ╬
        build('boxVh', 9579),                          # ╫
        build('boxvH', 9578),                          # ╪
        build('boxvh', 9532),                          # ┼
        build('boxVL', 9571),                          # ╣
        build('boxVl', 9570),                          # ╢
        build('boxvL', 9569),                          # ╡
        build('boxvl', 9508),                          # ┤
        build('boxVR', 9568),                          # ╠
        build('boxVr', 9567),                          # ╟
        build('boxvR', 9566),                          # ╞
        build('boxvr', 9500),                          # ├
        build('bprime', 8245),                         # ‵
        build('Breve', 728),                           # ˘
        build('breve', 728),                           # ˘
        build('Bscr', 8492),                           # ℬ
        build('bscr', 119991),                         # 𝒷
        build('bsemi', 8271),                          # ⁏
        build('bsim', 8765),                           # ∽
        build('bsime', 8909),                          # ⋍
        build('bsol', 92),                             # \
        build('bsolb', 10693),                         # ⧅
        build('bsolhsub', 10184),                      # ⟈
        build('bullet', 8226),                         # •
        build('bump', 8782),                           # ≎
        build('bumpE', 10926),                         # ⪮
        build('bumpe', 8783),                          # ≏
        build('Bumpeq', 8782),                         # ≎
        build('bumpeq', 8783),                         # ≏
        build('Cacute', 262),                          # Ć
        build('cacute', 263),                          # ć
        build('Cap', 8914),                            # ⋒
        build('cap', 8745),                            # ∩
        build('capand', 10820),                        # ⩄
        build('capbrcup', 10825),                      # ⩉
        build('capcap', 10827),                        # ⩋
        build('capcup', 10823),                        # ⩇
        build('capdot', 10816),                        # ⩀
        build('CapitalDifferentialD', 8517),           # ⅅ
        build('caps', '∩︀'),                            # ∩︀
        build('caret', 8257),                          # ⁁
        build('caron', 711),                           # ˇ
        build('Cayleys', 8493),                        # ℭ
        build('ccaps', 10829),                         # ⩍
        build('Ccaron', 268),                          # Č
        build('ccaron', 269),                          # č
        build('Ccirc', 264),                           # Ĉ
        build('ccirc', 265),                           # ĉ
        build('Cconint', 8752),                        # ∰
        build('ccups', 10828),                         # ⩌
        build('ccupssm', 10832),                       # ⩐
        build('Cdot', 266),                            # Ċ
        build('cdot', 267),                            # ċ
        build('Cedilla', 184),                         # ¸
        build('cemptyv', 10674),                       # ⦲
        build('CenterDot', 183),                       # ·
        build('centerdot', 183),                       # ·
        build('Cfr', 8493),                            # ℭ
        build('cfr', 120096),                          # 𝔠
        build('CHcy', 1063),                           # Ч
        build('chcy', 1095),                           # ч
        build('check', 10003),                         # ✓
        build('checkmark', 10003),                     # ✓
        build('cir', 9675),                            # ○
        build('circeq', 8791),                         # ≗
        build('circlearrowleft', 8634),                # ↺
        build('circlearrowright', 8635),               # ↻
        build('circledast', 8859),                     # ⊛
        build('circledcirc', 8858),                    # ⊚
        build('circleddash', 8861),                    # ⊝
        build('CircleDot', 8857),                      # ⊙
        build('circledR', 174),                        # ®
        build('circledS', 9416),                       # Ⓢ
        build('CircleMinus', 8854),                    # ⊖
        build('CirclePlus', 8853),                     # ⊕
        build('CircleTimes', 8855),                    # ⊗
        build('cirE', 10691),                          # ⧃
        build('cire', 8791),                           # ≗
        build('cirfnint', 10768),                      # ⨐
        build('cirmid', 10991),                        # ⫯
        build('cirscir', 10690),                       # ⧂
        build('ClockwiseContourIntegral', 8754),       # ∲
        build('CloseCurlyDoubleQuote', 8221),          # ”
        build('CloseCurlyQuote', 8217),                # ’
        build('clubsuit', 9827),                       # ♣
        build('Colon', 8759),                          # ∷
        build('colon', 58),                            # :
        build('Colone', 10868),                        # ⩴
        build('colone', 8788),                         # ≔
        build('coloneq', 8788),                        # ≔
        build('comma', 44),                            # ,
        build('commat', 64),                           # @
        build('comp', 8705),                           # ∁
        build('compfn', 8728),                         # ∘
        build('complement', 8705),                     # ∁
        build('complexes', 8450),                      # ℂ
        build('cong', 8773),                           # ≅
        build('congdot', 10861),                       # ⩭
        build('Congruent', 8801),                      # ≡
        build('Conint', 8751),                         # ∯
        build('conint', 8750),                         # ∮
        build('ContourIntegral', 8750),                # ∮
        build('Copf', 8450),                           # ℂ
        build('copf', 120148),                         # 𝕔
        build('coprod', 8720),                         # ∐
        build('Coproduct', 8720),                      # ∐
        build('COPY', 169),                            # ©
        build('COPY', 169),                            # ©
        build('copysr', 8471),                         # ℗
        build('CounterClockwiseContourIntegral', 8755),# ∳
        build('crarr', 8629),                          # ↵
        build('Cross', 10799),                         # ⨯
        build('cross', 10007),                         # ✗
        build('Cscr', 119966),                         # 𝒞
        build('cscr', 119992),                         # 𝒸
        build('csub', 10959),                          # ⫏
        build('csube', 10961),                         # ⫑
        build('csup', 10960),                          # ⫐
        build('csupe', 10962),                         # ⫒
        build('ctdot', 8943),                          # ⋯
        build('cudarrl', 10552),                       # ⤸
        build('cudarrr', 10549),                       # ⤵
        build('cuepr', 8926),                          # ⋞
        build('cuesc', 8927),                          # ⋟
        build('cularr', 8630),                         # ↶
        build('cularrp', 10557),                       # ⤽
        build('Cup', 8915),                            # ⋓
        build('cup', 8746),                            # ∪
        build('cupbrcap', 10824),                      # ⩈
        build('CupCap', 8781),                         # ≍
        build('cupcap', 10822),                        # ⩆
        build('cupcup', 10826),                        # ⩊
        build('cupdot', 8845),                         # ⊍
        build('cupor', 10821),                         # ⩅
        build('cups', '∪︀'),                            # ∪︀
        build('curarr', 8631),                         # ↷
        build('curarrm', 10556),                       # ⤼
        build('curlyeqprec', 8926),                    # ⋞
        build('curlyeqsucc', 8927),                    # ⋟
        build('curlyvee', 8910),                       # ⋎
        build('curlywedge', 8911),                     # ⋏
        build('curvearrowleft', 8630),                 # ↶
        build('curvearrowright', 8631),                # ↷
        build('cuvee', 8910),                          # ⋎
        build('cuwed', 8911),                          # ⋏
        build('cwconint', 8754),                       # ∲
        build('cwint', 8753),                          # ∱
        build('cylcty', 9005),                         # ⌭
        build('Dagger', 8225),                         # ‡
        build('daleth', 8504),                         # ℸ
        build('Darr', 8609),                           # ↡
        build('dArr', 8659),                           # ⇓
        build('darr', 8595),                           # ↓
        build('dash', 8208),                           # ‐
        build('Dashv', 10980),                         # ⫤
        build('dashv', 8867),                          # ⊣
        build('dbkarow', 10511),                       # ⤏
        build('dblac', 733),                           # ˝
        build('Dcaron', 270),                          # Ď
        build('dcaron', 271),                          # ď
        build('Dcy', 1044),                            # Д
        build('dcy', 1076),                            # д
        build('DD', 8517),                             # ⅅ
        build('dd', 8518),                             # ⅆ
        build('ddarr', 8650),                          # ⇊
        build('DDotrahd', 10513),                      # ⤑
        build('ddotseq', 10871),                       # ⩷
        build('Del', 8711),                            # ∇
        build('demptyv', 10673),                       # ⦱
        build('dfisht', 10623),                        # ⥿
        build('Dfr', 120071),                          # 𝔇
        build('dfr', 120097),                          # 𝔡
        build('dHar', 10597),                          # ⥥
        build('dharl', 8643),                          # ⇃
        build('dharr', 8642),                          # ⇂
        build('DiacriticalAcute', 180),                # ´
        build('DiacriticalDot', 729),                  # ˙
        build('DiacriticalDoubleAcute', 733),          # ˝
        build('DiacriticalGrave', 96),                 # `
        build('DiacriticalTilde', 732),                # ˜
        build('diam', 8900),                           # ⋄
        build('Diamond', 8900),                        # ⋄
        build('diamond', 8900),                        # ⋄
        build('diamondsuit', 9830),                    # ♦
        build('die', 168),                             # ¨
        build('DifferentialD', 8518),                  # ⅆ
        build('digamma', 989),                         # ϝ
        build('disin', 8946),                          # ⋲
        build('div', 247),                             # ÷
        build('divideontimes', 8903),                  # ⋇
        build('divonx', 8903),                         # ⋇
        build('DJcy', 1026),                           # Ђ
        build('djcy', 1106),                           # ђ
        build('dlcorn', 8990),                         # ⌞
        build('dlcrop', 8973),                         # ⌍
        build('dollar', 36),                           # $
        build('Dopf', 120123),                         # 𝔻
        build('dopf', 120149),                         # 𝕕
        build('Dot', 168),                             # ¨
        build('dot', 729),                             # ˙
        build('DotDot', 8412),                         #⃜ 
        build('doteq', 8784),                          # ≐
        build('doteqdot', 8785),                       # ≑
        build('DotEqual', 8784),                       # ≐
        build('dotminus', 8760),                       # ∸
        build('dotplus', 8724),                        # ∔
        build('dotsquare', 8865),                      # ⊡
        build('doublebarwedge', 8966),                 # ⌆
        build('DoubleContourIntegral', 8751),          # ∯
        build('DoubleDot', 168),                       # ¨
        build('DoubleDownArrow', 8659),                # ⇓
        build('DoubleLeftArrow', 8656),                # ⇐
        build('DoubleLeftRightArrow', 8660),           # ⇔
        build('DoubleLeftTee', 10980),                 # ⫤
        build('DoubleLongLeftArrow', 10232),           # ⟸
        build('DoubleLongLeftRightArrow', 10234),      # ⟺
        build('DoubleLongRightArrow', 10233),          # ⟹
        build('DoubleRightArrow', 8658),               # ⇒
        build('DoubleRightTee', 8872),                 # ⊨
        build('DoubleUpArrow', 8657),                  # ⇑
        build('DoubleUpDownArrow', 8661),              # ⇕
        build('DoubleVerticalBar', 8741),              # ∥
        build('DownArrow', 8595),                      # ↓
        build('Downarrow', 8659),                      # ⇓
        build('downarrow', 8595),                      # ↓
        build('DownArrowBar', 10515),                  # ⤓
        build('DownArrowUpArrow', 8693),               # ⇵
        build('DownBreve', 785),                       #̑ 
        build('downdownarrows', 8650),                 # ⇊
        build('downharpoonleft', 8643),                # ⇃
        build('downharpoonright', 8642),               # ⇂
        build('DownLeftRightVector', 10576),           # ⥐
        build('DownLeftTeeVector', 10590),             # ⥞
        build('DownLeftVector', 8637),                 # ↽
        build('DownLeftVectorBar', 10582),             # ⥖
        build('DownRightTeeVector', 10591),            # ⥟
        build('DownRightVector', 8641),                # ⇁
        build('DownRightVectorBar', 10583),            # ⥗
        build('DownTee', 8868),                        # ⊤
        build('DownTeeArrow', 8615),                   # ↧
        build('drbkarow', 10512),                      # ⤐
        build('drcorn', 8991),                         # ⌟
        build('drcrop', 8972),                         # ⌌
        build('Dscr', 119967),                         # 𝒟
        build('dscr', 119993),                         # 𝒹
        build('DScy', 1029),                           # Ѕ
        build('dscy', 1109),                           # ѕ
        build('dsol', 10742),                          # ⧶
        build('Dstrok', 272),                          # Đ
        build('dstrok', 273),                          # đ
        build('dtdot', 8945),                          # ⋱
        build('dtri', 9663),                           # ▿
        build('dtrif', 9662),                          # ▾
        build('duarr', 8693),                          # ⇵
        build('duhar', 10607),                         # ⥯
        build('dwangle', 10662),                       # ⦦
        build('DZcy', 1039),                           # Џ
        build('dzcy', 1119),                           # џ
        build('dzigrarr', 10239),                      # ⟿
        build('easter', 10862),                        # ⩮
        build('Ecaron', 282),                          # Ě
        build('ecaron', 283),                          # ě
        build('ecir', 8790),                           # ≖
        build('ecolon', 8789),                         # ≕
        build('Ecy', 1069),                            # Э
        build('ecy', 1101),                            # э
        build('eDDot', 10871),                         # ⩷
        build('Edot', 278),                            # Ė
        build('eDot', 8785),                           # ≑
        build('edot', 279),                            # ė
        build('ee', 8519),                             # ⅇ
        build('efDot', 8786),                          # ≒
        build('Efr', 120072),                          # 𝔈
        build('efr', 120098),                          # 𝔢
        build('eg', 10906),                            # ⪚
        build('egs', 10902),                           # ⪖
        build('egsdot', 10904),                        # ⪘
        build('el', 10905),                            # ⪙
        build('Element', 8712),                        # ∈
        build('elinters', 9191),                       # ⏧
        build('ell', 8467),                            # ℓ
        build('els', 10901),                           # ⪕
        build('elsdot', 10903),                        # ⪗
        build('Emacr', 274),                           # Ē
        build('emacr', 275),                           # ē
        build('empty', 8709),                          # ∅
        build('emptyset', 8709),                       # ∅
        build('EmptySmallSquare', 9723),               # ◻
        build('emptyv', 8709),                         # ∅
        build('EmptyVerySmallSquare', 9643),           # ▫
        build('emsp13', 8196),                         #  
        build('emsp14', 8197),                         #  
        build('ENG', 330),                             # Ŋ
        build('eng', 331),                             # ŋ
        build('Eogon', 280),                           # Ę
        build('eogon', 281),                           # ę
        build('Eopf', 120124),                         # 𝔼
        build('eopf', 120150),                         # 𝕖
        build('epar', 8917),                           # ⋕
        build('eparsl', 10723),                        # ⧣
        build('eplus', 10865),                         # ⩱
        build('epsiv', 1013),                          # ϵ
        build('eqcirc', 8790),                         # ≖
        build('eqcolon', 8789),                        # ≕
        build('eqsim', 8770),                          # ≂
        build('eqslantgtr', 10902),                    # ⪖
        build('eqslantless', 10901),                   # ⪕
        build('Equal', 10869),                         # ⩵
        build('equals', 61),                           # =
        build('EqualTilde', 8770),                     # ≂
        build('equest', 8799),                         # ≟
        build('Equilibrium', 8652),                    # ⇌
        build('equiv', 8801),                          # ≡
        build('equivDD', 10872),                       # ⩸
        build('eqvparsl', 10725),                      # ⧥
        build('erarr', 10609),                         # ⥱
        build('erDot', 8787),                          # ≓
        build('Escr', 8496),                           # ℰ
        build('escr', 8495),                           # ℯ
        build('esdot', 8784),                          # ≐
        build('Esim', 10867),                          # ⩳
        build('esim', 8770),                           # ≂
        build('excl', 33),                             # !
        build('exist', 8707),                          # ∃
        build('Exists', 8707),                         # ∃
        build('expectation', 8496),                    # ℰ
        build('ExponentialE', 8519),                   # ⅇ
        build('exponentiale', 8519),                   # ⅇ
        build('fallingdotseq', 8786),                  # ≒
        build('Fcy', 1060),                            # Ф
        build('fcy', 1092),                            # ф
        build('female', 9792),                         # ♀
        build('ffilig', 64259),                        # ﬃ
        build('fflig', 64256),                         # ﬀ
        build('ffllig', 64260),                        # ﬄ
        build('Ffr', 120073),                          # 𝔉
        build('ffr', 120099),                          # 𝔣
        build('filig', 64257),                         # ﬁ
        build('FilledSmallSquare', 9724),              # ◼
        build('FilledVerySmallSquare', 9642),          # ▪
        build('fjlig', 'fj'),                          # fj
        build('flat', 9837),                           # ♭
        build('fllig', 64258),                         # ﬂ
        build('fltns', 9649),                          # ▱
        build('Fopf', 120125),                         # 𝔽
        build('fopf', 120151),                         # 𝕗
        build('ForAll', 8704),                         # ∀
        build('forall', 8704),                         # ∀
        build('fork', 8916),                           # ⋔
        build('forkv', 10969),                         # ⫙
        build('Fouriertrf', 8497),                     # ℱ
        build('fpartint', 10765),                      # ⨍
        build('frac13', 8531),                         # ⅓
        build('frac15', 8533),                         # ⅕
        build('frac16', 8537),                         # ⅙
        build('frac18', 8539),                         # ⅛
        build('frac23', 8532),                         # ⅔
        build('frac25', 8534),                         # ⅖
        build('frac35', 8535),                         # ⅗
        build('frac38', 8540),                         # ⅜
        build('frac45', 8536),                         # ⅘
        build('frac56', 8538),                         # ⅚
        build('frac58', 8541),                         # ⅝
        build('frac78', 8542),                         # ⅞
        build('frasl', 8260),                          # ⁄
        build('frown', 8994),                          # ⌢
        build('Fscr', 8497),                           # ℱ
        build('fscr', 119995),                         # 𝒻
        build('gacute', 501),                          # ǵ
        build('Gammad', 988),                          # Ϝ
        build('gammad', 989),                          # ϝ
        build('gap', 10886),                           # ⪆
        build('Gbreve', 286),                          # Ğ
        build('gbreve', 287),                          # ğ
        build('Gcedil', 290),                          # Ģ
        build('Gcirc', 284),                           # Ĝ
        build('gcirc', 285),                           # ĝ
        build('Gcy', 1043),                            # Г
        build('gcy', 1075),                            # г
        build('Gdot', 288),                            # Ġ
        build('gdot', 289),                            # ġ
        build('gE', 8807),                             # ≧
        build('ge', 8805),                             # ≥
        build('gEl', 10892),                           # ⪌
        build('gel', 8923),                            # ⋛
        build('geq', 8805),                            # ≥
        build('geqq', 8807),                           # ≧
        build('geqslant', 10878),                      # ⩾
        build('ges', 10878),                           # ⩾
        build('gescc', 10921),                         # ⪩
        build('gesdot', 10880),                        # ⪀
        build('gesdoto', 10882),                       # ⪂
        build('gesdotol', 10884),                      # ⪄
        build('gesl', '⋛︀'),                            # ⋛︀
        build('gesles', 10900),                        # ⪔
        build('Gfr', 120074),                          # 𝔊
        build('gfr', 120100),                          # 𝔤
        build('Gg', 8921),                             # ⋙
        build('gg', 8811),                             # ≫
        build('ggg', 8921),                            # ⋙
        build('gimel', 8503),                          # ℷ
        build('GJcy', 1027),                           # Ѓ
        build('gjcy', 1107),                           # ѓ
        build('gl', 8823),                             # ≷
        build('gla', 10917),                           # ⪥
        build('glE', 10898),                           # ⪒
        build('glj', 10916),                           # ⪤
        build('gnap', 10890),                          # ⪊
        build('gnapprox', 10890),                      # ⪊
        build('gnE', 8809),                            # ≩
        build('gne', 10888),                           # ⪈
        build('gneq', 10888),                          # ⪈
        build('gneqq', 8809),                          # ≩
        build('gnsim', 8935),                          # ⋧
        build('Gopf', 120126),                         # 𝔾
        build('gopf', 120152),                         # 𝕘
        build('grave', 96),                            # `
        build('GreaterEqual', 8805),                   # ≥
        build('GreaterEqualLess', 8923),               # ⋛
        build('GreaterFullEqual', 8807),               # ≧
        build('GreaterGreater', 10914),                # ⪢
        build('GreaterLess', 8823),                    # ≷
        build('GreaterSlantEqual', 10878),             # ⩾
        build('GreaterTilde', 8819),                   # ≳
        build('Gscr', 119970),                         # 𝒢
        build('gscr', 8458),                           # ℊ
        build('gsim', 8819),                           # ≳
        build('gsime', 10894),                         # ⪎
        build('gsiml', 10896),                         # ⪐
        build('Gt', 8811),                             # ≫
        build('gtcc', 10919),                          # ⪧
        build('gtcir', 10874),                         # ⩺
        build('gtdot', 8919),                          # ⋗
        build('gtlPar', 10645),                        # ⦕
        build('gtquest', 10876),                       # ⩼
        build('gtrapprox', 10886),                     # ⪆
        build('gtrarr', 10616),                        # ⥸
        build('gtrdot', 8919),                         # ⋗
        build('gtreqless', 8923),                      # ⋛
        build('gtreqqless', 10892),                    # ⪌
        build('gtrless', 8823),                        # ≷
        build('gtrsim', 8819),                         # ≳
        build('gvertneqq', '≩︀'),                       # ≩︀
        build('gvnE', '≩︀'),                            # ≩︀
        build('Hacek', 711),                           # ˇ
        build('hairsp', 8202),                         #  
        build('half', 189),                            # ½
        build('hamilt', 8459),                         # ℋ
        build('HARDcy', 1066),                         # Ъ
        build('hardcy', 1098),                         # ъ
        build('hArr', 8660),                           # ⇔
        build('harr', 8596),                           # ↔
        build('harrcir', 10568),                       # ⥈
        build('harrw', 8621),                          # ↭
        build('Hat', 94),                              # ^
        build('hbar', 8463),                           # ℏ
        build('Hcirc', 292),                           # Ĥ
        build('hcirc', 293),                           # ĥ
        build('heartsuit', 9829),                      # ♥
        build('hercon', 8889),                         # ⊹
        build('Hfr', 8460),                            # ℌ
        build('hfr', 120101),                          # 𝔥
        build('HilbertSpace', 8459),                   # ℋ
        build('hksearow', 10533),                      # ⤥
        build('hkswarow', 10534),                      # ⤦
        build('hoarr', 8703),                          # ⇿
        build('homtht', 8763),                         # ∻
        build('hookleftarrow', 8617),                  # ↩
        build('hookrightarrow', 8618),                 # ↪
        build('Hopf', 8461),                           # ℍ
        build('hopf', 120153),                         # 𝕙
        build('horbar', 8213),                         # ―
        build('HorizontalLine', 9472),                 # ─
        build('Hscr', 8459),                           # ℋ
        build('hscr', 119997),                         # 𝒽
        build('hslash', 8463),                         # ℏ
        build('Hstrok', 294),                          # Ħ
        build('hstrok', 295),                          # ħ
        build('HumpDownHump', 8782),                   # ≎
        build('HumpEqual', 8783),                      # ≏
        build('hybull', 8259),                         # ⁃
        build('hyphen', 8208),                         # ‐
        build('ic', 8291),                             # ⁣
        build('Icy', 1048),                            # И
        build('icy', 1080),                            # и
        build('Idot', 304),                            # İ
        build('IEcy', 1045),                           # Е
        build('iecy', 1077),                           # е
        build('iff', 8660),                            # ⇔
        build('Ifr', 8465),                            # ℑ
        build('ifr', 120102),                          # 𝔦
        build('ii', 8520),                             # ⅈ
        build('iiiint', 10764),                        # ⨌
        build('iiint', 8749),                          # ∭
        build('iinfin', 10716),                        # ⧜
        build('iiota', 8489),                          # ℩
        build('IJlig', 306),                           # Ĳ
        build('ijlig', 307),                           # ĳ
        build('Im', 8465),                             # ℑ
        build('Imacr', 298),                           # Ī
        build('imacr', 299),                           # ī
        build('ImaginaryI', 8520),                     # ⅈ
        build('imagline', 8464),                       # ℐ
        build('imagpart', 8465),                       # ℑ
        build('imath', 305),                           # ı
        build('imof', 8887),                           # ⊷
        build('imped', 437),                           # Ƶ
        build('Implies', 8658),                        # ⇒
        build('in', 8712),                             # ∈
        build('incare', 8453),                         # ℅
        build('infin', 8734),                          # ∞
        build('infintie', 10717),                      # ⧝
        build('inodot', 305),                          # ı
        build('Int', 8748),                            # ∬
        build('int', 8747),                            # ∫
        build('intcal', 8890),                         # ⊺
        build('integers', 8484),                       # ℤ
        build('Integral', 8747),                       # ∫
        build('intercal', 8890),                       # ⊺
        build('Intersection', 8898),                   # ⋂
        build('intlarhk', 10775),                      # ⨗
        build('intprod', 10812),                       # ⨼
        build('InvisibleComma', 8291),                 # ⁣
        build('InvisibleTimes', 8290),                 # ⁢
        build('IOcy', 1025),                           # Ё
        build('iocy', 1105),                           # ё
        build('Iogon', 302),                           # Į
        build('iogon', 303),                           # į
        build('Iopf', 120128),                         # 𝕀
        build('iopf', 120154),                         # 𝕚
        build('iprod', 10812),                         # ⨼
        build('Iscr', 8464),                           # ℐ
        build('iscr', 119998),                         # 𝒾
        build('isin', 8712),                           # ∈
        build('isindot', 8949),                        # ⋵
        build('isinE', 8953),                          # ⋹
        build('isins', 8948),                          # ⋴
        build('isinsv', 8947),                         # ⋳
        build('isinv', 8712),                          # ∈
        build('it', 8290),                             # ⁢
        build('Itilde', 296),                          # Ĩ
        build('itilde', 297),                          # ĩ
        build('Iukcy', 1030),                          # І
        build('iukcy', 1110),                          # і
        build('Jcirc', 308),                           # Ĵ
        build('jcirc', 309),                           # ĵ
        build('Jcy', 1049),                            # Й
        build('jcy', 1081),                            # й
        build('Jfr', 120077),                          # 𝔍
        build('jfr', 120103),                          # 𝔧
        build('jmath', 567),                           # ȷ
        build('Jopf', 120129),                         # 𝕁
        build('jopf', 120155),                         # 𝕛
        build('Jscr', 119973),                         # 𝒥
        build('jscr', 119999),                         # 𝒿
        build('Jsercy', 1032),                         # Ј
        build('jsercy', 1112),                         # ј
        build('Jukcy', 1028),                          # Є
        build('jukcy', 1108),                          # є
        build('kappav', 1008),                         # ϰ
        build('Kcedil', 310),                          # Ķ
        build('kcedil', 311),                          # ķ
        build('Kcy', 1050),                            # К
        build('kcy', 1082),                            # к
        build('Kfr', 120078),                          # 𝔎
        build('kfr', 120104),                          # 𝔨
        build('kgreen', 312),                          # ĸ
        build('KHcy', 1061),                           # Х
        build('khcy', 1093),                           # х
        build('KJcy', 1036),                           # Ќ
        build('kjcy', 1116),                           # ќ
        build('Kopf', 120130),                         # 𝕂
        build('kopf', 120156),                         # 𝕜
        build('Kscr', 119974),                         # 𝒦
        build('kscr', 120000),                         # 𝓀
        build('lAarr', 8666),                          # ⇚
        build('Lacute', 313),                          # Ĺ
        build('lacute', 314),                          # ĺ
        build('laemptyv', 10676),                      # ⦴
        build('lagran', 8466),                         # ℒ
        build('Lang', 10218),                          # ⟪
        build('langd', 10641),                         # ⦑
        build('langle', 10216),                        # ⟨
        build('lap', 10885),                           # ⪅
        build('Laplacetrf', 8466),                     # ℒ
        build('Larr', 8606),                           # ↞
        build('lArr', 8656),                           # ⇐
        build('larr', 8592),                           # ←
        build('larrb', 8676),                          # ⇤
        build('larrbfs', 10527),                       # ⤟
        build('larrfs', 10525),                        # ⤝
        build('larrhk', 8617),                         # ↩
        build('larrlp', 8619),                         # ↫
        build('larrpl', 10553),                        # ⤹
        build('larrsim', 10611),                       # ⥳
        build('larrtl', 8610),                         # ↢
        build('lat', 10923),                           # ⪫
        build('lAtail', 10523),                        # ⤛
        build('latail', 10521),                        # ⤙
        build('late', 10925),                          # ⪭
        build('lates', '⪭︀'),                           # ⪭︀
        build('lBarr', 10510),                         # ⤎
        build('lbarr', 10508),                         # ⤌
        build('lbbrk', 10098),                         # ❲
        build('lbrace', 123),                          # {
        build('lbrack', 91),                           # [
        build('lbrke', 10635),                         # ⦋
        build('lbrksld', 10639),                       # ⦏
        build('lbrkslu', 10637),                       # ⦍
        build('Lcaron', 317),                          # Ľ
        build('lcaron', 318),                          # ľ
        build('Lcedil', 315),                          # Ļ
        build('lcedil', 316),                          # ļ
        build('lceil', 8968),                          # ⌈
        build('lcub', 123),                            # {
        build('Lcy', 1051),                            # Л
        build('lcy', 1083),                            # л
        build('ldca', 10550),                          # ⤶
        build('ldquor', 8222),                         # „
        build('ldrdhar', 10599),                       # ⥧
        build('ldrushar', 10571),                      # ⥋
        build('ldsh', 8626),                           # ↲
        build('lE', 8806),                             # ≦
        build('le', 8804),                             # ≤
        build('LeftAngleBracket', 10216),              # ⟨
        build('LeftArrow', 8592),                      # ←
        build('Leftarrow', 8656),                      # ⇐
        build('leftarrow', 8592),                      # ←
        build('LeftArrowBar', 8676),                   # ⇤
        build('LeftArrowRightArrow', 8646),            # ⇆
        build('leftarrowtail', 8610),                  # ↢
        build('LeftCeiling', 8968),                    # ⌈
        build('LeftDoubleBracket', 10214),             # ⟦
        build('LeftDownTeeVector', 10593),             # ⥡
        build('LeftDownVector', 8643),                 # ⇃
        build('LeftDownVectorBar', 10585),             # ⥙
        build('LeftFloor', 8970),                      # ⌊
        build('leftharpoondown', 8637),                # ↽
        build('leftharpoonup', 8636),                  # ↼
        build('leftleftarrows', 8647),                 # ⇇
        build('LeftRightArrow', 8596),                 # ↔
        build('Leftrightarrow', 8660),                 # ⇔
        build('leftrightarrow', 8596),                 # ↔
        build('leftrightarrows', 8646),                # ⇆
        build('leftrightharpoons', 8651),              # ⇋
        build('leftrightsquigarrow', 8621),            # ↭
        build('LeftRightVector', 10574),               # ⥎
        build('LeftTee', 8867),                        # ⊣
        build('LeftTeeArrow', 8612),                   # ↤
        build('LeftTeeVector', 10586),                 # ⥚
        build('leftthreetimes', 8907),                 # ⋋
        build('LeftTriangle', 8882),                   # ⊲
        build('LeftTriangleBar', 10703),               # ⧏
        build('LeftTriangleEqual', 8884),              # ⊴
        build('LeftUpDownVector', 10577),              # ⥑
        build('LeftUpTeeVector', 10592),               # ⥠
        build('LeftUpVector', 8639),                   # ↿
        build('LeftUpVectorBar', 10584),               # ⥘
        build('LeftVector', 8636),                     # ↼
        build('LeftVectorBar', 10578),                 # ⥒
        build('lEg', 10891),                           # ⪋
        build('leg', 8922),                            # ⋚
        build('leq', 8804),                            # ≤
        build('leqq', 8806),                           # ≦
        build('leqslant', 10877),                      # ⩽
        build('les', 10877),                           # ⩽
        build('lescc', 10920),                         # ⪨
        build('lesdot', 10879),                        # ⩿
        build('lesdoto', 10881),                       # ⪁
        build('lesdotor', 10883),                      # ⪃
        build('lesg', '⋚︀'),                            # ⋚︀
        build('lesges', 10899),                        # ⪓
        build('lessapprox', 10885),                    # ⪅
        build('lessdot', 8918),                        # ⋖
        build('lesseqgtr', 8922),                      # ⋚
        build('lesseqqgtr', 10891),                    # ⪋
        build('LessEqualGreater', 8922),               # ⋚
        build('LessFullEqual', 8806),                  # ≦
        build('LessGreater', 8822),                    # ≶
        build('lessgtr', 8822),                        # ≶
        build('LessLess', 10913),                      # ⪡
        build('lesssim', 8818),                        # ≲
        build('LessSlantEqual', 10877),                # ⩽
        build('LessTilde', 8818),                      # ≲
        build('lfisht', 10620),                        # ⥼
        build('lfloor', 8970),                         # ⌊
        build('Lfr', 120079),                          # 𝔏
        build('lfr', 120105),                          # 𝔩
        build('lg', 8822),                             # ≶
        build('lgE', 10897),                           # ⪑
        build('lHar', 10594),                          # ⥢
        build('lhard', 8637),                          # ↽
        build('lharu', 8636),                          # ↼
        build('lharul', 10602),                        # ⥪
        build('lhblk', 9604),                          # ▄
        build('LJcy', 1033),                           # Љ
        build('ljcy', 1113),                           # љ
        build('Ll', 8920),                             # ⋘
        build('ll', 8810),                             # ≪
        build('llarr', 8647),                          # ⇇
        build('llcorner', 8990),                       # ⌞
        build('Lleftarrow', 8666),                     # ⇚
        build('llhard', 10603),                        # ⥫
        build('lltri', 9722),                          # ◺
        build('Lmidot', 319),                          # Ŀ
        build('lmidot', 320),                          # ŀ
        build('lmoust', 9136),                         # ⎰
        build('lmoustache', 9136),                     # ⎰
        build('lnap', 10889),                          # ⪉
        build('lnapprox', 10889),                      # ⪉
        build('lnE', 8808),                            # ≨
        build('lne', 10887),                           # ⪇
        build('lneq', 10887),                          # ⪇
        build('lneqq', 8808),                          # ≨
        build('lnsim', 8934),                          # ⋦
        build('loang', 10220),                         # ⟬
        build('loarr', 8701),                          # ⇽
        build('lobrk', 10214),                         # ⟦
        build('LongLeftArrow', 10229),                 # ⟵
        build('Longleftarrow', 10232),                 # ⟸
        build('longleftarrow', 10229),                 # ⟵
        build('LongLeftRightArrow', 10231),            # ⟷
        build('Longleftrightarrow', 10234),            # ⟺
        build('longleftrightarrow', 10231),            # ⟷
        build('longmapsto', 10236),                    # ⟼
        build('LongRightArrow', 10230),                # ⟶
        build('Longrightarrow', 10233),                # ⟹
        build('longrightarrow', 10230),                # ⟶
        build('looparrowleft', 8619),                  # ↫
        build('looparrowright', 8620),                 # ↬
        build('lopar', 10629),                         # ⦅
        build('Lopf', 120131),                         # 𝕃
        build('lopf', 120157),                         # 𝕝
        build('loplus', 10797),                        # ⨭
        build('lotimes', 10804),                       # ⨴
        build('lowast', 8727),                         # ∗
        build('lowbar', 95),                           # _
        build('LowerLeftArrow', 8601),                 # ↙
        build('LowerRightArrow', 8600),                # ↘
        build('lozenge', 9674),                        # ◊
        build('lozf', 10731),                          # ⧫
        build('lpar', 40),                             # (
        build('lparlt', 10643),                        # ⦓
        build('lrarr', 8646),                          # ⇆
        build('lrcorner', 8991),                       # ⌟
        build('lrhar', 8651),                          # ⇋
        build('lrhard', 10605),                        # ⥭
        build('lrtri', 8895),                          # ⊿
        build('Lscr', 8466),                           # ℒ
        build('lscr', 120001),                         # 𝓁
        build('Lsh', 8624),                            # ↰
        build('lsh', 8624),                            # ↰
        build('lsim', 8818),                           # ≲
        build('lsime', 10893),                         # ⪍
        build('lsimg', 10895),                         # ⪏
        build('lsqb', 91),                             # [
        build('lsquor', 8218),                         # ‚
        build('Lstrok', 321),                          # Ł
        build('lstrok', 322),                          # ł
        build('Lt', 8810),                             # ≪
        build('ltcc', 10918),                          # ⪦
        build('ltcir', 10873),                         # ⩹
        build('ltdot', 8918),                          # ⋖
        build('lthree', 8907),                         # ⋋
        build('ltimes', 8905),                         # ⋉
        build('ltlarr', 10614),                        # ⥶
        build('ltquest', 10875),                       # ⩻
        build('ltri', 9667),                           # ◃
        build('ltrie', 8884),                          # ⊴
        build('ltrif', 9666),                          # ◂
        build('ltrPar', 10646),                        # ⦖
        build('lurdshar', 10570),                      # ⥊
        build('luruhar', 10598),                       # ⥦
        build('lvertneqq', '≨︀'),                       # ≨︀
        build('lvnE', '≨︀'),                            # ≨︀
        build('male', 9794),                           # ♂
        build('malt', 10016),                          # ✠
        build('maltese', 10016),                       # ✠
        build('Map', 10501),                           # ⤅
        build('map', 8614),                            # ↦
        build('mapsto', 8614),                         # ↦
        build('mapstodown', 8615),                     # ↧
        build('mapstoleft', 8612),                     # ↤
        build('mapstoup', 8613),                       # ↥
        build('marker', 9646),                         # ▮
        build('mcomma', 10793),                        # ⨩
        build('Mcy', 1052),                            # М
        build('mcy', 1084),                            # м
        build('mDDot', 8762),                          # ∺
        build('measuredangle', 8737),                  # ∡
        build('MediumSpace', 8287),                    #  
        build('Mellintrf', 8499),                      # ℳ
        build('Mfr', 120080),                          # 𝔐
        build('mfr', 120106),                          # 𝔪
        build('mho', 8487),                            # ℧
        build('mid', 8739),                            # ∣
        build('midast', 42),                           # *
        build('midcir', 10992),                        # ⫰
        build('minus', 8722),                          # −
        build('minusb', 8863),                         # ⊟
        build('minusd', 8760),                         # ∸
        build('minusdu', 10794),                       # ⨪
        build('MinusPlus', 8723),                      # ∓
        build('mlcp', 10971),                          # ⫛
        build('mldr', 8230),                           # …
        build('mnplus', 8723),                         # ∓
        build('models', 8871),                         # ⊧
        build('Mopf', 120132),                         # 𝕄
        build('mopf', 120158),                         # 𝕞
        build('mp', 8723),                             # ∓
        build('Mscr', 8499),                           # ℳ
        build('mscr', 120002),                         # 𝓂
        build('mstpos', 8766),                         # ∾
        build('multimap', 8888),                       # ⊸
        build('mumap', 8888),                          # ⊸
        build('nabla', 8711),                          # ∇
        build('Nacute', 323),                          # Ń
        build('nacute', 324),                          # ń
        build('nang', '∠⃒'),                            # ∠⃒
        build('nap', 8777),                            # ≉
        build('napE', '⩰̸'),                            # ⩰̸
        build('napid', '≋̸'),                           # ≋̸
        build('napos', 329),                           # ŉ
        build('napprox', 8777),                        # ≉
        build('natur', 9838),                          # ♮
        build('natural', 9838),                        # ♮
        build('naturals', 8469),                       # ℕ
        build('nbump', '≎̸'),                           # ≎̸
        build('nbumpe', '≏̸'),                          # ≏̸
        build('ncap', 10819),                          # ⩃
        build('Ncaron', 327),                          # Ň
        build('ncaron', 328),                          # ň
        build('Ncedil', 325),                          # Ņ
        build('ncedil', 326),                          # ņ
        build('ncong', 8775),                          # ≇
        build('ncongdot', '⩭̸'),                        # ⩭̸
        build('ncup', 10818),                          # ⩂
        build('Ncy', 1053),                            # Н
        build('ncy', 1085),                            # н
        build('ne', 8800),                             # ≠
        build('nearhk', 10532),                        # ⤤
        build('neArr', 8663),                          # ⇗
        build('nearr', 8599),                          # ↗
        build('nearrow', 8599),                        # ↗
        build('nedot', '≐̸'),                           # ≐̸
        build('NegativeMediumSpace', 8203),            # ​
        build('NegativeThickSpace', 8203),             # ​
        build('NegativeThinSpace', 8203),              # ​
        build('NegativeVeryThinSpace', 8203),          # ​
        build('nequiv', 8802),                         # ≢
        build('nesear', 10536),                        # ⤨
        build('nesim', '≂̸'),                           # ≂̸
        build('NestedGreaterGreater', 8811),           # ≫
        build('NestedLessLess', 8810),                 # ≪
        build('NewLine', 10),                          # 
        build('nexist', 8708),                         # ∄
        build('nexists', 8708),                        # ∄
        build('Nfr', 120081),                          # 𝔑
        build('nfr', 120107),                          # 𝔫
        build('ngE', '≧̸'),                             # ≧̸
        build('nge', 8817),                            # ≱
        build('ngeq', 8817),                           # ≱
        build('ngeqq', '≧̸'),                           # ≧̸
        build('ngeqslant', '⩾̸'),                       # ⩾̸
        build('nges', '⩾̸'),                            # ⩾̸
        build('nGg', '⋙̸'),                             # ⋙̸
        build('ngsim', 8821),                          # ≵
        build('nGt', '≫⃒'),                             # ≫⃒
        build('ngt', 8815),                            # ≯
        build('ngtr', 8815),                           # ≯
        build('nGtv', '≫̸'),                            # ≫̸
        build('nhArr', 8654),                          # ⇎
        build('nharr', 8622),                          # ↮
        build('nhpar', 10994),                         # ⫲
        build('ni', 8715),                             # ∋
        build('nis', 8956),                            # ⋼
        build('nisd', 8954),                           # ⋺
        build('niv', 8715),                            # ∋
        build('NJcy', 1034),                           # Њ
        build('njcy', 1114),                           # њ
        build('nlArr', 8653),                          # ⇍
        build('nlarr', 8602),                          # ↚
        build('nldr', 8229),                           # ‥
        build('nlE', '≦̸'),                             # ≦̸
        build('nle', 8816),                            # ≰
        build('nLeftarrow', 8653),                     # ⇍
        build('nleftarrow', 8602),                     # ↚
        build('nLeftrightarrow', 8654),                # ⇎
        build('nleftrightarrow', 8622),                # ↮
        build('nleq', 8816),                           # ≰
        build('nleqq', '≦̸'),                           # ≦̸
        build('nleqslant', '⩽̸'),                       # ⩽̸
        build('nles', '⩽̸'),                            # ⩽̸
        build('nless', 8814),                          # ≮
        build('nLl', '⋘̸'),                             # ⋘̸
        build('nlsim', 8820),                          # ≴
        build('nLt', '≪⃒'),                             # ≪⃒
        build('nlt', 8814),                            # ≮
        build('nltri', 8938),                          # ⋪
        build('nltrie', 8940),                         # ⋬
        build('nLtv', '≪̸'),                            # ≪̸
        build('nmid', 8740),                           # ∤
        build('NoBreak', 8288),                        # ⁠
        build('NonBreakingSpace', 160),                #  
        build('Nopf', 8469),                           # ℕ
        build('nopf', 120159),                         # 𝕟
        build('Not', 10988),                           # ⫬
        build('NotCongruent', 8802),                   # ≢
        build('NotCupCap', 8813),                      # ≭
        build('NotDoubleVerticalBar', 8742),           # ∦
        build('NotElement', 8713),                     # ∉
        build('NotEqual', 8800),                       # ≠
        build('NotEqualTilde', '≂̸'),                   # ≂̸
        build('NotExists', 8708),                      # ∄
        build('NotGreater', 8815),                     # ≯
        build('NotGreaterEqual', 8817),                # ≱
        build('NotGreaterFullEqual', '≧̸'),             # ≧̸
        build('NotGreaterGreater', '≫̸'),               # ≫̸
        build('NotGreaterLess', 8825),                 # ≹
        build('NotGreaterSlantEqual', '⩾̸'),            # ⩾̸
        build('NotGreaterTilde', 8821),                # ≵
        build('NotHumpDownHump', '≎̸'),                 # ≎̸
        build('NotHumpEqual', '≏̸'),                    # ≏̸
        build('notin', 8713),                          # ∉
        build('notindot', '⋵̸'),                        # ⋵̸
        build('notinE', '⋹̸'),                          # ⋹̸
        build('notinva', 8713),                        # ∉
        build('notinvb', 8951),                        # ⋷
        build('notinvc', 8950),                        # ⋶
        build('NotLeftTriangle', 8938),                # ⋪
        build('NotLeftTriangleBar', '⧏̸'),              # ⧏̸
        build('NotLeftTriangleEqual', 8940),           # ⋬
        build('NotLess', 8814),                        # ≮
        build('NotLessEqual', 8816),                   # ≰
        build('NotLessGreater', 8824),                 # ≸
        build('NotLessLess', '≪̸'),                     # ≪̸
        build('NotLessSlantEqual', '⩽̸'),               # ⩽̸
        build('NotLessTilde', 8820),                   # ≴
        build('NotNestedGreaterGreater', '⪢̸'),         # ⪢̸
        build('NotNestedLessLess', '⪡̸'),               # ⪡̸
        build('notni', 8716),                          # ∌
        build('notniva', 8716),                        # ∌
        build('notnivb', 8958),                        # ⋾
        build('notnivc', 8957),                        # ⋽
        build('NotPrecedes', 8832),                    # ⊀
        build('NotPrecedesEqual', '⪯̸'),                # ⪯̸
        build('NotPrecedesSlantEqual', 8928),          # ⋠
        build('NotReverseElement', 8716),              # ∌
        build('NotRightTriangle', 8939),               # ⋫
        build('NotRightTriangleBar', '⧐̸'),             # ⧐̸
        build('NotRightTriangleEqual', 8941),          # ⋭
        build('NotSquareSubset', '⊏̸'),                 # ⊏̸
        build('NotSquareSubsetEqual', 8930),           # ⋢
        build('NotSquareSuperset', '⊐̸'),               # ⊐̸
        build('NotSquareSupersetEqual', 8931),         # ⋣
        build('NotSubset', '⊂⃒'),                       # ⊂⃒
        build('NotSubsetEqual', 8840),                 # ⊈
        build('NotSucceeds', 8833),                    # ⊁
        build('NotSucceedsEqual', '⪰̸'),                # ⪰̸
        build('NotSucceedsSlantEqual', 8929),          # ⋡
        build('NotSucceedsTilde', '≿̸'),                # ≿̸
        build('NotSuperset', '⊃⃒'),                     # ⊃⃒
        build('NotSupersetEqual', 8841),               # ⊉
        build('NotTilde', 8769),                       # ≁
        build('NotTildeEqual', 8772),                  # ≄
        build('NotTildeFullEqual', 8775),              # ≇
        build('NotTildeTilde', 8777),                  # ≉
        build('NotVerticalBar', 8740),                 # ∤
        build('npar', 8742),                           # ∦
        build('nparallel', 8742),                      # ∦
        build('nparsl', '⫽⃥'),                          # ⫽⃥
        build('npart', '∂̸'),                           # ∂̸
        build('npolint', 10772),                       # ⨔
        build('npr', 8832),                            # ⊀
        build('nprcue', 8928),                         # ⋠
        build('npre', '⪯̸'),                            # ⪯̸
        build('nprec', 8832),                          # ⊀
        build('npreceq', '⪯̸'),                         # ⪯̸
        build('nrArr', 8655),                          # ⇏
        build('nrarr', 8603),                          # ↛
        build('nrarrc', '⤳̸'),                          # ⤳̸
        build('nrarrw', '↝̸'),                          # ↝̸
        build('nRightarrow', 8655),                    # ⇏
        build('nrightarrow', 8603),                    # ↛
        build('nrtri', 8939),                          # ⋫
        build('nrtrie', 8941),                         # ⋭
        build('nsc', 8833),                            # ⊁
        build('nsccue', 8929),                         # ⋡
        build('nsce', '⪰̸'),                            # ⪰̸
        build('Nscr', 119977),                         # 𝒩
        build('nscr', 120003),                         # 𝓃
        build('nshortmid', 8740),                      # ∤
        build('nshortparallel', 8742),                 # ∦
        build('nsim', 8769),                           # ≁
        build('nsime', 8772),                          # ≄
        build('nsimeq', 8772),                         # ≄
        build('nsmid', 8740),                          # ∤
        build('nspar', 8742),                          # ∦
        build('nsqsube', 8930),                        # ⋢
        build('nsqsupe', 8931),                        # ⋣
        build('nsub', 8836),                           # ⊄
        build('nsubE', '⫅̸'),                           # ⫅̸
        build('nsube', 8840),                          # ⊈
        build('nsubset', '⊂⃒'),                         # ⊂⃒
        build('nsubseteq', 8840),                      # ⊈
        build('nsubseteqq', '⫅̸'),                      # ⫅̸
        build('nsucc', 8833),                          # ⊁
        build('nsucceq', '⪰̸'),                         # ⪰̸
        build('nsup', 8837),                           # ⊅
        build('nsupE', '⫆̸'),                           # ⫆̸
        build('nsupe', 8841),                          # ⊉
        build('nsupset', '⊃⃒'),                         # ⊃⃒
        build('nsupseteq', 8841),                      # ⊉
        build('nsupseteqq', '⫆̸'),                      # ⫆̸
        build('ntgl', 8825),                           # ≹
        build('ntlg', 8824),                           # ≸
        build('ntriangleleft', 8938),                  # ⋪
        build('ntrianglelefteq', 8940),                # ⋬
        build('ntriangleright', 8939),                 # ⋫
        build('ntrianglerighteq', 8941),               # ⋭
        build('num', 35),                              # #
        build('numero', 8470),                         # №
        build('numsp', 8199),                          #  
        build('nvap', '≍⃒'),                            # ≍⃒
        build('nVDash', 8879),                         # ⊯
        build('nVdash', 8878),                         # ⊮
        build('nvDash', 8877),                         # ⊭
        build('nvdash', 8876),                         # ⊬
        build('nvge', '≥⃒'),                            # ≥⃒
        build('nvgt', '>⃒'),                            # >⃒
        build('nvHarr', 10500),                        # ⤄
        build('nvinfin', 10718),                       # ⧞
        build('nvlArr', 10498),                        # ⤂
        build('nvle', '≤⃒'),                            # ≤⃒
        build('nvlt', '<⃒'),                            # <⃒
        build('nvltrie', '⊴⃒'),                         # ⊴⃒
        build('nvrArr', 10499),                            # ⤃
        build('nvrtrie', '⊵⃒'),                         # ⊵⃒
        build('nvsim', '∼⃒'),                           # ∼⃒
        build('nwarhk', 10531),                        # ⤣
        build('nwArr', 8662),                          # ⇖
        build('nwarr', 8598),                          # ↖
        build('nwarrow', 8598),                        # ↖
        build('nwnear', 10535),                        # ⤧
        build('oast', 8859),                           # ⊛
        build('ocir', 8858),                           # ⊚
        build('Ocy', 1054),                            # О
        build('ocy', 1086),                            # о
        build('odash', 8861),                          # ⊝
        build('Odblac', 336),                          # Ő
        build('odblac', 337),                          # ő
        build('odiv', 10808),                          # ⨸
        build('odot', 8857),                           # ⊙
        build('odsold', 10684),                        # ⦼
        build('ofcir', 10687),                         # ⦿
        build('Ofr', 120082),                          # 𝔒
        build('ofr', 120108),                          # 𝔬
        build('ogon', 731),                            # ˛
        build('ogt', 10689),                           # ⧁
        build('ohbar', 10677),                         # ⦵
        build('oint', 8750),                           # ∮
        build('olarr', 8634),                          # ↺
        build('olcir', 10686),                         # ⦾
        build('olcross', 10683),                       # ⦻
        build('olt', 10688),                           # ⧀
        build('Omacr', 332),                           # Ō
        build('omacr', 333),                           # ō
        build('omid', 10678),                          # ⦶
        build('ominus', 8854),                         # ⊖
        build('Oopf', 120134),                         # 𝕆
        build('oopf', 120160),                         # 𝕠
        build('opar', 10679),                          # ⦷
        build('OpenCurlyDoubleQuote', 8220),           # “
        build('OpenCurlyQuote', 8216),                 # ‘
        build('operp', 10681),                         # ⦹
        build('oplus', 8853),                          # ⊕
        build('Or', 10836),                            # ⩔
        build('or', 8744),                             # ∨
        build('orarr', 8635),                          # ↻
        build('ord', 10845),                           # ⩝
        build('order', 8500),                          # ℴ
        build('orderof', 8500),                        # ℴ
        build('origof', 8886),                         # ⊶
        build('oror', 10838),                          # ⩖
        build('orslope', 10839),                       # ⩗
        build('orv', 10843),                           # ⩛
        build('oS', 9416),                             # Ⓢ
        build('Oscr', 119978),                         # 𝒪
        build('oscr', 8500),                           # ℴ
        build('osol', 8856),                           # ⊘
        build('Otimes', 10807),                        # ⨷
        build('otimes', 8855),                         # ⊗
        build('otimesas', 10806),                      # ⨶
        build('ovbar', 9021),                          # ⌽
        build('OverBar', 8254),                        # ‾
        build('OverBrace', 9182),                      # ⏞
        build('OverBracket', 9140),                    # ⎴
        build('OverParenthesis', 9180),                # ⏜
        build('par', 8741),                            # ∥
        build('parallel', 8741),                       # ∥
        build('parsim', 10995),                        # ⫳
        build('parsl', 11005),                         # ⫽
        build('part', 8706),                           # ∂
        build('PartialD', 8706),                       # ∂
        build('Pcy', 1055),                            # П
        build('pcy', 1087),                            # п
        build('percnt', 37),                           # %
        build('period', 46),                           # .
        build('perp', 8869),                           # ⊥
        build('pertenk', 8241),                        # ‱
        build('Pfr', 120083),                          # 𝔓
        build('pfr', 120109),                          # 𝔭
        build('phmmat', 8499),                         # ℳ
        build('phone', 9742),                          # ☎
        build('pitchfork', 8916),                      # ⋔
        build('piv', 982),                             # ϖ
        build('planck', 8463),                         # ℏ
        build('planckh', 8462),                        # ℎ
        build('plankv', 8463),                         # ℏ
        build('plus', 43),                             # +
        build('plusacir', 10787),                      # ⨣
        build('plusb', 8862),                          # ⊞
        build('pluscir', 10786),                       # ⨢
        build('plusdo', 8724),                         # ∔
        build('plusdu', 10789),                        # ⨥
        build('pluse', 10866),                         # ⩲
        build('PlusMinus', 177),                       # ±
        build('plussim', 10790),                       # ⨦
        build('plustwo', 10791),                       # ⨧
        build('pm', 177),                              # ±
        build('Poincareplane', 8460),                  # ℌ
        build('pointint', 10773),                      # ⨕
        build('Popf', 8473),                           # ℙ
        build('popf', 120161),                         # 𝕡
        build('Pr', 10939),                            # ⪻
        build('pr', 8826),                             # ≺
        build('prap', 10935),                          # ⪷
        build('prcue', 8828),                          # ≼
        build('prE', 10931),                           # ⪳
        build('pre', 10927),                           # ⪯
        build('prec', 8826),                           # ≺
        build('precapprox', 10935),                    # ⪷
        build('preccurlyeq', 8828),                    # ≼
        build('Precedes', 8826),                       # ≺
        build('PrecedesEqual', 10927),                 # ⪯
        build('PrecedesSlantEqual', 8828),             # ≼
        build('PrecedesTilde', 8830),                  # ≾
        build('preceq', 10927),                        # ⪯
        build('precnapprox', 10937),                   # ⪹
        build('precneqq', 10933),                      # ⪵
        build('precnsim', 8936),                       # ⋨
        build('precsim', 8830),                        # ≾
        build('primes', 8473),                         # ℙ
        build('prnap', 10937),                         # ⪹
        build('prnE', 10933),                          # ⪵
        build('prnsim', 8936),                         # ⋨
        build('prod', 8719),                           # ∏
        build('Product', 8719),                        # ∏
        build('profalar', 9006),                       # ⌮
        build('profline', 8978),                       # ⌒
        build('profsurf', 8979),                       # ⌓
        build('prop', 8733),                           # ∝
        build('Proportion', 8759),                     # ∷
        build('Proportional', 8733),                   # ∝
        build('propto', 8733),                         # ∝
        build('prsim', 8830),                          # ≾
        build('prurel', 8880),                         # ⊰
        build('Pscr', 119979),                         # 𝒫
        build('pscr', 120005),                         # 𝓅
        build('puncsp', 8200),                         #  
        build('Qfr', 120084),                          # 𝔔
        build('qfr', 120110),                          # 𝔮
        build('qint', 10764),                          # ⨌
        build('Qopf', 8474),                           # ℚ
        build('qopf', 120162),                         # 𝕢
        build('qprime', 8279),                         # ⁗
        build('Qscr', 119980),                         # 𝒬
        build('qscr', 120006),                         # 𝓆
        build('quaternions', 8461),                    # ℍ
        build('quatint', 10774),                       # ⨖
        build('quest', 63),                            # ?
        build('questeq', 8799),                        # ≟
        build('rAarr', 8667),                          # ⇛
        build('race', '∽̱'),                            # ∽̱
        build('Racute', 340),                          # Ŕ
        build('racute', 341),                          # ŕ
        build('radic', 8730),                          # √
        build('raemptyv', 10675),                      # ⦳
        build('Rang', 10219),                          # ⟫
        build('rangd', 10642),                         # ⦒
        build('range', 10661),                         # ⦥
        build('rangle', 10217),                        # ⟩
        build('Rarr', 8608),                           # ↠
        build('rArr', 8658),                           # ⇒
        build('rarr', 8594),                           # →
        build('rarrap', 10613),                        # ⥵
        build('rarrb', 8677),                          # ⇥
        build('rarrbfs', 10528),                       # ⤠
        build('rarrc', 10547),                         # ⤳
        build('rarrfs', 10526),                        # ⤞
        build('rarrhk', 8618),                         # ↪
        build('rarrlp', 8620),                         # ↬
        build('rarrpl', 10565),                        # ⥅
        build('rarrsim', 10612),                       # ⥴
        build('Rarrtl', 10518),                        # ⤖
        build('rarrtl', 8611),                         # ↣
        build('rarrw', 8605),                          # ↝
        build('rAtail', 10524),                        # ⤜
        build('ratail', 10522),                        # ⤚
        build('ratio', 8758),                          # ∶
        build('rationals', 8474),                      # ℚ
        build('RBarr', 10512),                         # ⤐
        build('rBarr', 10511),                         # ⤏
        build('rbarr', 10509),                         # ⤍
        build('rbbrk', 10099),                         # ❳
        build('rbrace', 125),                          # }
        build('rbrack', 93),                           # ]
        build('rbrke', 10636),                         # ⦌
        build('rbrksld', 10638),                       # ⦎
        build('rbrkslu', 10640),                       # ⦐
        build('Rcaron', 344),                          # Ř
        build('rcaron', 345),                          # ř
        build('Rcedil', 342),                          # Ŗ
        build('rcedil', 343),                          # ŗ
        build('rceil', 8969),                          # ⌉
        build('rcub', 125),                            # }
        build('Rcy', 1056),                            # Р
        build('rcy', 1088),                            # р
        build('rdca', 10551),                          # ⤷
        build('rdldhar', 10601),                       # ⥩
        build('rdquor', 8221),                         # ”
        build('rdsh', 8627),                           # ↳
        build('Re', 8476),                             # ℜ
        build('realine', 8475),                        # ℛ
        build('realpart', 8476),                       # ℜ
        build('reals', 8477),                          # ℝ
        build('rect', 9645),                           # ▭
        build('REG', 174),                             # ®
        build('REG', 174),                             # ®
        build('ReverseElement', 8715),                 # ∋
        build('ReverseEquilibrium', 8651),             # ⇋
        build('ReverseUpEquilibrium', 10607),          # ⥯
        build('rfisht', 10621),                        # ⥽
        build('rfloor', 8971),                         # ⌋
        build('Rfr', 8476),                            # ℜ
        build('rfr', 120111),                          # 𝔯
        build('rHar', 10596),                          # ⥤
        build('rhard', 8641),                          # ⇁
        build('rharu', 8640),                          # ⇀
        build('rharul', 10604),                        # ⥬
        build('rhov', 1009),                           # ϱ
        build('RightAngleBracket', 10217),             # ⟩
        build('RightArrow', 8594),                     # →
        build('Rightarrow', 8658),                     # ⇒
        build('rightarrow', 8594),                     # →
        build('RightArrowBar', 8677),                  # ⇥
        build('RightArrowLeftArrow', 8644),            # ⇄
        build('rightarrowtail', 8611),                 # ↣
        build('RightCeiling', 8969),                   # ⌉
        build('RightDoubleBracket', 10215),            # ⟧
        build('RightDownTeeVector', 10589),            # ⥝
        build('RightDownVector', 8642),                # ⇂
        build('RightDownVectorBar', 10581),            # ⥕
        build('RightFloor', 8971),                     # ⌋
        build('rightharpoondown', 8641),               # ⇁
        build('rightharpoonup', 8640),                 # ⇀
        build('rightleftarrows', 8644),                # ⇄
        build('rightleftharpoons', 8652),              # ⇌
        build('rightrightarrows', 8649),               # ⇉
        build('rightsquigarrow', 8605),                # ↝
        build('RightTee', 8866),                       # ⊢
        build('RightTeeArrow', 8614),                  # ↦
        build('RightTeeVector', 10587),                # ⥛
        build('rightthreetimes', 8908),                # ⋌
        build('RightTriangle', 8883),                  # ⊳
        build('RightTriangleBar', 10704),              # ⧐
        build('RightTriangleEqual', 8885),             # ⊵
        build('RightUpDownVector', 10575),             # ⥏
        build('RightUpTeeVector', 10588),              # ⥜
        build('RightUpVector', 8638),                  # ↾
        build('RightUpVectorBar', 10580),              # ⥔
        build('RightVector', 8640),                    # ⇀
        build('RightVectorBar', 10579),                # ⥓
        build('ring', 730),                            # ˚
        build('risingdotseq', 8787),                   # ≓
        build('rlarr', 8644),                          # ⇄
        build('rlhar', 8652),                          # ⇌
        build('rmoust', 9137),                         # ⎱
        build('rmoustache', 9137),                     # ⎱
        build('rnmid', 10990),                         # ⫮
        build('roang', 10221),                         # ⟭
        build('roarr', 8702),                          # ⇾
        build('robrk', 10215),                         # ⟧
        build('ropar', 10630),                         # ⦆
        build('Ropf', 8477),                           # ℝ
        build('ropf', 120163),                         # 𝕣
        build('roplus', 10798),                        # ⨮
        build('rotimes', 10805),                       # ⨵
        build('RoundImplies', 10608),                  # ⥰
        build('rpar', 41),                             # )
        build('rpargt', 10644),                        # ⦔
        build('rppolint', 10770),                      # ⨒
        build('rrarr', 8649),                          # ⇉
        build('Rrightarrow', 8667),                    # ⇛
        build('Rscr', 8475),                           # ℛ
        build('rscr', 120007),                         # 𝓇
        build('Rsh', 8625),                            # ↱
        build('rsh', 8625),                            # ↱
        build('rsqb', 93),                             # ]
        build('rthree', 8908),                         # ⋌
        build('rtimes', 8906),                         # ⋊
        build('rtri', 9657),                           # ▹
        build('rtrie', 8885),                          # ⊵
        build('rtrif', 9656),                          # ▸
        build('rtriltri', 10702),                      # ⧎
        build('RuleDelayed', 10740),                   # ⧴
        build('ruluhar', 10600),                       # ⥨
        build('rx', 8478),                             # ℞
        build('Sacute', 346),                          # Ś
        build('sacute', 347),                          # ś
        build('Sc', 10940),                            # ⪼
        build('sc', 8827),                             # ≻
        build('scap', 10936),                          # ⪸
        build('sccue', 8829),                          # ≽
        build('scE', 10932),                           # ⪴
        build('sce', 10928),                           # ⪰
        build('Scedil', 350),                          # Ş
        build('scedil', 351),                          # ş
        build('Scirc', 348),                           # Ŝ
        build('scirc', 349),                           # ŝ
        build('scnap', 10938),                         # ⪺
        build('scnE', 10934),                          # ⪶
        build('scnsim', 8937),                         # ⋩
        build('scpolint', 10771),                      # ⨓
        build('scsim', 8831),                          # ≿
        build('Scy', 1057),                            # С
        build('scy', 1089),                            # с
        build('sdot', 8901),                           # ⋅
        build('sdotb', 8865),                          # ⊡
        build('sdote', 10854),                         # ⩦
        build('searhk', 10533),                        # ⤥
        build('seArr', 8664),                          # ⇘
        build('searr', 8600),                          # ↘
        build('searrow', 8600),                        # ↘
        build('semi', 59),                             # ;
        build('seswar', 10537),                        # ⤩
        build('setminus', 8726),                       # ∖
        build('setmn', 8726),                          # ∖
        build('sext', 10038),                          # ✶
        build('Sfr', 120086),                          # 𝔖
        build('sfr', 120112),                          # 𝔰
        build('sfrown', 8994),                         # ⌢
        build('sharp', 9839),                          # ♯
        build('SHCHcy', 1065),                         # Щ
        build('shchcy', 1097),                         # щ
        build('SHcy', 1064),                           # Ш
        build('shcy', 1096),                           # ш
        build('ShortDownArrow', 8595),                 # ↓
        build('ShortLeftArrow', 8592),                 # ←
        build('shortmid', 8739),                       # ∣
        build('shortparallel', 8741),                  # ∥
        build('ShortRightArrow', 8594),                # →
        build('ShortUpArrow', 8593),                   # ↑
        build('sim', 8764),                            # ∼
        build('simdot', 10858),                        # ⩪
        build('sime', 8771),                           # ≃
        build('simeq', 8771),                          # ≃
        build('simg', 10910),                          # ⪞
        build('simgE', 10912),                         # ⪠
        build('siml', 10909),                          # ⪝
        build('simlE', 10911),                         # ⪟
        build('simne', 8774),                          # ≆
        build('simplus', 10788),                       # ⨤
        build('simrarr', 10610),                       # ⥲
        build('slarr', 8592),                          # ←
        build('SmallCircle', 8728),                    # ∘
        build('smallsetminus', 8726),                  # ∖
        build('smashp', 10803),                        # ⨳
        build('smeparsl', 10724),                      # ⧤
        build('smid', 8739),                           # ∣
        build('smile', 8995),                          # ⌣
        build('smt', 10922),                           # ⪪
        build('smte', 10924),                          # ⪬
        build('smtes', '⪬︀'),                           # ⪬︀
        build('SOFTcy', 1068),                         # Ь
        build('softcy', 1100),                         # ь
        build('sol', 47),                              # /
        build('solb', 10692),                          # ⧄
        build('solbar', 9023),                         # ⌿
        build('Sopf', 120138),                         # 𝕊
        build('sopf', 120164),                         # 𝕤
        build('spadesuit', 9824),                      # ♠
        build('spar', 8741),                           # ∥
        build('sqcap', 8851),                          # ⊓
        build('sqcaps', '⊓︀'),                          # ⊓︀
        build('sqcup', 8852),                          # ⊔
        build('sqcups', '⊔︀'),                          # ⊔︀
        build('Sqrt', 8730),                           # √
        build('sqsub', 8847),                          # ⊏
        build('sqsube', 8849),                         # ⊑
        build('sqsubset', 8847),                       # ⊏
        build('sqsubseteq', 8849),                     # ⊑
        build('sqsup', 8848),                          # ⊐
        build('sqsupe', 8850),                         # ⊒
        build('sqsupset', 8848),                       # ⊐
        build('sqsupseteq', 8850),                     # ⊒
        build('squ', 9633),                            # □
        build('Square', 9633),                         # □
        build('square', 9633),                         # □
        build('SquareIntersection', 8851),             # ⊓
        build('SquareSubset', 8847),                   # ⊏
        build('SquareSubsetEqual', 8849),              # ⊑
        build('SquareSuperset', 8848),                 # ⊐
        build('SquareSupersetEqual', 8850),            # ⊒
        build('SquareUnion', 8852),                    # ⊔
        build('squarf', 9642),                         # ▪
        build('squf', 9642),                           # ▪
        build('srarr', 8594),                          # →
        build('Sscr', 119982),                         # 𝒮
        build('sscr', 120008),                         # 𝓈
        build('ssetmn', 8726),                         # ∖
        build('ssmile', 8995),                         # ⌣
        build('sstarf', 8902),                         # ⋆
        build('Star', 8902),                           # ⋆
        build('star', 9734),                           # ☆
        build('starf', 9733),                          # ★
        build('straightepsilon', 1013),                # ϵ
        build('straightphi', 981),                     # ϕ
        build('strns', 175),                           # ¯
        build('Sub', 8912),                            # ⋐
        build('sub', 8834),                            # ⊂
        build('subdot', 10941),                        # ⪽
        build('subE', 10949),                          # ⫅
        build('sube', 8838),                           # ⊆
        build('subedot', 10947),                       # ⫃
        build('submult', 10945),                       # ⫁
        build('subnE', 10955),                         # ⫋
        build('subne', 8842),                          # ⊊
        build('subplus', 10943),                       # ⪿
        build('subrarr', 10617),                       # ⥹
        build('Subset', 8912),                         # ⋐
        build('subset', 8834),                         # ⊂
        build('subseteq', 8838),                       # ⊆
        build('subseteqq', 10949),                     # ⫅
        build('SubsetEqual', 8838),                    # ⊆
        build('subsetneq', 8842),                      # ⊊
        build('subsetneqq', 10955),                    # ⫋
        build('subsim', 10951),                        # ⫇
        build('subsub', 10965),                        # ⫕
        build('subsup', 10963),                        # ⫓
        build('succ', 8827),                           # ≻
        build('succapprox', 10936),                    # ⪸
        build('succcurlyeq', 8829),                    # ≽
        build('Succeeds', 8827),                       # ≻
        build('SucceedsEqual', 10928),                 # ⪰
        build('SucceedsSlantEqual', 8829),             # ≽
        build('SucceedsTilde', 8831),                  # ≿
        build('succeq', 10928),                        # ⪰
        build('succnapprox', 10938),                   # ⪺
        build('succneqq', 10934),                      # ⪶
        build('succnsim', 8937),                       # ⋩
        build('succsim', 8831),                        # ≿
        build('SuchThat', 8715),                       # ∋
        build('Sum', 8721),                            # ∑
        build('sum', 8721),                            # ∑
        build('sung', 9834),                           # ♪
        build('Sup', 8913),                            # ⋑
        build('sup', 8835),                            # ⊃
        build('supdot', 10942),                        # ⪾
        build('supdsub', 10968),                       # ⫘
        build('supE', 10950),                          # ⫆
        build('supe', 8839),                           # ⊇
        build('supedot', 10948),                       # ⫄
        build('Superset', 8835),                       # ⊃
        build('SupersetEqual', 8839),                  # ⊇
        build('suphsol', 10185),                       # ⟉
        build('suphsub', 10967),                       # ⫗
        build('suplarr', 10619),                       # ⥻
        build('supmult', 10946),                       # ⫂
        build('supnE', 10956),                         # ⫌
        build('supne', 8843),                          # ⊋
        build('supplus', 10944),                       # ⫀
        build('Supset', 8913),                         # ⋑
        build('supset', 8835),                         # ⊃
        build('supseteq', 8839),                       # ⊇
        build('supseteqq', 10950),                     # ⫆
        build('supsetneq', 8843),                      # ⊋
        build('supsetneqq', 10956),                    # ⫌
        build('supsim', 10952),                        # ⫈
        build('supsub', 10964),                        # ⫔
        build('supsup', 10966),                        # ⫖
        build('swarhk', 10534),                        # ⤦
        build('swArr', 8665),                          # ⇙
        build('swarr', 8601),                          # ↙
        build('swarrow', 8601),                        # ↙
        build('swnwar', 10538),                        # ⤪
        build('Tab', 9),                               # 	
        build('target', 8982),                         # ⌖
        build('tbrk', 9140),                           # ⎴
        build('Tcaron', 356),                          # Ť
        build('tcaron', 357),                          # ť
        build('Tcedil', 354),                          # Ţ
        build('tcedil', 355),                          # ţ
        build('Tcy', 1058),                            # Т
        build('tcy', 1090),                            # т
        build('tdot', 8411),                           #⃛ 
        build('telrec', 8981),                         # ⌕
        build('Tfr', 120087),                          # 𝔗
        build('tfr', 120113),                          # 𝔱
        build('there4', 8756),                         # ∴
        build('Therefore', 8756),                      # ∴
        build('therefore', 8756),                      # ∴
        build('thetasym', 977),                        # ϑ
        build('thickapprox', 8776),                    # ≈
        build('thicksim', 8764),                       # ∼
        build('ThickSpace', '  '),                     #   
        build('ThinSpace', 8201),                      #  
        build('thkap', 8776),                          # ≈
        build('thksim', 8764),                         # ∼
        build('Tilde', 8764),                          # ∼
        build('TildeEqual', 8771),                     # ≃
        build('TildeFullEqual', 8773),                 # ≅
        build('TildeTilde', 8776),                     # ≈
        build('timesb', 8864),                         # ⊠
        build('timesbar', 10801),                      # ⨱
        build('timesd', 10800),                        # ⨰
        build('tint', 8749),                           # ∭
        build('toea', 10536),                          # ⤨
        build('top', 8868),                            # ⊤
        build('topbot', 9014),                         # ⌶
        build('topcir', 10993),                        # ⫱
        build('Topf', 120139),                         # 𝕋
        build('topf', 120165),                         # 𝕥
        build('topfork', 10970),                       # ⫚
        build('tosa', 10537),                          # ⤩
        build('tprime', 8244),                         # ‴
        build('TRADE', 8482),                          # ™
        build('triangle', 9653),                       # ▵
        build('triangledown', 9663),                   # ▿
        build('triangleleft', 9667),                   # ◃
        build('trianglelefteq', 8884),                 # ⊴
        build('triangleq', 8796),                      # ≜
        build('triangleright', 9657),                  # ▹
        build('trianglerighteq', 8885),                # ⊵
        build('tridot', 9708),                         # ◬
        build('trie', 8796),                           # ≜
        build('triminus', 10810),                      # ⨺
        build('TripleDot', 8411),                      #⃛ 
        build('triplus', 10809),                       # ⨹
        build('trisb', 10701),                         # ⧍
        build('tritime', 10811),                       # ⨻
        build('trpezium', 9186),                       # ⏢
        build('Tscr', 119983),                         # 𝒯
        build('tscr', 120009),                         # 𝓉
        build('TScy', 1062),                           # Ц
        build('tscy', 1094),                           # ц
        build('TSHcy', 1035),                          # Ћ
        build('tshcy', 1115),                          # ћ
        build('Tstrok', 358),                          # Ŧ
        build('tstrok', 359),                          # ŧ
        build('twixt', 8812),                          # ≬
        build('twoheadleftarrow', 8606),               # ↞
        build('twoheadrightarrow', 8608),              # ↠
        build('Uarr', 8607),                           # ↟
        build('uArr', 8657),                           # ⇑
        build('uarr', 8593),                           # ↑
        build('Uarrocir', 10569),                      # ⥉
        build('Ubrcy', 1038),                          # Ў
        build('ubrcy', 1118),                          # ў
        build('Ubreve', 364),                          # Ŭ
        build('ubreve', 365),                          # ŭ
        build('Ucy', 1059),                            # У
        build('ucy', 1091),                            # у
        build('udarr', 8645),                          # ⇅
        build('Udblac', 368),                          # Ű
        build('udblac', 369),                          # ű
        build('udhar', 10606),                         # ⥮
        build('ufisht', 10622),                        # ⥾
        build('Ufr', 120088),                          # 𝔘
        build('ufr', 120114),                          # 𝔲
        build('uHar', 10595),                          # ⥣
        build('uharl', 8639),                          # ↿
        build('uharr', 8638),                          # ↾
        build('uhblk', 9600),                          # ▀
        build('ulcorn', 8988),                         # ⌜
        build('ulcorner', 8988),                       # ⌜
        build('ulcrop', 8975),                         # ⌏
        build('ultri', 9720),                          # ◸
        build('Umacr', 362),                           # Ū
        build('umacr', 363),                           # ū
        build('UnderBar', 95),                         # _
        build('UnderBrace', 9183),                     # ⏟
        build('UnderBracket', 9141),                   # ⎵
        build('UnderParenthesis', 9181),               # ⏝
        build('Union', 8899),                          # ⋃
        build('UnionPlus', 8846),                      # ⊎
        build('Uogon', 370),                           # Ų
        build('uogon', 371),                           # ų
        build('Uopf', 120140),                         # 𝕌
        build('uopf', 120166),                         # 𝕦
        build('UpArrow', 8593),                        # ↑
        build('Uparrow', 8657),                        # ⇑
        build('uparrow', 8593),                        # ↑
        build('UpArrowBar', 10514),                    # ⤒
        build('UpArrowDownArrow', 8645),               # ⇅
        build('UpDownArrow', 8597),                    # ↕
        build('Updownarrow', 8661),                    # ⇕
        build('updownarrow', 8597),                    # ↕
        build('UpEquilibrium', 10606),                 # ⥮
        build('upharpoonleft', 8639),                  # ↿
        build('upharpoonright', 8638),                 # ↾
        build('uplus', 8846),                          # ⊎
        build('UpperLeftArrow', 8598),                 # ↖
        build('UpperRightArrow', 8599),                # ↗
        build('Upsi', 978),                            # ϒ
        build('upsilon', 965),                         # υ
        build('UpTee', 8869),                          # ⊥
        build('UpTeeArrow', 8613),                     # ↥
        build('upuparrows', 8648),                     # ⇈
        build('urcorn', 8989),                         # ⌝
        build('urcorner', 8989),                       # ⌝
        build('urcrop', 8974),                         # ⌎
        build('Uring', 366),                           # Ů
        build('uring', 367),                           # ů
        build('urtri', 9721),                          # ◹
        build('Uscr', 119984),                         # 𝒰
        build('uscr', 120010),                         # 𝓊
        build('utdot', 8944),                          # ⋰
        build('Utilde', 360),                          # Ũ
        build('utilde', 361),                          # ũ
        build('utri', 9653),                           # ▵
        build('utrif', 9652),                          # ▴
        build('uuarr', 8648),                          # ⇈
        build('uwangle', 10663),                       # ⦧
        build('vangrt', 10652),                        # ⦜
        build('varepsilon', 1013),                     # ϵ
        build('varkappa', 1008),                       # ϰ
        build('varnothing', 8709),                     # ∅
        build('varphi', 981),                          # ϕ
        build('varpi', 982),                           # ϖ
        build('varpropto', 8733),                      # ∝
        build('vArr', 8661),                           # ⇕
        build('varr', 8597),                           # ↕
        build('varrho', 1009),                         # ϱ
        build('varsigma', 962),                        # ς
        build('varsubsetneq', '⊊︀'),                    # ⊊︀
        build('varsubsetneqq', '⫋︀'),                   # ⫋︀
        build('varsupsetneq', '⊋︀'),                    # ⊋︀
        build('varsupsetneqq', '⫌︀'),                   # ⫌︀
        build('vartheta', 977),                        # ϑ
        build('vartriangleleft', 8882),                # ⊲
        build('vartriangleright', 8883),               # ⊳
        build('Vbar', 10987),                          # ⫫
        build('vBar', 10984),                          # ⫨
        build('vBarv', 10985),                         # ⫩
        build('Vcy', 1042),                            # В
        build('vcy', 1074),                            # в
        build('VDash', 8875),                          # ⊫
        build('Vdash', 8873),                          # ⊩
        build('vDash', 8872),                          # ⊨
        build('vdash', 8866),                          # ⊢
        build('Vdashl', 10982),                        # ⫦
        build('Vee', 8897),                            # ⋁
        build('vee', 8744),                            # ∨
        build('veebar', 8891),                         # ⊻
        build('veeeq', 8794),                          # ≚
        build('vellip', 8942),                         # ⋮
        build('Verbar', 8214),                         # ‖
        build('verbar', 124),                          # |
        build('Vert', 8214),                           # ‖
        build('vert', 124),                            # |
        build('VerticalBar', 8739),                    # ∣
        build('VerticalLine', 124),                    # |
        build('VerticalSeparator', 10072),             # ❘
        build('VerticalTilde', 8768),                  # ≀
        build('VeryThinSpace', 8202),                  #  
        build('Vfr', 120089),                          # 𝔙
        build('vfr', 120115),                          # 𝔳
        build('vltri', 8882),                          # ⊲
        build('vnsub', '⊂⃒'),                           # ⊂⃒
        build('vnsup', '⊃⃒'),                           # ⊃⃒
        build('Vopf', 120141),                         # 𝕍
        build('vopf', 120167),                         # 𝕧
        build('vprop', 8733),                          # ∝
        build('vrtri', 8883),                          # ⊳
        build('Vscr', 119985),                         # 𝒱
        build('vscr', 120011),                         # 𝓋
        build('vsubnE', '⫋︀'),                          # ⫋︀
        build('vsubne', '⊊︀'),                          # ⊊︀
        build('vsupnE', '⫌︀'),                          # ⫌︀
        build('vsupne', '⊋︀'),                          # ⊋︀
        build('Vvdash', 8874),                         # ⊪
        build('vzigzag', 10650),                       # ⦚
        build('Wcirc', 372),                           # Ŵ
        build('wcirc', 373),                           # ŵ
        build('wedbar', 10847),                        # ⩟
        build('Wedge', 8896),                          # ⋀
        build('wedge', 8743),                          # ∧
        build('wedgeq', 8793),                         # ≙
        build('Wfr', 120090),                          # 𝔚
        build('wfr', 120116),                          # 𝔴
        build('Wopf', 120142),                         # 𝕎
        build('wopf', 120168),                         # 𝕨
        build('wp', 8472),                             # ℘
        build('wr', 8768),                             # ≀
        build('wreath', 8768),                         # ≀
        build('Wscr', 119986),                         # 𝒲
        build('wscr', 120012),                         # 𝓌
        build('xcap', 8898),                           # ⋂
        build('xcirc', 9711),                          # ◯
        build('xcup', 8899),                           # ⋃
        build('xdtri', 9661),                          # ▽
        build('Xfr', 120091),                          # 𝔛
        build('xfr', 120117),                          # 𝔵
        build('xhArr', 10234),                         # ⟺
        build('xharr', 10231),                         # ⟷
        build('xlArr', 10232),                         # ⟸
        build('xlarr', 10229),                         # ⟵
        build('xmap', 10236),                          # ⟼
        build('xnis', 8955),                           # ⋻
        build('xodot', 10752),                         # ⨀
        build('Xopf', 120143),                         # 𝕏
        build('xopf', 120169),                         # 𝕩
        build('xoplus', 10753),                        # ⨁
        build('xotime', 10754),                        # ⨂
        build('xrArr', 10233),                         # ⟹
        build('xrarr', 10230),                         # ⟶
        build('Xscr', 119987),                         # 𝒳
        build('xscr', 120013),                         # 𝓍
        build('xsqcup', 10758),                        # ⨆
        build('xuplus', 10756),                        # ⨄
        build('xutri', 9651),                          # △
        build('xvee', 8897),                           # ⋁
        build('xwedge', 8896),                         # ⋀
        build('YAcy', 1071),                           # Я
        build('yacy', 1103),                           # я
        build('Ycirc', 374),                           # Ŷ
        build('ycirc', 375),                           # ŷ
        build('Ycy', 1067),                            # Ы
        build('ycy', 1099),                            # ы
        build('Yfr', 120092),                          # 𝔜
        build('yfr', 120118),                          # 𝔶
        build('YIcy', 1031),                           # Ї
        build('yicy', 1111),                           # ї
        build('Yopf', 120144),                         # 𝕐
        build('yopf', 120170),                         # 𝕪
        build('Yscr', 119988),                         # 𝒴
        build('yscr', 120014),                         # 𝓎
        build('YUcy', 1070),                           # Ю
        build('yucy', 1102),                           # ю
        build('Zacute', 377),                          # Ź
        build('zacute', 378),                          # ź
        build('Zcaron', 381),                          # Ž
        build('zcaron', 382),                          # ž
        build('Zcy', 1047),                            # З
        build('zcy', 1079),                            # з
        build('Zdot', 379),                            # Ż
        build('zdot', 380),                            # ż
        build('zeetrf', 8488),                         # ℨ
        build('ZeroWidthSpace', 8203),                 # ​
        build('Zfr', 8488),                            # ℨ
        build('zfr', 120119),                          # 𝔷
        build('ZHcy', 1046),                           # Ж
        build('zhcy', 1078),                           # ж
        build('zigrarr', 8669),                        # ⇝
        build('Zopf', 8484),                           # ℤ
        build('zopf', 120171),                         # 𝕫
        build('Zscr', 119989),                         # 𝒵
        build('zscr', 120015),                         # 𝓏
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
            print(f"build('{k}', {c}),     # {v}")
        else:
            print(f"build('{v}', '{k}'),   # {v}")
