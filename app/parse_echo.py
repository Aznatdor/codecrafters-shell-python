# =============================================== Parsing functions ===============================

def parse_line(line: str) -> list[str]:
    """
    Разбирает всю строку команды на список токенов,
    правильно обрабатывая одинарные кавычки.

    ПРИМЕРЫ:
    - "ls -l" -> ['ls', '-l']
    - "echo 'hello world'" -> ['echo', 'hello world']
    - "echo 'hello'world" -> ['echo', 'helloworld']
    """
    tokens = []
    current_token = ""
    in_quote = False

    # Используем итератор, чтобы можно было "заглядывать" вперед
    # (хотя в этой версии это не нужно, но это хорошая практика)
    i = 0
    while i < len(line):
        char = line[i]

        if char == "'":
            # Просто переключаем режим "в кавычках"
            in_quote = not in_quote
        
        elif char == ' ' and not in_quote:
            # Пробел вне кавычек - это разделитель токенов
            if current_token:  # Добавляем токен, только если он не пустой
                tokens.append(current_token)
                current_token = ""
        
        else:
            # Любой другой символ (буква, цифра, или пробел ВНУТРИ кавычек)
            # просто добавляется к текущему токену
            current_token += char
        
        i += 1

    # После окончания цикла не забыть добавить последний токен
    if current_token:
        tokens.append(current_token)

    # Обработка незакрытой кавычки (простой вариант)
    if in_quote:
        print("shell: error: unclosed single quote")
        return [] # Возвращаем пустой список в случае ошибки

    return tokens

def main():
    while (rawArgs := input()):
        args = parse_line(rawArgs)
        print(args)


if __name__ == "__main__":
    main()
