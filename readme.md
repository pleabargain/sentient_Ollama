# Sentient URL Search

This script provides a graphical user interface for performing automated searches on multiple URLs using specified search terms.

## Features

- Select a file containing URLs to search
- Select a file containing search terms
- Set minimum and maximum pause times between searches
- Automated searching using the Sentient AI library

## Requirements

- Python 3.7+
- tkinter
- asyncio
- sentient
- random
- time

## Setting up a Virtual Environment

To set up and use a virtual environment for this project, follow these steps:

1. Open a terminal and navigate to the project directory.

2. Create a new virtual environment:
   ```
   python3 -m venv venv
   ```

3. Activate the virtual environment:
   - On macOS and Linux:
     ```
     source venv/bin/activate
     ```
   - On Windows:
     ```
     venv\Scripts\activate
     ```

4. Install the required packages:
   ```
   pip3 install asyncio sentient
   ```

5. When you're done working on the project, deactivate the virtual environment:
   ```
   deactivate
   ```

## Usage

1. Activate the virtual environment (see steps above)
2. Run the script: `python3 main.py`
3. In the GUI:
   - Click "Browse" to select the URL file (a text file with one URL per line)
   - Click "Browse" to select the search terms file (a text file with one search term per line)
   - Set the minimum and maximum pause times (in seconds) between searches
   - Click "Start Search" to begin the automated search process
4. The script will perform searches for each combination of URL and search term, with random pauses between searches
5. Results and progress will be printed to the console
6. A completion message will be shown when all searches are finished

## Note

This script uses the Sentient AI library with the Ollama provider and the llama3.1 model. Make sure you have the necessary permissions and resources to use these services.

"""

with open("README.md", "w") as readme_file:
    readme_file.write(readme_content)