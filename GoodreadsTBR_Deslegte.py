import time
import requests
import urllib.parse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_goodreads_to_read_list(url):
    # Set up Selenium WebDriver (using Chrome in this example)
    print("\nOpening Goodreads list. Please wait...")
    driver = webdriver.Chrome()

    try:
        # Open the Goodreads page
        driver.get(url)
        
        # Initialize an empty list to store all book titles
        all_books = []
        
        while True:
            # Wait for the page to load completely
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'td.field.title div.value a'))
                )
            except Exception as e:
                print(f"Error waiting for page to load: {e}")
                break
            
            # Get the page source after the content has been loaded
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Extract books from the current page
            books = [book.get_text(strip=True) for book in soup.select('td.field.title div.value a')]
            all_books.extend(books)
            
            # Scroll to the bottom of the page to ensure the "Next" button is in view
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)  # Wait for the page to adjust
            
            # Try to find the "Next" button
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'a.next_page'))
                )
                
                if "disabled" in next_button.get_attribute("class"):
                    print("Reached the last page of your Goodreads list.")
                    break  # Exit the loop if "Next" button is disabled
                
                # Click on the "Next" button to go to the next page
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(3)  # Wait for the next page to load
            except Exception as e:
                print(f"Error finding or clicking the 'Next' button: {e}")
                break  # Exit the loop if the "Next" button is not found or clickable

    finally:
        # Close the driver
        driver.quit()
        
    return all_books

def search_deslegte_book(book_title):
    # Encode book title for URL
    search_url = "https://www.deslegte.com/boeken/?q=" + urllib.parse.quote_plus(book_title)
    
    # Fetch the search results page
    response = requests.get(search_url)
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve search results for '{book_title}'. Skipping this book.")
        return False

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract the number of results from the meta description
    meta_description = soup.find('meta', {'name': 'description'})
    if meta_description:
        description_content = meta_description.get('content', '')        
        if 'uitgaven gevonden' in description_content:
            # Extract the number of editions found
            try:
                number_of_editions = int(description_content.split(' ')[0])
            except ValueError:
                number_of_editions = 0
            
            if number_of_editions > 0:
                return True
            else:
                return False
    return False

def check_books_in_deslegte(to_read_list):
    available_books = []
    for book in to_read_list:
        print(f"Checking availability for book: '{book}'...")
        if search_deslegte_book(book):
            print(f"'{book}' is available at Deslegte!")
            available_books.append(book)
        else:
            print(f"'{book}' is not available at Deslegte.")
    
    return available_books

def main():
    print("Welcome to the Goodreads to Deslegte Book Availability Checker!")
    goodreads_url = input("Please enter your Goodreads To-Be-Read list URL: ").strip()

    if not goodreads_url:
        print("Error: No URL entered. Please try again.")
        return

    try:
        to_read_list = get_goodreads_to_read_list(goodreads_url)
        
        if not to_read_list:
            print("No books found in your Goodreads list or failed to retrieve them.")
            return
        
        print(f"\nFound {len(to_read_list)} books in your Goodreads list.")
        available_books = check_books_in_deslegte(to_read_list)

        if available_books:
            print("\nThe following books are available at Deslegte:")
            for idx, book in enumerate(available_books, 1):
                print(f"{idx}. {book}")
        else:
            print("\nNo books from your list are currently available at Deslegte.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()