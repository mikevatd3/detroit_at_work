import click
import pandas as pd
from pandera.errors import SchemaError, SchemaErrors
import tomli

from detroit_at_work import setup_logging, db_engine, metadata_engine
from metadata_audit.capture import record_metadata
from sqlalchemy.orm import sessionmaker

from detroit_at_work.schema import Trainings, renames

logger = setup_logging()

table_name = "trainings"

with open("metadata.toml", "rb") as md:
    metadata = tomli.load(md)


def remove_hours_weeks(string):
    """
    Takes inputs like '1234 hours' or '5678 weeks'
    and returns 1234, 5678.
    """
    try:
        digits, *_ = string.split(" ")

        return int(digits)

    except AttributeError:
        return string


def replace_na(val):
    if val == "N/A":
        return None
    return val


def clear_pct(pct_str: str):
    try:
        return int(pct_str.replace("%", ""))
    except (AttributeError, ValueError):
        return pct_str


def yes_no_to_bool(yn: str):
    if yn == "Yes":
        return True
    return False


fields_for_yn = [
    "hs_diploma_required",
    "drug_screen_required",
    "background_check_required",
    "valid_drivers_license_required",
    "exam",
]

fields_remove_na = [
    "clinical_location",
    "convictions_prohibited",
    "other_requirements",
    "students_per_instructor",
    "completion_rate",
    "placement_rate",
    "credential_attainment_rate",
    "math_grade_level",
    "equipment_trained_on"
]


@click.command()
@click.argument("edition_date")
@click.option("-m", "--metadata_only", is_flag=True, help="Skip uploading dataset.")
def main(edition_date, metadata_only):
    if metadata_only:
        logger.info("Metadata only was selected.")

    edition = metadata["tables"][table_name]["editions"][edition_date]

    result = (
        pd.read_csv(edition["raw_path"])
        .rename(columns=renames)
        .dropna(subset="program")
        .rename( # rename the columns that I have to fix
            columns={
                "weeks": "__weeks",
                "total_hours": "__total_hours",
                **{
                    col: f"__{col}"
                    for col in fields_for_yn + fields_remove_na
                }
            }
        )
        .assign(
            # A few variables need to be standardized to integers
            weeks = lambda df: df["__weeks"].apply(replace_na).apply(remove_hours_weeks),
            total_hours = lambda df: df["__total_hours"].apply(remove_hours_weeks),
            **{
                col: lambda df, col=col: df[f"__{col}"].apply(yes_no_to_bool)
                for col in fields_for_yn
            },
            **{
                col: lambda df, col=col: df[f"__{col}"].apply(clear_pct).apply(replace_na)
                for col in fields_remove_na
            }
        )
        .drop(
            [
                "__weeks",
                "__total_hours",
                *[
                    f"__{col}" for col in fields_for_yn + fields_remove_na
                ]
            ], axis=1
        )
        .reset_index()
        .rename(columns={"index": "id"})
    )

    logger.info(f"Number of rows: {len(result)}")
    logger.info(f"Cleaning {table_name} was successful validating schema.")

    # Validate
    try:
        validated = Trainings.validate(result)
        logger.info(
            f"Validating {table_name} was successful. Recording metadata."
        )
    except (SchemaError, SchemaErrors) as e:
        logger.error(f"Validating {table_name} failed.", e)
        return

    with metadata_engine.connect() as db:
        logger.info("Connected to metadata schema.")

        record_metadata(
            Trainings,
            __file__,
            table_name,
            metadata,
            edition_date,
            result,
            sessionmaker(bind=db)(),
            logger,
        )

        db.commit()
        logger.info("successfully recorded metadata")

    if not metadata_only:
        with db_engine.connect() as db:
            logger.info("Metadata recorded, pushing data to db.")

            validated.to_sql(  # type: ignore
                table_name, db, index=False, schema=metadata["schema"], if_exists="append"
            )
    else:
        logger.info("Metadata only specified, so process complete.")

if __name__ == "__main__":
    main()
