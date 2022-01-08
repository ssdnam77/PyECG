from utils.manager import update
from utils.manager import fetch
from utils.manager import create
from utils.objects.object import Object


class Registro(Object):
    table = "registro"

    cid = ""  ##
    date = ""  ##
    last_update = ""  ##
    treatment = ""  ##
    observations = ""  ##
    diagnosis = ""  ##
    reg_count = 0  ##
    reg_ig = ""  ##
    rec_fs = 0  ##
    rec_nleads = 0  ##
    rec_posleads = ""  ##
    metadt_rec = ""  ##

    def __str__(self):
        return self.name + "/" + self.frname + "/" + self.clnh + "/" + self.cid
