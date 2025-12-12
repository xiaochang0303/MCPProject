import os
import time
import json
import traceback
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from liulanqi import COOKING_PATH, get_driver, get_map4, get_publish_date


XIAOHONGSHU_COOKING = os.path.join(COOKING_PATH, "xiaohongshu.json")


def xiaohongshu_login(driver):
    if (os.path.exists(XIAOHONGSHU_COOKING)):
        print("cookies存在")
        with open(XIAOHONGSHU_COOKING) as f:
            cookies = json.loads(f.read())
            driver.get("https://creator.xiaohongshu.com/creator/post")
            driver.implicitly_wait(10)
            driver.delete_all_cookies()
            time.sleep(8)
            # 遍历cook
            print("加载cookie")
            for cookie in cookies:
                if 'expiry' in cookie:
                    del cookie["expiry"]
                # 添加cook
                driver.add_cookie(cookie)
            time.sleep(5)
            # 刷新
            print("开始刷新")
            driver.refresh()
            driver.get("https://creator.xiaohongshu.com/publish/publish")
            time.sleep(10)
    else:
        print("cookies不存在")
        driver.get('https://creator.xiaohongshu.com/creator/post')
        # driver.find_element(
        #     "xpath", '//*[@placeholder="请输入手机号"]').send_keys("")
        # # driver.find_element(
        # #     "xpath", '//*[@placeholder="请输入密码"]').send_keys("")
        # driver.find_element("xpath", '//button[text()="登录"]').click()
        print("等待登录")
        time.sleep(30)
        print("登录完毕")
        cookies = driver.get_cookies()
        with open(XIAOHONGSHU_COOKING, 'w') as f:
            f.write(json.dumps(cookies))
        print(cookies)
        time.sleep(1)


def publish_xiaohongshu(driver, mp4, index):
    time.sleep(3)
    driver.find_element("xpath", '//*[text()="发布笔记"]').click()
    print("开始上传文件", mp4[0])
    time.sleep(3)
    # ### 上传视频
    vidoe = driver.find_element("xpath", '//input[@type="file"]')
    vidoe.send_keys(mp4[0])

    # 填写标题
    content = mp4[1].replace('.mp4', '')
    driver.find_element(
        "xpath", '//*[@placeholder="填写标题，可能会有更多赞哦～"]').send_keys(content)

    time.sleep(1)
    # 填写描述
    content_clink = driver.find_element(
        "xpath", '//*[@placeholder="填写更全面的描述信息，让更多的人看到你吧！"]')
    content_clink.send_keys(content)

    time.sleep(3)
    # #虐文推荐 #知乎小说 #知乎文
    for label in ["#虐文","#知乎文","#小说推荐","#知乎小说","#爽文"]:
        content_clink.send_keys(label)
        time.sleep(1)
        data_indexs = driver.find_elements(
            "class name", "publish-topic-item")
        try:
            for data_index in data_indexs:
                if(label in data_index.text):
                    print("点击标签",label)
                    data_index.click()
                    break
        except Exception:
            traceback.print_exc()
        time.sleep(1)

    # 定时发布
    dingshi = driver.find_elements(
        "xpath", '//*[@class="css-1v54vzp"]')
    time.sleep(4)
    print("点击定时发布")
    dingshi[3].click()
    time.sleep(5)
    input_data = driver.find_element("xpath", '//*[@placeholder="请选择日期"]')
    input_data.send_keys(Keys.CONTROL,'a')     #全选
    # input_data.send_keys(Keys.DELETE)
    input_data.send_keys(get_publish_date(content,index))    
    time.sleep(3)
    # driver.find_element("xpath", '//*[text()="确定"]').click()

    # 等待视频上传完成
    while True:
        time.sleep(10)
        try:
            driver.find_element("xpath",'//*[@id="publish-container"]/div/div[2]/div[2]/div[6]/div/div/div[1]//*[contains(text(),"重新上传")]')
            break
        except Exception as e:
            traceback.print_exc()
            print("视频还在上传中···")
    
    print("视频已上传完成！")
    time.sleep(3)
    # 发布
    driver.find_element("xpath", '//*[text()="发布"]').click()
    print("视频发布完成！")
    time.sleep(10)


