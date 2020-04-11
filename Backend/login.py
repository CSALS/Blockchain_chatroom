users = dict({'charan': 'charan', 'rohit': 'rohit'})
def verify_login(username, password):
    if username in users:
        if users[username] == password:
            return True
        else:
            return False
    else:
        return False