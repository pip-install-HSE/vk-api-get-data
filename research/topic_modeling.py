import re

import gensim
import pyLDAvis.gensim
import pymorphy2
from gensim.corpora import Dictionary
from textacy import preprocessing
from tqdm import tqdm

from vkapi.wall import get_wall_execute


def example():
    posts = get_wall_execute(domain="rbc", count=5000, max_count=1000, progress=tqdm)
    stopwords = list(map(str.strip, open("stop_words.txt")))
    text_no_urls = map(preprocessing.replace.replace_urls, posts.text.dropna().to_list())
    text_no_punct = map(preprocessing.remove_punctuation, text_no_urls)
    text_no_emojis = map(preprocessing.replace.replace_emojis, text_no_punct)
    text_no_white_space = map(preprocessing.normalize.normalize_whitespace, text_no_emojis)
    docs = map(str.split, text_no_white_space)
    docs = [[word.lower() for word in doc if word not in stopwords] for doc in docs]
    docs = [[word for word in doc if word not in stopwords] for doc in docs]
    dictionary = Dictionary(docs)
    corpus = list(dictionary.doc2bow(text) for text in docs)
    ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=10, id2word=dictionary, passes=15)
    vis = pyLDAvis.gensim.prepare(ldamodel, corpus, dictionary)
    pyLDAvis.show(vis)

def my_realization():
    posts = get_wall_execute(domain="rbc", count=5000, max_count=1000, progress=tqdm)
    morph = pymorphy2.MorphAnalyzer()
    stopwords = list(map(str.strip, open("stop_words.txt")))
    texts = []
    for text in posts.text.dropna().to_list():
        text = re.sub(r'[^\w\s]', '', text)
        emoji_pattern = re.compile("["
                                   u"\U0001F600-\U0001F64F"  # emoticons
                                   u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                   u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                   u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                   "]+", flags=re.UNICODE)
        text = emoji_pattern.sub(r'', text)
        text = re.sub(r'http\S+', '', text)
        text = ' '.join(morph.parse(word.lower())[0].normal_form.lower() for word in text.split())
        text.replace("  ", " ")
        text.replace("\n", "")
        res = [[w.lower()] for w in text.split() if not w.lower() in stopwords]
        texts += res
    dictionary = Dictionary(texts)
    corpus = list(dictionary.doc2bow(t) for t in texts)
    ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=10, id2word=dictionary, passes=15)
    vis = pyLDAvis.gensim.prepare(ldamodel, corpus, dictionary)
    pyLDAvis.show(vis)


if __name__ == "__main__":
    my_realization()
