import json
import yaml

class file_merge(object):

    @classmethod
    def merge_dicts(cls,dict1, dict2, merge_lists=True):  
        """  
        递归合并两个字典，支持多层结构和列表的合并（如果merge_lists为True）。  

        :param dict1: 第一个字典  
        :param dict2: 第二个字典  
        :param merge_lists: 是否尝试合并列表。如果为False，则列表将被直接覆盖。  
        :return: 合并后的字典  
        """  
        result = dict1.copy()  
    
        for key, value in dict2.items():
            if key in result:  
                if isinstance(value, dict) and isinstance(result[key], dict):  
                    # 递归合并两个字典  
                    result[key] = cls.merge_dicts(result[key], value, merge_lists=merge_lists)  
                elif isinstance(value, list) and isinstance(result[key], list) and merge_lists:  
                    # 尝试合并两个列表（这里简单地使用列表扩展，可能需要根据实际情况调整）  
                    result[key] = result[key] + [item for item in value if item not in result[key]]  
                else:  
                    # 直接覆盖  
                    result[key] = value  
            else:  
                # 添加新键  
                result[key] = value  
    
        return result  
    
    @classmethod
    def json_merge(cls,f1_path,f2_path,merge_file_path):
        # 读取JSON文件  
        with open(f1_path, 'r',encoding='utf-8') as f1:  
            data1 = json.load(f1)  
        
        with open(f2_path, 'r',encoding='utf-8') as f2:  
            data2 = json.load(f2)  
        
        # 合并字典，这里假设我们想要合并列表  
        merged_data = cls.merge_dicts(data1, data2, merge_lists=True)  
        
        # 如果你不希望合并列表，而是想要覆盖，可以将merge_lists设置为False  
        # merged_data = merge_dicts(data1, data2, merge_lists=False)  
        
        # 将合并后的数据写回JSON文件  
        with open(merge_file_path, 'w',encoding='utf-8') as f:  
            json.dump(merged_data, f, indent=4)
    
    @classmethod
    def yaml_merge(cls,f1_path,f2_path,merge_file_path):
        with open(f1_path, 'r', encoding='utf-8') as f1, open(f2_path, 'r', encoding='utf-8') as f2:
            dict1 = yaml.safe_load(f1)
            dict2 = yaml.safe_load(f2) 
            merged_data = cls.merge_dicts(dict1, dict2, merge_lists=True)
        with open(merge_file_path, 'w',encoding='utf-8') as f:  
            yaml.dump(merged_data, f, indent=4,allow_unicode=True,sort_keys=False)