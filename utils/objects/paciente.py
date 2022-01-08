from utils.manager import update
from utils.manager import fetch
from utils.manager import create
from utils.objects.object import Object


class Paciente(Object):
    table = "paciente"

    id = ""  ##
    name = ""  ##
    last_name = ""  ##
    second_name = ""  ##

    address = ""  ##
    sex = ""  ##
    age = 0  ##
    clinic_id = ""  ##

    def __str__(self):
        return self.name + "/" + self.frname + "/" + self.clnh + "/" + self.cid
