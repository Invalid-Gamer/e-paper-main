from DATABASE.raumdatabase import RaumManager

def main():
    raum_manager = RaumManager()
    
    while True:
        # Benutzer-Eingaben für einen neuen Raum
        print("\n--- Neuen Raum anlegen ---")
        raumname = input("Geben Sie den Raumnamen ein (z.B. '2.311'): ")
        secret = input("Geben Sie das Secret für den Raum ein: ")

        # Raum hinzufügen
        raum_manager.add_raum(raumname, None, secret)

        # Abfrage, ob noch ein weiterer Raum angelegt werden soll
        weiter = input("Möchten Sie einen weiteren Raum anlegen? (j/n): ").strip().lower()
        if weiter != 'j':
            print("Programm beendet.")
            break

if __name__ == "__main__":
    main()
