class tagTran:
    def __init__(self):
        super().__init__()
        self.translateDict = {}  # 存储翻译结果的字典
        self.translation_file_path = "danbooru-cn.txt"  # 字典路径
        
        self.load_translation_file()

    def load_translation_file(self):
        with open(self.translation_file_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line:
                    parts = line.split("=")
                    if len(parts) == 2:
                        english = parts[0].strip()
                        chinese = parts[1].strip()
                        self.translateDict[english] = chinese
                        
    def saveTranslate(self):
        # 按照字典的键排序
        sortedList = sorted(self.translateDict.items(), key=lambda x: x[0])
        # 将sortedList的内容写入到翻译文件
        with open(self.translation_file_path, 'w', encoding='utf-8') as file:
            for key, value in sortedList:
                file.write(f"{key}={value}\n")
        self.ui.statusbar.showMessage("翻译文件已更新！", 700)

    def translateTag(self, tag):
        if tag in self.translateDict:
            return self.translateDict[tag]
        else:
            return tag
    
    def validate_file_lines(self):
        with open(self.translation_file_path, "r", encoding="utf-8") as file:
            line_number = 0
            for line in file:
                line_number += 1
                line = line.strip()
                if line:
                    if line.count("=") > 1:
                        print(f"Error: 发现多个等号，位于 {line_number}: {line}")
                        # 一次性输出所有错误位置
                        # return False
        return True
        
if __name__ == "__main__":
    # 翻译文件格式验证
    A = tagTran()
    result = A.validate_file_lines()
    if result:
        print("所有行都通过验证，没有多个等号。")
    else:
        print("存在多个等号的行，请检查错误信息。")