# Author: Nina Yang

from bs4 import BeautifulSoup
import requests
import re
import os
import csv
import unittest


def get_titles_from_search_results(filename):

    source_dir = os.path.dirname(__file__)
    full_path = os.path.join(source_dir, filename)
    infile = open(full_path, 'r', encoding='utf-8')
    soup = BeautifulSoup(infile, 'html.parser')
    infile.close()

    titles = []
    rows = soup.find_all("tr", itemtype="http://schema.org/Book")

    for row in rows:

        book = row.find("a", class_="bookTitle")
        bookTitle = book.find("span", itemprop="name")

        author = row.find("a", class_="authorName")
        authorName = author.find("span", itemprop="name")

        titles.append((bookTitle.text.strip(), authorName.text.strip()))
        
    return titles


def get_search_links():
    
    url = "https://www.goodreads.com/search?q=fantasy&qid=NwUsLiA2Nc"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    links = []
    rows = soup.find_all("a", class_="bookTitle")
    
    for row in rows:
        link = row.get('href', None)
        links.append("https://www.goodreads.com"+link)

    return links[0:10]


def get_book_summary(book_url):

    url = book_url
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    bookTitle = soup.find("h1", id="bookTitle")
    author = soup.find("a", class_="authorName")
    authorName = author.find("span", itemprop="name")
    pageNum = soup.find("span", itemprop="numberOfPages")
    return (bookTitle.text.strip(), authorName.text.strip(), int(pageNum.text.strip().split(" ")[0]))


def summarize_best_books(filepath):

    infile = open(filepath, 'r', encoding='utf-8')
    soup = BeautifulSoup(infile, 'html.parser')
    infile.close()

    books = soup.find_all(class_="category clearFix")
    categories = []

    for book in books:

        category = book.find(class_="category__copy").text.strip()
        bookTitle = book.find("img", class_="category__winnerImage").get('alt', None)
        link = book.find("a").get('href', None)

        categories.append((category, bookTitle, link))
        
    return categories


def write_csv(data, filename):
    
    with open(filename, mode='w') as csvfile:

        dataWriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        dataWriter.writerow(["Book title", "Author Name"])
        
        for line in data:
            dataWriter.writerow([line[0], line[1]])

    csvfile.close()


def extra_credit(filepath):

    infile = open(filepath, 'r', encoding='utf-8')
    soup = BeautifulSoup(infile, 'html.parser')
    infile.close()

    regex = r"([A-Z][a-z][a-z]+\s+[A-Z][a-z]+)"

    description = soup.find('div', id="description")
    parts = description.find_all('span')
    text = ""

    for part in parts:
        text += part.text

    entities = re.findall(regex, text)
    return entities


