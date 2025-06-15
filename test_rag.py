import ollama
import pickle
import os

# ollama model
EMBBEDING_MODEL = "hf.co/CompendiumLabs/bge-base-en-v1.5-gguf"
LANGUAGE_MODEL = "hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF"

# VECTOR DATABASE
VECTOR_DB_PATH = 'rag_db.pkl'

# retrieval dataset / database
def load_vector_db():
    VECTOR_DB_PATH = 'rag_db.pkl'
    if os.path.exists(VECTOR_DB_PATH):
        with open(VECTOR_DB_PATH, 'rb') as f:
            VECTOR_DB = pickle.load(f)
        print(f'Loaded existing vector database with {len(VECTOR_DB)} chunks')
        return VECTOR_DB
    else:
        dataset = []

        with open('retrieve_data/database.txt', 'r', encoding='utf-8') as file:
            retrieval1 = file.readlines()
            print(f'loaded {len(retrieval1)} entries from database.txt')
            dataset.extend(retrieval1)

        with open('retrieve_data/scraped_texts.txt', 'r', encoding='utf-8') as file:
            retrieval2 = file.readlines()
            print(f'loaded {len(retrieval2)} entries from scraped_texts.txt')
            dataset.extend(retrieval2)

        # Ollama embedding model will convert each chunk of data to an embedding vector and store the chunk & corresponding vector in list
        VECTOR_DB = []
        
        # each line of data as a chunck
        for i, chunk in enumerate(dataset):
            embedding = ollama.embed(model=EMBBEDING_MODEL, input=chunk)['embeddings'][0]
            VECTOR_DB.append((chunk, embedding))
            print(f'added chunk {i+1}/{len(dataset)} to the database')

        # Save to disk
        with open(VECTOR_DB_PATH, 'wb') as f:
            pickle.dump(VECTOR_DB, f)
        print(f'Saved vector database with {len(VECTOR_DB)} chunks')
        return VECTOR_DB

VECTOR_DB = load_vector_db()

# RETRIEVAL
# returns top N most relevant chunks based on cosine similarity
# the higher the cosine score, the "closer" they are in vector space. Similar in terms of meaning
def cosine_similarity (a, b):
  dot_product = sum([x * y for x, y in zip(a,b)])
  norm_a = sum([x ** 2 for x in a]) ** 0.5
  norm_b = sum([x ** 2 for x in b]) ** 0.5
  return dot_product / (norm_a * norm_b)

# the retrieve function
def retrieve(query, vector_db, top_n=3):
  top_n = int(top_n)
  query_embbeding = ollama.embed(model=EMBBEDING_MODEL, input=query)['embeddings'][0]
  # temp list to store [chunk, similarity] pairs
  similarities = []
  for chunk, embedding in vector_db:
    similarity = cosine_similarity(query_embbeding, embedding)
    similarities.append((chunk, similarity))
  # sort similarity in descending order, higher similarity -- more relevant
  similarities.sort(key=lambda x: x[1], reverse=True)
  
  return similarities[:top_n]


# GENERATION 
# chatbot will respone based on the retrieved knowledge, from the step before.
# by adding chunks to the prompt that will be taken as an input for the bot
chat_history = []

while True:
    input_query = input('\nYou: ')
    if input_query.lower() in ['exit', 'quit']:
        print("Goodbye!")
        break

    retrieved_knowledge = retrieve(input_query, VECTOR_DB)

    print('Retrieved knowledge:')
    for chunk, similarity in retrieved_knowledge:
        print(f' - (similarity: {similarity:.2f}) {chunk}')

    chunks = '\n'.join([f' - {chunk.strip()}' for chunk, similarity in retrieved_knowledge])

    instruction_prompt = f'''You are a helpful assistant. 
Answer the user's question using **only** the information provided in the context below. 
Do not add anything else or make assumptions.

CONTEXT:
{chunks}

If the answer is not in the context, reply with: "Maaf, informasi tersebut belum tersedia."
'''

    # build the messages list with chat history
    messages = [{'role': 'system', 'content': instruction_prompt}] + chat_history
    messages.append({'role': 'user', 'content': input_query})

    # generate response from ollama
    stream = ollama.chat(model=LANGUAGE_MODEL, messages=messages, stream=True)

    print('Bot:', end=' ')
    bot_reply = ''
    for chunk in stream:
        content = chunk['message']['content']
        print(content, end='', flush=True)
        bot_reply += content

    # update chat history
    chat_history.append({'role': 'user', 'content': input_query})
    chat_history.append({'role': 'assistant', 'content': bot_reply})