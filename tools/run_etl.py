import os

from flash_llm.orchestration.pipelines.etl import digital_data_etl

if __name__ == "__main__":
    # Ensure the factory knows which DB to use
    os.environ["DATABASE_TYPE"] = "mongo"

    print("🚀 Triggering the Digital Data ETL Pipeline...")

    # Call your ZenML pipeline exactly as you defined it
    digital_data_etl.with_options(enable_cache=False)(
        user_full_name="siddhi vedika",
        links=[
            "https://github.com/imflash217/flash_llm",
            "https://github.com/imflash217/portfolio",
        ],
    )

    print("✅ Pipeline execution finished!")
