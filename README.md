# books-library-restyle

Скрипты для парсинга онлайн библиотеки [tululu](https://tululu.org).

## Запуск

Для запуска у вас должен быть установлен Python 3.

Установите зависимости:

```sh
$ pip install -r requirements.txt
```

Выберите и запустите скрипт:

```sh
$ python3 book_loader.py
```

Предназначен для скачивания книг с указанием диапазона с помощью начального и конечного id книги.

```sh
$ python3 parse_tululu_category.py
```

Предназначен для скачивания книг в категории "научная фантастика". Позволяеет гибко указать параметры для загрузки данных.

## Параметры

Скрипт book_loader.py принимает необязательные параметры (start_id, end_id), с помощью которых можно указать какие именно книги необходимо загрузить.

Для указания параметров добавьте в вызов скрипта начальный и конечный id вот таким образом:
```sh
$ python3 book_loader.py 30 50
```

Если параметры не переданы, то по умолчанию будут загружены книги с 1 по 10 id включительно.

Скрипт parse_tululu_category.py принимает следующие необязательные параметры:

* Номер начальной (--start_page) и конечной страницы (--end_page) для обработки, в категории "научная фантастика". По умолчанию с 1 по 10 страницу;
* Путь к каталогу с загруженными данными (--dest_folder), по молчанию "parse_results" в текущем каталоге;
* Не загружать обложки (0  или 1) (--skip_imgs), по умолчанию 0;
* Не загружать тексты книг (0 или 1) (--skip_txt), по умолчанию 0;
* Путь к json файлу с результатами парсинга (--json_path), по умолчанию "books.json" в текущем каталоге;

```sh
$ python3 parse_tululu_category.py --skip_txt 1 --skip_imgs 1
```

## Цели проекта

Код написан в учебных целях — это урок в курсе по верстке для Python разработчика на сайте [Devman](https://dvmn.org).
