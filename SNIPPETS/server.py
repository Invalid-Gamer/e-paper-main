import socket
import numpy as np
from PIL import Image
import struct

# Server-Einstellungen
HOST = '0.0.0.0'  # Lausche auf allen verfügbaren Netzwerkschnittstellen
PORT = 8080       # Der Port, auf dem der Server auf Verbindungen wartet

def image_to_array(image_path):
    """Öffnet ein Graustufenbild und gibt die Pixelwerte als eindimensionales Array zurück."""
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
    """Reduziert die Pixelanzahl um die Hälfte."""
    # Neues Array erstellen, das die Hälfte der Pixelanzahl hat
    reduced_array = pixel_array[::2]  # Nur jeden zweiten Pixel nehmen
    return reduced_array

def start_server():
    # Erstelle einen TCP/IP-Server-Socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()  # Warte auf eingehende Verbindungen
        print(f"Server läuft und wartet auf Verbindungen auf {HOST}:{PORT}...")

        # Endlosschleife, um mehrere Verbindungen zu ermöglichen
        try:
            while True:
                conn, addr = server_socket.accept()  # Akzeptiere eingehende Verbindung
                print(f"Verbindung von {addr} akzeptiert")
                
                with conn:
                            # Zuerst die Länge des Strings (4 Bytes) empfangen
                    length_data = conn.recv(4)
                    if len(length_data) < 4:
                        print("Fehler: Ungültige Längenangabe empfangen")
                        conn.close()
                        continue

                    # Länge des Strings aus den empfangenen 4 Bytes (uint32) extrahieren
                    string_length = struct.unpack('!I', length_data)[0]  # '!I' = Network byte order, unsigned int (4 Bytes)
                    print(f"Erwartete Länge des Strings: {string_length} Bytes")

                    # Nun den String selbst empfangen (mit der angegebenen Länge)
                    received_string = conn.recv(string_length).decode('utf-8')
                    print(f"Empfangene Daten: {received_string}")
                    # DeepSleepTime an Server senden
                    dst = 42
                    conn.send(bytes([dst]))
                    # Länge der Nutzdaten senden
                    data_to_send = reduce_pixel_count(image_to_array("graustufenbild_demo.png"))
                    laenge_daten = len(data_to_send)
                    daten = f"{laenge_daten}\n"
                    conn.sendall(daten.encode('utf-8'))
                    # Nutzdaten an den ESP32 senden
                    for value in data_to_send:
                        conn.send(bytes([value]))

                    print(f"{len(data_to_send)} Bytes an {addr} gesendet")

                    # Nach dem Senden kannst du entscheiden, ob du die Verbindung offen hältst oder schließt.
                    # Hier wird die Verbindung nach dem Senden geschlossen.
                    print(f"Verbindung zu {addr} geschlossen")
        except KeyboardInterrupt:
            # Behandle Strg+C und beende den Server sauber
            print("\nStrg+C erkannt. Server wird beendet...")

if __name__ == "__main__":
    start_server()