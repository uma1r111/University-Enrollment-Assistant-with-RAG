import pandas as pd
from collections import defaultdict
from backend import solve_schedule  # Ensure your backend.py implements solve_schedule

def parse_excel_single_sheet(file_path: str) -> dict:
    """
    Reads an Excel file with the following columns:
      - 'Course Name'
      - 'Program'
      - 'Class Code'
      - 'Day'
      - 'Time'
      - 'Teacher'
    
    Each row represents one course session.
    Returns a dictionary with "courses" and "teachers".
    The course id is constructed as "Course Name_Class Code".
    Skips rows with any missing essential data.
    """
    df = pd.read_excel(file_path, engine='openpyxl')
    courses = []
    teachers_dict = {}
    required_columns = ['Course Name', 'Class Code', 'Day', 'Time', 'Teacher']
    
    for _, row in df.iterrows():
        if any(pd.isna(row[col]) for col in required_columns):
            continue
        
        time_slot = f"{row['Day']} {row['Time']}"
        course_id = f"{str(row['Course Name']).strip()}_{str(row['Class Code']).strip()}"
        course = {
            "id": course_id,
            "name": str(row["Course Name"]).strip(),
            "preferred_teacher": str(row["Teacher"]).strip(),  # default from Excel
            "time_slot": time_slot
        }
        courses.append(course)
        
        teacher_name = str(row["Teacher"]).strip()
        if teacher_name:
            if teacher_name not in teachers_dict:
                teachers_dict[teacher_name] = {
                    "id": teacher_name,
                    "name": teacher_name,
                    "available_slots": set()
                }
            teachers_dict[teacher_name]["available_slots"].add(time_slot)
    
    teachers = []
    for teacher_data in teachers_dict.values():
        teacher_data["available_slots"] = list(teacher_data["available_slots"])
        teachers.append(teacher_data)
    
    return {"courses": courses, "teachers": teachers}

def get_unique_course_names(data: dict) -> list:
    """Returns a sorted list of unique course names from the parsed data."""
    unique = set(course["name"].strip() for course in data["courses"] if course["name"])
    return sorted(unique)

def prompt_course_selection(available_courses: list) -> dict:
    """
    Displays available courses and lets the user select which courses they want to take.
    For each selected course, it filters the raw sessions for that course and extracts
    the teacher names (those who are associated with that course in the Excel data).
    The user then selects one of these teachers or enters one manually.
    Returns a dict mapping the selected course name (lowercased) to the user's preferred teacher.
    """
    print("Available courses:")
    for idx, course in enumerate(available_courses):
        print(f"{idx+1}. {course}")
    
    try:
        num = int(input("Enter the number of courses you want to take: "))
    except ValueError:
        print("Invalid input. Defaulting to 0 courses.")
        num = 0

    user_choices = {}
    for i in range(num):
        while True:
            try:
                selection = int(input(f"Enter the course number (1 to {len(available_courses)}) for course {i+1}: "))
                if 1 <= selection <= len(available_courses):
                    break
                else:
                    print("Invalid number, please try again.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")
        course_name = available_courses[selection - 1]
        
        # Filter sessions for the selected course (match by name, case-insensitive)
        rep_courses = [c for c in raw_data["courses"] if c["name"].strip().lower() == course_name.lower()]
        if rep_courses:
            # Instead of checking the teacher's available_slots (global),
            # use only the default teachers that appear for sessions of this course.
            teacher_options = sorted(set(c["preferred_teacher"] for c in rep_courses))
            if teacher_options:
                print(f"Available teachers for '{course_name}':")
                for idx, t in enumerate(teacher_options):
                    print(f"{idx+1}. {t}")
                try:
                    t_choice = int(input("Select a teacher by number (or 0 to enter manually): "))
                except ValueError:
                    t_choice = 0
                if t_choice == 0 or not (1 <= t_choice <= len(teacher_options)):
                    teacher_choice = input("Enter your preferred teacher: ").strip()
                else:
                    teacher_choice = teacher_options[t_choice - 1]
            else:
                teacher_choice = input(f"Enter the preferred teacher for '{course_name}': ").strip()
        else:
            teacher_choice = input(f"Enter the preferred teacher for '{course_name}': ").strip()
        user_choices[course_name.lower()] = teacher_choice
    return user_choices


