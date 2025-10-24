import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from PIL import Image, ImageTk

MAIN_BG = "#0a1835"  
HEADER_BG = "#1e4e89"  
TEXT_COLOR = "#ffffff" 
BUTTON_COLOR = "#1f77b4" 

DATAFILE = "WHO-COVID-19-global-daily-data.csv"

def load_data(path):
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        messagebox.showerror("Error", f"Data file not found: {path}")
        return pd.DataFrame({'Country': [], 'Date_reported': [], 'New_cases': [], 'Cumulative_cases': [], 'New_deaths': [], 'Cumulative_deaths': []})
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load data: {e}")
        return pd.DataFrame({'Country': [], 'Date_reported': [], 'New_cases': [], 'Cumulative_cases': [], 'New_deaths': [], 'Cumulative_deaths': []})

    df['Date_reported'] = pd.to_datetime(df['Date_reported'], errors='coerce')
    df = df.dropna(subset=['Date_reported'])
    df['Country'] = df['Country'].str.strip()
    for col in ['New_cases', 'Cumulative_cases', 'New_deaths', 'Cumulative_deaths']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    df = df.sort_values(['Country', 'Date_reported']).reset_index(drop=True)
    return df

data = load_data(DATAFILE)
countries = sorted(data['Country'].unique())

root = tk.Tk()
root.title("COVID Data Visualizer")
root.geometry("700x550")
root.resizable(False, False)
root.configure(bg=MAIN_BG)



try:
    
    bg_image = Image.open("corona.jpeg")
    bg_image = bg_image.resize((700, 550), Image.Resampling.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)
    
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1) 
except FileNotFoundError:
    
    print("WARNING: Background image 'corona.jpeg' not found. Using a dark solid background.")
    bg_label = tk.Label(root, text="", bg=MAIN_BG)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)


header_band = tk.Label(root, bg=HEADER_BG)
header_band.place(x=0, y=0, relwidth=1, height=50)

title = tk.Label(root, text="COVID Data Visualizer", font=("Helvetica", 18, "bold"),
                 fg=TEXT_COLOR, bg=HEADER_BG, pady=10)
title.place(x=0, y=0, relwidth=1, height=50)



input_band_height = 100
input_band_y = 50 


input_container_bg = "#120841" 
input_container = tk.Frame(root, bg=input_container_bg, height=input_band_height)
input_container.place(x=0, y=input_band_y, relwidth=1)


tk.Label(input_container, text="Country:", font=("Arial", 11, "bold"), fg="#F7F2F2", bg=input_container_bg).place(x=15, y=5)
country_var = tk.StringVar()

style = ttk.Style()
style.theme_use('clam')

style.configure("TCombobox", fieldbackground="#f0f0f0", background="#cccccc", foreground="#333333") 

country_box = ttk.Combobox(input_container, textvariable=country_var, values=countries, state="readonly", width=37, style="TCombobox")
country_box.place(x=15, y=30)


tk.Label(input_container, text="From (YYYY-MM-DD):", font=("Arial", 10, "bold"), fg="#F7F2F2", bg=input_container_bg).place(x=15, y=65)
from_var = tk.StringVar()
from_entry = tk.Entry(input_container, textvariable=from_var, width=25, bg="#f0f0f0", fg="#333333")
from_entry.place(x=15, y=85)


tk.Label(input_container, text="To (YYYY-MM-DD):", font=("Arial", 10, "bold"), fg="#F7F2F2", bg=input_container_bg).place(x=220, y=65)
to_var = tk.StringVar()
to_entry = tk.Entry(input_container, textvariable=to_var, width=25, bg="#f0f0f0", fg="#333333")
to_entry.place(x=220, y=85)



button_y_start = input_band_y + input_band_height + 10 


btn_style_row1 = {
    "font":("Arial", 10, "bold"), 
    "bg":BUTTON_COLOR, 
    "fg":TEXT_COLOR,
    "activebackground":'#1565c0', 
    "activeforeground":TEXT_COLOR, 
    "width":20, 
    "bd":0, 
    "relief":"raised",
    "padx": 5, 
    "pady": 5 
}


btn1 = tk.Button(root, text="Show Graphical Plot", command=lambda: show_plot(), **btn_style_row1)
btn1.place(x=15, y=button_y_start)

btn2= tk.Button(root, text="Show Bar Plot", command=lambda: show_plot1(), **btn_style_row1)
btn2.place(x=230, y=button_y_start)

btn3= tk.Button(root, text="Show Pie Chart", command=lambda: show_plot2(), **btn_style_row1)
btn3.place(x=445, y=button_y_start)


btn4_style = btn_style_row1.copy()

btn4= tk.Button(root, text="Save Analysis", command=lambda: save_analysis(), **btn4_style)
btn4.place(x=15, y=button_y_start + 50)




