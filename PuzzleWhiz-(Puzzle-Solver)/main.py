import os
import cv2
import pickle
import pygame
import random
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
from sklearn.ensemble import RandomForestClassifier
from skimage.metrics import structural_similarity as ssim
from tkinter import Label, filedialog, Toplevel, simpledialog, Canvas, colorchooser, messagebox


model = None
original_img = None
training_images = []
training_pieces = []
puzzle_images = []
puzzle_pieces = []
pieces_edges = []
rotated_puzzle_pieces = []
piece_labels = []
selected_piece = None
playlist = []
current_song_index = 0
global_volume = 1.0
global_bg_color = "white"
global_text_color = "black"
global_button_color = "SystemButtonFace"
dataset = "C:\\Users\\Admin\\PycharmProjects\\Puzzle\\puzzle_piece_data.pkl"


def load_original_image():
    global original_img
    file_path = filedialog.askopenfilename()
    if not file_path:
        return
    cv_img = cv2.imread(file_path)
    if cv_img is None:
        print(f"Imaginea nu a putut fi găsită la calea: {file_path}")
        return
    cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    original_img = Image.fromarray(cv_img)
    print("Imaginea originală a fost încărcată.")
    show_original_image()

def show_original_image():
    if original_img is None:
        print("Imaginea originală nu a fost încărcată.")
        return
    original_window = Toplevel(root)
    original_window.title("Imaginea Originală")

    screen_width = original_window.winfo_screenwidth()
    screen_height = original_window.winfo_screenheight()

    img_aspect_ratio = original_img.width / original_img.height
    screen_aspect_ratio = screen_width / screen_height

    if img_aspect_ratio > screen_aspect_ratio:
        new_width = screen_width
        new_height = int(screen_width / img_aspect_ratio)
    else:
        new_height = screen_height
        new_width = int(screen_height * img_aspect_ratio)

    resized_img = original_img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    tk_original_img = ImageTk.PhotoImage(image=resized_img)
    original_label = Label(original_window, image=tk_original_img)
    original_label.image = tk_original_img
    original_label.pack()

    original_window.geometry(f"{screen_width}x{screen_height}")

def load_puzzle_images():
    global puzzle_images
    puzzle_images = []
    file_paths = filedialog.askopenfilenames()
    if not file_paths:
        return
    for file_path in file_paths:
        cv_img = cv2.imread(file_path)
        if cv_img is None:
            print(f"Imaginea nu a putut fi găsită la calea: {file_path}")
            continue
        cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        puzzle_img = Image.fromarray(cv_img)
        puzzle_images.append(puzzle_img)
    print(f"{len(puzzle_images)} imagini puzzle au fost încărcate.")
    process_puzzle_images()

def process_puzzle_images():
    global puzzle_pieces, pieces_edges
    if not puzzle_images:
        print("Nicio imagine puzzle nu a fost încărcată.")
        return

    puzzle_pieces = []
    pieces_edges = []
    big_index = 0
    for puzzle_img in puzzle_images:
        cv_img = np.array(puzzle_img)
        gray = cv2.cvtColor(cv_img, cv2.COLOR_RGB2GRAY)
        _, thresh = cv2.threshold(gray, 6, 255, cv2.THRESH_BINARY)

        kernel = np.ones((5, 5), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) < 2:
            print("Imaginea trebuie să conțină cel puțin două piese separate de un fundal negru.")
            continue

        max_contour_area = max(cv2.contourArea(cnt) for cnt in contours)
        min_relative_area = 0.01
        filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > max_contour_area * min_relative_area]

        for index, cnt in enumerate(filtered_contours):
            piece_exact = extract_piece_with_contour(cv_img, cnt)
            puzzle_pieces.append(piece_exact)
            #create_piece_window(piece_exact, index + big_index)
        big_index = index + big_index + 1

    for piece in puzzle_pieces:
        piece_resized = cv2.resize(piece, (100, 100))
        gray_piece = cv2.cvtColor(piece_resized, cv2.COLOR_RGBA2GRAY)
        flat_feature = gray_piece.flatten().reshape(1, -1)
        predicted_edges = model.predict(flat_feature)
        pieces_edges.append(predicted_edges[0])

    index = 1
    for edges in pieces_edges:
        edges_tuple = tuple(edges)
        print("Piesa", index, ", are marignile: ", edges_tuple)
        index += 1

    print(f"{len(puzzle_pieces)} piese au fost detectate și procesate.")
    return puzzle_pieces

def extract_piece_with_contour(image, contour):
    x, y, w, h = cv2.boundingRect(contour)
    piece = image[y:y + h, x:x + w]

    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.drawContours(mask, [contour], -1, 255, thickness=cv2.FILLED, offset=(-x, -y))
    piece_exact = cv2.bitwise_and(piece, piece, mask=mask)

    if piece_exact.shape[2] == 3:
        piece_exact = cv2.cvtColor(piece_exact, cv2.COLOR_RGB2RGBA)

    piece_rgba = np.zeros((h, w, 4), dtype=np.uint8)
    piece_rgba[:, :, :3] = piece_exact[:, :, :3]
    piece_rgba[:, :, 3] = mask

    return piece_rgba

def load_training_data(dataset_file):
    with open(dataset_file, 'rb') as f:
        piece_data = pickle.load(f)
    return piece_data

def preprocess_training_data(piece_data, target_size=(100, 100)):
    features = []
    labels = []
    for piece, edges in piece_data:
        piece_resized = cv2.resize(piece, target_size)
        gray_piece = cv2.cvtColor(piece_resized, cv2.COLOR_RGBA2GRAY)
        flat_feature = gray_piece.flatten()
        features.append(flat_feature)
        labels.append(edges)

    features = np.array(features)
    labels = np.array(labels)
    return features, labels

