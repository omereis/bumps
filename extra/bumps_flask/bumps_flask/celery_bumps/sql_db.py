import mysql
from mysql.connector import MySQLConnection, Error
import os
import time
import datetime
from .oe_debug import print_debug
#------------------------------------------------------------------------------
TABLE_PARAMS      = "t_bumps_jobs"

FIELD_TOKEN       = 'token'
FIELD_JOB_ID      = 'job_id'
FIELD_TIME_START  = 'time_started'
FIELD_PARAMS      = 'params'
FIELD_CONTENT     = 'in_file_content'
FIELD_TIME_ENDED  = 'time_ended'
FIELD_RES_DIR     = 'result_dir'
FIELD_RES_CONTENT = 'result_zip'
#------------------------------------------------------------------------------
class bumps_sql(object):
    init_done = False
    host     = 'ncnr-r9nano'#p858547'
    database = 'bumps_db'
    user     = 'bumps'
    password = 'bumps_dba'
    conn     = None#mysql.connector.connect(host='p858547', database='bumps_db', user='bumps',password='bumps_dba')
    cursor   = None#conn.cursor()
#------------------------------------------------------------------------------
    def __del__ (self):
        try:
            if (hasattr (self, 'cursor')):
                if (self.cursor):
                    self.cursor.close()
            if (hasattr (self, 'conn')):
                if (self.conn):
                    self.conn.close()
        except Exception as e:
            print_debug(str(e))
#------------------------------------------------------------------------------
    def insert_key(self, token, job_id):
        records_count = 0
        try:
            strSql = "select count(*) as count from %s where (%s='%s' and %s='%s');" % (TABLE_PARAMS, FIELD_TOKEN, \
                        token, FIELD_JOB_ID, job_id)
            self.cursor.execute(strSql)
            result = self.cursor.fetchone()[0]
            if (result > 0):
                return(self.insert_key(token, job_id + 1))
        except Exception as e:
            print_debug ("insert_key NOT connected" + str(e))
            job_id = -1
        return (job_id)
#------------------------------------------------------------------------------
    def insert_new_key(self, token, job_id, job_params):
        try:
            self.connect_to_db()
            job_id = self.insert_key(token, job_id)
            if (job_id > 0):
                in_file = read_file(job_params.split()[1])
                ts = get_current_time_string()
                strSql = "insert into %s ( %s, %s, %s,  %s, %s) values \
                                         ('%s',%s,'%s','%s','%s');" % (TABLE_PARAMS, \
                        FIELD_TOKEN, FIELD_JOB_ID, FIELD_TIME_START, FIELD_PARAMS, FIELD_CONTENT, \
                        token, job_id, ts, job_params, in_file)
                self.cursor.execute(strSql)
                self.conn.commit()
                self.cursor.close()
            fInsert = True
        except Exception as e:
            print_debug ("insert_new_key NOT connected" + str(e))
            fInsert = False
        return (fInsert)
    #------------------------------------------------------------------------------
    def connect_to_db(self):
        fConnect = None
        try:
            self.conn = mysql.connector.connect(host = self.host, database = self.database, user = self.user, password = self.password)
#            self.conn = mysql.connector.connect(host='ncnr-r9nano', database='bumps_db', user='bumps',password='bumps_dba')
#            self.conn = mysql.connector.connect(host='p858547', database='bumps_db', user='bumps',password='bumps_dba')
            self.cursor = self.conn.cursor()
            fConnect = True
        except Exception as e:
            print_debug("sql_db.py, connect, exception :" + str(e))
            fConnect = False
        return (fConnect)
    #------------------------------------------------------------------------------
    def find_key(self, token, job_id):
        self.connect_to_db()
        print_debug("token: " + str(token) + "\njob_id: " + str(job_id))
#------------------------------------------------------------------------------
    def extract_file_and_path(self, job_id, token):
        try:
            strSql = "select %s,%s from %s where (%s='%s' and %s=%s);" % \
                    (FIELD_PARAMS, FIELD_CONTENT, \
                    TABLE_PARAMS, \
                    FIELD_TOKEN, token, \
                    FIELD_JOB_ID, str(job_id))
            self.cursor.execute(strSql)
            results = self.cursor.fetchone()
            file_path = results[0].split()[1]
            file_data = results[1]
        except Exception as e:
            print_debug("sql_db.py, extract_file_and_path\nException: " + str(e))
            file_path = file_data = None
        return file_path, file_data
