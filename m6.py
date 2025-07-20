import tkinter as tk
from tkinter import filedialog
from pygame import mixer
import pygame
from PIL import Image, ImageTk
import os
import random
import time
from mutagen.mp3 import MP3
root = tk.Tk()
root.title("Music Player")
root.geometry("920x620+290+90")
root.resizable(False, False)

mixer.init()
pygame.init()

paused = False
current_song_length = 0
current_position = 0
song_start_time = 0
is_playing = False
manual_control = False 
repeat_mode = 0
song_ended = False

canvas = tk.Canvas(root, width=920, height=750)
canvas.pack(fill="both", expand=True)

#funtion region

def create_gradient(canvas, color1, color2):
    for i in range(750):
        r = int(color1[1:3], 16) + (int(color2[1:3], 16) - int(color1[1:3], 16)) * i // 750
        g = int(color1[3:5], 16) + (int(color2[3:5], 16) - int(color1[3:5], 16)) * i // 750
        b = int(color1[5:7], 16) + (int(color2[5:7], 16) - int(color1[5:7], 16)) * i // 750
        color = f"#{r:02x}{g:02x}{b:02x}"
        canvas.create_line(0, i, 920, i, fill=color)

root.after(0, create_gradient, canvas,"#73B6E5", "#8FC2DE")  
pygame.init()
mixer.init()
root.configure(bg="#256B84")

def get_song_duration(file_path):
    try:
        if file_path.lower().endswith('.mp3'):
            audio_file = MP3(file_path)
            return audio_file.info.length
        elif file_path.lower().endswith(('.wav', '.ogg', '.flac', '.m4a')):
            from mutagen import File
            audio_file = File(file_path)
            if audio_file is not None and audio_file.info is not None:
                return audio_file.info.length
        
        try:
            mixer.music.load(file_path)
            return 0
        except Exception:
            return 0
    except Exception as e:
        print(f"Error getting duration for {file_path}: {e}")
        return 0
    
def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes}:{seconds:02d}"

def open_folder():          
    path = filedialog.askdirectory(title="Select Music Folder") 
    if path:  
        try:
            os.chdir(path) 
            playlist.delete(0, "end") 
            songs = os.listdir(path)
            for song in songs:
                if song.lower().endswith(('.mp3', '.wav', '.ogg')): 
                    playlist.insert("end", song)
        except Exception as e:
            print(f"Error: {e}")

def update_progress():
    global current_position, current_song_length, song_start_time, is_playing, manual_control, song_ended
    
    if is_playing and not paused and not song_ended:
        if mixer.music.get_busy():
            current_position = time.time() - song_start_time
            
            if current_song_length > 0:
                if current_position >= current_song_length:
                    current_position = current_song_length
                    song_ended = True
                    handle_song_end()
                    root.after(1000, update_progress)
                    return
                    
                progress_percentage = current_position / current_song_length
                bar_width = 294 * progress_percentage 
                progress_bar.coords(progress_line, 0, 0, bar_width, 10)
            
            current_time_label.config(text=format_time(current_position))
            if current_song_length > 0:
                total_time_label.config(text=format_time(current_song_length))
            else:
                total_time_label.config(text="--:--")
                  
        else:
            if not manual_control and not song_ended:
                song_ended = True
                handle_song_end()
                root.after(1000, update_progress)
                return
    
    if is_playing:
        current_time_label.config(text=format_time(current_position))
        if current_song_length > 0:
            total_time_label.config(text=format_time(current_song_length))
        else:
            total_time_label.config(text="--:--")
    else:
        current_time_label.config(text="0:00")
        total_time_label.config(text="0:00")
    
    manual_control = False
    root.after(1000, update_progress)

def handle_song_end():
    global repeat_mode, song_ended, is_playing
    
    if not song_ended:
        return
        
    if repeat_mode == 1:
        repeat_current_song()
    elif repeat_mode == 2:
        auto_next_song()
    else:
        auto_next_song()

