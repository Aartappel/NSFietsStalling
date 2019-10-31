from tkinter import *
import time
from datetime import datetime
from datetime import timedelta
from telegram.ext import Updater, CommandHandler
import logging
from telegram.ext import MessageHandler, Filters


def dictionary():
    """Maak een dictionary van de regels in het bestand."""
    kluisDict = dict.fromkeys(range(1, 21))

    with open('FietsStalling.txt', 'r+') as readFile:
        for line in readFile:  # kluizen uit bestand lezen
            splitLine = line.split(' ')  # regels opdelen
            kluisNummer = int(splitLine[0].strip(';'))  # eerste getal is kluisnummer
            OVNummer = int(splitLine[3].strip('\n'))  # laatste getal is OV nummer
            dateTime = splitLine[1] + ' ' + splitLine[2].strip(',')  # middelste deel is datum en tijd
            kluisDict[kluisNummer] = (dateTime, OVNummer)  # keys zijn kluisnummers, values zijn OV nummer en datetime
        return kluisDict


def kluisAanvragen():
    """Kluis associeren met OV nummer en huidige datum en tijd en naar bestand schrijven."""
    kluisDict = dictionary()
    beginSchermTopTitel['text'] = ''
    beginSchermTerug.grid(pady=3, padx=(10, 10), sticky='w', row=1)

    try:
        if len(beginSchermEntry.get()) == 16:
            for getal in kluisDict:
                if kluisDict[getal] is not None and kluisDict[getal][1] == int(beginSchermEntry.get()):
                    beginSchermTitel['text'] = 'Je hebt al een kluis: nummer ' + str(getal)
                    return

            with open('FietsStalling.txt', 'r+') as readFile:
                for kluis in kluisDict:
                    if kluisDict[kluis] is None:  # kluis toewijzen
                        beginSchermTitel['text'] = 'Kluis nummer ' + str(kluis)
                        kluisDict[kluis] = (time.strftime('%d-%m-%Y %H:%M'),
                                            int(beginSchermEntry.get()))  # value wordt tijd en OV
                        readFile.truncate(0)
                        readFile.seek(0)
                        for item in kluisDict:  # bestand updaten (nieuwe kluis toevoegen)
                            if kluisDict[item] is not None:
                                readFile.write(str(item) + '; ' + ''.join(str(kluisDict[item])).strip('{}()\'\'')
                                               .replace('\'', '') + '\n')
                        beginSchermEntry.delete(0, END)
                        return
                beginSchermTitel['text'] = 'Geen kluizen vrij'
                return
        else:
            beginSchermTitel['text'] = 'Geen geldige invoer'
            return
    except ValueError:
        beginSchermTitel['text'] = 'Geen geldige invoer'
        return


def kluisOpenen():
    """Kluis geassocieerd met OV nummer tijdelijk openen."""
    kluisDict = dictionary()
    beginSchermTopTitel['text'] = ''
    beginSchermTerug.grid(pady=3, padx=(10, 10), sticky='w', row=1)

    for kluis in kluisDict:
        try:
            if kluisDict[kluis] is not None and int(beginSchermEntry.get()) in kluisDict[kluis]:  # kluis zoeken in
                # dictionary
                beginSchermTitel['text'] = 'Kluis nummer ' + str(kluis) + ' is geopend'
                beginSchermEntry.delete(0, END)
                return
        except ValueError:
            beginSchermTitel['text'] = 'Geen geldige invoer'
            return
    beginSchermTitel['text'] = 'Dit OV nummer is onbekend'
    return


