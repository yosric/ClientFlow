import sqlite3
from datetime import datetime, timedelta
import random

def get_connection():
    from database import get_connection
    return get_connection()

def seed_clients():
    """Add sample Tunisian clients"""
    clients = [
        ("Ahmed Ben Ali", "+216 20 123 456", "Tunis, Avenue Habib Bourguiba", "ahmed@email.com"),
        ("Fatma Trabelsi", "+216 70 987 654", "Sousse, Boulevard du 14 Janvier", "fatma@email.com"),
        ("Mohamed Salah", "+216 73 555 123", "Monastir, Rue de la Kasbah", "mohamed@email.com"),
        ("Leila Mansour", "+216 71 444 789", "Sfax, Avenue de la République", "leila@email.com"),
        ("Karim Jaziri", "+216 72 333 456", "Bizerte, Rue de France", "karim@email.com"),
       
    ]

    conn = get_connection()
    c = conn.cursor()

    for client in clients:
        c.execute("""
            INSERT INTO clients (nom, telephone, adresse, email)
            VALUES (?, ?, ?, ?)
        """, client)

    conn.commit()
    conn.close()
    print(f"Added {len(clients)} sample clients")

def seed_ventes():
    """Add sample sales with different dates"""
    conn = get_connection()
    c = conn.cursor()

    # Get all client IDs
    c.execute("SELECT id FROM clients")
    client_ids = [row[0] for row in c.fetchall()]

    if not client_ids:
        print("No clients found. Please run seed_clients() first.")
        return

    # Generate sales for the last 6 months
    base_date = datetime.now() - timedelta(days=180)
    ventes = []

    descriptions = [
        "Tuyaux PVC 50mm x 10m",
        "Robinets mélangeurs x 5",
        "Joints silicone 300ml x 20",
        "Vannes de régulation x 3",
        "Tuyaux galvanisés 32mm x 15m",
        "Colliers de serrage x 50",
        "Siphons lavabo x 8",
        "Flexible douche 1.5m x 12",
        "Tees PVC 40mm x 25",
        "Coudes PVC 90° x 30",
        "Adhésif téflon x 10 rouleaux",
        "Pistolet à silicone x 3",
        "Clés plates x 15",
        "Niveau laser x 2",
        "Mètre ruban 5m x 8",
        "Scie à métaux x 4",
        "Perceuse électrique x 2",
        "Mèches métal x 50",
        "Tournevis cruciforme x 20",
        "Marteau arrache-clou x 3"
    ]

    for i in range(50):  # 50 sales
        client_id = random.choice(client_ids)
        days_offset = random.randint(0, 180)
        sale_date = base_date + timedelta(days=days_offset)

        # Generate reference
        ref_number = f"V{sale_date.strftime('%y%m%d')}{random.randint(1000, 9999)}"

        # Random amount between 50 and 2000 DT
        montant_total = round(random.uniform(50, 2000), 2)

        # Random description
        description = random.choice(descriptions)

        ventes.append((client_id, sale_date.strftime('%Y-%m-%d'), ref_number, montant_total, description))

    for vente in ventes:
        c.execute("""
            INSERT INTO ventes (client_id, date, reference, montant_total, description)
            VALUES (?, ?, ?, ?, ?)
        """, vente)

    conn.commit()
    conn.close()
    print(f"Added {len(ventes)} sample sales")

def seed_paiements():
    """Add sample payments with different dates for existing sales"""
    conn = get_connection()
    c = conn.cursor()

    # Get all vente IDs with their dates and amounts
    c.execute("SELECT id, date, montant_total FROM ventes")
    ventes = c.fetchall()

    if not ventes:
        print("No sales found. Please run seed_ventes() first.")
        return

    paiements = []
    payment_modes = ["Espèces", "Carte bancaire", "Chèque", "Virement", "Mobile Money"]

    for vente_id, vente_date, montant_total in ventes:
        # Convert vente_date to datetime
        vente_datetime = datetime.strptime(vente_date, '%Y-%m-%d')

        # Each sale gets 1-3 payments
        num_payments = random.randint(1, 3)

        remaining_amount = montant_total
        for i in range(num_payments):
            if remaining_amount <= 0:
                break

            # Payment date: same day or up to 30 days after sale
            days_after = random.randint(0, 30)
            payment_date = vente_datetime + timedelta(days=days_after)

            # Payment amount: partial or full remaining amount
            if i == num_payments - 1:  # Last payment
                payment_amount = remaining_amount
            else:
                # Partial payment: 30-80% of remaining
                min_amount = max(10, remaining_amount * 0.3)
                max_amount = remaining_amount * 0.8
                payment_amount = round(random.uniform(min_amount, max_amount), 2)

            remaining_amount -= payment_amount
            remaining_amount = round(remaining_amount, 2)

            # Payment mode
            mode = random.choice(payment_modes)

            # Optional note
            notes = [
                "",
                "Paiement partiel",
                "Règlement complet",
                "Via mobile",
                "À la livraison",
                "Par chèque différé",
                "Escompte accordé",
                "Paiement anticipé"
            ]
            note = random.choice(notes)

            paiements.append((vente_id, payment_date.strftime('%Y-%m-%d'), payment_amount, mode, note))

    for paiement in paiements:
        c.execute("""
            INSERT INTO paiements (vente_id, date, montant, mode, note)
            VALUES (?, ?, ?, ?, ?)
        """, paiement)

    conn.commit()
    conn.close()
    print(f"Added {len(paiements)} sample payments with different dates")

def seed_all():
    """Run all seeding functions"""
    print("Seeding database with sample data...")
    seed_clients()
    seed_ventes()
    seed_paiements()
    print("Seeding completed!")

if __name__ == "__main__":
    seed_all()
