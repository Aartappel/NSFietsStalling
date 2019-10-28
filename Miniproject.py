from tkinter import *
import time
from datetime import datetime
from datetime import timedelta
from telegram.ext import Updater, CommandHandler
import logging
from telegram.ext import MessageHandler, Filters


def dictionary():  # dictionary maken van bestand
    kluisDict = dict.fromkeys(range(1, 21))

    with open('FietsStalling.txt', 'r+') as readFile:
        for line in readFile:  # kluizen uit bestand lezen
            splitLine = line.split(' ')  # regels opdelen
            kluisNummer = int(splitLine[0].strip(';'))  # 1ste getal is kluisnummer
            OVNummer = int(splitLine[3].strip('\n'))  # laatste getal is OV nummer
            dateTime = splitLine[1] + ' ' + splitLine[2].strip(',')  # middelste deel is datum en tijd
            kluisDict[kluisNummer] = [dateTime, OVNummer]  # keys zijn kluisnummers, values zijn OV nummer en datetime
        return kluisDict


def kluisAanvragen():  # nieuwe kluis aanvragen
    kluisDict = dictionary()
    beginSchermTopTitel['text'] = ''
    beginSchermTerug.grid(pady=3, padx=(10, 10), sticky='w', row=1)

    with open('FietsStalling.txt', 'r+') as readFile:
        while True:
            for kluis in kluisDict:
                if kluisDict[kluis] is None:  # kluis toewijzen
                    beginSchermTitel['text'] = 'Kluis nummer ' + str(kluis)
                    kluisDict[kluis] = [time.strftime('%d-%m-%Y %H:%M'),
                                        int(beginSchermEntry.get())]  # value wordt tijd en OV
                    readFile.truncate(0)
                    readFile.seek(0)
                    for item in kluisDict:  # bestand updaten (nieuwe kluis toevoegen)
                        if kluisDict[item] is not None:
                            readFile.write(str(item) + '; ' + ''.join(str(kluisDict[item])).strip('{}[]\'\'')
                                           .replace('\'', '') + '\n')
                    return

            beginSchermTitel['text'] = 'Geen kluizen vrij'
            return


def kluisOpenen():  # kluis tijdelijk openen
    kluisDict = dictionary()
    beginSchermTopTitel['text'] = ''
    beginSchermTitel['text'] = beginSchermEntry.get()
    beginSchermTerug.grid(pady=3, padx=(10, 10), sticky='w', row=1)

    while True:
        for kluis in kluisDict:
            try:
                if kluisDict[kluis] is not None and int(beginSchermEntry.get()) in kluisDict[kluis]:
                    beginSchermTitel['text'] = 'Kluis nummer ' + str(kluis) + ' is geopend'
                    return
            except ValueError:
                beginSchermTitel['text'] = 'Geen geldige invoer'
                return
        beginSchermTitel['text'] = 'Dit OV nummer is onbekend'
        return


def kluisVrijgeven():  # kluis vrijgeven
    kluisDict = dictionary()
    beginSchermTopTitel['text'] = ''
    beginSchermTerug.grid(pady=3, padx=(10, 10), sticky='w', row=1)

    with open('FietsStalling.txt', 'r+') as readFile:
        while True:
            for kluis in kluisDict:
                try:
                    if kluisDict[kluis] is not None and int(beginSchermEntry.get()) in kluisDict[kluis]:
                        kluisDict[kluis] = None
                        beginSchermTitel['text'] = 'Kluis nummer ' + str(kluis) + ' is vrijgegeven'
                        readFile.truncate(0)
                        readFile.seek(0)
                        for item in kluisDict:  # bestand updaten (vrijgegeven kluis verwijderen)
                            if kluisDict[item] is not None:
                                readFile.write(str(item) + '; ' + ''.join(str(kluisDict[item])).strip('{}[]\'\'')
                                               .replace('\'', '') + '\n')
                        return
                except ValueError:
                    beginSchermTitel['text'] = 'Geen geldige invoer'
                    return
            beginSchermTitel['text'] = 'Dit OV nummer is onbekend'
            return


def kluisInfo():  # huidige kosten opvragen
    kluisDict = dictionary()
    beginSchermTerug.grid(pady=3, padx=(10, 10), sticky='w', row=1)

    while True:
        for kluis in kluisDict:
            try:
                if kluisDict[kluis] is not None and int(beginSchermEntry.get()) in kluisDict[kluis]:
                    beginSchermTopTitel['text'] = fietsStalTijd(kluisDict[kluis][0])
                    beginSchermTitel['text'] = 'De huidige kosten zijn €' + str(prijs(kluisDict[kluis][0]))
                    return
            except ValueError:
                beginSchermTitel['text'] = 'Geen geldige invoer'
                return beginSchermTitel['text']
        beginSchermTitel['text'] = 'Dit OV nummer is onbekend'
        return


