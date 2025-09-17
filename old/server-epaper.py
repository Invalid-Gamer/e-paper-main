# TODO: - schedule alle X Minuten Webuntis pruefen und ggf. Bildchen neumachen z.B. mit Schedule : import schedule
# TODO: - Zeit fuer Deepsleep berechnen und irgendwo speichern, der Server-Loop muss darauf zugreifen können wenn sich Displays melden
# TODO: - Speichern der INfos mit Pickle-DB?

from IMAGEGEN.imagegen2 import gen_image

import socket
import numpy as np
from PIL import Image
import struct  
import time
import logging

# Server-Einstellungen
HOST = '0.0.0.0'  # Lausche auf allen verfuegbaren Netzwerkschnittstellen
PORT = 8080       # Der Port, auf dem der Server auf Verbindungen wartet

def image_to_array(image_path):
    """Öffnet ein Graustufenbild und gibt die Pixelwerte als eindimensionales Array zurueck."""
    # Bild öffnen
    with Image.open(image_path) as img:
        # Bild in Graustufen konvertieren, falls es nicht schon in diesem Modus ist
        gray_image = img.convert('L')
        
        # Pixelwerte als numpy-Array extrahieren
        pixel_array = np.array(gray_image)

        # In ein eindimensionales Array konvertieren
        pixel_array_flattened = pixel_array.flatten()  # Alternativ: pixel_array.ravel()

    return pixel_array_flattened



def reduce_pixel_count(pixel_array):
    """_summary_

    Args:
        pixel_array (uint8): Graustufenwerte des Bildes: 0 = Schwarz, 255 = Weiß

    Returns:
        halbiertes Array: _description_
    """    
    # Neues Array erstellen, das die Haelfte der Pixelanzahl hat
    reduced_array = pixel_array[::2]  # Nur jeden zweiten Pixel nehmen
    return reduced_array

def start_server():
    """_summary_
    Startet den Server und wartet dann auf Anfragen von Clients.
    """    
    # Erstelle einen TCP/IP-Server-Socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()  # Warte auf eingehende Verbindungen
        print(f"Server agiert und wartet auf Verbindungen auf {HOST}:{PORT}...")
        logger.info(f"Server agiert und wartet auf Verbindungen auf {HOST}:{PORT}...")

        # Endlosschleife, um mehrere Verbindungen zu ermöglichen
        while True:
            conn, addr = server_socket.accept()  # Akzeptiere eingehende Verbindung
            print(f"Verbindung von {addr} akzeptiert")
            logger.info(f"Verbindung von {addr} akzeptiert")

            with conn:
                # Zuerst die Laenge des Strings (4 Bytes) empfangen
                length_data = conn.recv(4)
                if len(length_data) < 4:
                    print("Fehler: Ungueltige Laengenangabe empfangen")
                    logger.info("Fehler: Ungueltige Laengenangabe empfangen")
                    conn.close()
                    continue

                # Laenge des Strings aus den empfangenen 4 Bytes (uint32) extrahieren
                string_length = struct.unpack('!I', length_data)[0]  # '!I' = Network byte order, unsigned int (4 Bytes)
                print(f"Erwartete Laenge des Strings: {string_length} Bytes")
                logger.info(f"Eingehende Daten von Display: Erwartete Laenge des Strings: {string_length} Bytes")
                # Nun den String selbst empfangen (mit der angegebenen Laenge)
                received_string = conn.recv(string_length).decode('utf-8')
                print(f"Empfangene Daten: {received_string}")
                logger.info(f"Empfangene Daten: {received_string}")
                # DeepSleepTime an Server senden

                dst = 42
                logger.info(f"Ermittelte DeepSleep Zeit fuer Display XYZ {dst}")
                conn.send(bytes([dst]))
                logger.info(f"DeepSleep Zeit fuer Display XYZ gesendet")
                # Laenge der Nutzdaten senden
                logger.info("Bildaten graustufenbild_demo.png an Display XYZ senden")
                data_to_send = reduce_pixel_count(image_to_array("graustufenbild_demo.png"))
                laenge_daten = len(data_to_send)
                daten = f"{laenge_daten}\n"
                conn.sendall(daten.encode('utf-8'))
                # Nutzdaten an den ESP32 senden
                for value in data_to_send:
                    conn.send(bytes([value]))

                print(f"{len(data_to_send)} Bytes an {addr} gesendet")
                logger.info(f"{len(data_to_send)} Bytes an {addr} gesendet")



                # Nach dem Senden kannst du entscheiden, ob du die Verbindung offen haeltst oder schließt.
                # Hier wird die Verbindung nach dem Senden geschlossen.
                print(f"Verbindung zu {addr} geschlossen")







if __name__ == "__main__":
    try:
        
        #gen_image("2.312", "1", "2", "LIB", "ENG", "BGT241", "1", "3", "4", "WIB", "DEU", "BGT241", "0", "5", "6", "STT", "MAT",
        #  "BGT241", "0")
        # Logger erstellen
        logger = logging.getLogger("epaper_server.log")
        logger.setLevel(logging.INFO)  # Setze das Logging-Level auf INFO

        # FileHandler erstellen, der die Logs in eine Datei schreibt
        file_handler = logging.FileHandler("epaper_server.log")
        file_handler.setLevel(logging.INFO)

        # Format fuer die Log-Meldungen festlegen
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)

        # FileHandler zum Logger hinzufuegen
        logger.addHandler(file_handler)
        logger.info("Server start...")
        start_server()
    except KeyboardInterrupt:
        # Behandle Strg+C und beende den Server sauber
        logger.info("Server gestoppt.")
        print("\nStrg+C erkannt. Server wird beendet...")