def create_piece_window(piece, index, show_rotate_button=True):
    piece_height, piece_width, _ = piece.shape
    border_size = 50

    piece_with_border = cv2.copyMakeBorder(piece, border_size, border_size, border_size, border_size, cv2.BORDER_CONSTANT, value=[0, 0, 0, 0])

    piece_window = Toplevel(root)
    piece_window.title(f"Piesă Puzzle {index + 1}")

    piece_img = Image.fromarray(piece_with_border)
    tk_piece_img = ImageTk.PhotoImage(image=piece_img)

    piece_label = Label(piece_window, image=tk_piece_img, bg='gray')
    piece_label.image = tk_piece_img
    piece_label.pack()

    piece_with_border_height, piece_with_border_width, _ = piece_with_border.shape
    piece_window.geometry(f"{piece_with_border_width}x{piece_with_border_height + 50}")

    if show_rotate_button:
        rotate_button = tk.Button(piece_window, text="Rotate", command=lambda: rotate_piece_prompt(piece_with_border, piece_label, index))
        rotate_button.pack(side=tk.BOTTOM, pady=10)

def rotate_piece_prompt(piece, piece_label, index):
    angle = simpledialog.askfloat("Input", "Introduceți unghiul de rotație (grade):", minvalue=-360, maxvalue=360)
    if angle is not None:
        rotate_piece(piece, angle, piece_label, index)

def rotate_piece(piece, angle, piece_label, index):
    pil_img = Image.fromarray(piece)
    rotated_img = pil_img.rotate(angle, expand=True, fillcolor=(0, 0, 0, 0))
    rotated_piece = np.array(rotated_img)

    gray = cv2.cvtColor(rotated_piece, cv2.COLOR_RGBA2GRAY)
    _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    largest_contour = max(contours, key=cv2.contourArea)

    cropped_piece = extract_piece_with_contour(rotated_piece, largest_contour)
    border_size = 50
    cropped_piece_with_border = cv2.copyMakeBorder(cropped_piece, border_size, border_size, border_size, border_size, cv2.BORDER_CONSTANT, value=[0, 0, 0, 0])

    resized_img = Image.fromarray(cropped_piece_with_border)
    tk_resized_img = ImageTk.PhotoImage(image=resized_img)

    piece_label.config(image=tk_resized_img)
    piece_label.image = tk_resized_img

    piece_with_border_height, piece_with_border_width, _ = cropped_piece_with_border.shape
    piece_window = piece_label.master
    piece_window.geometry(f"{piece_with_border_width}x{piece_with_border_height + 50}")

    puzzle_pieces[index] = cropped_piece

def calculate_resize_factor_single(piece, window_width, window_height):
    max_piece_width = piece.shape[1]
    max_piece_height = piece.shape[0]
    max_piece_dim = max(max_piece_width, max_piece_height)
    resize_factor = 1
    if max_piece_dim > window_width or max_piece_dim > window_height:
        resize_factor = min(window_width / max_piece_dim, window_height / max_piece_dim)
    return resize_factor

def calculate_resize_factor(pieces, window_width, window_height, padding=10):
    max_piece_width = max(piece.shape[1] for piece in pieces)
    max_piece_height = max(piece.shape[0] for piece in pieces)

    num_columns = int(np.ceil(np.sqrt(len(pieces))))
    num_rows = int(np.ceil(len(pieces) / num_columns))

    target_piece_width = (window_width - (num_columns + 1) * padding) / num_columns
    target_piece_height = (window_height - (num_rows + 1) * padding) / num_rows

    max_piece_dim = max(max_piece_width, max_piece_height)
    resize_factor = 1
    if max_piece_dim > target_piece_width or max_piece_dim > target_piece_height:
        resize_factor = min(target_piece_width / max_piece_dim, target_piece_height / max_piece_dim)

    return resize_factor

def resize_pieces_to_fit_window(pieces, window_width, window_height, padding=10):
    resize_factor = calculate_resize_factor(pieces, window_width, window_height, padding)

    resized_pieces = []
    for piece in pieces:
        piece_img = Image.fromarray(piece)
        new_width = int(piece_img.width * resize_factor)
        new_height = int(piece_img.height * resize_factor)
        resized_piece = piece_img.resize((new_width, new_height), Image.LANCZOS)
        resized_pieces.append(np.array(resized_piece))

    pieces[:] = resized_pieces
    return resized_pieces

def start_drag(event, index):
    global selected_piece
    selected_piece = index
    widget = event.widget
    widget.startX = (event.x + canvas.canvasx(0)) / zoom_factor
    widget.startY = (event.y + canvas.canvasy(0)) / zoom_factor
    widget.initX = canvas.coords(widget.find_withtag("current"))[0] / zoom_factor
    widget.initY = canvas.coords(widget.find_withtag("current"))[1] / zoom_factor

def on_drag(event):
    widget = event.widget
    x = (widget.initX + ((canvas.canvasx(event.x) / zoom_factor) - widget.startX))
    y = (widget.initY + ((canvas.canvasy(event.y) / zoom_factor) - widget.startY))
    canvas.coords(widget.find_withtag("current"), x * zoom_factor, y * zoom_factor)

def stop_drag(event):
    pass

def zoom_in():
    global zoom_factor
    zoom_factor *= 1.1
    update_zoom()

def zoom_out():
    global zoom_factor
    zoom_factor /= 1.1
    update_zoom()

def update_zoom():
    global canvas, piece_labels, image_refs, zoom_factor, piece_positions
    for index, piece_id in enumerate(piece_labels):
        x, y, w, h = piece_positions[index]
        new_w = int(w * zoom_factor)
        new_h = int(h * zoom_factor)
        new_x = int(x * zoom_factor)
        new_y = int(y * zoom_factor)

        piece = puzzle_pieces[index]
        piece_resized = cv2.resize(piece, (new_w, new_h))
        piece_img = Image.fromarray(piece_resized)
        tk_piece_img = ImageTk.PhotoImage(image=piece_img)

        canvas.coords(piece_id, new_x, new_y)
        canvas.itemconfig(piece_id, image=tk_piece_img)
        image_refs[index] = tk_piece_img
        piece_positions[index] = (x, y, w, h)

def select_piece(index):
    global selected_piece
    selected_piece = index

