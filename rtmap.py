import psycopg2
import folium
import time
import configparser

# Ustawienie domyślnej ścieżki do pliku konfiguracyjnego
config_file_path = '/etc/lms/lms.ini'

# Tworzenie obiektu ConfigParser
config = configparser.ConfigParser()

# Wczytanie pliku konfiguracyjnego
config.read(config_file_path)

# Pobieranie wartości z sekcji [database]
host = config['database']['host']
user = config['database']['user']
password = config['database']['password']
database = config['database']['database']

# Wypisanie wartości na ekran
print(f"host: {host}")
print(f"user: {user}")
print(f"password: {password}")
print(f"database: {database}")



# Config section
db_host = "localhost"
db_name = "lms"
db_user = "lms"
db_password = None
queueid_list = [1000001, 2000026, 2000030, 2000042, 2000035, 2000031, 2000033]
count=0
countOld=0
iteracja=0

# DB connect
conn = psycopg2.connect(host=db_host, dbname=db_name, user=db_user, password=db_password)

# Creating map
map = folium.Map(location=[51.268056994984995, 18.37092884412042], zoom_start=11)

while True:

    # Zapytanie SQL sprawdzające ilość rekordów o statusie 2
    queueid_str = ', '.join(str(i) for i in queueid_list)
    firstQuery = f"""
        SELECT count(id) FROM rttickets WHERE state <> 2 AND queueid IN ({queueid_str})
    """
    with conn.cursor() as cur:
        cur.execute(firstQuery)
        firstRows = cur.fetchall()

    for firstRow in firstRows:
        count = str(firstRow[0])
        countOld = str(countOld)
        iteracja = iteracja+1
        if iteracja > 50:
            count = str(-1)
            iteracja = 0
        print ("Liczba nowych zgłoszeń: "+count+", liczba zgłoszeń z poprzedniej iteracji: "+countOld)
        if count != countOld:
            # Zapytanie SQL do wybrania współrzędnych geograficznych
            query = """
                SELECT n.latitude, n.longitude, t.subject, t.queueid, t.id
                FROM nodes n
                INNER JOIN rttickets t ON n.ownerid = t.customerid
                WHERE t.state <> 2 AND t.queueid IN (1000001, 2000026, 2000030, 2000042, 2000035, 2000031, 2000033)
                AND n.latitude IS NOT NULL AND n.longitude IS NOT NULL
            """

            # Wykonanie zapytania i pobranie wyników
            with conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()

            # Dodawanie punktów o pobranych współrzędnych do mapy
            for row in rows:
                if row[3] == 2000026:
                    color = 'red'
                else:
                    color = 'blue'

                # Tworzymy klikalny link z napisem "Zgłoszenie"
                link = f'<b><a href="https://lmsmm.w2s.net.pl/?m=rtticketview&id={row[4]}">Idź do zgłoszenia</a></b>'
                popup_text = f"{link}<br>{row[2]}"  # dodaj klikalny link i nową linię
                folium.Marker([row[0], row[1]], popup=popup_text, icon=folium.Icon(color=color)).add_to(map)



            # Generuję mapę
            print("Zmiana liczby zgłoszeń, robię nową mapę")
            map.save("/var/www/html/lms/map.html")
        countOld = count

    time.sleep(5)

        # Zamykanie połączenia z bazą danych
conn.close()
