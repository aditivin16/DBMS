import mysql.connector

host = ""
port = ""
password = ""

def connect():
    return mysql.connector.connect(
        host=host,
        port=port,
        user="root",
        password=password,
        database="academic_insti"
    )

def val_dept(dept_id, cursor):
    cursor.execute('SELECT * FROM department WHERE deptId = %s', (dept_id,))
    return bool(cursor.fetchone())

def val_course(course_id, dept_id, cursor):
    cursor.execute("SELECT * FROM course WHERE courseId = %s AND deptNo = %s", (course_id, dept_id))
    return bool(cursor.fetchone())

def val_classroom(classroom, cursor):
    cursor.execute('SELECT * FROM teaching WHERE classroom = %s', (classroom,))
    return bool(cursor.fetchall())

def val_course_2(course_id, cursor):
    cursor.execute("SELECT * FROM course WHERE courseId = %s", (course_id,))
    return bool(cursor.fetchone())

def val_empId(emp_id,dept_id, cursor):
    cursor.execute("SELECT * FROM professor WHERE empId = %s AND deptNo = %s", (emp_id, dept_id))
    return bool(cursor.fetchone())

def val_stud(rollNo, cursor):
    cursor.execute("SELECT * FROM student WHERE rollNo = %s", (rollNo,))
    return bool(cursor.fetchone())

def prereq(course_id, roll_no, cursor):
    cursor.execute("SELECT preReqCourse FROM prerequisite WHERE courseId = %s", (course_id,))
    prerequisites = cursor.fetchall()

    for (prereq_id,) in prerequisites:
        cursor.execute("""
            SELECT grade FROM enrollment
            WHERE rollNo = %s AND courseId = %s AND grade IS NOT NULL
        """, (roll_no, prereq_id))
        result = cursor.fetchone()
        if not result or result[0] == 'U':
            print(f"Cannot enroll in {course_id}: Prerequisite '{prereq_id}' not passed.")
            return False
    return True

def add_teaching():
    conn = connect()
    cursor = conn.cursor()

    while True:
        pr = input("Do you wish to proceed? (y/n) ").strip().lower()
        if pr == 'n':
            break

        dept_id = input("Enter department ID: ")
        course_id = input("Enter course ID: ")
        emp_id = input("Enter teacher (employee) ID: ")
        classroom = input("Enter classroom: ")

        cursor.execute("""
            SELECT * FROM teaching
            WHERE empId = %s AND courseId = %s AND sem = %s AND year = %s AND classroom = %s
        """, (emp_id, course_id, 'even', 2006, classroom))

        if cursor.fetchone():
            print("Teaching instance already exists. Current entry not added.")
            continue

        if not val_dept(dept_id, cursor):
            print("Invalid department ID. Kindly re-enter details.")
            continue

        if not val_empId(emp_id,dept_id, cursor):
            print("Invalid professor ID. Kindly re-enter details.")
            continue

        if not val_course(course_id, dept_id, cursor):
            print("The given department does not offer this course. Kindly re-enter details.")
            continue
        
        if not val_classroom(classroom, cursor):
            print("Invalid classroom entered. Kindly re-enter details.")
            continue

        cursor.execute("""
            INSERT INTO teaching(empId, courseId, sem, year, classroom)
            VALUES (%s, %s, %s, %s, %s)
        """, (emp_id, course_id, 'even', 2006, classroom))
        conn.commit()
        print("Teaching instance added successfully.")

    cursor.close()
    conn.close()
    return 

def enroll_stud():
    conn = connect()
    cursor = conn.cursor()

    while True:
        pr = input("Do you wish to proceed (y/n)? ").strip().lower()
        if pr == 'n':
            break

        roll_no = input("Enter student roll number: ")
        course_ids = input("Enter course IDs to enroll in (comma-separated): ").split(',')

        if not val_stud(roll_no, cursor):
            print("Invalid roll number. Kindly re-enter details.")
            continue

        for course_id in course_ids:
            course_id = course_id.strip()

            cursor.execute("""
                SELECT * FROM enrollment 
                WHERE rollNo = %s AND courseId = %s AND (grade <> %s OR (year = %s AND sem = %s))
            """, (roll_no, course_id, 'U', 2006, 'even'))

            if cursor.fetchone():
                print(f"Student already enrolled or passed {course_id}.")
                continue

            if not val_course_2(course_id, cursor):
                print(f"Invalid course ID {course_id}. Enrollment terminated.")
                continue

            if not prereq(course_id, roll_no, cursor):
                continue

            cursor.execute("""
                INSERT INTO enrollment (rollNo, courseId, sem, year)
                VALUES (%s, %s, %s, %s)
            """, (roll_no, course_id, 'even', 2006))
            conn.commit()
            print(f"Student {roll_no} successfully enrolled in {course_id}")

    cursor.close()
    conn.close()
    return 

def main():
   
    while True:
        print("\n1. Add teaching instances")
        print("2. Enroll students")
        print("Press any other number to exit")

        try:
            choice = int(input("Enter your choice: "))
        except ValueError:
            break

        if choice == 1:
            add_teaching()
        elif choice == 2:
            enroll_stud()
        else:
            break

if __name__ == "__main__":
    host = input ('enter host: ')
    port = int(input ('enter port: ') )  
    password = input ('enter password: ')
    main()

