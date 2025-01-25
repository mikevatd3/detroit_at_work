import pandas as pd
import pandera as pa
from pandera.typing import Series


class OccupationsPreparedFor(pa.DataFrameModel):
    """
    FUTURE (as of 2025-01-24): run some kind of analysis on their suggested fields
    to connect back to the best fit SOC code.
    """
    training_id: int = pa.Field(nullable=False)
    code: str = pa.Field(nullable=False)

    class Config:
        strict=True
        unique=True


class Trainings(pa.DataFrameModel):
    """
    This is the schema for the Detroit at Work Scrape
    """
    id: int = pa.Field()
    provider: str = pa.Field()
    program: str = pa.Field()
    location: str = pa.Field()
    clinical_location: str = pa.Field(nullable=True)
    phone: str = pa.Field()
    website: str = pa.Field()
    description: str = pa.Field()
    reading_grade_level: str = pa.Field()
    math_grade_level: str = pa.Field(nullable=True)
    convictions_prohibited: str = pa.Field(nullable=True)
    other_requirements: str = pa.Field(nullable=True)
    required_supplies: str = pa.Field()
    weeks: int = pa.Field(nullable=True)
    total_hours: int = pa.Field(nullable=True)
    schedule: str = pa.Field()
    max_students: int = pa.Field()
    students_per_instructor: pd.Int64Dtype = pa.Field(nullable=True)
    completion_rate: float = pa.Field(nullable=True)
    placement_rate: float = pa.Field(nullable=True)
    credential_attainment_rate: float = pa.Field(nullable=True)
    credential_earned: str = pa.Field()
    occupations_prepared_for: str = pa.Field() # This is many to many ?
    average_grad_occ_wage: str = pa.Field(nullable=True) # If you can link to SOC we can calculate
    hs_diploma_required: bool = pa.Field()
    drug_screen_required: bool = pa.Field()
    background_check_required: bool = pa.Field()
    valid_drivers_license_required: bool = pa.Field()
    exam: bool = pa.Field()
    equipment_trained_on: str = pa.Field(nullable=True)
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
    "Average wage of graduates in these occupations": "average_grad_occ_wage",
    "High School Diploma / GED": "hs_diploma_required",
    "Drug Screen": "drug_screen_required",
    "Criminal Background Check": "background_check_required",
    "Valid Driver License": "valid_drivers_license_required",
    "Is there am exam required at the end of the training?": "exam",
    "Equipment graduates will be trained to use": "equipment_trained_on",
    "Training Delivery": "in_person_online",
}
