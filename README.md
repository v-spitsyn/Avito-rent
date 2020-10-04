# Avito-rent
The project presents modelling rent prices of one-bedroom flats in Moscow. The model predicts what a flat's rental cost should be based on its physical parameters (area, floor, subway station, etc).  The data used for modelling were scrapped from a popular classified avito.ru. Below is a description of the project files. 

*Only modelling.ipynb contains comments.  




scraping.py - crawling web-pages of flats and parsing their descriptions

stations.py - parsing coordinates of underground stations and computing their distances to the city center

cleaning.py - constructing a dataframe from the parsed data

modelling.ipynb - short exploratory analysis followed by model training
