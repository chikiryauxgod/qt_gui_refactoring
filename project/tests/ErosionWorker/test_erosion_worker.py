from src.erosion_worker.erosion_worker import (
    ErosionController,
    GCodeProcessor,
    ErosionWorker
)
from src.electoerosion import Electroerosion

def test_gcode_processor_progress():
    points = [(0, 0, 0), (1, 1, 1), (2, 2, 2)]
    processor = GCodeProcessor(points, total_time=60)

    processor.current_index = 0
    assert processor.get_progress() == (1 / 3) * 100

    processor.current_index = 1
    assert processor.get_progress() == (2 / 3) * 100

    processor.current_index = 2
    assert processor.get_progress() == 100


def test_gcode_processor_remaining_time():
    processor = GCodeProcessor([(0, 0, 0)], total_time=125)
    assert processor.get_remaining_time(5) == "02:00"


def test_erosion_controller_creation():
    controller = ErosionController(
        erosion_cls=Electroerosion,
        filename="test.nc",
        speed=5
    )

    assert controller.filename == "test.nc"
    assert controller.erosion_instance is not None


def test_erosion_controller_start_stop_no_exception():
    controller = ErosionController(
        erosion_cls=Electroerosion,
        filename="file.nc"
    )

    controller.start_erosion()
    controller.stop_erosion()


def test_erosion_controller_logger_called():
    messages = []

    def logger(msg):
        messages.append(msg)

    controller = ErosionController(
        erosion_cls=Electroerosion,
        filename="file.nc",
        logger=logger
    )

    controller.start_erosion()

    assert len(messages) == 1
    assert "Starting erosion" in messages[0]


def test_erosion_worker_run_no_exception():
    controller = ErosionController(
        erosion_cls=Electroerosion,
        filename="file.nc"
    )

    processor = GCodeProcessor([(0, 0, 0)], total_time=1)
    worker = ErosionWorker(controller, processor)

    worker.run()


def test_erosion_worker_pause_resume():
    controller = ErosionController(Electroerosion)
    processor = GCodeProcessor([], 0)
    worker = ErosionWorker(controller, processor)

    worker.pause()
    assert worker.is_paused is True

    worker.resume()
    assert worker.is_paused is False


def test_erosion_worker_stop():
    controller = ErosionController(Electroerosion)
    processor = GCodeProcessor([], 0)
    worker = ErosionWorker(controller, processor)

    worker.stop()

    assert worker.is_running is False
    assert worker.is_paused is False