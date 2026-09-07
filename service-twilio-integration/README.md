# Сервис интеграции с twilio (service-twilio-integration)

___


*Сервис предназначен для взаимодействия с twilio: узнать баланс аккаунта, купить номер с привязкой к вебхуку для входящего вызова. 
Сервис написан на Python 3.10. С использованием библиотеки fastAPI*

___

<details open>
<summary>Разделы</summary> 

1. [Файлы проекта](#файлы-проекта)
1. [Связанные сервисы](#связанные-сервисы)
1. [Техническое описание](#техническое-описание)
    - [Ключевые кодовые единицы](#ключевые-кодовые-единицы)
    - [Модификация функционала сервиса](#модификация-функционала-сервиса)
1. [Деплой и запуск](#деплой-и-запуск)
1. [Тестирование](#тестирование)
1. [API](#api)
1. [Известные проблемы](#известные-проблемы)
1. [История изменений](#история-изменений)
1. [Ответственные разработчики](#ответственные-разработчики)
1. [Полезные ссылки](#полезные-ссылки)

___

</details>

## Файлы проекта

- [requirements.py](/requirements.txt) - файл с перечислением всех зависимостей для языка Python
- [Dockerfile](/Dockerfile) - Dockerfile, для запуска в докере
- *.env файлы - файлы в которых перечислены переменные для работы программы вместе с их значениями
- [/tests](/tests/) - тесты для сервиса и его компонентов
- [/deployment](/deployment/) - скрипты для деплоя сервиса
- [/scripts](/scripts/) - скрипты для запуска сервиса локально в разных конфигурациях
- [/src](/src) - исходный код сервиса
- [/src/dependencies](/src/dependencies) - dependencies для fastapi (как общие так и бизнесовые)
- [/src/routers](/src/routers) - описание всех endpoints API сервиса
- [/src/schemas](/src/schemas) - pydantic-модели для сущностей с которыми работает сервис
- [/src/services](/src/services) - бизнес-компоненты приложения
- [/src/main.py](/src/main.py) - entrypoint fastapi приложения

## Связанные сервисы

(внешние)

- **twilio** - сервис интегрирован с twilio и взаимодействует с ним с помощью API twilio (
  библиотека twilio). Для доступа к api требуется TWILIO_ACCOUNT_SID и TWILIO_AUTH_TOKEN. Для выполнения некоторых тестовых функций
  также возможно потребуются тестовые TWILIO_ACCOUNT_SID и TWILIO_AUTH_TOKEN.


## Техническое описание

Сервис написан на fastapi и работает как http веб сервер.

### Ключевые кодовые единицы

Бизнес логика интеграций с твилио содержится в файлах директории [/src/services/twilio_service.py](/src/services/twilio_service.py).
Комментарии, при необходимости, в самом коде.

API маршруты лежат в [/src/routers](/src/routers).

Точка входа в приложения в [/src/main.py](/src/main.py)

Переменные окружения которые нужны сервису и используются в пользовательском коде можно посмотреть в
файле [src/config.py](src/config.py).
Также документация есть в самом коде.

### Модификация функционала сервиса

Смотреть в [/src/services](/src/services) и в [/src/routers](/src/routers)

## Деплой и запуск

<details open>
    <summary>Локальный запуск</summary> 

#### В системе:

1) Для запуска локально с использованием инфры запущенной локально (см. директорию [local_infra](scripts/local_infra/))
   из текущей директории выполнить:

```bash
bash scripts/run_service.sh
```

или

```bash
bash scripts/run_service.sh -e local
```

2) Для запуска локально с использованием инфры на стейдже из текущей директории выполнить:

```bash
bash scripts/run_service.sh -e stage
```

3) Для остановки сервиса достаточно отправить в терминал команду ctrl + c

#### В docker-контейнере:

1) Для запуска локально в докере с использованием инфры запущенной локально (см. директорию local_infra) из текущей
   директории выполнить:

```bash
bash scripts/run_service_docker.sh
```

или

```bash
bash scripts/run_service_docker.sh -e local
```

2) Для запуска локально в докере с использованием инфры на стейдже из текущей директории выполнить:

```bash
bash scripts/run_service_docker.sh -e stage
```

3) Для остановки запущенного в докере сервиса выполнить:

```bash
bash scripts/stop_service_docker.sh
```

</details>

<details open>
    <summary>Деплой и запуск на сервере</summary> 

#### На стейдже:

Выполните команду:

```bash
    cd deployment
    bash update_staging.sh
```

#### На препроде:

Выполните команду:

```bash
    command1 arg1 -opt1
```

#### На проде:

Выполните команду:

```bash
    command1 arg1 -opt1
```

</details>

## Тестирование

<details open>
    <summary>Мануальное</summary> 

(empty)
</details>

<details open>
    <summary>Автотесты</summary> 

Для запуска автотестов последовательно выполните команды
### (Пока в проекте нет автотестов)

```bash
    python3.10 -m pip install --upgrade pip
    python3.10 -m pip install -r requirements.txt
    python3.10 -m pytest --verbose -vv
```

</details>

## API

Для просмотра swagger ui последовательно выполните команды

```bash
    python3.10 -m pip install --upgrade pip
    python3.10 -m pip install -r requirements.txt
    python3.10 -m uvicorn src.main:app --host 0.0.0.0 --port 8080
```

После запуска приложения перейдите на http://127.0.0.1:8080/docs и авторизуйтесь (креды смотреть [здесь](src/config.py))
Для использования запросов к календарям следует дополнительно авторизоваться с помощью заголовка.

### Если нет возможности запускать приложение:

То [вот swagger](/openapi.json)
Посмотреть его можно например, с помощью https://editor.swagger.io/

## Известные проблемы

## История изменений

[deleted block]

## Ответственные разработчики

[deleted block]

## Полезные ссылки

- https://fastapi.tiangolo.com/
- https://www.twilio.com/docs/usage/api
- https://www.twilio.com/docs/libraries/reference/twilio-python/index.html
- https://www.twilio.com/docs/iam/connect/quickstart/python

