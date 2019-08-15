import sys
import sqlite3

def printResult(cur):
  print(list(map(lambda x: x[0], cur.description)))
  for row in cur:
    print(row)

def main():
    args = sys.argv
    if len(args) != 2:
        print( 'ERROR: invalid num input args: {}.\nUsage:\n{} db_instance'.format( len(args), args[0] ) )
        return
    db_instance = args[1]
    conn = sqlite3.connect(db_instance)
    cur = conn.cursor()
    q1 = '''SELECT t.name AS pokemonType, AVG(p.weight) AS averageWeight
      FROM pokemon p, typeInfo t, pokemonType pt 
      WHERE p.pokemonID = pt.pokemonID AND pt.typeID = t.typeID group by t.typeID'''
    cur.execute(q1)
    print(f'\nQuestion 1: What is the average weight of the pokemon by Pokemon type?')
    print(f'======================================================================')
    printResult(cur)
    
    q2 = '''SELECT t.name AS pokemonType, MAX(m.accuracy) AS maxAccuracy
      FROM pokemon p, moveInfo m, pokemonMove pm, typeInfo t, pokemonType pt
      WHERE p.pokemonID = pt.pokemonID AND pt.typeID = t.typeID
      AND p.pokemonID = pm.pokemonID AND pm.moveID = m.moveID
      GROUP BY t.typeID'''
    cur.execute(q2)
    print(f'\nQuestion 2: List the highest accuracy move by Pokemon type')
    print(f'==========================================================')
    printResult(cur)

    q3 = '''SELECT p.name, count(*) as count
      FROM pokemonMove pm, pokemon p
      WHERE pm.pokemonID = p.pokemonID
      GROUP BY pm.pokemonID
      ORDER BY count DESC'''
    cur.execute(q3)
    print(f'\nQuestion 3: Count the number of moves by Pokemon and order from greatest to least')
    print(f'=================================================================================')
    printResult(cur)

if "__main__":
    main()