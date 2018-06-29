import mysql
from mysql.connector import MySQLConnection, Error
import os
#import MySQLdb
#from python_mysql_dbconfig import 
#------------------------------------------------------------------------------
from .misc import print_debug
TABLE_PARAMS = "t_bumps_jobs"
FIELD_TOKEN = 'token'
FIELD_JOB_ID = 'job_id'
FIELD_PARAMS = 'params'
FIELD_CONTENT = 'in_file_content'
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
            for count in self.cursor:
                records_count = int (count[0])
#            fInsert = True
        except Exception as e:
            print_debug ("insert_new_key NOT connected" + str(e))
            records_count = 0
        return (records_count)
#------------------------------------------------------------------------------
    def insert_new_key(self, token, job_id, job_params):
        try:
            self.connect_to_db()
            records_count = self.insert_key(token, job_id)
            if (records_count == 0):
                strSql = "insert into %s (%s,%s,%s) values ('%s',%s,'%s');" % (TABLE_PARAMS, \
                        FIELD_TOKEN, FIELD_JOB_ID, FIELD_PARAMS, \
                        token, job_id, job_params)
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
def read_file(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    return data
#------------------------------------------------------------------------------
def update_blob(id, filename):
    # prepare update query and data
    query = "UPDATE tblBumpsInParams SET in_file_blob = '%s' WHERE id  = %d;"
 
#    db_config = read_db_config()
 
    try:
        data = read_file(filename)
        sql = "INSERT INTO tblBumpsInParams (in_file_blob) VALUES ('%s');"
        q = (sql, (data,))
        conn = ConnectBumpsDB()
        cursor = conn.cursor()
        # read file
#        args = (data, id)
#        conn = MySQLConnection(**db_config)
#        cursor = conn.cursor()
        cursor.execute(q)
#        cursor.execute(query, args)
        conn.commit()
    except Error as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
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