def rotate_selected_piece():
    if selected_piece is None:
        return
    piece_img = puzzle_pieces[selected_piece]
    angle = simpledialog.askfloat("Input", "Introduceți unghiul de rotație (grade):", minvalue=-360, maxvalue=360)
    if angle is not None:
        rotated_img = Image.fromarray(piece_img).rotate(angle, expand=True)

        screen_width = canvas.winfo_width()
        screen_height = canvas.winfo_height()
        resize_factor = calculate_resize_factor_single(np.array(rotated_img), screen_width, screen_height)

        new_width = int(rotated_img.width * resize_factor)
        new_height = int(rotated_img.height * resize_factor)
        resized_rotated_img = rotated_img.resize((new_width, new_height), Image.LANCZOS)

        tk_resized_rotated_img = ImageTk.PhotoImage(image=resized_rotated_img)
        canvas.itemconfig(piece_labels[selected_piece], image=tk_resized_rotated_img)
        image_refs[selected_piece] = tk_resized_rotated_img
        puzzle_pieces[selected_piece] = np.array(resized_rotated_img)

        x, y = canvas.coords(piece_labels[selected_piece])
        dx = (resized_rotated_img.size[0] - piece_img.shape[1]) / 2
        dy = (resized_rotated_img.size[1] - piece_img.shape[0]) / 2
        canvas.coords(piece_labels[selected_piece], x - dx, y - dy)

def show_manual_solve_window():
    global canvas, piece_labels, image_refs, zoom_factor, canvas_frame, manual_window, piece_positions
    zoom_factor = 1.0
    manual_window = Toplevel(root)
    manual_window.title("Rezolvă Puzzle-ul Manual")
    manual_window.configure(background='black')
    manual_window.geometry(f"{manual_window.winfo_screenwidth()}x{manual_window.winfo_screenheight()}")

    screen_width = manual_window.winfo_screenwidth()
    screen_height = manual_window.winfo_screenheight() - 150
    resized_pieces = resize_pieces_to_fit_window(puzzle_pieces, screen_width, screen_height, padding=20)

    canvas_frame = tk.Frame(manual_window, bg='black')
    canvas_frame.pack(fill=tk.BOTH, expand=True)

    canvas = Canvas(canvas_frame, bg='black', scrollregion=(0, 0, screen_width * 2, screen_height * 2))
    hbar = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=canvas.xview)
    hbar.pack(side=tk.BOTTOM, fill=tk.X)
    vbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
    vbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
    canvas.pack(fill=tk.BOTH, expand=True)

    piece_labels = []
    image_refs = {}
    piece_positions = []

    num_columns = int(np.ceil(np.sqrt(len(resized_pieces))))
    num_rows = int(np.ceil(len(resized_pieces) / num_columns))

    for index, piece in enumerate(resized_pieces):
        piece_img = Image.fromarray(piece)
        tk_piece_img = ImageTk.PhotoImage(image=piece_img)

        row = index // num_columns
        col = index % num_columns

        x = 20 + col * (piece.shape[1] + 20)
        y = 20 + row * (piece.shape[0] + 20)

        piece_id = canvas.create_image(x, y, anchor=tk.NW, image=tk_piece_img)
        piece_labels.append(piece_id)
        image_refs[index] = tk_piece_img
        piece_positions.append((x, y, piece.shape[1], piece.shape[0]))  # Store the original position and size

        canvas.tag_bind(piece_id, "<Button-1>", lambda event, idx=index: start_drag(event, idx))
        canvas.tag_bind(piece_id, "<B1-Motion>", on_drag)
        canvas.tag_bind(piece_id, "<ButtonRelease-1>", stop_drag)

    button_frame = tk.Frame(manual_window, bg='black')
    button_frame.pack(side=tk.BOTTOM, fill=tk.X)

    zoom_in_button = tk.Button(button_frame, text="Zoom In", command=zoom_in, width=20, height=3)
    zoom_in_button.pack(side=tk.LEFT, padx=10, pady=20)

    rotate_button = tk.Button(button_frame, text="Rotate", command=rotate_selected_piece, width=20, height=3)
    rotate_button.pack(side=tk.LEFT, padx=10, pady=20)

    zoom_out_button = tk.Button(button_frame, text="Zoom Out", command=zoom_out, width=20, height=3)
    zoom_out_button.pack(side=tk.LEFT, padx=10, pady=20)

def calculate_segments(original_width, original_height, num_pieces):
    aspect_ratio = original_width / original_height
    print("original_width =", original_width, "original_height =", original_height, "aspect_ratio =", aspect_ratio)
    num_columns = int(np.ceil(np.sqrt(num_pieces * aspect_ratio)))
    num_rows = int(np.floor(num_pieces / num_columns))

    while num_columns * num_rows < num_pieces:
        num_rows += 1

    if num_columns * num_rows > num_pieces:
        num_columns -= 1

    segment_width = original_width // num_columns
    segment_height = original_height // num_rows

    print("num_rows =", num_rows, "num_cols =", num_columns, "seg_width =", segment_width, "seg_height =", segment_height)
    return num_rows, num_columns, segment_width, segment_height

def create_large_segment(original_image, segment_x, segment_y, segment_width, segment_height):
    large_segment = np.zeros((segment_height * 3, segment_width * 3, original_image.shape[2]), dtype=original_image.dtype)
    for i in range(-1, 2):
        for j in range(-1, 2):
            x = segment_x + j * segment_width
            y = segment_y + i * segment_height
            segment_slice = original_image[y:y+segment_height, x:x+segment_width]
            target_y_start = (i+1) * segment_height
            target_y_end = target_y_start + segment_slice.shape[0]
            target_x_start = (j+1) * segment_width
            target_x_end = target_x_start + segment_slice.shape[1]
            large_segment[target_y_start:target_y_end, target_x_start:target_x_end] = segment_slice
    return large_segment

def calculate_similarity(piece, segment):
    if piece.shape[:2] != segment.shape[:2] or piece.shape[2] != segment.shape[2]:
        resized_piece = cv2.resize(piece, (segment.shape[1], segment.shape[0]), interpolation=cv2.INTER_AREA)
    else:
        resized_piece = piece

    if resized_piece.shape[2] != segment.shape[2]:
        resized_piece = cv2.cvtColor(resized_piece, cv2.COLOR_RGBA2RGB)
        segment = cv2.cvtColor(segment, cv2.COLOR_BGR2RGB)

    win_size = min(segment.shape[0], segment.shape[1], 7)
    similarity, _ = ssim(segment, resized_piece, full=True, multichannel=True, win_size=win_size, channel_axis=2)
    return similarity * 100

