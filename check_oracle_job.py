#!/usr/bin/python 
# FileName     : checkOracleUserJobs.py
# Description  : Nagios Plugin to check scheduled jobs on Oracle (through DBMS_JOB Package)
# Author       : Fabio GRANDE
# Date Created : 4 February 2012
#
# Changes
# xx/xx/xxxx - description
 
import sys
import os
import getopt
import cx_Oracle
import socket
 
_version="0.1"
 
_verbose=False
_jobNumber=0
_connStr=""
_timeout=10
_minutes=0
_user=""
_password=""
_sid=""
_connectionString=""
 
 
def AnalyzeJobs():
        socket.setdefaulttimeout(_timeout)
        try:
                conn = cx_Oracle.connect(_connectionString);
        except cx_Oracle.DatabaseError, err:
                print "DB Error : ", err
                sys.exit(3)
        except socket.timeout:
                print "Timeout !"
                sys.exit(3)
 
        _messages = ""
        _status = 0
        _checkedJobs = 0
        
        cursor = conn.cursor()
        _sql = "select job, what, failures, broken, trunc(((next_date - sysdate) * 24 * 60)) min2go from dba_jobs"
        if _jobNumber > 0:
                _sql += " where job = %d" % _jobNumber
        cursor.execute(_sql)
 
        for job, what, failures, broken, min2go in cursor.fetchall():
                _checkedJobs += 1
                if broken == "Y":
                        if _messages != "":
                                _messages += " "
                        _msg = "Broken Job #%s - %s" % (job, what)
                        log(_msg)
                        _messages += _msg
                        #_status = 3
                        _status = 2
                elif failures > 0:
                        if _messages != "":
                                _messages += " "
                        _msg = "Failing Job #%s(failed %s times) - %s" % (job, failures, what)
                        log(_msg)
                        _messages += _msg
                        if (_status < 2):
                                _status = 2
                elif min2go > _minutes and _minutes > 0:
                        if _messages != "":
                                _messages += " "
                        _msg = "Badly Scheduled Job #%s - %s" % (job, what)
                        log(_msg)
                        _messages += _msg
                        #_status = 3
                        _status = 2
                else:
                        log("Job %s (%s) is OK !" % (job, what))
                        
        conn.close()
        
        if _messages == "":
                _messages = "%d DB Scheduled Jobs are OK" % _checkedJobs
                
        return _status, _messages
 
 
def Version():
        print "%s %s" % (os.path.basename(__file__), _version)
 
 
def Usage():
        Version()
        print "Parameters :"
        print "             -h : Display this help screen"
        print "             -V : Show the version"
        print "             -v : Verbose"
        print "\n"
        print "             -c : Oracle Connection String (format user/password@sid)"
        print "\n"
        print "             -u : Oracle Schema"
        print "             -p : Password"
        print "             -s : SID"
        print "\n"
        print "             -j : Job Number"
        print "             -m : Max Minutes before next launch"
        print "             -t : Connection Timeout (Default is 10 seconds)"
        sys.exit(3)
 
 
def log(pString):
        if _verbose:
                print pString
 
def BuildParameters():  
        global _verbose, _jobNumber, _connStr, _timeout, _minutes, _user, _password, _sid
        try:
                opts, args = getopt.getopt(sys.argv[1:], "hc:u:p:s:j:vVm:t:", ["help"])
        except getopt.GetoptError, err:
                print "ERROR : ", err
                Usage()
        for opt, arg in opts:
                if opt in ("-h", "--help"):
                        Usage()
                elif opt in ("-V", "--version"):
                        Version()
                        sys.exit(3)
                elif opt in ("-v", "--verbose"):
                        _verbose = True
                elif opt == "-j":
                        _jobNumber = int(arg)
                elif opt == "-t":
                        if arg > 0:
                                _timeout = arg
                elif opt == "-c":
                        _connStr = arg
                elif opt == "-u":
                        _user = arg
                elif opt == "-p":
                        _password = arg
                elif opt == "-s":
                        _sid = arg
                elif opt == "-m":
                        _minutes = int(arg)
                #print "Opt : %s - Arg : %s" % (opt, arg)
        #for arg in args:
                #print "Argument : %s" % arg
 
 
def CheckParameters():
        if _connStr == "" and (_user == "" or _password == "" or _sid == ""):
                Usage()
 
 
def BuildConnectionString():
        global _connectionString
        
        _connectionString = _connStr;
        if _connectionString == "":
                _connectionString = "%s/%s@%s" % (_user, _password, _sid)
        log("Composed Connection String : %s" % _connectionString)
 
 
def main(argv):
        BuildParameters()
        CheckParameters()
        BuildConnectionString()
        _status, _messages = AnalyzeJobs()
        print _messages
        sys.exit(_status)
 
if __name__ == "__main__":
        main(sys.argv[1:])
