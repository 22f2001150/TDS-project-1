import requests
import csv

# Use your GitHub token here
GITHUB_TOKEN = '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'
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}
BASE_URL = "https://api.github.com"

# Step 4.1: Define functions to get users and repositories
def fetch_users():
    url = f"{BASE_URL}/search/users?q=location:Sydney+followers:>100"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json().get('items', [])

def fetch_user_details(login):
    url = f"{BASE_URL}/users/{login}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def fetch_user_repos(login):
    url = f"{BASE_URL}/users/{login}/repos?per_page=500"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

# Step 4.2: Process and save users data
def process_user_data(users):
    user_data = []
    for user in users:
        details = fetch_user_details(user['login'])
        user_data.append({
            'login': details.get('login', ''),
            'name': details.get('name', ''),
            'company': details.get('company', '').strip().lstrip('@').upper() if details.get('company') else '',
            'location': details.get('location', ''),
            'email': details.get('email', ''),
            'hireable': details.get('hireable', ''),
            'bio': details.get('bio', ''),
            'public_repos': details.get('public_repos', 0),
            'followers': details.get('followers', 0),
            'following': details.get('following', 0),
            'created_at': details.get('created_at', '')
        })
    return user_data

# Step 4.3: Process and save repositories data
def process_repositories_data(users):
    repos_data = []
    for user in users:
        if 'login' not in user:
            continue  # Skip if 'login' key is missing
        repos = fetch_user_repos(user['login'])
        for repo in repos:
            if not repo:  # Skip None repos
                continue
            license_info = repo.get('license') if repo.get('license') else {}
            repos_data.append({
                'login': user['login'],
                'full_name': repo.get('full_name', ''),
                'created_at': repo.get('created_at', ''),
                'stargazers_count': repo.get('stargazers_count', 0),
                'watchers_count': repo.get('watchers_count', 0),
                'language': repo.get('language', ''),
                'has_projects': repo.get('has_projects', False),
                'has_wiki': repo.get('has_wiki', False),
                'license_name': license_info.get('key', '')  # Safely get 'key' from license_info
            })
    return repos_data

# Step 4.4: Write data to CSV files
def write_to_csv(filename, data, fieldnames):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

# Run the steps
if __name__ == "__main__":
    # Get users with over 100 followers
    users = fetch_users()
    user_data = process_user_data(users)
    if user_data:
        write_to_csv("users.csv", user_data, fieldnames=user_data[0].keys())

    # Get repository data
    repos_data = process_repositories_data(user_data)
    if repos_data:
        write_to_csv("repositories.csv", repos_data, fieldnames=repos_data[0].keys())
