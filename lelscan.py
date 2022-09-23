from pathlib import Path
from bs4 import BeautifulSoup
import requests
import sys




argument = sys.argv
repetition = 0
EN_TETE = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0"}




def recup_navigation_page(url_, element_cible, attribut_element, valeur_attribut):
    """Cette fonction a pour but d'initialiser la requête afin de recupéré que les balises conteneur des liens des chapitre sur la page
    actuel ainsi que du lien du chapitre suivant.

    Args:
        url_ (chaine de caractère): Il s'agit d'URL de la page où on souhaite récupere le liens exemple: https://lelscans.net/scan-one-piece/1052
        element_cible (chaine de caractère): Ce paramètre correspond au balise qu'on souhaite ciblé (div, a, td, ...)
        attribut_element (chaine de caractère): Comme son nom l'indique, il s'agit de l'attribut du balise qu'on cible, ça peut être un id ou class
        valeur_attribut (chaine de caractère): valeur de l'attribut qu'on souhaite atteindre

    Returns:
        list: list contenant des objets de type BeautifulSoup, c'est sur cette valeur qu'on va pouvoir faire des recherche un peut plus poussé
    """
    requete = requests.get(url_, headers=EN_TETE)
    
    if requete.status_code != 200 :
        print(f"ERREUR HTTP {requete.status_code}")
        sys.exit()

    soup = BeautifulSoup(requete.content, "html.parser")

    balise_cible = soup.find_all(element_cible, {attribut_element: valeur_attribut})
   
    return balise_cible




def filtre_navigation_page(navigation_page):
    """Cette fonction a pour but de les informations relative concernant le chapitre qu'on lie actuellement.


    Args:
        navigation_page (liste): Cette paramètre est issu du resultat de la fonction recup_navigation_page, de ce fait elle contiendra
        tous les liens vers les pages du chapitre actuel mais il va aussi contenir le liens du chapitre suivant. Cependant,
        il y'aura des doublant d'où :  navigation_page_clean = list(set(navigation_page_clean))

    Returns:
        dictionaire: Ce dernier, contiendra plusieurs informations utile :
                                                                                *navigation_page_actuel (liste): qui contient tous les liens des chapitres de la page actuel
                                                                                *lien_prochain_chapitre: contenant le liens vers le chapitre suivant
                                                                                *titre pour recupéré le titre du scan 
                                                                                *Et enfin chapitre_actuel qui contiendra le numéro du chapitre qu'on est en train de lire
    """
    navigation_page_clean = []

    info_page = {"navigation_page_actuel": [], "lien_prochain_chapitre": "", "titre": "", "chapitre_actuel": ""}

    for i in navigation_page:
        liens = i.find_all("a")
        for lien in liens:
            lnk = lien.attrs["href"]
            navigation_page_clean.append(lnk)

    navigation_page_clean = list(set(navigation_page_clean))

    """On va boucler sur navigation_page_clean qui contient tous les liens SANS DOUBLANT dont on a besoin (liens pour tous les pages + liens vers le chapitre précédent)
       pour chaque liens on split puis on vérifier la longueur de l'avant dernière élément pour savoir s'il s'agit d'un liens pour un page de chapitre
       ou d'un lien vers la page suivant.
       
       EXEMPLE:: 
                    Pour un lien de chapitre:   https://lelscans.net/scan-one-piece/1052/15 
                                                
                                                 lnk[-2] = 1052 & str(lnk[-2]) = 4 donc on peut utilisé ça pour déterminé si c'est bien un
                                                 lien d'une page ou du chapitre suivant.
                    
                    Pour un lien de chapitre: https://lelscans.net/scan-one-piece/1052
                                              
                                               lnk[-2] = scan-one-piece & str(lnk[-2]) = 14 

                    A partir de ces informations on peut déterminé le type du lien on fonction de la longueur de lnk[-2]

    Ainsi donc si la longueur est supérieur à 4, alors on déduit qu'il s'agit du lien du prochain chapitre.            
    """

    for lien in navigation_page_clean:
        lnk = str(lien).split("/")
        
        if len(str(lnk[-2])) > 4:
            info_page["lien_prochain_chapitre"] = str(lien)
            info_page["titre"] = str(lnk[-2])

        else:
            if not info_page["chapitre_actuel"]:
                info_page["chapitre_actuel"] = str(lnk[-2])

            info_page["navigation_page_actuel"].append(lien)
    
    return info_page




