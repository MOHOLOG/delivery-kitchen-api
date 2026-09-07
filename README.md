# Авито.Кухня (MVP Backend Service)

Сервис заказа и доставки еды для платформы «Авито». Репозиторий содержит реализацию основного REST API для клиентов и партнеров, а также микросервис-симулятор партнерского заведения.

---

## 📌 Бизнес-сценарии и пользовательский путь (CJM)

Сервис спроектирован на основе ключевых сценариев взаимодействия клиентов и ресторанов-партнеров:
1. **Клиент (Happy Path):** получение актуального меню заведения, выбор доступных позиций и оформление заказа со статусом `created`.
2. **Клиент (Negative Path):** попытка добавления позиции из стоп-листа (is_available = false) с возвратом валидационной ошибки `400 Bad Request`.
3. **Ресторан (Синхронизация):** выгрузка позиций меню на платформу через публичный API.
4. **Ресторан (Обработка заказа):** автоматический опрос новых заказов, перевод в процесс готовки (`cooking`) и фиксация готовности к выдаче (`ready_for_pickup`).

> 📊 Полные интерактивные sequence-диаграммы (Mermaid) для каждого шага вынесены в отдельный документ:  
> 🔗 **[Открыть схемы пользовательских путей (docs/cjm.md)](docs/cjm.md)**

---

## 🏛 Архитектура системы (C4 Model — Level 2)

Система спроектирована по микросервисной архитектуре и состоит из двух независимых сервисов, взаимодействующих по протоколу HTTP через изолированную сеть Docker Compose:

* **API Сервис (Авито.Кухня)** — основной бэкенд на Python (FastAPI). Отвечает за прием клиентских заказов, валидацию позиций в стоп-листах и управление статусами.
* **База данных (SQLite)** — встраиваемое хранилище данных MVP, обеспечивающее персистентность меню, ресторанов и заказов.
* **Сервис Ресторана** — автономный фоновый микросервис на Python. Эмулирует реальное заведение: регистрирует меню, периодически опрашивает новые заказы и переводит их в статус готовности с временной задержкой.

```mermaid
flowchart TB
    %% Определение участников и внешних сервисов
    client["<b>Клиент</b><br/><i>[Person]</i><br/>Пользователь веб-версии сервиса, заказывающий доставку блюд"]
    restaurant["<b>Сервис Ресторана</b><br/><i>[Container: Python-скрипт]</i><br/>Партнерский микросервис: эмуляция кухни, опрос заказов и смена статусов"]

    %% Границы платформы
    subgraph avito ["<b>Контур Авито.Кухня</b> [System Boundary]"]
        api["<b>API Сервис (Авито.Кухня)</b><br/><i>[Container: Python / FastAPI]</i><br/>Основной бэкенд: обработка заказов, валидация остатков и статусы"]
        db[("<b>База данных</b><br/><i>[Container: SQLite]</i><br/>Хранение заведений, меню и заказов")]
    end

    %% Связи и протоколы
    client -->|"1. Просмотр меню, оформление заказов<br/><b>[HTTP / JSON]</b>"| api
    restaurant -->|"2. Синхронизация меню, опрос заказов, смена статусов<br/><b>[HTTP / JSON]</b>"| api
    api -->|"3. Чтение и запись сущностей<br/><b>[SQL]</b>"| db

    %% Стилизация под цвета C4 (синие контейнеры, читаемый контрастный текст)
    style client fill:#08427b,stroke:#073b6f,color:#ffffff
    style restaurant fill:#1168bd,stroke:#0b4884,color:#ffffff
    style api fill:#1168bd,stroke:#0b4884,color:#ffffff
    style db fill:#1168bd,stroke:#0b4884,color:#ffffff
    style avito fill:transparent,stroke:#999999,stroke-dasharray: 5 5,color:#cccccc
```
---

## Схема базы данных

В качестве СУБД на этапе MVP используется SQLite с управлением миграциями через Alembic. 

### ER-диаграмма связей

