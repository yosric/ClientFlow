import os
import sqlite3


def get_connection():
    return sqlite3.connect(DB_NAME)


APP_NAME = "ClientFlow"

def get_db_path():
    appdata = os.getenv("APPDATA")
    if not appdata:
        raise RuntimeError("APPDATA environment variable not found")

    app_dir = os.path.join(appdata, APP_NAME)
    os.makedirs(app_dir, exist_ok=True)  # 🔥 THIS LINE FIXES IT

    return os.path.join(app_dir, "app.db")

DB_NAME = get_db_path()

def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        telephone TEXT,
        adresse TEXT,
        email TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS ventes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        date TEXT,
        reference TEXT,
        montant_total REAL,
        FOREIGN KEY(client_id) REFERENCES clients(id)
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS paiements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vente_id INTEGER,
        date TEXT,
        montant REAL,
        mode TEXT,
        note TEXT,
        FOREIGN KEY(vente_id) REFERENCES ventes(id)
    )
    """)

    # Categories table: product categories
    c.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT
    )
    """)

    # Products table: holds available products and their unit price
    c.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        unit_price REAL NOT NULL,
        category_id INTEGER,
        FOREIGN KEY(category_id) REFERENCES categories(id)
    )
    """)

    # Sale items: items belonging to a vente (sale)
    c.execute("""
    CREATE TABLE IF NOT EXISTS vente_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vente_id INTEGER NOT NULL,
        product_id INTEGER,
        description TEXT,
        quantity REAL DEFAULT 1,
        unit_price REAL,
        total_price REAL,
        FOREIGN KEY(vente_id) REFERENCES ventes(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    )
    """)

    # Add new columns if not exist
    try:
        c.execute("ALTER TABLE clients ADD COLUMN adresse TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists
    try:
        c.execute("ALTER TABLE clients ADD COLUMN email TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE ventes ADD COLUMN description TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists
    try:
        c.execute("ALTER TABLE products ADD COLUMN category_id INTEGER")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # older installations may not have new tables; ensure columns exist where applicable
    # (product tables created above with IF NOT EXISTS are non-destructive)

    conn.commit()
    conn.close()


def add_product(name, unit_price, category_id=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO products (name, unit_price, category_id) VALUES (?, ?, ?)", (name, float(unit_price), category_id))
    vid = c.lastrowid
    conn.commit()
    conn.close()
    return vid


def get_products():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, unit_price, category_id FROM products ORDER BY name")
    rows = c.fetchall()
    conn.close()
    return rows


def update_product(product_id, name, unit_price, category_id=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE products SET name=?, unit_price=?, category_id=? WHERE id=?", (name, float(unit_price), category_id, product_id))
    conn.commit()
    conn.close()


def delete_product(product_id):
    conn = get_connection()
    c = conn.cursor()
    # Remove any orphan references in vente_items gracefully by setting product_id to NULL
    c.execute("UPDATE vente_items SET product_id=NULL WHERE product_id=?", (product_id,))
    c.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()


def add_category(name, description=""):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO categories (name, description) VALUES (?, ?)", (name, description))
    cat_id = c.lastrowid
    conn.commit()
    conn.close()
    return cat_id


def get_categories():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, description FROM categories ORDER BY name")
    rows = c.fetchall()
    conn.close()
    return rows


def update_category(category_id, name, description=""):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE categories SET name=?, description=? WHERE id=?", (name, description, category_id))
    conn.commit()
    conn.close()


def delete_category(category_id):
    conn = get_connection()
    c = conn.cursor()
    # Set products' category_id to NULL when deleting a category
    c.execute("UPDATE products SET category_id=NULL WHERE category_id=?", (category_id,))
    c.execute("DELETE FROM categories WHERE id=?", (category_id,))
    conn.commit()
    conn.close()


def add_vente(client_id, date, reference, montant_total, description=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO ventes (client_id, date, reference, montant_total, description) VALUES (?, ?, ?, ?, ?)",
        (client_id, date, reference, montant_total, description)
    )
    vid = c.lastrowid
    conn.commit()
    conn.close()
    return vid


def add_vente_item(vente_id, product_id, description, quantity, unit_price, total_price):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO vente_items (vente_id, product_id, description, quantity, unit_price, total_price) VALUES (?, ?, ?, ?, ?, ?)",
        (vente_id, product_id, description, quantity, unit_price, total_price)
    )
    iid = c.lastrowid
    conn.commit()
    conn.close()
    return iid




def reset_db():
    """Reset the database by dropping all tables and recreating them"""
    conn = get_connection()
    c = conn.cursor()

    # Drop all tables
    c.execute("DROP TABLE IF EXISTS paiements")
    c.execute("DROP TABLE IF EXISTS ventes")
    c.execute("DROP TABLE IF EXISTS clients")

    conn.commit()
    conn.close()

    # Reinitialize the database
    init_db()
    create_indexes()
    print("Database reset successfully.")


def create_indexes():
    conn = get_connection()
    c = conn.cursor()

    # Recherche rapide par nom
    c.execute("CREATE INDEX IF NOT EXISTS idx_clients_nom ON clients(nom)")

    # Recherche rapide par email
    c.execute("CREATE INDEX IF NOT EXISTS idx_clients_email ON clients(email)")

    # Recherche rapide par téléphone si besoin
    c.execute("CREATE INDEX IF NOT EXISTS idx_clients_telephone ON clients(telephone)")

    # Pour les ventes liées à un client
    c.execute("CREATE INDEX IF NOT EXISTS idx_ventes_client_id ON ventes(client_id)")

    # Pour les paiements liés à une vente
    c.execute("CREATE INDEX IF NOT EXISTS idx_paiements_vente_id ON paiements(vente_id)")

    conn.commit()
    conn.close()
    print("Indexes created successfully.")





