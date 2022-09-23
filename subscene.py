from pathlib import Path
from bs4 import BeautifulSoup
import requests
import sys




EN_TETE = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0"}




def recup_reponse_requete(url_, element_cible, attribut_element, valeur_attribut):
    """Cette fonction a pour but d'initialiser la requête afin de recupéré que les balises conteneur d'url de la page de telechargement

    Args:
        url_ (chaine de caractère): Il s'agit d'URL de la page où on souhaite récupere le liens exemple: https://subscene.com/subtitles/three-thousand-years-of-longing
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




def recup_liens_sous_titre(balise_cible, langue):
    """Cette fonction prend la valeur de retour de la fonction recup_reponse_requete en première paramètre (balise_cible).
       On va bouclé sur cette première paramètre afin de chercher tous les balises <a></a>. 
       Puis après on va récupéré la valeur de l'attribut "href". 
       Et après, si et seulement si la langue correspond à notre langue de recherche : On recuperera le lien et le nom correspondant.
       
       Exemple: 
                    lien = lien.attrs["href"]
                                                     lien.attrs["href"] ==> /subtitles/three-thousand-years-of-longing/english/2883198  #liens
                    lien_ = str(lien).split("/")
                                                     lien.split() ==> ["<a href="", "subtitles", "three-thousand-years-of-longing", "english", "2883198"]
                    lien_[-1] = 2883198  #nom
                    lien_[-2] = english  #langue
                    lien_[-3] = three-thousand-years-of-longing  #titre_drama

    Args:
        balise_cible (list):  Il s'agit du valeur de retour de la fonction recup_reponse_requete, cette valeur contient
                              Les balises conteneur des liens qui nous interesse
        langue (chaine de caractère): La langue du sous-titre qu'on veut télecharger, ce paramètre sera utilisé pour filtré que la langue choisis par l'utilisateur

    Returns:
        dictionaire: Cette valeur de retour, contiendra :
                                                            1-Les liens vers la page de telechargement
                                                            2-Le nom correspondant à la page actuel
                                                            3-Le titre du drama dont on veut récupéré le sous-titre
    """

    resultat = {"liens": [], "nom": [], "titre_drama": ""}

    for i in balise_cible:
        lien = i.find("a")
        lien = lien.attrs["href"]
        lien_ = str(lien).split("/")

        if str(lien_[-2]) == langue:
            resultat["liens"].append("https://subscene.com"+lien)
            resultat["nom"].append(lien_[-1])

            if not resultat["titre_drama"]:
                resultat["titre_drama"] = lien_[-3]

    return resultat




def telecharge_sous_titre(info_sur_le_lien, langue, emplacement):
    """Cette fonction créer les dossiers et telecharge les sous-titre pour chaque lien contenu dans:
                                                                                                         info_sur_le_lien["liens"]
        Il est bon de rappeller que info_sur_le_lien["liens"] contient tous les liens vers la page du telechargement:
            EXEMPLE: https://subscene.com/subtitles/three-thousand-years-of-longing/english/2883303
        Et en analysant cette page d'EXEMPLE, le liens de telechargement est :
            <a href="/subtitles/english-text/UThu7h225z4DZAORpdXLhvjbl3FKtIXOPJ1Yw1jhgJSEfHt7HMSMFwQN3qqTs42MXnKbkn4mQLL7vyXOqnQSDBNRF0pjGHmkZrMf6fnxC_Wth_q-YXpD-u8AAp9zhbXc0" rel="nofollow" onclick="DownloadSubtitle(this)" id="downloadButton" class="button positive">
        
                 Il a un attribut id avec la valeur "downloadButton"
                 et aussi un class avec la valeur "button positive"
        
                 POURQUOI id au lieu de class ?
                    Parce que pour certain page de telechargement cette class vaut "button neutral"
                    Donc y'aura un rajjout de code pour vérifier si on a un class "button postivie" ou "button neutral"
                    D'où le choix de l'id.
    Args:
        info_sur_le_lien (dictionaire): Il s'agit de la valeur du retour de la fonction recup_liens_sous_titre, cette valeur
                                        de retour contient les informations utile au telechagement
        langue (chaine de carractere, optionel): 
        emplacement (chaine de carractère, optionel): Il s'agit tous simplement de l'emplacement où on aimerait stocker notre telechargement,
        par défaut il sera dans
                                 D:\\subscene.com\\titre_du_drama\\langue

    """

    nombre_de_lien = len(info_sur_le_lien["liens"])
    emplacement_ = emplacement + ":\\"
    dossier_telechargement = Path(emplacement_)
    dossier_telechargement = dossier_telechargement / "subscene.com" / info_sur_le_lien["titre_drama"] / langue
    dossier_telechargement.mkdir(parents=True, exist_ok=True)
    
    loading = ""

    print("DEBUT TELECHARGEMENT DES SOUS-TITRE DE {}".format(info_sur_le_lien["titre_drama"]))

    for i in range(0, nombre_de_lien):
       lien_du_telechargement = recup_reponse_requete(info_sur_le_lien["liens"][i], "a", "id", "downloadButton")
       
       for lien in lien_du_telechargement:
            requete_telechargement = requests.get("https://subscene.com"+str(lien.attrs["href"]), headers=EN_TETE)
            
            with open(str(dossier_telechargement)+"\\"+str(info_sur_le_lien["nom"][i])+".zip", "wb") as telechargement_sous_titre:
                loading += "*"
                telechargement_sous_titre.write(requete_telechargement.content)

            print(loading)

    print("TELECHARGEMENT DES SOUS-TITRE DE {} TERMINE".format(info_sur_le_lien["titre_drama"]))

    print("EMPLACEMENT :: {} ".format(dossier_telechargement))

"""
    Par défaut le script va telecharger les sous-titres en français et les stock dans D:\\titre_drama\\french\\
    Cependant il est possible de préciser la langue du sous-titre ainsi que l'emplacement:
        *première argument obligatoire, il s'agit d'URL
        *second argument, facultatif il s'agit de la langue du sous-titre souhaité (french, english, ...)
        *troisière et dernière argument, il s'agit de l'emplacement où on veut stocker les sous-titres (C, D, F, ...)

    EXEMPLE: subscene.py https://subscene.com/subtitles/house-of-the-dragon-first-season french C
    
"""

argument_ = sys.argv

langue = "french"
emplacement = "D"
url = ""

if len(argument_) == 1:
        print("URL REQUIS !!!!")
        sys.exit()

elif len(argument_) >= 2:
    url = str(argument_[1])

elif len(argument_) >= 3:
    print("langue ok")
    langue = str(argument_[2])

elif len(argument_) == 4:
    print("emplacement ok")
    emplacement = str(argument_[3])


resultat_premier_requete = recup_reponse_requete(url, "td", "class","a1")
    
info_sur_le_lien = recup_liens_sous_titre(resultat_premier_requete, langue)

telecharge_sous_titre(info_sur_le_lien, langue, emplacement)



