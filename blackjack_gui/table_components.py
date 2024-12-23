import tkinter

BACKGROUND = "#4e9572"
FOREGROUND = "white"


def setup_canvas(root: tkinter.Tk) -> None:
    rect = tkinter.Canvas(
        root,
        bg=BACKGROUND,
        height=100,
        width=80,
        bd=0,
        highlightthickness=0,
        relief="ridge",
    )
    rect.place(x=525, y=485)
    _round_polygon(
        rect,
        [5, 75, 75, 5],
        [5, 5, 90, 90],
        10,
        width=4,
        outline="#bbb500",
        fill=BACKGROUND,
    )


def get_shoe_status(root: tkinter.Tk) -> tkinter.Label:
    shoe_status_container = tkinter.Label(root, borderwidth=0, background="white")
    shoe_status_container.place(x=20, y=30, height=150, width=30)
    shoe_progress = tkinter.Label(
        shoe_status_container, background="black", borderwidth=0, anchor="e"
    )
    shoe_label = tkinter.Label(
        root,
        text="Discard",
        font="12",
        borderwidth=0,
        background=BACKGROUND,
        fg=FOREGROUND,
    )
    shoe_label.place(x=5, y=190)
    return shoe_progress


def get_label(root: tkinter.Tk) -> tkinter.StringVar:
    label_text = tkinter.StringVar(root)
    label = tkinter.Label(
        root,
        textvariable=label_text,
        font="Helvetica 13 bold",
        borderwidth=0,
        background=BACKGROUND,
        fg=FOREGROUND,
    )
    label.place(x=430, y=670)
    return label_text


def _round_polygon(canvas, x, y, sharpness, **kwargs):
    sharpness = max(sharpness, 2)
    ratio_multiplier = sharpness - 1
    ratio_divider = sharpness
    points = []
    for i, _ in enumerate(x):
        points.append(x[i])
        points.append(y[i])
        if i != (len(x) - 1):
            points.append((ratio_multiplier * x[i] + x[i + 1]) / ratio_divider)
            points.append((ratio_multiplier * y[i] + y[i + 1]) / ratio_divider)
            points.append((ratio_multiplier * x[i + 1] + x[i]) / ratio_divider)
            points.append((ratio_multiplier * y[i + 1] + y[i]) / ratio_divider)
        else:
            points.append((ratio_multiplier * x[i] + x[0]) / ratio_divider)
            points.append((ratio_multiplier * y[i] + y[0]) / ratio_divider)
            points.append((ratio_multiplier * x[0] + x[i]) / ratio_divider)
            points.append((ratio_multiplier * y[0] + y[i]) / ratio_divider)
            points.append(x[0])
            points.append(y[0])
    return canvas.create_polygon(points, **kwargs, smooth=tkinter.TRUE)
