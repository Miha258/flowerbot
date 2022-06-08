import sqlite3

conection = sqlite3.connect('server.db')
cursor = conection.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS serverss_db (
      name TEXT,
      id INT,
      cash BIGINT,
      timess INT,
      when_climed INT,
      names TEXT,
      private_room INT
      )""")
  conection.commit()
  cursor.execute("""CREATE TABLE IF NOT EXISTS log (
      id INT,
      timess TEXT,
      resaon TEXT
  )""")
  conection.commit()
  cursor.execute("""CREATE TABLE IF NOT EXISTS adminnsnff (
      id INT,                                      
      reports INT,
      mutes INT,
      warns INT,
      weekly_mutes INT,
      weekly_reports INT,
      weekly_warns INT,
      rating_pos INT,
      rating_neg INT,
      weekly_clear INT 
      )""")
  conection.commit()
  cursor.execute("""CREATE TABLE IF NOT EXISTS warninform (
      name TEXT,
      id INT,
      warns INT,
      type TEXT,
      reason TEXT,
      timess TEXT,
      admin INT
      )""") 
  conection.commit()
  
  cursor.execute("""CREATE TABLE IF NOT EXISTS shops (
      guild_id INT,
      role_name TEXT,
      role_id INT,
      cost BIGINT
      
  )""")
  conection.commit()
 
  cursor.execute("""CREATE TABLE IF NOT EXISTS exp_system  (
      xp BIGINT,
      lvl INT,
      when_xp INT,
      id INT
      
  )""")
  conection.commit()
  
  cursor.execute("""CREATE TABLE IF NOT EXISTS clans  (
      clan_name BIGINT,
      clan_owner TEXT,
      clan_id INT,
      clan_members INT,
      in_clan BOOLEAN,
      have_clan BOOLEAN,
      when_created TEXT,
      users INT,
      clan_channel_id INT,
      clan_text_channel_id INT,
      clan_role_id INT,
      clan_slots INT,
      time_for_pay INT,
      str_time_for_pay TEXT,
      clan_img_url TEXT,
      clan_avatar_url TEXT,
      clan_description TEXT,
      has_invited BOOLEAN,
      channels INT,
      clan_points INT,
      has_payed BOOLEAN,
      clan_cash BIGINT,
      lvl INT,
      balance INT,
      voice_time INT
      
  )""")
