Даниил, [21.05.2025 4:36]
import streamlit as st
import sqlite3
import pandas as pd

def get_db_connection():
    conn = sqlite3.connect('db1')
    conn.row_factory = sqlite3.Row
    return conn

def get_workshops():
    conn = get_db_connection()
    workshops = conn.execute('SELECT * FROM Цех').fetchall()
    conn.close()
    return [dict(workshop) for workshop in workshops]

def calculate_total_production_time(product_id):
    conn = get_db_connection()
    total_time = conn.execute(
        'SELECT SUM(Время) as total FROM ПродуктЦех WHERE ПродуктКод = ?',
        (product_id,)  
    ).fetchone()['total']
    conn.close()
    return total_time if total_time else 0

def get_products():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    
    products_with_time = []
    for product in products:
        product_dict = dict(product)
        product_dict['total_time'] = calculate_total_production_time(product['id'])
        products_with_time.append(product_dict)
    
    conn.close()
    return products_with_time

def update_product(product_id, new_title):
    conn = get_db_connection()
    conn.execute('UPDATE products SET title = ? WHERE id = ?', (new_title, product_id))
    conn.commit()
    conn.close()

def add_product(title):
    conn = get_db_connection()
    conn.execute('INSERT INTO products (title) VALUES (?)', (title,))
    conn.commit()
    conn.close()

def show_workshops_page():
    st.title("Список производственных цехов")
    workshops = get_workshops()
    
    if not workshops:
        st.warning("Нет данных о цехах")
    else:
        df = pd.DataFrame(workshops).rename(columns={
            'id': 'ID',
            'title': 'Название цеха'
        })
        st.dataframe(df[['ID', 'Название цеха']])
        
        st.subheader("Статистика по загрузке цехов")
        conn = get_db_connection()
        stats = conn.execute('''
            SELECT Цех.id, Цех.title, COUNT(ПродуктЦех.ПродуктКод) as product_count, 
                   SUM(ПродуктЦех.Время) as total_time
            FROM Цех
            LEFT JOIN ПродуктЦех ON Цех.id = ПродуктЦех.ЦехКод
            GROUP BY Цех.id
        ''').fetchall()
        conn.close()
        
        if stats:
            stats_df = pd.DataFrame([dict(row) for row in stats]).rename(columns={
                'id': 'ID',
                'title': 'Цех',
                'product_count': 'Количество продуктов',
                'total_time': 'Общее время работы (мин)'
            })
            st.dataframe(stats_df[['ID', 'Цех', 'Количество продуктов', 'Общее время работы (мин)']])

def main():
    st.sidebar.title("Меню")
    page = st.sidebar.radio(
        "Выберите страницу:", 
        [
            "Просмотр продукции", 
            "Редактирование продукции", 
            "Добавление продукции", 
            "Просмотр цехов"
        ]  
    )  
    
    if page == "Просмотр продукции":
        st.title("Производство мебели - Просмотр продукции")
        products = get_products()
        
        if not products:
            st.warning("Нет данных о продукции")
        else:
            df = pd.DataFrame(products).rename(columns={
                'id': 'ID',
                'title': 'Название продукции',
                'total_time': 'Общее время производства (мин)'
            })
            st.dataframe(df[['ID', 'Название продукции', 'Общее время производства (мин)']])

Даниил, [21.05.2025 4:36]
elif page == "Редактирование продукции":
        st.title("Редактирование продукции")
        products = get_products()
        
        if not products:
            st.warning("Нет продукции для редактирования")
        else:
            product_options = {f"{p['id']} - {p['title']}": p['id'] for p in products}
            selected_product = st.selectbox(
                "Выберите продукт для редактирования:",
                options=list(product_options.keys())
            )
            
            product_id = product_options[selected_product]
            current_title = next(p['title'] for p in products if p['id'] == product_id)
            
            new_title = st.text_input("Новое название продукта:", value=current_title)
            
            if st.button("Сохранить изменения"):
                if new_title.strip() == "":
                    st.error("Название продукта не может быть пустым")
                else:
                    update_product(product_id, new_title)
                    st.success("Продукт успешно обновлен!")
                    st.rerun()

    elif page == "Добавление продукции":
        st.title("Добавление новой продукции")
        new_product = st.text_input("Введите название новой продукции:")
        
        if st.button("Добавить продукт"):
            if new_product.strip() == "":
                st.error("Название продукта не может быть пустым")
            else:
                add_product(new_product)
                st.success(f"Продукт '{new_product}' успешно добавлен!")
                st.rerun()
    
    elif page == "Просмотр цехов":
        show_workshops_page()

if name == "main":
    main()
