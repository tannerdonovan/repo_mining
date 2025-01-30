import json
import requests
import csv
import os


# GitHub Authentication function
def github_auth(url, lsttokens, ct):
    """Handles API authentication and retrieves JSON data from GitHub."""
    jsonData = None
    try:
        ct = ct % len(lsttokens)
        headers = {'Authorization': f'Bearer {lsttokens[ct]}'}
        request = requests.get(url, headers=headers)

        # Check for a valid response
        if request.status_code != 200:
            print(f"GitHub API error {request.status_code}: {request.text}")
            return None, ct

        jsonData = json.loads(request.content)
        ct += 1
    except Exception as e:
        print(f"Error during GitHub API request: {e}")
    return jsonData, ct


# Define valid source file extensions
SOURCE_EXTENSIONS = {".py", ".java", ".cpp", ".c", ".h", ".js", ".ts"}


def is_source_file(filename):
    """Checks if a file is a source file based on its extension."""
    return any(filename.endswith(ext) for ext in SOURCE_EXTENSIONS)


def collect_authors_and_dates(lsttokens, repo, file_list):
    """Retrieves the authors and dates for each source file in the repository."""
    authors_data = {}
    ipage = 1
    ct = 0

    try:
        while True:
            commits_url = f'https://api.github.com/repos/{repo}/commits?page={ipage}&per_page=100'
            json_commits, ct = github_auth(commits_url, lsttokens, ct)

            # Break if API response is invalid or no commits are left
            if not json_commits or isinstance(json_commits, dict):
                print("No more commits or error in response")
                break

            for commit in json_commits:
                sha = commit.get('sha')
                if not sha:
                    continue

                sha_url = f'https://api.github.com/repos/{repo}/commits/{sha}'
                sha_details, ct = github_auth(sha_url, lsttokens, ct)

                if not isinstance(sha_details, dict):
                    print(f"Unexpected response for commit {sha}")
                    continue

                if 'commit' not in sha_details or 'files' not in sha_details:
                    print(f"Skipping commit {sha}: Missing expected data")
                    continue

                author = sha_details['commit'].get('author', {}).get('name', 'Unknown')
                date = sha_details['commit'].get('author', {}).get('date', 'Unknown')

                for file in sha_details['files']:
                    filename = file.get('filename')
                    if filename and is_source_file(filename) and filename in file_list:
                        authors_data.setdefault(filename, []).append((author, date))

            ipage += 1

    except Exception as e:
        print(f"Error receiving data: {e}")

    return authors_data


# Read file list from CollectFiles.py output
repo = 'scottyab/rootbeer'  # Change this for different repos
file_name = f"data/file_{repo.split('/')[1]}.csv"
file_list = []

try:
    with open(file_name, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)  # Skip header safely
        for row in reader:
            if not row:  # Skip empty lines
                continue
            if len(row) < 1:  # Ensure row has at least one column
                print("Skipping malformed row:", row)
                continue
            if is_source_file(row[0]):  # Only include source files
                file_list.append(row[0])

except FileNotFoundError:
    print(f"Error: {file_name} not found. Ensure CollectFiles.py has run successfully.")
    exit(1)

# GitHub tokens
lstTokens = ["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s"]

# Retrieve author and date information
authors_data = collect_authors_and_dates(lstTokens, repo, file_list)

# Save results to CSV
output_file = f"data/authors_{repo.split('/')[1]}.csv"
os.makedirs("data", exist_ok=True)

with open(output_file, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Filename", "Author", "Date"])

    for filename, touches in authors_data.items():
        for author, date in touches:
            writer.writerow([filename, author, date])

print(f"Author data saved to {output_file}")
