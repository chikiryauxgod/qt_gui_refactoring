# Чек-лист интеграции нового GUI в electroerosion

  
## 0. Выбрать режим запуска


- `stub mode` для текущей разработки без реального железа.

- `legacy backend mode` если нужно подключить существующий backend из `electroerosion`.

  

Рекомендация на текущем этапе: сначала поднять `stub mode`, потом отдельно включать `legacy backend mode`.

  

## 1. Зафиксировать одно окружение Python

  

- Использовать Python `3.12.x`.

- Не смешивать одновременно два разных venv для одного запуска GUI.

- Базовое окружение брать от `qt_gui_refactoring`, потому что новый GUI проверен именно на нём.

  

Команды:

  

```bash

cd /home/lew/prog/qt_gui_refactoring

python3 -m venv .venv

. .venv/bin/activate

pip install -r requirements.txt

```

  

Если нужен именно старый backend из `electroerosion`, дополнительно потребуется `pyserial`.

  

## 2. Проверить новый GUI отдельно

  

```bash

cd /home/lew/prog/qt_gui_refactoring

QT_QPA_PLATFORM=offscreen MPLCONFIGDIR=/tmp/mpl .venv/bin/pytest -q \

project/tests/MainWindow \

project/tests/ErosionProcessTab \

project/tests/AxisControlWidget

```

Ожидаемый результат: тесты проходят.
  

## 3. Понять конфликтующие зависимости

  

Сейчас между проектами уже есть расхождения:

  

- `PySide6`: refactoring `6.6.1`, electroerosion `6.10.0`

- `numpy`: refactoring `1.26.4`, electroerosion `2.2.6`

- `matplotlib`: refactoring `3.8.2`, electroerosion `3.10.7`

- `opencv-python`: refactoring `4.9.0.80`, electroerosion `4.12.0.88`

- в `electroerosion` есть `pyserial`, а в refactoring-окружении он пока не заявлен

  

Практическое правило:

  

- для запуска нового GUI сначала использовать зависимости из `qt_gui_refactoring`

- старый backend подключать постепенно

- не копировать старые `requirements.txt` поверх новых

  

## 4. Запускать новый GUI из electroerosion через мост

  

В `qt_gui_refactoring` уже есть модуль:

  

- `project/src/integration/electroerosion_bridge.py`

  

Он делает две вещи:

  

- пытается загрузить `electroerosion` backend из старого проекта

- если backend не поднялся, автоматически падает обратно на локальные заглушки

  

## 5. Добавить тонкий launcher в проект electroerosion

  

Создать файл `/home/lew/prog/electroerosion/electroerosion/new_gui.py`:

  

```python

from pathlib import Path

import sys

  

REF_GUI_ROOT = Path("/home/lew/prog/qt_gui_refactoring/project")

LEGACY_ROOT = Path(__file__).resolve().parent

  

if str(REF_GUI_ROOT) not in sys.path:

sys.path.insert(0, str(REF_GUI_ROOT))

  

from src.integration.electroerosion_bridge import run_with_legacy_backend

  
  

if __name__ == "__main__":

raise SystemExit(run_with_legacy_backend(LEGACY_ROOT))

```

  

## 6. Первый запуск сделать в stub mode

  

Если legacy backend не готов, GUI всё равно должен открыться на заглушках.

  

Команда:

  

```bash

cd /home/lew/prog/electroerosion/electroerosion

QT_QPA_PLATFORM=offscreen MPLCONFIGDIR=/tmp/mpl \

/home/lew/prog/qt_gui_refactoring/.venv/bin/python new_gui.py

```

  

Для обычного запуска с экраном `QT_QPA_PLATFORM=offscreen` не нужен.

  

## 7. Подключать legacy backend только после двух проверок

  

- установлен `pyserial`

- запуск идёт из директории `/home/lew/prog/electroerosion/electroerosion`, потому что старый backend читает `robot_6_axis.urdf` относительным путём

  

Если этих условий нет, мост автоматически уйдёт в stub mode.

  

