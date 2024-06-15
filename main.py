from flask import Flask, render_template, request, send_file, abort, send_from_directory, redirect
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from zipfile import ZipFile
from dotenv import load_dotenv

load_dotenv()
import os

from_mail = os.environ.get("FROM_MAIL")
to_mail = os.environ.get("TO_MAIL")
pass_w = os.environ.get("PASS_W")

app = Flask(__name__)
secteur = ['Secteur ingéniérie',
           'Secteur agricole',
           'Secteur Medical',
           'Secteur militaire',
           'Secteur de l’Education',
           'Classes Préparatoires aux Grandes Ecoles',
           'Secteur du commerce et de la gestion']
school_page = False
school = {
    'Secteur ingénierie': {'era': 'static/pdf/era.pdf'},
    'Secteur agricole': {'era': 'static/pdf/era.pdf'},
    'Secteur Medical': {'era': 'static/pdf/era.pdf'},
    'Secteur militaire': {
        'Academie Royal militaire de Meknes': 'static/pdf/era.pdf',
        'Ecole Royal de l\'Air Marrakesh': 'static/pdf/ad.pdf',
        'École royale du service de santé militaire(médecine,dentiste,pharmacien)': 'static/s.pdf',
        'École royale du service de santé militaire(Vétérinaire)': 'static/s.pdf',
        'Sous Officiers des Forces Auxiliaires': 'pdf'
    },
    'Secteur de l’Education': {'era': 'static/pdf/era.pdf'},
    'Classes Préparatoires aux Grandes Ecoles': {'era': 'static/pdf/era.pdf'},
    'Secteur du commerce et de la gestion': {'era': 'static/pdf/era.pdf'}
}

secteurs = {
    "sectors": {
        "1": {
            "name": "Secteur ingénierie",
            "icon": "bi bi-gear",
            "pdfdisplay": {"Ecole Nationale d'Architécture ENA": "ENA.pdf",
                           "Ecole Nationale Supérieure d'Arts et Métiers ENSAM": "ENSAM.pdf",
                           "Ecoles Nationale des Sciences Appliquées ENSA": "Écoles nationales des sciences appliquées ENSA.pdf",
                           "Institut National d'Aménagment et d'Urbanisme INAU": "INAU.pdf",
                           "Faculté des Sciences et Techniques FST": "Faculté des Sciences et Techniques FST.pdf",
                           "Ecole Supérieure de Technologie EST": "Ecole Supérieure de Technologie EST.pdf",
                           "Ecole Nationale Supérieure de Chimie ENSCK": "Ecole Nationale Supérieure de Chimie ENSCK.pdf",
                           "Ecole Normale Supérieure de l'Enseignement Technique ENSET ": "Ecole Normale Supérieure de "
                                                                                          "l’Enseignement Technique "
                                                                                          "ENSET.pdf"}

        },
        "2": {
            "name": "Secteur agricole",
            "icon": "bi bi-tree",
            "pdfdisplay": {"Instiut agronomique et vétérinaire IAV": "Institut agronomique et vétérinaire IAV.pdf",
                           "Ecole National d'Agriculture ENAM": "ENAM.pdf",
                           "Ecole National Forestière d'Ingénieurs ENFI":"ENFI.pdf",
                           "Complexe Horticole d'Agadir CHA": "Complexe Horticole d’Agadir CHA.pdf",
                           }
        },
        "3": {
            "name": "Secteur Medical",
            "icon": "bi bi-activity",
            "pdfdisplay": {
                "Faculté de Médecine,Pharmacie et de Médecine Dentaire": "Faculté de Médecine, Pharmacie et de Médecine Dentaire.pdf",
                "Institut Supérieur des Sciences de la Santé ISSS": "Institut Supérieur des Sciences de la Santé ISSS.pdf",
                "ISPITS": "ISPITS.pdf"}
        },
        "4": {
            "name": "Secteur militaire",
            "icon": "bi bi-shield",
            "pdfdisplay": {"Academie Royal militaire de Meknes": "Académie royale militaire de Meknès.pdf",
                           "Officier des forces auxiliaires": "officiers des forces auxiliaires.pdf",
                           "Sous Officiers des Forces Auxiliaires": "sous officiers des forces auxiliaires.pdf",
                           "sous officier arme de terre": "sous officier arme de terre (1).pdf",
                           "ERA officier": "ERA OFFICIER.pdf",
                           "ERA sous officier": "ERA sous OFFICIER.pdf",
                           "École royale du service de santé militaire": "sante militaire medcin.pdf",
                           "École royale du service de santé militaire(Vétérinaire)": "sante miliTAIRE veterinaire.pdf",
                           "École royale naval casablanca officier": "ern officier.pdf",
                           "École royale naval casablanca sous officier": "ern sous officier.pdf",
                           "Ecole de la Gendarmerie Royale": "Ecole de la Gendarmerie Royale.pdf",
                           "Institut de la Police Royale": "la police.pdf"
                           }},
        "5": {
            "name": "Secteur de l’Education",
            "icon": "bi bi-book",
            "pdfdisplay": {
                "Centres Régionaux des Métiers de l'éducation et le la Formation CRMEF": "CRMEF.pdf",
                "Cycle de Licence en Education": "CLE.pdf",
                "Ecole normale supérieure ENS": "ENS.pdf",
                "Ecoles supérieures d'enseignement et de formation ESEF": "ESEF.pdf",
                "Faculté des Sciences de l'Education FSE": "FSE.pdf"}
        },
        "6": {
            "name": "Classes Préparatoires aux Grandes Ecoles",
            "icon": "bi bi-infinity",
            "pdfdisplay": {
                "Classes Préparatoires aux Grandes Ecoles": "Classes Préparatoires aux Grandes Écoles CPGE.pdf",
                "Concours national commun CNAEM & CNC": "Concours national commun CNAEM & CNC.pdf",
                "Ecoles superieures participants aux concours": "Ecoles superieures participants aux concours.pdf",
            }
        },
        "7": {
            "name": "Secteur du commerce et de la gestion",
            "icon": "bi bi-cash-coin",
            "pdfdisplay": {
                "Ecoles nationales de commerce et de gestion ENCG": "ENCG.pdf",
                "Institut supérieur de commerce et d'administration des entreprises ISCAE": "ISCAE.pdf", }

        }
    }
}

