import requests
import os
from bs4 import BeautifulSoup
import urllib3
from pathvalidate import sanitize_filename
import urllib.parse


def download_txt_file(url, filename, folder='books/'):
    response = requests.get(url, verify=False, allow_redirects=True)
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
    response = requests.get(url, verify=False, allow_redirects=False)
    if response.status_code != 200:
        return
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


def parse_book_page(url):
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')
    content = soup.find('div', id='content')
    if not content:
        return
    title_tag = content.find('h1')
    parts_of_title = title_tag.text.split('::')
    img_tag = content.find('div', 'bookimage').find('img')
    comments = []
    comment_tags = soup.find_all('div', 'texts')
    if comment_tags:
        comments = [item.find('span', 'black').text for item in comment_tags]
    book_properties = {
        'name': parts_of_title[0].strip(),
        'autor': parts_of_title[1].strip(),
        'img_url': img_tag.attrs['src'],
        'comments': comments
    }
    return book_properties


def main(root_url):
    for id in range(1, 11):
        book_url = f'{root_url}/b{id}/'
        book_properties = parse_book_page(book_url)
        if not book_properties:
            print(f'Cant parse {book_url} check the url!')
            continue
        book_filename = f'{id}.{book_properties["autor"]}_{book_properties["name"]}.txt'
        try:
            txt_download_url = f'{root_url}/txt.php?id={id}'
            book_filepath = download_txt_file(txt_download_url, book_filename)
            img_download_url = f'{root_url}/{book_properties["img_url"]}'
            img_filepath = download_image(img_download_url)
            if book_properties['comments']:
                write_comments(book_properties['comments'], book_filename)
            print(f'The book data loaded successfully from {book_url}')

        except requests.HTTPError:
            print(f'Book from {book_url} not loaded something was wrong!')


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
main('https://tululu.org')
# print(download_image('https://tululu.org/shots/9.jpg'))
