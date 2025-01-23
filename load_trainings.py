import click
import pandas as pd
from pandera.errors import SchemaError, SchemaErrors
import tomli

from detroit_at_work import setup_logging, db_engine, metadata_engine
from metadata_audit.capture import record_metadata
from sqlalchemy.orm import sessionmaker

from detroit_at_work.schema import TrainingsSchema, rename

logger = setup_logging()

table_name = "trainings"

with open("metadata.toml", "rb") as md:
    metadata = tomli.load(md)


@click.command()
@click.argument("edition_date")
@click.option("-m", "--metadata_only", is_flag=True, help="Skip uploading dataset.")
def main(edition_date, metadata_only):
    if metadata_only:
        logger.info("Metadata only was selected.")

    edition = metadata["tables"][table_name]["editions"][edition_date]

    result = (
        pd.read_csv(edition["raw_path"])
        .rename(
            columns={
                "Code": "code",
                "Title": "title",
                "Description": "description",
            }
        )
        .drop("Unnamed: 0", axis=1)
    )

    logger.info(f"Cleaning {table_name} was successful validating schema.")

    # Validate
    try:
        validated = TrainingsSchema.validate(result)
        logger.info(
            f"Validating {table_name} was successful. Recording metadata."
        )
    except (SchemaError, SchemaErrors) as e:
        logger.error(f"Validating {table_name} failed.", e)

    with metadata_engine.connect() as db:
        logger.info("Connected to metadata schema.")

        record_metadata(
            TrainingsSchema,
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
