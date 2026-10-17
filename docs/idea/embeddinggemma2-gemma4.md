Skip to main contentAccessibility help
AI Mode
All
Images
News
Videos
More
Upgrade




embeddinggemma
EmbeddingGemma is a family of lightweight, open-source embedding models developed by Google and Google DeepMind for on-device and local AI applications. 

Google AI for Developers
 +1
Model Versions & Specifications
EmbeddingGemma 2 (Latest - Released October 2026):
Modality: Natively multimodal, mapping text, code, images, video frames, and audio into a single unified 768-dimensional vector space.
Size Options: Scales from a 270M parameter text-and-code model up to a 740M parameter full multimodal model (utilizing modular vision and audio encoders).
Context Window: Up to 8,192 tokens (supports long documents, codebases, or ~5.5 minutes of audio).
Efficiency: Features Matryoshka Representation Learning (MRL), allowing output dimensions to be truncated down to 512, 256, or 128 dimensions to reduce vector database storage costs by up to 6x.
Memory Footprint: Runs on approximately 191 MB of RAM for text-only weights or 567 MB for the full multimodal model.
License: Apache 2.0 (open weights for commercial and research use). 

blog.google
 +5
EmbeddingGemma 1 (Original):
Modality: Multilingual text embedding model (308M parameters, based on Gemma 3).
Languages: Supports over 100 spoken languages.
Context Window: 2,000 tokens.
Efficiency: Runs on less than 200 MB of RAM with quantization and sub-22ms latency on edge hardware. 

Hugging Face
 +1
Key Use Cases
Multimodal RAG & Search: Find specific video clips from voice memos, or query images and documents using text without intermediate speech-to-text transcription. 

YouTube
·Prompt Engineering
 +1
Local & Offline Processing: Generate and store embeddings directly on consumer hardware (phones, laptops, edge devices) without sending data to external cloud APIs. 

blog.google
 +1
Downstream Tasks: Semantic similarity, zero-shot classification, clustering, and local codebase retrieval. 

Google AI for Developers
 +1
Would you like to see a code snippet for loading EmbeddingGemma 2 using sentence-transformers, or details on how to set up Matryoshka truncation?





Hugging Face
google/embeddinggemma-300m - Hugging Face
Description. EmbeddingGemma is a 300M parameter, state-of-the-art for its size, open embedding model from Google, built from Gemma...


Google AI for Developers
EmbeddingGemma - Google AI for Developers
EmbeddingGemma. ... Your browser can't play this video. EmbeddingGemma 2 is a lightweight, open-source 740M parameter model design...


Google DeepMind
EmbeddingGemma — Google DeepMind
Overview: EmbeddingGemma (developed by Google DeepMind) lightweight open embedding models optimized for on-device use cases, searc...

how does it compare to gemma 4 interms of architecture and multimodal support
EmbeddingGemma 2 is built directly on top of the Gemma 4 base. However, because they are designed for completely different tasks—EmbeddingGemma 2 for creating dense vector representations and Gemma 4 for generating text and reasoning—their architectural implementations and handling of multimodal inputs differ significantly. 

Google AI for Developers
 +5
Here is a direct comparison of how they stack up across architecture and multimodal mechanics.
Feature / Dimension	EmbeddingGemma 2	Gemma 4 (Family Overview)
Primary Task	Multimodal Embedding Generation & Retrieval	Autoregressive Text Generation & Reasoning
Model Size	740M total parameters (scales down to 270M for text-only)	E2B, E4B, 12B, 26B (MoE), and 31B (Dense)
Output Type	A single 768-dimensional vector (via mean pooling)	Continuous streams of Text Tokens
Context Window	8,192 tokens	128K (small models) to 256K tokens (medium/large models)
Multimodal Input	Text, Code, Images, Video, and Audio	Text, Images, Video (All); Audio natively on E2B, E4B, and 12B
Architectural Differences
Decoder vs. Pooling Architecture: Gemma 4 generates text token-by-token using an autoregressive decoder setup equipped with speculative decoding (Multi-Token Prediction). EmbeddingGemma 2 utilizes the Gemma 4 decoder layers as a backbone, but instead of predicting the next token, it applies mean pooling to compress the entire sequence into a single 768-dimensional space. 

Exploring Language Models
 +3
Matryoshka Representation Learning (MRL): This is unique to EmbeddingGemma 2. It explicitly structures the embedding vector so that the most critical information is packed into the earliest dimensions. Developers can truncate the vector from 768 down to 512, 256, or 128 dimensions to drastically save vector database storage with minimal accuracy loss. Gemma 4 does not feature MRL. 

YouTube
·Google for Developers
 +1
Model Routing vs. Modularity: While larger Gemma 4 models utilize a heavy Mixture of Experts (MoE) routing architecture (e.g., loading 26B parameters but only activating 3.8B per token), EmbeddingGemma 2 uses a modular encoder footprint. If a developer only needs text and code, they can load a tiny 270M parameter subset; they selectively load the 170M vision or 300M audio modules only if those modalities are required. 

MindStudio
 +1
Multimodal Support Mechanics
Alignment vs. Token Generation: Gemma 4 ingests multimodal content to understand and write about it (e.g., answering a question about an image). EmbeddingGemma 2 maps all these inputs into a shared geometric space. This allows true cross-modal retrieval—meaning you can search an un-transcribed audio registry using a text query, or find a picture using a voice memo, because their mathematical representations align. 

