from enum import Enum
#------------------------------------------------------------------------------
class MessageCommand (Enum):
    Error    = -1
    StartFit = 1
    Status   = 2
    Delete   = 3
    GetData  = 4
    PrintStatus = 5
    GetResults  = 6
    GetDbStatus = 7
    GetTags     = 8
    GetRefl1dResults = 9
 #------------------------------------------------------------------------------
