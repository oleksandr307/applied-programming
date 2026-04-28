class QueryEngine:
    '''Клас для пошуку та агрегації документів у колекції.

       Поля:
       self.collection - об'єкт класу Collection
    '''

    def __init__(self, collection):
        self.collection = collection

    def find(self, field, operator, value):
        '''Шукає документи за умовою.

           Параметри:
           field - поле для пошуку (може бути вкладеним, наприклад "address.city")
           operator - оператор (=, >, <, >=, <=, in, exists)
           value - значення для порівняння

           Повертає список документів, що задовольняють умову.
        '''
        results = []
        for doc in self.collection.get_all():
            doc_value = self.collection._get_nested_value(doc, field)

            if operator == "exists":
                if value.lower() == "true":
                    if doc_value is not None:
                        results.append(doc)
                elif value.lower() == "false":
                    if doc_value is None:
                        results.append(doc)
                continue

            if doc_value is None:
                continue

            if operator == "in":
                if isinstance(doc_value, list):
                    try:
                        parsed_value = self._parse_value(value)
                        if parsed_value in doc_value:
                            results.append(doc)
                    except ValueError:
                        if value in doc_value:
                            results.append(doc)
                continue

            try:
                doc_value = float(doc_value)
                cmp_value = float(value)
            except (ValueError, TypeError):
                doc_value = str(doc_value)
                cmp_value = value

            if operator == "=":
                if doc_value == cmp_value:
                    results.append(doc)
            elif operator == ">":
                if doc_value > cmp_value:
                    results.append(doc)
            elif operator == "<":
                if doc_value < cmp_value:
                    results.append(doc)
            elif operator == ">=":
                if doc_value >= cmp_value:
                    results.append(doc)
            elif operator == "<=":
                if doc_value <= cmp_value:
                    results.append(doc)

        return results

    def aggregate(self, operation, field):
        '''Виконує агрегатну операцію над полем field.

           Параметри:
           operation - операція (count, sum, avg, min, max)
           field - поле для агрегації

           Повертає результат агрегації.
        '''
        values = []
        for doc in self.collection.get_all():
            doc_value = self.collection._get_nested_value(doc, field)
            if doc_value is not None:
                try:
                    values.append(float(doc_value))
                except (ValueError, TypeError):
                    pass

        if operation == "count":
            return len(values)

        if not values:
            raise ValueError(f"Немає числових значень для поля '{field}'.")

        if operation == "sum":
            return sum(values)
        elif operation == "avg":
            return sum(values) / len(values)
        elif operation == "min":
            return min(values)
        elif operation == "max":
            return max(values)
        else:
            raise ValueError(f"Невідома операція: {operation}")

    def group_by(self, field):
        '''Групує документи за значенням поля field.

           Повертає словник, де ключ - значення поля, значення - список документів.
        '''
        groups = {}
        for doc in self.collection.get_all():
            doc_value = self.collection._get_nested_value(doc, field)
            if doc_value is None:
                key = "None"
            else:
                key = str(doc_value)
            if key not in groups:
                groups[key] = []
            groups[key].append(doc)
        return groups

    def _parse_value(self, value):
        '''Допоміжний метод для перетворення рядкового значення.'''
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value
