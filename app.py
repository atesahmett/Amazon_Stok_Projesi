import streamlit as st
import pandas as pd
from db_manager import (fetch_all_products, add_stock, sell_product, 
                        add_new_product, add_new_supplier, delete_product, 
                        delete_supplier, fetch_all_suppliers, fetch_all_categories, 
                        fetch_purchase_history, fetch_sales_history, delete_category, add_category)

# Arayüzün sayfa ayarlarını ve sekme başlığını belirliyoruz
st.set_page_config(page_title="Amazon Stok Sistemi", layout="wide", initial_sidebar_state="expanded")

# Arayüzü biraz daha profesyonel göstermek için özel CSS ekledim (Amazon renkleri)
st.markdown("""
    <style>
    .stButton>button { background-color: #FF9900; color: white; border-radius: 5px; }
    .stHeader { color: #232F3E; }
    </style>
    """, unsafe_allow_html=True)

st.title("📦 Amazon Envanter Yönetim Paneli")
st.markdown("---")

# Silme işlemi sonrası anlık bildirim göstermek için Session State kullandım
if 'last_msg' in st.session_state:
    st.success(st.session_state['last_msg'])
    del st.session_state['last_msg'] 

# Sol taraftaki menü barı
menu = ["📊 Stok Listesi", "🔄 Stok Hareketleri (Alım/Satış)", "🛒 Ürün Yönetimi", "🏢 Tedarikçi Yönetimi"]
choice = st.sidebar.selectbox("Gezinti Menüsü", menu)

# --- 1. SAYFA: STOK LİSTESİ ---
if choice == "📊 Stok Listesi":
    st.subheader("Güncel Envanter Durumu")
    products = fetch_all_products()
    
    if products:
        df = pd.DataFrame(products)
        df.columns = ['ID', 'Ürün Adı', 'Kategori', 'Birim Fiyat', 'Stok Miktarı', 'Kritik Limit']
        
        # Kritik stoğun altındaki ürünleri kırmızı ile vurgulayan fonksiyon
        def highlight_low_stock(row):
            return ['background-color: #ffcccc' if row['Stok Miktarı'] <= row['Kritik Limit'] else '' for _ in row]
        
        st.dataframe(df.style.apply(highlight_low_stock, axis=1), use_container_width=True, hide_index=True)
        
        # Sol menüde kritik stok uyarılarını listeletiyorum
        st.sidebar.subheader("🚨 Kritik Stok Uyarıları")
        low_stock_items = [p for p in products if p['stock_quantity'] <= p['critical_limit']]
        for item in low_stock_items:
            st.sidebar.error(f"{item['product_name']}! (Kalan: {item['stock_quantity']})")
    else:
        st.info("Veritabanında ürün bulunamadı.")

# --- 2. SAYFA: STOK HAREKETLERİ ---
elif choice == "🔄 Stok Hareketleri (Alım/Satış)":
    st.subheader("Hızlı Stok İşlemleri")
    
    products_list = fetch_all_products()
    
    if not products_list:
        st.warning("İşlem yapabilmek için önce ürün eklemelisiniz.")
    else:
        product_options = {f"{p['product_id']} - {p['product_name']}": p['product_id'] for p in products_list}
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("📥 Mal Kabulü (Stok Artır)")
            with st.form("purchase_form"):
                selected_p = st.selectbox("Ürün Seçin", options=list(product_options.keys()))
                qty = st.number_input("Alınan Miktar", min_value=1, step=1)
                
                if st.form_submit_button("Stoğa Ekle"):
                    p_id = product_options[selected_p] 
                    success, data = add_stock(p_id, qty)
                    if success: 
                        st.success(f"✅ {data}")
                    else: st.error(data)
        
        with col2:
            st.info("📤 Satış Kaydı (Stok Azalt)")
            with st.form("sale_form"):
                selected_p_s = st.selectbox("Satılan Ürün", options=list(product_options.keys()))
                qty_s = st.number_input("Satış Miktarı", min_value=1, step=1)
                
                if st.form_submit_button("Satışı Onayla"):
                    p_id_s = product_options[selected_p_s]
                    success, data = sell_product(p_id_s, qty_s)
                    if success: 
                        st.success(f"✅ {data}")
                    else: st.error(data)

    st.markdown("---")
    st.subheader("📋 İşlem Geçmişi")
    
    tab_purchase, tab_sales = st.tabs(["📥 Alım Geçmişi", "📤 Satış Geçmişi"])
    
    with tab_purchase:
        st.write("Yapılan stok girişleri:")
        purchases = fetch_purchase_history()
        if purchases:
            df_p = pd.DataFrame(purchases)
            df_p.columns = ['Sipariş ID', 'Ürün Adı', 'Ürün ID', 'Miktar', 'İşlem Tarihi']
            st.dataframe(df_p, use_container_width=True)
        else:
            st.info("Henüz alım kaydı bulunmuyor.")
            
    with tab_sales:
        st.write("Yapılan satış detayları:")
        sales = fetch_sales_history()
        if sales:
            df_s = pd.DataFrame(sales)
            df_s.columns = ['Satış ID', 'Ürün Adı', 'Ürün ID', 'Satılan Adet', 'Birim Fiyat', 'Toplam Tutar', 'Satış Tarihi']
            df_s['Birim Fiyat'] = df_s['Birim Fiyat'].map('{:,.2f} ₺'.format)
            df_s['Toplam Tutar'] = df_s['Toplam Tutar'].map('{:,.2f} ₺'.format)
            st.dataframe(df_s, use_container_width=True)
        else:
            st.info("Henüz satış kaydı bulunmuyor.")

