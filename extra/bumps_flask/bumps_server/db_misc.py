from bumps_constants import DB_Table, DB_Field_JobID, DB_Field_SentIP, DB_Field_SentTime, DB_Field_Tag, \
                            DB_Field_Message, DB_Field_ResultsDir,DB_Field_JobStatus, DB_Field_EndTime, \
                            DB_Field_ProblemFile
#------------------------------------------------------------------------------
def get_next_job_id(connection):
    job_id = 0
    try:
        sql = 'select max({}) from {};'.format(DB_Field_JobID, DB_Table)
        res = connection.execute(sql)
        for row in res:
            job_id = row.values()[0]
    except Exception as e:
        print("Error in get_next_job_id()")
        print("{}".format(e))
        job_id = None
    return job_id
#------------------------------------------------------------------------------
