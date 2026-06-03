from openai import OpenAI
import requests


import json

client = OpenAI(...)

def analyze_resume (resume_text , user_goal):
    prompt = f"""
you are a senior software engineer and hiring manager.

evaluate the resume based on the user's goal.

user goal: "{user_goal}"

STRICT RULES:
-Extractonly relevant skills for this goal
-REMOVE irrelevant tools [excel for backend, etc]
-Identify real gaps
-Generate roadmap only for missing fields
-Make output DIFFERENT based on goal

return only JSON:
{{
"skills":[],
"missing_skills":[],
"roadmap":[],
"interview_questions":[]

}}
resume:
{resume_text}

"""
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            temperature=0.3,
            messages= [

                {"role":"system","content":"you're a strict hiring manager."},
                {"role":"user","content":prompt}
            ]
        )

        content = response.choices[0].message.content.strip()

        start = content.find("{")
        end = content.rfind("}")

        return json.loads(content[start:end+1])

    except Exception as e:
        return {
            "skills":[],
            "missing_skills":[],
            "roadmap":[],
            "interview_questions":[],
            "error":str(e)
        }