class TestCases(unittest.TestCase):

    # call get_search_links() and save it to a static variable: search_urls
    search_urls = get_search_links()


    def test_get_titles_from_search_results(self):

        # call get_titles_from_search_results() on search_results.htm and save to a local variable
        results = get_titles_from_search_results("search_results.htm")

        # check that the number of titles extracted is correct (20 titles)
        self.assertEqual(len(results), 20)

        # check that the variable you saved after calling the function is a list
        self.assertEqual(type(results), list)

        # check that each item in the list is a tuple
        for item in results:
            self.assertEqual(type(item), tuple)

        # check that the first book and author tuple is correct (open search_results.htm and find it)
        self.assertEqual(results[0][0], "Harry Potter and the Deathly Hallows (Harry Potter, #7)")
        self.assertEqual(results[0][1], "J.K. Rowling")

        # check that the last title is correct (open search_results.htm and find it)
        self.assertEqual(results[len(results)-1][0], "Harry Potter: The Prequel (Harry Potter, #0.5)")
        self.assertEqual(results[len(results)-1][1], "J.K. Rowling")

    def test_get_search_links(self):

        # check that TestCases.search_urls is a list
        self.assertEqual(type(TestCases.search_urls), list)

        # check that the length of TestCases.search_urls is correct (10 URLs)
        self.assertEqual(len(TestCases.search_urls), 10)

        # check that each URL in the TestCases.search_urls is a string
        # check that each URL contains the correct url for Goodreads.com followed by /book/show/
        for item in TestCases.search_urls:
            self.assertEqual(type(item), str)
            self.assertTrue("goodreads.com/book/show/" in item)


    def test_get_book_summary(self):

        # create a local variable – summaries – a list containing the results from get_book_summary()
        # for each URL in TestCases.search_urls (should be a list of tuples)
        summaries = []
        for x in TestCases.search_urls:
            summaries.append(get_book_summary(x))

        # check that the number of book summaries is correct (10)
        self.assertEqual(len(summaries), 10)
        for item in summaries:

            # check that each item in the list is a tuple
            self.assertEqual(type(item), tuple)

            # check that each tuple has 3 elements
            self.assertEqual(len(item), 3)

            # check that the first two elements in the tuple are string
            self.assertEqual(type(item[0]), str)
            self.assertEqual(type(item[1]), str)

            # check that the third element in the tuple, i.e. pages is an int
            self.assertEqual(type(item[2]), int)

        # check that the first book in the search has 337 pages
        self.assertEqual(summaries[0][2], 337)


    def test_summarize_best_books(self):

        # call summarize_best_books and save it to a variable
        source_dir = os.path.dirname(__file__)
        full_path = os.path.join(source_dir, "best_books_2020.htm")
        bestBooks = summarize_best_books(full_path)

        # check that we have the right number of best books (20)
        self.assertEqual(len(bestBooks), 20)
        for book in bestBooks:

            # assert each item in the list of best books is a tuple
            self.assertEqual(type(book), tuple)

            # check that each tuple has a length of 3
            self.assertEqual(len(book), 3)

        # check that the first tuple is made up of the following 3 strings:'Fiction', "The Midnight Library", 'https://www.goodreads.com/choiceawards/best-fiction-books-2020'
        self.assertEqual(bestBooks[0], ('Fiction', "The Midnight Library", 'https://www.goodreads.com/choiceawards/best-fiction-books-2020'))

        # check that the last tuple is made up of the following 3 strings: 'Picture Books', 'Antiracist Baby', 'https://www.goodreads.com/choiceawards/best-picture-books-2020'
        self.assertEqual(bestBooks[len(bestBooks)-1], ('Picture Books', 'Antiracist Baby', 'https://www.goodreads.com/choiceawards/best-picture-books-2020'))

    def test_write_csv(self):

        # call get_titles_from_search_results on search_results.htm and save the result to a variable
        titles = get_titles_from_search_results("search_results.htm")

        # call write csv on the variable you saved and 'test.csv'
        write_csv(titles, "test.csv")

        # read in the csv that you wrote (create a variable csv_lines - a list containing all the lines in the csv you just wrote to above)
        f = open('test.csv')
        csv_reader = csv.reader(f, delimiter=',')
        csv_lines = [r for r in csv_reader]

        # check that there are 21 lines in the csv
        self.assertEqual(len(csv_lines), 21)

        # check that the header row is correct
        self.assertEqual(csv_lines[0], ["Book title","Author Name"])

        # check that the next row is 'Harry Potter and the Deathly Hallows (Harry Potter, #7)', 'J.K. Rowling'
        self.assertEqual(csv_lines[1], ['Harry Potter and the Deathly Hallows (Harry Potter, #7)', 'J.K. Rowling'])

        # check that the last row is 'Harry Potter: The Prequel (Harry Potter, #0.5)', 'J.K. Rowling'
        self.assertEqual(csv_lines[len(csv_lines)-1], ['Harry Potter: The Prequel (Harry Potter, #0.5)', 'J.K. Rowling'])

        f.close()



if __name__ == '__main__':
    print(extra_credit("extra_credit.htm"))
    unittest.main(verbosity=2)






