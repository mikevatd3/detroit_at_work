import pandera as pa
from pandera.typing import Series


class TrainingsSchema(pa.DataFrameModel):
    """
    This is the schema for the Detroit at Work Scrape
    """
    provider: str = pa.Field()
    program: str = pa.Field()
    location: str = pa.Field()
    clinical_location: str = pa.Field()
    phone: str = pa.Field()
    website: str = pa.Field()
    description: str = pa.Field()
    reading_grade_level: str = pa.Field()
    math_grade_level: str = pa.Field()
    convictions_prohibited: str = pa.Field()
    other_requirements: str = pa.Field()
    required_supplie: str = pa.Field()
    weeks: str = pa.Field()
    total_hours: str = pa.Field()
    schedule: str = pa.Field()
    max_students: str = pa.Field()
    students_per_instructor: str = pa.Field()
    completion_rat: str = pa.Field()
    placement_rate: str = pa.Field()
    credential_attainment_rate: str = pa.Field()
    credential_earned: str = pa.Field()
    occupations_prepared_for: str = pa.Field() # This is many to many ?
    average_grad_wage: str = pa.Field()
    hs_diploma_required: str = pa.Field()
    drug_screen_required: str = pa.Field()
    background_check_required: str = pa.Field()
    valid_drivers_license_required: str = pa.Field()
    exam: str = pa.Field()
    equipment_used: str = pa.Field()
    in_person_online: str = pa.Field()

    class Config:  # type: ignore
        strict = True
        coerce = True


renames = {
    "Training Provider": "provider",
    "Training Program": "program",
    "Training Location": "location",
    "Clinical Location If Applicable": "clinical_location",
    "Phone Number": "phone",
    "Website": "website",
    "Description of Training ProgramRow1": "description",
    "Reading Grade Level": "reading_grade_level",
    "Math Grade Level": "math_grade_level",
    "If yes which types of convictions are not allowed": "convictions_prohibited",
    "Other Requirements": "other_requirements",
    "Required Supplies Available through Detroit at Work For more information contact your Detroit at Work Career Coach": "required_supplies",
    "Number of Weeks": "weeks",
    "Number of Total Hours": "total_hours",
    "Schedule": "schedule",
    "Maximum number of students in each class": "max_students",
    "Number of students for each instructor": "students_per_instructor",
    "Percentage of students who complete the training program Completion Rate": "completion_rate",
    "Percentage of graduates who are placed in employment related to their training within 120 days of completing the program Training Related Placement Rate": "placement_rate",
    "Percentage of students who complete the training program and earn an industry recognized certification or license Credential Attainment Rate": "credential_attainment_rate",
    "Credentials graduates earn": "credential_earned",
    "Occupations graduates will be prepared to enter": "occupations_prepared_for", # This is many to many ?
    "Average wage of graduates in these occupations": "average_grad_wage",
    "High School Diploma / GED": "hs_diploma_required",
    "Drug Screen": "drug_screen_required",
    "Criminal Background Check": "background_check_required",
    "Valid Driver License": "valid_drivers_license_required",
    "Is there am exam required at the end of the training?": "exam",
    "Equipment graduates will be trained to use": "equipment_used",
    "Training Delivery": "in_person_online",
}
