import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sources.business_source_manager import collect_business_sources


def collect_all_sources():
    return collect_business_sources()


if __name__ == "__main__":

    posts = collect_all_sources()

    print(f"\nCollected {len(posts)} posts")