def publish_single_post(driver, file_path, title, content, topics=None, date_offset_hours=24):
    """
    Refactored function to publish a single post with explicit parameters.
    """
    if topics is None:
        topics = ["#旅游", "#攻略"]

    time.sleep(3)
    driver.find_element("xpath", '//*[text()="发布笔记"]').click()
    print("开始上传文件", file_path)
    time.sleep(3)
    
    # Upload
    # Determine if it's video or image based on extension? 
    # The original code assumes video input for 'mp4' variable but uses same input selector.
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    file_input = driver.find_element("xpath", '//input[@type="file"]')
    file_input.send_keys(file_path)
    
    # Wait for upload to process and UI to update
    print("Waiting for title input field to appear...")
    title_selectors = [
        '//*[@placeholder="填写标题，可能会有更多赞哦～"]',
        '//input[contains(@placeholder, "标题")]',
        '//div[contains(@class, "title")]//input'
    ]
    
    title_input = None
    for xpath in title_selectors:
        try:
            print(f"Trying selector: {xpath}")
            title_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            print("Found title input!")
            break
        except:
            continue
            
    if title_input:
        title_input.send_keys(title)
    else:
        raise Exception("Could not find title input with any known selector.")

    time.sleep(1)
    # Content
    time.sleep(1)
    # Content
    print("Waiting for content input...")
    content_selectors = [
        '//*[@placeholder="输入正文描述，真诚有价值的分享予人温暖"]',
        '//div[@class="post-content"]//div[@contenteditable="true"]',
        '//div[contains(@class, "content")]//textarea',
        '//div[contains(@placeholder, "描述")]'
    ]
    
    content_input = None
    for xpath in content_selectors:
        try:
            print(f"Trying content selector: {xpath}")
            content_input = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            print("Found content input!")
            break
        except:
             continue
    
    if content_input:
        content_input.send_keys(content)
    else:
        print("Warning: Could not find content input. Skipping description.")

    time.sleep(3)
    
    # Topics
    for label in topics:
        content_input.send_keys(label)
        time.sleep(1)
        data_indexs = driver.find_elements(
            "class name", "publish-topic-item")
        try:
            for data_index in data_indexs:
                if(label in data_index.text):
                    print("点击标签",label)
                    data_index.click()
                    break
        except Exception:
            traceback.print_exc()
        time.sleep(1)

    # Schedule publish (Optional, for now hardcoded to follow original logic somewhat or just publish immediately if needed)
    # Original logic forces scheduled publish.
    dingshi = driver.find_elements(
        "xpath", '//*[@class="css-1v54vzp"]')
    
    if len(dingshi) > 3:
        time.sleep(4)
        print("点击定时发布")
        dingshi[3].click()
        time.sleep(5)
        input_data = driver.find_element("xpath", '//*[@placeholder="请选择日期"]')
        input_data.send_keys(Keys.CONTROL,'a')
        
        # Calculate publish time
        from datetime import datetime, timedelta
        publish_time = (datetime.now() + timedelta(hours=date_offset_hours)).strftime("%Y-%m-%d %H:%M")
        
        input_data.send_keys(publish_time)    
        time.sleep(3)

    # Wait for upload
    while True:
        time.sleep(10)
        try:
            driver.find_element("xpath",'//*[@id="publish-container"]/div/div[2]/div[2]/div[6]/div/div/div[1]//*[contains(text(),"重新上传")]')
            break
        except Exception as e:
            # traceback.print_exc()
            print("视频/图片还在上传中···")
    
    print("上传完成！")
    time.sleep(3)
    # Publish
    driver.find_element("xpath", '//*[text()="发布"]').click()
    print("发布完成！")
    time.sleep(10)