```mermaid
erDiagram
    RESTAURANTS ||--o{ MENU_ITEMS : "содержит"
    RESTAURANTS ||--o{ ORDERS : "принимает"
    ORDERS ||--|{ ORDER_ITEMS : "состоит из"
    MENU_ITEMS ||--o{ ORDER_ITEMS : "включается в"

    RESTAURANTS {
        int id PK
        string name
        string address
        datetime created_at
    }

    MENU_ITEMS {
        int id PK
        int restaurant_id FK
        string name
        string description
        int price
        bool is_available
    }

    ORDERS {
        int id PK
        int restaurant_id FK
        int client_id
        string delivery_address
        enum status
        int total_price
        datetime created_at
        datetime updated_at
    }

    ORDER_ITEMS {
        int id PK
        int order_id FK
        int menu_item_id FK
        int quantity
        int price_at_order
    }
```

---

### Описание сущностей и таблиц

* **`restaurants`** — заведения, подключенные к платформе:
  * `id` (INTEGER, PK) — уникальный идентификатор заведения.
  * `name` (VARCHAR) — наименование ресторана.
  * `address` (VARCHAR) — фактический адрес.
  * `created_at` (DATETIME) — дата и время подключения к сервису.

* **`menu_items`** — блюда и позиции меню заведений:
  * `id` (INTEGER, PK) — уникальный идентификатор позиции.
  * `restaurant_id` (INTEGER, FK -> `restaurants.id`, `ON DELETE CASCADE`) — привязка блюда к заведению.
  * `name` (VARCHAR) — название блюда.
  * `description` (VARCHAR, NULL) — опциональное описание состава.
  * `price` (INTEGER) — текущая базовая стоимость в копейках.
  * `is_available` (BOOLEAN) — признак доступности для заказа (управление стоп-листом).

* **`orders`** — клиентские заказы:
  * `id` (INTEGER, PK) — номер заказа.
  * `restaurant_id` (INTEGER, FK -> `restaurants.id`, `ON DELETE CASCADE`) — заведение, исполняющее заказ.
  * `client_id` (INTEGER) — идентификатор пользователя (авторизация вынесена за рамки MVP).
  * `delivery_address` (VARCHAR) — адрес доставки.
  * `status` (ENUM) — жизненный цикл заказа (`created`, `cooking`, `ready_for_pickup`, `completed`, `cancelled`).
  * `total_price` (INTEGER) — финальная стоимость заказа в копейках.
  * `created_at` (DATETIME) — метка времени оформления.
  * `updated_at` (DATETIME) — метка времени последней смены статуса.

* **`order_items`** — состав конкретного чека:
  * `id` (INTEGER, PK) — идентификатор позиции в заказе.
  * `order_id` (INTEGER, FK -> `orders.id`, `ON DELETE CASCADE`) — привязка к заказу.
  * `menu_item_id` (INTEGER, FK -> `menu_items.id`, `ON DELETE RESTRICT`) — привязка к исходному блюду из меню.
  * `quantity` (INTEGER) — количество единиц товара.
  * `price_at_order` (INTEGER) — зафиксированная цена единицы товара на момент покупки в копейках.

---

### Архитектурные решения в схеме данных

* **Хранение денежных средств в целых числах (`Integer`):**
  * Все финансовые поля (`price`, `total_price`, `price_at_order`) хранятся в неделимых единицах (копейках). Это исключает погрешности вычислений чисел с плавающей точкой (`Float`/`Double`).
* **Снимок цены (`price_at_order`):**
  * Цена единицы товара фиксируется в `order_items` в момент покупки. Последующие изменения цен рестораном в таблице `menu_items` не искажают исторические данные и финансовую отчетность по ранее выполненным заказам.
* **Стратегии целостности связей (`Foreign Keys`):**
  * `ON DELETE CASCADE` для связей ресторана и блюд/заказов: при удалении тестового заведения из системы автоматически очищаются зависимые позиции меню и заказы.
  * `ON DELETE RESTRICT` для позиций в чеке (`order_items.menu_item_id`): запрещает удаление блюда из базы, если оно уже фигурирует в ранее оформленных заказах пользователей. Для вывода блюда из продажи предусмотрен флаг `is_available = False`.