def auto_next_song():
    global is_playing, manual_control, repeat_mode, song_ended
    try:
        if playlist.size() > 0:
            current_selection = playlist.curselection()
            if current_selection:
                next_index = (current_selection[0] + 1) % playlist.size()
                
                if repeat_mode == 0 and current_selection[0] == playlist.size() - 1:
                    stop_song()
                    return
                    
            else:
                next_index = 0
            
            playlist.selection_clear(0, tk.END)
            playlist.selection_set(next_index)
            playlist.activate(next_index)
            
            manual_control = False
            song_ended = False
            play_song()
    except Exception as e:
        print(f"Error in auto_next_song: {e}")
        is_playing = False

def repeat_current_song():
    global manual_control, song_ended
    try:
        current_selection = playlist.curselection()
        if current_selection and playlist.size() > 0:
            manual_control = False
            song_ended = False
            play_song()
    except Exception as e:
        print(f"Error in repeat_current_song: {e}")

def play_song():
    global paused, current_song_length, song_start_time, current_position, is_playing, manual_control, song_ended
    try:
        current_selection = playlist.curselection()
        if not current_selection:
            return
            
        music = playlist.get(current_selection[0])
        
        mixer.music.stop()
        
        current_song_length = get_song_duration(music)
        
        if current_song_length <= 0:
            try:
                mixer.music.load(music)
                current_song_length = 0
            except Exception as e:
                print(f"Error loading song {music}: {e}")
                return
        
        mixer.music.load(music)
        mixer.music.play()

        song_start_time = time.time()
        current_position = 0
        is_playing = True
        paused = False
        song_ended = False
        
        display_name = music[:30] + "..." if len(music) > 30 else music
        music_label.config(text=display_name)
        pause_btn.config(text="⏸")
        
        progress_bar.coords(progress_line, 0, 0, 0, 15)
        
        if current_song_length > 0:
            total_time_label.config(text=format_time(current_song_length))
        else:
            total_time_label.config(text="--:--")
        
        current_time_label.config(text="0:00")
        
    except Exception as e:
        print(f"Error playing song: {e}")
        is_playing = False

def next_song():
    global manual_control, song_ended
    manual_control = True
    song_ended = False
    try:
        current_selection = playlist.curselection()
        if current_selection:
            next_index = (current_selection[0] + 1) % playlist.size()
        else:
            next_index = 0
            
        if playlist.size() > 0:
            playlist.selection_clear(0, tk.END)
            playlist.selection_set(next_index)
            playlist.activate(next_index)
            play_song()
    except Exception as e:
        print(f"Error in next_song: {e}")

def previous_song():
    global manual_control, song_ended
    manual_control = True
    song_ended = False
    try:
        current_selection = playlist.curselection()
        if current_selection:
            prev_index = (current_selection[0] - 1) % playlist.size()
        else:
            prev_index = playlist.size() - 1 if playlist.size() > 0 else 0
            
        if playlist.size() > 0:
            playlist.selection_clear(0, tk.END)
            playlist.selection_set(prev_index)
            playlist.activate(prev_index)
            play_song()
    except Exception as e:
        print(f"Error in previous_song: {e}")

def shuffle_song():
    global manual_control, song_ended
    manual_control = True
    song_ended = False
    try:
        if playlist.size() > 0:
            next_index = random.randint(0, playlist.size() - 1)
            playlist.selection_clear(0, tk.END)
            playlist.selection_set(next_index)
            playlist.activate(next_index)
            play_song()
    except Exception as e:
        print(f"Error in shuffle_song: {e}")

def toggle_repeat():
    global repeat_mode
    repeat_mode = (repeat_mode + 1) % 3
    
    if repeat_mode == 0:
        repeat_btn.config(text="🔁", bg="#795548")
        status_label.config(text="Repeat: Off", bg="#2E4092")
    elif repeat_mode == 1:
        repeat_btn.config(text="🔂", bg="#4CAF50")
        status_label.config(text="Repeat: Single", bg="#2E4092")
    else:
        repeat_btn.config(text="🔁", bg="#2196F3")
        status_label.config(text="Repeat: Playlist", bg="#2E4092")

def pause_resume():
    global paused, song_start_time, current_position, manual_control, song_ended
    manual_control = True
    song_ended = False
    
    if is_playing:
        # if mixer.music.get_busy():
            if not paused:
                mixer.music.pause()
                pause_btn.config(text="▶")
                paused = True
                current_position = time.time() - song_start_time
            else:
                mixer.music.unpause()
                pause_btn.config(text="⏸")
                paused = False
                song_start_time = time.time() - current_position
        # else:
        #     if playlist.curselection():
        #         play_song()
    else:
        if playlist.curselection():
            play_song()

