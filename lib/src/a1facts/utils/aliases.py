import spacy
from spacy.language import Language
from spacy.tokens import Span
from sentence_transformers import SentenceTransformer
import chromadb
import yaml
import uuid

# --- 1. Dynamic, Learning Knowledge Base ---
class DynamicKnowledgeBase:
    """
    Manages a knowledge base that is built dynamically from processed text.
    It encapsulates the "find or create" logic for entity resolution.
    """
    def __init__(self, ontology_yaml: str, model_name='all-MiniLM-L6-v2', similarity_threshold=0.85):
        print("Initializing Dynamic Knowledge Base...")
        self.ontology = yaml.safe_load(ontology_yaml)
        self.main_entities = self.ontology.get('world', {}).get('main_entities', [])
        self.entity_counter = {entity: 0 for entity in self.main_entities}
        
        # In-memory storage for the dynamic KB
        self.alias_to_id = {}
        self.id_to_canonical = {}
        
        # Setup for semantic search
        self.model = SentenceTransformer(model_name)
        self.similarity_threshold = similarity_threshold
        chroma_client = chromadb.Client()
        self.collection = chroma_client.get_or_create_collection(
            name="dynamic_entity_kb",
            metadata={"hnsw:space": "cosine"}
        )
        print(f"Ready to resolve main entities: {self.main_entities}")

    def _create_new_entity(self, text: str, entity_type: str) -> str:
        """Adds a new entity to the knowledge base."""
        # Determine the entity type from NER label (e.g., ORG -> Company)
        # This mapping might need to be more sophisticated in a real system.
        # For now, we'll assume a direct mapping if possible.
        kb_type = entity_type if entity_type in self.main_entities else "Unknown"
        
        self.entity_counter[kb_type] = self.entity_counter.get(kb_type, 0) + 1
        new_id = f"{kb_type.upper()}_{self.entity_counter[kb_type]}"
        
        print(f"  -> CREATING new entity. ID: {new_id}, Canonical Name: '{text}'")
        
        # Update KB state
        self.id_to_canonical[new_id] = text
        self.alias_to_id[text.lower()] = new_id
        
        # Index the new entity in ChromaDB for future semantic lookups
        embedding = self.model.encode([text]).tolist()
        self.collection.add(
            embeddings=embedding,
            documents=[text],
            metadatas=[{"canonical_id": new_id}],
            ids=[str(uuid.uuid4())]
        )
        return new_id

    def find_or_create_entity(self, text: str, entity_type: str) -> (str, str):
        """
        The core logic: finds an existing entity or creates a new one.
        Returns the canonical ID and name.
        """
        text_lower = text.lower().strip()
        
        # 1. Exact Match
        if text_lower in self.alias_to_id:
            kb_id = self.alias_to_id[text_lower]
            print(f"  -> FOUND entity via Exact Match. ID: {kb_id}")
            return kb_id, self.id_to_canonical[kb_id], "Exact"
            
        # 2. Semantic Match
        if self.collection.count() > 0:
            query_embedding = self.model.encode([text]).tolist()
            results = self.collection.query(query_embeddings=query_embedding, n_results=1)
            
            if results and results['distances'][0]:
                distance = results['distances'][0][0]
                similarity = 1 - distance
                if similarity >= self.similarity_threshold:
                    kb_id = results['metadatas'][0][0]['canonical_id']
                    print(f"  -> FOUND entity via Semantic Match. ID: {kb_id} (Score: {similarity:.2f})")
                    # Learn this new alias!
                    print(f"     Learning new alias: '{text}' -> {self.id_to_canonical[kb_id]}")
                    self.alias_to_id[text_lower] = kb_id
                    return kb_id, self.id_to_canonical[kb_id], f"Semantic (Score: {similarity:.2f})"

        # 3. Create New Entity
        kb_id = self._create_new_entity(text, entity_type)
        return kb_id, text, "Created New"


# --- 2. spaCy Component (now simpler) ---
@Language.factory(
    "dynamic_entity_linker",
    default_config={
        "ontology_yaml": "",
        "model_name": "all-mpnet-base-v2",
        "similarity_threshold": 0.85,
    },
)
def create_dynamic_entity_linker(
    nlp: Language,
    name: str,
    ontology_yaml: str,
    model_name: str,
    similarity_threshold: float,
):
    """Factory function to create the DynamicEntityLinker component."""
    kb = DynamicKnowledgeBase(
        ontology_yaml=ontology_yaml,
        model_name=model_name,
        similarity_threshold=similarity_threshold,
    )
    return DynamicEntityLinker(kb=kb)


class DynamicEntityLinker:
    def __init__(self, kb: DynamicKnowledgeBase):
        self.kb = kb
        for ext in ["kb_id", "canonical_name", "match_method"]:
            if not Span.has_extension(ext):
                Span.set_extension(ext, default=None)

    def __call__(self, doc):
        for ent in doc.ents:
            # Simple mapping from spaCy labels to ontology types.
            # This can be customized for more complex scenarios.
            entity_type_map = {"ORG": "Company", "PRODUCT": "Drug", "PERSON": "Sponsor"}
            ent_type = entity_type_map.get(ent.label_, ent.label_)

            # Only resolve entities defined as 'main' in the ontology
            if ent_type in self.kb.main_entities:
                kb_id, canonical_name, method = self.kb.find_or_create_entity(ent.text, ent_type)
                ent._.kb_id = kb_id
                ent._.canonical_name = canonical_name
                ent._.match_method = method
        return doc


# --- 3. Main Execution Block ---
if __name__ == "__main__":
    financial_ontology_yaml = """
    world:
      name: Company Knowledge Graph
      main_entities: [Company]
    entity_classes:
      Company:
        properties: [{name: name, type: str, primary_key: true}]
    """
    
    # 1. Setup spaCy pipeline
    nlp = spacy.load("en_core_web_lg")
    nlp.add_pipe("dynamic_entity_linker", after="ner", config={
        "ontology_yaml": financial_ontology_yaml,
        "similarity_threshold": 0.85,
    })

    # 2. Process texts SEQUENTIALLY to see the KB learn
    texts_to_process = [
        "A report mentioned Intel Corporation as a key player.",
        "Later, Intel Inc. released its earnings.",
        "Separately, UnitedHealth Group announced a new initiative.",
        "A statement from the healthcare company United Health followed."
    ]

    print("\n" + "="*50)
    print("Processing documents and building Knowledge Base dynamically...")
    print("="*50)

    for i, text in enumerate(texts_to_process):
        print(f"\n--- Processing Doc {i+1}: '{text}' ---")
        doc = nlp(text)
        for ent in doc.ents:
            if ent._.kb_id: # Check if it was resolved by our component
                print(
                    f"  Entity: '{ent.text}' (Label: {ent.label_})\n"
                    f"  -> Resolved ID: {ent._.kb_id}\n"
                    f"  -> Canonical Name: {ent._.canonical_name}\n"
                    f"  -> Method: {ent._.match_method}"
                )
    
    # Get the component from the pipeline to access its knowledge base
    dynamic_linker = nlp.get_pipe("dynamic_entity_linker")
    kb = dynamic_linker.kb

    print("\n" + "="*50)
    print("Final Knowledge Base State:")
    print("="*50)
    print("Canonical Entities:", kb.id_to_canonical)
    print("Learned Aliases:", kb.alias_to_id)