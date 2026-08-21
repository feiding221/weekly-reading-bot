from pipelines.global_pipeline import run_global_pipeline


if __name__ == "__main__":
    print("Starting weekly reading bot...")

    # 暂停 China AI Reading，仅运行 Global Reading Pipeline。
    # China pipeline 代码保留，后续需要恢复时再重新启用。
    run_global_pipeline()

    print("Weekly reading bot completed.")
