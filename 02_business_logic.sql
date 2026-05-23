-- STOK ARTIRMA FONKSİYONU(increase) VE TRIGGER'I
-- Purchase_Orders (Satın alma) tablosuna yeni mal girişi olduğunda çalışır.
CREATE OR REPLACE FUNCTION fn_increase_stock()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE Products
    SET stock_quantity = stock_quantity + NEW.quantity_bought
    WHERE product_id = NEW.product_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_after_purchase
AFTER INSERT ON Purchase_Orders
FOR EACH ROW EXECUTE FUNCTION fn_increase_stock();


-- STOK AZALTMA FONKSİYONU VE TRIGGER'I
-- Sales (Satış) tablosuna kayıt eklenmeden önce çalışır ve stoğu kontrol eder.
CREATE OR REPLACE FUNCTION fn_decrease_stock()
RETURNS TRIGGER AS $$
DECLARE
    v_current_stock INT;
BEGIN
    -- Satılmak istenen ürünün mevcut stoğunu bul
    SELECT stock_quantity INTO v_current_stock FROM Products WHERE product_id = NEW.product_id;

    -- Eğer stok yetmiyorsa satış işlemine izin verme ve veritabanı seviyesinde hata fırlat.
    IF v_current_stock < NEW.quantity_sold THEN
        RAISE EXCEPTION 'Stok yetersiz! Mevcut: %, İstenen: %', v_current_stock, NEW.quantity_sold;
    END IF;

    -- Stok yetiyorsa düş
    UPDATE Products
    SET stock_quantity = stock_quantity - NEW.quantity_sold
    WHERE product_id = NEW.product_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_before_sale
BEFORE INSERT ON Sales
FOR EACH ROW EXECUTE FUNCTION fn_decrease_stock();