concour = {"ENSAM": "https://drive.google.com/drive/folders/1KIwZ6lIB3SJUHGYnyNTjRT_EyIb_Y7OI?usp=drive_link",
           "ENSA": "https://drive.google.com/drive/folders/1jqaEgBl8oJkHifMqqwCZjy_gKQgRMyhL?usp=drive_link",
           "ENCG": "https://drive.google.com/drive/folders/1MMMbs714DUgBsIoepPYkF1ey0SkMlLrG?usp=drive_link",
           "ENA": "https://drive.google.com/drive/folders/1fYWTJEGK1K7pMI6S_urlzx17abFU6bJ2?usp=drive_link",
           "MEDECINE": "https://drive.google.com/drive/folders/1Ax9mgVsETh66t22vxGrVtOermq8gLL8P?usp=drive_link"}


@app.route('/')
def home():
    return render_template("about.html")


@app.route('/Secteur/<int:sector_id>')
def school(sector_id):
    sector = secteurs["sectors"].get(str(sector_id))
    if sector is None:
        abort(404)
    school_page = True
    return render_template('school.html', sector=sector, school_page=school_page)


@app.route("/concours d'admission")
def concours():
    return render_template("concours.html", concour=concour)


# @app.route('/pdf')
# def pdfs():
#     return send_file('static/example.pdf')

@app.route('/download/<cnc_name>')
def drive_link(cnc_name):
    if cnc_name in concour:
        link = concour[cnc_name]
        return redirect(link)
    else:
        return "link not found"


@app.route("/Secteur")
def filiere():
    index = 0
    return render_template("services.html", secteurs=secteurs)


@app.route('/<file_name>')
def download(file_name):
    return send_from_directory('./static/pdf/', file_name)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    sent_msg = False
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form['email']
        subject = request.form.get("subject")
        body = request.form['message']

        # msg = MIMEMultipart()
        # msg.attach(MIMEText(body, 'plain', 'utf-8'))
        #
        # con = smtplib.SMTP_SSL('smtp.gmail.com')
        # con.login(from_mail, pass_w)
        #
        # msg['Subject'] = subject
        # msg['From'] = from_mail
        # msg['To'] = to_mail
        #
        # con.sendmail(from_mail, to_mail, msg.as_string())
        #
        # con.quit()

        sent_msg = True

    return render_template("contact.html", sent_msg=sent_msg)


if __name__ == "__main__":
    app.run()
