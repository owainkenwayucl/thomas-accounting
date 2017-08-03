#!/usr/bin/env python3
import sys
import mysql.connector

def incrementmonth(orig, inc=1):
  oy = orig[0]
  om = orig[1]

  nm = om + inc
  ny = oy
  if nm > 12:
    nm = nm - om
    ny = ny + 1

  return [ny, nm]

def goldmonth(month):
  m = str(month[1])
  if len(m) == 1:
    m = "0" + m
  return str(month[0]) + "-" + m + "-01"

def mysqlmonth(month):
  return str(month[0]) + "-" + str(month[1]) + "-01 00:00:01"

def getgoldusage(month):
  import subprocess
  endmonth = incrementmonth(month)
  gargs = ["./shell/get-gold-usage", goldmonth(month),  goldmonth(endmonth)]
  usage = float(subprocess.check_output(gargs))
  return usage

def getmysqldata(query):
  import os
  output = ""
  try:
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

def getmysqlusage(month):
  import simpletemplate as st

  monthstr = mysqlmonth(month)
  emonthstr = mysqlmonth(incrementmonth(month))
  
  keys = {'%DB%':'thomas_sgelogs', '%START%':monthstr, '%STOP%':emonthstr}
  query = st.templatefile(filename="sql/usage.sql", keys=keys)

  output = float(getmysqldata(query)[0][0])/3600.0
  return output
  
  

# Syntax is very simple - single argument for year, month.
if __name__ == "__main__":
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


