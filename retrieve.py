import json

import re


path_poetry = 'dict/poetry.json'


def retrieve(path_poetry):
    with open(path_poetry, 'r') as f:
        poetry = json.load(f)
    poet = input('poet: ')
    if poet in poetry:
        key = input('title: ')
        titles = list()
        texts = list()
        for cand in poetry[poet].keys():
            if re.findall(key, cand):
                titles.append(cand)
                texts.extend(poetry[poet][cand])
        if titles:
            for title, text in zip(titles, texts):
                print('%s：%s' % (title, text))
        else:
            print('invalid title')
    else:
        print('invalid poet')


if __name__ == '__main__':
    while True:
        retrieve(path_poetry)