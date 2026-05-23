-- Sisteme başlangıç kategorilerini ekliyoruz
INSERT INTO Categories (category_name) 
VALUES ('Elektronik'), ('Kırtasiye'), ('Ev Gereçleri'), ('Spor Malzemeleri'), ('Oyuncak');

-- Başlangıç tedarikçilerini ekliyoruz
INSERT INTO Suppliers (company_name, contact_email) 
VALUES ('Global Tedarik', 'info@global.com'),
       ('Ev-Yaşam Dış Ticaret', 'destek@evyasam.com'),
       ('SporDünyası Ltd.', 'satis@spordunyasi.com'),
       ('Hobi Market', 'info@hobimarket.com');

-- Başlangıç ürünlerini ekliyoruz (Stoklar başta 0, kritik limitler devrede)
INSERT INTO Products (product_name, category_id, supplier_id, unit_price, stock_quantity, critical_limit)
VALUES 
('Kablosuz Mouse', 1, 1, 350.00, 0, 5),
('Airfryer', 3, 2, 4500.00, 5, 3),       
('Yoga Matı', 4, 3, 600.00, 0, 10),     
('LEGO Technic', 5, 4, 3200.00, 15, 5),  
('Termos 1L', 3, 2, 850.00, 2, 5); 

-- Geçmişe dönük birkaç mal alım işlemi (Trigger otomatik olarak ürünlerin stoğunu artıracak)
INSERT INTO Purchase_Orders (product_id, quantity_bought) VALUES (1, 50);
INSERT INTO Purchase_Orders (product_id, quantity_bought) VALUES (3, 100);
INSERT INTO Purchase_Orders (product_id, quantity_bought) VALUES (2, 20);

-- Geçmişe dönük birkaç satış işlemi (Trigger otomatik olarak ürünlerin stoğunu azaltacak)
INSERT INTO Sales (product_id, quantity_sold) VALUES (1, 10);
INSERT INTO Sales (product_id, quantity_sold) VALUES (4, 5);
INSERT INTO Sales (product_id, quantity_sold) VALUES (5, 20);