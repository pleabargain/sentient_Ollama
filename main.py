import tkinter as tk
from tkinter import filedialog, messagebox
import asyncio
from sentient import sentient
import random
import time
import csv
import re
from datetime import datetime
import os
import subprocess

class SentientURLSearch:
    def __init__(self, master):
        self.master = master
        master.title("Sentient URL Search")

        self.url_file_path = tk.StringVar(value="/home/dgd/Documents/sentient_Ollama/searchURLs.txt")
        self.search_terms_file_path = tk.StringVar(value="/home/dgd/Documents/sentient_Ollama/searchterms.txt")
        self.output_file_path = tk.StringVar(value=self.get_default_output_path())
        self.min_pause = tk.IntVar(value=5)
        self.max_pause = tk.IntVar(value=10)

        # URL file selection
        tk.Label(master, text="URL File:").grid(row=0, column=0, sticky="e")
        tk.Entry(master, textvariable=self.url_file_path, width=50).grid(row=0, column=1)
        tk.Button(master, text="Browse", command=self.browse_url_file).grid(row=0, column=2)

        # Search terms file selection
        tk.Label(master, text="Search Terms File:").grid(row=1, column=0, sticky="e")
        tk.Entry(master, textvariable=self.search_terms_file_path, width=50).grid(row=1, column=1)
        tk.Button(master, text="Browse", command=self.browse_search_terms_file).grid(row=1, column=2)

        # Output CSV file selection
        tk.Label(master, text="Output CSV File:").grid(row=2, column=0, sticky="e")
        tk.Entry(master, textvariable=self.output_file_path, width=50).grid(row=2, column=1)
        tk.Button(master, text="Browse", command=self.browse_output_file).grid(row=2, column=2)

        # Pause time inputs
        tk.Label(master, text="Min Pause (seconds):").grid(row=3, column=0, sticky="e")
        tk.Entry(master, textvariable=self.min_pause, width=10).grid(row=3, column=1, sticky="w")
        tk.Label(master, text="Max Pause (seconds):").grid(row=4, column=0, sticky="e")
        tk.Entry(master, textvariable=self.max_pause, width=10).grid(row=4, column=1, sticky="w")

        # Start button
        tk.Button(master, text="Start Search", command=self.start_search).grid(row=5, column=1)

        # Progress bar
        self.progress = tk.DoubleVar()
        self.progress_bar = tk.Scale(master, variable=self.progress, from_=0, to=100, orient=tk.HORIZONTAL, length=300, state='disabled')
        self.progress_bar.grid(row=6, column=0, columnspan=3)

    def get_default_output_path(self):
        current_date = datetime.now().strftime("%S.%d.%m")
        return f"/home/dgd/Documents/sentient_Ollama/{current_date}output.csv"

    def browse_url_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if filename:
            self.url_file_path.set(filename)

    def browse_search_terms_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if filename:
            self.search_terms_file_path.set(filename)

    def browse_output_file(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if filename:
            self.output_file_path.set(filename)

    def start_search(self):
        url_file = self.url_file_path.get()
        search_terms_file = self.search_terms_file_path.get()
        output_file = self.output_file_path.get()
        min_pause = self.min_pause.get()
        max_pause = self.max_pause.get()

        if not os.path.exists(url_file) or not os.path.exists(search_terms_file):
            messagebox.showerror("Error", "Input files not found. Please check the file paths.")
            return

        try:
            with open(url_file, 'r') as f:
                urls = f.read().splitlines()
            with open(search_terms_file, 'r') as f:
                search_terms = f.read().splitlines()
        except IOError as e:
            messagebox.showerror("Error", f"Error reading input files: {str(e)}")
            return

        asyncio.run(self.perform_searches(urls, search_terms, output_file, min_pause, max_pause))

    async def perform_searches(self, urls, search_terms, output_file, min_pause, max_pause):
        total_searches = len(urls) * len(search_terms)
        completed_searches = 0

        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(['URL', 'search_term', 'string_found'])

                for url in urls:
                    for term in search_terms:
                        goal = f"Go to {url} and search for '{term}'. Return the full sentence or paragraph containing the search term, including punctuation before and after."
                        try:
                            result = await sentient.invoke(
                                goal=goal,
                                provider="ollama",
                                model="llama3.1:latest"
                            )
                            
                            string_found = self.extract_string_with_term(result, term)
                            
                            if string_found:
                                csvwriter.writerow([url, term, string_found])
                                print(f"Found '{term}' on {url}: {string_found}")
                            else:
                                print(f"Could not find '{term}' on {url}")
                                csvwriter.writerow([url, term, "Term not found"])
                        
                        except Exception as e:
                            error_message = str(e)
                            print(f"Error searching {url} for '{term}': {error_message}")
                            csvwriter.writerow([url, term, f"Error: {error_message}"])
                            
                            if "ECONNREFUSED" in error_message:
                                await self.handle_connection_error()
                                return

                        # Update progress
                        completed_searches += 1
                        self.update_progress(completed_searches / total_searches * 100)

                        # Random pause between searches
                        pause_time = random.uniform(min_pause, max_pause)
                        print(f"Pausing for {pause_time:.2f} seconds...")
                        time.sleep(pause_time)

            print(f"Search process completed. Results saved to {output_file}")
            messagebox.showinfo("Complete", f"Search process completed. Results saved to {output_file}")
        except Exception as e:
            error_message = f"An error occurred during the search process: {str(e)}"
            print(error_message)
            messagebox.showerror("Error", error_message)

    async def handle_connection_error(self):
        error_message = (
            "Failed to connect to the browser. Please ensure that a browser is running in debug mode on port 9222.\n\n"
            "For Chrome on Linux, use the command:\n"
            "google-chrome --remote-debugging-port=9222\n\n"
            "For Brave on Linux, use the command:\n"
            "brave-browser --remote-debugging-port=9222 --guest"
        )
        print("\nERROR: " + error_message)
        
        user_input = input("\nWould you like to attempt to start the browser in debug mode? (y/n): ").lower()
        if user_input == 'y':
            print("\nWARNING: This will execute a command to start a browser in debug mode. "
                  "Make sure you trust the source of this script before proceeding.")
            browser_choice = input("Which browser would you like to start? (chrome/brave): ").lower()
            
            if browser_choice == 'chrome':
                command = "google-chrome --remote-debugging-port=9222"
            elif browser_choice == 'brave':
                command = "brave-browser --remote-debugging-port=9222 --guest"
            else:
                print("Invalid choice. Please start the browser manually using the commands provided above.")
                return
            
            try:
                subprocess.Popen(command, shell=True)
                print(f"Attempting to start {browser_choice} in debug mode. Please wait a moment and then try your search again.")
            except Exception as e:
                print(f"Failed to start the browser: {str(e)}")
        else:
            print("Please start the browser manually using the commands provided above.")

    def extract_string_with_term(self, text, term):
        pattern = r'([^.!?\n]*\b{}\b[^.!?\n]*)'.format(re.escape(term))
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None

    def update_progress(self, value):
        self.progress.set(value)
        self.master.update_idletasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = SentientURLSearch(root)
    root.mainloop()