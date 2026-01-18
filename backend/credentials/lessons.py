import mysql.connector  # allows Python to talk to MySQL

# Database connection info
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "YOUR_PASSWORD",   # change locally, don’t commit real password
    "database": "silent_speak_db",
    "port": 3306,
}

# All lessons grouped by level
LESSONS = {
    "BEGINNER": [
        {"id": 101, "title": "Alphabet Basics", "recommended_problem_count": 4},
        {"id": 102, "title": "Numbers 1–5", "recommended_problem_count": 4},
    ],
    "INTERMEDIATE": [
        {"id": 201, "title": "Greetings", "recommended_problem_count": 6},
    ],
    "PRO": [
        {"id": 301, "title": "Conversation Flow", "recommended_problem_count": 8},
    ],
    "EXPERT": [
        {"id": 401, "title": "Advanced Grammar", "recommended_problem_count": 10},
    ],
}

# Fixes casing and common typos in level names
def normalize_level(level):
    if not level:
        return "BEGINNER"
    level = level.upper()
    if level == "INTERMIDIATE":
        return "INTERMEDIATE"
    return level if level in LESSONS else "BEGINNER"

# Gets the user's progress from the database
def get_user_progress(user_id):
    conn = mysql.connector.connect(**DB_CONFIG)  # connect to DB
    cur = conn.cursor(dictionary=True)           # return rows as dicts

    # Query user progress
    cur.execute(
        "SELECT level_type, level_number FROM user_progress WHERE user_id=%s",
        (user_id,)
    )
    row = cur.fetchone()  # get one result

    cur.close()           # close cursor
    conn.close()          # close DB connection

    return row

# Picks which lesson to show based on level number
def pick_lesson(level_type, level_number):
    lessons = LESSONS[level_type]  # get lessons for that level

    # Convert level_number to a safe index
    index = max(0, min(level_number - 1, len(lessons) - 1))

    return lessons[index]

# Main function called when user clicks Start Learning
def start_learning(user_id, questions_module=None):

    # Get progress from DB
    progress = get_user_progress(user_id)
    if not progress:
        return {"ok": False, "message": "No progress found"}

    # Normalize level name
    level_type = normalize_level(progress["level_type"])

    # Choose the correct lesson
    lesson = pick_lesson(level_type, progress["level_number"])

    # Load questions for this lesson (if questions file exists)
    problems = []
    if questions_module:
        problems = questions_module.get_questions_for_lesson(lesson["id"])

    # Send everything back to backend / frontend
    return {
        "ok": True,
        "level": level_type,
        "lesson": lesson,
        "problems": problems,
    }