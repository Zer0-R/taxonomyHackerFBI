import requests
import json
from bs4 import BeautifulSoup

# Url renvoyant la liste des criminels pour une annee definie
REQUEST_ITEMS = "https://www.fbi.gov/wanted/cyber/@@castle.cms.querylisting/querylisting-1?selected-year="

# entete http utliser a chaque requete
HEADERS = {
	'Host': 'www.fbi.gov',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
	'Accept': '*/*',
	'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
	'Accept-Encoding': 'gzip, deflate',
	'X-Requested-With': 'XMLHttpRequest',
	'DNT': '1',
	'Connection': 'close',
	'Referer': 'https://www.fbi.gov/wanted/cyber',
}

# annee minimum a partir de laquelle les criminiels on commence a etre recherche
YEAR_BEGIN = 2010
# annee maximum a partir de laquelle les criminiels on commence a etre recherche
YEAR_END = 2025

"""
Quitte le programme anormalement
"""
def error(message):
	print("[!] " + message)
	exit(1)

"""
Recupere la liste des url des cyber-criminels
"""
def get_items():

	items = []

	for year in range(YEAR_BEGIN, YEAR_END + 1):

		page = requests.get(REQUEST_ITEMS + str(year), headers=HEADERS)
		soup = BeautifulSoup(page.content, 'html.parser')

		for a in soup.find_all('a', href=True): 
		    if a.text:
		    	items.append(a['href'])

	return list(dict.fromkeys(items))

"""
Recupere les informations d'un criminel a partir
de l'url de sa page profil
"""
def get_item(url):

	item = {}
	item['picture'] = url + '/@@images/image'

	page = requests.get(url, headers=HEADERS)
	soup = BeautifulSoup(page.content, 'html.parser')

	name = soup.find(class_="sr-only")
	if name:
		item['name'] = name.get_text()

	alias = soup.find(class_="wanted-person-aliases")
	if alias:
		for p in alias.find_all('p'):
			if p.text:
		   		item['alias'] = p.text

	data = []
	table = soup.find('table', attrs={'class':'table table-striped wanted-person-description'})
	if table:
		table_body = table.find('tbody')
		rows = table_body.find_all('tr')
		for row in rows:

		    cols = row.find_all('td')
		    cols = [ele.text.strip() for ele in cols]

		    if len(cols) != 2:
		    	error("len invalid")

		    item[cols[0].replace(' ', '-').lower()] = cols[1]

	return item

def main():

	urls = get_items()
	len_urls = len(urls)
	print("[*] " + str(len_urls) + " URL founds\n")

	items = []
	cpt = 0
	for url in urls:

		cpt += 1
		print("[+] Scrap " + str(cpt) + "/" + str(len_urls) + ": " + url)
		items.append(get_item(url))

	items = json.dumps(items, indent=4)
	print("\n[*] Data in json format:")
	print(items)

if __name__ == "__main__":
	main()