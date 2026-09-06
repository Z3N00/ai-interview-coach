from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
import os
import tempfile
from interviewer import get_first_question, get_next_question
from evaluator import evaluate_answer, generate_final_report
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


load_dotenv()

app = FastAPI(title="AI Interview Coach")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Store interview sessions
sessions = {}

class StartInterview(BaseModel):
    candidate_name: str
    topic: str

class SubmitAnswer(BaseModel):
    session_id: str
    answer: str

@app.get("/")
def home():
    return {"message": "AI Interview Coach API running!"}

# Serve frontend static files
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

@app.get("/app")
def serve_frontend():
    return FileResponse("../frontend/index.html")

@app.get("/topics")
def get_topics():
    return {
        "topics": [
            {"id": "python_basics", "name": "Python Basics"},
            {"id": "python_advanced", "name": "Python Advanced"},
            {"id": "system_design", "name": "System Design"},
            {"id": "ml_ai", "name": "ML & AI"},
            {"id": "data_structures", "name": "Data Structures"}
        ]
    }

@app.post("/start-interview")
def start_interview(data: StartInterview):
    import uuid
    session_id = str(uuid.uuid4())
    
    first_question = get_first_question(data.topic, data.candidate_name)
    
    sessions[session_id] = {
        "candidate_name": data.candidate_name,
        "topic": data.topic,
        "conversation_history": [],
        "scores": [],
        "question_count": 0,
        "current_question": first_question
    }
    
    sessions[session_id]["conversation_history"].append({
        "role": "interviewer",
        "content": first_question
    })
    
    return {
        "session_id": session_id,
        "question": first_question,
        "question_number": 1
    }

@app.post("/submit-answer")
def submit_answer(data: SubmitAnswer):
    if data.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[data.session_id]
    session["conversation_history"].append({
        "role": "candidate",
        "content": data.answer
    })
    
    # Evaluate answer
    evaluation = evaluate_answer(
        question=session["current_question"],
        answer=data.answer,
        topic=session["topic"]
    )
    
    session["scores"].append(evaluation["score"])
    session["question_count"] += 1
    
    # Check if interview should end (after 5 questions)
    if session["question_count"] >= 5:
        report = generate_final_report(
            topic=session["topic"],
            scores=session["scores"],
            conversation_history=session["conversation_history"]
        )
        return {
            "status": "completed",
            "evaluation": evaluation,
            "final_report": report
        }
    
    # Get next question
    next_question = get_next_question(
        topic=session["topic"],
        conversation_history=session["conversation_history"],
        evaluation=f"Score: {evaluation['score']}/10 - {evaluation['feedback']}"
    )
    
    session["current_question"] = next_question
    session["conversation_history"].append({
        "role": "interviewer",
        "content": next_question
    })
    
    return {
        "status": "ongoing",
        "evaluation": evaluation,
        "next_question": next_question,
        "question_number": session["question_count"] + 1
    }

@app.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        content = await audio.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    with open(tmp_path, "rb") as audio_file:
        transcription = groq_client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=audio_file
        )
    
    os.unlink(tmp_path)
    return {"text": transcription.text}

@app.get("/health")
def health():
    return {"status": "healthy"}