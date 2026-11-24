GRADE_POINTS = {
    "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7, "D+": 1.3, "D": 1.0, "F": 0.0,
}


class Student:
    def __init__(self, name):
        self.name = name
        self._courses = []
        self._grades = {}  # Course -> grade points (0.0-4.0)

    def record_grade(self, course, grade):
        """Record a letter grade ("A-") or grade points (3.7) for an enrolled course."""
        if course not in self._courses:
            raise ValueError(f"{self.name} is not enrolled in {course.name}.")
        if isinstance(grade, str):
            key = grade.strip().upper()
            if key not in GRADE_POINTS:
                raise ValueError(f"Unknown letter grade: {grade!r}")
            points = GRADE_POINTS[key]
        elif 0.0 <= grade <= 4.0:
            points = float(grade)
        else:
            raise ValueError("Grade points must be between 0.0 and 4.0.")
        self._grades[course] = points

    @property
    def gpa(self):
        """Credit-weighted GPA over graded courses, or None if none are graded."""
        total_credits = sum(c.credits for c in self._grades)
        if total_credits == 0:
            return None
        weighted = sum(c.credits * pts for c, pts in self._grades.items())
        return round(weighted / total_credits, 2)

    @property
    def courses(self):
        return self._courses.copy()

    def change_courses(self, course_to_add=None, course_to_remove=None):
        """Drop and/or enroll in a course; both sides stay in sync."""
        if course_to_remove is not None:
            course_to_remove.drop(self)
        if course_to_add is not None:
            course_to_add.enroll(self)

    def __repr__(self):
        return f"Student({self.name!r})"


class Professor:
    def __init__(self, name):
        self.name = name
        self._current_courses = []
        self._past_courses = []

    @property
    def current_courses(self):
        return self._current_courses.copy()

    @property
    def past_courses(self):
        return self._past_courses.copy()

    def assign(self, course):
        course.add_professor(self)

    def finish_term(self):
        """Move current courses to the past-course list."""
        for course in self._current_courses:
            if course not in self._past_courses:
                self._past_courses.append(course)
        self._current_courses.clear()
        return self.past_courses

    def __repr__(self):
        return f"Professor({self.name!r})"


class Course:
    def __init__(self, name, capacity, credits=3):
        self.name = name
        self.credits = credits
        self._capacity = capacity
        self._students = []
        self._professors = []

    @property
    def capacity(self):
        return self._capacity

    @property
    def spots_left(self):
        return self._capacity - len(self._students)

    @property
    def students(self):
        return self._students.copy()

    @property
    def professors(self):
        return self._professors.copy()

    def update_capacity(self, new_capacity):
        if new_capacity < len(self._students):
            raise ValueError("Capacity cannot be less than current enrollment.")
        self._capacity = new_capacity

    def enroll(self, student):
        if student in self._students:
            return
        if self.spots_left <= 0:
            raise ValueError(f"{self.name} is full.")
        self._students.append(student)
        student._courses.append(self)

    def drop(self, student):
        if student in self._students:
            self._students.remove(student)
            student._courses.remove(self)
            student._grades.pop(self, None)

    def add_professor(self, professor):
        if professor not in self._professors:
            self._professors.append(professor)
            professor._current_courses.append(self)

    def __repr__(self):
        return f"Course({self.name!r})"


if __name__ == "__main__":
    alex = Student("Alex")
    sam = Student("Sam")
    smith = Professor("Dr. Smith")
    cs = Course("Computer Science", 1)
    math = Course("Math", 5)

    smith.assign(cs)
    alex.change_courses(course_to_add=cs)

    print("Alex's courses:", alex.courses)
    print("CS students:", cs.students, "| spots left:", cs.spots_left)
    print("CS professors:", cs.professors)

    try:
        sam.change_courses(course_to_add=cs)
    except ValueError as e:
        print("Error:", e)

    alex.change_courses(course_to_add=math, course_to_remove=cs)
    print("After swap:", alex.courses, "| CS spots left:", cs.spots_left)

    print("Past courses after term:", smith.finish_term())

    # GPA demo (credit-weighted)
    lab = Course("Physics Lab", 5, credits=1)
    alex.change_courses(course_to_add=lab)
    print("GPA before grades:", alex.gpa)
    alex.record_grade(math, "A")      # 3 credits x 4.0
    alex.record_grade(lab, "B")       # 1 credit  x 3.0
    print("Alex's GPA:", alex.gpa)
