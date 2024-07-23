import os
import yaml
import json
from datetime import datetime

config_params = []

with open('config.yml','r',encoding='utf-8') as file:
    config_params = yaml.safe_load(file)

if __name__ == "__main__":
    for root,dirs,files in os.walk(config_params['folder_path']):
        for file in files:
            file_path = os.path.join(root,file)
            file_temp_path = file_path.split('.txt')[0]+"_temp.txt"
            print("开始处理文件--->"+file_path)
            lines = []
            flag = True
            with open(file_path,'r',encoding='utf-8') as txt,open(file_temp_path,'w',encoding='utf-8') as txt_temp:
                line = txt.readline()
                while line:
                    json_data = json.loads(line)
                    try:
                        collect_date = datetime.strptime(json_data['collectDate']+"","%Y-%m-%d %H:%M:%S").date()
                        target_date = datetime.strptime(config_params['collect_date'],"%Y-%m-%d").date()
                        if collect_date>=target_date:
                            txt_temp.write(line)
                    except:
                        flag = False
                        print("采集时间转换错误")
                        break
                    line = txt.readline()
            #如果flag是true删除原有文件，保留复制文件，false做相反操作
            if flag:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    os.rename(file_temp_path,file_path)
            else:
                if os.path.exists(file_temp_path):
                    os.remove(file_temp_path)
            print(file_path+"--->文件处理完成")
    input("操作完成，任意键退出!")