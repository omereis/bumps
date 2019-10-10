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
    CommunicationTest = 10;
    get_tags_jobs = 11;
    get_tag_count = 12;
    del_by_tag = 13;
    load_by_tag = 14;
    job_data_by_id = 15;
    get_all_tag_count = 16;
 #------------------------------------------------------------------------------
