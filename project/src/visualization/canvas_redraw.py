def request_canvas_redraw(canvas) -> None:
    draw_idle = getattr(type(canvas), "draw_idle", None)
    if callable(draw_idle):
        canvas.draw_idle()
        return

    canvas.draw()