def telechargement(url_, info_page, emplacement, rep=repetition):
    """Il s'agit d'un fonction recursive qui ne s'arrête qu'après avoir télécharger tous les chapitres à partir d'url du chapitre envoyer en argument


    Args:
        url_ (chaine de carractère): Liens vers la page de la chapitre dont on souhaite telecharger
        info_page (dictionaire): Ce dernier contiendra (presque) tous les informations dont on a besoin, 
                                 afin de créer les dossier correspondant aux scans et par la suite les telecharger
        emplacement (chaine de carractère): Il s'agit tous simplement de l'endroit où on veut stocker nos telechargement (C, D, E, F, ...)
        rep (entier, obligatoire): Cette paramètre servira de condition d'arrêt pour la recursivité, en effet une fois qu'on a commencer
                                   le telechargement des images de la dernières chapitres dispo, rep aura un valeur de -1, donc on arrete 
                                   la recursivité à ce moment là
    """

    """titre: contiendra le titre du scan qu'on veut telecharger, par exemple Black Clover
       recup_titre: servira à récupéré une liste qui contiendra le titre. On va d'ailleurs travailler sur recup_titre pour avoir
                    ce fammeux titre
       dernier_chap_dispo_: Contiendra l'url de la dernier chapitre actuellement disponible
    """
    titre = ""
    recup_titre = ""
    dernier_chap_dispo_ = ""


    """On commence par vérifier si on est à la dernière chapitre disponible ou pas:
        *Si c'est le cas alors on va jouer avec la première élèment contenu dans info_page["navigation_page_actuel"][0].
         Puis on split et on exclu la dernière élement qui réprésente le numéro de la page du chapitre: ["https:/", "lelscan.net", "scan-one-piece", "1000"]
         Ensuite on stock la valeur qui nous interesse(qui contient le titre) dans la varible tmp_titre.
         Cette valeur à ce moment là sera de la forme: scan-one-piece Or ce qu'on veut c'est One Piece
         C'est pour cela qu'on split sur tmp_titre et on stock le resultat dans recup_titre afin d'y travailler plus tard: ["scan", "one", "piece"]
         Maintenant, on va faire un join sur info_page["navigation_page_actuel"][0] qu'on a split et dont on a exclu le dernier élement plus haut: https:/lelscan.net/scan-one-piece/1000

      Et si on est pas à la dernière chapitre disponible alors on va tous simplement split sur info_page["titre"], puis stocker le résultat dans recup_titre afin d'avoir les élément dont on aura besoin.

      Après tous cela, on boucle sur recup_titre et on fait un if afin de vérifier si l'élement actul ne vaut pas "scan" :
        si c'est condition est vrai alors : 
                                            1- on applique capitalize à l'element actuel (qui est réprésenté par i) de la boucle afin de 
                                               mettre la première lettre en majuscule car on veut avoir: OnePiece et non onepiece
                                            2- on le concataine avec un espace pour avoir l'espace entre One et Piece par exemple: One Piece
                                            3- Enfin on concataine le tous avec la variable titre (ligne numéro 128)

      Efin après la boucle on élimite l'espace à la fin de la variable titre grace à strip.
    """
    if not info_page["lien_prochain_chapitre"]:   
        dernier_chap_dispo = [i for i in str(info_page["navigation_page_actuel"][0]).split("/")]
        dernier_chap_dispo = dernier_chap_dispo[:-1]
        tmp_titre = dernier_chap_dispo[-2]
        recup_titre = str(tmp_titre).split("-")
        dernier_chap_dispo_ = "/".join(dernier_chap_dispo)
        
    else:
            recup_titre = str(info_page["titre"]).split("-")
    

    for i in recup_titre:
        if i != "scan":
            titre += i.capitalize() + " "

    titre = str(titre).strip(" ")


    """On crée les dossiers pour acceullir le telechargement
    """
    emplacement_ = emplacement + ":\\"
    chemin_telechargement = Path(emplacement_)
    chemin_telechargement = chemin_telechargement / "lelscans.net" / titre / info_page["chapitre_actuel"]
    chemin_telechargement.mkdir(parents=True,exist_ok=True)


    """Pour chaque liens présent dans info_page["navigation_page_actuel"]:
            *On le split afin de recupéré le numero de la page actuel, ce numero de page sera le dernier élement du resultat du split d'où le -1
             On sauvegardera ce résultat dans num_page

             *Ensuite on appelle la fonction recup_navigation_page afin de récuperer la balise contenant le lien de l'image
                petit problème: pour les pages 1 jusqu'à l'avant dernière chapitre, l'attribut alt de la balise img aura la valeur "Lecture en ligne..."
                                Et pour la dernière page, cette valeur sera "lecture en ligne..."
              D'où le "if not recup_lien_img".
              
              *Après pour chaque element dans recup_lien_img, recuperera la valeur de l'attribut "src" puis on le concataine avec https://lelscan.net
               afin d'obtenir l'url complet du telechargement de l'image

              *Enfin on fait un get avec notre url complet suivis d'un open afin de telecharger l'image


    """
    print("\n\nDEBUT TELECHARGEMENT DU CHAPITRE {}".format(info_page["chapitre_actuel"]))

    for lien_navigation in info_page["navigation_page_actuel"]:
        recup_num_page = str(lien_navigation).split("/")
        num_page = recup_num_page[-1]
        
        recup_lien_img = recup_navigation_page(lien_navigation, "img", "alt", "Lecture en ligne {titre_} {chap_actuel} page {page_actuel}".format(titre_=titre, chap_actuel=info_page["chapitre_actuel"], page_actuel=num_page))

        if not recup_lien_img:
             recup_lien_img = recup_navigation_page(lien_navigation, "img", "alt", "lecture en ligne {titre_} {chap_actuel} page {page_actuel}".format(titre_=titre, chap_actuel=info_page["chapitre_actuel"], page_actuel=num_page))

        for elm in recup_lien_img:
            lien_image = "https://lelscans.net"+str(elm.attrs["src"])

            telechargement_chapitre = requests.get(lien_image)

            with open(str(chemin_telechargement)+"\\"+str(num_page)+".jpg", "wb") as download_:
                print("\t\t\t\t\tTELECHARGEMENT DE LA PAGE {} ".format(num_page))
                download_.write(telechargement_chapitre.content)

    print("\n\nTELECHARGEMENT DU CHAPITRE {} TERMINE".format(info_page["chapitre_actuel"]))

    """On vérifie que repetition est égal à -1, cela veut dire qu'on a telecharger le dernier chapitre dispo si c'est le cas.
       Donc y'a plus rien à telecharger, d'où le sys.exit()

       *On vérifie que info_page["lien_prohain_chapitre"] n'est pas vide, c'est à dire qu'on est pas encore à la dernière chapitre:
            Si c'est le cas alors on rappelle la fonction telechargement on lui donnant le lien du prochain chapitre comme url
            
            Si ce n'est pas le cas alors on commence par change la valeur de repetition à -1 . Puis on appelle la fonction telechargement
            on lui donnant cette fois-ci dernier_chap_dispo en guise d'url.
    """
    if rep == -1:
        print("TELECHARGEMENT TERMINE")
        sys.exit()

    if info_page["lien_prochain_chapitre"]: 
        return telechargement(info_page["lien_prochain_chapitre"], filtre_navigation_page(recup_navigation_page(info_page["lien_prochain_chapitre"], "div", "id", "navigation")), "D", rep)
   
    else:
        rep = -1
        telechargement(dernier_chap_dispo_, filtre_navigation_page(recup_navigation_page(dernier_chap_dispo_, "div", "id", "navigation")), "D", rep)
        


    """on vérifie la longueur de argument:
        Si cette langueur est 1 alors ça veut dire que l'utilisateur n'a pas fournis l'URL en paramètre. Donc on quitte direct

        Si cette longueur est supérieur ou égal à 2, alors on déduit que l'utilisateur a fournis l'url en paramètre et non l'emplacement
        donc on choisit D par défaut

        Si cette longueur vaut 3, alors on déduit que l'utilisateur a fournis l'url et l'emplacement
    """
if len(argument) == 1:
    print("URL REQUIS !!!!")
    sys.exit()

elif len(argument) >= 2:
    telechargement(argument[1], filtre_navigation_page(recup_navigation_page(argument[1], "div", "id", "navigation")), "D", repetition)

elif len(argument) == 3:
    telechargement(argument[1], filtre_navigation_page(recup_navigation_page(argument[1], "div", "id", "navigation")), argument[2], repetition)