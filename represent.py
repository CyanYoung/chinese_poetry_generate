import pickle as pk

import numpy as np

from gensim.models.word2vec import Word2Vec

from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences

from util import flat_read


embed_len = 200
min_freq = 10
max_vocab = 5000
seq_len = 20

bos, eos = '*', '#'

path_word_vec = 'feat/word_vec.pkl'
path_word2ind = 'model/word2ind.pkl'
path_embed = 'feat/embed.pkl'


def add_flag(texts):
    flag_texts = list()
    for text in texts:
        flag_texts.append(bos + text + eos)
    return flag_texts


def shift(flag_texts):
    sents = [text[:-1] for text in flag_texts]
    labels = [text[1:] for text in flag_texts]
    return sents, labels


def word2vec(texts, path_word_vec):
    model = Word2Vec(texts, size=embed_len, window=3, min_count=min_freq, negative=5, iter=10)
    word_vecs = model.wv
    with open(path_word_vec, 'wb') as f:
        pk.dump(word_vecs, f)
    if __name__ == '__main__':
        words = ['，', '。', '*', '#']
        for word in words:
            print(word_vecs.most_similar(word))


def embed(texts, path_word2ind, path_word_vec, path_embed):
    model = Tokenizer(num_words=max_vocab, filters='', char_level=True)
    model.fit_on_texts(texts)
    word_inds = model.word_index
    with open(path_word2ind, 'wb') as f:
        pk.dump(model, f)
    with open(path_word_vec, 'rb') as f:
        word_vecs = pk.load(f)
    vocab = word_vecs.vocab
    vocab_num = min(max_vocab + 1, len(word_inds) + 1)
    embed_mat = np.zeros((vocab_num, embed_len))
    for word, ind in word_inds.items():
        if word in vocab:
            if ind < max_vocab:
                embed_mat[ind] = word_vecs[word]
    with open(path_embed, 'wb') as f:
        pk.dump(embed_mat, f)


def align(sents, path):
    with open(path_word2ind, 'rb') as f:
        model = pk.load(f)
    seqs = model.texts_to_sequences(sents)
    align_seqs = list()
    for seq in seqs:
        while len(seq) > seq_len:
            trunc_seq = seq[:seq_len]
            align_seqs.append(trunc_seq)
            seq = seq[seq_len:]
        pad_seq = pad_sequences([seq], maxlen=seq_len)[0]
        align_seqs.append(pad_seq)
    align_seqs = np.array(align_seqs)
    with open(path, 'wb') as f:
        pk.dump(align_seqs, f)


def vectorize(path_train, path_sent, path_label):
    texts = flat_read(path_train, 'text')
    flag_texts = add_flag(texts)
    word2vec(flag_texts, path_word_vec)
    embed(flag_texts, path_word2ind, path_word_vec, path_embed)
    sents, labels = shift(flag_texts)
    align(sents, path_sent)
    align(labels, path_label)


if __name__ == '__main__':
    path_train = 'data/train.csv'
    path_sent = 'feat/align_seq.pkl'
    path_label = 'feat/align_ind.pkl'
    vectorize(path_train, path_sent, path_label)
