"""FILE FOR TEXT PREPROCESSING SRS DOCUMENTS"""
# PyMuPDF python Library
import re
import fitz
import string
import pickle
import spacy
import gensim
from gensim import corpora
from gensim.utils import simple_preprocess
from nltk.corpus import stopwords
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
import tempfile

# Initialize SpaCy and Gensim
stopWords = stopwords.words('english')
stopWords.extend(["from", "subject", "re", "edu", "use"])
nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])

# FILE PATHS
CORPUS_FILE_PATH = 'processed_files/corpora/'
DICTIONARY_FILE_PATH = 'dictionaries/'
PROCESSED_TEXT_FILE_PATH = 'processed_files/texts/'

def remove_punctuation(supplied_text):
    translator = str.maketrans('', '', string.punctuation)
    return supplied_text.translate(translator)

def remove_whitespaces(supplied_text):
    return " ".join(supplied_text.split())

def sent_to_words(sentences):
    for sentence in sentences:
        yield gensim.utils.simple_preprocess(str(sentence), deacc=True)

def remove_stopwords(supplied_text):
    return [[word for word in simple_preprocess(str(doc)) if word not in stopWords] for doc in supplied_text]

def lemmatization(supplied_text, allowed_pos=["NOUN", "ADJ", "VERB", "ADV"]):
    text_out = []
    for sent in supplied_text:
        doc = nlp(" ".join(sent))
        text_out.append([token.lemma_ for token in doc if token.pos_ in allowed_pos])
    return text_out

def process_pdf(file_obj, start_page, end_page, original_filename):
    processed_text = []
    pdf = fitz.open(stream=file_obj.read(), filetype="pdf")
    for x in range(start_page, end_page):
        page = pdf.load_page(x)
        text = page.get_text("text")

        # Convert text to lowercase
        text = text.lower()
        # Remove numbers
        text = re.sub(r'\d+', '', text)
        # Remove punctuation
        text = remove_punctuation(text)
        # Remove whitespaces
        text = remove_whitespaces(text)
        text = list(text.split(" "))
        text = list(filter(None, text))
        processed_text.append(text)

    data_words = list(sent_to_words(processed_text))
    # REMOVE DEFAULT STOPWORDS
    data_words_no_stops = remove_stopwords(data_words)
    bigram = gensim.models.Phrases(data_words_no_stops, min_count=5, threshold=100)
    trigram = gensim.models.Phrases(bigram[data_words_no_stops], min_count=5, threshold=100)

    bigram_model = gensim.models.phrases.Phraser(bigram)
    trigram_model = gensim.models.phrases.Phraser(trigram)

    data_words_bigrams = [bigram_model[doc] for doc in data_words_no_stops]
    data_words_trigrams = [x for x in data_words_bigrams if x != []]
    #Lemmatization
    lemma = lemmatization(data_words_bigrams, allowed_pos=['NOUN', 'ADJ', 'VERB', 'ADV'])

    id2word = corpora.Dictionary(lemma)
    
    corpus = [id2word.doc2bow(word) for word in lemma]
    
    # SAVED RESULTS FILE NAMES
    corpus_file_name = original_filename + '_corpus'
    dictionary_file_name = original_filename + '_dictionary'
    texts_file_name = original_filename+ '_text'
    # Serialize corpus to a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_corpus_file:
        temp_corpus_path = temp_corpus_file.name
    corpora.MmCorpus.serialize(temp_corpus_path, corpus)
    # Save the serialized corpus to Azure Blob Storage
    with open(temp_corpus_path, 'rb') as corpus_file:
        corpus_content = ContentFile(corpus_file.read())
        corpus_path = default_storage.save(f'processed_files/corpora/{corpus_file_name}', corpus_content)
    
    # Serialize dictionary to a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_dict_file:
        temp_dict_path = temp_dict_file.name
    id2word.save(temp_dict_path)
     # Save the serialized dictionary to Azure Blob Storage
    with open(temp_dict_path, 'rb') as dict_file:
        dict_content = ContentFile(dict_file.read())
        dictionary_path = default_storage.save(f'processed_files/dictionaries/{dictionary_file_name}', dict_content)
    
    # Serialize the lemma to bytes and save it to Azure Blob Storage
    texts_bytes = ContentFile(pickle.dumps(lemma))
    texts_path = default_storage.save(f'processed_files/texts/{texts_file_name}', texts_bytes)

    return (f'{settings.MEDIA_URL}processed_files/corpora/{corpus_file_name}',
            f'{settings.MEDIA_URL}processed_files/dictionaries/{dictionary_file_name}',
            f'{settings.MEDIA_URL}processed_files/texts/{texts_file_name}')
