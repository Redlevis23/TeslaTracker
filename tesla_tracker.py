import requests
import time
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import hashlib

# Configuration
CHECK_INTERVAL = 120  # Vérification toutes les 2 minutes (en secondes)
TESLA_URL = "https://www.tesla.com/inventory/new/m3"  # URL des Tesla Model 3

# Config email
EMAIL_SENDER = "letmeresumeit@gmail.com"
EMAIL_PASSWORD = "ntpakxvvgdbckfeg"
EMAIL_RECEIVER = "reda.elidrissi95@gmail.com"

class TeslaTracker:
    def __init__(self):
        self.known_cars = set()  # Stocke les hash des voitures déjà vues
        
    def get_tesla_inventory(self):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(TESLA_URL, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Cible les conteneurs des voitures
            cars = soup.find_all('div', class_='result-photo-controls')
            if not cars:
                print("Aucun véhicule trouvé - vérifier la structure HTML")
            return cars
        except requests.RequestException as e:
            print(f"Erreur lors de la récupération: {e}")
            return []

    def send_email(self, subject, body):
        try:
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = EMAIL_SENDER
            msg['To'] = EMAIL_RECEIVER

            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                server.send_message(msg)
            print(f"Email envoyé à {EMAIL_RECEIVER}")
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email: {e}")

    def track_new_cars(self):
        print("Début de la surveillance des Tesla...")
        while True:
            cars = self.get_tesla_inventory()
            new_cars_found = False

            for car in cars:
                # Cherche le lien dans la balise <a>
                link_tag = car.find('a', href=True)
                if not link_tag:
                    continue
                car_link = link_tag['href']
                # Complète le lien si relatif
                if not car_link.startswith('http'):
                    car_link = f"https://www.tesla.com{car_link}"

                # Crée un identifiant unique basé sur le lien
                car_hash = hashlib.md5(car_link.encode()).hexdigest()

                if car_hash not in self.known_cars:
                    self.known_cars.add(car_hash)
                    new_cars_found = True
                    
                    # Prépare le message avec le lien
                    message = (
                        f"Nouvelle Tesla disponible!\n"
                        f"Lien direct: {car_link}\n"
                        f"Détails: {str(car)[:200]}..."
                    )
                    
                    # Envoi de la notification par email
                    self.send_email("Nouvelle Tesla trouvée!", message)

            if not new_cars_found:
                print(f"Vérification à {time.ctime()}: Aucune nouvelle voiture trouvée")
            
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    tracker = TeslaTracker()
    tracker.track_new_cars()