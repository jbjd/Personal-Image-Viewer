"""Classes representing a canvas UI element"""

from tkinter import Canvas, Event, Tk
from tkinter.font import Font  # noqa: TC003

from PIL.ImageTk import PhotoImage

from image_viewer.constants import TEXT_RGB, TkTags
from image_viewer.ui.base import ButtonUIElementBase
from image_viewer.ui.image import ImageUIElement
from image_viewer.utils.os import maybe_truncate_long_name


class CustomCanvas(Canvas):
    """Extended version of tkinter's canvas to support internal methods"""

    __slots__ = (
        "_motion_schedule",
        "_topbar",
        "button_name_to_object",
        "drag_start_x",
        "drag_start_y",
        "file_name_text_id",
        "font",
        "image_display",
        "screen_height",
        "screen_width",
    )

    def __init__(self, master: Tk, background_color: str) -> None:
        super().__init__(master, bg=background_color, highlightthickness=0)
        self.pack(anchor="nw", fill="both", expand=1)

        master.update()  # updates winfo width and height to the current size
        self._motion_schedule: str = ""
        self._topbar: PhotoImage
        self.button_name_to_object: dict[str, ButtonUIElementBase] = {}
        self.file_name_text_id: int = -1
        self.font: Font
        self.image_display = ImageUIElement(None, -1)
        self.screen_width: int = master.winfo_width()
        self.screen_height: int = master.winfo_height()
        self.drag_start_x: int
        self.drag_start_y: int

        self.create_rectangle(
            0,
            0,
            self.screen_width,
            self.screen_height,
            fill=background_color,
            tags=TkTags.BACKGROUND,
        )

        self.bind("<ButtonPress-3>", self._move_from)
        self.bind("<B3-Motion>", self._move_to)

    def _move_from(self, event: Event) -> None:
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def _move_to(self, event: Event) -> None:
        if self._motion_schedule:
            return

        self._motion_schedule = self.after(15, self._drag_image, event)

    def _drag_image(self, event: Event) -> None:
        drag_x: int = event.x - self.drag_start_x
        drag_y: int = event.y - self.drag_start_y
        self.drag_start_x = event.x
        self.drag_start_y = event.y

        bbox: tuple[int, int, int, int] = self.bbox(self.image_display.id)
        # Keep in bounds horizontally
        if bbox[2] + drag_x <= 0:
            drag_x = -bbox[2]
        elif bbox[0] + drag_x >= self.screen_width:
            drag_x = self.screen_width - bbox[0]

        # Keep in bounds vertically
        if bbox[3] + drag_y <= 0:
            drag_y = -bbox[3]
        elif bbox[1] + drag_y >= self.screen_height:
            drag_y = self.screen_height - bbox[1]

        self.move(self.image_display.id, drag_x, drag_y)
        self._motion_schedule = ""

    def create_button(
        self,
        button_object: ButtonUIElementBase,
        name: str,
        x_offset: int,
        y_offset: int,
        image: PhotoImage,
    ) -> int:
        image_id: int = self.create_image(
            x_offset,
            y_offset,
            image=image,
            anchor="nw",
            tag=TkTags.TOPBAR,
            state="hidden",
        )

        self.button_name_to_object[name] = button_object

        return image_id

    def create_topbar(self, topbar_img: PhotoImage) -> None:
        """Creates the topbar and stores it"""
        self._topbar = topbar_img  # save from garbage collector
        self.create_image(
            0, 0, image=topbar_img, anchor="nw", tag=TkTags.TOPBAR, state="hidden"
        )

    def create_name_text(self, x: int, y: int) -> None:
        """Creates text object used to display file name"""
        self.file_name_text_id = self.create_text(
            x, y, fill=TEXT_RGB, anchor="w", font=self.font, tags=TkTags.TOPBAR
        )

    def update_image_display(self, new_image: PhotoImage) -> None:
        """Puts a new image on screen"""
        self.delete(self.image_display.id)

        self.image_display.id = self.create_image(
            self.screen_width >> 1,
            self.screen_height >> 1,
            anchor="center",
            tag=TkTags.BACKGROUND,
            image=new_image,
        )
        self.image_display.image = new_image
        self.tag_raise(TkTags.TOPBAR)
        self.master.update_idletasks()

    def update_existing_image_display(self, new_image: PhotoImage) -> None:
        """Updates existing image on screen with a new PhotoImage"""
        self.itemconfig(self.image_display.id, image=new_image)
        self.image_display.image = new_image
        self.master.update_idletasks()

    def update_file_name(self, new_name: str) -> int:
        """Updates file name. Returns width of new name"""
        expected_width: int = self.font.measure(new_name)
        max_width: int = self.screen_width // 3
        self.itemconfigure(
            self.file_name_text_id,
            text=maybe_truncate_long_name(new_name, expected_width, max_width),
        )
        return self.bbox(self.file_name_text_id)[2]

    def is_widget_visible(self, tag_or_id: str | int) -> bool:
        """Returns bool of if provided tag/id is visible"""
        return self.itemcget(tag_or_id, "state") != "hidden"

    def get_button_id(self, name: str) -> int:
        return self.button_name_to_object[name].id

    def mock_button_click(self, name: str) -> None:
        """Triggers on click event of button programmatically
        passing None as event"""
        button: ButtonUIElementBase = self.button_name_to_object[name]
        button.on_click(None)
        button.on_leave(None)  # Don't make button look hovered by mouse
