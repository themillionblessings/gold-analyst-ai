import os
from typing import List, Dict, Any
from pypdf import PdfReader
import google.generativeai as genai
from sqlalchemy.orm import Session
from backend.models import DocumentChunk
from sqlalchemy import text

class RagService:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
        
    def ingest_pdf(self, file_path: str, filename: str, db: Session):
        reader = PdfReader(file_path)
        text_content = ""
        for page in reader.pages:
            text_content += page.extract_text() + "\n"
        
        # Chunk text (1000 chars)
        chunks = [text_content[i:i + 1000] for i in range(0, len(text_content), 1000)]
        
        for chunk in chunks:
            if not chunk.strip():
                continue
                
            # Generate embeddings using gemini
            embedding_resp = genai.embed_content(
                model='models/text-embedding-004',
                content=chunk,
                task_type="retrieval_document"
            )
            embedding = embedding_resp['embedding']
            
            # Save to DB
            db_chunk = DocumentChunk(
                filename=filename,
                content=chunk,
                embedding=embedding
            )
            db.add(db_chunk)
        
        db.commit()
        return len(chunks)

    def search_docs(self, query: str, db: Session) -> Dict[str, Any]:
        # Embed the query
        query_embedding_resp = genai.embed_content(
            model='models/text-embedding-004',
            content=query,
            task_type="retrieval_query"
        )
        query_embedding = query_embedding_resp['embedding']
        
        # Query the DB using L2 distance (<->)
        # Using raw SQL via text() because pgvector SQLAlchemy integration can be tricky with some versions
        results = db.query(DocumentChunk).order_by(
            DocumentChunk.embedding.l2_distance(query_embedding)
        ).limit(3).all()
        
        context = "\n\n".join([r.content for r in results])
        sources = list(set([r.filename for r in results]))
        
        # Send chunks + query to Gemini Flash for the final answer
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        You are a Gold Market Expert. Use the following context from gold market reports to answer the question.
        If the answer is not in the context, say you don't know based on the provided documents.
        
        Context:
        {context}
        
        Question: {query}
        
        Answer professionally and concisely.
        """
        
        response = model.generate_content(prompt)
        
        return {
            "answer": response.text,
            "sources": sources
        }
