import requests
import os


def download_txt_file(url, filename):
    response = requests.get(url, verify=False, allow_redirects=False)
    response.raise_for_status()
    if response.status_code != 200:
        return
    with open(filename, 'wb') as file:
        file.write(response.content)


def main():
    books_directory_path = 'books'
    os.makedirs(books_directory_path, exist_ok=True)
    for id in range(1, 11):
        url = f'https://tululu.org/txt.php?id={id}'
        filename = f'{books_directory_path}{os.sep}id_{id}.txt'
        download_txt_file(url, filename)


main()
