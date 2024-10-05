## How the ChatBot Works
1. It takes a user query
2. The function looks for any traces for years and company names.
3. If there are no years and company names, the model returns an error. 
4. The model use the company names and the years to select the data the user wants based on certain keywords in the query. 

## Limitations
1. The function requires a pandas dataframe. 
2. The function will return an error message if the neither date or company is specified in the query. 