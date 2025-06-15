from sentence_transformers import SentenceTransformer
from loguru import logger
from tqdm import tqdm

from io import BytesIO
import requests
from PIL import Image



def test_embeddings():
    model = SentenceTransformer('all-MiniLM-L6-v2')

    sentences = ["This is a test sentence", "This is another sentence", "Yet another example sentence", "I am a dog", "I am a dog"]
    embeddings = model.encode(sentences)
    logger.info(f"Embeddings generated successfully: {embeddings.shape}")

    for i, embedding in enumerate(embeddings):
        logger.info(f"Embedding for sentence {i}: {embedding}")

    # calculate the cosine similarity between the embeddings
    similarity = model.similarity(embeddings, embeddings)
    logger.info(f"Similarity matrix generated successfully: {similarity.shape}")
    logger.info(f"Similarity matrix: {similarity}")
    for i in tqdm(range(len(sentences))):
        for j in range(i + 1, len(sentences)):
            sim = model.similarity(embeddings[i], embeddings[j])
            logger.info(f"Similarity between sentence {i} and {j}: {sim}")


def image_embedding():
    response = requests.get("https://github.com/PacktPublishing/LLM-Engineering/blob/main/images/crazy_cat.jpg?raw=true")
    image = Image.open(BytesIO(response.content))
    model = SentenceTransformer('clip-ViT-B-32')
    embedding = model.encode(image, convert_to_tensor=True)
    logger.info(f"Image embedding generated successfully: {embedding.shape}")

    text_emb = model.encode(["A crazy cat smiling.",
                             "A white and brown cat with a yellow bandana.",
                             "A man eatin in the garden."])
    
    logger.info(f"Text embedding generated successfully: {text_emb.shape}")

    similarity = model.similarity(embedding, text_emb)
    logger.info(f"Similarity between image and text embeddings: {similarity}")


if __name__ == "__main__":
    #test_embeddings()
    image_embedding()