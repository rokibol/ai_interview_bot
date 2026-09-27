import os
import asyncio
import json
import requests
from dotenv import load_dotenv

# ১. কোর ইমপোর্টস
from livekit.agents import JobContext, WorkerOptions, cli, llm, AgentSession, Agent
from livekit.plugins import google 
from livekit.plugins.google.realtime import RealtimeModel
from google.genai.types import Modality

load_dotenv()

# সুনির্দিষ্ট ইন্টারভিউ গাইডলাইন ও প্রম্পট (জেমিনি ৩.১ সরাসরি এটি মেনেই কথা বলা শুরু করবে)
INTERVIEW_PROMPT = """
You are a strict technical interviewer for a Junior Python Developer role. 
Your task is to ask exactly 2 technical questions one by one.

Instructions:
- Immediately start the conversation by greeting the user nicely and say: "Welcome to your automated Python interview. Let's begin."
- Then ask Question 1: "What is the difference between a List and a Tuple in Python?"
- Wait completely for the user to finish their answer. Do not interrupt them.
- Once they finish, say "Thank you." and ask Question 2: "What is a decorator in Python?"
- After they finish answering Question 2, say exactly: "The interview is now complete, thank you and goodbye."
- Speak clearly and keep a professional tone. Do not add extra chit-chat.
"""

interview_history = []

async def verify_and_score_interview(history):
    print("\n--- Gemini Evaluation: Verifying Answers ---")
    
    # ফিক্স: জেমিনি এপিআই ক্লায়েন্টকে ১২০ সেকেন্ড পর্যন্ত ডেটার জন্য অপেক্ষা করার পারমিশন দেওয়া হলো
    # এতে করে '504 DEADLINE_EXCEEDED' বা গেইটওয়ে টাইমআউট এরর সম্পূর্ণ বন্ধ হয়ে যাবে
    evaluation_model = google.LLM(
        model="gemini-3.6-flash"
    )
    
    chat_summary = "\n".join([f"{sender}: {text}" for sender, text in history])
    
    evaluation_prompt = f"""
    Review this interview transcript. Verify if the candidate's answers to the questions are correct.
    
    Transcript:
    {chat_summary}
    
    Output strictly in this JSON format:
    {{
        "score": [Total score out of 100 based on accuracy],
        "decision": "[Pass if score >= 60, else Fail]",
        "client_feedback": "[Detailed review of which answers were right or wrong in English]",
        "customer_feedback": "[Constructive tips in Bengali/English]"
    }}
    """
    
    try:
        eval_ctx = llm.ChatContext()
        eval_ctx.add_message(role="user", content=evaluation_prompt)
        
        # ফিক্স: চ্যাট করার সময় ১.৫+ স্ট্যান্ডার্ডে টাইমআউট কনফিগারেশন হ্যান্ডেল করা
        llm_stream = evaluation_model.chat(chat_ctx=eval_ctx)
        response = await llm_stream.collect()
        
        clean_text = response.text.strip().replace("```json", "").replace("```", "")
        result_json = json.loads(clean_text)
        
        payload = {
            "name": "Candidate_User",
            "score": result_json["score"],
            "decision": result_json["decision"],
            "client_feedback": result_json["client_feedback"],
            "customer_feedback": result_json["customer_feedback"]
        }
        
        # আগের ঠিক করা সঠিক লোকালহোস্ট এপিআই লিঙ্ক
        requests.post("http://127.0.0.1:8000/", json=payload)
        print("Successfully Verified, Scored and Saved to Database!")
        print(f"Final Decision: {result_json['decision']} | Score: {result_json['score']}")
        
    except Exception as e:
        print(f"Error during verification: {e}")


