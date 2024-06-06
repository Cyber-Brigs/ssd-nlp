### NRF SECURE SYSTEMS DESIGN NATURAL LANGUAGE PROCESSOR

This tool is a natural language processor, that allows ordinary language used in Software Requirement Specifications Documents to be parsed and mapped against known threats, mapping such vulnerabilities to the [CAPEC](https://capec.mitre.org) library. The project is built as an innovative solution in the NRF 2024 hackathon themed: _"Harnessing cybersecurity and emerging tech innovation for development, secuurity and empowerment"_

### Objectives
* Implement a natural language processor that rides on srs document uploads to clean text, train models, consume trained mdels and process results that map the mdels to attack patterns/vulnerabilities.
* Develop an API that interfaces a web application with the prcessor via a REST framework.
* Develop a responsive web application that allows user interaction with the tool, by:
  *  Providing a UI for SRS documents upload.
  *  Running initial text processing for the uploaded documents.
  *  Perform model training for LDA and LSA models.
  *  Providing a UI for processing the LDA and LSA model analysis in correlation to CAPEC.
  *  Providing a results view for the LDA and LSA mapped vulnerabilities.

### Technology Stack
##### Backend
The application is primarily implemented with python, with:  
* Django REST Framework
* Python scripts implementing nltk, spacy, gensim and numpy.
##### FrontEnd
The application has utilized ReactJs with a few libraries for charts, grids and display.
Such, the stack is primarily dependent on:
* Vite
* Material UI & TailwindCSS - Styling libraries.
* React Axios - For API Requests
* React Redux -For state management and data persisting
  
These were primarily chosen due to their robustness and feature support, coupled with seasoned experience in their utilization, allowing for a clean and expedited development.
##### Deployment
Both the front end and backend apps are containerized with docker and deployed on Digital Ocean.
Additionally Microsft azure storage spaces offers suppr for uploads, models and results storing.
##### Other Technologies
* Postgresql for DB.
___
## Set Up Instructions
##### Pre-requisites
1. Python version 3.9 or higher.
2. Node version 14 or higher.
3. Postgresql version 12 or higher.
   
To run the project locally:
1. Clone the backend repository.
  `git clone "https://github.com/Cyber-Brigs/ssd-nlp.git"`
2. Install dependencies required for the api and scripts.  
  `pip3 install -r requirements.txt`
4. set up postgresql locally by providing the password and username in a .env file e.g.
    ```
     # .env file
     DB_PASSWORD: '******'
     DB_USERNAME: 'jane'
     DB_PORT: 5432
    ```
5. Run the migrations
   `python3 manage.py migrate`
6. Run pythn server
7. `python3 manage.py runserver`
8. clone the frontend repository.
  `git clone "https://github.com/Cyber-Brigs/ssd-nlp.git"`
1. 
 
  
