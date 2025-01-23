import requests
from bs4 import BeautifulSoup
import pandas as pd
import subprocess

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

def save_to_csv(df, filename):
    """Save the DataFrame to a CSV file."""
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

def encrypt_file(filename, password):
    """Encrypt the file using openssl."""
    encrypted_filename = f"{filename}.enc"
    command = f"openssl enc -aes-256-cbc -salt -in {filename} -out {encrypted_filename} -k {password}"
    subprocess.run(command, shell=True, check=True)
    print(f"File encrypted and saved as {encrypted_filename}")

def decrypt_file(encrypted_filename, password):
    """Decrypt the file using openssl."""
    decrypted_filename = encrypted_filename.replace(".enc", "_decrypted.csv")
    command = f"openssl enc -d -aes-256-cbc -in {encrypted_filename} -out {decrypted_filename} -k {password}"
    subprocess.run(command, shell=True, check=True)
    print(f"File decrypted and saved as {decrypted_filename}")

def main():
    """Main function to execute the workflow."""
    url = "https://economictimes.indiatimes.com/wealth/insure/life-insurance/latest-life-insurance-claim-settlement-ratio-of-insurance-companies-in-india/articleshow/97366610.cms"
    soup = fetch_and_parse(url)
    tables = extract_tables(soup)
    
    # Parse and save table1
    table1_df = parse_table1(tables[0])
    print("\nIndividual death claims settlement by % of policies")
    print(table1_df)
    save_to_csv(table1_df, "settlement_by_%_of_policies")
    
    # Parse and save table2
    table2_df = parse_table2(tables[1])
    print("\nIndividual death claims settlement by % of benefit amount")
    print(table2_df)
    save_to_csv(table2_df, "settlement_%_benefit_amount")
    
    # Encrypt the CSV files
    password = "arnav1234"  # Replace with a secure password
    encrypt_file("settlement_by_%_of_policies", password)
    encrypt_file("settlement_%_benefit_amount", password)

if __name__ == "__main__":
    main()