def stop_song():
    global is_playing, current_position, current_song_length, paused, manual_control, song_ended
    manual_control = True
    song_ended = False
    mixer.music.stop()
    is_playing = False
    paused = False
    current_position = 0
    current_song_length = 0
    progress_bar.coords(progress_line, 0, 0, 0, 10)
    current_time_label.config(text="0:00")
    total_time_label.config(text="0:00")
    music_label.config(text="No music selected")
    pause_btn.config(text="⏸")

def set_volume(val):
    volume = float(val) / 100
    mixer.music.set_volume(volume)
    volume_label.config(text=f"Volume: {val}%")

try:
    icon_image = Image.new('RGB', (64, 64), color='blue')
    image_icon = ImageTk.PhotoImage(icon_image)
    root.iconphoto(True, image_icon)
except Exception as e:
    print(f"Could not set icon: {e}")
def on_playlist_select(event):
    selection = playlist.curselection()
    if selection:
        song_name = playlist.get(selection[0])
        try:
            duration = get_song_duration(song_name)
            if duration > 0:
                duration_text = f" ({format_time(duration)})"
            else:
                duration_text = " (--:--)"
            
            info_text = f"{song_name[:30]}{'...' if len(song_name) > 30 else ''}{duration_text}"
            print(info_text)
            
        except Exception as e:
            print(f"Error getting info for {song_name}: {e}")

def on_playlist_double_click(event):
    global manual_control, song_ended
    manual_control = True
    song_ended = False
    selection = playlist.curselection()
    if selection:
        playlist.activate(selection[0])
        play_song()    
      
control_area_x = 470
control_area_width = 300
playlist_area_x = 50
playlist_area_width = 350

label = tk.Label(root,text = "Welcome to Music Player", font= ("arial",12,"bold"),bg ="#73B6E5",fg = "black",highlightbackground="black",highlightthickness=1)
label.place(x= 460 , y =80,anchor= "center")

control_frame = tk.Frame(root, bg="#73B6E5", relief="flat", bd=2,highlightbackground="black",highlightthickness=1)
control_frame.place(x=control_area_x-20, y=190, width=control_area_width, height=300)

control_title = tk.Label(control_frame, text="Music Controls", font=("Arial", 12,"bold"),fg="black",bg ="#73B6E5",highlightbackground="black",highlightthickness=1)
control_title.place(x=148, y=20, anchor="center")

progress_bar = tk.Canvas(control_frame, height=10, bg="#5fb0d2",bd=0, relief="flat", highlightbackground="black", highlightthickness=1)
progress_bar.place(x=30, y=125, width=control_area_width-65, height=10)
progress_line = progress_bar.create_rectangle(0, 0, 0,15, fill="green", outline="black")

current_time_label = tk.Label(control_frame, text="0:00", font=("Arial", 8), fg="black", bg="#73B6E5", highlightbackground="black", highlightthickness=1)
current_time_label.place(x=1,y =120)

total_time_label = tk.Label(control_frame, text="0:00", font=("Arial", 8), fg="black", bg="#73B6E5", highlightbackground="black", highlightthickness=1)
total_time_label.place(x= 266,y = 120)

music_label = tk.Label(control_frame, text="No music selected", font=("Arial", 10), fg="#2c3e50", bg="white", wraplength=280, relief="flat", bd=1,pady =2,highlightbackground="black",highlightthickness=1)
music_label.place(x=150, y=70, anchor="center")

play_btn = tk.Button(control_frame, text="🎵", font=("Arial", 12), bg="#4CAF50", fg="white", bd=2, relief="raised", width=3, height=1, command=play_song, highlightbackground="black",highlightthickness=1)
play_btn.place(x=240, y=220)

prev_btn = tk.Button(control_frame, text="⏮", font=("Arial", 12), bg="#9C27B0", fg="white", 
                    bd=2, relief="raised", width=3, height=1, command=previous_song,highlightbackground="black",highlightthickness=1)
prev_btn.place(x=50, y=160)

