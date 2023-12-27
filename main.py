from bs4 import BeautifulSoup
import re
import requests
from datetime import datetime, timedelta
import csv

# Mapping of Persian numerals to English numerals
persian_to_english = {
    '۰': '0',
    '۱': '1',
    '۲': '2',
    '۳': '3',
    '۴': '4',
    '۵': '5',
    '۶': '6',
    '۷': '7',
    '۸': '8',
    '۹': '9'
}

def persian_numbers_to_range(text):
    # Convert Persian numerals to English numerals
    for persian_num, english_num in persian_to_english.items():
        text = text.replace(persian_num, english_num)

    # Find all numbers in the string
    numbers = re.findall(r'\d+', text)

    # Check if we found any numbers and return the appropriate format
    if len(numbers) == 1:
        return f"{numbers[0]}-"
    elif len(numbers) > 1:
        return f"{numbers[0]}-{numbers[1]}"
    else:
        return None
    

def calculate_hours(work_str):
    # Helper function to convert string time to a timedelta
    try:
        def time_to_timedelta(time_str):
            hours, minutes = map(int, time_str.split(':'))
            return timedelta(hours=hours, minutes=minutes)
        
        # Map Persian days to numbers , considering Saturday as day 0
        days_map = {
        'شنبه': 0,
        'یک‌شنبه': 1,
        'یک‌ شنبه': 1,
        'دوشنبه': 2,
        'دو شنبه': 2,
        'سه‌شنبه': 3,
        'سه‌ شنبه': 3,
        'چهارشنبه': 4,
        'چهار شنبه': 4,
        'پنج‌شنبه': 5,  # Adjusted the formatting here
        'پنجشنبه':5,
        'پنج شنبه':5,
        }

        # Regex pattern to split the string into parts for range days and individual days
        
        # parts = re.split(r' - ', work_str)
        parts = re.split(r' - و ', work_str)
        total_time = timedelta()

        for part in parts:
            # Adjust the regex pattern to correctly match the persian days and times
            pattern = r'(\S+?)(?: تا (\S+?))? (\d+):?(\d{0,2}) تا (\d+):?(\d{0,2})'
            matches = re.findall(pattern, part)
            
            for match in matches:
                start_day, end_day, start_hour, start_minute, end_hour, end_minute = match
                start_minute = start_minute or '00'
                end_minute = end_minute or '00'
                
                # Calculate timedelta for given hours
                start_time_delta = time_to_timedelta(f"{start_hour}:{start_minute}")
                end_time_delta = time_to_timedelta(f"{end_hour}:{end_minute}")
                daily_work_time = end_time_delta - start_time_delta

                # Adjust the total time based on whether the string specifies a range of days or just one day
                if end_day:  # It's a range of days
                    work_days = days_map[end_day] - days_map[start_day] + 1
                    total_time += work_days * daily_work_time
                else:  # It's a single day
                    total_time += daily_work_time

        # Return the total hours in HH:MM:SS format
        total_seconds = int(total_time.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{hours}:{str(minutes).zfill(2)}:00"

    except Exception as e:
        print(f"An error occurred: {e}. Returning original input.")
        return work_str



##web scraping e-estekhdam
# url='https://www.e-estekhdam.com/search/%D8%A7%D8%B3%D8%AA%D8%AE%D8%AF%D8%A7%D9%85-%D8%A8%D8%B1%D9%86%D8%A7%D9%85%D9%87-%D9%86%D9%88%DB%8C%D8%B3--%D9%85%D9%87%D9%86%D8%AF%D8%B3-%DA%A9%D8%A7%D9%85%D9%BE%DB%8C%D9%88%D8%AA%D8%B1--%D8%B7%D8%B1%D8%A7%D8%AD-%D9%88%D8%A8-%D8%B3%D8%A7%DB%8C%D8%AA-%D8%AF%D8%B1-%D8%AE%D8%B1%D8%A7%D8%B3%D8%A7%D9%86-%D8%B1%D8%B6%D9%88%DB%8C?sort=%D8%AC%D8%AF%DB%8C%D8%AF%D8%AA%D8%B1%DB%8C%D9%86'

url='https://www.e-estekhdam.com/search/%D8%A7%D8%B3%D8%AA%D8%AE%D8%AF%D8%A7%D9%85-%D8%A8%D8%B1%D9%86%D8%A7%D9%85%D9%87-%D9%86%D9%88%DB%8C%D8%B3--%D9%85%D9%87%D9%86%D8%AF%D8%B3-%DA%A9%D8%A7%D9%85%D9%BE%DB%8C%D9%88%D8%AA%D8%B1--%D8%B7%D8%B1%D8%A7%D8%AD-%D9%88%D8%A8-%D8%B3%D8%A7%DB%8C%D8%AA-%D8%AF%D8%B1-%D8%AE%D8%B1%D8%A7%D8%B3%D8%A7%D9%86-%D8%B1%D8%B6%D9%88%DB%8C?sort=%D8%A8%D8%A7%D9%84%D8%A7%D8%AA%D8%B1%DB%8C%D9%86-%D8%AD%D9%82%D9%88%D9%82'
response=requests.get(url,verify=False)
estekhdam_text=response.text

soup = BeautifulSoup(estekhdam_text,'lxml')


all_jobs=soup.find('div',class_='search-list')

lists=all_jobs.find_all('div',class_='job-list-item')
# print(lists)

with open('scraped_data.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)

    # Write the header row
    writer.writerow(['Title', 'Company', 'Skills', 'Location', 'Salary', 'Total_Hours','Link'])

    for job in lists:
        # print(job)
        title = job.find('div',class_='title').text
        company= job.find('div',class_='company').div.text
        skills= job.find('div',class_='chip technologies ml-10 mt-5')
        link=job.find('a',class_='item-content media display-block')
        # mylink=link['href']
        mylink=link.get('href')

        base_url = 'https://www.e-estekhdam.com'

        if not base_url.endswith('/') and not mylink.startswith('/'):
            full_url = base_url + '/' + mylink
        else:
            full_url = base_url + mylink

        location = job.find('div',class_='provinces').span.text

        new_response=requests.get(full_url,verify=False)

        job_detail_text=new_response.text

        new_soup = BeautifulSoup(job_detail_text,'lxml')

        job_content=new_soup.find('div',class_='hentry')

        time_tag = job_content.find('time')

        datetime_str = time_tag['datetime']

        job_date = datetime_str.split('T')[0]    


        # Find all divs with the specific class
        divs_with_class = job_content.find_all('div', class_='font-weight-bold font-size-13 mb-5')

        # Placeholder for the next sibling
        next_sibling_content = None

        for div in divs_with_class:
            if div.get_text(strip=True) == "حقوق ثابت ماهانه":
                # Get the next sibling of this div
                next_sibling = div.find_next_sibling()
                if next_sibling:
                    salary = next_sibling.get_text(strip=True)
                break


        h5_classes=job_content.find_all('h3',class_='h5 font-weight-bold mt-30')

        nest_sib_work= None

        for div in h5_classes:
            if div.get_text(strip=True) == "ساعات کاری":
                work_time = div.find_next_sibling()
                if work_time:
                    work_time2=work_time.get_text(strip=True)
                break
                
        writer.writerow([title, company, skills.span.text if skills else '', location, persian_numbers_to_range(salary), calculate_hours(work_time2), full_url])