def kluisVrijgeven():
    """Kluis geassocieerd met OV nummer vrijgeven en verwijderen uit bestand."""
    kluisDict = dictionary()
    beginSchermTopTitel['text'] = ''
    beginSchermTerug.grid(pady=3, padx=(10, 10), sticky='w', row=1)

    with open('FietsStalling.txt', 'r+') as readFile:
        for kluis in kluisDict:
            try:
                if kluisDict[kluis] is not None and int(beginSchermEntry.get()) in kluisDict[kluis]:  # kluis zoeken
                    # in dictionary
                    kluisDict[kluis] = None
                    beginSchermTitel['text'] = 'Kluis nummer ' + str(kluis) + ' is vrijgegeven'
                    readFile.truncate(0)
                    readFile.seek(0)
                    for item in kluisDict:  # bestand updaten (vrijgegeven kluis verwijderen)
                        if kluisDict[item] is not None:
                            readFile.write(str(item) + '; ' + ''.join(str(kluisDict[item])).strip('{}()\'\'')
                                           .replace('\'', '') + '\n')  # bezette kluizen naar bestand schrijven
                    beginSchermEntry.delete(0, END)
                    return
            except ValueError:
                beginSchermTitel['text'] = 'Geen geldige invoer'
                return
        beginSchermTitel['text'] = 'Dit OV nummer is onbekend'
        return


def kluisInfo():
    """Geef huidige kosten weer van kluis geassocieerd met OV nummer."""
    kluisDict = dictionary()
    beginSchermTerug.grid(pady=3, padx=(10, 10), sticky='w', row=1)

    for kluis in kluisDict:
        try:
            if kluisDict[kluis] is not None and int(beginSchermEntry.get()) in kluisDict[kluis]:  # kluis zoeken in
                # dictionary
                beginSchermTopTitel['text'] = fietsStalTijd(kluisDict[kluis][1])  # functie fietsStalTijd op kluis
                # aanroepen
                beginSchermTitel['text'] = 'De huidige kosten zijn €' + str(prijs(kluisDict[kluis][0]))
                beginSchermEntry.delete(0, END)
                return
        except ValueError:
            beginSchermTitel['text'] = 'Geen geldige invoer'
            return
    beginSchermTitel['text'] = 'Dit OV nummer is onbekend'
    return


def prijs(begintijd):
    """Bereken huidige kosten gebaseerd op tijdsduur."""
    starttijd = datetime.strptime(begintijd, '%d-%m-%Y %H:%M')  # begintijd in juiste format
    huidigeTijd = datetime.strptime(time.strftime('%d-%m-%Y %H:%M'), '%d-%m-%Y %H:%M')  # huidige tijd opvragen
    dagVerschil = (huidigeTijd - starttijd).days  # verschil in dagen
    secondeVerschil = (huidigeTijd - starttijd).seconds  # verschil in seconden
    dagMin = dagVerschil * 1440  # dagen naar minuten omrekenen
    secMin = secondeVerschil / 60  # seconden naar minuten omrekenen
    minuten = int(dagMin + secMin)  # totaal aantal minuten
    totaalPrijs = '{:.2f}'.format(minuten * 0.00833333333)  # totaalprijs
    return totaalPrijs


def fietsStalTijd(ovnummer):
    """Bereken huidige tijdsduur door middel van stalTijd functie met geassocieerde tijd bij ingevoerd OV nummer
    als parameter."""
    kluisDict = dictionary()
    beginSchermTopTitel['text'] = ''

    for kluis in kluisDict:
        try:
            if kluisDict[kluis] is not None and ovnummer in kluisDict[kluis]:  # zoek ov nummer in dictionary
                huidigeTijdsDuur = str(stalTijd(kluisDict[kluis][0]))  # bereken tijdsduur bij ov nummer
                return str(huidigeTijdsDuur)
        except ValueError:
            huidigeTijdsDuur = 'Geen geldige invoer'
            return str(huidigeTijdsDuur)