#------------------------------------------------------------------------------
    def save_results (self, job_id, token, str_end_time, zip_name):
        f_results_saved = False
        try :
            zip_data = read_file (zip_name)
            if (not self.conn.is_connected()):
                self.connect_to_db()
            strWhere =  " where (%s='%s' and %s=%s);" % (FIELD_TOKEN, str(token), FIELD_JOB_ID, str(job_id))
            self.cursor.execute("update %s set %s='%s' %s" %  (TABLE_PARAMS, FIELD_TIME_ENDED, str_end_time, strWhere))
            self.conn.commit()

            query= "update %s set %s=%%s %s;" %  (TABLE_PARAMS, FIELD_RES_CONTENT, strWhere)
            self.cursor.execute(query, (zip_data, ))
            self.conn.commit()
            print_debug("sql_db.py, save_results\nResults Saved!")
            f_results_saved = True
        except Error as e:
            print_debug("sql_db.py, save_results\nMySQL Error: " + str(e))
        except Exception as e:
            print_debug("sql_db.py, save_results\nException: " + str(e))
        finally:
            self.cursor.close()
            self.conn.close()
        return (f_results_saved)
#------------------------------------------------------------------------------
    def get_completed_results(self, user_token):
        try :
            if (not self.conn.is_connected()):
                self.connect_to_db()
            strSql = "select %s,%s,%s from %s where (%s='%s') and (%s is not null);" % (FIELD_PARAMS, FIELD_RES_CONTENT, FIELD_JOB_ID, \
                                                            TABLE_PARAMS, FIELD_TOKEN, str(user_token), \
                                                            FIELD_TIME_ENDED)
            self.cursor.execute(strSql)
            results_recoreds = self.cursor.fetchall()
        except Exception as e:
            print_debug("sql_db.py, save_results\nException: " + str(e))
            results_recoreds = None
        finally:
            self.cursor.close()
            self.conn.close()
        return (results_recoreds)
#------------------------------------------------------------------------------
    def delete_job(self, user_id, job_id):
        try:
#            if (not self.conn.is_connected()):
#                self.connect_to_db()
            self.connect_to_db()
            strSql = "delete from {} where ({}='{}') and ({}={});".format(TABLE_PARAMS,
                                                                    FIELD_TOKEN, user_id,
                                                                    FIELD_JOB_ID, job_id)
            self.cursor.execute(strSql)
            self.conn.commit()
        except Exception as e:
            print_debug("sql_db.py, delete_job\nException: " + str(e))
            results_recoreds = None
        finally:
            self.cursor.close()
            self.conn.close()
#---------------- class and ---------------------------------------------------
#------------------------------------------------------------------------------
def read_file(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    return data
#------------------------------------------------------------------------------
def update_blob(id, filename):
    # prepare update query and data
    query = "UPDATE tblBumpsInParams SET in_file_blob = '%s' WHERE id  = %d;"
    try:
        data = read_file(filename)
        sql = "INSERT INTO tblBumpsInParams (in_file_blob) VALUES ('%s');"
        q = (sql, (data,))
        conn = ConnectBumpsDB()
        cursor = conn.cursor()
        cursor.execute(q)
        conn.commit()
    except Error as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
#------------------------------------------------------------------------------
def get_current_time_string():
    strTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return (strTime)
#------------------------------------------------------------------------------
def ConnectBumpsDB():
    conn = None
    try:
        conn = mysql.connector.connect(host='p858547', database='bumps_db', user='bumps',password='bumps_dba')
    except Error as e:
        print(e)
    return conn
#------------------------------------------------------------------------------
def NextID(conn,table,field):
    strSql = "select max(%s) from %s;" % (field, table)
#    strSql = "select * from tbl;"
    try:
        conn = ConnectBumpsDB()
        cursor = conn.cursor()
        cursor.execute(strSql)
        strDB = cursor.fetchall()
        id = strDB[0][0] + 1
    except Error as e:
        id = 1
        print(e)
    finally:
        cursor.close()
    return id
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#def update_blob(filename):
#------------------------------------------------------------------------------
def insert_file(filename):
    # read file
    data = read_file(filename)
    # prepare update query and data
    query = "insert into tblBumpsInParams(in_file_name) values ('%s');" % filename
    try:
        conn = mysql.connector.connect(host='p858547', database='bumps_db', user='bumps',password='bumps_dba')
        id = NextID(conn,'tblBumpsInParams','file_id')
        cursor = conn.cursor()
        query = "insert into tblBumpsInParams(in_file_name,file_id) values ('%s',%d);" % (filename, id)
        cursor.execute(query)
#        query = "update tblBumpsInParams set in_file_blob=%s where in_file_name=%s;" % (MySQLdb.escape_string(data), filename)
#        cursor.execute(query)
        conn.commit()
#        update_blob(id,filename)
    except Error as e:
        id = -1
        print(e)
    finally:
        cursor.close()
        conn.close()
    return id
#------------------------------------------------------------------------------
if __name__ == '__main__':
    try:
        strDir = os.getcwd()
        strFileName = 'D:\\Omer\\Source\\Tutorial\\MySQL\\hdf5_job_outline.png'
        id = insert_file(strFileName)
        if (id > 0):
            update_blob (id, strFileName)
    except Error as e:
        print(e)
