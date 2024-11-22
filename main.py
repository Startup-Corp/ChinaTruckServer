from flask import Flask, jsonify, request, send_from_directory
import pandas as pd
import json 
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
# import nltk
# from nltk.stem import PorterStemmer
# from nltk.tokenize import word_tokenize

app = Flask(__name__)
CORS(app)
# nltk.download('punkt') # Загрузка необходимых ресурсов для nltk
# nltk.download('punkt_tab')
# stemmer = PorterStemmer() # Инициализация стеммера

# def stem_words(text):
#     if pd.isna(text):
#         return ""
#     words = word_tokenize(text.lower())
#     return ' '.join([stemmer.stem(word) for word in words])

@app.route('/files/images/<filename>', methods=['GET'])
def serve_image(filename):
    directory_path = 'files/images'
    files = os.listdir(directory_path)
    files = [f for f in files if os.path.isfile(os.path.join(directory_path, f))]
    matching_files = [f for f in files if filename in f]

    if not matching_files:
        return send_from_directory(directory_path, "404.jpg")

    return send_from_directory(directory_path, matching_files[0])

@app.route('/read_excel', methods=['GET'])
def read_excel():
    file_path = 'files/products.xlsx'
    columns = ['number', 'articul', 'name', 'Производитель', 'model', 'Цена', 'Примечание']
    # columns = ['Артикул', 'Номенклатура', 'Количество', 'Сумма']
    
    try:
        # Чтение Excel файла с пропуском строк и заданными заголовками
        df = pd.read_excel(file_path, skiprows=1, names=columns, engine='openpyxl')
    except Exception as e:
        err_message = {'error': f'Error reading Excel file: {str(e)}'}
        print(err_message)
        return jsonify(err_message), 400

    # Проверка наличия необходимых колонок
    if not all(column in df.columns for column in columns):
        return jsonify({'error': 'Missing required columns in Excel file'}), 400

    # Замена NaN на None (будет сериализован как null в JSON)
    df = df.where(pd.notnull(df), None)

    # Замена NaN на 0 для всех необходимых колонок
    df['articul'] = df['articul'].fillna('')  # Заменяем NaN в "Артикул" на пустую строку
    df['Производитель'] = df['Производитель'].fillna('')  # Заменяем NaN в "Примечание" на под заказ
    df['Цена'] = df['Цена'].fillna(0)  # Заменяем NaN в "Сумма" на 0
    df['Примечание'] = df['Примечание'].fillna('под заказ')  # Заменяем NaN в "Примечание" на под заказ

    # Добавление колонки "stemed" с преобразованными названиями
    # df['stemed'] = df['name'].apply(stem_words)

    # Извлечение данных
    data = df[columns].to_dict(orient='records')

    # Возврат данных с отключением экранирования не-ASCII символов
    response = app.response_class(
        response=json.dumps(data, ensure_ascii=False),
        status=200,
        mimetype='application/json'
    )
    return response


# Функция для отправки письма
def send_email(sender_email, sender_password, receiver_email, subject, body):
    try:
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        print("Подключение к SMTP серверу...")

        with smtplib.SMTP("smtp.mail.ru", 587) as server:
            server.starttls()
            print("Успешно установлено TLS соединение.")
            
            # Логирование процесса авторизации
            print(f"Авторизация под {sender_email}...")
            server.login(sender_email, sender_password)
            print("Успешная авторизация.")
            
            # Отправка письма
            print(f"Отправка письма на {receiver_email}...")
            server.sendmail(sender_email, receiver_email, message.as_string())
            print("Письмо успешно отправлено.")

    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")

# Обработка заказа
@app.route('/submit_order', methods=['POST'])
def submit_order():
    try:
        data = request.json  # Получаем данные от клиента (телефон и товары)
        phone = data.get('phone')
        namePerson = data.get('name')
        cart = data.get('cart')

        print("Формирование данных заказа...")

        print(namePerson)
        # Формируем текст письма
        order_details = f" Имя:{namePerson}\n\nТелефон: {phone}\n\nТовары:\n"
        total_price = 0

        for item in cart:
            item_total = item['price'] * item['quantity']
            total_price += item_total
            order_details += f"{item['name']} (Артикул: {item['id']}) - {item['quantity']} шт. - {item_total} руб.\n"

        order_details += f"\nОбщая сумма: {total_price} руб."

        print("Попытка отправить письмо с данными заказа...")

        # Отправляем письмо
        sender_email = "kulzhenya11@mail.ru"
        sender_password = "h5BEUUvAcENd6GujJMzn"
        receiver_email = "kulzhenya11@mail.ru"
        subject = "Новый заказ"
        
        # Отправка письма
        send_email(sender_email, sender_password, receiver_email, subject, order_details)

        print("Заказ успешно отправлен по email.")

        return jsonify({"message": "Order submitted successfully"})

    except Exception as e:
        print(f"Ошибка при обработке заказа: {e}")
        return jsonify({"message": "Ошибка при отправке заказа"}), 500


if __name__ == '__main__':
    app.run(port=5000)
