# Ai-based-Image-to-text-speech-generator-
VisionAI — Intelligent Image Understanding System for Partially Blind Users
Upload an image → understand the scene → ask questions → receive text and voice responses ( Voice?speech feature for Blind users) 
Designed as an accessibility-focused multimodal assistant running locally on your system. 

| Feature                   | Description                                            |
| ------------------------- | ------------------------------------------------------ |
| **Image Upload**          | Supports JPG, PNG, JPEG, BMP, and WebP images          |
| **Scene Understanding**   | Generates meaningful descriptions from uploaded images |
| **Interactive Q&A**       | Ask follow-up questions related to the image           |
| **Voice Interaction**     | Supports both speech input and audio responses         |
| **Local Execution**       | Processing runs directly on the system                 |
| **Accessibility Focused** | Designed to assist partially blind users               |
| **Responsive Interface**  | Simple and user-friendly interface                     |

+----------------------+----------------------------------------------+
| Category             | Technologies Used                            |
+----------------------+----------------------------------------------+
| Backend              | Python, Flask                                |
+----------------------+----------------------------------------------+
| AI & Processing      | PyTorch, Transformers Library, OpenCV, NumPy |
+----------------------+----------------------------------------------+
| Frontend             | HTML, CSS, JavaScript                        |
+----------------------+----------------------------------------------+
| Speech Components    | Whisper, pyttsx3                             |
+----------------------+----------------------------------------------+


How the System Works
Step 1 — Upload Image
The user uploads an image through the interface.

Step 2 — Image Analysis
The system processes the image and extracts visual information such as:
objects
actions
scene details

Step 3 — Description Generation
A meaningful description is generated based on the visual content.

Step 4 — User Interaction
Users can ask questions related to the uploaded image.

Examples:

“What is the person doing?”
“How many people are present?”
“What color is the object?”

Step 5 — Voice Processing
If voice input is used:
speech is converted into text
query is processed

Step 6 — Response Generation
The system generates a context-aware answer.

Step 7 — Audio Response
The generated answer can also be spoken aloud.

PROJECT STRUCTURE 
VisionAssist/
│
├── app.py
├── model.py
├── requirements.txt
├── templates/
│   └── index.html
├── static/
├── uploads/
├── speech/
└── README.md

SYSTEM ARCHITECTURE 
User Uploads Image
        ↓
Image Processing Module
        ↓
Scene Description Generation
        ↓
User Interaction (Text / Voice)
        ↓
Question Processing
        ↓
Response Generation
        ↓
Audio Output

Installation Guide
1. Clone Repository
git clone <repository-link>
cd VisionAI
2. Create Virtual Environment
   
Windows
python -m venv venv
venv\Scripts\activate

Linux / macOS
python3 -m venv venv
source venv/bin/activate
4. Install Dependencies
pip install -r requirements.txt
5. Start Application
python app.py
6. Open in Browser
http://127.0.0.1:5000


The system was tested under multiple scenarios:
| Test Scenario          | Result |
| ---------------------- | ------ |
| Single object image    | Passed |
| Multi-object scene     | Passed |
| Question answering     | Passed |
| Voice input            | Passed |
| Voice output           | Passed |
| Invalid image handling | Passed |


 Advantages
Improves accessibility
Easy interaction through voice
Supports image understanding
Interactive and user-friendly
Works efficiently on local systems

 Limitations
Complex scenes may affect response quality
Processing speed depends on system performance
Accuracy may vary for unclear images

 
