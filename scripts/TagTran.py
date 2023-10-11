import csv


def usingSpace_delSlash(tag):
    tag_len = len(tag)
    tag_usingSpace = tag.replace('_', ' ')
    tag_delSlash = ''
    for i in range(tag_len):
        if (i < tag_len - 1
                and tag_usingSpace[i] == '\\'
                and (tag_usingSpace[i + 1] == '(' or tag_usingSpace[i + 1] == ')')):
            continue
        else:
            tag_delSlash += tag_usingSpace[i]

    return tag_delSlash


class TagTran:
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
        # tag下划线，tag去除括号前的转义符'/'
        new_tag = usingSpace_delSlash(tag)
        if new_tag in self.translateDict:
            return self.translateDict[new_tag][0]
        else:
            return tag

    def update_translation(self, en_text, cn_text):
        new_en_text = usingSpace_delSlash(en_text)
        if self.translateDict.get(new_en_text, -1) == -1:
            # 字典新增内容
            self.translateDict[new_en_text] = [cn_text, 0]
        else:
            self.translateDict[new_en_text][0] = cn_text



