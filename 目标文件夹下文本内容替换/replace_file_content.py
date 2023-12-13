import os
import yaml

config_params = []
with open('config.yml','r',encoding='utf-8') as file:
    config_params = yaml.safe_load(file)

if __name__ == "__main__":
    for root, dirs, files in os.walk(config_params['destination_folder']):
        for file_name in files:
            if file_name == config_params['file_name']:
                print(f"开始替换文件内容--->{root}\{file_name}")
                try:
                    target_content = ''
                    with open(f"{root}\{file_name}",'r',encoding='UTF-8') as file:
                        content = file.read()
                        target_content = content.replace(config_params['before_content'],config_params['after_content'])
                    with open(f"{root}\{file_name}",'w',encoding='UTF-8') as file:
                        file.write(target_content)
                    print("替换成功")
                except:
                    print("替换失败")
    input("替换完成，任意键退出!")
                