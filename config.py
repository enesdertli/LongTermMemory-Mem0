# This is a configuration file that uses the Gemini 2.0 Flash, Qdrant vector store and Gemini embedding model.
memory_config = {
    "llm": {
        "provider": "gemini",
        "config": {
            "model": "gemini-2.0-flash",
            "temperature": 0.2,
            "max_tokens": 2000,
        }
    },
    "embedder": {
        "provider": "gemini",
        "config": {
            "model": "models/text-embedding-004",
            "embedding_dims": 1536, 
        },
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "long_term_memory",
            "host": "qdrant",
            "port": 6333,
            "embedding_model_dims": 1536
        }
    },

    "custom_update_memory_prompt": """Only add information that the user explicitly wants remembered (name, specific details, preferences, contextual information)"""
}

# User context configuration
context = {"user_id": "default_user"}
