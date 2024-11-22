import os
from github import Github
from datetime import datetime, timedelta
import json
def write_to_file(content, base_filename='thats-a-wrap-'):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')  # current date and time as a string
    filename = f"{base_filename}_{timestamp}.html"
    try:
        with open(filename, 'w') as f:
            f.write(content)
    except Exception as e:
        print(f"An error occurred while writing to the file: {str(e)}") 
def get_github_instance():
    """
    Initializes and returns a Github instance.
    If a GITHUB_TOKEN is found in environment variables, uses it for authentication.
    Otherwise, initializes an anonymous instance.
    """
    token = os.getenv('GITHUB_TOKEN')
    if token:
        print("Authenticated with GitHub token.")
        return Github(token)
    else:
        print("No GitHub token found. Using anonymous access.")
        return Github()  # Anonymous access

def configure_search_parameters():
    """
    Configures the search parameters. Modify these variables as needed.
    """
    search_params = {
        'username': 'ranfysvalle02',           # GitHub username to search
        'language': 'Python',            # Primary language of repositories
        'min_stars': 1,                 # Minimum number of stars
        'updated_within_months': 12       # Repositories updated within the last N months
    }
    return search_params

def search_repositories_pygithub(github_instance, search_params):
    """
    Searches through the specified user's public repositories based on the provided search parameters.
    """
    username = search_params['username']
    try:
        user = github_instance.get_user(username)
    except Exception as e:
        print(f"Error fetching user '{username}': {e}")
        return []

    public_repos = user.get_repos(type='public')

    # Calculate the cutoff date for recent updates
    since_date = datetime.now() - timedelta(days=30 * search_params['updated_within_months'])

    matching_repos = []

    for repo in public_repos:
        # Check for primary language
        if repo.language != search_params['language']:
            continue

        # Check for minimum stars
        if repo.stargazers_count < search_params['min_stars']:
            continue

        # Check for recent updates
        if repo.updated_at < since_date:
            continue

        # If all conditions are met, add to the list
        matching_repos.append({
            'name': repo.name,
            'description': repo.description,
            'stars': repo.stargazers_count,
            'forks': repo.forks_count,
            'language': repo.language,
            'updated_at': repo.updated_at.strftime('%Y-%m-%d'),
            'url': repo.html_url
        })

    return matching_repos

def display_repositories(repos, username):
    """
    Displays the list of matching repositories in a readable format.
    """
    if not repos:
        print(f"No repositories match the given criteria for user '{username}'.")
        return

    print(f"\nFound {len(repos)} matching repositories for user '{username}':\n")
    for repo in repos:
        print(f"Name        : {repo['name']}")
        print(f"Description : {repo['description'] or 'No description provided.'}")
        print(f"Stars       : {repo['stars']} ⭐")
        print(f"Forks       : {repo['forks']}")
        print(f"Language    : {repo['language']}")
        print(f"Updated At  : {repo['updated_at']}")
        print(f"URL         : {repo['url']}")
        print("-" * 60)

def main():
    """
    Main function to execute the search.
    """
    # Initialize GitHub instance
    github_instance = get_github_instance()

    # Configure search parameters
    search_params = configure_search_parameters()

    # Search repositories
    matching_repos = search_repositories_pygithub(github_instance, search_params)

    # Display results
    #display_repositories(matching_repos, search_params['username'])

    # load html file as string
    html_raw = ""
    with open('githubber.html', 'r') as file:
        html_raw = file.read()

    print(html_raw)
    # print matching repos
    print(matching_repos)


    # LLM Setup for Demo
    # demo setup
    from openai import AzureOpenAI
    # Initialize the Azure OpenAI client
    client = AzureOpenAI(
        api_key="",  
        api_version="2024-10-21",
        azure_endpoint="https://.openai.azure.com"
    )
    response = client.chat.completions.create(
        model="gpt-4o",  # e.g., "gpt-4" or "gpt-35-turbo"
        messages=[
            {"role": "system", "content": "You are a helpful Javascript Expert that always responds with a javascript array."},
            {"role": "user", "content": """
[response_template]
const giftsData = [
            {
                repoNumber: 1,
                name: <repo_name>,
                description: <repo_description=reason you think this repo is awesome>, //USE EMOJIS, MAX WORD COUNT 50, BE CREATIVE AND FESTIVE! ITS CHRISTMAS!
                imageUrl: <https://github.com/___USERNAME__.png>,
                repoUrl: <https://github.com/___USERNAME__/___REPO_NAME___>
            },
        ];
             
// IMPORTANT! RESPONSE MUST BE VALID JSON!
return {'giftsData': giftsData};
[/response_template]
""".replace('___USERNAME___', search_params['username'])},
            {"role":"user", "content": f"""

[context]
{json.dumps(matching_repos)}
[/context]

Use the [context] to complete the [html_template]. FOCUS ON const giftsData = []; MAX 6.
Pick your favorite repos, and tell me why you think they are awesome in the `description`.
Make your `description` creative and unique, and make it perfect for the holiday season. It's Christmas! 
"""},
            {"role": "user", "content": "Respond with JSON object that returns the giftsData array under the key 'giftsData'."},
        ],
        response_format={"type": "json_object"}
    )
    print("ho, ho, ho! Merry Christmas!")
    print(response.choices[0].message.content.strip())

    # now lets replace the magic string ___GIFTS_DATA___ with the response.
    response_object = json.loads(response.choices[0].message.content.strip())
    html = html_raw.replace('___GIFTS_DATA___', str(json.dumps(response_object['giftsData'])))

    # write the html to a file
    write_to_file(html)

if __name__ == "__main__":
    main()

"""
Github Ratelimit
https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting

Smaller response size == faster inference?
Asking for FULL HTML vs just a JSON object
"""
