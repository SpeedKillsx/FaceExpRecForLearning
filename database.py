import sqlite3 as sql

database_dir = "basdedonnees\database.db"
conn=sql.connect(database_dir)
# Creation d'un curseur
cursor = conn.cursor()

# insertion d'un tuple

cursor.execute("Insert into compte values ('amayas','amayas','etudiant')")
print("Requet done")
conn.commit()
conn.close()

 
