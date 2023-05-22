import json

def requestChallenges():
    # Open the JSON file
    with open('tasks.json') as file:
        # Load JSON data
        data = json.load(file)
    challenges=[]
    # Iterate over the categories and tasks
    for category in data['challanges']:
        challenges.append(category)
    # for category in challenges:
    #     print(f"Category: {category['name']} ({category['short_name']})")
    #     print("Tasks:",category['tasks'])
    #     for task in category['tasks']:
    #         print(f"  Task: {task['name']}")
    #         print(f"    Flag: {task['flag']}")
    #         print(f"    Description: {task['desc']}")
    #         print(f"    File: {task['file']}")
    #     print()
    return challenges

def printChallenges():
    # Open the JSON file
    with open('tasks.json') as file:
        # Load JSON data
        data = json.load(file)
    challenges=[]
    # Iterate over the categories and tasks
    for category in data['categories']:
        challenges.append(category)
    for category in challenges:
        print(f"Category: {category['category']} ({category['short_name']})")
        print("Tasks:",category['tasks'])
        for task in category['tasks']:
            print(f"  Task: {task['name']}")
            print(f"    Flag: {task['flag']}")
            print(f"    Description: {task['desc']}")
            print(f"    File: {task['file']}")
        print()


    return challenges
# receiveChallenges()
# printChallenges()