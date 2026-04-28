import json
import os
from t28_02_collection import Collection
from t28_02_queries import QueryEngine

MENU = """
Меню:
1  - Додати документ
2  - Видалити документ
3  - Змінити документ
4  - Знайти документи
5  - Агрегація
6  - Групування
7  - Зберегти колекцію
8  - Завантажити колекцію
9  - Показати всі документи
10 - Вийти
"""


def print_documents(docs):
    if not docs:
        print("Документів не знайдено.")
        return
    for doc in docs:
        print(json.dumps(doc, indent=2, ensure_ascii=False))
        print("---")


def main():
    collection = Collection()
    query_engine = QueryEngine(collection)

    while True:
        print(MENU)
        try:
            choice = int(input("Оберіть дію: "))
        except ValueError:
            print("Введіть число.")
            continue

        if choice == 1:
            print("Введіть JSON-документ (без id, він додається автоматично):")
            try:
                doc_str = input()
                doc = json.loads(doc_str)
                doc_id = collection.add(doc)
                print(f"Документ додано. ID: {doc_id}")
            except json.JSONDecodeError:
                print("Помилка: некоректний JSON.")

        elif choice == 2:
            key = input("Видалити за id чи за умовою (id/condition): ")
            if key == "id":
                try:
                    doc_id = int(input("ID документа: "))
                    if collection.delete_by_id(doc_id):
                        print("Документ видалено.")
                    else:
                        print("Документ не знайдено.")
                except ValueError:
                    print("ID має бути числом.")
            elif key == "condition":
                field = input("Поле: ")
                operator = input("Оператор (=, >, <, >=, <=, in, exists): ")
                value = input("Значення: ")
                count = collection.delete_by_condition(field, operator, value)
                print(f"Видалено документів: {count}")
            else:
                print("Невідома опція.")

        elif choice == 3:
            key = input("Змінити за id чи за умовою (id/condition): ")
            field = input("Поле для оновлення: ")
            new_value_str = input("Нове значення (як JSON): ")
            try:
                new_value = json.loads(new_value_str)
            except json.JSONDecodeError:
                new_value = new_value_str

            if key == "id":
                try:
                    doc_id = int(input("ID документа: "))
                    if collection.update_by_id(doc_id, field, new_value):
                        print("Документ оновлено.")
                    else:
                        print("Документ не знайдено.")
                except ValueError:
                    print("ID має бути числом.")
            elif key == "condition":
                cond_field = input("Поле для умови: ")
                operator = input("Оператор (=, >, <, >=, <=, in, exists): ")
                value = input("Значення: ")
                count = collection.update_by_condition(cond_field, operator, value, field, new_value)
                print(f"Оновлено документів: {count}")
            else:
                print("Невідома опція.")

        elif choice == 4:
            field = input("Поле: ")
            operator = input("Оператор (=, >, <, >=, <=, in, exists): ")
            value = input("Значення: ")
            results = query_engine.find(field, operator, value)
            print_documents(results)

        elif choice == 5:
            operation = input("Операція (count, sum, avg, min, max): ")
            field = input("Поле: ")
            try:
                result = query_engine.aggregate(operation, field)
                print(f"Результат: {result}")
            except Exception as e:
                print(f"Помилка: {e}")

        elif choice == 6:
            field = input("Поле для групування: ")
            try:
                groups = query_engine.group_by(field)
                for key, docs in groups.items():
                    print(f"Група '{key}': {len(docs)} документ(ів)")
            except Exception as e:
                print(f"Помилка: {e}")

        elif choice == 7:
            filename = input("Ім'я файлу: ")
            collection.save(filename)
            print(f"Колекцію збережено у файл {filename}")

        elif choice == 8:
            filename = input("Ім'я файлу: ")
            if os.path.exists(filename):
                collection.load(filename)
                print(f"Колекцію завантажено з файлу {filename}")
            else:
                print("Файл не знайдено.")

        elif choice == 9:
            docs = collection.get_all()
            print_documents(docs)

        elif choice == 10:
            print("Завершення роботи.")
            break

        else:
            print("Невірний вибір.")


if __name__ == "__main__":
    main()
