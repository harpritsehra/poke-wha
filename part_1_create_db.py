import sqlite3
import sys

def main():
  args = sys.argv
  if len(args) != 3:
    print( 'ERROR: invalid num input args: {}.\nExpected:\n{} db_instance sql_script'.format( len(args), args[0] ) )
    return
  db_instance = args[1]
  sql_script = args[2]
  if not sql_script.endswith('.sql'):
      print( 'ERROR: sql_script must be a .sql file' )
      return
  conn = sqlite3.connect(db_instance)

  with open( sql_script, 'r' ) as sqlScript:
    conn.executescript( sqlScript.read() )

  print( 'Created db instance: {} using script: {}.'.format( db_instance, sql_script ) )

if __name__ == '__main__':
  main()
