from pathlib import Path
from profsagent.ingest.canonicalize import TopicCanonicalizer
from profsagent.ingest.derived import DerivedRelationshipEngine
from profsagent.ingest.pipeline import LayerAIngestionPipeline
from profsagent.ingest.programmes import load_programme_spec


def test_load_programme_specification():
    prog = load_programme_spec()
    assert prog["programme_code"] == "BTECH_CSE"
    assert len(prog["pos"]) == 12
    assert len(prog["peos"]) == 4
    assert prog["pos"][0]["po_id"] == "PO1"


def test_pipeline_single_course_processing(tmp_path: Path):
    pipeline = LayerAIngestionPipeline(raw_dir=tmp_path, output_dir=tmp_path)

    sample_sheet = """
    # Course Details
    Course Code: CSE101
    Course Title: Introduction to Programming
    Credits: 4
    Department: CSE

    # Prerequisites
    Prerequisites: None

    # Course Outcomes (COs)
    CO1: Formulate algorithmic solutions for computational problems
    CO2: Implement modular code in Python using functions
    CO3: Debug and test programs to eliminate syntax errors
    CO4: Apply basic data structures including lists and dictionaries

    # Weekly Lecture Plan
    Week 1: Introduction to Computation, Variables and Expressions
    Week 2: Conditional Statements, Branching and Booleans
    Week 3: Loops, Iteration and Nested Loops
    Week 4: Functions, Parameter Passing and Scope
    Week 5: Strings, String Manipulation and Formatting
    Week 6: Lists, Tuples and Sequence Operations
    Week 7: Dictionaries and Sets
    Week 8: Mid-Semester Recess and Review
    Week 9: Recursion and Divide-and-Conquer Basics
    Week 10: File Handling, Reading and Writing Data
    Week 11: Error Handling, Exceptions and Assertions
    Week 12: Object-Oriented Basics, Classes and Attributes
    Week 13: Standard Libraries and Modules
    Week 14: Final Projects, Code Review and Synthesis

    # Assessment Plan
    Midsem: 25%
    Endsem: 35%
    Assignments: 25%
    Quizzes: 15%

    # Resource Material
    1. Think Python by Allen B. Downey
    """

    course, report = pipeline.process_sheet_text(sample_sheet, Path("CSE101.txt"))

    assert course.header.course_code == "CSE101"
    assert len(course.course_outcomes) == 4
    assert len(course.weekly_plans) == 14
    assert course.total_assessment_weight == 100.0
    assert report.passed


def test_derived_topic_precedence():
    canon = TopicCanonicalizer()
    derived = DerivedRelationshipEngine(canon)

    pipeline = LayerAIngestionPipeline()
    sample_sheet = """
    # Course Details
    Course Code: CSE201
    Course Title: Advanced Programming
    Credits: 4

    # Weekly Lecture Plan
    Week 1: Object-Oriented Design and Patterns
    Week 2: Version Control and Git Workflows
    Week 3: Concurrency and Synchronization
    Week 4: Software Testing and Verification

    # Course Outcomes (COs)
    CO1: Design object-oriented software
    CO2: Apply version control workflows
    CO3: Implement concurrent threads
    CO4: Test and verify code

    # Assessment Plan
    Endsem: 100%
    """
    course, _ = pipeline.process_sheet_text(sample_sheet, Path("CSE201.txt"))
    precedence = derived.compute_intra_course_topic_precedence(course)

    assert len(precedence) > 0
    # The first topic should precede the second topic
    t1, t2, w1, w2 = precedence[0]
    assert w1 < w2
