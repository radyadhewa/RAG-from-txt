import ollama

# retrieval dataset / database
dataset = []
with open('retrieve_data/cat-facts.txt', 'r', encoding='utf-8') as file:
  dataset = file.readlines()
  print(f'loaded {len(dataset)} entries')

# ollama model
EMBBEDING_MODEL = "hf.co/CompendiumLabs/bge-base-en-v1.5-gguf"
LANGUAGE_MODEL = "hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF"

# VECTOR DATABASE
# Ollama embedding model will convert each chunk of data to an embedding vector and store the chunk & corresponding vector in list
VECTOR_DB = []

def add_chunk_to_database(chunk):
  embedding = ollama.embed(model=EMBBEDING_MODEL, input=chunk)['embeddings'][0]
  VECTOR_DB.append((chunk, embedding))
  
# each line of data as a chunck
for i, chunk in enumerate(dataset):
  add_chunk_to_database(chunk)
  print(f'added chunk {i+1}/{len(dataset)} to the database')
  

# RETRIEVAL
# returns top N most relevant chunks based on cosine similarity
# the higher the cosine score, the "closer" they are in vector space. Similar in terms of meaning
def cosine_similarity (a, b):
  dot_product = sum([x * y for x, y in zip(a,b)])
  norm_a = sum([x ** 2 for x in a]) ** 0.5
  norm_b = sum([x ** 2 for x in b]) ** 0.5
  return dot_product / (norm_a * norm_b)

# the retrieve function
def retrieve(query, top_n=3):
  query_embbeding = ollama.embed(model=EMBBEDING_MODEL, input=query)['embeddings'][0]
  # temp list to store [chunk, similarity] pairs
  similarities = []
  for chunk, embedding in VECTOR_DB:
    similarity = cosine_similarity(query_embbeding, embedding)
    similarities.append((chunk, similarity))
  # sort similarity in descending order, higher similarity -- more relevant
  similarities.sort(key=lambda x: x[1], reverse=True)
  
  return similarities[:top_n]


# GENERATION 
# chatbot will respone based on the retrieved knowledge, from the step before.
# by adding chunks to the prompt that will be taken as an input for the bot
input_query = input('Ask me a question: ')
retrieved_knowledge = retrieve(input_query)

print('Retrieved knowledge:')
for chunk, similarity in retrieved_knowledge:
  print(f' - (similarity: {similarity:.2f}) {chunk}')

chunks = '\n'.join([f' - {chunk}' for chunk, similarity in retrieved_knowledge])

instruction_prompt = f'''You are a helpful chatbot.
Use only the following pieces of context to answer the question. Don't make up any new information:
{chunks}
'''

# generating response from ollama
stream = ollama.chat(
  model=LANGUAGE_MODEL,
  messages=[
    {'role': 'system', 'content': instruction_prompt},
    {'role': 'user', 'content': input_query},
  ],
  stream=True
)

print('Chatbot response:')
for chunk in stream:
  print(chunk['message']['content'], end='', flush=True)