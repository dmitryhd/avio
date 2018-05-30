from locust import HttpLocust, TaskSet

def login(l):
    l.client.post("/login", {"username":"ellen_key", "password":"education"})

def info(l):
    l.client.get("/_info")

def profile(l):
    l.client.get("/profile")

class UserBehavior(TaskSet):
    tasks = {info: 1}

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 0
    max_wait = 0