from gensim import corpora
from gensim.models import LsiModel, CoherenceModel
import pickle

def truncate_path(full_path):
    """
    Truncates a full path to start from 'media/uploads/'.
    Args:
        full_path: The full path to truncate.
    Returns:
        The truncated path starting from 'media/uploads/'.
    Todo:
        Implement a better filter to hadle relative paths
    """
    return full_path.split("/home/steve/NRF/media/", 1)[1] if "NRF/" in full_path else full_path

lsa_model_list = []
coherence_values = []
# Define a function to train LDA models and return coherence values
# def train_lsa_models(corpus_path, dictionary_path, processed_texts_path):
def train_lsa_models(processing_instance):
    corpus_path = truncate_path(processing_instance.corpus_path.path)
    dictionary_path = truncate_path(processing_instance.dictionary_path.path)
    processed_texts_path = truncate_path(processing_instance.processed_text_path.path)
    corpus = corpora.MmCorpus(corpus_path)
    id2word = corpora.Dictionary.load(dictionary_path)
    start = 1
    limit = 5
    step = 1
    with open(processed_texts_path, 'rb') as processed_text_file:
        processed_text = pickle.load(processed_text_file)
    for num_topics in range(start, limit + 1, step):
        lsa_model = LsiModel(corpus=corpus, id2word=id2word, num_topics=num_topics, chunksize=100)
        coherence_model_lsa = CoherenceModel(model=lsa_model, texts=processed_text, dictionary=id2word, coherence='c_v')
        lsa_model_list.append(lsa_model)
        coherence_values.append(coherence_model_lsa.get_coherence())
        print(f"Num Topics = {num_topics}, Coherence Score = {round(coherence_model_lsa.get_coherence(), 4)}")

    data = {'num_topics': list(range(start, limit + 1, step)),
            'coherence_values': coherence_values}

    return data

# Define a function to save the selected LSA model
def save_selected_lsa_model(model_instance, file_name):
    output_file_path = 'media/topic_models/lsa/'
    lsa_topic_file = output_file_path + file_name + "_lsa"
    print(lsa_model_list)
    selected_lsa_model = lsa_model_list[model_instance.selected_topics - 1]
    selected_lsa_model.save(lsa_topic_file)

    return lsa_topic_file, coherence_values[model_instance.selected_topics - 1]