def show_auto_solve_window():
    global puzzle_pieces, original_img, pieces_edges

    if not original_img:
        messagebox.showerror("Eroare", "Încărcați imaginea originală.")
        return

    if not puzzle_pieces:
        messagebox.showerror("Eroare", "Încărcați piesele de puzzle.")
        return

    def get_corner_pieces():
        corners = []
        for i, edges in enumerate(pieces_edges_copy):
            if (edges[0] == 0 and edges[1] == 0) or (edges[1] == 0 and edges[2] == 0) or (
                    edges[2] == 0 and edges[3] == 0) or (edges[3] == 0 and edges[0] == 0):
                corners.append(i)
        return corners

    def get_edge_pieces(str, placed_pieces):
        edges = []
        if str == "north":
            for i, edge in enumerate(pieces_edges_copy):
                if edge[1] == 0:
                    ok = 1
                    for index, _, _ in placed_pieces:
                        if i == index:
                            ok = 0
                            break
                    if ok == 1:
                        edges.append(i)

        elif str == "south":
            for i, edge in enumerate(pieces_edges_copy):
                if edge[3] == 0:
                    ok = 1
                    for index, _, _ in placed_pieces:
                        if i == index:
                            ok = 0
                            break
                    if ok == 1:
                        edges.append(i)

        elif str == "west":
            for i, edge in enumerate(pieces_edges_copy):
                if edge[0] == 0:
                    ok = 1
                    for index, _, _ in placed_pieces:
                        if i == index:
                            ok = 0
                            break
                    if ok == 1:
                        edges.append(i)

        elif str == "east":
            for i, edge in enumerate(pieces_edges_copy):
                if edge[2] == 0:
                    ok = 1
                    for index, _, _ in placed_pieces:
                        if i == index:
                            ok = 0
                            break
                    if ok == 1:
                        edges.append(i)
        return edges

    def find_best_piece(piece_indexes, segment):
        print()
        print("Fresh Start:")
        best_piece_index = None
        best_score = float('-inf')

        for i in piece_indexes:
            piece = puzzle_pieces_copy[i]
            similarity = calculate_similarity(piece, segment)

            print("piesa ", i + 1)
            print("similarity ", similarity)

            if similarity > best_score:
                best_score = similarity
                best_piece_index = i

        return best_piece_index

    def place_edge_pieces_north():
        for col in range(1, num_columns - 1):
            segment_x = col * segment_width
            segment = original_resized_cv[0:segment_height, segment_x:segment_x + segment_width]
            candidate_edge_indices = get_edge_pieces("north", placed_pieces)

            candidate_pieces = []
            prev_piece_index = None

            for indexx, roww, coll in placed_pieces:
                if roww == 0 and coll == col - 1:
                    prev_piece_index = indexx
                    break

            if len(candidate_edge_indices) == 0:
                break

            if len(candidate_edge_indices) == 1:
                piece = puzzle_pieces_copy[candidate_edge_indices[0]]
                piece_resized = cv2.resize(piece, (segment_width, segment_height), interpolation=cv2.INTER_AREA)
                piece_img = Image.fromarray(piece_resized)
                tk_piece_img = ImageTk.PhotoImage(piece_img)
                piece_id = f"piece_0_{col}"
                image_refs[piece_id] = tk_piece_img
                canvas.create_image(col * segment_width, 0, anchor=tk.NW, image=tk_piece_img)
                placed_pieces.append((candidate_edge_indices[0], 0, col))

            if len(candidate_edge_indices) > 1 and prev_piece_index is not None:
                for candidate in candidate_edge_indices:
                    if (pieces_edges_copy[prev_piece_index][2] == -1 * pieces_edges_copy[candidate][0]):
                        candidate_pieces.append(candidate)

            if len(candidate_pieces) == 0:
                break

            if len(candidate_pieces) == 1:
                piece = puzzle_pieces_copy[candidate_pieces[0]]
                piece_resized = cv2.resize(piece, (segment_width, segment_height), interpolation=cv2.INTER_AREA)
                piece_img = Image.fromarray(piece_resized)
                tk_piece_img = ImageTk.PhotoImage(piece_img)
                piece_id = f"piece_0_{col}"
                image_refs[piece_id] = tk_piece_img
                canvas.create_image(col * segment_width, 0, anchor=tk.NW, image=tk_piece_img)
                placed_pieces.append((candidate_pieces[0], 0, col))

            if len(candidate_pieces) > 1:
                best_piece_index = find_best_piece(candidate_pieces, segment)
                if best_piece_index is not None:
                    piece = puzzle_pieces_copy[best_piece_index]
                    piece_resized = cv2.resize(piece, (segment_width, segment_height), interpolation=cv2.INTER_AREA)
                    piece_img = Image.fromarray(piece_resized)
                    tk_piece_img = ImageTk.PhotoImage(piece_img)
                    piece_id = f"piece_0_{col}"
                    image_refs[piece_id] = tk_piece_img
                    canvas.create_image(segment_x, 0, anchor=tk.NW, image=tk_piece_img)
                    placed_pieces.append((best_piece_index, 0, col))

    def place_edge_pieces_south():
        for col in range(1, num_columns - 1):
            segment_x = col * segment_width
            segment_y = (num_rows - 1) * segment_height
            segment = original_resized_cv[segment_y - segment_height:segment_y, segment_x:segment_x + segment_width]
            candidate_edge_indices = get_edge_pieces("south", placed_pieces)

            candidate_pieces = []
            prev_piece_index = None

            for indexx, roww, coll in placed_pieces:
                if roww == num_rows - 1 and coll == col - 1:
                    prev_piece_index = indexx
                    break

            if len(candidate_edge_indices) == 0:
                break

            if len(candidate_edge_indices) == 1:
                piece = puzzle_pieces_copy[candidate_edge_indices[0]]
                piece_resized = cv2.resize(piece, (segment_width, segment_height), interpolation=cv2.INTER_AREA)
                piece_img = Image.fromarray(piece_resized)
                tk_piece_img = ImageTk.PhotoImage(piece_img)
                piece_id = f"piece_{num_rows - 1}_{col}"
                image_refs[piece_id] = tk_piece_img
                canvas.create_image(segment_x, segment_y, anchor=tk.NW, image=tk_piece_img)
                placed_pieces.append((candidate_edge_indices[0], num_rows - 1, col))

            if len(candidate_edge_indices) > 1 and prev_piece_index is not None:
                for candidate in candidate_edge_indices:
                    if (pieces_edges_copy[prev_piece_index][2] == -1 * pieces_edges_copy[candidate][0]):
                        candidate_pieces.append(candidate)

            if len(candidate_pieces) == 0:
                break

            if len(candidate_pieces) == 1:
                piece = puzzle_pieces_copy[candidate_pieces[0]]
                piece_resized = cv2.resize(piece, (segment_width, segment_height), interpolation=cv2.INTER_AREA)
                piece_img = Image.fromarray(piece_resized)
                tk_piece_img = ImageTk.PhotoImage(piece_img)
                piece_id = f"piece_{num_rows - 1}_{col}"
                image_refs[piece_id] = tk_piece_img
                canvas.create_image(segment_x, segment_y, anchor=tk.NW, image=tk_piece_img)
                placed_pieces.append((candidate_pieces[0], num_rows - 1, col))

            if len(candidate_pieces) > 1:
                best_piece_index = find_best_piece(candidate_pieces, segment)
                if best_piece_index is not None:
                    piece = puzzle_pieces_copy[best_piece_index]
                    piece_resized = cv2.resize(piece, (segment_width, segment_height), interpolation=cv2.INTER_AREA)
                    piece_img = Image.fromarray(piece_resized)
                    tk_piece_img = ImageTk.PhotoImage(piece_img)
                    piece_id = f"piece_{num_rows - 1}_{col}"
                    image_refs[piece_id] = tk_piece_img
                    canvas.create_image(segment_x, segment_y, anchor=tk.NW, image=tk_piece_img)
                    placed_pieces.append((best_piece_index, num_rows - 1, col))

    def place_edge_pieces_west():
        for row in range(1, num_rows - 1):
            segment_y = row * segment_height
            segment = original_resized_cv[segment_y:segment_y + segment_height, 0:segment_width]
            candidate_edge_indices = get_edge_pieces("west", placed_pieces)

            candidate_pieces = []
            prev_piece_index = None

            for indexx, roww, coll in placed_pieces:
                if roww == row - 1 and coll == 0:
                    prev_piece_index = indexx
                    break

            if len(candidate_edge_indices) == 0:
                break

            if len(candidate_edge_indices) == 1:
                piece = puzzle_pieces_copy[candidate_edge_indices[0]]
                piece_resized = cv2.resize(piece, (segment_width, segment_height), interpolation=cv2.INTER_AREA)
                piece_img = Image.fromarray(piece_resized)
                tk_piece_img = ImageTk.PhotoImage(piece_img)
                piece_id = f"piece_{row}_{0}"
                image_refs[piece_id] = tk_piece_img
                canvas.create_image(0, segment_y, anchor=tk.NW, image=tk_piece_img)
                placed_pieces.append((candidate_edge_indices[0], row, 0))

            if len(candidate_edge_indices) > 1 and prev_piece_index is not None:
                for candidate in candidate_edge_indices:
                    if (pieces_edges_copy[prev_piece_index][3] == -1 * pieces_edges_copy[candidate][1]):
                        candidate_pieces.append(candidate)

            if len(candidate_pieces) == 0:
                break

            if len(candidate_pieces) == 1:
                piece = puzzle_pieces_copy[candidate_pieces[0]]
                piece_resized = cv2.resize(piece, (segment_width, segment_height), interpolation=cv2.INTER_AREA)
                piece_img = Image.fromarray(piece_resized)
                tk_piece_img = ImageTk.PhotoImage(piece_img)
                piece_id = f"piece_{row}_{0}"
                image_refs[piece_id] = tk_piece_img
                canvas.create_image(0, segment_y, anchor=tk.NW, image=tk_piece_img)
                placed_pieces.append((candidate_pieces[0], row, 0))

            if len(candidate_pieces) > 1:
                best_piece_index = find_best_piece(candidate_pieces, segment)
                if best_piece_index is not None:
                    piece = puzzle_pieces_copy[best_piece_index]
                    piece_resized = cv2.resize(piece, (segment_width, segment_height), interpolation=cv2.INTER_AREA)
                    piece_img = Image.fromarray(piece_resized)
                    tk_piece_img = ImageTk.PhotoImage(piece_img)
                    piece_id = f"piece_{row}_{0}"
                    image_refs[piece_id] = tk_piece_img
                    canvas.create_image(0, segment_y, anchor=tk.NW, image=tk_piece_img)
                    placed_pieces.append((best_piece_index, row, 0))

    def place_edge_pieces_east():
        for row in range(1, num_rows - 1):
            segment_x = (num_columns - 1) * segment_width
            segment_y = row * segment_height
            segment = original_resized_cv[segment_y:segment_y + segment_height, segment_x - segment_width:segment_x]
            candidate_edge_indices = get_edge_pieces("east", placed_pieces)

            candidate_pieces = []
            prev_piece_index = None

            for indexx, roww, coll in placed_pieces:
                if roww == row - 1 and coll == num_columns - 1:
                    prev_piece_index = indexx
                    break

            if len(candidate_edge_indices) == 0:
                break

            if len(candidate_edge_indices) == 1:
                piece = puzzle_pieces_copy[candidate_edge_indices[0]]
                piece_resized = cv2.resize(piece, (segment_width, segment_height), interpolation=cv2.INTER_AREA)
                piece_img = Image.fromarray(piece_resized)
                tk_piece_img = ImageTk.PhotoImage(piece_img)
                piece_id = f"piece_{row}_{num_columns - 1}"
                image_refs[piece_id] = tk_piece_img
                canvas.create_image(segment_x, segment_y, anchor=tk.NW, image=tk_piece_img)
                placed_pieces.append((candidate_edge_indices[0], row, num_columns - 1))

            if len(candidate_edge_indices) > 1 and prev_piece_index is not None:
                for candidate in candidate_edge_indices:
                    if (pieces_edges_copy[prev_piece_index][3] == -1 * pieces_edges_copy[candidate][1]):
                        candidate_pieces.append(candidate)

            if len(candidate_pieces) == 0:
                break

            if len(candidate_pieces) == 1:
                piece = puzzle_pieces_copy[candidate_pieces[0]]
                piece_resized = cv2.resize(piece, (segment_width, segment_height), interpolation=cv2.INTER_AREA)
                piece_img = Image.fromarray(piece_resized)
                tk_piece_img = ImageTk.PhotoImage(piece_img)
                piece_id = f"piece_{row}_{num_columns - 1}"
                image_refs[piece_id] = tk_piece_img
                canvas.create_image(segment_x, segment_y, anchor=tk.NW, image=tk_piece_img)
                placed_pieces.append((candidate_pieces[0], row, num_columns - 1))

            if len(candidate_pieces) > 1:
                best_piece_index = find_best_piece(candidate_pieces, segment)
                if best_piece_index is not None:
                    piece = puzzle_pieces_copy[best_piece_index]
                    piece_resized = cv2.resize(piece, (segment_width, segment_height), interpolation=cv2.INTER_AREA)
                    piece_img = Image.fromarray(piece_resized)
                    tk_piece_img = ImageTk.PhotoImage(piece_img)
                    piece_id = f"piece_{row}_{num_columns - 1}"
                    image_refs[piece_id] = tk_piece_img
                    canvas.create_image(segment_x, segment_y, anchor=tk.NW, image=tk_piece_img)
                    placed_pieces.append((best_piece_index, row, num_columns - 1))

    def place_inner_pieces():
        for row in range(1, num_rows - 1):
            for col in range(1, num_columns - 1):
                segment_x = col * segment_width
                segment_y = row * segment_height
                segment = original_resized_cv[segment_y:segment_y + segment_height, segment_x:segment_x + segment_width]

                candidate_pieces = []
                not_placed = []
                top_piece_index = None
                bottom_piece_index = None
                left_piece_index = None
                right_piece_index = None

                for indexx, roww, coll in placed_pieces:
                    if roww == row - 1 and coll == col:
                        top_piece_index = indexx
                    elif roww == row + 1 and coll == col:
                        bottom_piece_index = indexx
                    elif roww == row and coll == col - 1:
                        left_piece_index = indexx
                    elif roww == row and coll == col + 1:
                        right_piece_index = indexx

                for index_piece, _ in enumerate(puzzle_pieces_copy):
                    ok = 1
                    for index_placed, _, _ in placed_pieces:
                        if index_piece == index_placed:
                            ok = 0
                    if ok == 1:
                        not_placed.append(index_piece)

                if len(not_placed) == 0:
                    break

                if len(not_placed) == 1:
                    piece = puzzle_pieces_copy[not_placed[0]]
                    piece_resized = cv2.resize(piece, (segment_width, segment_height), interpolation=cv2.INTER_AREA)
                    piece_img = Image.fromarray(piece_resized)
                    tk_piece_img = ImageTk.PhotoImage(piece_img)
                    piece_id = f"piece_{row}_{col}"
                    image_refs[piece_id] = tk_piece_img
                    canvas.create_image(segment_x, segment_y, anchor=tk.NW, image=tk_piece_img)
                    placed_pieces.append((not_placed[0], row, col))

                if len(not_placed) > 1:
                    if top_piece_index is not None and left_piece_index is not None:
                        if right_piece_index is not None and bottom_piece_index is not None:
                            for candidate_index in not_placed:
                                if (pieces_edges_copy[top_piece_index][3] == -1 * pieces_edges_copy[candidate_index][
                                    1]) and (
                                        pieces_edges_copy[left_piece_index][2] == -1 * pieces_edges_copy[candidate_index][
                                    0]) and (
                                        pieces_edges_copy[right_piece_index][0] == -1 * pieces_edges_copy[candidate_index][
                                    2]) and (
                                        pieces_edges_copy[bottom_piece_index][1] == -1 * pieces_edges_copy[candidate_index][
                                    3]):
                                    candidate_pieces.append(candidate_index)
                        elif right_piece_index is not None:
                            for candidate_index in not_placed:
                                if (pieces_edges_copy[top_piece_index][3] == -1 * pieces_edges_copy[candidate_index][
                                    1]) and (
                                        pieces_edges_copy[left_piece_index][2] == -1 * pieces_edges_copy[candidate_index][
                                    0]) and (
                                        pieces_edges_copy[right_piece_index][0] == -1 * pieces_edges_copy[candidate_index][
                                    2]):
                                    candidate_pieces.append(candidate_index)
                        elif bottom_piece_index is not None:
                            for candidate_index in not_placed:
                                if (pieces_edges_copy[top_piece_index][3] == -1 * pieces_edges_copy[candidate_index][
                                    1]) and (
                                        pieces_edges_copy[left_piece_index][2] == -1 * pieces_edges_copy[candidate_index][
                                    0]) and (
                                        pieces_edges_copy[bottom_piece_index][1] == -1 * pieces_edges_copy[candidate_index][
                                    3]):
                                    candidate_pieces.append(candidate_index)
                        else:
                            for candidate_index in not_placed:
                                if (pieces_edges_copy[top_piece_index][3] == -1 * pieces_edges_copy[candidate_index][
                                    1]) and (
                                        pieces_edges_copy[left_piece_index][2] == -1 * pieces_edges_copy[candidate_index][
                                    0]):
                                    candidate_pieces.append(candidate_index)

                if len(candidate_pieces) == 0:
                    break

                if len(candidate_pieces) == 1:
                    piece = puzzle_pieces_copy[candidate_pieces[0]]
                    piece_resized = cv2.resize(piece, (segment_width, segment_height), interpolation=cv2.INTER_AREA)
                    piece_img = Image.fromarray(piece_resized)
                    tk_piece_img = ImageTk.PhotoImage(piece_img)
                    piece_id = f"piece_{row}_{col}"
                    image_refs[piece_id] = tk_piece_img
                    canvas.create_image(segment_x, segment_y, anchor=tk.NW, image=tk_piece_img)
                    placed_pieces.append((candidate_pieces[0], row, col))

                if len(candidate_pieces) > 1:
                    best_piece_index = find_best_piece(candidate_pieces, segment)
                    if best_piece_index is not None:
                        piece = puzzle_pieces_copy[best_piece_index]
                        piece_resized = cv2.resize(piece, (segment_width, segment_height), interpolation=cv2.INTER_AREA)
                        piece_img = Image.fromarray(piece_resized)
                        tk_piece_img = ImageTk.PhotoImage(piece_img)
                        piece_id = f"piece_{row}_{col}"
                        image_refs[piece_id] = tk_piece_img
                        canvas.create_image(segment_x, segment_y, anchor=tk.NW, image=tk_piece_img)
                        placed_pieces.append((best_piece_index, row, col))

    auto_window = Toplevel(root)
    auto_window.title("Rezolvă Puzzle-ul Automat")
    auto_window.configure(background='black')
    auto_window.geometry(f"{auto_window.winfo_screenwidth()}x{auto_window.winfo_screenheight()}")

    screen_width = auto_window.winfo_screenwidth()
    screen_height = auto_window.winfo_screenheight()
    factor_redimensionare = calculate_resize_factor_single(np.array(original_img), screen_width, screen_height)

    original_resized = original_img.resize((int(original_img.width * factor_redimensionare), int(original_img.height * factor_redimensionare)), Image.LANCZOS)
    original_resized_cv = cv2.cvtColor(np.array(original_resized), cv2.COLOR_RGB2BGR)
    original_width, original_height = original_resized_cv.shape[1], original_resized_cv.shape[0]

    num_pieces = len(puzzle_pieces)
    num_rows, num_columns, segment_width, segment_height = calculate_segments(original_width, original_height, num_pieces)

    canvas = Canvas(auto_window, bg='black', scrollregion=(0, 0, screen_width * 2, screen_height * 2))
    hbar = tk.Scrollbar(auto_window, orient=tk.HORIZONTAL, command=canvas.xview)
    hbar.pack(side=tk.BOTTOM, fill=tk.X)
    vbar = tk.Scrollbar(auto_window, orient=tk.VERTICAL, command=canvas.yview)
    vbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
    canvas.pack(fill=tk.BOTH, expand=True)

    image_refs = {}
    corner_positions = []
    placed_pieces = []
    puzzle_pieces_copy = puzzle_pieces.copy()
    pieces_edges_copy = pieces_edges.copy()

    corners = get_corner_pieces()
    for index in corners:
        edges = pieces_edges_copy[index]
        if edges[0] == 0 and edges[1] == 0:
            row, col = 0, 0
        elif edges[1] == 0 and edges[2] == 0:
            row, col = 0, num_columns - 1
        elif edges[2] == 0 and edges[3] == 0:
            row, col = num_rows - 1, num_columns - 1
        elif edges[0] == 0 and edges[3] == 0:
            row, col = num_rows - 1, 0
        corner_positions.append((index, row, col))

    for index, row, col in corner_positions:
        piece = puzzle_pieces_copy[index]
        piece_resized = cv2.resize(piece, (segment_width, segment_height), interpolation=cv2.INTER_AREA)
        piece_img = Image.fromarray(piece_resized)
        tk_piece_img = ImageTk.PhotoImage(piece_img)
        piece_id = f"piece_{row}_{col}"
        image_refs[piece_id] = tk_piece_img
        canvas.create_image(col * segment_width, row * segment_height, anchor=tk.NW, image=tk_piece_img)
        placed_pieces.append((index, row, col))

    place_edge_pieces_north()
    place_edge_pieces_west()
    place_edge_pieces_south()
    place_edge_pieces_east()
    place_inner_pieces()

    canvas.image_refs = image_refs

