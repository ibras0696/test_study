import requests
from bs4 import BeautifulSoup


def get_times():
    url = "https://namaz-24.ru/groznyj/"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        prayer_times = {}


        fajr_div = soup.find('div', class_="time-block time-block_Fajr exo2 time-block_green")
        if fajr_div:

            time_fajr = fajr_div.find('span')
            if time_fajr:
                prayer_times['Фаджр'] = time_fajr.text.strip()


        zuhr_div = soup.find('div', class_='time-block_Dhuhr')
        if zuhr_div:
            time_zuhr = zuhr_div.find('span')
            if time_zuhr:
                prayer_times['Зухр'] = time_zuhr.text.strip()


        asr = soup.find('div', class_='time-block_Asr')
        if asr:
            time_asr = asr.find('span')
            if time_asr:
                prayer_times['Аср'] = time_asr.text.strip()


        maghrib = soup.find('div', class_='time-block_Maghrib')
        if maghrib:
            time_maghrib = maghrib.find('span')
            if time_maghrib:
                prayer_times['Магриб'] = time_maghrib.text.strip()


        isha = soup.find('div', class_='time-block_Isha')
        if isha:
            time_isha = isha.find('span')
            if time_isha:
                prayer_times['Иша'] = time_isha.text.strip()

        return prayer_times

    except Exception as e:
        return {"Ошибка": str(e)}


times = get_times()
for prayer, time in times.items():
    print(f"{prayer}: {time}")