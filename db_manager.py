import psycopg2
from psycopg2 import extras

# Yerel PostgreSQL veritabanı bağlantı ayarları
DB_CONFIG = {
    "dbname": "amazon_inventory", 
    "user": "postgres",
    "password": "ates000",  # Benim veritabanı şifresi
    "host": "localhost",
    "port": "5432"
}

def get_connection():
    """Veritabanına güvenli bir bağlantı açar."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Bağlantı Hatası: {e}")
        return None

def fetch_all_products():
    """Tüm ürünleri, kategori isimleriyle birlikte sözlük yapısında döndürür."""
    conn = get_connection()
    if not conn: return []
    
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    try:
        query = """
            SELECT p.product_id, p.product_name, c.category_name, 
                   p.unit_price, p.stock_quantity, p.critical_limit
            FROM Products p
            JOIN Categories c ON p.category_id = c.category_id
            ORDER BY p.product_id;
        """
        cur.execute(query)
        return cur.fetchall()
    except Exception as e:
        print(f"Veri çekme hatası: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def fetch_all_categories():
    """Yeni ürün ekleme formunda listelenmek üzere tüm kategorileri veritabanından çeker."""
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    try:
        cur.execute("SELECT * FROM Categories;")
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def add_stock(product_id, quantity):
    """
    Purchase_Orders tablosuna yeni satın alım kaydı ekler. 
    Veritabanı seviyesindeki trigger (tetikleyici) otomatik olarak Products tablosundaki stoğu artıracaktır.
    """
    conn = get_connection()
    if not conn: return False, "Veritabanı bağlantısı yok."
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO Purchase_Orders (product_id, quantity_bought) VALUES (%s, %s)",
            (product_id, quantity)
        )
        conn.commit()
        return True, "Stok başarıyla artırıldı."
    except Exception as e:
        conn.rollback()
        return False, f"Hata oluştu: {str(e)}"
    finally:
        cur.close()
        conn.close()

def sell_product(product_id, quantity):
    """
    Sales tablosuna satış kaydı ekler. 
    Veritabanı tetikleyicisi (trigger) stoğu azaltır. Stok yetersizse trigger 
    hata fırlatır, bu fonksiyon da o hatayı yakalayıp kullanıcı arayüzüne iletir.
    """
    conn = get_connection()
    if not conn: return False, "Veritabanı bağlantısı yok."
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO Sales (product_id, quantity_sold) VALUES (%s, %s)",
            (product_id, quantity)
        )
        conn.commit()
        return True, "Satış işlemi başarıyla kaydedildi."
    except Exception as e:
        conn.rollback()
        return False, str(e).split('\n')[0] 
    finally:
        cur.close()
        conn.close()

def add_new_supplier(name, email):
    """Sisteme yeni bir tedarikçi firma ekler."""
    conn = get_connection()
    if not conn: return False, "Veritabanı bağlantısı yok."
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO Suppliers (company_name, contact_email) VALUES (%s, %s)", (name, email))
        conn.commit()
        return True, "Tedarikçi başarıyla eklendi."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cur.close()
        conn.close()

def add_new_product(name, cat_id, sup_id, price, limit):
    """Yeni bir ürün tanımlar (Başlangıç stoğu varsayılan olarak 0'dır)."""
    conn = get_connection()
    if not conn: return False, "Veritabanı bağlantısı yok."
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO Products (product_name, category_id, supplier_id, unit_price, stock_quantity, critical_limit) VALUES (%s, %s, %s, %s, 0, %s)",
            (name, cat_id, sup_id, price, limit)
        )
        conn.commit()
        return True, "Yeni ürün başarıyla tanımlandı."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cur.close()
        conn.close()

def add_category(category_name):
    """Sisteme yeni bir ürün kategorisi ekler."""
    conn = get_connection()
    if not conn: return False, "Veritabanı bağlantısı yok."
    cur = conn.cursor()
    try:
        query = "INSERT INTO Categories (category_name) VALUES (%s)"
        cur.execute(query, (category_name,))
        conn.commit()
        return True, "Kategori başarıyla eklendi."
    except Exception as e:
        conn.rollback()
        return False, f"Kategori ekleme hatası: {str(e)}"
    finally:
        cur.close()
        conn.close()

