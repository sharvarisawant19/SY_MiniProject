import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from PIL import Image, ImageTk
import os

# --- Global Style Variables ---
PRIMARY_COLOR = '#4CAF50'  # Green
SECONDARY_COLOR = '#E8F5E9'  # Light Green
ACCENT_COLOR = '#FF9800'  # Orange
TEXT_COLOR = '#333333'
FONT_LARGE = ('Arial', 24, 'bold')
FONT_MEDIUM = ('Arial', 16, 'bold')
FONT_SMALL = ('Arial', 12)

# --- Map Colors for Legend ---
ROOM_COLOR_CLASSROOM = '#ADD8E6'  # Light Blue
ROOM_COLOR_WASHROOM = '#FFC0CB'  # Pink
ROOM_COLOR_OFFICE = '#90EE90'  # Light Green
ROOM_COLOR_START = '#FFD700'  # Gold (Entrance)

# --- Data Loading Functions ---


def load_staff_data(filename="staff_data.txt"):
    """Loads staff information from a text file."""
    data = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                parts = [p.strip() for p in line.strip().split(',')]
                if len(parts) >= 5:
                    data.append({
                        "Name": parts[0],
                        "Designation": parts[1],
                        "Department": parts[2],
                        "Office Location": parts[3],
                        "Contact Information": parts[4]
                    })
    except FileNotFoundError:
        print(f"Warning: Data file not found: {filename}. Using empty data.")
    return data


def load_timetable(filename="timetable.txt"):
    """Loads classroom timetable data."""
    data = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                parts = [p.strip() for p in line.strip().split(',')]
                if len(parts) == 5:
                    data.append({
                        "Floor": parts[0],
                        "Room": parts[1],
                        "Start": parts[2],
                        "End": parts[3],
                        "Status": parts[4]
                    })
    except FileNotFoundError:
        print(f"Warning: Data file not found: {filename}. Using empty data.")
    return data


# -------------------------------------------------------------
## 🖼 Splash Screen Class (Click to Continue)
# -------------------------------------------------------------
class SplashPage(tk.Frame):
    """Initial screen displaying the institute image, requires a click to proceed."""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg='black')

        self.image_tk = None
        self.image_label = None

        # fallback label & click_label to bind
        self.fallback_label = tk.Label(self, text="Loading UMIT Navigation System...\nClick anywhere to proceed.",
                                       font=('Arial', 20), fg='white', bg='black')
        self.fallback_label.pack(expand=True, fill='both')

        # visually clickable hint at bottom
        self.click_label = tk.Label(self, text="(Click anywhere or on this text to continue)",
                                    font=('Arial', 10), fg='white', bg='black')
        self.click_label.place(relx=0.5, rely=0.95, anchor='s')

        # Bind events
        self.bind("<Configure>", self.initial_draw)
        self.bind("<Button-1>", self.finish_splash)
        self.click_label.bind("<Button-1>", self.finish_splash)
        self.fallback_label.bind("<Button-1>", self.finish_splash)

    def load_splash_image(self, filename, target_width, target_height):
        """Loads and resizes the image to fit the screen."""
        # try multiple candidate filenames
        candidates = [
            filename,
            "splash_screen_image.jpg",
            "Screenshot 2025-11-12 210318.jpg",
            "image_c69122.jpg",
        ]
        original_img = None
        for fn in candidates:
            if fn and os.path.exists(fn):
                try:
                    original_img = Image.open(fn)
                    break
                except Exception:
                    original_img = None

        if original_img is None:
            # No image found
            return None

        # Resize image to fit or cover the window size (maintain aspect)
        ratio = min(target_width / original_img.width, target_height / original_img.height)
        new_width = int(original_img.width * ratio)
        new_height = int(original_img.height * ratio)

        # Use LANCZOS for high-quality downscaling when available
        try:
            resized_img = original_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        except Exception:
            resized_img = original_img.resize((new_width, new_height))

        # Create a full-size black background canvas
        splash_image = Image.new('RGB', (target_width, target_height), 'black')

        # Center the resized image on the black canvas
        offset_x = (target_width - new_width) // 2
        offset_y = (target_height - new_height) // 2

        splash_image.paste(resized_img, (offset_x, offset_y))

        return ImageTk.PhotoImage(splash_image)

    def initial_draw(self, event):
        """Draws the image once the window size is stable."""
        if self.image_tk is None:
            w = max(200, self.winfo_width())
            h = max(200, self.winfo_height())

            if w > 100 and h > 100:
                self.image_tk = self.load_splash_image("splash_screen_image.jpg", w, h)
                # remove fallback only after we have attempted to draw
                try:
                    self.fallback_label.destroy()
                except Exception:
                    pass

                if self.image_tk:
                    self.image_label = tk.Label(self, image=self.image_tk, bg='black')
                    self.image_label.pack(expand=True, fill='both')
                    # ensure the click works on image as well
                    self.image_label.bind("<Button-1>", self.finish_splash)

                # only need the configure handler once
                try:
                    self.unbind("<Configure>")
                except Exception:
                    pass

    def finish_splash(self, event=None):
        """Transition from splash screen to the home page."""
        self.controller.show_frame("HomePage")


