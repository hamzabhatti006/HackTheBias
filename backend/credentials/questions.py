# This file handles questions for each lesson
# Beginner questions use images + text input
# Higher levels can later add camera / AI input

# All questions stored in Python for now
QUESTIONS = [
    # ---------------- BEGINNER: Alphabet Basics (lesson_id = 101) ----------------

    {
        "id": 1001,                         # unique question id
        "lesson_id": 101,                   # links question to lesson
        "prompt": "What letter is this sign?",
        "image_url": "/ASL/A.png", # frontend loads this image
        "hint": "It's the first letter of the alphabet.",
        "input_type": "text",               # user types answer
        "answer": "A",                      # backend-only (do not send to frontend)
    },
    {
        "id": 1002,
        "lesson_id": 101,
        "prompt": "What letter is this sign?",
        "image_url": "/ASL/B.png",
        "hint": "Your fingers are flat and pointing up.",
        "input_type": "text",
        "answer": "B",
    },

    {
        "id": 1003,
        "lesson_id": 101,
        "prompt": "What letter is this sign?",
        "image_url": "/ASL/C.png",
        "hint": "Your hand forms a 'C' shape.",
        "input_type": "text",
        "answer": "C",
    },

    {
        "id": 1004,
        "lesson_id": 101,
        "prompt": "What letter is this sign?",
        "image_url": "/ASL/D.png",
        "hint": "Your index finger points up while other fingers touch your thumb.",
        "input_type": "text",
        "answer": "D",
    },
]

# Returns questions for a given lesson
def get_questions_for_lesson(lesson_id):
    lesson_id = int(lesson_id)

    # Filter questions that belong to this lesson
    lesson_questions = [
        q for q in QUESTIONS if q["lesson_id"] == lesson_id
    ]

    # Remove answers before sending to frontend
    safe_questions = []
    for q in lesson_questions:
        safe_questions.append({
            "id": q["id"],
            "prompt": q["prompt"],
            "image_url": q["image_url"],
            "hint": q["hint"],
            "input_type": q["input_type"],
        })

    return safe_questions