def stalTijd(begintijd):
    """Bereken huidige tijdsduur op basis van tijd geassocieerd met kluis en huidige tijd."""
    starttijd = datetime.strptime(begintijd, '%d-%m-%Y %H:%M')  # begintijd in juiste format
    huidigeTijd = datetime.strptime(time.strftime('%d-%m-%Y %H:%M'), '%d-%m-%Y %H:%M')  # huidige tijd opvragen
    dagVerschil = (huidigeTijd - starttijd).days  # verschil in dagen
    secondeVerschil = (huidigeTijd - starttijd).seconds  # verschil in seconden
    dagMin = dagVerschil * 1440  # dagen naar minuten omrekenen
    secMin = secondeVerschil / 60  # seconden naar minuten omrekenen
    minuten = int(dagMin + secMin)  # totaal aantal minuten
    uurMin = str(timedelta(minutes=minuten))[:-3]
    if 'day' not in uurMin:  # wanneer tijdsduur minder dan een dag is
        tijdSplit = uurMin.split(':')
        uren = tijdSplit[0]
        if tijdSplit[1] != '00':
            minuten = tijdSplit[1].lstrip('0')  # overbodige eerste '0' verwijderen
        else:
            minuten = tijdSplit[1][:1]
        if uren == '0':  # wanneer aantal uren 0 is uren niet printen
            uurTekst = ''
            uren = ''
        else:
            uurTekst = ' uur en '
        if minuten == '1':  # 'minuut' printen in plaats van 'minuten' bij 1 minuut
            tijdsDuur = 'Je fiets is ' + uren + uurTekst + minuten + ' minuut gestald'
        else:
            tijdsDuur = 'Je fiets is ' + uren + uurTekst + minuten + ' minuten gestald'
        return tijdsDuur
    else:
        tijdSplit = uurMin.split(' ')
        urenMinuten = tijdSplit[2].split(':')
        dagen = tijdSplit[0]
        uren = urenMinuten[0]
        if urenMinuten[1] != '00':
            minuten = urenMinuten[1].lstrip('0')  # overbodige eerste '0' verwijderen
        else:
            minuten = urenMinuten[1][:1]
        if uren == '0':  # wanneer aantal uren 0 is uren niet printen
            uurTekst = ''
            uren = ''
        else:
            uurTekst = ' uur en '
        if 'days' in uurMin:  # 'dagen' printen in plaats van 'dag' bij 1 dag
            if minuten == '1':
                tijdsDuur = 'Je fiets is ' + dagen + ' dagen, ' + uren + uurTekst + minuten + ' minuut gestald'
            else:
                tijdsDuur = 'Je fiets is ' + dagen + ' dagen, ' + uren + uurTekst + minuten + ' minuten gestald'
            return tijdsDuur
        else:
            if minuten == '1':
                tijdsDuur = 'Je fiets is ' + dagen + ' dag, ' + uren + uurTekst + minuten + ' minuut gestald'
            else:
                tijdsDuur = 'Je fiets is ' + dagen + ' dag, ' + uren + uurTekst + minuten + ' minuten gestald'
            return tijdsDuur


def beheerderOpenen():
    """Kluis openen gebaseerd op ingevoerd kluisnummer."""
    beheerderEntry.get()
    kluisDict = dictionary()

    try:
        if kluisDict[int(beheerderEntry.get())] is not None:  # wanneer kluis bezet is
            beheerderTitel['text'] = 'Kluis nummer ' + beheerderEntry.get() + ' is geopend'
        else:
            beheerderTitel['text'] = 'Deze kluis is niet bezet'
        return
    except ValueError:
        beheerderTitel['text'] = 'Geen geldige invoer'
        return


def beheerderVrijgeven():
    """Kluis vrijgeven gebaseerd op ingevoerd kluisnummer."""
    kluisDict = dictionary()
    with open('FietsStalling.txt', 'r+') as readFile:
        try:
            if kluisDict[int(beheerderEntry.get())] is not None:  # wanneer kluis bezet is
                kluisDict[int(beheerderEntry.get())] = None  # kluis waarde verwijderen uit dictionary
                beheerderTitel['text'] = 'Kluis nummer ' + beheerderEntry.get() + ' is vrijgegeven'
                readFile.truncate(0)
                readFile.seek(0)
                for item in kluisDict:  # bestand updaten (vrijgegeven kluis verwijderen)
                    if kluisDict[item] is not None:
                        readFile.write(str(item) + '; ' + ''.join(str(kluisDict[item])).strip('{}()\'\'')
                                       .replace('\'', '') + '\n')  # bezette kluizen naar bestand schrijven
                return
            else:
                beheerderTitel['text'] = 'Deze kluis is niet bezet'
        except ValueError:
            beheerderTitel['text'] = 'Geen geldige invoer'
            return


