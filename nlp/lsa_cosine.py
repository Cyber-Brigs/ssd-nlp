import os
import copy
import gensim
import pandas as pd
import gensim.corpora as corpora
import requests
import tempfile
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

def download_file(url, local_filename):
    """
    Download a file from a URL and save it locally.
    """
    response = requests.get(url)
    if response.status_code == 200:
        with open(local_filename, 'wb') as f:
            f.write(response.content)
    else:
        raise RuntimeError(f"Failed to download file: {url}")

def load_lsa_model_from_url(base_url):
    """
    Download LSA model files from a given base URL and load the model using gensim.
    Args:
        base_url (str): The base URL where the model files are stored.
    Returns:
        gensim.models.LsiModel: The loaded LSA model.
    """
    # Extract the model name from the base URL
    model_name = os.path.basename(base_url)
    # Create a temporary directory to store downloaded files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Define URLs for each file
        model_url = f"{base_url}"
        projection_url = f"{base_url}.projection"
        
        # Define local file paths
        model_path = os.path.join(temp_dir, model_name)
        projection_path = os.path.join(temp_dir, f"{model_name}.projection")
        
        # Download each file
        download_file(model_url, model_path)
        download_file(projection_url, projection_path)
        
        # Load the LDA model from the temporary directory
        lsa_model = gensim.models.LsiModel.load(model_path)
    
    return lsa_model

# Function to download file from Azure Blob Storage
def download_file_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    return ContentFile(response.content)

def truncate_path(full_path):
    """
    Truncates a full path to start from 'media/'.
    Args:
        full_path: The full path to truncate.
    Returns:
        The truncated path starting from 'media/uploads/'.
    Todo:
        Implement a better filter to hadle relative paths
    """
    return full_path.split("/home/steve/NRF/media/", 1)[1] if "NRF/" in full_path else full_path

def calculate_cosine_similarity_lsa(lsa_srs_num_topics, lsa_vector, capec_vector_list_lsa, lsa_cosine_result_list):
    lsa_result = {}
    for y in range(0, lsa_srs_num_topics):
        for z in range(0, 544):
            lsa_result.update({z: gensim.matutils.cossim(lsa_vector[y], capec_vector_list_lsa[z])})
        lsa_cosine_result_list.append(copy.deepcopy(lsa_result))
        lsa_result.clear()

# returns a list
def lsa_get_topic_terms(models_dictionary, topicid, topwords,lsa_model):
    lsa_show_topics = lsa_model.show_topic(topicno=topicid, topn=topwords)
    lsa_topic_terms = []
    # ISSUES WITH LOOP
    for pair in lsa_show_topics:
        for wordID in models_dictionary:
            if models_dictionary[wordID] in pair[0] and models_dictionary[wordID] == pair[0]:
                lsa_topic_terms.append((wordID, abs(pair[1])))
    return copy.deepcopy(lsa_topic_terms)
       
def create_CAPEC_vectors_lsa(models_dictionary):
    capec_vector = []
    capec_number = 1
    vector_list = []
    for x in range(1, 545):
        capec_lsa = gensim.models.LsiModel.load("nlp/CAPEC/LSA/capec_lsa_" + str(capec_number))
        for topic_number in range(0, len(capec_lsa.get_topics())):
            capec_vector.extend(lsa_get_topic_terms(models_dictionary, topicid=topic_number,topwords=10,lsa_model=capec_lsa))
        vector_list.append(capec_vector[:])
        capec_vector.clear()
        capec_number += 1
    return vector_list

def get_CAPEC_IDs(capec_list):
    CAPEC_IDs = pd.read_csv("nlp/CAPEC/Comprehensive CAPEC Dictionary.csv", usecols=["ID"])
    list_with_topics_and_capec_ids = []
    for pattern in capec_list:
        topic_list = []
        for value in pattern:
            index = value[0] - 1
            new_tuple = tuple((CAPEC_IDs.iloc[index].values[0], value[1]))
            topic_list.append(new_tuple)
        list_with_topics_and_capec_ids.append(copy.deepcopy(topic_list))
    return list_with_topics_and_capec_ids

