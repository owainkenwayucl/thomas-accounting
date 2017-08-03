#!/usr/bin/env python3
''' 
    This is a fundamentally terrible piece of programming.
    If this is still in use in 2018 something has gone wrong.

    Anyway, this is a main script that calls out to other things that:
      1. Gets the amount of credit charged in Gold.
      2. Gets the number of CPU hours recorded in the thomas SGE logs DB
      3. Uses these to estimate ratio of paid to unpaid usage for a given month.

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
def getgoldusage(month):
  import subprocess
  endmonth = incrementmonth(month)
  gargs = ["./shell/get-gold-usage", goldmonth(month),  goldmonth(endmonth)]
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
def getmysqlusage(month):
  import simpletemplate as st

  monthstr = mysqlmonth(month)
  emonthstr = mysqlmonth(incrementmonth(month))
  
  # These are the keys in the file that will be replaced.
  keys = {'%DB%':'thomas_sgelogs', '%START%':monthstr, '%STOP%':emonthstr}
  query = st.templatefile(filename="sql/usage.sql", keys=keys)

  # The data is returned as a tuple inside a list for reasons.  Yank it out and
  # convert to hours from seconds.
  output = float(getmysqldata(query)[0][0])/3600.0
  return output
  
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

  gusage = getgoldusage(month)
  print("Paid usage (hours): %.2f" % gusage)
  musage = getmysqlusage(month)
  print("SGE usage (hours): %.2f" % musage)

  percentpaid=100.0*(gusage/musage)
  percentfree=100.0-percentpaid

  print("")
  print("%% Paid: %.2f" % percentpaid)
  print("%% Free: %.2f" % percentfree)  

'''
    *sigh*
'''
if __name__ == "__main__":
  main()


