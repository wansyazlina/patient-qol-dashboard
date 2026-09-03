from langchain_ollama import (
    ChatOllama,
    OllamaEmbeddings
)

from langchain_chroma import Chroma


CHROMA_DIR = "chroma_db"


def get_vector_store():

    embeddings = OllamaEmbeddings(
        model="nomic-embed-text"
    )

    vector_store = Chroma(
        collection_name="clinical_guidelines",
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR
    )

    return vector_store

def get_llm():

    return ChatOllama(
        model="llama3.1:8b",
        temperature=0
    )
    
def retrieve_guideline_evidence(
    query,
    top_k=4
):

    vector_store = get_vector_store()

    documents = vector_store.similarity_search(
        query,
        k=top_k
    )

    return documents

#---- SHAP values as a query retrieval prompt

def build_retrieval_query(
    risk_level,
    risk_probability,
    top_factors
):

    factor_text = ", ".join(
        top_factors
    )

    return (
        "Rehabilitation clinical guidance for a patient "
        f"with {risk_level} predicted quality-of-life decline risk "
        f"({risk_probability:.0f}%). "
        f"Relevant patient factors: {factor_text}. "
        "Find guidance related to monitoring, rehabilitation, "
        "functional status, pain, mobility, mental health, "
        "and quality-of-life assessment."
    )

def generate_clinical_interpretation(
    patient_context,
    top_factors
):

    risk_probability = (
        patient_context["risk_probability"]
    )

    risk_level = (
        patient_context["risk_level"]
    )


    # -----------------------------------------
    # Build search query from SHAP factors
    # -----------------------------------------

    query = build_retrieval_query(
        risk_level=risk_level,
        risk_probability=risk_probability,
        top_factors=[
            factor["display_name"]
            for factor in top_factors
        ]
    )


    # -----------------------------------------
    # Retrieve guideline evidence
    # -----------------------------------------

    retrieved_docs = retrieve_guideline_evidence(
        query,
        top_k=5
    )


    # -----------------------------------------
    # Prepare evidence for Ollama
    # -----------------------------------------

    evidence_blocks = []

    for index, doc in enumerate(
        retrieved_docs,
        start=1
    ):

        filename = doc.metadata.get(
            "filename",
            "Unknown source"
        )

        page = doc.metadata.get(
            "page",
            "Unknown page"
        )

        evidence_blocks.append(
            f"""Evidence {index} Source: {filename} Page: {page}
{doc.page_content} """)

    evidence_text = "\n".join(
        evidence_blocks
    )


    # -----------------------------------------
    # Prepare SHAP information
    # -----------------------------------------

    factor_lines = []

    for factor in top_factors:

        factor_lines.append(
            f"- {factor['display_name']}: "
            f"value={factor['feature_value']}, "
            f"SHAP={factor['shap_value']:.3f}"
        )

    factors_text = "\n".join(
        factor_lines
    )


    # -----------------------------------------
    # Prompt
    # -----------------------------------------

    prompt = f"""
    You are assisting a rehabilitation clinician
    with quality-of-life risk interpretation.

    IMPORTANT RULES:
    - Use only the supplied patient information and guideline evidence.
    - Do not diagnose.
    - Do not prescribe medication.
    - Do not invent patient information.
    - Do not claim that SHAP factors cause the outcome.
    - SHAP factors represent model contributions, not clinical causation.
    - Recommendations must be phrased as clinical considerations.
    - If the evidence does not support a recommendation, do not make it.
    - Keep the response concise and clinically readable.

    PATIENT MODEL INFORMATION

    Predicted QoL decline probability:
    {risk_probability:.1f}%

    Risk level:
    {risk_level}

    Top model factors:

    {factors_text}


    RETRIEVED GUIDELINE EVIDENCE

    {evidence_text}


    Generate the following:

    1. Clinical Interpretation
    Briefly explain the patient's predicted QoL risk.

    2. Suggested Clinical Considerations
    Provide 2-4 concise evidence-grounded considerations.

    3. Monitoring Considerations
    Mention relevant aspects that could be monitored during rehabilitation.

    4. Draft Clinical Note
    Write a short clinician-editable draft note.

    5. Evidence Sources
    List the guideline filenames/pages used.

    Do not present the output as a final medical decision.
    """


    # -----------------------------------------
    # Ollama generation
    # -----------------------------------------

    llm = get_llm()

    response = llm.invoke(
        prompt
    )

    return {
        "text": response.content,
        "sources": retrieved_docs
    }