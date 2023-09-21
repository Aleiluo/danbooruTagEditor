import csv


class tagTran:
    def __init__(self):
        super().__init__()
        self.inf_post_count = 1145141919810
        self.translateDict = {}  # 存储翻译结果的字典
        self.translation_file_path = "danbooru-cn.csv"  # 字典路径
        self.load_translation_file()

    def load_translation_file(self):
        with open(self.translation_file_path, "r", newline='', encoding="utf-8") as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                en_text = row[0].strip()
                cn_text = row[1].strip()
                post_count = int(row[2])
                self.translateDict[en_text] = [cn_text, post_count]

    def write_translation_file(self):
        # 保存翻译文件
        with open(self.translation_file_path, "w", newline='', encoding="utf-8") as file:
            csv_writer = csv.writer(file)
            for en_text, translation_info in self.translateDict.items():
                cn_text = translation_info[0]
                post_count = translation_info[1]
                csv_writer.writerow([en_text, cn_text if cn_text else 'None', post_count])
        self.ui.statusbar.showMessage("翻译文件已更新！", 700)

    def translateTag(self, tag):
        if tag in self.translateDict:
            return self.translateDict[tag][0]
        else:
            return tag

    def update_translation(self, en_text, cn_text):
        if self.translateDict.get(en_text, -1) == -1:
            # 字典新增内容
            self.translateDict[en_text] = [cn_text, 0]
        else:
            self.translateDict[en_text][0] = cn_text


