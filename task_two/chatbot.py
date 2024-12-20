import os
import io
import pandas as pd
from typing import List, Dict

import textwrap
import pprint 
import torch.nn.functional as F
from transformers import logging
from unsloth import FastLanguageModel
from contextlib import redirect_stdout
from transformers import AutoTokenizer, AutoModelForCausalLM

def simple_chatbot(user_query: str, df: pd.DataFrame) -> str:
    # Extract companies and years from the query
    companies = extract_entities(user_query, df["Company"].unique())
    years = extract_entities(user_query, df["Year"].unique())

    # If no companies or years found, return an error message
    if not companies and not years:
        return "I couldn't find any specific company or year in your query. Please try again with more details."

    # Prepare the result based on the query type
    if "total revenue" in user_query.lower():
        result = get_data(df, companies, years, 'Total Revenue')
    elif "net income" in user_query.lower():
        result = get_data(df, companies, years, 'Net Income')
    elif "total assets" in user_query.lower():
        result = get_data(df, companies, years, 'Total Assets')
    elif "total liabilities" in user_query.lower():
        result = get_data(df, companies, years, 'Total Liabilities')
    elif "cashflow" in user_query.lower():
        result = get_data(df, companies, years, 'Cashflow')
    elif "profit margin" in user_query.lower():
        result = get_data(df, companies, years, 'Profit Margin')
    elif "revenue growth" in user_query.lower():
        result = get_data(df, companies, years, 'Revenue Growth (%)')
    elif "profit margin" in user_query.lower():
        result = get_data(df, companies, years, 'Profit Margin')
    elif "return on assets" in user_query.lower():
        result = get_data(df, companies, years, 'ROA')
    elif "debt to equity" in user_query.lower():
        result = get_data(df, companies, years, 'Debt to Equity')
    elif "asset turnover" in user_query.lower():
        result = get_data(df, companies, years, 'Asset Turnover')
    else:
        return "No data specified, please be specific."

    return result

def extract_entities(query: str, entities: List) -> List:
    return [entity for entity in entities if str(entity).lower() in query.lower()]

def get_data(df: pd.DataFrame, companies: List[str], years: List[int], param:str) -> str:
    results = []
    for company in companies:
        for year in years:
            extracted_data = df[
                (df['Year'] == year) & 
                (df['Company'] == company)
            ][param].values
            
            if len(extracted_data) > 0:
                results.append(f"{company} ({year}): {extracted_data[0]:,.2f}")
    
    return f"{param}:\n" + "\n".join(results) if results else "No data found for the specified companies and years."


def llm_response(query:str, response:str):

    # Create a template for the prompt
    prompt = f"Given this query '{query}' and the response '{response}', write out the response in a way that is easy for non technical person to understand"

    # Create a template for the prompt
    return gemma_2B(prompt=prompt)

def gemma_2B(prompt:str):
    with redirect_stdout(io.StringIO()):
        tokenizer = AutoTokenizer.from_pretrained("unsloth/gemma-2-2b-it-bnb-4bit")
        model = AutoModelForCausalLM.from_pretrained("unsloth/gemma-2-2b-it-bnb-4bit")

    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_length=2048, return_dict_in_generate=True)
    
    # Get the length of the input sequence
    input_length = inputs['input_ids'].shape[1]
    
    # Decode the generated sequence, skipping the input tokens
    response = tokenizer.decode(outputs.sequences[0][input_length:], skip_special_tokens=True)

    return response

def print_wrapped(text:str, wrap_length:int=80):
    wrapped_text = textwrap.fill(text, wrap_length)
    print(wrapped_text)