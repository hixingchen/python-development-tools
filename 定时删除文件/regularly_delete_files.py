import yaml
import os
import schedule
from datetime import datetime,date,timedelta
import time

config_params = []
with open('config.yml','r',encoding='utf-8') as file:
    config_params = yaml.safe_load(file)

current_date = date.today()
begin_date = current_date - timedelta(days=config_params['days'])

file_nums = 0

def work():
    file_nums = 0
    print(f"定时任务执行时间:{current_date}")
    for root, dirs, files in os.walk('./'):
        for file_name in files:
            try:
                date_string = file_name.split('.')[0].split('all-')[1]
                date = datetime.strptime(date_string,f"%Y-%m-%d").date()
                if begin_date>date:
                    os.remove(os.path.join(root,file_name))
                    file_nums += 1
            except:
                continue
    else:
        print(f"共删除文件{file_nums}个")

if __name__ == "__main__":
    work()
    schedule.every().day.at(config_params['time']).do(work)
    while True:
        schedule.run_pending()
        time.sleep(1)
