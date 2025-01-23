import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_and_parse(url):
    """Fetch and parse the webpage using BeautifulSoup."""
    response = requests.get(url)
    return BeautifulSoup(response.content, 'html.parser')

def extract_tables(soup):
    """Extract all tables with the class 'tableBox' from the parsed HTML."""
    return soup.find_all('div', {'class': 'tableBox'})

def parse_table1(table):
    """Parse table1 and return a cleaned DataFrame."""
    soup = BeautifulSoup(str(table), 'html.parser')
    table_element = soup.find('table')
    headers = [header.text for header in table_element.find_all('th')]
    rows = []
    for row in table_element.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) > 0:
            rows.append([cell.text.strip() for cell in cells])
    df = pd.DataFrame(rows, columns=["Life Insurer", "Total claims", "Claims paid", "Claims paid", "Claims repudiated", "Claims repudiated"])
    return df.drop([0, 1]).reset_index(drop=True)

def parse_table2(table):
    """Parse table2 and return a cleaned DataFrame."""
    soup = BeautifulSoup(str(table), 'html.parser')
    table_element = soup.find('table')
    header_row = table_element.find_all('tr')[1]
    headers = [header.text.strip() for header in header_row.find_all('td')]
    rows = []
    for row in table_element.find_all('tr')[2:]:
        cells = row.find_all('td')
        if len(cells) > 0:
            rows.append([cell.text.strip() for cell in cells])
    return pd.DataFrame(rows, columns=headers)

def main():
    """Main function to execute the workflow."""
    url = "https://economictimes.indiatimes.com/wealth/insure/life-insurance/latest-life-insurance-claim-settlement-ratio-of-insurance-companies-in-india/articleshow/97366610.cms"
    soup = fetch_and_parse(url)
    tables = extract_tables(soup)
    
    table1_df = parse_table1(tables[0])
    print("\n Individual death claims settlement by % of policies")
    print(table1_df)
    
    table2_df = parse_table2(tables[1])
    print("\n Individual death claims settlement by % of benefit amount")
    print(table2_df)

if __name__ == "__main__":
    main()