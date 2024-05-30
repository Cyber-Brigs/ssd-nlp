import os
from gensim import corpora
from gensim.models import LsiModel, CoherenceModel
import pickle
import tempfile
import requests
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings

def upload_files_to_azure(local_dir, base_azure_path):
    """
    Uploads all files from a local directory to Azure Blob Storage under the specified base path.
    
    Args:
        local_dir (str): The local directory containing the files to upload.
        base_azure_path (str): The base path in Azure Blob Storage where the files will be uploaded.
    
    Returns:
        list: A list of URLs to the uploaded files.
    """
    uploaded_files = []
    for file_name in os.listdir(local_dir):
        file_path = os.path.join(local_dir, file_name)
        with open(file_path, 'rb') as file_data:
            azure_path = f"{base_azure_path}/{file_name}"
            default_storage.save(azure_path, ContentFile(file_data.read()))
            uploaded_files.append(f"{settings.MEDIA_URL}{azure_path}")
    return uploaded_files

# Function to download file from Azure Blob Storage
def download_file_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    return ContentFile(response.content)
lsa_model_list = []
coherence_values = []

# Define a function to train LDA models and return coherence values
# def train_lsa_models(corpus_path, dictionary_path, processed_texts_path):
def train_lsa_models(processing_instance):
    corpus_url = processing_instance.corpus_path
    dictionary_url = processing_instance.dictionary_path
    processed_texts_url = processing_instance.processed_text_path
    # Download files from Azure Blob Storage
    corpus_file = download_file_from_url(corpus_url)
    dictionary_file = download_file_from_url(dictionary_url)
    processed_text_file = download_file_from_url(processed_texts_url)
    
    start = 1
    limit = 5
    step = 1
    # Load processed texts
    with tempfile.NamedTemporaryFile(delete=False) as temp_texts_file:
        temp_texts_file.write(processed_text_file.read())
        temp_texts_path = temp_texts_file.name
    with open(temp_texts_path, 'rb') as processed_text_file:
        processed_text = pickle.load(processed_text_file)
       
    # Load corpus and dictionary
    with tempfile.NamedTemporaryFile(delete=False) as temp_corpus_file:
        temp_corpus_file.write(corpus_file.read())
        temp_corpus_path = temp_corpus_file.name
    corpus = corpora.MmCorpus(temp_corpus_path)

    with tempfile.NamedTemporaryFile(delete=False) as temp_dict_file:
        temp_dict_file.write(dictionary_file.read())
        temp_dict_path = temp_dict_file.name
    id2word = corpora.Dictionary.load(temp_dict_path)
     
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
    output_file_path = 'topic_models/lsa/'
    lsa_topic_file_name = file_name + "_lsa"
    
    selected_lsa_model = lsa_model_list[model_instance.selected_topics - 1]

    # Save the model to a temporary file
    with tempfile.TemporaryDirectory() as temp_lsa_dir:
        temp_lsa_path =  os.path.join(temp_lsa_dir, lsa_topic_file_name)
        selected_lsa_model.save(temp_lsa_path)
        # Upload all model files to Azure Blob Storage
        uploaded_files = upload_files_to_azure(temp_lsa_dir, output_file_path)
    
    return f'{settings.MEDIA_URL}{output_file_path}{lsa_topic_file_name}', coherence_values[model_instance.selected_topics - 1]
