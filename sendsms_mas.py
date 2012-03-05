#!/usr/bin/env python
# encoding: gbk
import MySQLdb
import sys
import getopt

__version__ = '0.1'
__author__ = 'kylexlau@gmail.com'

## db api name is nagios
## api config
db_host = '%host'
db_user = '%user'
db_passwd = '%pass'
db_name = 'mas'

def api_send_sms(mobile,content=''):
  sql = """insert into api_mt_nagios
(mobiles,content,send_time)
values
('%s','%s',null)""" % (mobile,content)

  try:
    conn=MySQLdb.connect(db_host,db_user,db_passwd,db_name)
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    conn.close()
  except Exception, e:
    print "Can't connect to DB!, %s" % (e)

def version():
  print sys.argv[0] + " version " + __version__ + " by " + __author__
  sys.exit(0)

def usage():
  s = sys.argv[0]
  print """
Usage:
  %s -m mobile -c content
  %s [-h | --help]
  %s [-v | --version]
  """ % (s,s,s)
  sys.exit(0)

def main():
  try:
    options, args = getopt.getopt(sys.argv[1:],
        "hvm:c:",
        "--help --version --mobile= --content=",
        )
  except getopt.GetoptError:
    print sys.argv[0] + ": Wrong arguments"
    usage()

  if options == []:
    print sys.argv[0] + ": Could not parse arguments"
    usage()

  for k,v in options:
    if k in ("-h","--help"):
      usage()
    if k in ("-v","--version"):
      version()
    if k in ("-m","--mobile"):
      mobile = v.decode('utf-8').encode('gbk')
    if k in ("-c","--content"):
      content = v.decode('utf-8').encode('gbk')

  api_send_sms(mobile,content)

if __name__ == "__main__":
  main()