def publish_image_post(driver, file_path, title, content, topics=None, date_offset_hours=24):
    """
    Publishes an image (or multiple images) as a 'Image/Text' note.
    """
    if topics is None:
        topics = ["#旅游", "#攻略"]

    time.sleep(3)
    driver.find_element("xpath", '//*[text()="发布笔记"]').click()
    print("开始上传图片")
    time.sleep(3)
    
    # Switch to Image Upload tab
    try:
        image_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[text()="上传图文"]'))
        )
        image_tab.click()
        time.sleep(1)
    except Exception as e:
        print("Could not click '上传图文', maybe already active or UI changed. trying JS click as fallback.")
        try:
             driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, '//*[text()="上传图文"]'))
        except Exception as e2:
             print("JS click failed too:", e2)

    # Upload
    file_input = driver.find_element("xpath", '//input[@type="file"]')
    file_input.send_keys(file_path)
    
    # Wait for upload to process and UI to update
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    print("Waiting for title input field to appear...")
    title_selectors = [
        '//*[@placeholder="填写标题，可能会有更多赞哦～"]',
        '//input[contains(@placeholder, "标题")]',
        '//div[contains(@class, "title")]//input'
    ]
    
    # Helper to strip non-BMP characters (emojis)
    def remove_non_bmp(text):
        return ''.join(c for c in text if c <= '\uFFFF')

    title = remove_non_bmp(title)
    content = remove_non_bmp(content)

    title_input = None
    for xpath in title_selectors:
        try:
            print(f"Trying selector: {xpath}")
            title_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            print("Found title input!")
            break
        except:
            continue
            
    if title_input:
        # Clear existing text just in case
        title_input.send_keys(Keys.CONTROL, "a")
        title_input.send_keys(Keys.DELETE)
        title_input.send_keys(title)
    else:
        raise Exception("Could not find title input with any known selector.")

    time.sleep(1)
    # Content
    time.sleep(1)
    # Content
    content_selectors = [
        '//*[@placeholder="输入正文描述，真诚有价值的分享予人温暖"]',
        '//*[@placeholder="填写更全面的描述信息，让更多的人看到你吧！"]',
        '//*[@id="post-textarea"]',
        '//div[@contenteditable="true"]',
        '//div[contains(@class, "post-content")]//div[@contenteditable="true"]',
        '//div[contains(@class, "content")]//textarea',
        '//div[contains(@placeholder, "描述")]'
    ]
    
    content_input = None
    for xpath in content_selectors:
        try:
            print(f"Trying content selector: {xpath}")
            content_input = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            print("Found content input!")
            break
        except:
             continue
    
    if content_input:
        content_input.send_keys(content)
    else:
        print("Warning: Could not find content input. Skipping description.")

    time.sleep(3)
    
    # Topics
    if content_input and topics:
        for label in topics:
            label = remove_non_bmp(label)
            content_input.send_keys(label)
            time.sleep(1)
            try:
                # Wait briefly for suggestions
                data_indexs = driver.find_elements("class name", "publish-topic-item")
                for data_index in data_indexs:
                    if(label in data_index.text):
                        print("点击标签",label)
                        data_index.click()
                        break
            except Exception:
                pass
            time.sleep(1)

    # Schedule publish
    dingshi = driver.find_elements(
        "xpath", '//*[@class="css-1v54vzp"]')
    
    if len(dingshi) > 3:
        time.sleep(4)
        print("点击定时发布")
        dingshi[3].click()
        time.sleep(5)
        input_data = driver.find_element("xpath", '//*[@placeholder="请选择日期"]')
        input_data.send_keys(Keys.CONTROL,'a')
        
        # Calculate publish time
        from datetime import datetime, timedelta
        publish_time = (datetime.now() + timedelta(hours=date_offset_hours)).strftime("%Y-%m-%d %H:%M")
        
        input_data.send_keys(publish_time)    
        time.sleep(3)
    
    print("上传完成！")
    time.sleep(3)
    # Publish
    driver.find_element("xpath", '//*[text()="发布"]').click()
    print("图文发布完成！")
    time.sleep(10)


def run(driver):
    xiaohongshu_login(driver=driver)
    mp4s = get_map4()
    for index, mp4 in enumerate(mp4s):
        publish_xiaohongshu(driver, mp4, index)
        time.sleep(10)

if __name__ == "__main__":
    try:
        driver = get_driver()
        xiaohongshu_login(driver=driver)
        mp4s = get_map4()
        for index, mp4 in enumerate(mp4s):
            publish_xiaohongshu(driver, mp4, index)
            time.sleep(10)
    finally:
        driver.quit()