# --- 3. SAYFA: ÜRÜN YÖNETİMİ ---
elif choice == "🛒 Ürün Yönetimi":
    st.subheader("Yeni Ürün Tanımlama ve Ürün Silme")
    
    tab1, tab2, tab3 = st.tabs(["➕ Yeni Ürün Ekle", "🗑️ Ürün Sil", "📁 Kategori Yönetimi"])
    
    with tab1:
        categories = fetch_all_categories()
        suppliers = fetch_all_suppliers()
        
        if categories and suppliers:
            with st.form("add_product_form"):
                p_name = st.text_input("Ürün Adı")
                
                cat_id = st.selectbox("Kategori", options=[c['category_id'] for c in categories], 
                                     format_func=lambda x: next(c['category_name'] for c in categories if c['category_id'] == x))
                sup_id = st.selectbox("Tedarikçi", options=[s['supplier_id'] for s in suppliers], 
                                     format_func=lambda x: next(s['company_name'] for s in suppliers if s['supplier_id'] == x))
                
                price = st.number_input("Birim Fiyat (TL)", min_value=0.0)
                limit = st.number_input("Kritik Stok Sınırı", min_value=1, value=5)
                
                if st.form_submit_button("Ürünü Kaydet"):
                    success, msg = add_new_product(p_name, cat_id, sup_id, price, limit)
                    if success: st.success(msg)
                    else: st.error(msg)
        else:
            st.warning("Ürün eklemeden önce lütfen en az bir kategori ve tedarikçi ekleyin.")

    with tab2:
        st.warning("⚠️ DİKKAT: Ürünü sildiğinizde ON DELETE CASCADE sayesinde bu ürüne ait tüm alım ve satış kayıtları kalıcı olarak silinecektir!")
        
        products_list = fetch_all_products()
        
        if products_list:
            product_options_del = {f"{p['product_id']} - {p['product_name']}": p['product_id'] for p in products_list}
            selected_del = st.selectbox("Silinecek Ürünü Seçin", options=list(product_options_del.keys()), key="del_select")
            
            st.write(f"Seçili Ürün: **{selected_del}**")
            confirm_check = st.checkbox("Bu ürünü ve ilgili tüm verileri kalıcı olarak silmeyi onaylıyorum.")
            
            if st.button("🚨 Ürünü Sistemden Kaldır"):
                if confirm_check:
                    del_id = product_options_del[selected_del]
                    success, msg = delete_product(del_id)
                    if success: 
                        st.session_state['last_msg'] = f"✅ {selected_del} başarıyla silindi."
                        st.rerun()
                    else: 
                        st.error(f"Hata: {msg}")
                else:
                    st.warning("Lütfen silme işlemini gerçekleştirmek için yukarıdaki onay kutucuğunu işaretleyin.")
        else:
            st.info("Sistemde silinecek ürün bulunamadı.")
		
    with tab3:
        st.markdown("### ➕ Yeni Kategori Tanımla")
        with st.form("add_category_form"):
            new_cat_name = st.text_input("Kategori Adı", placeholder="Örn: Mutfak Gereçleri")
            submit_cat = st.form_submit_button("Kategoriyi Kaydet")
            
            if submit_cat:
                if new_cat_name.strip():
                    success, msg = add_category(new_cat_name)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.warning("Lütfen geçerli bir kategori adı girin.")
        
        st.markdown("---")
        st.write("#### Mevcut Kategoriler")
        cats = fetch_all_categories()
        if cats:
            st.table(pd.DataFrame(cats))

        st.markdown("---")
        st.markdown("### 🗑️ Kategori Sil")
        
        if cats:
            cat_options = {f"{c['category_id']} - {c['category_name']}": c['category_id'] for c in cats}
            selected_cat_to_del = st.selectbox("Silinecek Kategoriyi Seçin", options=list(cat_options.keys()))
            
            if st.button("Kategoriyi Sil", type="secondary"):
                cat_id_to_del = cat_options[selected_cat_to_del]
                success, msg = delete_category(cat_id_to_del)
                
                if success:
                    st.success(f"✅ {msg}")
                    st.rerun()
                else:
                    st.error(msg)
        else:
            st.info("Sistemde silinecek kategori bulunamadı.")
  
# --- 4. SAYFA: TEDARİKÇİ YÖNETİMİ ---
elif choice == "🏢 Tedarikçi Yönetimi":
    st.subheader("Tedarikçi Listesi ve Kayıt")
    
    suppliers = fetch_all_suppliers()
    if suppliers:
        st.table(pd.DataFrame(suppliers))
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### ➕ Yeni Tedarikçi")
        with st.form("new_sup"):
            s_name = st.text_input("Firma Adı")
            s_mail = st.text_input("E-posta")
            if st.form_submit_button("Kaydet"):
                success, msg = add_new_supplier(s_name, s_mail)
                if success: st.success(msg)
                else: st.error(msg)
                
    with col_b:
        st.markdown("### 🗑️ Tedarikçi Sil")
        s_del_id = st.number_input("Tedarikçi ID", min_value=1, step=1)
        if st.button("Tedarikçiyi Sistemden Kaldır"):
            success, msg = delete_supplier(s_del_id)
            if success: st.success(msg)
            else: st.error(msg)