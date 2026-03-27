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