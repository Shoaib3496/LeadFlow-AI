from pipeline.pipeline_status import (
    get_pipeline_status,
    mark_running,
    mark_completed,
    mark_failed
)


print("\nInitial Status")
print(get_pipeline_status())


print("\nRunning Status")

mark_running()

print(get_pipeline_status())


print("\nCompleted Status")

mark_completed(
    {
        "collected": 50,
        "buyer_intent_rejected": 30,
        "business_fit_rejected": 10,
        "duplicates": 5,
        "saved": 5
    }
)

print(get_pipeline_status())


print("\nFailed Status Test")

mark_failed("Sample pipeline error")

print(get_pipeline_status())