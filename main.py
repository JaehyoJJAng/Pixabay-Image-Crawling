import time
import  os
from config import headers
from bs4 import BeautifulSoup as bs
import  requests as rq
import urllib.parse as rep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Dict,List,Union

class ChromeDriver:
    @staticmethod
    def set_driver():
        # options 객체
        chrome_options = Options()

        # headless Chrome 선언
        chrome_options.add_argument('--headless')

        # 브라우저 꺼짐 방지
        chrome_options.add_experimental_option('detach', True)

        chrome_options.add_argument(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.104 Whale/3.13.131.36 Safari/537.36")

        # 불필요한 에러메시지 없애기
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        service = Service(executable_path=ChromeDriverManager().install())
        browser = webdriver.Chrome(service=service, options=chrome_options)
        browser.maximize_window()

        return browser

class Pixabay:
    def __init__(self)-> None:
        self.__headers : Dict[str,str] = headers.get_headers(key='headers')

        self.query : str = '우주'

        self.URLS : List[str] = [f'https://pixabay.com/ko/photos/search/{rep.quote_plus(self.query)}/?manual_search={1}&pagi={page}' for page in range(1,5 + 1)]

        self.browser = ChromeDriver().set_driver()

        self.count : int = 1

    def main(self)-> None:
        [self.fetch(url=url) for url in self.URLS]

    def fetch(self,url:str)-> None:
        self.browser.get(url)
        self.browser.implicitly_wait(20)

        # 브라우저 로딩 대기
        WebDriverWait(self.browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.row-masonry.search-results div.row-masonry-cell')))

        # 스크롤 내리기
        self.scroll_down()

        soup = bs(self.browser.page_source,'html.parser')

        images_length : int = len(soup.select('div.row-masonry.search-results div.row-masonry-cell'))

        for idx in range(images_length):
            images : list = soup.select('div.row-masonry.search-results div.row-masonry-cell')

            image = images[idx].select_one('div.item img.photo-result-image')
            if image != None:
                img_url = image.attrs['src']
                self.image_download(img_url=img_url)
            else:
                pass

        # 서버 과부하 방지용 대기시간 할당
        time.sleep(1.5)

    def image_download(self,img_url: str)-> None:
        """ 이미지 다운로드 메서드 """

        # 이미지 파일 저장 위치 지정
        img_save_path : str = os.path.abspath(f"{self.query}")
        if not os.path.exists(img_save_path):
            os.mkdir(img_save_path)

        # 이미지 파일명 지정
        img_filename : str = os.path.join(img_save_path, f'localImage-{self.count}.jpg')

        try :
            # 이미지 다운로드
            download_file = rq.get(img_url, headers=self.__headers,verify=False)
            with open(img_filename, 'wb') as photo:
                photo.write(download_file.content)
                print(f"{img_filename}\n")
                self.count += 1
        except:
            print('이미지 다운로드 실패\n')
            pass

    def scroll_down(self)-> None:
        scroll_count : int = 0
        while True:
            if scroll_count == 8:
                break

            self.browser.find_element(By.CSS_SELECTOR,'body').send_keys(Keys.PAGE_DOWN)
            time.sleep(0.5)
            scroll_count += 1

if __name__ == '__main__':
    app = Pixabay()
    app.main()