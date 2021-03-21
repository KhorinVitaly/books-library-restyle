import requests
import os
from bs4 import BeautifulSoup
import urllib3
from pathvalidate import sanitize_filename
import urllib.parse
import argparse
from tqdm import tqdm


def download_txt_file(url, params, filename, folder='books/'):
    response = requests.get(url, verify=False, params=params)
    check_response(response)
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, sanitize_filename(filename))
    with open(filepath, 'wb') as file:
        file.write(response.content)
    return filepath


def check_response(response):
    if response.history or not response.ok:
        raise requests.HTTPError


def download_image(url, folder='images/'):
    response = requests.get(url, verify=False)
    check_response(response)
    os.makedirs(folder, exist_ok=True)
    url_parts = urllib.parse.urlsplit(url, scheme='', allow_fragments=True)
    filename = os.path.basename(url_parts.path)
    filepath = os.path.join(folder, sanitize_filename(filename))
    with open(filepath, 'wb') as file:
        file.write(response.content)
    return filepath


def write_comments(comments, filename, folder='comments/'):
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, sanitize_filename(filename))
    with open(filepath, 'w') as file:
        for comment in comments:
            file.write(f'{comment}{os.linesep}')
    return filepath


def parse_book_page(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    content_tag = soup.find('div', id='content')

    title_tag = content_tag.find('h1')
    name, autor = title_tag.text.split('::')

    img_tag = content_tag.find('div', 'bookimage').find('img')
    comment_tags = soup.find_all('div', 'texts')
    genre_tags = content_tag.find('span', 'd_book').find_all('a')

    book_properties = {
        'name': name.strip(),
        'autor': autor.strip(),
        'img_url': img_tag.attrs['src'],
        'genres': [item.text for item in genre_tags],
        'comments': [item.find('span', 'black').text for item in comment_tags] if comment_tags else []
    }
    return book_properties


def main():
    root_url = 'https://tululu.org'
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_id', help='Начальный id книги', default=1)
    parser.add_argument('--end_id', help='Конечный id книги', default=11)
    args = parser.parse_args()
    for id in tqdm(range(args.start_id, args.end_id)):
        book_url = f'{root_url}/b{id}/'
        try:
            response = requests.get(book_url, verify=False)
            check_response(response)
            book_properties = parse_book_page(response.text)
            book_filename = f'{id}.{book_properties["autor"]} {book_properties["name"]}.txt'
            download_txt_file(f'{root_url}/txt.php', {'id': id}, book_filename)
            download_image(f'{root_url}/{book_properties["img_url"]}')
            if book_properties['comments']:
                write_comments(book_properties['comments'], book_filename)
            tqdm.write(book_properties['name'])
            tqdm.write(str(book_properties['genres']))

        except requests.HTTPError:
            tqdm.write(f'Book from {book_url} not loaded something was wrong!')
        except requests.ConnectionError:
            tqdm.write(f'Error, cant connected to site!')


if __name__ == '__main__':
    main()
