import sqlite3
import requests
import sys

class PokemonInfo:
  """
  simple class to represent pokemon info
  """
  def __init__(self, id, name, weight, type_url_list, move_url_list):
    self.id = id
    self.name = name
    self.weight = weight
    self.type_url_list = type_url_list
    self.move_url_list = move_url_list

  def __str__(self):
     return f'{self.id}, {self.name}, {self.weight}, types: {len(self.type_url_list)}, moves: {len(self.move_url_list)}'

class TypeInfo:
  """
  simple class to represent type info
  """
  def __init__(self, id, name):
    self.id = id
    self.name = name

  def __str__(self):
    return f'{self.id}, {self.name}'

class MoveInfo:
  """
  simple class to represent move info
  """
  def __init__(self, id, name, accuracy):
    self.id = id
    self.name = name
    self.accuracy = accuracy
    self.cur = None

  def __str__(self):
    return f'{self.id}, {self.name}, {self.accuracy}'

class DbHelper:
  """
  Class to handle db interaction
  """
  def __init__(self, db_instance):
    self.conn = sqlite3.connect(db_instance)
  
  def check_autocommit(self):
    autocommit = False
    if self.cur == None:
      self.create_session()
      autocommit = True
    return autocommit

  def store_pokemon_info(self, pokemon_info):
    autocommit = self.check_autocommit()
    # Always force delete in this implementation, we can do something smarter later
    del_query = "DELETE FROM pokemon WHERE pokemonID = ?"
    ins_query = "INSERT INTO pokemon(pokemonID, name, weight) VALUES(?, ?, ?)"
    self.cur.execute(del_query, (pokemon_info.id,))
    self.cur.execute(ins_query, (pokemon_info.id, pokemon_info.name, pokemon_info.weight))
    if autocommit:
      self.commit_session()

  def store_type_info(self, type_info):
    autocommit = self.check_autocommit()
    # Always force delete in this implementation, we can do something smarter later
    del_query = "DELETE FROM typeInfo WHERE typeID = ?"
    ins_query = "INSERT INTO typeInfo(typeID, name) VALUES(?, ?)"
    self.cur.execute(del_query, (type_info.id,))
    self.cur.execute(ins_query, (type_info.id, type_info.name))
    if autocommit:
      self.commit_session()
  
  def store_pokemon_type(self, pokemonID, typeID):
    autocommit = self.check_autocommit()
    # Always force delete in this implementation, we can do something smarter later
    del_query = "DELETE FROM pokemonType WHERE pokemonID = ? AND typeID = ?"
    ins_query = "INSERT INTO pokemonType(pokemonID, typeID) VALUES(?, ?)"
    self.cur.execute(del_query, (pokemonID, typeID))
    self.cur.execute(ins_query, (pokemonID, typeID))
    if autocommit:
      self.commit_session()

  def store_move_info(self, move_info):
    autocommit = self.check_autocommit()
    # Always force delete in this implementation, we can do something smarter later
    del_query = "DELETE FROM moveInfo WHERE moveID = ?"
    ins_query = "INSERT INTO moveInfo(moveID, name, accuracy) VALUES(?, ?, ?)"
    self.cur.execute(del_query, (move_info.id,))
    self.cur.execute(ins_query, (move_info.id, move_info.name, move_info.accuracy))
    if autocommit:
      self.commit_session()
  
  def store_pokemon_move(self, pokemonID, moveID):
    autocommit = self.check_autocommit()
    # Always force delete in this implementation, we can do something smarter later
    del_query = "DELETE FROM pokemonmove WHERE pokemonID = ? AND moveID = ?"
    ins_query = "INSERT INTO pokemonmove(pokemonID, moveID) VALUES(?, ?)"
    self.cur.execute(del_query, (pokemonID, moveID))
    self.cur.execute(ins_query, (pokemonID, moveID))
    if autocommit:
      self.commit_session()

  def create_session(self):
    self.cur = self.conn.cursor()

  def commit_session(self):
    self.conn.commit()
    self.cur = None

class ApiHelper:
  """
  Class to handle api interaction
  """
  BASE_URL = "https://pokeapi.co/api/v2"
  POKEMON = "{}/pokemon/{}"

  def get_pokemon_info(self, id):
    """
    Call pokemon API, construct and return PokemonInfo object
    """
    response = requests.get(self.POKEMON.format(self.BASE_URL, id))
    if response.status_code == 200:
      j = response.json()
      type_url_list = list( map(lambda x: self.extract_url(x, "type"), j.get("types")))
      move_url_list = list( map(lambda x: self.extract_url(x, "move"), j.get("moves")))
      pokemon_info = PokemonInfo(id, j.get("name"), j.get("weight"), type_url_list, move_url_list)
      return pokemon_info
    else:
      return None

  def get_type_info(self, url):
    """
    Call type API, construct and return TypeInfo object
    """
    response = requests.get(url)
    if response.status_code == 200:
      j = response.json()
      type_info = TypeInfo(j.get("id"), j.get("name"))
      return type_info
    else:
      return None

  def get_move_info(self, url):
    """
    Call move API, construct and return MoveInfo object
    """
    response = requests.get(url)
    if response.status_code == 200:
      j = response.json()
      move_info = MoveInfo(j.get("id"), j.get("name"), j.get("accuracy"))
      return move_info
    else:
      return None

  def extract_url(self, json, key):
    """
    Expects json to contain key and then extracts url
    """
    entry = json.get(key)
    if entry:
        return entry.get("url")
    else:
        return None

def main():
    args = sys.argv
    if len(args) != 2:
        print( 'ERROR: invalid num input args: {}.\nUsage:\n{} db_instance'.format( len(args), args[0] ) )
        return
    db_instance = args[1]
    db_helper = DbHelper(db_instance)
    api_helper = ApiHelper()

    # Optimization: cache type and move urls that have already been called in this session to reduce api calls
    url_cache = {}
    
    for i in range(1, 16):
      pokemon_info = api_helper.get_pokemon_info(i)
      print(str(pokemon_info))
      db_helper.create_session()
      db_helper.store_pokemon_info(pokemon_info)
      # Store type info
      for url in pokemon_info.type_url_list:
        if url not in url_cache:
          type_info = api_helper.get_type_info(url)
          print(str(type_info))
          db_helper.store_type_info(type_info)
          url_cache[url] = type_info.id
        # Add reference info
        db_helper.store_pokemon_type(i, url_cache[url])
      # Store move info
      for url in pokemon_info.move_url_list:
        if url not in url_cache:
          move_info = api_helper.get_move_info(url)
          print(str(move_info))
          db_helper.store_move_info(move_info)
          url_cache[url] = move_info.id
        # Add reference info
        db_helper.store_pokemon_move(i, url_cache[url])

      # Commit after all info for one pokemon has been written
      db_helper.commit_session()

if "__main__":
    main()