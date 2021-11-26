import requests
import csv
from typing import Union

from bs4 import BeautifulSoup


class Parser:
    pass


HOST = "https://crewdata.com/"
URL = "https://crewdata.com/crewings.php"
HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0"
}


def get_html(url, params: Union[str, dict] = ""):
    """

    :param url:
    :param params:
    :return:
    """
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_crewing_link(html):
    """

    :param html:
    :return:
    """
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all("div", class_="rowLike")
    links = [
        HOST + element.get('href')
        for item in items if (element := item.find('a', class_="nameLink")) is not None
    ]

    return links


def get_content(links):
    """

    :param links:
    :return:
    """
    emails = []
    for link in links:
        r = requests.get(link, headers=HEADERS)
        soup = BeautifulSoup(r.text, 'html.parser')
        items = soup.find_all("div", class_="crewingInfo")
        for item in items:
            try:
                element = (
                    item.find('div', class_="headerTxt").find("h1").get_text()
                )
                element2 = item.find('div', class_="c2").find("a").get_text()
                emails.append(
                    {
                        "name": element,
                        "email": element2
                    }
                )
            except Exception as err:
                print(err)

    return [dict(email) for email in set(frozenset(i.items()) for i in emails)]


def save_doc(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Crewing_Name", "email"])
        for item in items:
            writer.writerow([item['name'], item['email']])


def main():
    html = get_html(URL)
    if html.status_code == 200:
        vacancies = []
        for page in range(1, 40):
            html = get_html(URL, params={"page": page})
            content = (get_crewing_link(html.text))
            vacancies.extend(get_content(content))
            save_doc(vacancies, "cards.csv")
    else:
        print(f"Error occurred: {html.status_code}")


if __name__ == "__main__":
    main()
