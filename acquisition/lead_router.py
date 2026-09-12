def route_lead(item):

    if item["type"] == "business_lead":
        return True

    return False


if __name__ == "__main__":

    test1 = {
        "title": "Need ecommerce website",
        "type": "business_lead"
    }

    test2 = {
        "title": "Software Engineer",
        "type": "job"
    }

    print(route_lead(test1))
    print(route_lead(test2))