def filter_user_courses(data: dict, selected_courses: dict) -> dict:
    """
    Filters the parsed data to include only sessions for the courses the user selected.
    Also updates each session's 'preferred_teacher' with the user-provided teacher.
    """
    filtered_courses = []
    for c in data["courses"]:
        if "98577" in c["id"] or "98568" in c["id"]:
            print(f"{c['id']!r} -> Teacher: {c['preferred_teacher']!r}")

    for course in data["courses"]:
        if course["name"].strip().lower() in selected_courses:
            if course["preferred_teacher"] in selected_courses[course["name"].strip().lower()]:
                print(repr(course["time_slot"]))

    for course in data["courses"]:
        if course["name"].strip().lower() in selected_courses:
            course["preferred_teacher"] = selected_courses[course["name"].strip().lower()]
            filtered_courses.append(course)
    return {"courses": filtered_courses, "teachers": data["teachers"]}

def group_assignments_by_day(assignments: list) -> dict:
    """Groups assignment records by day, assuming the day is the first token in time_slot."""
    grouped = defaultdict(list)
    for a in assignments:
        day = a["time_slot"].split()[0]
        grouped[day].append(a)
    return grouped

def display_schedule(grouped_schedule: dict):
    """Prints the final schedule grouped by day (Monday through Saturday)."""
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    print("\n--- Final Weekly Schedule ---")
    for day in day_order:
        print(f"\n--- {day} ---")
        day_assignments = grouped_schedule.get(day, [])
        if day_assignments:
            for idx, assignment in enumerate(day_assignments, start=1):
                print(f"{idx}) {assignment['course']} at {assignment['time_slot']} -> Teacher: {assignment['teacher']}")
        else:
            print("No classes scheduled.")

def display_conflicts(conflicts: list):
    """
    Prints simplified conflict messages that indicate what caused the conflict.
    For example, if a preferred teacher is not available, it prints that information.
    """
    if conflicts:
        print("\nConflicts detected during scheduling:")
        for conflict in conflicts:
            conflict_type = conflict.get("type", "unknown")
            course = conflict.get("course", "unknown course")
            preferred_teacher = conflict.get("preferred_teacher", "unknown teacher")
            message = conflict.get("message", "Conflict occurred.")
            if conflict_type == "preferred_unavailable":
                available_teachers = conflict.get("available_teachers", [])
                alt_text = ", ".join(available_teachers) if available_teachers else "No alternatives available"
                print(f"- For course '{course}': Preferred teacher '{preferred_teacher}' could not be assigned. {message} Alternatives: {alt_text}.")
            elif conflict_type == "no_teachers":
                print(f"- For course '{course}': {message}")
            else:
                print(f"- {message}")
    else:
        print("\nNo scheduling conflicts detected.")

# -------------------- Main Script --------------------

if __name__ == "__main__":
    file_path = "/Users/mohibalikhan/Desktop/project 901/AI RAG Project Transformed Schedule (1).xlsx"


    
    # Step 1: Parse the raw Excel data.
    raw_data = parse_excel_single_sheet(file_path)
    
    # Step 2: Get a sorted list of unique available courses.
    available_courses = get_unique_course_names(raw_data)
    
    # Step 3: Let the user select which courses they want to take and enter their preferred teacher.
    selected_preferences = prompt_course_selection(available_courses)
    
    # Step 4: Filter raw data to include only the selected courses and update with user preferences.
    user_data = filter_user_courses(raw_data, selected_preferences)
    
    # Step 5: Run the scheduling backend.
    result = solve_schedule(user_data)
    
    # Step 6: Group the assignments by day.
    assignments = result.get('assignments', [])
    grouped_schedule = group_assignments_by_day(assignments)
    
    # Step 7: Display the final weekly schedule.
    display_schedule(grouped_schedule)
    
    # Step 8: Display detailed conflict information with explanations.
    display_conflicts(result.get('conflicts', []))
11