next_btn = tk.Button(control_frame, text="⏭", font=("Arial", 12), bg="#9C27B0", fg="white", 
                    bd=2, relief="raised", width=3, height=1, command=next_song,highlightbackground="black",highlightthickness=1)
next_btn.place(x=210, y=160)

stop_btn = tk.Button(control_frame, text="⏹", font=("Arial", 12), bg="#f44336", fg="white", 
                    bd=2, relief="raised", width=3, height=1, command=stop_song,highlightbackground="black",highlightthickness=1)
stop_btn.place(x=30, y=220)

pause_btn = tk.Button(control_frame, text="⏸", font=("Arial", 12), bg="#FF9800", fg="white", 
                     bd=2, relief="raised", width=3, height=1, command=pause_resume,highlightbackground="black",highlightthickness=1)
pause_btn.place(x=130, y=160)

shuffle_btn = tk.Button(control_frame, command=shuffle_song, text="🔀", font=("Arial", 12), bg="#795548", fg="white", 
                       bd=2, relief="raised", width=3, height=1,highlightbackground="black",highlightthickness=1)
shuffle_btn.place(x=100, y=220)

repeat_btn = tk.Button(control_frame, command=toggle_repeat, text="🔁", font=("Arial", 12), bg="#795548", fg="white", 
                      bd=2, relief="raised", width=3, height=1,highlightbackground="black",highlightthickness=1)
repeat_btn.place(x=170, y=220)

status_label = tk.Label(control_frame, text="Repeat: Off", font=("Arial",7, "bold"), fg="black", bg="#73B6E5")
status_label.place(x=160,y=260)

music_frame = tk.Frame(root, bd=2, relief="flat", bg="#36D3EB", highlightbackground="black", highlightthickness=2)
music_frame.place(x=playlist_area_x, y=185, width=playlist_area_width, height=306)
open_folder_btn = tk.Button(music_frame, text="Add Music", width=15, height=1,fg = "black", font=("Arial", 10, "bold"), bg="#E0E035", 
                            bd=2, relief="raised", command=open_folder, highlightbackground="black", highlightthickness=1)
open_folder_btn.pack(side="top")

scroll = tk.Scrollbar(music_frame, bg="#55D5D5", troughcolor="#1F1616", width=16, bd=1, relief="flat")
playlist = tk.Listbox(music_frame, font=("Arial",10), bg="#0E0F10", fg="#dce4ec", selectbackground="#4E9AC3", selectforeground="#d3e5d9",
                      cursor="hand2", bd=1, yscrollcommand=scroll.set, activestyle="none", relief="flat")
scroll.config(command=playlist.yview)
scroll.pack(side="right", fill="y")
playlist.pack(side="top", fill="both", expand=True)
 
volume_frame = tk.Frame(root, bg="#73B6E5", relief="flat", bd=2, highlightbackground="black", highlightthickness=1)
volume_frame.place(x=control_area_x +300, y=290, width=78, height=200)

volume_label = tk.Label(volume_frame, text="Volume: 70%", font=("Arial", 7,"bold"), fg="#090909", bg="#73B6E5")
volume_label.place(x=0, y=1)

volume_scale = tk.Scale(volume_frame, from_=100, to=0, orient=tk.VERTICAL, bg="#73B6E5", fg="black", length=150, width=5, command=set_volume,highlightbackground="black",highlightthickness=1)
volume_scale.set(70)  
volume_scale.place(x=34, y=20)

def volume_up():
    current_vol = volume_scale.get()
    new_vol = min(100, current_vol + 10)
    volume_scale.set(new_vol)

def volume_down():
    current_vol = volume_scale.get()
    new_vol = max(0, current_vol - 10)
    volume_scale.set(new_vol)

vol_down_btn = tk.Button(volume_frame, text="🔉", font=("Arial", 13), bg="#73B6E5", fg="black",
                        bd=1, relief="raised", width=2, height=1, command=volume_down, highlightbackground="black", highlightthickness=1)
vol_down_btn.place(x=10, y=142)

vol_up_btn = tk.Button(volume_frame, text="🔊", font=("Arial", 13), bg="#73B6E5", fg="black",
                      bd=1, relief="raised", width=2, height=1, command=volume_up, highlightbackground="black", highlightthickness=1)
vol_up_btn.place(x=10, y=20)

update_progress()

root.mainloop()