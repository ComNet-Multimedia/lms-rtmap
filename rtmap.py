import psycopg2
import folium
import time
import configparser

# Config section

# lms.ini file
config_file_path = '/etc/lms/lms.ini'
# queues to show on map
queueid_list = [1000001, 2000026, 2000030, 2000042, 2000035, 2000031, 2000033]
# where to save map file
map_file_path = '/var/www/html/lms/map.html'
# LMS URL
lms_url = 'https://lms.firma.pl/'


config = configparser.ConfigParser()
config.read(config_file_path)
db_host = config['database']['host']
db_user = config['database']['user']
db_password = config['database']['password']
db_name = config['database']['database']
queueid_list = [1000001, 2000026, 2000030, 2000042, 2000035, 2000031, 2000033]
count=0
countOld=0
iteracja=0

if db_host == "''":
    db_host = "localhost"

# DB connect
conn = psycopg2.connect(host=db_host, dbname=db_name, user=db_user, password=db_password)



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
            # Creating map
            map = folium.Map(location=[51.268056994984995, 18.37092884412042], zoom_start=11)
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
                link = f'<b><a href="{lms_url}?m=rtticketview&id={row[4]}">Idź do zgłoszenia</a></b>'
                popup_text = f"{link}<br>{row[2]}"  # dodaj klikalny link i nową linię
                folium.Marker([row[0], row[1]], popup=popup_text, icon=folium.Icon(color=color)).add_to(map)



            # Generuję mapę
            print("Zmiana liczby zgłoszeń, robię nową mapę")
            map.save(map_file_path)
        countOld = count

    time.sleep(5)

        # Zamykanie połączenia z bazą danych
conn.close()
