import argparse
import requests
from bs4 import BeautifulSoup
from tabulate import tabulate

## Change This URL To Your League
url = "https://hockey.fantasysports.yahoo.com/hockey/33026"

def fetch_matchups(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    content = response.text
    soup = BeautifulSoup(content, 'html.parser')

    matchups_section = soup.find('ul', class_='List')
    matchup_dict = {}
    if matchups_section:
        matchups = matchups_section.find_all('li')
        for index, matchup in enumerate(matchups, start=1):
            teams = matchup.find_all('div', class_='Fz-sm Phone-fz-xs Ell Mawpx-200 Phone-Mawpx-70')
            if len(teams) == 2:
                team1 = teams[0].get_text(strip=True)
                team2 = teams[1].get_text(strip=True)
                link = matchup.find('a', href=True)['href']
                matchup_dict[index] = {
                    'text': f"{team1} vs {team2}",
                    'url': f"https://hockey.fantasysports.yahoo.com{link}"
                }

    return matchup_dict

def fetch_matchup(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    content = response.text
    soup = BeautifulSoup(content, 'html.parser')

    matchup_header = soup.find(id="matchup-header")
    matchup_wall_header = soup.find(id="matchup-wall-header")

    team1_info = soup.find('div', class_='Ta-start Grid-u-1-3')
    team2_info = soup.find('div', class_='Ta-end Grid-u-1-3')

    team1_text = team1_info.get_text(strip=True) if team1_info else 'N/A'
    team2_text = team2_info.get_text(strip=True) if team2_info else 'N/A'

    format_table(matchup_wall_header, "matchup-wall-header", team1_text, team2_text)

def format_table(section, title, team1_text, team2_text):
    if section:
        table = section.find('table')
        if table:
            rows = table.find_all('tr')
            table_data = []
            ccount = 0
            for row in rows:
                columns = row.find_all(['td', 'th'])
                row_data = []
                for col in columns:
                    ccount = ccount + 1
                    text = col.get_text(strip=True)
                    # Check if the cell has the specified class and add background lime green and font black
                    if set(['Fw-b', 'Bg-shade2', 'Bg-selected', 'Ta-c']).issubset(set(col.get('class', []))):
                        text = f"\033[30;102m  {text}  \033[0m"  # Black font on lime green background
                    row_data.append(text)
                table_data.append(row_data)
            table_data[0].append('')
            table_data[1].append("{} Games Left".format(team1_text.replace('Remaining', '')))
            table_data[2].append("{} Games Left".format(team2_text.replace('Remaining', '')))
            print(tabulate(table_data, tablefmt="fancy_grid"))

if __name__ == "__main__":
    print("""
 __   __  _______  __   __  _______  _______    _______  _______  __    _  _______  _______  _______  __   __ 
|  | |  ||   _   ||  | |  ||       ||       |  |       ||   _   ||  |  | ||       ||   _   ||       ||  | |  |
|  |_|  ||  |_|  ||  |_|  ||   _   ||   _   |  |    ___||  |_|  ||   |_| ||_     _||  |_|  ||  _____||  |_|  |
|       ||       ||       ||  | |  ||  | |  |  |   |___ |       ||       |  |   |  |       || |_____ |       |
|_     _||       ||       ||  |_|  ||  |_|  |  |    ___||       ||  _    |  |   |  |       ||_____  ||_     _|
  |   |  |   _   ||   _   ||       ||       |  |   |    |   _   || | |   |  |   |  |   _   | _____| |  |   |  
  |___|  |__| |__||__| |__||_______||_______|  |___|    |__| |__||_|  |__|  |___|  |__| |__||_______|  |___|  
          """)
    parser = argparse.ArgumentParser(description="Fetch Yahoo Fantasy Hockey Matchups")
    parser.add_argument('--matchup', type=int, help="Matchup number to fetch details for")
    args = parser.parse_args()
    matchups = fetch_matchups(url)

    if matchups:
        print("This week's matchups!\n")
        for index, matchup in matchups.items():
            print(f"[{index}] {matchup['text']}")

        if args.matchup:
            choice = args.matchup
        else:
            try:
                choice = int(input("\nPress # to fetch results: "))
            except ValueError:
                print("Invalid input. Please enter a number.")
                exit()

        if choice in matchups:
            fetch_matchup(matchups[choice]['url'])
        else:
            print("Invalid choice. Please enter a valid number.")