def generate_lsa_capec_results(text_processing_instace, file_name, lsa_file_path):
    """
    Runs lsa analysis and maps vulnerabilities in document to CAPEC Lib.
    Args:
        text_processing_instace: Instance of relevant a text processing.
        file_name: Name for the specific document in process.
        lsa_file_path: Path to the directory with specific lsa_file.
    Returns:
        LSA matching attack patterns.
    """
    dictionary_url = text_processing_instace.dictionary_path
    dictionary_file = download_file_from_url(dictionary_url)

    with tempfile.NamedTemporaryFile(delete=False) as temp_dict_file:
        temp_dict_file.write(dictionary_file.read())
        temp_dict_path = temp_dict_file.name
    models_dictionary = corpora.Dictionary.load(temp_dict_path)
    lsa_vector = []
    srs_lsa = load_lsa_model_from_url(f'{lsa_file_path}')
    lsa_srs_num_topics = len(srs_lsa.get_topics())
    
    # i. Load in the LSA model from the SRS document into lsa_vector
    for topic_num in range(0, lsa_srs_num_topics):
        lsa_vector.append(lsa_get_topic_terms(models_dictionary=models_dictionary, topicid=topic_num, topwords=30, lsa_model=srs_lsa))
    
    # ii. Load in the capec lsa models into vectors
    capec_vector_list_lsa = create_CAPEC_vectors_lsa(models_dictionary)
    lsa_cosine_result_list = []
    calculate_cosine_similarity_lsa(lsa_srs_num_topics, lsa_vector, capec_vector_list_lsa, lsa_cosine_result_list)
    
    # iii. Sort the values of the list from highest similarity value to lowest similarity value.
    lsa_sorted_lists = []
    for y in range(0, lsa_srs_num_topics):
        lsa_sorted_lists.append(sorted(lsa_cosine_result_list[y].items(), key=lambda x: x[1], reverse=True))
        
    # iv. Returns a new list with the CAPEC IDS of the Attack Pattern for all topics
    lsa_result = get_CAPEC_IDs(lsa_sorted_lists)
    
    # v. Convert the list of lists into a Pandas Dataframe. For easier manipulation.
    pandas_frame_lsa = pd.DataFrame(lsa_result)
    
    # vi. Transpose the Data Frame
    pandas_frame_lsa = pandas_frame_lsa.transpose()
    top_LSA_patterns = {}
    for topic in range(0, lsa_srs_num_topics):
        items_added = 0
        for values in lsa_result[topic]:
            if items_added == 20:
                break
            if not (values[0] in top_LSA_patterns):
                top_LSA_patterns[values[0]] = values[1]
                items_added += 1
            else:
                top_LSA_patterns[values[0]] = max(values[1], top_LSA_patterns[values[0]])
                
    lsa_top_results = [(k, v) for k, v in top_LSA_patterns.items()]
    lsa_top_results = sorted(lsa_top_results, key=lambda x: x[1], reverse=True)
    
    # vii. Rename the columns of the Pandas DataFrame
    for x in range(0, lsa_srs_num_topics):
        pandas_frame_lsa.rename(columns={x: "Topic-" + str(x + 1)}, inplace=True)

    # Save the results to a csv file.
    output_file_path = 'similarity_results/lsa/'
    lsa_results_file = output_file_path  + file_name + '_lsa.csv'
    # Save the DataFrame to a temporary CSV file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_csv_file:
        pandas_frame_lsa.to_csv(temp_csv_file.name, encoding="utf-8", index=False)
        temp_csv_path = temp_csv_file.name
    # Read the CSV file content and save it to Azure Blob Storage
    with open(temp_csv_path, 'rb') as csv_file:
        csv_content = ContentFile(csv_file.read())
        default_storage.save(lsa_results_file, csv_content)

    # Clean up the temporary file
    os.remove(temp_csv_path)
    
    formatted_results = [{'capec_id': int(item[0]), 'coherence': float(item[1])} for item in lsa_top_results[:10]]

    return formatted_results
