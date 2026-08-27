#%%
def clean_text(text):
    """Remove unnecessary whitespace from text."""
    return text.strip()


def normalize_text(text):
    """Convert text to lowercase."""
    return text.lower()

def create_prefix_processor(prefix):
    """
    Create and return a function that adds a prefix to text.
    """

    def add_prefix(text):
        return f"{prefix}{text}"

    return add_prefix

def apply_processor(processor, data):
    """
    Receive a function and data,
    then apply the function to the data.
    """

    return processor(data)

def run_pipeline(data, *steps):
    """
    Sequentially pass data through multiple processing steps.
    """

    for step in steps:
        data = step(data)

    return data

def process_documents(
    *documents,
    lowercase=True,
    prefix="[Processed] "
):

    processed_documents = []

    # Create prefix processor dynamically
    prefix_processor = create_prefix_processor(prefix)

    for document in documents:

        # Build pipeline dynamically
        steps = [
            clean_text,
        ]

        if lowercase:
            steps.append(normalize_text)

        steps.append(prefix_processor)

        # Run document through pipeline
        processed_document = run_pipeline(
            document,
            *steps
        )

        processed_documents.append(processed_document)

    return processed_documents

documents = (
    "   HELLO WORLD   ",
    "   Python Is Easy   ",
    "   RAG Uses Embeddings   ",
)

result = process_documents(
    *documents,
    lowercase=True,
    prefix="[CLEANED] "
)

print("Processed Documents:")

for document in result:
    print(document)
# %%
