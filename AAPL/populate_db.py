import sqlite3
import alpaca_trade_api as tradeapi
connection = sqlite3.connect("app.db")

cursor = connection.cursor()

# cursor.execute(" INSERT INTO stock (symbol, company) VALUES ('ADBE', 'Adobe Inc.')")
# cursor.execute(" INSERT INTO stock (symbol, company) VALUES ('VZ', 'Verzion')")
# cursor.execute(" INSERT INTO stock (symbol, company) VALUES ('Z', 'Zillow')")

# cursor.execute("DELETE FROM stock")

connection.commit()