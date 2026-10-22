from bs4 import BeautifulSoup

from lession30.excample import html_content

#Html content

html_content = """
<html>
    <head>
        <title> hello hello</title>
    </head>
    
    <body>
        <h1> Welcome to Beautiful soup</h1>
        <p>Beautiful Soup makes web scraping easy!</p>
        <div id="content">
            <p>here are some links:</p>
            <a>Link 1</a>
            <a>Link 2</a>
            <a>Link 3</a>
        </div>
    </body>
</html>
"""
soup = BeautifulSoup(html_content, "html.parser:")
print("Title of the page:",soup.title.text)
intro_text = soup.find('p', class_='intro').text
print(intro_text)

div_content = soup.find('div',id="content")
links = div_content.find_all('a')

print(links)