def load_playlist(directory):
    global playlist
    supported_formats = ('.mp3', '.wav')
    playlist = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith(supported_formats)]
    random.shuffle(playlist)
    print(f"Playlist încărcat: {playlist}")

def play_next_song():
    global current_song_index
    if playlist:
        print(f"Redare melodie: {playlist[current_song_index]}")
        pygame.mixer.music.load(playlist[current_song_index])
        pygame.mixer.music.play()
        current_song_index = (current_song_index + 1) % len(playlist)
        root.after(1000, check_music_end)

def start_playlist():
    directory = os.path.join(os.path.dirname(__file__), 'music')
    if os.path.isdir(directory):
        load_playlist(directory)
        play_next_song()
    else:
        messagebox.showerror("Eroare", f"Directorul {directory} nu există.")

def check_music_end():
    if not pygame.mixer.music.get_busy():
        play_next_song()
    else:
        root.after(1000, check_music_end)

def show_settings_window():
    settings_window = Toplevel(root)
    settings_window.title("Setări")
    settings_window.geometry("400x400")
    settings_window.configure(bg=global_bg_color)

    volume_label = Label(settings_window, text="Setează volumul:", bg=global_bg_color, fg=global_text_color)
    volume_label.pack(pady=10)
    volume_scale = tk.Scale(settings_window, from_=0, to=100, orient=tk.HORIZONTAL, bg=global_button_color, fg=global_text_color, troughcolor=global_bg_color)
    volume_scale.pack(pady=10)
    volume_scale.set(global_volume * 100)

    def update_volume(val):
        global global_volume
        volume = int(val) / 100
        pygame.mixer.music.set_volume(volume)
        global_volume = volume
    volume_scale.config(command=update_volume)

    def set_background_color():
        global global_bg_color
        color_code = colorchooser.askcolor(title="Alege culoarea de fundal")
        if color_code[1]:
            root.configure(bg=color_code[1])
            settings_window.configure(bg=color_code[1])
            volume_label.configure(bg=color_code[1])
            volume_scale.configure(bg=color_code[1])
            global_bg_color = color_code[1]
            print(f"Culoare de fundal selectată: {color_code[1]}")
    background_color_button = tk.Button(settings_window, text="Setează culoarea de fundal", command=set_background_color, bg=global_button_color)
    background_color_button.pack(pady=10)

    def change_text_color():
        global global_text_color
        color_code = colorchooser.askcolor(title="Alege culoarea textului")
        if color_code[1]:
            for widget in root.winfo_children():
                if isinstance(widget, tk.Button) or isinstance(widget, Label):
                    widget.config(fg=color_code[1])
            for widget in settings_window.winfo_children():
                if isinstance(widget, tk.Button) or isinstance(widget, Label):
                    widget.config(fg=color_code[1])
            volume_label.config(fg=color_code[1])
            volume_scale.config(fg=color_code[1])
            global_text_color = color_code[1]
            print(f"Culoare text selectată: {color_code[1]}")
    text_color_button = tk.Button(settings_window, text="Schimbare culoare text", command=change_text_color, bg=global_button_color)
    text_color_button.pack(pady=10)

    def change_button_color():
        global global_button_color
        color_code = colorchooser.askcolor(title="Alege culoarea butonului")
        if color_code[1]:
            for widget in root.winfo_children():
                if isinstance(widget, tk.Button):
                    widget.config(bg=color_code[1])
            for widget in settings_window.winfo_children():
                if isinstance(widget, tk.Button):
                    widget.config(bg=color_code[1])
            volume_scale.config(bg=color_code[1])
            volume_label.config(bg=global_bg_color)
            global_button_color = color_code[1]
            print(f"Culoare buton selectată: {color_code[1]}")
    button_color_button = tk.Button(settings_window, text="Schimbare culoare buton", command=change_button_color, bg=global_button_color)
    button_color_button.pack(pady=10)

