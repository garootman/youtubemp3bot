def drilldown(obj, drillist):
    """
    Функция для последовательного извлечения элементов из JSON-подобных структур.

    :param obj: JSON-подобный объект (словарь или список).
    :param drillist: Список ключей для последовательного извлечения значений.
    :return: Извлеченное значение или None, если ключ не найден.
    """
    if not obj or not drillist:
        return obj
    for key in drillist:
        try:
            obj = obj[key]
        except (KeyError, IndexError, TypeError):
            return None
    return obj


drilldown({}, "a") == None
