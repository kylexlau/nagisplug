# -*- coding: utf-8 -*-
import os
import re
import sys
import getopt

__version__ = '0.2'
__author__ = 'liuxk@szlanyou.com (Liu Xukai)'

# Changelog:
# 0.1 - basic function
# 0.2 - add performance data support

def main():
    try:
        options, args = getopt.getopt(sys.argv[1:],
                                      "hvm:n:q:w:c:",
                                      "--help --version --mode= --queuename= --queuemanager= --warning= --critical=",
                                      )
    except getopt.GetoptError:
        print( sys.argv[0] + ": Wrong arguments")
        usage()

    if options == []:
        print (sys.argv[0] + ": Could not parse arguments")
        usage()

    # defaults arguments
    mode = "queue"
    argw = 30
    argc = 100

    for name, value in options:
        if name in ("-h", "--help"):
            usage()
        if name in ("-v", "--version"):
            version()
        if name in ("-m", "--mode"):
            if value not in ("queue"):
                usage()
            mode = value
        if name in ("-n", "--queuename"):
            qn = value
        if name in ("-q", "--queuemanager"):
            qm = value
        if name in ("-w", "--warning"):
            try:
                argw = int(value)
            except Exception:
                usage()
        if name in ("-c", "--critical"):
            try:
                argc = int(value)
            except Exception:
                usage()

    if mode == "queue":
        qd = queuedepth(qn,qm)
        qd_s = str(qd)

        if qd >= argc:
            print("Critical, queue manager: %s queue: %s depth: %s|depth=%s;%s;%s;0;50000" % (qm,qn,qd_s,qd_s,argw,argc), end='')
            sys.exit(1)
        elif qd >= argw:
            print("Warning, queue manager: %s queue: %s depth: %s|depth=%s;%s;%s;0;50000" % (qm,qn,qd_s,qd_s,argw,argc), end='')
            sys.exit(2)
        else:
            print("OK, queue manager: %s queue: %s depth: %s|depth=%s;%s;%s;0;50000" % (qm,qn,qd_s,qd_s,argw,argc), end='')
            sys.exit(0)

def version():
    print ( sys.argv[0] + " version " + __version__ + " by " + __author__)
    sys.exit(0)

def usage():
    print ("""
Usage:
  %s [-t <timeout>] [-m|--mode=] [-n|--qeueuname=] [-q|--qm][-w|--warning level] [-c|--critical level]"
  %s [-h | --help]
  %s [-v | --version]

Modes:
- queue, check mq queue depth.

Defaults:
-w 30
-c 100""" % (sys.argv[0],sys.argv[0],sys.argv[0]))
    sys.exit(3)

def queuedepth(queue,qm):
    '''
    input: string, string
         - the queue name.
         - the queue manager name.
    output: int
         - the current queue depth of the input queue manager's queue.
    '''
    cmd = 'echo dis qs(%s) | runmqsc %s' % (queue,qm)
    output = os.popen(cmd).read()
    return int(re.search('CURDEPTH\((\d+)\)',output).group(1))

if __name__ == "__main__":
    main()