def load_images_for_training(file_paths):
    global training_images
    for file_path in file_paths:
        cv_img = cv2.imread(file_path)
        if cv_img is None:
            print(f"Imaginea nu a putut fi găsită la calea: {file_path}")
            continue
        cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        puzzle_img = Image.fromarray(cv_img)
        training_images.append(puzzle_img)
    print(f"{len(training_images)} imagini puzzle au fost încărcate.")
    return training_images

def process_training_images(training_images):
    training_pieces = []
    for puzzle_img in training_images:
        cv_img = np.array(puzzle_img)
        gray = cv2.cvtColor(cv_img, cv2.COLOR_RGB2GRAY)
        _, thresh = cv2.threshold(gray, 6, 255, cv2.THRESH_BINARY)

        kernel = np.ones((5, 5), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) < 2:
            print("Imaginea trebuie să conțină cel puțin două piese separate de un fundal negru.")
            continue

        max_contour_area = max(cv2.contourArea(cnt) for cnt in contours)
        min_relative_area = 0.01
        filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > max_contour_area * min_relative_area]

        for index, cnt in enumerate(filtered_contours):
            piece_exact = extract_piece_with_contour(cv_img, cnt)
            training_pieces.append(piece_exact)

    print(f"{len(training_pieces)} piese au fost detectate și procesate.")
    return training_pieces

