from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
from dotenv import load_dotenv
from typing import Dict, Any, List

load_dotenv()

class InMemoryCollection:
    """In-memory collection fallback for development"""
    def __init__(self):
        self.data: List[Dict[str, Any]] = []
        self._id_counter = 1
    
    def insert_one(self, document: Dict[str, Any]) -> Any:
        if '_id' not in document:
            document['_id'] = f"mem_{self._id_counter}"
            self._id_counter += 1
        self.data.append(document)
        return type('MockResult', (), {'inserted_id': document['_id']})()
    
    def insert_many(self, documents: List[Dict[str, Any]]) -> Any:
        for doc in documents:
            self.insert_one(doc)
        return type('MockResult', (), {'inserted_ids': [doc['_id'] for doc in documents]})()
    
    def find_one(self, query: Dict[str, Any]) -> Dict[str, Any]:
        for doc in self.data:
            if self._match_query(doc, query):
                return doc.copy()
        return None
    
    def find(self, query: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        if query is None:
            return [doc.copy() for doc in self.data]
        
        results = []
        for doc in self.data:
            if self._match_query(doc, query):
                results.append(doc.copy())
        return results
    
    def update_one(self, query: Dict[str, Any], update: Dict[str, Any]) -> Any:
        for i, doc in enumerate(self.data):
            if self._match_query(doc, query):
                if '$set' in update:
                    doc.update(update['$set'])
                if '$push' in update:
                    for key, value in update['$push'].items():
                        if key not in doc:
                            doc[key] = []
                        if isinstance(value, list):
                            doc[key].extend(value)
                        else:
                            doc[key].append(value)
                return type('MockResult', (), {'matched_count': 1, 'modified_count': 1})()
        return type('MockResult', (), {'matched_count': 0, 'modified_count': 0})()
    
    def delete_many(self, query: Dict[str, Any]) -> Any:
        original_count = len(self.data)
        self.data = [doc for doc in self.data if not self._match_query(doc, query)]
        deleted_count = original_count - len(self.data)
        return type('MockResult', (), {'deleted_count': deleted_count})()
    
    def count_documents(self, query: Dict[str, Any] = None) -> int:
        if query is None:
            return len(self.data)
        return len([doc for doc in self.data if self._match_query(doc, query)])
    
    def _match_query(self, doc: Dict[str, Any], query: Dict[str, Any]) -> bool:
        for key, value in query.items():
            if key == '$nin' and isinstance(value, list):
                if doc.get('_id') in value:
                    return False
            elif key not in doc or doc[key] != value:
                return False
        return True

class InMemoryDatabase:
    """In-memory database fallback for development"""
    def __init__(self):
        self.collections: Dict[str, InMemoryCollection] = {}
    
    def get_collection(self, name: str) -> InMemoryCollection:
        if name not in self.collections:
            self.collections[name] = InMemoryCollection()
        return self.collections[name]

class Database:
    def __init__(self):
        self.mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/adaptive_diagnostic")
        self.client = None
        self.db = None
        self.in_memory_db = None
        self.use_in_memory = False

    def connect(self):
        try:
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            # Extract database name from URI or use default
            from pymongo.uri_parser import parse_uri
            parsed = parse_uri(self.mongo_uri)
            db_name = parsed.get('database', 'adaptive_diagnostic')
            self.db = self.client[db_name]
            print("MongoDB connected successfully")
        except ConnectionFailure as e:
            print(f"MongoDB connection failed: {e}")
            print("Using in-memory storage for development")
            self.client = None
            self.db = None
            self.in_memory_db = InMemoryDatabase()
            self.use_in_memory = True

    def get_collection(self, name: str):
        if self.use_in_memory:
            return _in_memory_db.get_collection(name)
        
        if self.db is None:
            if self.client is None:
                self.connect()
            if self.use_in_memory:
                return _in_memory_db.get_collection(name)
            if self.db is None:
                raise ConnectionError("Database not connected")
        return self.db[name]

    def close(self):
        if self.client:
            self.client.close()

# Global database instance
db = Database()

# Global in-memory database instance for persistence
_in_memory_db = InMemoryDatabase()