Hugging Face
 +4
The Encoder Approach:
EmbeddingGemma 2 uses separate, modular tokenizers: a 170M vision encoder and a 300M audio encoder that convert multimedia frames into soft placeholder tokens before running them through the shared 270M text backbone.
Gemma 4 variants handle this in two distinct ways. The E2B, E4B, 26B, and 31B variants rely on heavy native encoders with advanced configurations like variable aspect ratio imaging. Conversely, the Gemma 4 12B Unified model pioneered an encoder-free architecture that entirely bypasses separate analytical encoders, projecting raw pixel patches and 40ms audio chunks directly into the LLM embedding space using thin mathematical linear projections. 

arXiv.org
 +4
Would you like to explore how to implement EmbeddingGemma 2 for a cross-modal search engine, or look closer at Gemma 4's encoder-free 12B model?
Try without personalization





blog.google
EmbeddingGemma 2: The Developer Guide
6 Oct 2026 — Based on Gemma 4, this sub-1B model maps text, code, images, video, and audio into a unified 768-dimensional space. directly in a ...


Google AI for Developers
Multimodal Embeddings with EmbeddingGemma 2
6 Oct 2026 — EmbeddingGemma 2 is a lightweight, open-source 740M parameter model designed for unified multimodal embeddings. Built on the Gemma...

blog.google
EmbeddingGemma 2: an open, lightweight multimodal ...
Built on the Gemma 4 architecture and released under a commercially permissive Apache 2.0 license, EmbeddingGemma 2 has 740 millio...

both is fine
1. Cross-Modal Search with EmbeddingGemma 2
The core advantage of EmbeddingGemma 2's multimodal shared vector space is cross-modal retrieval. You can project text queries, audio clips, and images into the exact same 768-dimensional space, enabling you to search an image or audio database using a plain text string.
The following Python example uses the Hugging Face Transformers library to load the full multimodal model, embed an image, and retrieve it using a textual search query.
python
import torch
from transformers import AutoProcessor, AutoModel

# 1. Load the unified multimodal processor and model
model_id = "google/embedding-gemma-2-740m-multimodal"
processor = AutoProcessor.from_pretrained(model_id)
model = AutoModel.from_pretrained(model_id, torch_dtype=torch.float16, device_map="auto")

# 2. Prepare database items (e.g., an uploaded image or an audio file)
# Assume 'raw_image' is a PIL Image object of a golden retriever in a park
inputs_media = processor(images=raw_image, return_tensors="pt").to("cuda", dtype=torch.float16)

with torch.no_grad():
    # Generate the media embedding (768 dimensions)
    media_outputs = model(**inputs_media)
    image_embedding = media_outputs.embedding  # Mean-pooled output

# 3. Process the text search query
text_query = "A fluffy dog running through green grass"
inputs_text = processor(text=text_query, return_tensors="pt").to("cuda")

with torch.no_grad():
    # Generate text embedding in the exact same geometric space
    text_outputs = model(**inputs_text)
    query_embedding = text_outputs.embedding

# 4. Truncate using Matryoshka Representation Learning (Optional)
# Truncating to 256 dimensions reduces vector DB footprint by 3x with minimal loss
truncated_image_vec = image_embedding[:, :256]
truncated_query_vec = query_embedding[:, :256]

# 5. Compute Semantic Similarity
similarity = torch.nn.functional.cosine_similarity(truncated_query_vec, truncated_image_vec)
print(f"Cross-modal Match Score: {similarity.item():.4f}")
Use code with caution.
2. Gemma 4 12B Unified: The Encoder-Free Paradigm
While EmbeddingGemma 2 passes assets through traditional 170M/300M specialized analytical encoders before the text backbone, the Gemma 4 12B Unified model strips away these heavy sub-networks entirely. This structural shift changes how multimodal information flows into a generative model:
[Traditional Multimodal (EmbeddingGemma 2)]
Image/Audio -> [Heavy Vision/Audio Encoder] -> [Linear Projection] -> LLM Core

[Encoder-Free Paradigm (Gemma 4 12B Unified)]
Image (Raw Pixels) -> [Patch Segmentation (16x16)] -\
                                                       -> [Single Unified Vocabulary Projection] -> LLM Core
Audio (Raw Wave)   -> [Chunk Segmentation (40ms)]   -/
How the Encoder-Free Mechanism Operates:
Direct Tokenization: Instead of running an image through a separate model (like a ViT) to extract deep visual features, Gemma 4 12B splits an image directly into 16x16 pixel patches.
Unified Embedding Space: These raw pixel patches and 40ms continuous audio waveforms are flattened and sent straight to a shallow mathematical projection layer. This layer projects them directly into the LLM’s primary embedding dimension.
Native Context Processing: The main 12B transformer block treats visual patches and audio frames identically to standard text tokens. This means cross-attention overhead is entirely eliminated. The model calculates temporal dependencies (such as video motion or spoken inflection) natively within its standard self-attention mechanism over its massive 256K context window.
Would you like to write a prompt engineering script to test Gemma 4 12B's interleaving capabilities (e.g., combining alternating image frames and text instructions), or see how to plug the EmbeddingGemma 2 vectors into a vector database like Milvus or Pinecone?




Skip to previous prompt
Ask anything



AI Mode response is ready
Ask about
