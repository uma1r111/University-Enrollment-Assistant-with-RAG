-- Database: university_schedule

-- DROP DATABASE IF EXISTS university_schedule;

CREATE DATABASE university_schedule
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'English_United States.1252'
    LC_CTYPE = 'English_United States.1252'
    LOCALE_PROVIDER = 'libc'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;



	CREATE TABLE students (
    student_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    department VARCHAR(50),
    program VARCHAR(50),
    year_of_study INT CHECK (year_of_study BETWEEN 1 AND 4)
);

CREATE TABLE faculty (
    faculty_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    department VARCHAR(50) NOT NULL,
    title VARCHAR(50) CHECK (title IN ('Professor', 'Associate Professor', 'Lecturer', 'Assistant Professor'))
);



CREATE TABLE courses (
    course_id SERIAL PRIMARY KEY,
    course_code VARCHAR(10) UNIQUE NOT NULL,
    course_name VARCHAR(100) NOT NULL,
    credit_hours INT CHECK (credit_hours BETWEEN 1 AND 6),
    department VARCHAR(50) NOT NULL
);


CREATE TABLE sections (
    section_id SERIAL PRIMARY KEY,
    course_id INT REFERENCES courses(course_id) ON DELETE CASCADE,
    faculty_id INT REFERENCES faculty(faculty_id) ON DELETE SET NULL,
    semester VARCHAR(20) NOT NULL,
    section_code VARCHAR(5) NOT NULL CHECK (section_code SIMILAR TO '[A-Z][0-9]?'),
    UNIQUE(course_id, semester, section_code)
);



CREATE TABLE rooms (
    room_id SERIAL PRIMARY KEY,
    room_number VARCHAR(10) UNIQUE NOT NULL,
    building VARCHAR(50) NOT NULL,
    capacity INT CHECK (capacity > 0)
);

CREATE TABLE schedule (
    schedule_id SERIAL PRIMARY KEY,
    section_id INT REFERENCES sections(section_id) ON DELETE CASCADE,
    room_id INT REFERENCES rooms(room_id) ON DELETE SET NULL,
    day_of_week VARCHAR(10) CHECK (day_of_week IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday')),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL CHECK (end_time > start_time)
);


CREATE TABLE enrollment (
    enrollment_id SERIAL PRIMARY KEY,
    student_id INT REFERENCES students(student_id) ON DELETE CASCADE,
    section_id INT REFERENCES sections(section_id) ON DELETE CASCADE,
    enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    grade CHAR(2) CHECK (grade IN ('A', 'B', 'C', 'D', 'F', 'W', 'I'))
);



INSERT INTO students (first_name, last_name, email, department, program, year_of_study) VALUES
('Ali', 'Khan', 'ali.khan@example.com', 'Computer Science', 'BSc CS', 2),
('Sara', 'Ahmed', 'sara.ahmed@example.com', 'Business Administration', 'BBA', 3);

INSERT INTO faculty (first_name, last_name, email, department, title) VALUES
('Dr. Asad', 'Hussain', 'asad.hussain@example.com', 'Computer Science', 'Professor'),
('Dr. Maria', 'Iqbal', 'maria.iqbal@example.com', 'Business Administration', 'Lecturer');


INSERT INTO courses (course_code, course_name, credit_hours, department) VALUES
('CS101', 'Introduction to Programming', 3, 'Computer Science'),
('MGT202', 'Principles of Management', 3, 'Business Administration');


INSERT INTO sections (course_id, faculty_id, semester, section_code) VALUES
(1, 1, 'Spring 2025', 'A1'),
(2, 2, 'Spring 2025', 'B1');


INSERT INTO rooms (room_number, building, capacity) VALUES
('C-101', 'Main Block', 40),
('B-202', 'Business Block', 50);


INSERT INTO schedule (section_id, room_id, day_of_week, start_time, end_time) VALUES
(1, 1, 'Monday', '09:00:00', '10:30:00'),
(2, 2, 'Wednesday', '11:00:00', '12:30:00');

INSERT INTO enrollment (student_id, section_id, grade) VALUES
(1, 1, 'A'),
(2, 2, 'B');

-- Get All Students Enrolled in a Course
SELECT s.student_id, s.first_name, s.last_name, c.course_name, sec.section_code
FROM students s
JOIN enrollment e ON s.student_id = e.student_id
JOIN sections sec ON e.section_id = sec.section_id
JOIN courses c ON sec.course_id = c.course_id
WHERE c.course_code = 'CS101';

-- Get Faculty Assigned to a Course
SELECT f.first_name, f.last_name, c.course_name, sec.section_code
FROM faculty f
JOIN sections sec ON f.faculty_id = sec.faculty_id
JOIN courses c ON sec.course_id = c.course_id
WHERE c.course_code = 'CS101';


-- get student schedule 

SELECT s.first_name, s.last_name, c.course_name, sch.day_of_week, sch.start_time, sch.end_time, r.room_number
FROM students s
JOIN enrollment e ON s.student_id = e.student_id
JOIN sections sec ON e.section_id = sec.section_id
JOIN courses c ON sec.course_id = c.course_id
JOIN schedule sch ON sec.section_id = sch.section_id
JOIN rooms r ON sch.room_id = r.room_id
WHERE s.student_id = 1;


-- get faculty schedule over here
SELECT f.first_name, f.last_name, c.course_name, sch.day_of_week, sch.start_time, sch.end_time, r.room_number
FROM faculty f
JOIN sections sec ON f.faculty_id = sec.faculty_id
JOIN courses c ON sec.course_id = c.course_id
JOIN schedule sch ON sec.section_id = sch.section_id
JOIN rooms r ON sch.room_id = r.room_id
WHERE f.faculty_id = 1;


-- Count Students in Each Course 
SELECT c.course_name, COUNT(e.student_id) AS total_students
FROM courses c
JOIN sections sec ON c.course_id = sec.course_id
JOIN enrollment e ON sec.section_id = e.section_id
GROUP BY c.course_name;


