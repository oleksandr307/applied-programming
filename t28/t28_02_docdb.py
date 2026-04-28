import json
import copy


class Collection:
    '''Клас для роботи з колекцією JSON-документів.

       Поля:
       self.documents - список документів (словників)
       self.next_id - наступний унікальний ідентифікатор
    '''

    def __init__(self):
        self.documents = []
        self.next_id = 1

    def add(self, doc):
        '''Додає документ до колекції.

           Повертає ідентифікатор нового документа.
        '''
        new_doc = copy.deepcopy(doc)
        new_doc["id"] = self.next_id
        self.next_id += 1
        self.documents.append(new_doc)
        return new_doc["id"]

    def get_all(self):
        '''Повертає список усіх документів.'''
        return self.documents

    def delete_by_id(self, doc_id):
        '''Видаляє документ за ідентифікатором.

           Повертає True, якщо документ видалено, інакше False.
        '''
        for i, doc in enumerate(self.documents):
            if doc.get("id") == doc_id:
                del self.documents[i]
                return True
        return False

    def delete_by_condition(self, field, operator, value):
        '''Видаляє документи, що задовольняють умову.

           Повертає кількість видалених документів.
        '''
        from t28_02_queries import QueryEngine
        qe = QueryEngine(self)
        to_delete = qe.find(field, operator, value)
        count = len(to_delete)
        for doc in to_delete:
            self.documents.remove(doc)
        return count

    def update_by_id(self, doc_id, field, new_value):
        '''Оновлює поле field документа за ідентифікатором.

           Повертає True, якщо документ оновлено, інакше False.
        '''
        for doc in self.documents:
            if doc.get("id") == doc_id:
                self._set_nested_field(doc, field, new_value)
                return True
        return False

    def update_by_condition(self, cond_field, operator, cond_value, field, new_value):
        '''Оновлює поле field для документів, що задовольняють умову.

           Повертає кількість оновлених документів.
        '''
        from t28_02_queries import QueryEngine
        qe = QueryEngine(self)
        to_update = qe.find(cond_field, operator, cond_value)
        for doc in to_update:
            self._set_nested_field(doc, field, new_value)
        return len(to_update)

    def _set_nested_field(self, doc, field, value):
        '''Встановлює значення вкладеного поля в документі.'''
        keys = field.split(".")
        current = doc
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value

    def _get_nested_value(self, doc, field):
        '''Отримує значення вкладеного поля з документа.

           Якщо поля немає, повертає None.
        '''
        keys = field.split(".")
        current = doc
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return None
            current = current[key]
        return current

    def save(self, filename):
        '''Зберігає колекцію у файл.'''
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.documents, f, indent=4, ensure_ascii=False)

    def load(self, filename):
        '''Завантажує колекцію з файлу.'''
        with open(filename, "r", encoding="utf-8") as f:
            self.documents = json.load(f)
        if self.documents:
            max_id = max(doc.get("id", 0) for doc in self.documents)
            self.next_id = max_id + 1
        else:
            self.next_id = 1
