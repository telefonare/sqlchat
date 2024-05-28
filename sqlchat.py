import streamlit as st
import os
from groq import Groq
import random
import sys
import io
import pandas as pd
import sqlite3

def f_preguntar():
    pass #st.title("####1")
    

def main():
    """
    This function is the main entry point of the application. It sets up the Groq client, the Streamlit interface, and handles the chat interaction.
    """
    
    # Get Groq API key
    groq_api_key = os.environ['GROQ_API_KEY']

    # Display the Groq logo
    spacer, col = st.columns([5, 1])  
    #with col:  
    #    st.image('groqcloud_darkmode.png')


    client = Groq(
        api_key=groq_api_key
    )
    print("#gak ",groq_api_key)

    # Crear una conexión a la base de datos SQLite
    conn = sqlite3.connect('test.db')
    
    # The title and greeting message of the Streamlit application
    st.title("SQLChat")
    st.write("Chat with crunchbase data.")
    
    # Add customization options to the sidebar
    st.sidebar.title('Available data (only from 2024):')
    st.sidebar.write('Investors: uuid, name, type')
    st.sidebar.write('Organizations: organization_uuid, name, country_code, state_code, status, category_list, founded_on')
    st.sidebar.write('Funding_rounds: funding_round_uuid, investment_type, announced_on, raised_amount_usd, investor_count, target_org_uuid, target_org_name, lead_investor_uuids')
    st.sidebar.write('Investments: investment_uuid, funding_round_uuid, investor_uuid, investor_type, is_lead_investor')
    st.sidebar.write('Example 1: list of investors and their deal count for 2024 with more than 10 deals')
    st.sidebar.write('Example 2: investor with more investments in 2024')
    message = st.text_input("Ask the database?:",on_change=f_preguntar,key = "userq")

    if message:
        
        message_data = {
            'role': 'user',
            'content': message
            }
        st.session_state.chat_history=[]
        st.session_state.chat_history.append(message_data)
        #st.session_state.chat_history.append(message)


        #print(result)
        messages = [
    {"role": "system", "content": f"""You are an agent that can generate sql code for sqlite 3 to answer a given question in the context of the following data schema which is a simplified version of the crunchbase financial information:

table 'investors' (every investor): ['investor_uuid', 'name', 'type'] (PK: investor_uuid)
table 'organizations' (every target organization): ['organization_uuid', 'name', 'country_code', 'state_code', 'status', 'category_list', 'founded_on'] (PK: organization_uuid)
table 'funding_rounds' (a group of investments, a header for each deal): ['funding_round_uuid', 'investment_type', 'announced_on', 'raised_amount_usd', 'investor_count', 'target_org_uuid', 'target_org_name', 'lead_investor_uuids'] (PK: funding_round_uuid, FK: target_org_uuid on organizations.organization_uuid)
table 'investments' (detail of each funding_round, one line per investor in a funding round): ['investment_uuid', 'funding_round_uuid', 'investor_uuid', 'investor_type', 'is_lead_investor'] (PK: investment_uuid) (FK: funding_round_uuid on funding_rounds.funding_round_uuid) (FK: investor_uuid on investors.funding_round_uuid)

considerations: use investor(name) only in like clauses or comparing strings as parameters, do not use in other cases like filtering with other tables.
Answer only with sql code. No comments, no introductions, no explanations, only sqlcode!
    """},
 
        ]

        messages.append(message_data)

        print("#76")
        #st.title("####2")
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama3-70b-8192",
            temperature=0.9,

            # The maximum number of tokens to generate. Requests can use up to
            # 32,768 tokens shared between prompt and completion.
            max_tokens=1024,
        )
        

        print("#77", type(chat_completion.choices[0].message),chat_completion.choices[0].message.content)
        cur = conn.cursor()
        query = chat_completion.choices[0].message.content.replace('```', '')
        st.write(query)
        cur.execute(query)
        resultados = cur.fetchall()

        dbres = ""
        for fila in resultados:
            st.write(fila)
            dbres += str(fila)
        print("#33 ",query,dbres)

        messages = [
    {"role": "system", "content": f"""You are an assistan that answers financial questions based on crunchbase public data, a query and the answer to the query.
Your objective is to take all those elements and elaborate a valid answer to the final user.

The data schema:

table 'investors' (every investor): ['investor_uuid', 'name', 'type'] (PK: investor_uuid)
table 'organizations' (every target organization): ['organization_uuid', 'name', 'country_code', 'state_code', 'status', 'category_list', 'founded_on'] (PK: organization_uuid)
table 'funding_rounds' (a group of investments, a header for each deal): ['funding_round_uuid', 'investment_type', 'announced_on', 'raised_amount_usd', 'investor_count', 'target_org_uuid', 'target_org_name', 'lead_investor_uuids'] (PK: funding_round_uuid, FK: target_org_uuid on organizations.organization_uuid)
table 'investments' (detail of each funding_round, one line per investor in a funding round): ['investment_uuid', 'funding_round_uuid', 'investor_uuid', 'investor_type', 'is_lead_investor'] (PK: investment_uuid) (FK: funding_round_uuid on funding_rounds.funding_round_uuid) (FK: investor_uuid on investors.funding_round_uuid)

the query used:
{query}

the answer from the query:
{dbres}
    """},
 
        ]
        
        
        messages.append(message_data)

        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama3-70b-8192",
            temperature=0.9,

            # The maximum number of tokens to generate. Requests can use up to
            # 32,768 tokens shared between prompt and completion.
            max_tokens=1024,
        )
        
            
        message_data = {
            'role': 'assistant',
            'content': chat_completion.choices[0].message.content
            }
        st.session_state.chat_history.append(message_data)
        st.write(chat_completion.choices[0].message.content)
        
        
    # session state variable
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history=[]
    else:
        for message in st.session_state.chat_history:
            print("#78", message)
            #st.write(f"{message['role']}: {message['content']}" )



    # No olvides cerrar la conexión cuando hayas terminado
    conn.close()

if __name__ == "__main__":
    main()





