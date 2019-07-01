from utils.manager import create
from utils.manager import update
from utils.manager import fetch
from utils.manager import find
# from utils.manager import delete

class Object:

    def update(self):
        return update(self)

    def create(self):
        return create(self)

    def fetch(self):
        return fetch(self)

    def find(self):
        return find(self)

    # def delete(self):
    #     return delete(self)