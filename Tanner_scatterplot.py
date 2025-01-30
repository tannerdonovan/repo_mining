import matplotlib
matplotlib.use('TkAgg')  # Set the backend for interactive plotting

import csv
import matplotlib.pyplot as plt
import math
from datetime import datetime

CSV_FILENAME = "data/authors_rootbeer.csv"

def parse_date(date_str):
    date_str = date_str.replace("Z", "")  # Remove the 'Z' if present
    return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")

def main():
    """Main function to read commit data, process it, and generate the scatter plot."""
    commits = []

    # Read commit data from CSV
    with open(CSV_FILENAME, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dt = parse_date(row["Date"])  # Parse the commit date
            commits.append({
                "filename": row["Filename"],
                "author": row["Author"],
                "date_dt": dt
            })

    # Calculate the earliest commit date (start of the project)
    earliest = min(c["date_dt"] for c in commits)

    # Calculate the weeks since the start for each commit
    for c in commits:
        c["weeks_since_start"] = (c["date_dt"] - earliest).days / 7.0

    # Get unique filenames and authors
    files = sorted({c["filename"] for c in commits})
    file_index = {f: i for i, f in enumerate(files)}  # Map files to indices
    authors = sorted({c["author"] for c in commits})  # Unique list of authors

    # Create a color map for authors (adjusted for deprecation warning)
    cmap = plt.get_cmap("tab20", len(authors))
    color_map = {a: cmap(i) for i, a in enumerate(authors)}

    # Create the scatter plot
    plt.figure(figsize=(10, 7))
    for c in commits:
        x = file_index[c["filename"]]  # Get x position of file
        y = c["weeks_since_start"]  # Get y position of file
        plt.scatter(x, y, color=color_map[c["author"]], alpha=0.8, s=30)

    # Labels and title
    plt.xlabel("File")  # X-axis will now show the file index (integer)
    plt.ylabel("Weeks")
    plt.title("File Touches Over Time by Author")

    # Set x-ticks to match the number of files (integer values)
    max_x = len(files) - 1
    plt.xticks(range(0, max_x + 1, 2))  # Display integers for file indices

    # Set y-ticks with appropriate intervals
    max_y = max(c["weeks_since_start"] for c in commits)
    max_y_rounded = int(math.ceil(max_y / 50.0) * 50)
    plt.yticks(range(0, max_y_rounded + 1, 50))

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
