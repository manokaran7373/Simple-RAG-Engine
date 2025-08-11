import os
from dotenv import load_dotenv
import google.generativeai as genai
from better_profanity import profanity
from database.chroma import collection

load_dotenv()

# Set up Gemini API key
GEMINI_API_KEY = os.getenv("gemini_api_key")

genai.configure(api_key=GEMINI_API_KEY)

# Choose a Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")

# Get user query
query = input("Enter your query: ").strip()
if not query:
    print("Error: Query cannot be empty.")
    exit(1)

if profanity.contains_profanity(query):
    print(
        "I'm sorry, but your query contains inappropriate language. Please rephrase it respectfully, and I'd be happy to assist with any questions related to our knowledge base."
    )

else:

    # Perform similarity search in vector DB
    try:
        results = collection.query(query_texts=[query], n_results=1)
        retrieved_doc = ""
        retrieved_meta = {}
        if results["documents"] and results["documents"][0]:
            retrieved_doc = results["documents"][0][0]
            retrieved_meta = results["metadatas"][0][0] if results["metadatas"] else {}
        else:
            print("No relevant documents found in the vector DB.")

        # Construct a professional prompt for LLM that handles all cases
        prompt = f"""
        You are a professional AI assistant for the AI Reader mobile application, designed to help users with queries related to documents and knowledge in the database. Your responses should always be polite, helpful, concise, and professional. Do not use casual language like emojis or slang.

        First, analyze the user's query:
        - If the query is a greeting (e.g., "hi", "hello", "hey", "good morning", "bye", "goodbye") or casual conversation starter without a specific question, respond warmly but professionally, e.g., "Hello! I'm the AI assistant for AI Reader. How can I assist you today?" Do not provide any enhanced knowledge response in this case.
        - If the query is irrelevant to the retrieved knowledge (i.e., the retrieved document does not meaningfully relate to or answer the query), or if no document was retrieved, respond: "I'm sorry, but your query doesn't seem relevant to the available documents in our knowledge base.
        - If the retrieved knowledge is relevant, use it to provide a clear, enhanced, and informative response to the query. Summarize key points, explain concepts if needed, and make the answer engaging and easy to understand. Always base your answer on the retrieved knowledge and metadata if useful.

        Retrieved Knowledge (use only if relevant):
        {retrieved_doc}
        
        Metadata (if useful): {retrieved_meta}
        
        User Query: {query}
        
        Provide only the final response to the user. Do not include any internal reasoning, prompts, or extra text.
        """

        # Send to Gemini LLM
        response = model.generate_content(prompt)

        # Print the enhanced response
        # print("\nEnhanced Response from LLM:")
        print(response.text)

    except Exception as e:
        print(f"Error querying collection or LLM: {str(e)}")
        exit(1)