## 8. Что проверить руками после запуска

  

- окно открывается

- вкладка процесса электроэрозии отображается

- вкладка сервисного управления отображается

- кнопки X/Y/Z двигают координаты без падения

- загрузка `.gcode` обновляет информацию и 3D-визуализацию

- запуск процесса меняет статус

- пауза и стоп не приводят к исключению

  

## 9. Когда переходить со stub на реальный backend

  

Переходить только когда:

  

- есть рабочее окружение с `pyserial`

- подтверждено, что старый `electoerosion.py` импортируется без ошибок

- решено, на каких версиях `PySide6/numpy/matplotlib/opencv` живёт объединённый проект

  

До этого безопаснее оставлять GUI на stub-классах.

## 10. Текущий статус интеграции

На текущий момент уже подтверждено:

- новый GUI запускается из `/home/lew/prog/electroerosion/electroerosion/new_gui.py`
- bridge из `qt_gui_refactoring` подключается корректно
- `legacy backend` загружается
- при отсутствии `/dev/ttyUSB0` и `/dev/ttyACM0` backend уходит в штатный режим эмуляции
- ошибки `MainWindow.X0/Y0/Z0` и `lambda checked` исправлены

Это означает, что основной риск миграции уже закрыт: новый GUI не просто импортируется, а реально живёт поверх старого backend.

## 11. Финальный smoke-check на 10 минут

Выполнять после запуска:

```bash
cd /home/lew/prog/electroerosion/electroerosion
/home/lew/prog/qt_gui_refactoring/.venv/bin/python new_gui.py
```

### 11.1. Запуск

- Ожидаемо открывается окно без traceback.
- В консоли допустимы сообщения про отсутствие `/dev/ttyUSB0` и `/dev/ttyACM0`.
- В консоли допустимы предупреждения OpenCV про камеру, если камера не подключена.

### 11.2. Базовая навигация

- Открываются обе вкладки.
- Переключение между вкладками не вызывает ошибок.
- Закрытие окна не вызывает traceback.

### 11.3. Проверка возврата в ноль

- Нажать `Вернуться в нулевое положение` во вкладке процесса.
- Нажать `Вернуться в нулевое положение` во вкладке сервисного управления.
- Ожидаемо: координаты возвращаются к `X=430`, `Y=0`, `Z=277`, traceback нет.

### 11.4. Проверка XYZ

- Нажать `+0.1`, `-0.1`, `+1.0` для `X`, `Y`, `Z`.
- Ожидаемо: значения обновляются, окно не падает, в backend нет исключений.

### 11.5. Проверка суставов

- Изменить `J0` и `J1` на небольшой угол.
- Проверить кнопки `+` и `−`.
- Ожидаемо: значения обновляются, traceback нет.

### 11.6. Проверка G-code

- Загрузить тестовый `.gcode`.
- Ожидаемо:
- появляется информация о файле
- строится 3D-визуализация
- переход по шагам интерфейса работает

### 11.7. Проверка процесса

- Нажать `Запуск`.
- Затем `Пауза`.
- Затем `Продолжить`.
- Затем `Стоп`.
- Ожидаемо: статус процесса меняется без traceback.

### 11.8. Проверка эрозии и помп

- Во вкладке сервисного управления нажать кнопки эрозии и воды.
- Проверить отдельные помпы.
- Ожидаемо: команды проходят, traceback нет.

### 11.9. Проверка логов

- Во время запуска процесса и сервисных действий посмотреть, попадают ли сообщения в текстовое поле логов.
- Ожидаемо: лог не пустой и обновляется во время действий.

## 12. Что остаётся после smoke-check

Если все пункты из раздела 11 проходят, остаются уже не аварийные задачи, а доводка:

- решить, как обрабатывать отсутствие камеры без шумных сообщений
- зафиксировать финальные версии зависимостей
- обновить документацию по запуску без железа и с железом
- решить, считать ли старый `qt_interface.py` legacy-only
