from pipelines.global_pipeline import run_global_pipeline
from pipelines.china_pipeline import run_china_pipeline


if __name__ == "__main__":
    print("Starting weekly reading bot...")

    run_global_pipeline()

    run_china_pipeline()

    print("Weekly reading bot completed.")
