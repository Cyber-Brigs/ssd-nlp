from gensim import corpora
from gensim.models import LdaModel, CoherenceModel
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


lda_model_list = []
coherence_values = []
# Define a function to train LDA models and return coherence values
def train_lda_models(processing_instance):    
    corpus_path = truncate_path(processing_instance.corpus_path.path)
    dictionary_path = truncate_path(processing_instance.dictionary_path.path)
    processed_texts_path = truncate_path(processing_instance.processed_text_path.path)
    start=1
    limit=5
    step=1
    corpus = corpora.MmCorpus(corpus_path)
    id2word = corpora.Dictionary.load(dictionary_path)

    with open(processed_texts_path, 'rb') as processed_text_file:
        processed_text = pickle.load(processed_text_file)
    # Create LDA models with varying number of topics
    for num_topics in range(start, limit + 1, step):
        lda_model = LdaModel(corpus=corpus, id2word=id2word, num_topics=num_topics, random_state=100,
                              update_every=1, chunksize=100, passes=10, alpha='auto', per_word_topics=True)
        coherence_model_lda = CoherenceModel(model=lda_model, texts=processed_text, dictionary=id2word, coherence='c_v')
        lda_model_list.append(lda_model)
        coherence_values.append(coherence_model_lda.get_coherence())
        print(f"Num Topics = {num_topics}, Coherence Score = {round(coherence_model_lda.get_coherence(), 4)}")

    # Prepare data for visualization
    data = {'num_topics': list(range(start, limit + 1, step)),
            'coherence_values': coherence_values}

    return data

# Define a function to save the selected LDA model
def save_selected_lda_model(model_instance, file_name):
    output_file_path = 'media/topic_models/lda/'
    lda_topic_file = output_file_path + file_name + "_lda"  
    print(lda_model_list) 
    selected_lda_model = lda_model_list[model_instance.selected_topics - 1]
    selected_lda_model.save(lda_topic_file)

    return lda_topic_file, coherence_values[model_instance.selected_topics - 1]