def tijd(update, context):
    """Huidige tijdsduur opvragen aan Telegram bot door middel van fietsStalTijd functie."""
    msgContent = str(update['message']['text']).split(' ')
    OVNummer = int(msgContent[1])  # OV nummer uit bericht lezen
    context.bot.send_message(chat_id=update.effective_chat.id, text=fietsStalTijd(OVNummer))


def prijsTg(update, context):
    """Huidige kosten opvragen aan Telegram bot door middel van kluisInfoTg functie."""
    msgContent = str(update['message']['text']).split(' ')
    OVNummer = int(msgContent[1])  # OV nummer uit bericht lezen
    context.bot.send_message(chat_id=update.effective_chat.id, text=kluisInfoTg(OVNummer))


def kluisInfoTg(ovnummer):
    """Huidige kosten opvragen aan Telegram bot door middel van prijs functie."""
    kluisDict = dictionary()

    for kluis in kluisDict:
        try:
            if kluisDict[kluis] is not None and ovnummer in kluisDict[kluis]:  # kluis zoeken in dictionary
                huidigeKosten = 'De huidige kosten zijn €' + str(prijs(kluisDict[kluis][0]))
                return huidigeKosten
        except ValueError:
            huidigeKosten = 'Geen geldige invoer'
            return huidigeKosten


def unknown(update, context):
    """Aangeven wanneer een commando niet herkend wordt door Telegram bot."""
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, dat commando is onbekend.")


def toonBeginScherm():
    """Beginscherm tonen of herladen."""
    beginSchermTerug.grid_forget()
    beheerderScherm.grid_forget()
    beginSchermTopTitel['text'] = ''
    beginSchermTitel['text'] = 'Welkom bij NS'
    beginSchermEntry.delete(0, END)
    beginScherm.grid()


def toonBeheerderScherm():
    """Beheerderscherm tonen."""
    if beginSchermEntry.get() == '1234123412341234':
        beginScherm.grid_forget()
        beheerderScherm.grid()
        beginSchermTerug.grid(pady=3, padx=(10, 10), sticky='w', row=1)
        beheerderTitel['text'] = 'Vul een kluisnummer in'
    else:
        toonBeginScherm()


updater = Updater(token='966523720:AAH9N8uV6r3ptO-Jhr2L8u-sRQVApa6VqIU', use_context=True)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

dispatcher = updater.dispatcher

tijd_handler = CommandHandler('tijd', tijd)
dispatcher.add_handler(tijd_handler)

prijs_handler = CommandHandler('prijs', prijsTg)
dispatcher.add_handler(prijs_handler)

unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)

updater.start_polling()

root = Tk()

beginScherm = Frame(master=root,
                    bg='#FCC63F',
                    width=750,
                    height=500)

beginSchermTerug = Button(master=beginScherm,
                          text='Terug',
                          background='#003091',
                          foreground='white',
                          font=('Arial', '12', 'bold'),
                          width=7,
                          height=2,
                          command=toonBeginScherm)

beginSchermBeheerKnop = Button(master=beginScherm,
                               text='Beheerder',
                               background='#003091',
                               foreground='white',
                               font=('Arial', '10', 'bold'),
                               width=8,
                               height=2,
                               command=toonBeheerderScherm)
beginSchermBeheerKnop.grid(pady=3, padx=(10, 10), sticky='n', row=0, column=0, columnspan=3)

beginSchermTopTitel = Label(master=beginScherm,
                            text='',
                            background='#FCC63F',
                            foreground='#003091',
                            font=('Arial', '16', 'bold'),
                            width=50,
                            height=1)
beginSchermTopTitel.grid(pady=40, row=0, column=0, columnspan=3)

beginSchermTitel = Label(master=beginScherm,
                         text='',
                         background='#FCC63F',
                         foreground='#003091',
                         font=('Arial', '24', 'bold'),
                         width=25,
                         height=4)