# -------------------------------------------------------------
## ⚙ Main Application Class (Updated Size to 1300x1000)
# -------------------------------------------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Campus Navigation & Information System")
        self.geometry("1300x1000")
        self.minsize(900, 700)
        self.configure(bg=SECONDARY_COLOR)

        self.container = tk.Frame(self, bg=SECONDARY_COLOR)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Register frames
        self.frames = {}

        for F in (SplashPage, HomePage, ClassroomNavigation, ClassOccupancy, FeedbackNotice, StaffInfoModule):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Start at splash
        self.show_frame("SplashPage")

    def show_frame(self, page_name):
        """Show a frame for the given page name"""
        frame = self.frames.get(page_name)
        if frame:
            frame.tkraise()
        else:
            print(f"Attempted to show unknown frame: {page_name}")


# -------------------------------------------------------------
# --- Module Frames ---
# -------------------------------------------------------------


class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=SECONDARY_COLOR)
        self.controller = controller

        try:
            img = Image.open("home_icon.png").resize((100, 100))
            self.home_img = ImageTk.PhotoImage(img)
            tk.Label(self, image=self.home_img, bg=SECONDARY_COLOR).pack(pady=(20, 10))
        except Exception:
            tk.Label(self, text="🏠", font=('Arial', 60), bg=SECONDARY_COLOR).pack(pady=(20, 10))

        tk.Label(self, text="USHA MITTAL INSTITUTE OF TECHNOLOGY, SNDT",
                 font=FONT_LARGE, fg='#000080', bg=SECONDARY_COLOR).pack(pady=10)

        button_style = {
            'font': FONT_MEDIUM,
            'bg': PRIMARY_COLOR,
            'fg': 'white',
            'activebackground': '#388E3C',
            'activeforeground': 'white',
            'cursor': 'hand2'
        }

        tk.Button(self, text="📍 Classroom Navigation",
                  command=lambda: self.controller.show_frame("ClassroomNavigation"),
                  **button_style).pack(pady=10, fill='x', padx=150, ipady=5)

        tk.Button(self, text="📊 Class Occupancy Check",
                  command=lambda: self.controller.show_frame("ClassOccupancy"),
                  **button_style).pack(pady=10, fill='x', padx=150, ipady=5)

        tk.Button(self, text="🧑‍💼 Staff/Non-Staff Information",
                  command=lambda: self.controller.show_frame("StaffInfoModule"),
                  **button_style).pack(pady=10, fill='x', padx=150, ipady=5)

        tk.Button(self, text="📝 Feedback or Notice Section",
                  command=lambda: self.controller.show_frame("FeedbackNotice"),
                  **button_style).pack(pady=10, fill='x', padx=150, ipady=5)


