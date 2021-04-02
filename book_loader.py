from typing import Dict, List, NamedTuple
import requests
from bs4 import BeautifulSoup
import urllib3
import urllib.parse
from tqdm import tqdm
import json
import argparse
import os
import pathvalidate
from typing import Union
from datetime import datetime

ROOT_URL = 'https://tululu.org'
BOOK_CATEGORY = 'l55'


def fetch_book_data(book_url: str, id: int, dest_folder: str, skip_imgs: bool, skip_txt: bool) -> Union[Dict, None]:
    try:
        response = requests.get(book_url, verify=False)
        check_response(response)
        book_properties = parse_book_page(response.text)
        book_filename = f'{id}.{book_properties["autor"]} {book_properties["name"]}.txt'
        if not skip_txt:
            url_for_txt_download = urllib.parse.urljoin(ROOT_URL, 'txt.php')
            book_path = download_txt_file(url_for_txt_download, {'id': id}, book_filename, dest_folder)
            book_properties['book_path'] = book_path
        if not skip_imgs:
            url_for_image_download = urllib.parse.urljoin(ROOT_URL, book_properties["img_url"])
            download_image(url_for_image_download, dest_folder)
        return book_properties
    except requests.HTTPError as e:
        tqdm.write(f'Book from {book_url} not loaded something was wrong: {str(e)}')
    except requests.ConnectionError:
        tqdm.write(f'Error, cant connected to site!')


def write_to_json_file(data: List, filepath: str) -> None:
    with open(filepath, "w", encoding='utf8') as my_file:
        json.dump(data, my_file, ensure_ascii=False, sort_keys=True, indent=4)


def download_txt_file(url: str, params: Dict, filename: str, folder: str) -> str:
    response = requests.get(url, verify=False, params=params)
    check_response(response)
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, pathvalidate.sanitize_filename(filename))
    with open(filepath, 'w') as file:
        file.write(response.text)
    return filepath


def check_response(response: requests.Response) -> None:
    response.raise_for_status()
    if response.history:
        raise requests.HTTPError('Error: redirect detected!')


def download_image(url: str, folder: str) -> str:
    response = requests.get(url, verify=False)
    check_response(response)
    os.makedirs(folder, exist_ok=True)
    url_parts = urllib.parse.urlsplit(url, scheme='', allow_fragments=True)
    timestamp = datetime.now().timestamp()
    filename = f'{timestamp}-{os.path.basename(url_parts.path)}'
    filepath = os.path.join(folder, pathvalidate.sanitize_filename(filename))
    with open(filepath, 'wb') as file:
        file.write(response.content)
    return filepath


def parse_book_page(html_text: str) -> Dict:
    soup = BeautifulSoup(html_text, 'html.parser')
    title_tag = soup.select_one('#content h1')
    name, autor = title_tag.text.split('::')
    img_tag = soup.select_one('#content .bookimage img')
    comment_tags = soup.select('.texts span.black')
    genre_tags = soup.select('span.d_book a')

    book_properties = {
        'name': name.strip(),
        'autor': autor.strip(),
        'img_url': img_tag.attrs['src'],
        'genres': [item.text for item in genre_tags],
        'comments': [item.text for item in comment_tags]
    }
    return book_properties


def parse_command_line_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_page', help='Номер начальной страницы', default=1, type=int)
    parser.add_argument('--end_page', help='Номер конечной страницы', default=701, type=int)
    parser.add_argument('--dest_folder', help='Путь каталогу для сохранения данных', default='parse_results', type=str)
    parser.add_argument('--skip_imgs', help='Не скачивать обложки', action='store_true')
    parser.add_argument('--skip_txt', help='Не скачивать текст книги', action='store_true')
    parser.add_argument('--json_path', help='Путь к файлу с результатами парсинга', default='books.json', type=str)
    return parser.parse_args()


def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    args = parse_command_line_arguments()
    books_of_category = []
    for i in tqdm(range(args.start_page, args.end_page), desc='Pages'):
        category_url = urllib.parse.urljoin(ROOT_URL, BOOK_CATEGORY, i)
        response = requests.get(category_url, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        links_to_books = soup.select('.d_book .bookimage a')
        for tag in tqdm(links_to_books, desc=f'Books on page({i})'):
            href = tag.attrs['href']
            book_url = urllib.parse.urljoin(ROOT_URL, href)
            id = int(href.replace('b', '').replace('/', ''))
            book_properties = fetch_book_data(book_url, id, args.dest_folder, args.skip_imgs, args.skip_txt)
            if book_properties:
                books_of_category.append(book_properties)

    write_to_json_file(books_of_category, args.json_path)


if __name__ == '__main__':
    main()
