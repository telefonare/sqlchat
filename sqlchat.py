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
    st.sidebar.title('Customization')
    consultante = st.sidebar.text_input("Nombre del consultante:")
    fecha_cons = st.sidebar.date_input("Fecha de Nacimiento:", value="default_value_today", format ="DD/MM/YYYY",min_value=pd.to_datetime("1930-01-01", format="%Y-%m-%d"))
    hora_cons = st.sidebar.time_input("Hora de nacimiento:", value="now")
    lugar = st.sidebar.selectbox(
        'Lugar',
        ['Buenos Aires']
    )

    if consultante:
       st.session_state.consultante = consultante

    if fecha_cons:
        st.session_state.fecha_cons = fecha_cons
    #conversational_memory_length = st.sidebar.slider('Conversational memory length:', 1, 10, value = 5)

    #memory = ConversationBufferWindowMemory(k=conversational_memory_length, memory_key="chat_history", return_messages=True)
    message = None
    if 'userq' in st.session_state:
        print("#2")
        message = st.session_state.userq
        st.session_state.userq = ""




    print("#3",type(fecha_cons))
    user_question = st.text_input("Que quieres preguntar?:",on_change=f_preguntar,key = "userq")
    #print("#4",user_question)
    #message = user_question
    


    if message:
        
        message_data = {
            'role': 'user',
            'content': message
            }
        st.session_state.chat_history.append(message_data)
        #st.session_state.chat_history.append(message)

        # Create a kerykeion instance:
        # Args: Name, year, month, day, hour, minuts, city, nation(optional)
        anio = fecha_cons.year
        mes = fecha_cons.month
        dia = fecha_cons.day
        hora = hora_cons.hour
        minutos = hora_cons.minute
        print("#6",anio,mes,dia,hora,minutos)
        #print(result)
        messages = [
    {"role": "system", "content": f"""You are an agent that can answer business question using data available in a database.
You can access the databasae generatin sql
    """},
 
        ]
        for i,msg in enumerate(st.session_state.chat_history):
            print("#35",type(msg),msg)
            messages.append(msg)

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
        message_data = {
            'role': 'assistant',
            'content': chat_completion.choices[0].message.content
            }
        st.session_state.chat_history.append(message_data)
        
    # session state variable
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history=[]
    else:
        for message in st.session_state.chat_history:
            print("#78", message)
            st.write(f"{message['role']}: {message['content']}" )

    # Crear un cursor
    cur = conn.cursor()

    # Ejecutar una consulta SQL
    cur.execute("SELECT * FROM ipos LIMIT 5")


    # Obtener los resultados
    resultados = cur.fetchall()

    # Imprimir los resultados
    for fila in resultados:
        st.write(fila)

    # No olvides cerrar la conexión cuando hayas terminado
    conn.close()

if __name__ == "__main__":
    main()