def delete_product(product_id):
    """Bir ürünü sistemden siler (Satış ve alım kayıtları da CASCADE kısıtlamasıyla otomatik silinir)."""
    conn = get_connection()
    if not conn: return False, "Veritabanı bağlantısı yok."
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM Products WHERE product_id = %s", (product_id,))
        conn.commit()
        return True, "Ürün silindi."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cur.close()
        conn.close()

def delete_supplier(supplier_id):
    """Bir tedarikçiyi sistemden siler."""
    conn = get_connection()
    if not conn: return False, "Veritabanı bağlantısı yok."
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM Suppliers WHERE supplier_id = %s", (supplier_id,))
        conn.commit()
        return True, "Tedarikçi silindi."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cur.close()
        conn.close()

def delete_category(category_id):
    """Belirtilen kategoriyi sistemden siler."""
    conn = get_connection()
    if not conn: return False, "Veritabanı bağlantısı yok."
    cur = conn.cursor()
    try:
        query = "DELETE FROM Categories WHERE category_id = %s"
        cur.execute(query, (category_id,))
        conn.commit()
        if cur.rowcount > 0:
            return True, "Kategori silindi."
        else:
            return False, "Silinecek kategori bulunamadı."
    except Exception as e:
        conn.rollback()
        return False, f"Kategori silme hatası: {str(e)}"
    finally:
        cur.close()
        conn.close()

def update_supplier(supplier_id, new_name, new_email):
    """Var olan tedarikçinin firma adı ve e-posta bilgilerini günceller."""
    conn = get_connection()
    if not conn: return False, "Veritabanı bağlantısı yok."
    cur = conn.cursor()
    try:
        query = """
            UPDATE Suppliers 
            SET company_name = %s, contact_email = %s 
            WHERE supplier_id = %s
        """
        cur.execute(query, (new_name, new_email, supplier_id))
        conn.commit()
        if cur.rowcount > 0:
            return True, "Tedarikçi başarıyla güncellendi."
        else:
            return False, "Tedarikçi bulunamadı."
    except Exception as e:
        conn.rollback()
        return False, f"Güncelleme hatası: {str(e)}"
    finally:
        cur.close()
        conn.close()

def update_product(product_id, name, cat_id, sup_id, price, critical_limit):
    """Stok miktarı hariç, ürünlerin genel bilgilerini günceller."""
    conn = get_connection()
    if not conn: return False, "Veritabanı bağlantısı yok."
    cur = conn.cursor()
    try:
        query = """
            UPDATE Products 
            SET product_name = %s, 
                category_id = %s, 
                supplier_id = %s, 
                unit_price = %s, 
                critical_limit = %s
            WHERE product_id = %s
        """
        cur.execute(query, (name, cat_id, sup_id, price, critical_limit, product_id))
        conn.commit()
        if cur.rowcount > 0:
            return True, "Ürün bilgileri güncellendi."
        else:
            return False, "Ürün bulunamadı."
    except Exception as e:
        conn.rollback()
        return False, f"Ürün güncelleme hatası: {str(e)}"
    finally:
        cur.close()
        conn.close()

def fetch_all_suppliers():
    """Tüm tedarikçi listesini arayüzde göstermek üzere çeker."""
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    try:
        cur.execute("SELECT * FROM Suppliers")
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def fetch_purchase_history():
    """Tüm alım (stok giriş) geçmişini tarih sırasına göre getirir."""
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    try:
        query = """
            SELECT po.order_id, p.product_name, po.product_id, po.quantity_bought, po.purchase_date
            FROM Purchase_Orders po
            JOIN Products p ON po.product_id = p.product_id
            ORDER BY po.purchase_date DESC
        """
        cur.execute(query)
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def fetch_sales_history():
    """Tüm satış (stok çıkış) geçmişini toplam tutar hesaplamasıyla birlikte getirir."""
    conn = get_connection()
    if not conn: return []
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    try:
        query = """
            SELECT s.sale_id, p.product_name, s.product_id, s.quantity_sold, p.unit_price, 
                   (s.quantity_sold * p.unit_price) as total_price, s.sale_date
            FROM Sales s
            JOIN Products p ON s.product_id = p.product_id
            ORDER BY s.sale_date DESC
        """
        cur.execute(query)
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    print("Bağlantı test ediliyor...")
    prods = fetch_all_products()
    if prods:
        print(f"Bağlantı başarılı! {len(prods)} adet ürün bulundu.")
    else:
        print("Bağlantı başarılı veya veritabanı şu an boş.")