beginSchermTitel.grid(row=1, column=0, columnspan=3)

beginSchermInstructie = Label(master=beginScherm,
                              text='Voer je OV-chipkaart nummer in en maak een keuze',
                              background='#FCC63F',
                              foreground='#003091',
                              font=('Arial', '18', 'bold'))
beginSchermInstructie.grid(row=2, column=0, columnspan=3)

beginSchermEntry = Entry(master=beginScherm,
                         font=('Arial', '20', 'bold'))
beginSchermEntry.grid(padx=111, pady=(6, 20), row=3, column=0, columnspan=3, ipady=5)

beginSchermNieuwKluis = Button(master=beginScherm,
                               text='Nieuwe kluis aanvragen',
                               background='#003091',
                               foreground='white',
                               font=('Arial', '18', 'bold'),
                               width=20,
                               height=2,
                               command=kluisAanvragen)
beginSchermNieuwKluis.grid(pady=3, padx=3, row=4, column=0)

beginSchermKluisOpenen = Button(master=beginScherm,
                                text='Kluis tijdelijk openen',
                                background='#003091',
                                foreground='white',
                                font=('Arial', '18', 'bold'),
                                width=20,
                                height=2,
                                command=kluisOpenen)
beginSchermKluisOpenen.grid(pady=3, padx=3, row=4, column=2)

beginSchermKluisVrijgeven = Button(master=beginScherm,
                                   text='Kluis vrijgeven',
                                   background='#003091',
                                   foreground='white',
                                   font=('Arial', '18', 'bold'),
                                   width=20,
                                   height=2,
                                   command=kluisVrijgeven)
beginSchermKluisVrijgeven.grid(pady=3, padx=3, row=5, column=0)

beginSchermInfo = Button(master=beginScherm,
                         text='Huidige prijs',
                         background='#003091',
                         foreground='white',
                         font=('Arial', '18', 'bold'),
                         width=20,
                         height=2,
                         command=kluisInfo)
beginSchermInfo.grid(pady=3, padx=3, row=5, column=2)

beheerderScherm = Frame(master=root,
                        bg='#FCC63F',
                        width=750,
                        height=500)

beheerderTerug = Button(master=beheerderScherm,
                        text='Terug',
                        background='#003091',
                        foreground='white',
                        font=('Arial', '12', 'bold'),
                        width=5,
                        height=2,
                        command=toonBeginScherm)
beheerderTerug.grid(pady=3, padx=(10, 10), sticky='w', row=1, columnspan=3)

beheerderTitel = Label(master=beheerderScherm,
                       text='',
                       background='#FCC63F',
                       foreground='#003091',
                       font=('Arial', '24', 'bold'),
                       width=25,
                       height=4)
beheerderTitel.grid(row=1, column=0, columnspan=3)

beheerderEntry = Entry(master=beheerderScherm,
                       font=('Arial', '20', 'bold'))
beheerderEntry.grid(padx=111, pady=(6, 20), row=3, column=0, columnspan=3, ipady=5)

beheerderKluisOpenen = Button(master=beheerderScherm,
                              text='Kluis openen',
                              background='#003091',
                              foreground='white',
                              font=('Arial', '18', 'bold'),
                              width=20,
                              height=2,
                              command=beheerderOpenen)
beheerderKluisOpenen.grid(pady=3, padx=3, row=5, column=1)

beheerderKluisVrijgeven = Button(master=beheerderScherm,
                                 text='Kluis vrijgeven',
                                 background='#003091',
                                 foreground='white',
                                 font=('Arial', '18', 'bold'),
                                 width=20,
                                 height=2,
                                 command=beheerderVrijgeven)
beheerderKluisVrijgeven.grid(pady=3, padx=3, row=5, column=2)

try:  # tekstbestand aanmaken als het nog niet bestaat
    open('FietsStalling.txt', 'x')
    open('FietsStalling.txt', 'x').close()
except FileExistsError:
    pass

toonBeginScherm()
root.mainloop()
