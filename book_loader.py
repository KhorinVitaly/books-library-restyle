import requests
import os
from bs4 import BeautifulSoup
import urllib3
from pathvalidate import sanitize_filename
import urllib.parse
import argparse
from tqdm import tqdm


def download_txt_file(url, filename, folder='books/'):
    response = requests.get(url, verify=False)
    check_for_redirect(response)
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, sanitize_filename(filename))
    with open(filepath, 'wb') as file:
        file.write(response.content)
    return filepath


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def download_image(url, folder='images/'):
    response = requests.get(url, verify=False)
    check_for_redirect(response)
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
            file.write(comment + os.linesep)
    return filepath


def parse_book_page(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    content_tag = soup.find('div', id='content')

    title_tag = content_tag.find('h1')
    parts_of_title = title_tag.text.split('::')

    img_tag = content_tag.find('div', 'bookimage').find('img')
    comment_tags = soup.find_all('div', 'texts')
    genre_tags = content_tag.find('span', 'd_book').find_all('a')

    book_properties = {
        'name': parts_of_title[0].strip(),
        'autor': parts_of_title[1].strip(),
        'img_url': img_tag.attrs['src'],
        'genres': [item.text for item in genre_tags],
        'comments': [item.find('span', 'black').text for item in comment_tags] if comment_tags else []
    }
    return book_properties


def main(root_url, start_id, end_id):
    for id in tqdm(range(start_id, end_id)):
        book_url = f'{root_url}/b{id}/'
        try:
            response = requests.get(book_url, verify=False)
            check_for_redirect(response)
            book_properties = parse_book_page(response.text)
            book_filename = f'{id}.{book_properties["autor"]} {book_properties["name"]}.txt'
            download_txt_file(f'{root_url}/txt.php?id={id}', book_filename)
            download_image(f'{root_url}/{book_properties["img_url"]}')
            if book_properties['comments']:
                write_comments(book_properties['comments'], book_filename)
            tqdm.write(book_properties['name'])
            tqdm.write(str(book_properties['genres']))

        except requests.HTTPError:
            tqdm.write(f'Book from {book_url} not loaded something was wrong!')


if __name__ == '__main__':
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_id', help='Начальный id книги', default=1)
    parser.add_argument('--end_id', help='Конечный id книги', default=11)
    args = parser.parse_args()
    main('https://tululu.org', args.start_id, args.end_id)
