from .basicEnum import BasicEnum



class RoleType(BasicEnum):
    ADMIN= "ADMIN"
    InventoryManager= "InventoryManager"
    SuperUser="SuperUser"
    Vendor="vendor"