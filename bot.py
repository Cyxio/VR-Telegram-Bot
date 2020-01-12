import telebot
import conf1
from urllib.request import urlopen
import json
import time

lisatunnit = 2  # Kesäajan koittaessa vaihdettava arvoon 3

print("started.")

d = urlopen("https://rata.digitraffic.fi/api/v1/metadata/stations")
dTiedosto = json.loads(d.read())
lyhenteet = {}
for i in range(0, (len(dTiedosto) - 1)):
    lyhenteet[dTiedosto[i]['stationShortCode']] = (dTiedosto[i]['stationName']).replace(" asema", "").replace(" Asema", "")


def format(stri):
    abc = stri.split('T')[1]
    return str(int(abc[0:2]) + lisatunnit) + abc.split('.000Z')[0][2:len(abc)]


bot = telebot.TeleBot(conf1.TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "Hei ja tervetuloa käyttämään VR:n pitkänmatkanjunien aikatauluinformaatiobottia.\n\nTietoa botin käyttämisestä saat komennolla /help")


@bot.message_handler(commands=['help'])
def echo_all(message):
    bot.send_message(message.chat.id, 'Voit käyttää bottia kirjoittamalla joko /juna junannumero (esim. "/juna 24" näyttää junan IC24 aikataulun) tai /train junannumero.')


@bot.message_handler(commands=['train', 'juna'])
def echo_all(message):
    numbers = [int(s) for s in message.text.split() if s.isdigit()]
    if (numbers):
        trainLink = "https://rata.digitraffic.fi/api/v1/trains/latest/" + str(numbers[0])
        opened = urlopen(trainLink)
        file = opened.read()
        jsonFile = json.loads(file)
        if (jsonFile):
            pysakkilista = []
            for x in jsonFile[0]["timeTableRows"]:
                if x['trainStopping'] and x['type'] == "ARRIVAL":
                    if x.get("liveEstimateTime") == None:
                        pysakkilista.append(
                            lyhenteet[x['stationShortCode']] + ": raiteelle " + x['commercialTrack'] + " ajassa " + format(
                                x['scheduledTime']))
                    elif x.get("liveEstimateTime") != None:
                        pysakkilista.append(
                            lyhenteet[x['stationShortCode']] + ": raiteelle " + x['commercialTrack'] + " ajassa " + format(
                                x['liveEstimateTime']) + " (alkuperäinen saapumisaika: " + format(
                                x['scheduledTime']) + ", eroa " + str(x["differenceInMinutes"]) + " minuuttia )")
            bot.send_message(message.chat.id, "Junan " + str(jsonFile[0]['trainType']) + "" 
                + str(numbers[0]) + " (" + lyhenteet[jsonFile[0]["timeTableRows"][0]['stationShortCode']]
                + " -> " + lyhenteet[jsonFile[0]["timeTableRows"][len(jsonFile[0]["timeTableRows"]) - 1]['stationShortCode']] + ")"
                + " saapumisajat:")
            bot.send_message(message.chat.id, "\n".join(pysakkilista))
        else:
            bot.send_message(message.chat.id, "En löytänyt junaa.")
    else:
        bot.send_message(message.chat.id, "En löytänyt junaa.")


if __name__ == '__main__':
    bot.polling(none_stop=True)