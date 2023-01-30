import os
import time
from threading import Thread
from tkinter import END, messagebox, NORMAL, DISABLED
from selenium import webdriver
from FolderChooser import Folder
from bs4 import BeautifulSoup
import regex as re
import pandas as pd

folder = Folder()
urls = []
entreprisesInfos = [[], [], [], [], []]


def effacer_zone_de_texte(entree):
    entree.delete(0, END)


def effacer_liste(entree):
    entree.delete(0, END)


def afficher(entree, text):
    entree.insert(END, text)


def afficher_infos_breve(entree, text):
    entree.delete(0, END)
    entree.insert(END, text)


def init(metier, region, pi, pf, liste, infosbox, bouton):
    if pf != '+∞':
        afficher(liste, "recherche...")
        thread = Thread(target=getLiens, args=[metier, region, pi, pf, liste, infosbox, bouton])
        thread.daemon = True
        thread.start()
    else:
        messagebox.showinfo("Paramètres incomplets",
                            "vérifiez vos paramètres (liste des métiers, page finale) !")


def stringify(chaine):
    n = chaine.count(' ')
    for index in range(0, n):
        chaine = chaine.replace(" ", "+")
    chaine = chaine.replace("(", "%28")
    chaine = chaine.replace(")", "%29")
    chaine = chaine.replace(",", "%2C")
    chaine = chaine.replace("'", "%27")
    return chaine


def getLiens(metier, region, pi, pf, mylist, entry_infos, bouton):
    options = webdriver.ChromeOptions()
    options.add_argument("--user-data-dir=" + folder.get_repertoire())
    driver = webdriver.Chrome("C:/chromedriver.exe", options=options)
    baseurl = "https://www.pagesjaunes.fr/annuaire/chercherlespros?quoiqui="

    def get_data(metier, region, pi, pf, mylist, entry_infos, baseurl):
        metier = stringify(metier)
        region = stringify(region)
        baseurl += metier
        baseurl += "&ou="
        baseurl += region
        baseurl += "&univers=pagesjaunes"
        folder.set_currentPage(int(pi))
        page = folder.get_currentPage()
        while page <= int(pf):
            url = baseurl
            if page > 1:
                pageUrl = "&page=" + str(page)
                url += pageUrl

            driver.get(url)
            content = driver.page_source
            soup = BeautifulSoup(content, features="html.parser")
            if page == int(pi):
                time.sleep(1)
                nombre_de_pages = soup.find("span", {"id": "SEL-compteur"})
                total_pages = int(nombre_de_pages.text.strip().split("/")[1])
                folder.set_total(total_pages)
                afficher_infos_breve(entry_infos, str(page) + " / " + str(total_pages))
            infos = soup.findAll("a", {"class": "bi-denomination"})
            if page > 1:
                total_recup = folder.get_total_recup()
            else:
                total_recup = 0

            regex1 = re.compile('.*aucun_resultat.*')
            regex2 = re.compile('.*wording-no-responses.*')
            notfound1 = soup.find("p", {"class": regex1})
            notfound2 = soup.find("h1", {"class": regex2})

            if notfound1 is not None:
                mylist.insert(END, notfound1.getText())
                return 0
            elif notfound2 is not None:
                mylist.insert(END, notfound2.getText())
                return 0
            mylist.insert(END, "Liens page n°" + str(page) + " : ")
            for infos_div in infos:
                titre_lien = infos_div.get('href')  #
                if titre_lien != "#":
                    mylist.insert(END, str(total_recup + 1) + " https://www.pagesjaunes.fr" + titre_lien)
                    urls.append("https://www.pagesjaunes.fr" + titre_lien)
                    total_recup += 1
                # if total == 20:
                # break
            folder.set_total_recup(total_recup)
            afficher_infos_breve(entry_infos, str(page) + " / " + str(total_pages))
            page += 1
            time.sleep(2)

    if len(metier.split(",")) < 1:
        effacer_liste(mylist)
        get_data(metier, region, pi, pf, mylist, entry_infos, baseurl)
    else:
        afficher_infos_breve(entry_infos, "plusieurs métiers")
        effacer_liste(mylist)
        metiers = metier.split(",")
        for metier in metiers:
            mylist.insert(END, "Métier: " + metier)
            get_data(metier, region, pi, pf, mylist, entry_infos, baseurl)

    messagebox.showinfo("Collecte de liens", "Liens des professionels récuperés !")
    afficher_infos_breve(entry_infos, "Total de liens récupérés: " + str(len(urls)))
    bouton["state"] = NORMAL
    bouton["cursor"] = "hand1"

    driver.close()


