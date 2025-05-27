import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
from collections import defaultdict

driver = uc.Chrome()
wait = WebDriverWait(driver, 10)
driver.maximize_window()

driver.get("https://in.bookmyshow.com/explore/home/ahmedabad")

movies_link = WebDriverWait(driver, 15).until(
    EC.element_to_be_clickable((By.XPATH, "//a[text()='Movies']"))
)
movies_link.click()

WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.XPATH, "//div[@class='sc-7o7nez-0 elfplV']"))
)

elements = driver.find_elements(By.XPATH, '//*[@id="super-container"]/div/div[3]/div[2]/div/div/div/div[2]/a/div/div[3]/div[1]/div')
data_list = [el.text.strip() for el in elements if el.text.strip()]
print("Available Movies:")

for i, name in enumerate(data_list):
    print(f"{i+1}. {name}")

selected_name = input("\nEnter the exact movie name you want to click: ").strip()

found = False
for el, name in zip(elements, data_list):
    if name.lower() == selected_name.lower():
        el.click()
        print(f"Clicked on: {name}")
        found = True
        time.sleep(5)
        bookT = driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div[1]/section[1]/div/div/div[2]/div[2]/div/div/button/div")
        bookT.click()
        time.sleep(3)
        break

if not found:
    print("Movie not found.")
    driver.quit()
    exit()

DateList = driver.find_elements(By.XPATH, "//div[@class='sc-6bpksa-0 HCNei'] | //div[@class='sc-6bpksa-0 gJVIzf']")
dateshow_list_dict = {el.get_attribute("id"): el.text.strip().replace("\n", " ") for el in DateList if el.text.strip()}
dateshow_list = {num: el.text.strip().replace("\n", " ") for num, el in enumerate(DateList) if el.text.strip()}
print("Available Dates:")
for k, v in dateshow_list.items():
    print(f"{k}: {v}")

select_date = int(input("Select date from above list (input number): "))
value = dateshow_list.get(select_date)
if value:
    key = next((k for k, v in dateshow_list_dict.items() if v == value), None)
    driver.find_element(By.ID, key).click()
    time.sleep(5)
    print(f"Selected Date: {value} (ID: {key})")
else:
    print("Invalid date selection.")
    driver.quit()
    exit()

movie_data = {
    "movie_name": selected_name,
    "date": value,
    "theatres": []
}

theatre_count = len(driver.find_elements(By.CSS_SELECTOR, "div.sc-e8nk8f-3.hStBrg"))

for i in range(theatre_count):
    theatre_elements = driver.find_elements(By.CSS_SELECTOR, "div.sc-e8nk8f-3.hStBrg")
    th = theatre_elements[i]

    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", th)
    time.sleep(2)

    theatre_name = th.find_element(By.CSS_SELECTOR, "div.sc-7o7nez-0.hvoTNx").text

    print(f"\nTheatre: {theatre_name}")
    theatre_info = {
        "theatre_name": theatre_name,
        "shows": []
    }

    showtime_elements = th.find_elements(By.CSS_SELECTOR, "div.sc-1vhizuf-2.bHUoUD")

    for j, showtime in enumerate(showtime_elements):
        try:
            showtime_text = showtime.text.strip()
            print(f"Movie Showtime: {showtime_text}")

            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", showtime)
            driver.execute_script("arguments[0].click();", showtime)

            wait.until(EC.element_to_be_clickable((By.ID, "proceed-Qty"))).click()

            total_seats = wait.until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[@class='seatI']//a"))
            )
            print(f"Total Seats: {len(total_seats)}")

            table = driver.find_element(By.CSS_SELECTOR, "table.setmain")
            price_cells = table.find_elements(By.CSS_SELECTOR, "td.PriceB1")
            price_seat_availability = defaultdict(int)

            for price_cell in price_cells:
                price_category = price_cell.find_element(By.CSS_SELECTOR, "div.seatP").text.strip()
                price_tr = price_cell.find_element(By.XPATH, "./ancestor::tr")
                seats_tr = price_tr.find_element(By.XPATH, "following-sibling::tr[1]")
                available_seats = seats_tr.find_elements(By.CSS_SELECTOR, "a._available")
                price_seat_availability[price_category] += len(available_seats)

            for price, count in price_seat_availability.items():
                print(f"{price}: {count} seats available")

            show_info = {
                "show_time": showtime_text,
                "total_seats": len(total_seats),
                "available_by_price": dict(price_seat_availability)
            }
            theatre_info["shows"].append(show_info)

            driver.back()
            time.sleep(3)

        except Exception as e:
            print(f"Error processing showtime '{showtime_text}': {e}")
            driver.back()
            time.sleep(3)

    movie_data["theatres"].append(theatre_info)

output_filename = f"{selected_name.replace(' ', '_')}_{value.replace(' ', '_')}.json"
with open(output_filename, "w", encoding="utf-8") as f:
    json.dump(movie_data, f, indent=4, ensure_ascii=False)

print(f"\nData exported to {output_filename}")
driver.quit()
