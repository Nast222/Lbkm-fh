import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json

# --- Настройки ---
API_KEY = "ВАШ_API_КЛЮЧ"  # Замените на свой ключ с exchangerate-api.com
HISTORY_FILE = "history.json"
# -------------------

def get_rate(from_cur, to_cur):
    """Получает курс обмена между двумя валютами."""
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{from_cur}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data["result"] == "error":
            raise Exception(data["error-type"])
        return data["conversion_rates"][to_cur]
    except Exception as e:
        messagebox.showerror("Ошибка API", f"Не удалось получить курс: {e}")
        return None

def is_valid_amount(amount):
    """Проверяет, что сумма — положительное число."""
    try:
        value = float(amount)
        return value > 0
    except ValueError:
        return False

def save_history(entry):
    """Сохраняет запись в историю (JSON)."""
    try:
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
    except FileNotFoundError:
        history = []
    history.append(entry)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def load_history():
    """Загружает историю из файла."""
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def update_history_tree(tree):
    """Обновляет таблицу истории в GUI."""
    for i in tree.get_children():
        tree.delete(i)
    for entry in load_history():
        tree.insert("", tk.END, values=(
            entry["from"],
            entry["to"],
            entry["amount"],
            entry["result"]
        ))

def convert():
    """Основная функция конвертации."""
    from_cur = from_currency.get()
    to_cur = to_currency.get()
    amount_str = amount_var.get()

    if not is_valid_amount(amount_str):
        messagebox.showerror("Ошибка ввода", "Сумма должна быть положительным числом.")
        return

    amount = float(amount_str)
    rate = get_rate(from_cur, to_cur)
    
    if rate is not None:
        result = round(amount * rate, 2)
        result_label.config(text=f"Результат: {result} {to_cur}")
        
        # Сохраняем в историю
        save_history({
            "from": from_cur,
            "to": to_cur,
            "amount": amount,
            "result": result,
            "rate": rate,
            "timestamp": "2026-05-01"  # Можно добавить datetime.now().isoformat()
        })
        update_history_tree(history_tree)

def create_ui():
    """Создаёт графический интерфейс."""
    global from_currency, to_currency, amount_var, result_label, history_tree

    root = tk.Tk()
    root.title("Currency Converter")

    # Валюты
    currencies = ["USD", "EUR", "RUB", "GBP", "CNY"]
    
    ttk.Label(root, text="Из:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    from_currency = tk.StringVar(value="USD")
    ttk.Combobox(root, textvariable=from_currency, values=currencies).grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(root, text="В:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    to_currency = tk.StringVar(value="EUR")
    ttk.Combobox(root, textvariable=to_currency, values=currencies).grid(row=1, column=1, padx=5, pady=5)

    # Сумма
    ttk.Label(root, text="Сумма:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    amount_var = tk.StringVar()
    ttk.Entry(root, textvariable=amount_var).grid(row=2, column=1, padx=5, pady=5)

    # Кнопка и результат
    ttk.Button(root, text="Конвертировать", command=convert).grid(row=3, column=0, columnspan=2, pady=10)
    
    result_label = ttk.Label(root, text="Результат: ")
    result_label.grid(row=4, column=0, columnspan=2)

    # Таблица истории
    history_tree = ttk.Treeview(root, columns=("from", "to", "amount", "result"), show="headings")
    history_tree.heading("from", text="Из")
    history_tree.heading("to", text="В")
    history_tree.heading("amount", text="Сумма")
    history_tree.heading("result", text="Результат")
    
    history_tree.grid(row=5, column=0, columnspan=2, padx=5, pady=5)
    
    # Загружаем историю при запуске
    update_history_tree(history_tree)

if __name__ == "__main__":
    create_ui()
