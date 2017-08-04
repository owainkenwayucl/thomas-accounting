#!/usr/bin/env python3
''' 
    This is a fundamentally terrible piece of programming.
    If this is still in use in 2018 something has gone wrong.

    Anyway, this is a main script that calls out to other things that:
      0. Gets a list of users for each institute.
      1. Gets the amount of credit charged to that institute in Gold.
      2. Gets the number of CPU hours recorded in the thomas SGE logs DB for those users.
      3. Uses these to estimate ratio of paid to unpaid usage for a given month.

    THIS IS WRONG WHEN A USER IS AT MULTIPLE INSTITUTES.

    Dates are a list of ints [year, month] for reasons.
'''
'''
    Have a standardised way of incrementing months, unlike that *other*
    RCAS stats code.
'''
def incrementmonth(orig, inc=1):
  oy = orig[0]
  om = orig[1]

  nm = om + inc
  ny = oy
  if nm > 12:
    nm = nm - om
    ny = ny + 1

  return [ny, nm]

'''
    Build an SQL list out of a python list.
'''
def sqllist(pylist):
    sqlstr="("
    if type(pylist) == str:
        sqlstr = sqlstr + "'" + pylist + "')"
    else:
        for a in pylist:
            if sqlstr!= "(":
                sqlstr = sqlstr + ", "
            sqlstr = sqlstr + "'" + a + "'"
        sqlstr = sqlstr + ")"
    return sqlstr


'''  
    Build owner/node limit string for queries.
'''
def onlimits(users="*"):
    query = ""

    # if users != * then construct a node list.
    if users != "*":
        userlist = sqllist(users)
        query = query + " and owner in " + userlist

    return query



''' 
    Convert a [year, month] month into a string that can be passed to Gold.
''' 
def goldmonth(month):
  m = str(month[1])

  # Left pad 0 because gold returns either 1 or 0 if you don't.
  if len(m) == 1:
    m = "0" + m
  return str(month[0]) + "-" + m + "-01"

''' 
    Convert a [year, month] month into a string that can be passed to MySQL.
''' 
def mysqlmonth(month):
  return str(month[0]) + "-" + str(month[1]) + "-01 00:00:01"

'''
    Call out to an external shell script to get Gold usage.  This is because
    we don't really have a view of the Gold DB.
'''
def getgoldusage(month, institute):
  import subprocess

  endmonth = incrementmonth(month)
  gargs = ["./shell/get-gold-usage-inst", goldmonth(month),  goldmonth(endmonth), institute]
  usage = float(subprocess.check_output(gargs))
  return usage

''' 
    Generic routine to process a query.  I've stripped this out because it stops
    lots of "talking to MySQL guff" polluting the routines where we do anything.
'''
def getmysqldata(query):
  import os
  import mysql.connector

  output = ""

  try:

    # Note this is a different secrets file from the thomas tools Heather wrote,
    # partly to confuse people, partly because I want to keep this stuff separate.
    conn = mysql.connector.connect(option_files=os.path.expanduser('~/.stats.cnf'), database='thomas_sgelogs')
    cursor = conn.cursor() 

    cursor.execute(query)
    output = cursor.fetchall()


  except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
      print("Access denied: Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
      print("Database does not exist")
    else:
      print(err)
  else:
      cursor.close()
      conn.close() 
  return output

''' 
    This procedure uses my simpletemplate library to construct a query from a
    separate .sql file and then passes it to getmysqldata.
'''
def getmysqlusage(month, users='*'):
  import simpletemplate as st
  
  if users==[]:
    return 0.0
  monthstr = mysqlmonth(month)
  emonthstr = mysqlmonth(incrementmonth(month))
  
  # These are the keys in the file that will be replaced.
  keys = {'%DB%':'thomas_sgelogs', '%START%':monthstr, '%STOP%':emonthstr, '%ONLIMITS%':onlimits(users=users)}
  query = st.templatefile(filename="sql/usage-opts.sql", keys=keys)

  # The data is returned as a tuple inside a list for reasons.  Yank it out and
  # convert to hours from seconds.
  output = float(getmysqldata(query)[0][0])/3600.0
  return output

'''
    Get a list of users for a given institute.
'''
def getusers(institute):
  import simpletemplate as st

  keys = {'%INSTITUTE%':institute}
  query = st.templatefile(filename="sql/ist-to-users.sql", keys=keys)
  output = getmysqldata(query)
  retval = []
  for a in output:
    retval.append(a[0])

  # UNIQUE!
  retval = list(set(retval))
  return retval

'''
    Get a list of institutions from Heather's DB.
'''
def getinstitutes():
  query = "select inst_id from thomas.institutes"
  output = getmysqldata(query)
  retval = []
  for a in output:
    retval.append(a[0])
  return retval

'''
    Print a nice report.
'''
def printreport(data):
  for i in data:
    for j in i:
      print(j, end=", ")
    print("")

'''
    Our "not actually a main procedure because this is python". 
    Syntax is very simple - single argument each for year, month.
'''
def main():
  import sys

  if len(sys.argv) <=2:
    print("Syntax ", sys.argv[0], "<year> <month>")
    exit(1)

  month = [int(sys.argv[1]), int(sys.argv[2])]

  # Get a list of institutes.
  institutes = getinstitutes()

  dataset = []
  dataset.append(["Institution", "SoGE usage", "Gold charging", "%% paid", "%% free"])
  for a in institutes:
    item = []
    item.append(a)
    users = getusers(a)
    usage = getmysqlusage(month, users)
    gusage = getgoldusage(month, a)
    item.append(usage)
    item.append(gusage)


    if (usage <=0 ):
      percentpaid=0.0
    else:
      percentpaid=100.0*(gusage/usage)
    percentfree=100.0-percentpaid
    item.append(percentpaid)
    item.append(percentfree)
    dataset.append(item)

  printreport(dataset)

'''
    *sigh*
'''
if __name__ == "__main__":
  main()


