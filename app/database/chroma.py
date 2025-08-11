import chromadb
import os
from chromadb.utils import embedding_functions
from dotenv import load_dotenv


load_dotenv()

# Get environment variables
CHROMA_API_KEY = os.getenv("api_key")
CHROMA_TENANT_ID = os.getenv("tenant_id")
CHROMA_DATABASE_NAME = os.getenv("db_name")
COHERE_API_KEY = os.getenv("cohere_api_key")


# Validate environment variables
if not all([CHROMA_API_KEY, CHROMA_TENANT_ID, CHROMA_DATABASE_NAME, COHERE_API_KEY]):
    raise ValueError(
        "Missing required environment variables: api_key, tenant_id, db_name, or cohere_api_key. Check your .env file."
    )

# Initialize Chroma Cloud Client
try:
    client = chromadb.CloudClient(
        api_key=CHROMA_API_KEY,
        tenant=CHROMA_TENANT_ID,
        database=CHROMA_DATABASE_NAME,
    )
except Exception as e:
    print(f"Failed to initialize Chroma Cloud Client: {str(e)}")
    exit(1)

# Initialize Cohere embedding function
try:
    embedding_function = embedding_functions.CohereEmbeddingFunction(
        api_key=COHERE_API_KEY, model_name="embed-english-v3.0"
    )
    # print("Cohere embedding function initialized successfully")
except Exception as e:
    print(f"Error initializing Cohere embedding function: {str(e)}")
    exit(1)

# Get or create collection
collection_name = "text_collection"
try:
    # Attempt to get or create the collection with Cohere embedding
    collection = client.get_or_create_collection(
        name=collection_name, embedding_function=embedding_function
    )
    # print(f"Collection '{collection_name}' retrieved or created successfully")
except Exception as e:
    if "embedding function already exists" in str(e).lower():
        print(
            f"Embedding function conflict for '{collection_name}'. Deleting and recreating with Cohere embedding."
        )
        try:
            client.delete_collection(name=collection_name)
            collection = client.create_collection(
                name=collection_name, embedding_function=embedding_function
            )
            print(
                f"Collection '{collection_name}' recreated successfully with Cohere embedding"
            )
        except Exception as e:
            print(f"Error recreating collection '{collection_name}': {str(e)}")
            exit(1)
    else:
        print(f"Error accessing or creating collection '{collection_name}': {str(e)}")
        exit(1)
