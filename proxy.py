import requests
from bs4 import BeautifulSoup
import sys
import pathlib
import random


def get_free_proxies():
    urls = ["https://free-proxy-list.net/anonymous-proxy.html",
            "https://free-proxy-list.net/"]
    data = []
    for url in urls:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, "html.parser")
            # Извлекаем прокси из текстовой области
            proxies = soup.textarea.text.split('\n')[3:-1]
            data.extend(proxies)  # Объединяем списки в один
        except Exception as e:
            print(f'Ошибка при получении прокси с {url}: {e}')
    return data


def get_current_ip():
    response = requests.get('https://httpbin.org/ip')
    return response.json()['origin']


def get_country_by_ip(ip):
    try:
        response = requests.get(f'https://ipinfo.io/{ip}/json')
        data = response.json()
        return data.get('country', 'Неизвестно')
    except Exception as e:
        print(f'Ошибка при получении информации о стране для IP {ip}: {e}')
        return 'Неизвестно'


def test_proxies(proxies: list):
    print(f'Обнаружено бесплатных прокси - {len(proxies)}:')

    # Записываем рабочие прокси в файл
    with open(pathlib.Path(sys.argv[0]).parent.resolve() / 'proxies.txt', 'a') as file:
        for prox in proxies:
            try:
                req = requests.get('https://httpbin.org/ip',
                                   proxies={"http": f'http://{prox}', 'https': f'http://{prox}'}, timeout=5)
                if req.status_code == 200:
                    print(f'Доступный прокси: {prox}')
                    # Получаем страну по IP прокси
                    proxy_ip = prox.split(':')[0]  # Извлекаем IP из прокси
                    country = get_country_by_ip(proxy_ip)
                    file.write(f'{prox} - {country}\n')  # Записываем рабочий прокси и страну в файл
                else:
                    print(f'{prox} недоступен. Код статуса: {req.status_code}')
            except Exception as e:
                print(f'{prox} недоступен. Ошибка: {e}')


def use_anonymizer():
    # Получаем список прокси
    proxies = get_free_proxies()

    # Получаем текущий IP
    current_ip = get_current_ip()
    print(f'Ваш текущий IP: {current_ip}')

    # Тестируем прокси
    test_proxies(proxies)

    # Используем случайный рабочий прокси для анонимного запроса
    working_proxies = []
    with open(pathlib.Path(sys.argv[0]).parent.resolve() / 'proxies.txt', 'r') as file:
        working_proxies = file.read().splitlines()

    if working_proxies:
        # Выбираем случайный рабочий прокси и извлекаем только IP и порт
        selected_proxy = random.choice(working_proxies).split(' - ')[0]  # Извлекаем только прокси без страны
        print(f'Используем прокси для анонимного запроса: {selected_proxy}')
        try:
            response = requests.get('https://httpbin.org/ip',
                                    proxies={"http": f'http://{selected_proxy}', 'https': f'http://{selected_proxy}'},
                                    timeout=5)
            proxy_ip = response.json()['origin']
            print(f'Ваш IP через прокси: {proxy_ip}')

            # Сравниваем IP
            if current_ip != proxy_ip:
                print('Прокси работает, ваш IP изменился.')
            else:
                print('Прокси не изменил ваш IP.')
        except Exception as e:
            print(f'Ошибка при использовании прокси: {e}')
    else:
        print('Нет доступных прокси для анонимного запроса.')

if __name__ == '__main__':
    print(f'Данная программа проверяет список публичных прокси серверов.\nВсе доступные прокси серверы будут в файле `proxies.txt`.')
    use_anonymizer()
