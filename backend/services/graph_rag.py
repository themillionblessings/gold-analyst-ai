import os
import json
from neo4j import AsyncGraphDatabase
import google.generativeai as genai
from typing import Dict, Any

class KnowledgeGraphService:
    def __init__(self):
        # Neo4j Setup
        neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        neo4j_password = os.getenv("NEO4J_PASSWORD", "password123")
        self.driver = AsyncGraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        
        # LLM Setup
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(
                model_name="gemini-flash-latest",
                generation_config={"temperature": 0.0, "response_mime_type": "application/json"}
            )
        else:
            self.model = None

    async def close(self):
        await self.driver.close()

    async def extract_and_store_entities(self, news_text: str) -> Dict[str, Any]:
        """
        Uses Gemini to extract entities/relations from economic news and stores them in Neo4j.
        """
        if not self.model:
            return {"status": "error", "message": "Missing GOOGLE_API_KEY"}

        prompt = f"""
        Extract entities and macroeconomic relationships from this economic news text.
        Focus on subjects like 'Interest Rates', 'Currency', 'Gold Premiums', 'Inflation', 'Central Banks', etc.
        
        Return a Strict JSON list of relationship objects exactly matching this format:
        [
            {{"source": "Entity A", "relation": "ACTION_VERB", "target": "Entity B"}},
            {{"source": "US Federal Reserve", "relation": "CUTS", "target": "Interest Rates"}}
        ]
        
        News Text:
        {news_text}
        """

        try:
            response = self.model.generate_content(prompt)
            # Robust JSON parsing
            text = response.text.strip()
            if text.startswith("```json"): text = text[7:]
            elif text.startswith("```"): text = text[3:]
            if text.endswith("```"): text = text[:-3]
            
            relationships = json.loads(text.strip())
            
            if not isinstance(relationships, list):
                relationships = [relationships] # Defensive array wrapping
                
        except Exception as e:
            print(f"Graph Extraction LLM Error: {e}")
            return {"status": "error", "message": "Failed to extract entities via LLM"}

        # Store in Neo4j
        nodes_created = 0
        try:
            async with self.driver.session() as session:
                for rel in relationships:
                    source = rel.get("source", "").strip()
                    relation = rel.get("relation", "RELATES_TO").strip().upper().replace(" ", "_")
                    target = rel.get("target", "").strip()
                    
                    if not source or not target:
                        continue
                        
                    # Cypher logic: Merge nodes and create relationship
                    query = f"""
                    MERGE (a:Entity {{name: $source}})
                    MERGE (b:Entity {{name: $target}})
                    MERGE (a)-[r:{relation}]->(b)
                    RETURN count(r)
                    """
                    result = await session.run(query, source=source, target=target)
                    nodes_created += 2 # Rough estimate: Two nodes touched per relation

            return {
                "status": "success",
                "extracted_relationships": len(relationships),
                "nodes_processed": nodes_created
            }
            
        except Exception as e:
            print(f"Neo4j Cypher Error: {e}")
            return {"status": "error", "message": f"Database insertion failed: {str(e)}"}