def get_filtered_df():
    df = data.copy()
    country = country_var.get().strip()
    if not country:
        messagebox.showerror("Error", "Please select a country.")
        return pd.DataFrame()
    df = df[df['Country'] == country]
    try:
        if from_var.get().strip():
            df = df[df['Date_reported'] >= pd.to_datetime(from_var.get().strip())]
        if to_var.get().strip():
            df = df[df['Date_reported'] <= pd.to_datetime(to_var.get().strip())]
    except:
        messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
        return pd.DataFrame()
    return df

def plot_line(df):
    df = df.sort_values('Date_reported').reset_index(drop=True)
    new_cases = df['New_cases'].to_numpy(dtype=float)
    prev = np.roll(new_cases, 1); prev[0] = np.nan
    with np.errstate(divide='ignore', invalid='ignore'):
        df['Growth_pct'] = (new_cases - prev)/prev * 100
    df['MA_Cases'] = df['New_cases'].rolling(7, min_periods=1).mean()
    df['MA_Deaths'] = df['New_deaths'].rolling(7, min_periods=1).mean()
    root.last_df = df
    plt.figure(figsize=(10,6), facecolor="#f5f5f5")
    plt.plot(df['Date_reported'], df['New_cases'], marker='o', label='New Cases', color="#1f77b4")
    plt.plot(df['Date_reported'], df['MA_Cases'], linestyle='--', label='7-day MA Cases', color="#ff7f0e")
    plt.plot(df['Date_reported'], df['New_deaths'], marker='x', label='New Deaths', color="#d62728")
    plt.plot(df['Date_reported'], df['MA_Deaths'], linestyle='--', label='7-day MA Deaths', color="#2ca02c")
    plt.title(f"COVID Trend: {country_var.get()}", fontsize=14, fontweight="bold", color="#333333")
    plt.xlabel("Date", fontsize=12)
    plt.ylabel("Counts", fontsize=12)
    plt.xticks(rotation=30)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_bar(df):
    df = df.sort_values('Date_reported').reset_index(drop=True)
    plt.figure(figsize=(10,6), facecolor="#f5f5f5")
    plt.bar(df['Date_reported'], df['New_cases'], color="#1f77b4", label='New Cases')
    plt.bar(df['Date_reported'], df['New_deaths'], bottom=df['New_cases'], color="#d62728", label='New Deaths')
    plt.title(f"COVID Bar Chart: {country_var.get()}", fontsize=14, fontweight="bold")
    plt.xlabel("Date", fontsize=12)
    plt.ylabel("Counts", fontsize=12)
    plt.xticks(rotation=30)
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_pie(df):
    total_cases = df['Cumulative_cases'].iloc[-1]
    total_deaths = df['Cumulative_deaths'].iloc[-1]
    plt.figure(figsize=(6,6), facecolor="#f5f5f5")
    plt.pie([total_cases-total_deaths, total_deaths], labels=["Recovered/Active", "Deaths"],
             colors=["#1f77b4", "#d62728"], autopct='%1.1f%%', startangle=140, explode=[0.05,0.05])
    plt.title(f"COVID Pie Chart: {country_var.get()}", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.show()

def show_plot():
    df = get_filtered_df()
    if df.empty:
        messagebox.showinfo("No data", "No records found for this selection.")
        return
    plot_line(df)

def show_plot1():
    df = get_filtered_df()
    if df.empty:
        messagebox.showinfo("No data", "No records found for this selection.")
        return
    plot_bar(df)

def show_plot2():
    df = get_filtered_df()
    if df.empty:
        messagebox.showinfo("No data", "No records found for this selection.")
        return
    plot_pie(df)

def save_analysis():
    df = getattr(root, 'last_df', None)
    if df is None or df.empty:
        messagebox.showinfo("Info", "Please plot data first.")
        return
    total_cases = int(df['Cumulative_cases'].iloc[-1])
    total_deaths = int(df['Cumulative_deaths'].iloc[-1])
    avg_daily_cases = float(df['New_cases'].mean())
    avg_growth = float(df['Growth_pct'].dropna().mean())
    save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files","*.txt")])
    if not save_path:
        return
    with open(save_path, 'w') as f:
        f.write(f"COVID Analysis — {country_var.get()}" + ("" if 'Province' in data.columns else "") + "\n")
        f.write(f"Rows used: {len(df)}\n")
        f.write(f"Total Cases: {total_cases}\n")
        f.write(f"Total Deaths: {total_deaths}\n")
        f.write(f"Average Daily Cases: {avg_daily_cases:.2f}\n")
        f.write(f"Average Daily Growth %: {avg_growth:.2f}\n")
    messagebox.showinfo("Saved", f"Analysis saved to:\n{save_path}")

root.mainloop()