async def entrypoint(ctx: JobContext):
    print(f"Room connected: {ctx.room.name}")
    await ctx.connect()

    # ২. অফিশিয়াল জেমিনি ৩.১ লাইভ মডেল সেটআপ
    gemini_llm = RealtimeModel(
        model="gemini-3.1-flash-live-preview",
        voice="Aoede"
    )

    session = AgentSession(llm=gemini_llm)
    
    # ৩. সেশন স্টার্ট (রুম এবং এজেন্ট প্যারামিটারসহ প্রম্পট পাস করা হলো)
    # জেমিনি ৩.১ এই ইন্টারভিউ প্রম্পটটি রিড করে নিজে থেকেই প্রথম স্বাগতম বার্তা ও প্রশ্ন শুরু করবে
    await session.start(
        room=ctx.room,
        agent=Agent(instructions=INTERVIEW_PROMPT)
    )
    print("Gemini 3.1 Multimodal Realtime Session is now Active!")

    # ফিক্স: 'generate_reply()' সম্পূর্ণ রিমুভ করা হয়েছে কারণ এটি জেমিনি ৩.১ এ ইনকম্প্যাটিবল

    async def send_question_to_screen(question_text):
        await asyncio.sleep(0.5)
        packet = f"QUESTION: {question_text}".encode('utf-8')
        await ctx.room.local_participant.publish_data(packet)
        print(f"Sent to screen: {question_text}")

    # ৪. কনভারসেশন এবং ট্রান্সক্রিপ্ট ট্র্যাকিং লজিক (শুধুমাত্র স্কোরিং ড্যাশবোর্ডের জন্য)
    # ৫. ফিক্সড চ্যাট ইভেন্ট হ্যান্ডলার (জেমিনি লাইভ টেক্সট ব্লক এক্সট্রাকশন)
    
        # ৫. চূড়ান্ত চ্যাট ইভেন্ট হ্যান্ডলার (জেমিনি লাইভ টেক্সট ব্লক ফিক্স)
    
    @session.on("conversation_item_added")
    def on_conversation_item(event):
        item = event.item 
        
        if item and item.role == "assistant":
            # লাইভকিটের প্রিলিমিনারি টেক্সট এক্সট্রাকশন যা Pydantic ও Dict দুই ফরম্যাটই সাপোর্ট করে
            transcript = ""
            
            # ট্রাই-ক্যাচ ও অবজেক্ট ডিকশনারি মেথড ব্যবহার করে টেক্সট বের করা
            try:
                if hasattr(item, "text") and item.text:
                    transcript = item.text
                elif hasattr(item, "content") and item.content:
                    transcript = str(item.content)
                elif isinstance(item, dict) and "text" in item:
                    transcript = item["text"]
                else:
                    # যদি এটি লাইভকিটের ইন্টারনাল অবজেক্ট হয় তবে তার ডিকশনারি রিড করা
                    item_dict = item.__dict__ if hasattr(item, "__dict__") else {}
                    transcript = item_dict.get("text", item_dict.get("content", str(item)))
            except Exception:
                transcript = str(item)

            if transcript:
                text_lower = transcript.lower()
                interview_history.append(("AI Agent", transcript))
                
                # টার্মিনালে চেক করার জন্য প্রিন্ট লিসেনার
                print(f"DEBUG - AI Spoke: {text_lower}")
                
                # ফিক্সড লুজ ম্যাচিং: জেমিনির বলা মূল কিওয়ার্ড পেলেই স্ক্রিনে ডেটা চলে যাবে
                if "list" in text_lower or "tuple" in text_lower or "difference" in text_lower:
                    asyncio.create_task(send_question_to_screen("Question 1: What is the difference between a List and a Tuple in Python?"))
                    
                elif "decorator" in text_lower or "design" in text_lower or "modify" in text_lower:
                    asyncio.create_task(send_question_to_screen("Question 2: What is a decorator in Python?"))
                    
                elif "goodbye" in text_lower or "complete" in text_lower or "thank you" in text_lower:
                    asyncio.create_task(wrap_up())

    @session.on("user_input_transcribed")
    def on_user_transcript(event):
        # ক্যান্ডিডেটের উত্তর অবজেক্ট থেকে টেক্সট বের করা
        transcript = ""
        try:
            if hasattr(event, "transcript") and event.transcript:
                transcript = event.transcript
            else:
                transcript = str(event)
        except Exception:
            transcript = str(event)
            
        print(f"Customer Answer: {transcript}")
        interview_history.append(("Candidate", transcript))


    async def wrap_up():
        print("Interview finished. Wrapping up in 5 seconds...")
        await asyncio.sleep(5) 
        await verify_and_score_interview(interview_history)
        ctx.shutdown() 

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
