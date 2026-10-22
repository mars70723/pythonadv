from bs4 import BeautifulSoup

html_content = ("<html><body><p>Hello, klasa 7:30B</p></body></html>")

soup = BeautifulSoup(html_content, 'html.parser')

paragrafi = soup.find('p').text

print(paragrafi)
