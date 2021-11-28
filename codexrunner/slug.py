from django.template.defaultfilters import slugify as django_slugify

alphabet = {
    'а': 'a',
    'б': 'b',
    'в': 'v',
    'г': 'g',
    'д': 'd',
    'е': 'e',
    'ё': 'yo',
    'ж': 'zh',
    'з': 'z',
    'и': 'i',
    'й': 'j',
    'к': 'k',
    'л': 'l',
    'м': 'm',
    'н': 'n',
    'о': 'o',
    'п': 'p',
    'р': 'r',
    'с': 's',
    'т': 't',
    'у': 'u',
    'ф': 'f',
    'х': 'kh',
    'ц': 'ts',
    'ч': 'ch',
    'ш': 'sh',
    'щ': 'shch',
    'ы': 'i',
    'э': 'e',
    'ю': 'yu',
    'я': 'ya',
}


def slugify(input_string: str):
    """
    Метод для выполнения транслита
    :param input_string: исходная строка
    :return: транслит исходной строки
    """
    return django_slugify(''.join(alphabet.get(word, word) for word in input_string.lower()))
