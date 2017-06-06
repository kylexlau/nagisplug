#!/usr/bin/python

# FileName     : check_oracle_my.py
# Description  : my Nagios Plugin to check Oracle database
# Author       : Liu Xukai
# Date Created : 2017-05-24

## ChangeLog:
#  2017-05-31: rewrite the codes with argparsea lib
#  2017-06-02: rewrite the codes using object-oriented programming
#              and change it to pep8 style.

## Todo:
# add more metrics by selecting v$sysmetrics

__version__ = '0.3'

import os
import re
import sys
import socket
import argparse

import cx_Oracle

class OracleMonitor(object):
    """Object for Oracle database monitroing."""
    ## sql
    dbstat_sql="""
    SELECT COALESCE((select to_char(dbtime)
                  from (SELECT ROUND(VALUE - LAG(VALUE, 1, '0')
                                     OVER(ORDER BY A.INSTANCE_NUMBER,
                                          A.SNAP_ID),
                                     2) DBTIME
                          FROM (SELECT B.SNAP_ID,
                                       INSTANCE_NUMBER,
                                       SUM(VALUE) / 1000000 / 60 VALUE
                                  FROM DBA_HIST_SYS_TIME_MODEL B
                                 WHERE B.DBID = (SELECT DBID FROM V$DATABASE)
                                   AND UPPER(B.STAT_NAME) IN
                                       UPPER(('DB TIME'))
                                 GROUP BY B.SNAP_ID, INSTANCE_NUMBER) A,
                               DBA_HIST_SNAPSHOT B
                         WHERE A.SNAP_ID = B.SNAP_ID
                           AND B.DBID = (SELECT DBID FROM V$DATABASE)
                           AND B.INSTANCE_NUMBER =
                               (select INSTANCE_NUMBER from v$instance)
                           AND B.INSTANCE_NUMBER = A.INSTANCE_NUMBER
                           and B.BEGIN_INTERVAL_TIME > sysdate - 4 / 24
                         order by B.BEGIN_INTERVAL_TIME desc)
                 where rownum = 1),
                '0')
      from dual
    union all
    select to_char(count(*))
      from v$session
     where type = 'USER'
       and status = 'ACTIVE'
   """

    dbconf_sql="""
    select value
      from v$parameter
     where name = 'cpu_count'
    union all
    select to_char(round(value/1024/1024/1024,2)) G
      from v$parameter
     where name = 'sga_target'
    union all
    select to_char(round(value/1024/1024/1024,2)) G
    from v$parameter where name = 'pga_aggregate_target'
    """

    asm_inb_sql="""
    select * from (
      select
        g.name Diskgroup,
        round(100 * (max((d.total_mb - d.free_mb) / d.total_mb) -
        min((d.total_mb - d.free_mb) / d.total_mb)) /
        max((d.total_mb - d.free_mb) / d.total_mb)) ImbalancePct,
        round(100 * (min(d.free_mb / d.total_mb))) MinFreePct
      from v$asm_disk d, v$asm_diskgroup g
      where d.group_number = g.group_number
      and d.group_number <> 0
      and d.state = 'NORMAL'
      and d.mount_status = 'CACHED'
      and g.name not like 'DBFS_DG%'
      group by g.name, g.type)
      where ImbalancePct >= 15 or MinFreePct <= 3
    """

    timeout = 10

    def __init__(self, db, user, passwd, timeout):
        """Take the db configuration info from command line options"""
        self.db = db
        self.user = user
        self.passwd = passwd
        if timeout is not None:
            self.timeout = timeout

    def dbstat(self):
        """DBtime and active_session performance data"""
        status = 0
        cnt_a = self.exe_sql(self.dbstat_sql)
        dbtime = cnt_a[0][0]
        active_session = cnt_a[1][0]
        msg = "check ok. | dbtime=%s;;;; active_session=%s;;;;" % \
                (dbtime,active_session)
        return status, msg

    def dbconf(self):
        """Some database configuration infomations as performance data"""
        status = 0
        cnt_a = self.exe_sql(self.dbconf_sql)
        cpu_count = cnt_a[0][0]
        sga = cnt_a[1][0]
        pga = cnt_a[2][0]
        mem = float(sga)+float(pga)
        msg = "check ok. | cpu_count=%s;;;; sga=%s;;;; pga=%s;;;; memory=%s;;;;" \
                % (cpu_count,sga,pga,str(int(round(mem))))
        return status, msg

    def asminb(self):
        """Check if ASM disks' data is balanced"""
        rst = self.exe_sql(self.asm_inb_sql)
        msg = ''
        for disk_group,imbalance_pct,min_free_pct in rst:
            s = "ASM DiskGroup %s's disks: Imblance percent is %s \
                 and minimum free percent is %s \n" % \
                 (disk_group,imbalance_pct,min_free_pct)
            msg += s
            status = 2

            if len(msg) > 600:
                break
        if msg == '':
            msg = "ASM disk imbanlace check ok."
            status = 0

        return status,msg

    def exe_sql(self, sql):
        """Execute sql statement in a db, return the sql result"""
        socket.setdefaulttimeout(self.timeout)
        conn_str= "%s/%s@%s" % (self.user,self.passwd,self.db)
        try:
            conn = cx_Oracle.connect(conn_str);
        except cx_Oracle.DatabaseError, err:
            print "DB Error : ", err
            sys.exit(3)
        except socket.timeout:
            print "Timeout !"
            sys.exit(3)
        cursor = conn.cursor()
        cursor.execute(sql)
        rst = cursor.fetchall()
        conn.close()
        return rst

def version():
    """Print version."""
    print "%s %s" % (os.path.basename(__file__), __version__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument('-v','--version', help='Show version number',
                        action='store_true')
    parser.add_argument('-s','--database',help='Database TNS Name')
    parser.add_argument('-u','--username',help='Monitoring Username')
    parser.add_argument('-p','--password',help='Monitoring Password')
    parser.add_argument('-t','--timeout',
                        help='Connection Timeout (Default is 10 seconds)',
                        default=10,type=int)
    parser.add_argument('-m','--mode',    help="""
           dbstat: Database statatics like active session and db time.
           dbconf: Database configuration information like parameter values and more.
           asminb: ASM inbalance check.""",
                        choices=['dbstats','dbconf','asminb'])
    args = parser.parse_args()

    if args.version:
        version()
        sys.exit(0)
    if not args.mode or not args.username \
       or not args.database or not args.password:
        parser.error('DB info and mode is required.')
    return args

def main():
    """The main program."""
    args = parse_args()
    dbm = OracleMonitor(args.database, args.username,
                        args.password, args.timeout)

    if args.mode=='dbstats':
        return dbm.dbstat()
    elif args.mode=='dbconf':
        return dbm.dbconf()
    elif args.mode=='asminb':
        return dbm.asminb()
    else:
        print('No arguments provided.')
        sys.exit(1)

if __name__ == "__main__":
    status, msg = main()
    print msg
    sys.exit(status)
