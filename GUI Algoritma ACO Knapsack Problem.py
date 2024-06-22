# KELOMPOK 9 SWARM INTELLIGENCE RB

import pandas as pd
import random
import time
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

# Fungsi untuk membaca data dari file Excel
def read_data(filename):
    df = pd.read_excel(filename)
    item_data = {}
    for index, row in df.iterrows():
        item_data[row['Nama Barang']] = {'Vol': int(row['Vol']), 'Berat': int(row['Berat']), 'Profit': int(row['Profit'])}
    return item_data

# Fungsi untuk menginisialisasi feromon
def init_pheromones(item_data):
    pheromones = {item: 1.0 for item in item_data}
    return pheromones

# Fungsi untuk menentukan probabilitas setiap item
def item_probabilities(item_data, pheromones, alpha, beta, knapsack_capacity, current_weight):
    total = sum(pheromones[item] ** alpha * (item_data[item]['Profit'] / item_data[item]['Berat']) ** beta 
                for item in item_data if item_data[item]['Vol'] > 0 and current_weight + item_data[item]['Berat'] <= knapsack_capacity)
    probabilities = {item: (pheromones[item] ** alpha * (item_data[item]['Profit'] / item_data[item]['Berat']) ** beta) / total 
                     for item in item_data if item_data[item]['Vol'] > 0 and current_weight + item_data[item]['Berat'] <= knapsack_capacity}
    return probabilities

# Fungsi untuk membuat solusi dengan ACO
def generate_solution(item_data, pheromones, alpha, beta, knapsack_capacity):
    current_weight = 0
    solution = []
    item_data_copy = {item: item_data[item].copy() for item in item_data}
    while True:
        probabilities = item_probabilities(item_data_copy, pheromones, 
        alpha, beta, knapsack_capacity, current_weight)
        if not probabilities:
            break
        item = random.choices(list(probabilities.keys()), list(probabilities.values()))[0]
        if item_data_copy[item]['Vol'] > 0 and current_weight + item_data_copy[item]['Berat'] <= knapsack_capacity:
            solution.append(item)
            current_weight += item_data_copy[item]['Berat']
            item_data_copy[item]['Vol'] -= 1
    
    return solution

# Fungsi untuk menghitung total profit dari solusi
def total_profit(item_data, solution):
    return sum(item_data[item]['Profit'] for item in solution)

# Fungsi untuk menghitung total berat dari solusi
def total_weight(item_data, solution):
    return sum(item_data[item]['Berat'] for item in solution)

# Fungsi untuk mengupdate feromon
def update_pheromones(pheromones, solution, pheromone_constant, pheromone_evaporation):
    for item in solution:
        pheromones[item] = (1 - pheromone_evaporation) * pheromones[item] + pheromone_constant

# Fungsi untuk mencari solusi terbaik
def find_best_solution(item_data, pheromones, alpha, beta, knapsack_capacity, num_ants, num_iterations, pheromone_evaporation, pheromone_constant):
    best_solution = []
    best_profit = 0
    best_weight = 0
    stagnation_count = 0
    max_stagnation = 100  # Maximum number of iterations without improvement
    
    for iter in range(num_iterations):
        solutions = [generate_solution(item_data, pheromones, alpha, beta, knapsack_capacity) for _ in range(num_ants)]
        valid_solutions = [sol for sol in solutions if total_weight(item_data, sol) <= knapsack_capacity]
        
        if not valid_solutions:
            continue
        
        profits = {tuple(solution): total_profit(item_data, solution) for solution in valid_solutions}
        
        best_solution_in_iteration = max(profits, key=profits.get)
        if profits[best_solution_in_iteration] > best_profit:
            best_solution = list(best_solution_in_iteration)
            best_profit = profits[best_solution_in_iteration]
            best_weight = total_weight(item_data, best_solution)
            stagnation_count = 0  # Reset stagnation count
        else:
            stagnation_count += 1
        
        if stagnation_count >= max_stagnation:
            break
        
        for solution in valid_solutions:
            update_pheromones(pheromones, solution, pheromone_constant, pheromone_evaporation)
    
    return best_solution, best_profit, best_weight, iter

# Fungsi untuk merangkum solusi terbaik
def summarize_solution(solution):
    summary = {}
    for item in solution:
        if item in summary:
            summary[item] += 1
        else:
            summary[item] = 1
    return summary

# Fungsi untuk menjalankan ACO dan menampilkan output
def start_aco():
    try:
        filename = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        item_data = read_data(filename)
        
        knapsack_capacity = int(capacity_entry.get())
        num_ants = int(ants_entry.get())
        num_iterations = int(iterations_entry.get())
        
        # Parameter yang tidak dapat diubah oleh pengguna
        pheromone_evaporation = 0.1
        pheromone_constant = 100
        alpha = 1
        beta = 2
        
        start_time = time.time()
        best_solution, best_profit, best_weight, iter = find_best_solution(item_data, 
        init_pheromones(item_data), alpha, beta, knapsack_capacity, num_ants, 
        num_iterations, pheromone_evaporation, pheromone_constant)
        end_time = time.time()
        
        best_solution_summary = summarize_solution(best_solution)
        
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Iterasi: {iter + 1}\n")
        result_text.insert(tk.END, f"Runtime: {end_time - start_time:.2f} seconds\n")
        result_text.insert(tk.END, f"Profit: {best_profit * 1000:.2f}\n")
        result_text.insert(tk.END, f"Berat: {best_weight} kg\n")
        result_text.insert(tk.END, "Solusi terbaik:\n")
        for item, count in best_solution_summary.items():
            result_text.insert(tk.END, f"{item}: {count}\n")
    except Exception as e:
        messagebox.showerror("Error", str(e))


# GUI ACO
root = tk.Tk()
root.title("ACO for Knapsack Problem (SI Kelompok 9)")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

tk.Label(frame, text="Knapsack Capacity:").grid(row=0, column=0, sticky=tk.W)
capacity_entry = tk.Entry(frame)
capacity_entry.grid(row=0, column=1)
capacity_entry.insert(tk.END, " ")

tk.Label(frame, text="Number of Ants:").grid(row=1, column=0, sticky=tk.W)
ants_entry = tk.Entry(frame)
ants_entry.grid(row=1, column=1)
ants_entry.insert(tk.END, " ")

tk.Label(frame, text="Number of Iterations:").grid(row=2, column=0, sticky=tk.W)
iterations_entry = tk.Entry(frame)
iterations_entry.grid(row=2, column=1)
iterations_entry.insert(tk.END, " ")

start_button = tk.Button(frame, text="Start ACO", command=start_aco)
start_button.grid(row=3, columnspan=2, pady=10)

result_text = ScrolledText(frame, width=50, height=40)
result_text.grid(row=4, columnspan=2)

root.mainloop()
