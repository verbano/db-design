# Система - аналог Pastebin
Полнофункциональная инфраструктура базы данных с мониторингом, репликацией и автоматизацией.

## Особенности

- **Проектирование**: Нормализованная схема БД (3NF) для платформы обмена кодом/текстом
- **Развертывание**: Docker-контейнеризация с автоматическими миграциями и сидированием тестовыми данными
- **Мониторинг**: Prometheus + Grafana для сбора и визуализации метрик
- **Оптимизация**: Специализированные индексы для ускорения поиска и аналитических запросов
- **Отказоустойчивость**: Полный стек Patroni + etcd + HAProxy с автоматическим failover
- **Бэкапы**: Автоматическое резервное копирование с retention policy
- **Безопасность**: Ролевая модель доступа с групповыми политиками
- **Миграции**: Протестированные идемпотентные миграции с up/down скриптами
- **Нагрузочное тестирование**: Сервис для имитации реальной нагрузки и анализа производительности
---

## Функциональные требования системы аналога Pastebin

#### **1. Управление пользователями**
- **1.1 Регистрация и аутентификация:**
  - Пользователь может зарегистрироваться, указав логин, email, пароль.
  - Пользователь может войти в систему через логин/email и пароль.
  - Система поддерживает сессии.
- **1.2 Восстановление пароля:**
  - Пользователь может запросить сброс пароля через email со специальной одноразовой ссылкой.
  - Ссылка для сброса пароля действительна только в течение ограниченного времени.
- **1.3 Профиль пользователя:**
  - Пользователь может редактировать свой профиль (логин, email, аватар).
  - Пользователь может просматривать список своих паст, комментариев и экспортов.

---

#### **2. Управление пастами**
- **2.1 Создание и редактирование:**
  - Пользователь может создать пасту с текстом, указав срок жизни, уровень приватности (public/private).
  - При создании пасты можно опционально указать язык подсветки, категорию, теги, папку.
  - Автор пасты может редактировать или удалить свою пасту.
  - Автор пасты может редактировать содержание пасты.
  - Автор пасты может редактировать настройки пасты (язык подсветки, срок жизни, уровень приватности, категорию, теги)
- **2.2 Доступ:**
  - Публичные пасты доступны всем пользователям.
  - Приватные пасты доступны только автору.
- **2.3 Срок жизни:**
  - Пасты автоматически удаляются по истечении указанного срока.
  - Пользователь может задать срок жизни (например, 1 день, 1 неделя, бессрочно).

---

#### **3. Теги и категории**
- **3.1 Теги:**
  - Пользователь может добавлять к пастам произвольные теги (например, "код", "ошибка").
  - Количество добавляемых тегов должно быть не более 10.
  - Теги можно фильтровать и искать по ним публичную пасту.
- **3.2 Категории:**
  - Пользователь может выбрать для пасты одну из предустановленных категорий.

---

#### **4. Комментарии и взаимодействие**
- **4.1 Комментирование:**
  - Пользователи могут оставлять комментарии к публичным пастам.
  - Автор пасты может удалять комментарии.
- **4.2 Уведомления:**
  - Автор пасты могут получать уведомления, например при новом комментарии, лайке, жалобе.
  - Уведомления отображаются в личном кабинете и могут быть помечены как прочитанные.

---

#### **5. Совместная работа**
- **5.1 Предложение изменений:**
  - Любые пользователи могут предлагать изменения (pull request) к пасте.
  - Автор принимает или отклоняет изменения.
  - В случае принятия оригинальная паста заменяется предложенной.
  - Изменения имеют статус (pending/approved/rejected).
- **5.2 Комментирование:**
  - Авторы оригинальной и измененной пасты могут оставлять комментарии к измененной пасте.

---

#### **6. Управление папками**
- **6.1 Создание папок:**
  - Пользователь может создавать папки для группировки паст.
- **6.2 Добавление паст в папки:**
  - Пользователь может добавлять пасты в несколько папок одновременно.

---

#### **7. Шаблоны**
- **7.1 Создание шаблонов:**
  - Пользователь может сохранять часто используемые пасты как шаблоны.
  - Шаблоны доступны только автору.
- **7.2 Использование шаблонов:**
  - При создании пасты можно выбрать шаблон для автоматической подстановки текста.

---

#### **8. Экспорт паст**
- **8.1 Форматы экспорта:**
  - Пользователь может экспортировать пасту в PDF, Markdown, Word и другие форматы.
- **8.2 История экспорта:**
  - Система сохраняет историю экспортов, включая статус (success/failed), формат, дату, название паста.

---

#### **9. Модерация и отчеты**
- **9.1 Жалобы:**
  - Пользователи могут жаловаться на пасты, указав причину.
  - Модераторы просматривают жалобы и меняют статус (решено/в обработке).
- **9.2 Блокировка контента:**
  - Модераторы могут удалять пасты, нарушающие правила.

---

#### **10. Оценки и голосование**
- **10.1 Голосование:**
  - Пользователи могут оценивать пасты (лайки).
  - Один пользователь может проголосовать за пасту только один раз.

---