class ClassroomNavigation(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=SECONDARY_COLOR)
        self.controller = controller

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        control_panel = tk.Frame(self, bg=SECONDARY_COLOR, width=350)  # Adjusted width
        control_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        control_panel.grid_propagate(False)

        tk.Label(control_panel, text="🗺 Interactive Floor Map", font=FONT_MEDIUM, fg=PRIMARY_COLOR,
                 bg=SECONDARY_COLOR).pack(pady=(0, 15))

        location_types = ["Classroom", "Washroom", "Office"]
        floors = ["1st", "Ground", "2nd", "3rd", "4th", "5th"]
        wings = ["North", "South", "East", "West"]

        self.location_type = tk.StringVar(self, location_types[0])
        self.floor = tk.StringVar(self, floors[0])
        self.wing = tk.StringVar(self, wings[0])
        self.room_id_var = tk.StringVar(self, "")

        tk.Label(control_panel, text="Location Type 🗃:", font=FONT_SMALL, bg=SECONDARY_COLOR,
                 fg=TEXT_COLOR).pack(anchor='w', padx=5, pady=(5, 0))
        ttk.Combobox(control_panel, textvariable=self.location_type, values=location_types, state="readonly",
                     font=FONT_SMALL, width=20).pack(fill='x', padx=5, pady=2)

        tk.Label(control_panel, text="Floor (Map demo is 1st):", font=FONT_SMALL, bg=SECONDARY_COLOR,
                 fg=TEXT_COLOR).pack(anchor='w', padx=5, pady=(5, 0))
        ttk.Combobox(control_panel, textvariable=self.floor, values=floors, state="readonly", font=FONT_SMALL,
                     width=20).pack(fill='x', padx=5, pady=2)

        tk.Label(control_panel, text="Wing:", font=FONT_SMALL, bg=SECONDARY_COLOR, fg=TEXT_COLOR).pack(anchor='w',
                                                                                                          padx=5,
                                                                                                          pady=(5, 0))
        ttk.Combobox(control_panel, textvariable=self.wing, values=wings, state="readonly", font=FONT_SMALL,
                     width=20).pack(fill='x', padx=5, pady=2)

        tk.Label(control_panel, text="Room ID (e.g., N101, optional):", font=FONT_SMALL, bg=SECONDARY_COLOR,
                 fg=TEXT_COLOR).pack(anchor='w', padx=5, pady=(5, 0))
        tk.Entry(control_panel, textvariable=self.room_id_var, font=FONT_SMALL, width=20).pack(fill='x', padx=5,
                                                                                              pady=2)

        tk.Button(control_panel, text="SHOW ROUTE", command=self.find_route, font=FONT_MEDIUM, bg=ACCENT_COLOR,
                  fg='white').pack(pady=15, fill='x', padx=5)

        tk.Label(control_panel, text="Route Instructions:", font=FONT_SMALL, bg=SECONDARY_COLOR,
                 fg=TEXT_COLOR).pack(anchor='w', padx=5, pady=(0, 0))
        self.result_label = tk.Label(control_panel, text="Select criteria and click SHOW ROUTE.",
                                     font=('Arial', 10), fg='darkgreen', bg='#C8E6C9', relief='groove', wraplength=300,
                                     justify=tk.LEFT, padx=10, pady=5)
        self.result_label.pack(fill='x', padx=5, pady=(5, 10))

        map_area_frame = tk.Frame(self, bg=SECONDARY_COLOR)
        map_area_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        map_area_frame.grid_columnconfigure(0, weight=1)
        map_area_frame.grid_rowconfigure(0, weight=1)

        self.map_canvas = tk.Canvas(map_area_frame, bg='white', relief='ridge', bd=2)
        self.map_canvas.grid(row=0, column=0, sticky="nsew")

        # keep a reference for background map image if used
        self.map_background_image = None

        self.map_canvas.bind('<Configure>', lambda e: self.draw_floor_map())

        tk.Button(self, text="← Home", command=lambda: self.controller.show_frame("HomePage"), font=FONT_SMALL,
                  bg='#607D8B', fg='white').grid(row=1, column=0, pady=10, sticky="sw", padx=10)

    def draw_room(self, tag, x1, y1, x2, y2, room_type, label, color):
        """Helper to draw a room and its label."""
        rect = self.map_canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='gray', width=1,
                                                tags=("room", tag, f"{tag}_rect"))

        icon = ""
        if room_type == "Classroom":
            icon = "📖"
        elif room_type == "Washroom":
            icon = "🚻"
        elif room_type == "Office":
            icon = "🏢"
        elif room_type == "Start":
            icon = "🚶"

        self.map_canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2 - 10, text=icon,
                                    font=('Arial', 14, 'bold'), tags=("room_label", tag, f"{tag}_label"))
        self.map_canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2 + 10, text=label,
                                    font=('Arial', 9), tags=("room_label", tag, f"{tag}_label"))

        # bind hover events to rectangle tag (the tag is set on rectangle and texts)
        self.map_canvas.tag_bind(tag, '<Enter>',
                                 lambda e, t=tag, l=label, rt=room_type: self.show_room_info(e, l, rt))
        self.map_canvas.tag_bind(tag, '<Leave>', self.hide_room_info)

    def show_room_info(self, event, label, room_type):
        """Displays room info on hover."""
        self.map_canvas.delete("tooltip")
        x, y = event.x, event.y
        w_box = 180
        h_box = 28
        self.map_canvas.create_rectangle(x + 10, y + 10, x + 10 + w_box, y + 10 + h_box, fill="lightyellow",
                                         outline="black", tags="tooltip")
        text = f"{room_type}: {label}"
        self.map_canvas.create_text(x + 10 + 6, y + 10 + h_box / 2, anchor='w', text=text,
                                    font=('Arial', 9), tags="tooltip")

    def hide_room_info(self, event):
        """Hides room info."""
        self.map_canvas.delete("tooltip")

    def draw_floor_map(self):
        """Draws the structured map for the 1st floor, centered on the canvas."""
        # clear canvas
        self.map_canvas.delete("all")

        w = self.map_canvas.winfo_width()
        h = self.map_canvas.winfo_height()
        if w < 100 or h < 100:
            return

        # Map sizing
        room_w, room_h = 110, 90
        corridor_w = 45
        margin = 30

        # Calculate intrinsic map size
        map_intrinsic_width = (4 * room_w) + (3 * corridor_w)
        map_intrinsic_height = (4 * room_h) + (3 * corridor_w) + room_h + corridor_w

        # Center the map on the canvas
        x_start = max(margin, (w - map_intrinsic_width) // 2)
        y_start = max(margin, (h - map_intrinsic_height) // 2)

        # Define column starting points
        x_c1 = x_start
        x_c2 = x_c1 + room_w + corridor_w
        x_c3 = x_c2 + room_w + corridor_w
        x_c4 = x_c3 + room_w + corridor_w

        # Define row starting points
        y_r1 = y_start
        y_r2 = y_r1 + room_h + corridor_w
        y_r3 = y_r2 + room_h + corridor_w
        y_r4 = y_r3 + room_h + corridor_w
        y_r_office_s1 = y_r4 + room_h + corridor_w

        corridor_fill = '#E0E0E0'
        line_color = 'gray'

        # Vertical Central Corridor
        x_vert_start = x_c2 + room_w / 2 - corridor_w / 2
        x_vert_end = x_c2 + room_w / 2 + corridor_w / 2
        y_vert_end = y_r_office_s1 + room_h

        self.map_canvas.create_rectangle(x_vert_start, y_r1 + room_h,
                                         x_vert_end, y_vert_end,
                                         fill=corridor_fill, outline=line_color, tags="corridor")

        # Horizontal Corridors
        self.map_canvas.create_rectangle(x_c1 + room_w, y_r1 + room_h / 2 - corridor_w / 2, x_c4,
                                         y_r1 + room_h / 2 + corridor_w / 2, fill=corridor_fill, outline=line_color,
                                         tags="corridor")
        self.map_canvas.create_rectangle(x_c1 + room_w, y_r2 + room_h / 2 - corridor_w / 2, x_c4,
                                         y_r2 + room_h / 2 + corridor_w / 2, fill=corridor_fill, outline=line_color,
                                         tags="corridor")
        self.map_canvas.create_rectangle(x_c1 + room_w, y_r3 + room_h / 2 - corridor_w / 2, x_c4,
                                         y_r3 + room_h / 2 + corridor_w / 2, fill=corridor_fill, outline=line_color,
                                         tags="corridor")
        self.map_canvas.create_rectangle(x_c1 + room_w, y_r4 + room_h / 2 - corridor_w / 2, x_c4,
                                         y_r4 + room_h / 2 + corridor_w / 2, fill=corridor_fill, outline=line_color,
                                         tags="corridor")

        # Draw Rooms
        self.draw_room("N101", x_c1, y_r1, x_c1 + room_w, y_r1 + room_h, "Classroom", "N101", ROOM_COLOR_CLASSROOM)
        self.draw_room("N102", x_c2, y_r1, x_c2 + room_w, y_r1 + room_h, "Classroom", "N102", ROOM_COLOR_CLASSROOM)
        self.draw_room("Wash-N", x_c3, y_r1, x_c3 + room_w, y_r1 + room_h, "Washroom", "Wash-N", ROOM_COLOR_WASHROOM)
        self.draw_room("Office-N1", x_c4, y_r1, x_c4 + room_w, y_r1 + room_h, "Office", "Office-N1", ROOM_COLOR_OFFICE)

        self.draw_room("W101", x_c1, y_r2, x_c1 + room_w, y_r2 + room_h, "Classroom", "W101", ROOM_COLOR_CLASSROOM)
        self.draw_room("W102", x_c1, y_r3, x_c1 + room_w, y_r3 + room_h, "Classroom", "W102", ROOM_COLOR_CLASSROOM)
        self.draw_room("E101", x_c4, y_r2, x_c4 + room_w, y_r2 + room_h, "Classroom", "E101", ROOM_COLOR_CLASSROOM)
        self.draw_room("E102", x_c4, y_r3, x_c4 + room_w, y_r3 + room_h, "Classroom", "E102", ROOM_COLOR_CLASSROOM)

        self.draw_room("Entrance", x_c1, y_r4, x_c1 + room_w, y_r4 + room_h, "Start", "Entrance/Stairs", ROOM_COLOR_START)
        self.draw_room("S101", x_c2, y_r4, x_c2 + room_w, y_r4 + room_h, "Classroom", "S101", ROOM_COLOR_CLASSROOM)
        self.draw_room("S102", x_c3, y_r4, x_c3 + room_w, y_r4 + room_h, "Classroom", "S102", ROOM_COLOR_CLASSROOM)
        self.draw_room("Wash-S", x_c4, y_r4, x_c4 + room_w, y_r4 + room_h, "Washroom", "Wash-S", ROOM_COLOR_WASHROOM)

        self.draw_room("Office-S1", x_c2, y_r_office_s1, x_c3 + room_w, y_r_office_s1 + room_h, "Office", "Office-S1",
                       ROOM_COLOR_OFFICE)

        # Waypoints for routing logic
        self.waypoints = {
            "X_CENTER": x_vert_start + corridor_w / 2,

            "Y_NORTH_CORR": y_r1 + room_h / 2,
            "Y_MIDDLE_CORR_2": y_r2 + room_h / 2,
            "Y_MIDDLE_CORR_3": y_r3 + room_h / 2,
            "Y_SOUTH_CORR": y_r4 + room_h / 2,

            "C_NORTH": (x_vert_start + corridor_w / 2, y_r1 + room_h / 2),
            "C_MIDDLE_2": (x_vert_start + corridor_w / 2, y_r2 + room_h / 2),
            "C_MIDDLE_3": (x_vert_start + corridor_w / 2, y_r3 + room_h / 2),
            "C_SOUTH": (x_vert_start + corridor_w / 2, y_r4 + room_h / 2),

            "ENT_S": (x_vert_start + corridor_w / 2, y_r4 + room_h / 2),

            "S_OFFICE_P": (x_vert_start + corridor_w / 2, y_r_office_s1 + room_h / 2),
        }

        # Draw legend last so it's on top of corridors but below route highlight by z-ordering later
        self.draw_legend()

    def draw_legend(self):
        """Draws a legend on the top right of the canvas, ensuring it is positioned relative to the right edge."""
        # remove old legend objects
        self.map_canvas.delete("legend")

        w = self.map_canvas.winfo_width()
        legend_x = w - 180
        legend_y = 40
        item_spacing = 26

        self.map_canvas.create_text(legend_x, legend_y, text="LEGEND", font=('Arial', 10, 'bold'), anchor='w',
                                    tags="legend")

        legend_y += item_spacing
        self.draw_legend_item(legend_x, legend_y, ROOM_COLOR_CLASSROOM, "Classroom", "📖")
        legend_y += item_spacing
        self.draw_legend_item(legend_x, legend_y, ROOM_COLOR_WASHROOM, "Washroom", "🚻")
        legend_y += item_spacing
        self.draw_legend_item(legend_x, legend_y, ROOM_COLOR_OFFICE, "Office", "🏢")
        legend_y += item_spacing
        self.draw_legend_item(legend_x, legend_y, ROOM_COLOR_START, "Start/Stairs", "🚶")
        legend_y += item_spacing
        self.draw_legend_item(legend_x, legend_y, 'green', "Route Path", "🟢")

    def draw_legend_item(self, x, y, color, text, icon=""):
        """Helper to draw a single legend item."""
        self.map_canvas.create_rectangle(x, y - 7, x + 15, y + 7, fill=color, outline='black', tags="legend")
        self.map_canvas.create_text(x + 22, y, text=f"{icon} {text}", font=('Arial', 9), anchor='w', tags="legend")

    def get_room_center(self, tag):
        """Returns the center (x, y) coordinates for a given room tag."""
        coords = self.map_canvas.bbox(f"{tag}_rect")
        if coords:
            x1, y1, x2, y2 = coords
            return (x1 + x2) / 2, (y1 + y2) / 2
        return None

    def highlight_route(self, floor, wing, location_type, specific_room_id=""):
        """Highlights the map path using corridor waypoints."""
        # remove old route overlays but keep map and legend
        self.map_canvas.delete("route_highlight")
        self.map_canvas.delete("destination_highlight")

        # normalize outlines of rooms
        for tag in self.map_canvas.find_withtag("room"):
            # only change rectangles (skip text items)
            if "_rect" in self.map_canvas.gettags(tag):
                try:
                    self.map_canvas.itemconfig(tag, outline='gray', width=1)
                except Exception:
                    pass

        if floor != "1st":
            return

        start_center = self.get_room_center("Entrance")
        if not start_center:
            # if the map hasn't been drawn yet return
            return

        path_points = [start_center, self.waypoints["ENT_S"]]

        destination_tag = None

        if specific_room_id:
            destination_tag = specific_room_id
        else:
            if location_type == "Classroom":
                tag_map = {"North": "N101", "South": "S101", "East": "E101", "West": "W101"}
                destination_tag = tag_map.get(wing)
            elif location_type == "Washroom":
                tag_map = {"North": "Wash-N", "South": "Wash-S"}
                destination_tag = tag_map.get(wing)
            elif location_type == "Office":
                tag_map = {"North": "Office-N1", "South": "Office-S1"}
                destination_tag = tag_map.get(wing)

        final_coord = self.get_room_center(destination_tag)

        if not final_coord:
            self.result_label.config(text="Could not find a valid destination for the selected criteria.", fg='red',
                                     bg='#FFCDD2')
            return

        x_final, y_final = final_coord

        # decide corridor routing by comparing y positions
        if y_final < self.waypoints["Y_MIDDLE_CORR_2"]:
            path_points.extend([
                self.waypoints["C_NORTH"],
                (x_final, self.waypoints["Y_NORTH_CORR"])
            ])
        elif y_final < self.waypoints["Y_MIDDLE_CORR_3"]:
            path_points.extend([
                self.waypoints["C_MIDDLE_2"],
                (x_final, self.waypoints["Y_MIDDLE_CORR_2"])
            ])
        elif y_final < self.waypoints["Y_SOUTH_CORR"]:
            path_points.extend([
                self.waypoints["C_MIDDLE_3"],
                (x_final, self.waypoints["Y_MIDDLE_CORR_3"])
            ])
        elif destination_tag == "Office-S1":
            path_points.append(self.waypoints["S_OFFICE_P"])
        else:
            path_points.append((x_final, self.waypoints["Y_SOUTH_CORR"]))

        path_points.append(final_coord)

        # draw line and destination marker
        self.map_canvas.create_line(path_points, fill='green', width=5, tags="route_highlight", capstyle=tk.ROUND,
                                    joinstyle=tk.ROUND)
        self.map_canvas.create_oval(x_final - 10, y_final - 10, x_final + 10, y_final + 10, fill='green',
                                    outline='white', width=3, tags="destination_highlight")

        # highlight destination rectangle
        rect_id = self.map_canvas.find_withtag(f"{destination_tag}_rect")
        if rect_id:
            try:
                self.map_canvas.itemconfig(rect_id[0], outline='green', width=4)
            except Exception:
                pass

        # ensure route draws on top of legend and rooms by moving to top
        for tag in ("route_highlight", "destination_highlight"):
            try:
                self.map_canvas.tag_raise(tag)
            except Exception:
                pass

    def find_route(self):
        """Generates a mock map route and triggers map highlighting."""
        loc = self.location_type.get()
        flr = self.floor.get()
        wng = self.wing.get()
        specific_room = self.room_id_var.get().strip().upper()

        route_message = f"🗺 Route Generated!\n"
        destination_text = specific_room if specific_room else f"{loc} in the {wng} Wing"
        route_message += f"Destination:\n{destination_text} on the {flr} Floor.\n"

        if flr == "1st":
            route_message += "\nPath: Start at Entrance/Stairs. Follow the GREEN path along the corridors."
        else:
            route_message += f"\nPath: Use the elevator/stairs to reach the {flr} floor. Map not displayed."

        self.result_label.config(text=route_message, fg='darkgreen', bg='#C8E6C9')

        # ensure map is drawn and then highlight route
        self.draw_floor_map()
        self.highlight_route(flr, wng, loc, specific_room)


class ClassOccupancy(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=SECONDARY_COLOR)
        self.controller = controller

        tk.Label(self, text="📊 Real-Time Class Occupancy", font=FONT_LARGE, fg=PRIMARY_COLOR,
                 bg=SECONDARY_COLOR).pack(pady=20)

        self.timetable = load_timetable()
        floors = ["Ground", "1st", "2nd", "3rd", "4th", "5th"]
        self.selected_floor = tk.StringVar(self, floors[0])

        tk.Label(self, text="Select Floor:", font=FONT_MEDIUM, bg=SECONDARY_COLOR, fg=TEXT_COLOR).pack(pady=5)
        ttk.Combobox(self, textvariable=self.selected_floor, values=floors, state="readonly",
                     font=FONT_MEDIUM).pack(pady=5)

        tk.Button(self, text="🔍 Check Occupancy Now", command=self.check_occupancy, font=FONT_MEDIUM, bg=ACCENT_COLOR,
                  fg='white').pack(pady=15)

        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure("Treeview.Heading", font=FONT_MEDIUM, background=PRIMARY_COLOR, foreground="white")
        style.configure("Treeview", font=FONT_SMALL, rowheight=25)

        self.result_tree = ttk.Treeview(self, columns=('Room', 'Status'), show='headings', style="Treeview")
        self.result_tree.heading('Room', text='Room ID')
        self.result_tree.heading('Status', text='Current Status (Active Time)')
        self.result_tree.column('Room', width=150, anchor='center')
        self.result_tree.column('Status', width=600, anchor='center')
        self.result_tree.pack(pady=10, padx=50, fill='x', expand=False)

        self.result_tree.tag_configure('occupied', background='#F44336', foreground='white')
        self.result_tree.tag_configure('vacant', background='#A5D6A7', foreground='black')

        tk.Button(self, text="← Home", command=lambda: self.controller.show_frame("HomePage"), font=FONT_SMALL,
                  bg='#607D8B', fg='white').pack(pady=20)

    def check_occupancy(self):
        """Verifies class schedule and current time to display occupancy."""
        floor = self.selected_floor.get()
        now = datetime.now()
        current_time = now.time()

        for i in self.result_tree.get_children():
            self.result_tree.delete(i)

        rooms_on_floor = sorted(list(set(entry["Room"] for entry in self.timetable if entry["Floor"] == floor)))

        found_rooms = False

        for room in rooms_on_floor:
            found_rooms = True
            is_occupied_now = False
            next_class_start = None
            display_status = "Vacant"

            for entry in self.timetable:
                if entry["Floor"] == floor and entry["Room"] == room:
                    try:
                        start_t = datetime.strptime(entry["Start"], "%H:%M").time()
                        end_t = datetime.strptime(entry["End"], "%H:%M").time()

                        if start_t <= current_time <= end_t:
                            is_occupied_now = True
                            display_status = f"Occupied (Until {entry['End']})"
                            break

                        if start_t > current_time:
                            if next_class_start is None or start_t < next_class_start:
                                next_class_start = start_t

                    except Exception:
                        display_status = "Error/Unknown Time Format"
                        is_occupied_now = True
                        break

            if not is_occupied_now:
                if next_class_start:
                    display_status = f"Vacant (Next Class: {next_class_start.strftime('%H:%M')})"
                else:
                    display_status = "Vacant (No further classes scheduled today)"

            self.result_tree.insert('', tk.END, values=(room, display_status),
                                     tags=('occupied' if is_occupied_now else 'vacant',))

        if not found_rooms:
            messagebox.showinfo("Info", f"No rooms or timetable data found for the {floor} floor.")


class StaffInfoModule(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=SECONDARY_COLOR)
        self.controller = controller
        self.staff_data = load_staff_data()

        tk.Label(self, text="🧑‍💼 Staff Directory", font=FONT_LARGE, fg=PRIMARY_COLOR, bg=SECONDARY_COLOR).pack(
            pady=20)

        search_frame = tk.Frame(self, bg=SECONDARY_COLOR)
        search_frame.pack(pady=10)

        tk.Label(search_frame, text="Search by Name/Department/Office:", font=FONT_SMALL,
                 bg=SECONDARY_COLOR).pack(side=tk.LEFT, padx=5)

        self.search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.search_var, width=40, font=('Arial', 12)).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="🔍 Search", command=self.search_staff, font=FONT_SMALL, bg='#03A9F4',
                  fg='white').pack(side=tk.LEFT, padx=5)

        style = ttk.Style()
        style.configure("Staff.Treeview.Heading", font=FONT_MEDIUM, background=PRIMARY_COLOR, foreground="white")
        style.configure("Staff.Treeview", font=FONT_SMALL, rowheight=25)

        cols = ('Name', 'Designation', 'Department', 'Office Location', 'Contact Information')
        self.staff_tree = ttk.Treeview(self, columns=cols, show='headings', style="Staff.Treeview")
        for col in cols:
            self.staff_tree.heading(col, text=col)
            self.staff_tree.column(col, anchor='center', width=220)

        self.staff_tree.pack(pady=10, padx=10, fill='both', expand=True)

        self.display_staff(self.staff_data)

        tk.Button(self, text="← Home", command=lambda: self.controller.show_frame("HomePage"), font=FONT_SMALL,
                  bg='#607D8B', fg='white').pack(pady=20)

    def display_staff(self, data):
        """Fills the Treeview with staff data."""
        for i in self.staff_tree.get_children():
            self.staff_tree.delete(i)

        for entry in data:
            self.staff_tree.insert('', tk.END, values=(
                entry['Name'],
                entry['Designation'],
                entry['Department'],
                entry['Office Location'],
                entry['Contact Information']
            ))

    def search_staff(self):
        """Filters staff data based on search term (case-insensitive)."""
        search_term = self.search_var.get().strip().lower()

        if not search_term:
            self.display_staff(self.staff_data)
            return

        filtered_data = [entry for entry in self.staff_data if any(search_term in str(value).lower() for key, value in
                                                                  entry.items())]

        self.display_staff(filtered_data)
        if not filtered_data:
            messagebox.showinfo("Search Result", f"No staff found matching '{search_term}'.")