def getEntrepriseInfos(url, driver):
    driver.get(url)
    content = driver.page_source
    soup = BeautifulSoup(content, features="html.parser")
    entrepriseInfos = []
    regex1 = re.compile('.*pj-on-autoload teaser-header.*')
    infos = soup.find("div", {"class": regex1})
    try:
        nom = infos.find("h1", {"class": "noTrad no-margin"}).text
    except Exception as e:
        nom = ""
        print("Erreur nom: ", e)
    try:
        activite = infos.find("span", {"class": "activite"}).text
    except Exception as e:
        activite = ""
        print("Erreur activité: ", e)
    try:
        regex2 = re.compile('.*teaser-footer fd-bloc.*')
        contacts = soup.find("div", {"class": regex2})
    except Exception as e:
        print("Erreur contacts (pour avoir le numero): " + e)

    try:
        regex2 = re.compile('.*btn btn_tertiary pj-lb pj-link.*')
        numero = contacts.find("a", {"class": regex2}).text.strip()
    except Exception as e:
        numero = ""
        print("Erreur numero: ", e)
    try:
        regex2 = re.compile('.*Site internet du professionnel nouvelle fenêtre.*')
        siteLink = contacts.find("a", {"title": regex2})
        site = siteLink.find("span", {"class": "value"}).text
        if not re.match(".*://.*", site):
            site = "https://" + site
        elif re.match("http://.*", site):
            site = site.replace("http://", "https://")
    except Exception as e:
        site = "pas de site"
        print("erreur site: ", e)
    try:
        adressesLink = contacts.find("a", {
            "class": "teaser-item black-icon address streetAddress clearfix map-click-zone pj-lb pj-link"})
        adresseTab = adressesLink.findAll("span", {"class": "noTrad"})
        adresse = ""
        for adr in adresseTab:
            adresse += adr.text
    except Exception as e:
        adresse = ""
        print("erreur adresse: ", e)

    entrepriseInfos.append(nom)
    entrepriseInfos.append(activite)
    entrepriseInfos.append(numero)
    entrepriseInfos.append(site)
    entrepriseInfos.append(adresse)

    return entrepriseInfos


def scrapper_les_liens(mylist, infosbox, bouton, pb):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--user-data-dir=" + folder.get_repertoire())
        driver = webdriver.Chrome("C:/chromedriver.exe", options=options)
    except Exception as e:
        print("ptit probleme", e)
    mylist.delete(0, END)
    i = 1
    total_liens = len(urls)
    pas = 100 / total_liens
    for u in urls:
        mylist.insert(END, "Lien n°" + str(i) + ": " + u)
        res = getEntrepriseInfos(u, driver)
        mylist.insert(END, res)
        entreprisesInfos[0].append(res[0])
        entreprisesInfos[1].append(res[1])
        entreprisesInfos[2].append(res[2])
        entreprisesInfos[3].append(res[3])
        entreprisesInfos[4].append(res[4])
        afficher_infos_breve(infosbox, "Niveau de progression: " + str(i) + " / " + str(total_liens))
        i += 1
        pb['value'] += pas
        time.sleep(1)
    driver.close()
    bouton["state"] = NORMAL
    bouton["cursor"] = "hand1"
    messagebox.showinfo("Résultat", "Données extraites !")


def process_links(mylist, infosbox, bouton, pb):
    mylist.delete(0, END)
    afficher(mylist, "traitement...")
    thread2 = Thread(target=scrapper_les_liens, args=[mylist, infosbox, bouton, pb])
    thread2.daemon = True
    thread2.start()


def out(metier, infosbox):
    thread = Thread(target=exporter, args=[metier, infosbox])
    thread.start()


def exporter(metier, infosbox):
    if len(metier.split(",")) < 1:
        filename = metier.strip()
    else:
        filename = metier.strip().replace(",", "_")
    infosbox.delete(0, END)
    afficher(infosbox, "exportation du résultat...")
    df = pd.DataFrame({'nom': entreprisesInfos[0], 'activite': entreprisesInfos[1], 'numero': entreprisesInfos[2],
                       'site': entreprisesInfos[3], 'adresse': entreprisesInfos[4]})
    if os.path.exists(filename + ".csv"):
        df.to_csv(filename + ".csv", mode='a', header=False, index=False, encoding='utf-8-sig')
    else:
        df.to_csv(filename + ".csv", index=False, encoding='utf-8-sig')
    messagebox.showinfo("Résultat", "Document csv exporté !")
    afficher(infosbox, "Document csv exporté !")
    afficher_infos_breve(infosbox, "Document csv exporté !")


def reboot(button_exporter, button_traiter, entry_resultats, entry_infos, pb):
    entry_resultats.delete(0, END)
    afficher_infos_breve(entry_infos, "rebootage...")
    folder.erease()
    urls.clear()
    entreprisesInfos = [[], [], [], [], []]
    pb['value'] = 0
    button_exporter["state"] = DISABLED
    button_traiter["state"] = DISABLED
    button_exporter["cursor"] = "circle"
    button_traiter["cursor"] = "circle"

