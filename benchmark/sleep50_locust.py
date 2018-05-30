from locust import HttpLocust, TaskSet

def sleep50(l):
    l.client.get("/sleep50")

class UserBehavior(TaskSet):
    tasks = {sleep50: 1}

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 0
    max_wait = 0