class FeedbackNotice(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=SECONDARY_COLOR)
        self.controller = controller

        tk.Label(self, text="📢 Submit Feedback or Notice", font=FONT_LARGE, fg=PRIMARY_COLOR,
                 bg=SECONDARY_COLOR).pack(pady=20)

        # Input Frame using grid for structure (as seen in screenshot)
        input_frame = tk.Frame(self, bg='white', relief='groove', borderwidth=2, padx=20, pady=20)
        input_frame.pack(padx=10, pady=(10, 40))

        # Row 0: Subject Title
        tk.Label(input_frame, text="Subject:", font=FONT_MEDIUM, bg='white', fg=TEXT_COLOR).grid(row=0, column=0,
                                                                                                 sticky='w', pady=5)
        self.title_entry = tk.Entry(input_frame, font=FONT_SMALL, width=50)
        self.title_entry.grid(row=0, column=1, padx=10, pady=5)

        # Row 1: Details Text Area
        tk.Label(input_frame, text="Details:", font=FONT_MEDIUM, bg='white', fg=TEXT_COLOR).grid(row=1, column=0,
                                                                                                 sticky='nw', pady=5)
        self.details_text = tk.Text(input_frame, width=50, height=8, font=FONT_SMALL, wrap='word')
        self.details_text.grid(row=1, column=1, padx=10, pady=5)

        # Row 2: Submit Button
        tk.Button(input_frame, text="Submit", command=self.submit_feedback, font=FONT_MEDIUM, bg=PRIMARY_COLOR,
                  fg='white').grid(row=2, column=1, pady=20, sticky='e')

        # Home Button
        tk.Button(self, text="← Home", command=lambda: self.controller.show_frame("HomePage"), font=FONT_SMALL,
                  bg='#607D8B', fg='white').pack(pady=20)

    def submit_feedback(self):
        """
        Saves the feedback/notice to a file and clears fields.
        """
        title = self.title_entry.get().strip()
        # Retrieve content from the Text widget
        details = self.details_text.get("1.0", tk.END).strip()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not title or not details:
            messagebox.showerror("Error", "Subject and Details cannot be empty.")
            return

        # Format the data string
        feedback_data = f"[{timestamp}] | Subject: {title} | Details: {details}\n---\n"

        try:
            # Open the log file in append mode
            with open("Feedback_log.txt", "a") as f:
                f.write(feedback_data)

            messagebox.showinfo("Submission Successful", "✅ Thank you! Your feedback/notice has been submitted.")

            # Clear input fields
            self.title_entry.delete(0, tk.END)
            self.details_text.delete("1.0", tk.END)

        except Exception as e:
            messagebox.showerror("Error", f"❌ Could not save feedback: {e}")


# --- Main Execution Block ---
if __name__ == '__main__':
    app = App()
    app.mainloop()
