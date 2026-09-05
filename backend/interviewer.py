from langchain_groq import ChatGroq

from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="openai/gpt-oss-20b"
)

INTERVIEW_TOPICS = {
    "python_basics": "Python fundamentals, data types, OOP, decorators, generators",
    "python_advanced": "Multiprocessing, threading, GIL, memory management, performance",
    "system_design": "Scalability, microservices, databases, caching, load balancing",
    "ml_ai": "Machine learning concepts, neural networks, RAG, LLMs, prompt engineering",
    "data_structures": "Arrays, linked lists, trees, graphs, sorting, searching"
}

def get_first_question(topic: str, candidate_name: str) -> str:
    topic_description = INTERVIEW_TOPICS.get(topic, "general programming")
    
    prompt = f"""You are an expert technical interviewer at a top tech company.
    You are interviewing {candidate_name} for a senior Python/AI engineer position.
    Topic: {topic_description}

    IMPORTANT: This is a VOICE interview. Ask conceptual and theoretical questions only.
    Do NOT ask candidates to write code. Focus on explaining concepts, architecture decisions,
    and problem solving approaches verbally.

    Introduce yourself briefly and ask the first interview question.
    Keep it professional and concise. Ask only ONE question."""

    response = llm.invoke(prompt)
    return response.content

def get_next_question(topic: str, conversation_history: list, evaluation: str) -> str:
    topic_description = INTERVIEW_TOPICS.get(topic, "general programming")
    
    history_text = "\n".join([
        f"{msg['role'].upper()}: {msg['content']}" 
        for msg in conversation_history
    ])
    
    prompt = f"""You are an expert technical interviewer.
Topic: {topic_description}

Conversation so far:
{history_text}

Previous answer evaluation: {evaluation}

Based on the candidate's performance, ask the next appropriate question.
If they struggled, ask a simpler follow-up. If they did well, increase difficulty.
Ask only ONE question. Be concise."""

    response = llm.invoke(prompt)
    return response.content