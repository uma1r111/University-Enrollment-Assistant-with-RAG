from ortools.sat.python import cp_model
from typing import Dict, List, Any

class SchedulingError(Exception):
    """Custom exception for scheduling errors"""
    pass

def validate_input(data: Dict) -> List[str]:
    errors = []
    if not all(key in data for key in ["courses", "teachers"]):
        errors.append("Missing required keys 'courses' or 'teachers' in input data")
        return errors
        
    for course in data["courses"]:
        required_fields = ["id", "name", "preferred_teacher", "time_slot"]
        missing = [field for field in required_fields if field not in course]
        if missing:
            errors.append(f"Course {course.get('name', 'Unknown')} missing required fields: {missing}")
            
    for teacher in data["teachers"]:
        required_fields = ["id", "name", "available_slots"]
        missing = [field for field in required_fields if field not in teacher]
        if missing:
            errors.append(f"Teacher {teacher.get('name', 'Unknown')} missing required fields: {missing}")
            
    return errors

def solve_schedule(data: Dict) -> Dict[str, Any]:
    try:
        # Basic input validation.
        if not isinstance(data, dict):
            return {
                'feasible': False,
                'error': 'Invalid input format',
                'conflicts': []
            }
        if 'courses' not in data or 'teachers' not in data:
            return {
                'feasible': False,
                'error': 'Missing required data (courses or teachers)',
                'conflicts': []
            }
            
        courses = data['courses']
        teachers = data['teachers']
        conflicts = []

        # Validate course and teacher data.
        for course in courses:
            required = ['id', 'name', 'preferred_teacher', 'time_slot']
            missing = [field for field in required if field not in course]
            if missing:
                conflicts.append({
                    'type': 'invalid_data',
                    'message': f"Course {course.get('name', 'Unknown')} missing fields: {', '.join(missing)}"
                })
        for teacher in teachers:
            required = ['id', 'name', 'available_slots']
            missing = [field for field in required if field not in teacher]
            if missing:
                conflicts.append({
                    'type': 'invalid_data',
                    'message': f"Teacher {teacher.get('name', 'Unknown')} missing fields: {', '.join(missing)}"
                })
        if conflicts:
            return {
                'feasible': False,
                'error': 'Invalid data format',
                'conflicts': conflicts
            }
        
        model = cp_model.CpModel()
        # Create a Boolean decision variable x[i, j] for each course session (i) and teacher (j)
        x = {}
        for i, course in enumerate(courses):
            for j, teacher in enumerate(teachers):
                x[(i, j)] = model.NewBoolVar(f'x_{i}_{j}')
                
        # Each session must be assigned exactly one teacher.
        for i, course in enumerate(courses):
            model.Add(sum(x[(i, j)] for j in range(len(teachers))) == 1)
            
        # For each session, disable assignments for teachers not available at that session's time.
        session_available = {}
        for i, course in enumerate(courses):
            available_set = set()
            for j, teacher in enumerate(teachers):
                if course['time_slot'] not in teacher['available_slots']:
                    model.Add(x[(i, j)] == 0)
                else:
                    available_set.add(teacher['name'])
            session_available[i] = available_set
            # Debug print for each session.
            print(f"Session {i} ({course['id']} at {course['time_slot']}): Available teachers: {available_set}")
        
        # Group sessions by unique course id (class code remains constant).
        # Here, we assume that course['id'] is constructed as "Course Name_Class Code"
        course_groups = {}
        for i, course in enumerate(courses):
            # Using course id for grouping (which contains the class code).
            key = course['id']
            course_groups.setdefault(key, []).append(i)
        
        # Debug: Print grouped sessions.
        print("\nGrouped sessions by course (by class code):")
        for key, indices in course_groups.items():
            print(f"Course '{key}': sessions {indices}")
        
        # Enforce uniform assignment for sessions in the same course group.
        for group in course_groups.values():
            if len(group) > 1:
                for j in range(len(teachers)):
                    for idx1 in range(len(group)):
                        for idx2 in range(idx1+1, len(group)):
                            i1 = group[idx1]
                            i2 = group[idx2]
                            model.Add(x[(i1, j)] == x[(i2, j)])
        
        # Aggregate available teachers per course group.
        aggregated_conflicts = []
        for course_id, indices in course_groups.items():
            # Get the default teachers recorded in the raw data for this course group.
            group_default = set(courses[i]['preferred_teacher'] for i in indices)
            # Compute the intersection of session availability.
            group_avail_intersection = None
            for i in indices:
                if group_avail_intersection is None:
                    group_avail_intersection = session_available[i].copy()
                else:
                    group_avail_intersection &= session_available[i]
            # Now, restrict alternatives to those teachers that are recorded for this course.
            group_available = group_default & group_avail_intersection if group_avail_intersection is not None else group_default
            
            # Debug: Print aggregated available teachers.
            print(f"Course '{course_id}': Default teachers: {group_default}, Intersection: {group_avail_intersection}, Final alternatives: {group_available}")
            
            # Use the preferred teacher from the first session (they should be uniform now).
            preferred = courses[indices[0]]['preferred_teacher']
            if not group_available:
                aggregated_conflicts.append({
                    'type': 'no_teachers',
                    'course': courses[indices[0]]['name'],
                    'message': f"No teachers available for {courses[indices[0]]['name']} (ID: {course_id}) across all sessions."
                })
            elif preferred not in group_available:
                aggregated_conflicts.append({
                    'type': 'preferred_unavailable',
                    'course': courses[indices[0]]['name'],
                    'preferred_teacher': preferred,
                    'available_teachers': sorted(group_available),
                    'message': f"Preferred teacher {preferred} not available for {courses[indices[0]]['name']} (ID: {course_id}). Alternatives: {', '.join(sorted(group_available))}."
                })
                
        # If any course group has no available teachers, scheduling is infeasible.
        if any(conflict['type'] == 'no_teachers' for conflict in aggregated_conflicts):
            return {
                'feasible': False,
                'error': 'Scheduling conflicts detected',
                'conflicts': aggregated_conflicts,
                'assignments': []
            }
        
        # Add objective: maximize assignment of the preferred teacher.
        objective_terms = []
        for i, course in enumerate(courses):
            for j, teacher in enumerate(teachers):
                if teacher['name'] == course['preferred_teacher']:
                    objective_terms.append(x[(i, j)])
                else:
                    objective_terms.append(0 * x[(i, j)])
        model.Maximize(sum(objective_terms))
        
        print("\nObjective function built. Now solving the model...")
        
        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            assignments = []
            for i, course in enumerate(courses):
                for j, teacher in enumerate(teachers):
                    if solver.Value(x[(i, j)]) == 1:
                        assignments.append({
                            'course': course['name'],
                            'teacher': teacher['name'],
                            'time_slot': course['time_slot'],
                            'preferred': teacher['name'] == course['preferred_teacher']
                        })
            print("Model solved successfully.")
            return {
                'feasible': True,
                'assignments': assignments,
                'conflicts': aggregated_conflicts,
                'status': 'optimal' if status == cp_model.OPTIMAL else 'feasible'
            }
        else:
            print("No feasible solution found.")
            return {
                'feasible': False,
                'error': 'No feasible solution found',
                'conflicts': aggregated_conflicts,
                'assignments': []
            }
        
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        return {
            'feasible': False,
            'error': f'Unexpected error: {str(e)}',
            'conflicts': [{
                'type': 'system_error',
                'message': str(e)
            }],
            'assignments': []
        }
