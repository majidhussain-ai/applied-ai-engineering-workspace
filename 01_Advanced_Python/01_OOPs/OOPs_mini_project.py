# Mini project using (Encapsulation, Inheritance, Polymorphism, Abstraction, Aggregation/Composition, Dunders method)
#%%
from abc import ABC , abstractmethod
class BaseLLMProvider(ABC):
    def __init__(self, model_name, cost_per_query):
        self.model_name = model_name
        self.cost_per_query = cost_per_query

    @abstractmethod
    def generate_response(self, context: str, query: str) -> str:
        pass
    def get_cost(self):
        return self.cost_per_query

class OpenAIProvider(BaseLLMProvider):
    def __init__(self):
        super().__init__(model_name = 'gpt-4o' , cost_per_query= 0.003)
    def generate_response(self, context, query):
        return f"[OpenAI {self.model_name}] answered: '{query}' using context {context[:20]}"

class OllamaLocalProvider(BaseLLMProvider):
    def __init__(self):
        super().__init__(model_name='Ollama-4.5-8b', cost_per_query=0.0)
    def generate_response(self, context, query):
        return f"[Ollama Local {self.model_name}] is answered {query} using context {context[:20]}"

class SimpleVectorStore:
    def __init__(self):
        self._documents = []
    def add_documents(self, docs):
        self._documents.extend(docs)
    def retrieve_top_k(self, query, k=2):
        return " ".join(self._documents[:k])
    def __len__(self):
        return len(self._documents)

class RAGPipeline:
    def __init__(self, retriever, llm_engine):
        self.retriever = retriever
        self.llm_engine = llm_engine
        self.total_cost_incurred = 0.0
        self.total_queries_run = 0

    def __call__(self, user_query):
        context = self.retriever.retrieve_top_k(user_query)
        response = self.llm_engine.generate_response(context, user_query)
        self.total_queries_run += 1
        self.total_cost_incurred += self.llm_engine.get_cost()
        return response
    def __repr__(self):
        return f"RAGPipline (Model = {self.llm_engine.model_name} with docs_index= {len(self.retriever)} with cost = ${self.total_cost_incurred})"

db = SimpleVectorStore()
db.add_documents(["Doc A text chunk", "Doc B text chunk", "Doc C text chunk"])
print(f"Lenght of db is: {len(db)}")

model = OpenAIProvider()

pipeline = RAGPipeline(retriever = db, llm_engine= model)
ans = pipeline('What is MCP ?.')
print(ans)
