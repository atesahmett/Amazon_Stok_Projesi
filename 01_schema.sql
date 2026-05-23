-- ürünleri sınıflandırmak için kullanılır ve Products tablosuyla 1-N ilişkisi vardır.
CREATE TABLE Categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL UNIQUE
);

-- Tedarikçiler Tablosu
-- Ürünlerin temin edildiği firmaları barındırır.
CREATE TABLE Suppliers (
    supplier_id SERIAL PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    contact_email VARCHAR(100)
);

-- Ürünler Tablosu
-- Ana sistem. 
-- Kategori silindiğinde ürün korunur (ON DELETE SET NULL).
-- Tedarikçi silindiğinde ona ait ürünler veritabanından temizlenir (ON DELETE CASCADE).
CREATE TABLE Products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category_id INT REFERENCES Categories(category_id) ON DELETE SET NULL,
    supplier_id INT REFERENCES Suppliers(supplier_id) ON DELETE CASCADE,
    unit_price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT DEFAULT 0 CHECK (stock_quantity >= 0),
    critical_limit INT DEFAULT 5
);

-- Satın alma Siparişleri Tablosu
-- Stok girişlerini takip eder. Ürün silindiğinde  alım geçmişi de temizlenir.
CREATE TABLE Purchase_Orders (
    order_id SERIAL PRIMARY KEY,
    product_id INT REFERENCES Products(product_id) ON DELETE CASCADE,
    quantity_bought INT NOT NULL CHECK (quantity_bought > 0),
    purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Satışlar Tablosu
-- Stok çıkışlarını takip eder. Ürün silinirse satış geçmişi de temizlenir.
CREATE TABLE Sales (
    sale_id SERIAL PRIMARY KEY,
    product_id INT REFERENCES Products(product_id) ON DELETE CASCADE,
    quantity_sold INT NOT NULL CHECK (quantity_sold > 0),
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);