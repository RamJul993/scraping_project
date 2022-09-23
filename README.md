# scraping_project
Pour commencer il est obligatoire d'avoir python >= 3.4 et installer BeautifulSoup

lelscan.py prend en argument 2 paramètres:
    *Première paramètre Obligatoire, il s'agit d'url du chapitre qu'on veut scrapter
        Exemple: lelscan.py https://lelscans.net/scan-one-piece/1053
        
    *Second paramètre, il s'agit de l'emplacement (C, D, E, F,...):
       Exemple: lelscan.py https://lelscans.net/scan-one-piece/1053 C
    
    Par défaut il va stocker dans D:\lelscans.net\titre_scan\num_chapitre
 
 
 
subscene.py prend en argument 3 paramètres:
    *Première paramètre Obligatoire, il s'agit d'url de la page du serie/drama/film/... dont on veut récuperé le sous-titre
        Exemple: subscene.py https://subscene.com/subtitles/doctors-dakteoseu-tv-2016-4
        
    *Second paramètre, il s'agit de la langue qu'on veut récupére (en minuscule):
        -french : français
        -english : anglais
        -arabic : arabe
        -spanish : espagnol
        ...
        ...(voir sur le site de subscene)
        Exemple: subscene.py https://subscene.com/subtitles/doctors-dakteoseu-tv-2016-4 english
    
    *Troisième et dernière paramètre, il s'agit de l'emplacement (C, D, E, F,...):
       Exemple: subscene.py https://subscene.com/subtitles/doctors-dakteoseu-tv-2016-4 english
    
    Par défaut il va telecharger les sous-titres en version french et le stocker dans D:\subscene.com\titre_drama\langue_choisis
