from enum import Enum

class ServiceStatusTypes(Enum):
    PendingCreate   = 1
    PendingPay      = 2
    PendingDelete   = 3
    PendingTransfer = 4
    ServerHold      = 5
    ClientHold      = 6
    OK              = 7
    PendingOK       = 8
    PendingDelegate = 9
    TransferHold    = 10
    TestPeriod      = 11
    Completed       = 12
