from selenium import webdriver
from selenium.webdriver.common.by import By
from xpinyin import Pinyin
import os
import yaml
import time
import win32gui
import win32con

config_params = []
with open('config.yml','r',encoding='utf-8') as file:
    config_params = yaml.safe_load(file)

pinyin = Pinyin()
browser = webdriver.Chrome()

def upload(filepath, browser_type="chrome"):
    if browser_type == "chrome":
        title = "打开"
    else:
        title = ""
 
    # 找元素
    # 从一级开始找，一级窗口“#32770”，“打开”
    dialog = win32gui.FindWindow("#32770", title)  # FindWindow用于找大窗口
 
    # 二级之后都用FindWindowEx，需要四个参数，
    # 1、元素的父亲，2、从第一个子代开始找元素，3、元素的类型名（class），4、元素的文本值
    comboBoxEx32 = win32gui.FindWindowEx(dialog, 0, "ComboBoxEx32", None)  # 二级
    comBox = win32gui.FindWindowEx(comboBoxEx32, 0, "ComboBox", None)  # 三级
    # 编辑框
    edit = win32gui.FindWindowEx(comBox, 0, 'Edit', None)  # 四级
    # 打开按钮
    button = win32gui.FindWindowEx(dialog, 0, 'Button', '打开(&0)')  # 二级
 
    # 往编辑框输入文件路径
    win32gui.SendMessage(edit, win32con.WM_SETTEXT, None, filepath)  # 发送文件路径
    win32gui.SendMessage(dialog, win32con.WM_COMMAND, 1, button)  # 点击打开按钮

def model_transformation(fbx_model_file,result_path):
    mode = browser.find_element(By.XPATH,'//button[text()="通用模型切片"]')
    mode.click()
    time.sleep(1)
    # 打开选择文件窗口
    fbx = browser.find_element(By.XPATH,'//button[text()="+FBX"]')
    fbx.click()
    time.sleep(1)
    # 选择文件
    upload(fbx_model_file)
    # 输出路径
    output_path = browser.find_element(By.XPATH,'//input[@placeholder="请设置输出路径"]')
    output_path.send_keys(result_path)
    #提交处理
    submit = browser.find_element(By.XPATH,'//button[text()="提交处理"]')
    submit.click()
    time.sleep(1)

if __name__ == "__main__":
    try:
        browser.implicitly_wait(10)
        browser.get('http://localhost:9003/login.html')
        browser.maximize_window()

        user_name = browser.find_element(By.XPATH,'//input[@placeholder="请输入手机号"]')
        user_name.send_keys(config_params['user_name'])
        password = browser.find_element(By.XPATH,'//input[@placeholder="请输入密码"]')
        password.send_keys(config_params['password'])
        log_on = browser.find_element(By.XPATH,'//button[text()="登录"]')
        log_on.click()
        time.sleep(1)
        for root,dirs,files in os.walk(config_params['fbx_model_path']):
            for file in files:
                result_path = os.path.join(pinyin.get_pinyin(os.path.join(root,file).replace(config_params['fbx_model_path'],config_params['result_path']).replace(file,'')).replace('-',''),file.replace(root.split('\\')[-1],'').replace('.FBX',''))
                model_transformation(os.path.join(root,file),result_path)
        time.sleep(10)
    except Exception as e:
        print(e)
    finally:
        browser.close()
        print('转换完成!')
    input('按任意键退出!')
