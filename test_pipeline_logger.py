from pipeline.pipeline_logger import get_pipeline_logger


logger = get_pipeline_logger()

logger.info("LeadFlow AI processing log test")

logger.info("Production pipeline logger working successfully")

logger.warning("This is a sample warning")

print("\nLogger test completed.")
print("Check the logs folder.")