def prijs(begintijd):  # prijs berekenen
    starttijd = datetime.strptime(begintijd, '%d-%m-%Y %H:%M')  # begintijd in juiste format
    huidigeTijd = datetime.strptime(time.strftime('%d-%m-%Y %H:%M'), '%d-%m-%Y %H:%M')  # huidige tijd opvragen
    dagVerschil = (huidigeTijd - starttijd).days  # verschil in dagen
    secondeVerschil = (huidigeTijd - starttijd).seconds  # verschil in seconden
    dagMin = dagVerschil * 1440  # dagen naar minuten omrekenen
    secMin = secondeVerschil / 60  # seconden naar minuten omrekenen
    minuten = int(dagMin + secMin)  # totaal aantal minuten
    totaalPrijs = '{:.2f}'.format(minuten * 0.00833333333)  # totaalprijs
    return totaalPrijs


def fietsStalTijd(ovnummer):  # tijdsduur opvragen
    kluisDict = dictionary()
    beginSchermTopTitel['text'] = ''

    while True:
        for kluis in kluisDict:
            try:
                if kluisDict[kluis] is not None and ovnummer in kluisDict[kluis]:  # zoek ov nummer in dictionary
                    huidigeTijdsDuur = str(stalTijd(kluisDict[kluis][0]))  # bereken tijdsduur bij ov nummer
                    return str(huidigeTijdsDuur)
            except ValueError:
                huidigeTijdsDuur = 'Geen geldige invoer'
                return str(huidigeTijdsDuur)


def stalTijd(begintijd):  # prijs berekenen
    starttijd = datetime.strptime(begintijd, '%d-%m-%Y %H:%M')  # begintijd in juiste format
    huidigeTijd = datetime.strptime(time.strftime('%d-%m-%Y %H:%M'), '%d-%m-%Y %H:%M')  # huidige tijd opvragen
    dagVerschil = (huidigeTijd - starttijd).days  # verschil in dagen
    secondeVerschil = (huidigeTijd - starttijd).seconds  # verschil in seconden
    dagMin = dagVerschil * 1440  # dagen naar minuten omrekenen
    secMin = secondeVerschil / 60  # seconden naar minuten omrekenen
    minuten = int(dagMin + secMin)  # totaal aantal minuten
    uurMin = str(timedelta(minutes=minuten))[:-3]
    if 'days' in uurMin:
        tijdSplit = uurMin.split(' ')
        urenMinuten = tijdSplit[2].split(':')
        dagen = tijdSplit[0]
        uren = urenMinuten[0]
        minuten = urenMinuten[1]
        tijdsDuur = 'Je fiets is ' + dagen + ' dagen, ' + uren + ' uur en ' + minuten + ' minuten gestald'
        return tijdsDuur
    else:
        tijdSplit = uurMin.split(':')
        uren = tijdSplit[0]
        minuten = tijdSplit[1]
        tijdsDuur = 'Je fiets is ' + uren + ' uur en ' + minuten + ' minuten gestald'
        return tijdsDuur


def tijd(update, context):  # tijd opvragen bot
    msgContent = str(update['message']['text']).split(' ')
    OVNummer = int(msgContent[1])
    context.bot.send_message(chat_id=update.effective_chat.id, text=fietsStalTijd(OVNummer))


def prijsTg(update, context):  # prijs opvragen bot
    msgContent = str(update['message']['text']).split(' ')
    OVNummer = int(msgContent[1])
    context.bot.send_message(chat_id=update.effective_chat.id, text=kluisInfoTg(OVNummer))


def kluisInfoTg(ovnummer):  # kosten opvragen met bot
    kluisDict = dictionary()

    while True:
        for kluis in kluisDict:
            try:
                if kluisDict[kluis] is not None and ovnummer in kluisDict[kluis]:
                    huidigeKosten = 'De huidige kosten zijn €' + str(prijs(kluisDict[kluis][0]))
                    return huidigeKosten
            except ValueError:
                huidigeKosten = 'Geen geldige invoer'
                return huidigeKosten


def unknown(update, context):  # onbekend bot commando
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


def toonBeginScherm():  # beginscherm herladen
    beginSchermTerug.grid_forget()
    beginSchermTopTitel['text'] = ''
    beginSchermTitel['text'] = 'Welkom bij NS'
    beginSchermEntry.delete(0, END)
    beginScherm.grid()


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
beginScherm.grid()

beginSchermTerug = Button(master=beginScherm,
                          text='Terug',
                          background='#003091',
                          foreground='white',
                          font=('Arial', '12', 'bold'),
                          width=7,
                          height=2,
                          command=toonBeginScherm)

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

beginSchermEntry = Entry(master=beginScherm,  # entry veld
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

beginSchermInfo = Button(master=beginScherm,  # knop zoeken
                         text='Huidige prijs',
                         background='#003091',
                         foreground='white',
                         font=('Arial', '18', 'bold'),
                         width=20,
                         height=2,
                         command=kluisInfo)
beginSchermInfo.grid(pady=3, padx=3, row=5, column=2)

toonBeginScherm()
root.mainloop()
