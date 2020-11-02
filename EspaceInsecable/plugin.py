#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os, re

from Common import *

# main routine
def run(bk):
	
	# iterate over all html files
	for html_id, href in bk.text_iter():
		
		print('Fichier en cour de traitement : ' + os.path.basename(href));
		# read orignal html code from file
		text = bk.readfile(html_id);
		
		text = CleanBasic(text);
		
		text = Traitement(text);
		
		text = CleanBasic(text);
		
		# write modified html code to file
		bk.writefile(html_id, text);
	
	print('');
	print('Traitement des espaces insécables terminer.');
	
	return 0

## Specifique

def Traitement(text):
	
	
	body = RegexSearch(r'<body[^>]*>.*</body>', text).group(0);
	
	# espace fine insécable
	body = RegexLoop(r'&#x202F;', '&#8239;', body);
	body = RegexLoop('\u202F', '&#8239;', body);
	
	
	#supprimé les paragraphe vide
	body = RegexLoop(r'(<(p|h\d)(?:| [^>]*)>)(?:\s*(?:<(?:i|b|em|strong|span)(?:| [^>]*)>)*\s*(?:</(?:i|b|em|strong|span)>)*\s*)*(</\2>)', r'', body);
	
	 #supprime les retour a la ligne dans un paragraphe
	body = RegexLoop(r'(<(p|h\d)(?:| [^>]*)>)\s+', r'\1', body);
	body = RegexLoop(r'\s+(</(p|h\d)>)', r'\1', body);
	body = RegexLoop(r'(<(p|h\d)(?:| [^>]*)>(?:.(?!</\2>))*?)(?:\s{2,}|\t)', r'\1 ', body);
	
	# supprime l'espace insécable en fin de paragraphe
	body = RegexLoop(r'(?:\s|&#160;|&#8239;)*((?:</(?:i|b|em|strong|span)>)*)(?:\s|&#160;|&#8239;)+</p>', r'\1</p>', body);
	body = RegexLoop(r'(?:\s|&#160;|&#8239;)+((?:</(?:i|b|em|strong|span)>)*)(?:\s|&#160;|&#8239;)*</p>', r'\1</p>', body);
	
	# supprime les espaces insécable en début de paragraphe
	emptyPara = r'(<(p|h\d)(?:| [^>]*)>)(?:(?:\s|&#160;|&#8239;|<br[^>]*/>){2,}(?:<(?:i|b|em|strong|span)(?:| [^>]*)>)*(?:\s|&#160;|&#8239;|<br[^>]*/>){2,}(?:</(?:i|b|em|strong|span)>)*(?:\s|&#160;|&#8239;|<br[^>]*/>){2,})';
	body = RegexSimple(emptyPara, r'\1', body);
	
	# remplace les paragraphe de br et d'espaces insécable
	emptyPara = r'(<(p|h\d)(?:| [^>]*)>)(?:(?:\s|&#160;|&#8239;|<br[^>]*/>)*(?:<(?:i|b|em|strong|span)(?:| [^>]*)>)*(?:\s|&#160;|&#8239;|<br[^>]*/>)*(?:</(?:i|b|em|strong|span)>)*(?:\s|&#160;|&#8239;|<br[^>]*/>)*)*(</\2>)';
	body = RegexSimple(emptyPara, r'\1&#160;\3', body);
	
	# supprime les espace en fin de body
	body = RegexLoop(r'(\s*<p(| [^>]*)>&#160;</p>)+(\s*</div>)?\s*</body>', r'\3\n</body>', body);
	
	#supprime les espaces insécable et balise br en fin de paragraphe (sauf si s'est le dernier)
	body = RegexLoop(r'([^>])(?:&#160;|&#8239;|<br[^>]*/>)+(</(p|h\d)>)', r'\1\2', body);
	body = RegexLoop(r'(?:(</(?:i|b|em|strong|span)>)(?:&#160;|&#8239;)+|<br[^>]*/>)+(</(p|h\d)>)', r'\1\2', body);
	
	# remplace les tiret cadratin invalide
	body = RegexSimple(r'<p(| [^>]*)>((?:<(?:i|b|em|strong|span)(?:| [^>]*)>)*)(?:–|-|—|_|~||⎯)((?:<(?:i|b|em|strong|span)(?:| [^>]*)>)*)(?:\s|&#160;|&#8239;){0,}', r'<p\1>\2—&#160;\3', body);
	body = RegexLoop(r'<p(| [^>]*)>((?:<(?:i|b|em|strong|span)(?:| [^>]*)>)*)(?:–|-|_|~||⎯)((?:<(?:i|b|em|strong|span)(?:| [^>]*)>)*)(?:\s|&#160;|&#8239;){0,}', r'<p\1>\2—&#160;\3', body);
	# supprime les espace en doubles
	body = RegexLoop(r'<p(| [^>]*)>((?:<(?:i|b|em|strong|span)(?:| [^>]*)>)*)—((?:<(?:i|b|em|strong|span)(?:| [^>]*)>)*)(?:\s|&#160;|&#8239;){2,}', r'<p\1>\2—&#160;\3', body);
	# supprime les espace en doubles
	body = RegexSimple(r'<p(| [^>]*)>((?:<(?:i|b|em|strong|span)(?:| [^>]*)>)*)—((?:<(?:i|b|em|strong|span)(?:| [^>]*)>)*)(?:\s|&#160;|&#8239;){1,}', r'<p\1>\2—&#160;\3', body);
	# supprime les espace en doubles mal placé
	body = RegexLoop(r'<p(| [^>]*)>—(?:&#160;|&#8239;)((?:<(?:i|b|em|strong|span)(?:| [^>]*)>)*)(?:\s|&#160;|&#8239;){1,}', r'<p\1>—&#160;\2', body);
	
	
	# remplace les apostrophes droit dans le texte
	body = RegexLoop(r">([^<]*)'([^<]*)<", r'>\1’\2<', body);
	# les espaces devant et derriére les apostrophes
	body = RegexLoop(r'\s+’|’\s+', r'’', body);
	
	
	# met l'espace insécable pour les quillement ouvrant
	body = RegexSimple(r'«(?:\s|&#160;|&#8239;)*((?:<(?:i|b|em|strong|span)(?:| [^>]*)>)*)(?:\s|&#160;|&#8239;)*', r'«&#8239;\1', body);
	# met l'espace insécable pour les quillement ouvrant
	body = RegexSimple(r'(?:\s|&#160;|&#8239;)*((?:</(?:i|b|em|strong|span)>)*)(?:\s|&#160;|&#8239;)*»', r'\1&#8239;»', body);
	
	# supprime les espace en doubles mal placé
	body = RegexSimple(r'<p(| [^>]*)>(?:\s|&#160;|&#8239;){0,}»(?:\s|&#160;){0,}', r'<p\1>»&#160;', body);
	
	
	# met l'espace insécable pour les point d'exclamation
	body = RegexSimple(r'(?:\s|&#160;|&#8239;)*((?:</(?:i|b|em|strong|span)>)*)(?:\s|&#160;|&#8239;)*!((?:</(?:i|b|em|strong|span)>)*)', r'\1&#8239;!\2', body);
	# corrige les erreur XML
	body = RegexSimple(r'<(&#160;|&#8239;)+!', r'<!', body)
	body = RegexSimple(r'(&#160;|&#8239;)+!>', r'!>', body);
	
	
	# met l'espace insécable pour les point d'intérogation
	body = RegexSimple(r'(?:\s|&#160;|&#8239;)*((?:</(?:i|b|em|strong|span)>)*)(?:\s|&#160;|&#8239;)*\?((?:</(?:i|b|em|strong|span)>)*)', r'\1&#8239;?\2', body);
	# corrige les erreur XML
	body = RegexSimple(r'<(&#160;|&#8239;)+\?', r'<?', body)
	body = RegexSimple(r'(&#160;|&#8239;)+\?>', r'?>', body);
	
	# supprime les espace entre les ponctuations
	body = RegexLoop(r'(\?|!)(\s|&#160;|&#8239;)+(\?|!)', r'\1\3', body);
	
	# met l'espace insécable pour les deux-point
	body = RegexSimple(r'(?:\s|&#160;|&#8239;)*((?:</(?:i|b|em|strong|span)>)*)(?:\s|&#160;|&#8239;)*:((?:</(?:i|b|em|strong|span)>)*)', r'\1&#160;:\2', body);
	# supprime les espace pour les heures
	body = RegexLoop(r'(\d)(?:\s|&#160;|&#8239;)+:(?:\s|&#160;|&#8239;)*(\d)', r'\1:\2', body);
	# supprime les espace pour grand nombre
	body = RegexLoop(r'(>[^<]*?\d+)\s+(\d{3,}[^<]*?<)', r'\1&#8239;\2', body);
	# supprime les espace pour les url
	body = RegexLoop(r'https?(&#160;|&#8239;):', r'http:', body);
	# corrige les erreur XML
	body = RegexLoop(r'(<(?:[^>]+)\s+(?:[^>]*))&#160;:([^>]*>)', r'\1:\2', body);
	
	# espace insécable pour les point-virgule
	body = RegexSimple('&([^\\s;\b]*);', '&\\1\b', body); #échapement des entités
	body = RegexSimple('(&#160\b|&#8239\b|\\s){0,};', '&#8239\b;', body); #met l'espace insécable pour les point-virgule et supprime les espace en doubles
	body = RegexSimple('&([^\\s;\b]*)\b', '&\\1;', body); #rétablit les entités
	# corrige les erreur XML
	body = RegexLoop(r'(<(?:[^>]+)\s+(?:[^>]*))&#8239;;([^>]*>)', r'\1;\2', body);
	
	# espace fine insécable
	body = RegexLoop(r'(&#x202F;|&#8239;)', '\u202F', body);
	
	return RegexSimple(r'<body[^>]*>.*</body>', body, text);


def main():
	print("I reached main when I should not have\n");
	return -1;

if __name__ == "__main__":
	sys.exit(main())