def create_training_labels(filepath):
    labels = []
    with open(filepath, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                label_tuple = tuple(map(int, line.strip('()').split(',')))
                labels.append(label_tuple)
    return labels

def create_training_dataset(file_paths, labels_path):
    puzzle_images = load_images_for_training(file_paths)
    puzzle_pieces = process_training_images(puzzle_images)

    labels = create_training_labels(labels_path)
    piece_data = [(piece, labels[i]) for i, piece in enumerate(puzzle_pieces)]

    with open('puzzle_piece_data.pkl', 'wb') as f:
        pickle.dump(piece_data, f)

    print("Setul de date de antrenament a fost creat și salvat cu succes.")


def main():
    global root, model
    root = tk.Tk()
    root.title("Meniu Principal")
    root.geometry("400x400")
    pygame.mixer.init()

    start_playlist()
    check_music_end()

    if not os.path.exists(dataset):
        file_paths = [
            "C:\\Users\\Admin\\PycharmProjects\\Puzzle\\resources\\Test4.png",
            "C:\\Users\\Admin\\PycharmProjects\\Puzzle\\resources\\Test13.png",
            "C:\\Users\\Admin\\PycharmProjects\\Puzzle\\resources\\Test17.png",
            "C:\\Users\\Admin\\PycharmProjects\\Puzzle\\resources\\Test18.png",
            "C:\\Users\\Admin\\PycharmProjects\\Puzzle\\resources\\Test20.png",
            "C:\\Users\\Admin\\PycharmProjects\\Puzzle\\resources\\Test21.png",
            "C:\\Users\\Admin\\PycharmProjects\\Puzzle\\resources\\Test22.png"
        ]
        labels_path = "C:\\Users\\Admin\\PycharmProjects\\Puzzle\\resources\\Training_Labels.txt"
        create_training_dataset(file_paths, labels_path)
    else:
        print("Setul de date de antrenament a fost incarcat!")

    piece_data = load_training_data(dataset)
    features, labels = preprocess_training_data(piece_data)
    model = RandomForestClassifier(n_estimators=100)
    model.fit(features, labels)

    load_original_button = tk.Button(root, text="Selectează Imaginea Originală", command=load_original_image)
    load_original_button.pack(pady=10)

    load_puzzle_button = tk.Button(root, text="Selectează Imaginea Puzzle", command=load_puzzle_images)
    load_puzzle_button.pack(pady=10)

    # process_puzzle_button = tk.Button(root, text="Procesează Imaginea Puzzle", command=process_puzzle_images)
    # process_puzzle_button.pack(pady=10)

    solve_manual_button = tk.Button(root, text="Rezolvă Puzzle-ul Manual", command=show_manual_solve_window)
    solve_manual_button.pack(pady=10)

    solve_auto_button = tk.Button(root, text="Rezolvă Puzzle-ul Automat", command=show_auto_solve_window)
    solve_auto_button.pack(pady=10)

    settings_button = tk.Button(root, text="Setări", command=show_settings_window)
    settings_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()