#### **11. Безопасность и сессии**
- **11.1 Управление сессиями:**
  - Пользователь может просматривать активные сессии и завершать их.
  - Сессии автоматически завершаются по истечении срока действия.

---

#### **12. Аналитика и отслеживание**
- **12.1 Статистика:**
  - Пользователи видят количество лайков пасты.
  - Автор видит список пользователей, лайкнувших пасту.
  - Пользователи видят количество просмотров пасты.

---

### ER диаграмма

```plantuml
skinparam linetype ortho
skinparam nodesep 50
skinparam ranksep 50
hide empty members

entity users {
  *id: SERIAL
  --
  username: VARCHAR(50)
  email: VARCHAR(100)
  password_hash: VARCHAR(255)
  avatar_url: VARCHAR(255)
  created_at: TIMESTAMP
  updated_at: TIMESTAMP
}

entity user_sessions {
  *id: SERIAL
  --
  ~user_id: INT
  session_token: VARCHAR(255)
  created_at: TIMESTAMP
  expires_at: TIMESTAMP
  ip_address: VARCHAR(45)
  user_agent: TEXT
}

entity password_reset_tokens {
  *id: SERIAL
  --
  ~user_id: INT
  token: VARCHAR(255)
  expires_at: TIMESTAMP
  used: BOOLEAN
}

entity pastes {
  *id: SERIAL
  --
  ~user_id: INT
  object_key: VARCHAR(512)
  name: VARCHAR(255)
  language: VARCHAR(50)
  privacy_level: VARCHAR(20)
  expiration: TIMESTAMP
  ~category_id: INT
  created_at: TIMESTAMP
  updated_at: TIMESTAMP
}

entity paste_views {
  *id: SERIAL
  --
  ~paste_id: INT
  ~user_id: INT
  viewed_at: TIMESTAMP
  ip_address: VARCHAR(45)
}

entity paste_proposals {
  *id: SERIAL
  --
  ~original_paste_id: INT
  proposed_content: TEXT
  status: VARCHAR(20)
  ~created_by: INT
  created_at: TIMESTAMP
  resolved_at: TIMESTAMP
}

entity comments {
  *id: SERIAL
  --
  ~user_id: INT
  ~paste_id: INT
  content: TEXT
  created_at: TIMESTAMP
  ~parent_comment_id: INT
}

entity likes {
  *user_id: INT
  *paste_id: INT
  --
  created_at: TIMESTAMP
}

entity tags {
  *id: SERIAL
  --
  name: VARCHAR(50)
}

entity paste_tags {
  *paste_id: INT
  *tag_id: INT
}

entity categories {
  *id: SERIAL
  --
  name: VARCHAR(50)
  description: TEXT
}

entity folders {
  *id: SERIAL
  --
  ~user_id: INT
  name: VARCHAR(100)
  created_at: TIMESTAMP
}

entity paste_folders {
  *paste_id: INT
  *folder_id: INT
}

entity exports {
  *id: SERIAL
  --
  ~paste_id: INT
  ~user_id: INT
  ~format_id: INT
  paste_name: VARCHAR(255)
  created_at: TIMESTAMP
}

entity export_formats {
  *id: SERIAL
  --
  name: VARCHAR(20)
  mime_type: VARCHAR(100)
  file_extension: VARCHAR(10)
}

entity export_logs {
  *id: SERIAL
  --
  ~export_id: INT
  status: VARCHAR(20)
  error_message: TEXT
  created_at: TIMESTAMP
}

entity paste_templates {
  *id: SERIAL
  --
  ~user_id: INT
  name: VARCHAR(100)
  content: TEXT
  created_at: TIMESTAMP
}

entity reports {
  *id: SERIAL
  --
  ~paste_id: INT
  ~reporter_id: INT
  reason: TEXT
  status: VARCHAR(20)
  resolved_at: TIMESTAMP
}

entity notifications {
  *id: SERIAL
  --
  ~user_id: INT
  ~type_id: INT
  message: TEXT
  related_id: INT
  is_read: BOOLEAN
  created_at: TIMESTAMP
  delivery_status: VARCHAR(20)
}

entity notification_types {
  *id: SERIAL
  --
  name: VARCHAR(50)
}

entity proposal_comments {
  *id: SERIAL
  --
  ~proposal_id: INT
  ~user_id: INT
  content: TEXT
  created_at: TIMESTAMP
}

users ||--o{ user_sessions
users ||--o{ password_reset_tokens
users ||--o{ pastes
users ||--o{ folders
users ||--o{ paste_templates
users ||--o{ comments
users ||--o{ paste_views
users ||--o{ paste_proposals
users ||--o{ exports
users ||--o{ reports
users ||--o{ likes

pastes }o--|| categories
pastes ||--o{ comments
pastes ||--o{ paste_views
pastes ||--o{ paste_proposals
pastes ||--o{ exports
pastes ||--o{ reports
pastes ||--o{ likes

pastes }o--o{ paste_tags
tags }o--o{ paste_tags
pastes }o--o{ paste_folders
folders }o--o{ paste_folders

exports }o--|| export_formats
exports ||--o{ export_logs

notification_types ||--o{ notifications

paste_proposals ||--o{ proposal_comments

categories ||--o{ pastes

comments ||--o{ comments
```
