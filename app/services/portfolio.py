import os
import requests
from fastapi import HTTPException

async def getPortfolio(text: str):
    # Get API key from environment variables
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Gemini API key not found")
    
    try:
        # Gemini API endpoint
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        
        # Prepare request payload for Gemini
        
        aboutMe = "My name is Joshua P. Laude, A BSIT Graduate from Manuel S. Enverga University Lucena. I have an experience of working as a Backend developer intern in the university, where I was able to create APIs including some microservices using C# ASP.NET CORE. I am currently looking for a developer position where I can apply my skills and continue to grow in the field of software development. Paid trainings are also welcome. I am also a self-taught developer, I have been learning and practicing programming languages such as C#, JavaScript, TypeScript, HTML, CSS, NodeJS, Git & GitHub, PHP, Bootstrap, TailwindCSS, and frameworks such as ASP.NET Core, CodeIgniter4, Laravel, ReactJS, ExpressJS, ReactNative, Django. I am passionate about coding and always eager to learn new technologies and improve my skills. By knowing the knowledge in some company requirements, I started creating personal project for practice using Python with FastAPI, AngularJS, Laravel, and ReactJS. I am also familiar with databases such as MySQL, and MongoDB. I am a team player and can work well under pressure. I am also willing to learn new technologies and adapt to the company's needs. I also have deployment experience using GitHub and Render Web Service for a full system deployment. I am also familiar with Agile methodologies and have experience working in a team environment. I am a quick learner and can adapt to new technologies and frameworks easily. I am also willing to learn new technologies and frameworks that I am not familiar with. I am looking for a company where I can grow and contribute my skills."
        strengths = "I am able to adapt quickly in learning"
        projects = "My deployed projects are TheFerry, Microservices. TheFerry is a web application that allows users to book ferry tickets online. Microservices is a project that I created to practice my skills in creating APIs and microservices using Python 3 and FastAPI. I also have undeployed CodeIgniter4 and Laravel that has CRUD functionality used for my practice"
        weakness = "I am sometimes scared to get out of my comfort zone but I am trying to overcome it. but I am trying to overcome it by starting to learn new technologies and frameworks that I am not familiar with and asking questions."
        contact ="Contact details: Phone number is 09480930937, email is joshualaude016@gmail.com or joshualaude03333@gmail.com"
        # Use f-string for proper variable interpolation
        prompt_text = f"{aboutMe}, {strengths}, {weakness}, {projects}, {contact}. Do not tell that the information is provided. Just tell them like you know him. You can use them in your response. Here is the question: {text}"


        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt_text
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 1024
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            'X-goog-api-key': api_key
        }
        
        response = requests.post(
            url, 
            headers=headers,
            json=payload
        )
        
        response.raise_for_status()
        response_data = response.json()
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API failed: {str(e)}")