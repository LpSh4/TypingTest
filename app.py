import tkinter as tk, os, time, random, json
from PIL import Image, ImageTk

def open_json(path):  #read JSON content from a file
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f'Error: {e}')

def dump_json(data, path):
    try:
        with open(path, 'w') as file:
            json.dump(data, path)
    except Exception as e:
        print(f'Error: {e}')

def find_avg(i):
    try:
        return sum(i) / len(i)
    except Exception as e:
        print(f'Error: {e}')
        return 0

def resource_path(relative_path):  #get absolute path
    return os.path.join(os.path.abspath("."), relative_path)

class TypingTestApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1280x720") #Window geometry
        self.root.minsize(800, 400)
        self.sentence = self.get_sentence()
        self.char_dict = self.create_char_dict()  #Create character dictionary
        self.current_index = 0
        self.start_time, self.original_image, self.result_label, self.restart_button = None, None, None, None
        self.last_button = 2
        self.red_line_id = None
        self.flicker_state = 0
        self.flicker_after_id = None  # New: Track the after() ID

        #Configure grids
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        #Configure top navigation pannel
        self.top_frame = tk.Frame(root, bg="#5D3E69", height=84)
        self.top_frame.grid(row=0, column=0, sticky="ew")
        self.top_frame.grid_propagate(False)
        self.create_buttons()

        #Configure main content frame and content
        self.main_frame = tk.Frame(root, bg="#373441")
        self.main_frame.grid(row=1, column=0, sticky="nsew")
        self.text_frame = tk.Frame(self.main_frame, bg="#373441")  # Frame for text display
        self.text_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.show_image()
        self.create_text_grid()  # Create text display grid

        #Configure keys and events
        self.root.bind("<Key>", self.handle_key_press)  # Key summons an event
        self.root.bind("<BackSpace>", self.handle_backspace)  # Backspace handling
        self.root.bind("<Configure>", self.resize_image)  #Resize event
        self.root.bind("<Return>", lambda event: self.restart() if self.restart_button else None)  #Enter restarts

    def create_buttons(self):   #Set up buttons
        button_style = {
            "bg": "#9552AF", "fg": "#C894DC", "bd": 0, "highlightthickness": 0,
            "activebackground": "#B026E7", "activeforeground": "#B026E7"
        }

        #Button 1: 84x84 at (0,0) - Clears everything
        tk.Button(self.top_frame, **button_style, width=84, height=84,
                  command=lambda: self.button_press(1)).place(x=0, y=0, width=84, height=84)
        #Button 2: 84x84 at (213,0) - Restarts test
        tk.Button(self.top_frame, **button_style, width=84, height=84,
                  command=lambda: self.button_press(2)).place(x=213, y=0, width=84, height=84)
        #Button 3: 84x84 at (338,0)
        tk.Button(self.top_frame, **button_style, width=84, height=84,
                  command=lambda: self.button_press(3)).place(x=338, y=0, width=84, height=84)
        #Button 4: 327x84 at (676,0)
        tk.Button(self.top_frame, **button_style, width=327, height=84,
                  command=lambda: self.button_press(4)).place(x=676, y=0, width=327, height=84)
        #Button 5: 84x84 at (1196,0)
        tk.Button(self.top_frame, **button_style, width=84, height=84,
                  command=lambda: self.button_press(5)).place(x=1196, y=0, width=84, height=84)

    def button_press(self, number): #Button press event
        if number == 1 and self.last_button != 1:
            self.destroy_menu(self.last_button)
            self.last_button = 1
            data = open_json(resource_path('./data.json'))
            avgwpm = sum(data[i]['wpm'] for i in data) / len(data)
            avgcpm = sum(data[i]['cpm'] for i in data) / len(data)
            avgaccuracy = sum(data[i]['accuracy'] for i in data) / len(data)
            #CREATE A AVG SESH HERE
            print(f'Average WPM: {avgwpm}\n Average CPM: {avgcpm}\nAverage Accuracy: {avgaccuracy}')

        elif number == 2 and self.last_button != 2: #Start test on button 2
            self.restart()
            self.last_button = 2
        elif number == 3:
            self.destroy_menu(self.last_button)
            self.last_button = 3
        elif number == 4:
            self.destroy_menu(self.last_button)
            self.last_button = 4
        elif number == 5:
            self.destroy_menu(self.last_button)
            self.last_button = 5

    def show_image(self):
        self.image_label = tk.Label(self.main_frame, bg="#373441")  # Label for current letter image
        self.image_label.place(relx=0.0, rely=1.0, anchor="sw")  # Stick to bottom left (relative positioning)

    def create_char_dict(self):  #Create dict for sentence characters
        char_dict = {}
        for i, char in enumerate(self.sentence):
            char_dict[i] = [char, False, None, True]  # [char, correct?, canvas_id, clean]
        #print("Character Dictionary:", {k: v[0] for k, v in char_dict.items()})  #For my stuf
        return char_dict

    def get_sentence(self):  #Get sentence
        difficulty = ''.join([i for i in random.choice(['simple', 'medium', 'hard']) if not i.isdigit()]).lower()
        return open_json(resource_path("garbage - Copy.json"))[f'{difficulty}_{random.randint(1, 33)}']  # Line 5: Load sentence from JSON

    def create_text_grid(self):  #Create text grid
        self.canvas = tk.Canvas(self.text_frame, bg="#373441", highlightthickness=0)
        self.canvas.pack()

        words = self.sentence.split()
        current_x, current_y = 0, 0
        char_index = 0
        max_width = 1000  # Maximum width before wrapping
        font = ("Arial", 25, "bold")  # Font for text

        for word in words:
            word_width = len(word) * 25
            if current_x + word_width > max_width:
                current_x = 0
                current_y += 30

            for char in word:
                text_id = self.canvas.create_text(current_x, current_y,
                                                  text=char, font=font, anchor="nw", fill="#BEA8C7")
                self.char_dict[char_index][2] = text_id
                bbox = self.canvas.bbox(text_id)  # Get bounding box of text
                char_width = bbox[2] - bbox[0]
                current_x += char_width + 2
                char_index += 1

            if char_index < len(self.sentence):
                text_id = self.canvas.create_text(current_x, current_y,
                                                  text=" ", font=font, anchor="nw", fill="#BEA8C7")
                self.char_dict[char_index][2] = text_id
                current_x += 10
                char_index += 1

        self.canvas.update()  # Update canvas to calculate bounds
        canvas_width = self.canvas.bbox("all")[2]
        canvas_height = self.canvas.bbox("all")[3] + 20
        self.canvas.config(width=canvas_width, height=canvas_height)  # Set canvas size

        self.update_letter_image()  #Update image
        self.update_red_line()

    def update_letter_image(self):  #Update current letter image
        if self.current_index < len(self.sentence):
            char = self.sentence[self.current_index].lower()
            try:
                self.original_image = Image.open(f"./content/{char}.png")  # Load image file
                self.resize_image()
            except FileNotFoundError:
                self.image_label.config(image="")

    def resize_image(self, event=None):  #Resize letter image on window resize
        if self.original_image:
            window_width = self.root.winfo_width()  # Get current window width
            window_height = self.root.winfo_height() - 84
            min_dimension = min(window_width, window_height)
            new_size = int(min_dimension * 0.3)  #10% of smallest dimension
            if new_size < 32:  #Enforce minimum size
                new_size = 32
            resized_img = self.original_image.resize((new_size, new_size), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(resized_img)
            self.image_label.config(image=self.photo)  #Update label with new image

    def update_red_line(self):  # Update position of indicator
        if self.red_line_id:
            self.canvas.delete(self.red_line_id)
            # New: Cancel any existing flicker loop
            if self.flicker_after_id is not None:
                self.root.after_cancel(self.flicker_after_id)
                self.flicker_after_id = None

        if self.current_index < len(self.sentence):
            text_id = self.char_dict[self.current_index][2]
            bbox = self.canvas.bbox(text_id)
            if bbox:
                x1, y1, x2, y2 = bbox
                width = x2 - x1

                # Create solid rectangle without outline, 3px height
                self.red_line_id = self.canvas.create_rectangle(
                    x1, y2 - 6, x1 + width, y2-3,
                    fill="#B026E7",  # Initial color
                    outline="",
                    tags="red_line"
                )
                self.canvas.lift(self.red_line_id)
                self.flicker_red_line()  # Start flickering

    def flicker_red_line(self):  #Handle indicator
        if self.red_line_id:
            steps = 200  # Increased steps for smoother transition
            self.flicker_state = (self.flicker_state + 1) % (steps * 2)  # Cycle 0 to 39

            # Calculate intensity (0 to 1 and back)
            if self.flicker_state < steps:
                intensity = self.flicker_state / steps  # Fade from dark to purple
            else:
                intensity = (steps * 2 - self.flicker_state) / steps  # Fade from purple to dark

            # Define the two colors in RGB
            color1 = (0x37, 0x34, 0x41)  # #373441 (dark gray)
            color2 = (0xB0, 0x26, 0xE7)  # #B026E7 (purple)

            #Interpolate between the two colors
            r = int(color1[0] + (color2[0] - color1[0]) * intensity)
            g = int(color1[1] + (color2[1] - color1[1]) * intensity)
            b = int(color1[2] + (color2[2] - color1[2]) * intensity)

            #Format as hex color
            color = f"#{r:02x}{g:02x}{b:02x}"

            self.canvas.itemconfig(self.red_line_id, fill=color)
            #New: Store the after ID and schedule next update
            self.flicker_after_id = self.root.after(50, self.flicker_red_line)

    def handle_key_press(self, event):  #Handle typing input
        if self.current_index >= len(self.char_dict) or event.char == '':
            return
        if self.start_time is None:  #Start timer on first key
            self.start_time = time.time()

        expected_char = self.char_dict[self.current_index][0]
        #print(f'{event.char} Pressed. {expected_char} expected.')
        if event.char == expected_char:  #Correct key pressed
            self.char_dict[self.current_index][1] = True
            self.canvas.itemconfig(self.char_dict[self.current_index][2], fill="green")
        else:  #Wrong key pressed
            self.char_dict[self.current_index][1] = False
            self.canvas.itemconfig(self.char_dict[self.current_index][2], fill="red")

        self.current_index += 1  #Move to next character
        self.update_letter_image()
        self.update_red_line()

        if self.current_index == len(self.char_dict):  #End test if last character
            self.show_results()

    def handle_backspace(self, event):  #Handle backspace
        if self.current_index > 0:
            self.current_index -= 1
            self.char_dict[self.current_index][1] = False
            self.char_dict[self.current_index][3] = False
            self.canvas.itemconfig(self.char_dict[self.current_index][2], fill="#BEA8C7")  #Reset color
            self.update_letter_image()  #Update image
            self.update_red_line()  #Update indicator

    def show_results(self):  #Display results
        end_time = time.time()
        elapsed_minutes = (end_time - self.start_time) / 60 if self.start_time else 0

        correct = sum(1 for char_info in self.char_dict.values() if char_info[1] and char_info[3])
        total = len(self.char_dict)
        accuracy = (correct / total) * 100 if total > 0 else 0
        wpm = (total / 5) / elapsed_minutes if elapsed_minutes > 0 else 0  #WPM
        cpm = total / elapsed_minutes if elapsed_minutes > 0 else 0  #CPM

        self.text_frame.place(relx=0.5, rely=0, anchor="n")  #Slide text to top
        data = open_json(resource_path('./data.json'))
        data[f'{len(data)+1}'] = {
            "wpm":  int(wpm),
            "cpm":  int(cpm),
            'accuracy': int(accuracy)
        }
        dump_json(data, resource_path('./data.json'))
        result_text = (f"Test Complete!\n" #Results
                       f"Accuracy: {accuracy:.2f}%\n"
                       f"WPM: {wpm:.2f}\n"
                       f"CPM: {cpm:.2f}\n"
                       f"Correct: {correct}/{total}")
        self.result_label = tk.Label(self.main_frame, text=result_text,
                                     bg="#373441", font=("Arial", 18), fg="#BEA8C7")
        self.result_label.place(relx=0.5, rely=0.5, anchor="center")  #Center result label
        button_style = {
            "bg": "#9552AF", "fg": "#C894DC", "bd": 0, "highlightthickness": 0,
            "activebackground": "#B026E7", "activeforeground": "#B026E7"
        }
        self.restart_button = tk.Button(self.main_frame, text="Restart",
                                        command=self.restart, **button_style,
                                        width=15, height=2, font=("Arial", 18))
        self.restart_button.place(relx=0.5, rely=0.7, anchor="center")

    def restart(self):  #Restar
        if self.result_label:
            self.result_label.destroy()
            self.result_label = None
        if self.restart_button:
            self.restart_button.destroy()
            self.restart_button = None
        self.canvas.destroy()  # Destroy old canvas
        self.text_frame.place(relx=0.5, rely=0.5, anchor="center")
        if self.image_label is None:
            self.show_image()

        #Reset stuff
        self.current_index = 0  # Reset typing position
        self.start_time, self.original_image, self.red_line_id = None, None, None  # Reset everythign

        #Cancel any existing indicator
        if self.flicker_after_id is not None:
            self.root.after_cancel(self.flicker_after_id)
            self.flicker_after_id = None

        #Create new test
        new_sentence = self.get_sentence()  # Get new sentence
        self.sentence = new_sentence  # Update sentence
        self.char_dict = self.create_char_dict()  # Recreate dict
        self.create_text_grid()  # Recreate text grid

    def destroy_menu(self, ID): #Destroy current menu's content:, call ID to destroy
        if ID == 1:
            print('there is nothing to destroy')
        elif ID == 2:
            if self.result_label:
                self.result_label.destroy()
                self.result_label = None
            if self.restart_button:
                self.restart_button.destroy()
                self.restart_button = None
            self.canvas.delete("all")  # Clear text grid

            #Reset stuff
            self.text_frame.place(relx=0.5, rely=0.5, anchor="center")
            self.current_index = 0
            self.image_label.destroy()
            self.start_time, self.original_image, self.red_line_id, self.image_label = None, None, None, None
            self.last_button = 1
        elif ID == 3:
            print('there is nothing to destroy')
        elif ID == 4:
            print('there is nothing to destroy')
        elif ID == 5:
            print('there is nothing to destroy')

def main():
    root = tk.Tk()
    root.title("BombApp")
    app = TypingTestApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()