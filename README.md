### NRF SECURE SYSTEMS DESIGN NATURAL LANGUAGE PROCESSOR

This tool is a natural language processor, that allows ordinary language used in Software Requirement Specifications Documents to be parsed and mapped against known threats, mapping such vulnerabilities to the [CAPEC](https://capec.mitre.org) library. The project is built as an innovative solution in the NRF 2024 hackathon themed: _"Harnessing cybersecurity and emerging tech innovation for development, secuurity and empowerment"_
___

### Objectives
* Implement a natural language processor that rides on srs document uploads to clean text, train models, consume trained mdels and process results that map the mdels to attack patterns/vulnerabilities.
* Develop an API that interfaces a web application with the prcessor via a REST framework.
* Develop a responsive web application that allows user interaction with the tool, by:
  *  Providing a UI for SRS documents upload.
  *  Running initial text processing for the uploaded documents.
  *  Perform model training for LDA and LSA models.
  *  Providing a UI for processing the LDA and LSA model analysis in correlation to CAPEC.
  *  Providing a results view for the LDA and LSA mapped vulnerabilities.
___

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
6. Run python server to start the app
7. `python3 manage.py runserver`
8. clone the frontend repository.
  `git clone "https://github.com/Cyber-Brigs/ssd-nlp.git"`
1. Install all packages required to run the app
   `npm i`
2. Run the app
   `npm run dev`
The application can now be accesses on a local server at port 5173

Alternatively, a deployed version of this application is already deployed as an instance on digital ocean and can be accessed by [ visiting the site.](https://nrf-cyberbrigs-nlp-web-gdsm9.ondigitalocean.app/)

___
#### Application Utilization
To get started:
1. You are required to ceate a user account.
2. On success, use the credentials to log in to the application.
3. The first page is a metrics dashboard that gives an overview of action and user specific data an shall be udated dynamically on tool utilization.
4. The entry point of tool utilization shall entail uploading a Software Requirements Specifications Document from the upload srs page.
5.We recommend doing a preview  of the uploaded document and note the pages you'd like to be processed, ensuring it is the correct version, thereby noting the starting  page of content in the doc, and the last page you'd like processed.
Next, process to run the text preprocesing from the short menu.
6. On text preprocessing, the  document is available for model training using LSA or LDA, and is done using a short action menu.
7. Follow the prompts on the page to complete model training.
8. Ultimately, the trained model can now be used to process and view results as from the LSA anlysis and LDA analysis side menus.
   
___
_Author: Stephen Muliru Lukanu_
_Version: v1.0.0_
___