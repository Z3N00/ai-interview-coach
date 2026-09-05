from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
import json

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="openai/gpt-oss-20b"
)

def evaluate_answer(question: str, answer: str, topic: str) -> dict:
    prompt = f"""You are an expert technical interviewer evaluating a candidate's answer.

Topic: {topic}
Question: {question}
Candidate's Answer: {answer}

Evaluate the answer and respond in this exact JSON format:
{{
    "score": <number from 1-10>,
    "feedback": "<specific feedback on what was good and what was missing>",
    "correct_answer": "<brief correct/complete answer>",
    "improvement_tips": "<specific tips to improve>"
}}

Be honest, constructive and specific. Return only valid JSON."""

    response = llm.invoke(prompt)
    
    try:
        evaluation = json.loads(response.content)
    except:
        evaluation = {
            "score": 5,
            "feedback": response.content,
            "correct_answer": "Please review the topic",
            "improvement_tips": "Practice more on this topic"
        }
    
    return evaluation

def generate_final_report(topic: str, scores: list, conversation_history: list) -> dict:
    avg_score = sum(scores) / len(scores) if scores else 0
    
    history_text = "\n".join([
        f"{msg['role'].upper()}: {msg['content']}"
        for msg in conversation_history
    ])
    
    prompt = f"""You are an expert technical interviewer providing a final interview report.

Topic: {topic}
Average Score: {avg_score:.1f}/10
Full Interview:
{history_text}

Provide a final report in this exact JSON format:
{{
    "overall_score": {avg_score:.1f},
    "performance_level": "<Excellent/Good/Average/Needs Improvement>",
    "strengths": ["<strength 1>", "<strength 2>"],
    "weaknesses": ["<weakness 1>", "<weakness 2>"],
    "study_recommendations": ["<recommendation 1>", "<recommendation 2>"],
    "hiring_recommendation": "<Strong Yes/Yes/Maybe/No>"
}}

Return only valid JSON."""

    response = llm.invoke(prompt)
    
    try:
        report = json.loads(response.content)
    except:
        report = {
            "overall_score": avg_score,
            "performance_level": "Average",
            "strengths": ["Attempted all questions"],
            "weaknesses": ["Need more practice"],
            "study_recommendations": ["Review core concepts"],
            "hiring_recommendation": "Maybe"
        }
    
    return report