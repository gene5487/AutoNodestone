from PyQt5 import QtCore, QtWidgets, QtTest
from PyQt5.QtGui import QPixmap, QIcon
from UI import Ui_MainWindow
import os
import functools
import webbrowser

#  ================================================
import pyautogui
from os import listdir
from os.path import isfile
import pulp
from playsound import playsound
import cv2
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import numpy as np


# parameters for locate_25node_at_once
part_list = ['bl', 'tm', 'br']
br_cor = [18, 16, 10, 13]  # x, y, w, h
tm_cor = [11, 3, 10, 7]
bl_cor = [4, 16, 11, 13]
trinode_index_connvert_table = [[0,   1,  2,  3],
                                [4,   5,  6],
                                [7,   8,  9, 10],
                                [11, 12, 13],
                                [14, 15, 16, 17],
                                [18, 19, 20],
                                [21, 22, 23, 24]]

# parameters for get_skill_icon
offset = [-39, -16]  # from left top of skill_separation_line, to left top of skill icon
threshold = 0.95


def sound_effect(sound_type):
    if sound_type == 0:
        playsound(rf'./sound/Maplestory-012.wav', block=False)
    elif sound_type == 1:
        playsound(rf'./sound/Maplestory-010.wav', block=False)


def duplicate_images_detection(img1, img2):
    res = cv2.matchTemplate(img1, img2, cv2.TM_CCOEFF_NORMED)
    return res.max()


def concat_image_vertical(img1, img2):
    base_img = Image.new('RGB', (max(img1.width, img2.width), img1.height + img2.height), (255, 255, 255))
    base_img.paste(img1, (0, 0))
    base_img.paste(img2, (0, img1.height))
    return base_img


def result_image_generation(trinode_combination_number, trinode_screenshot_list, trinode_selection_list, trinode_redundant_list, same_trinode_first_count_wrt_node, trinode_col):
    base_image_w, base_image_h = 50 + 52 * trinode_selection_list.count(1) + 20 + 130 + 32 * len(trinode_redundant_list), 100
    combination_left = 50
    redundant_left = 50 + 52 * trinode_selection_list.count(1) + 20

    base_image = Image.new('RGB', (base_image_w, base_image_h), (255, 255, 255))
    draw = ImageDraw.Draw(base_image)
    font = ImageFont.truetype("arial.ttf", 32)
    [x0, y0, x1, y1] = draw.textbbox(xy=(0, 0), text=f"{trinode_combination_number}.", font=font)
    draw.text(xy=(combination_left / 2 - (x1 - x0) / 2, base_image_h / 2 - (y1 - y0) / 2),
              text=f"{trinode_combination_number}.",
              font=font, fill=(255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0))

    offset = 14
    width = 52
    next_left = combination_left
    for i, trinode_selection in enumerate(trinode_selection_list):
        if trinode_selection == 1:
            screenshot_index = 0
            num = i
            for row in trinode_col:
                if num >= len(row):
                    num -= len(row)
                    screenshot_index += 1
                else:
                    col = row[num]
                    break

            trinode_screenshot = Image.open(trinode_screenshot_list[screenshot_index])
            trinode_screenshot_w, trinode_screenshot_h = trinode_screenshot.size
            left = offset + width * col
            right = left + width
            # print(i)
            cropped = trinode_screenshot.crop((left, 0, right, trinode_screenshot_h))  # (left, top, right, bottom)
            base_image.paste(cropped, (next_left, int(base_image_h / 2 - trinode_screenshot_h / 2)))  # (left, top)

            font = ImageFont.truetype("arial.ttf", 24)

            [x0, y0, x1, y1] = draw.textbbox(xy=(0, 0), text=f"x{same_trinode_first_count_wrt_node[i]}", font=font)
            draw.text(xy=(next_left + width / 2 - (x1 - x0) / 2, 10),
                      text=f"x{same_trinode_first_count_wrt_node[i]}",
                      font=font, fill=(255, 255, 255), stroke_width=1, stroke_fill=(0, 0, 0))

            next_left += width

    if len(trinode_redundant_list) == 0:
        font = ImageFont.truetype("arial.ttf", 32)
        [x0, y0, x1, y1] = draw.textbbox(xy=(0, 0), text="Perfect", font=font)
        draw.text(xy=(redundant_left, base_image_h / 2 - (y1 - y0) / 2), text="Perfect",
                  font=font, fill=(255, 0, 0))
    else:
        font = ImageFont.truetype("arial.ttf", 16)
        [x0, y0, x1, y1] = draw.textbbox(xy=(0, 0), text="Redundant skill :  ", font=font)
        draw.text(xy=(redundant_left, base_image_h / 2 - (y1 - y0) / 2), text="Redundant skill :  ",
                  font=font, fill=(255, 0, 0))
        next_left = redundant_left + (x1 - x0)
        for i, trinode_redundant in enumerate(trinode_redundant_list):
            # redundant_node = Image.open(r'./instruction_img/node.png')
            # redundant_node_w, redundant_node_h = redundant_node.size
            skill_icon = Image.open(trinode_redundant)
            skill_icon_w, skill_icon_h = skill_icon.size
            # redundant_node.paste(skill_icon, (20, 17))  # (left, top)
            base_image.paste(skill_icon, (next_left, int(base_image_h / 2 - skill_icon_h / 2)))
            next_left += skill_icon_w
    return base_image


# 9/7 new V-matrix UI update
def locate_25node_at_once(skill_icon_path_list, page, n_trinode_inlist, job_name, all_partial_skill_img_list, skill_name_list):
    query_icon_position = pyautogui.locateCenterOnScreen('./template_icon/query_icon.jpg', confidence=0.8)
    if query_icon_position is None:
        print('Unable to detect V-matrix UI.')
        return [], [], [], '', []
    v_matrix_region = [query_icon_position[0] - 255, query_icon_position[1] - 110, 596, 80]
    screenshot_name = rf'./V-matrix_{job_name}_{page}.jpg'
    pyautogui.screenshot(screenshot_name, region=v_matrix_region)

    # [["skill_name"], ["skill_name"], ["skill_name"]......], record skill name
    trinode_name_list = [[] for _ in range(11)]
    # [[x, y], [x, y]......], record position of trinode's bl part
    trinode_position = [[] for _ in range(11)]
    # [[0,0,......], [0,0,......],......], one-hot code which records the 3 skills of this trinode
    trinode_skill = [[0 for _ in range(len(skill_icon_path_list))] for _ in range(11)]
    trinode_first = [[0 for _ in range(len(skill_icon_path_list))] for _ in range(11)]
    for i, (partial_skill_img_list, part) in enumerate(zip(all_partial_skill_img_list, part_list)):
        for j, (partial_img, skill_name) in enumerate(zip(partial_skill_img_list, skill_name_list)):
            # print(f'Detecting {part} of {skill_name} : ')
            find_list = list(pyautogui.locateAllOnScreen(partial_img,
                                                        region=v_matrix_region,
                                                        confidence=threshold))  # (left, top, width, height) tuples
            
            # 去除相邻像素的匹配结果
            position_list = [find_list[0]] if len(find_list) > 0 else []
            for fi in range(1, len(find_list)):
                diffX = find_list[fi].left - find_list[fi-1].left
                diffY = find_list[fi].top - find_list[fi-1].top
                if diffX <= 5 and diffY <= 5:
                    continue
                else:
                    position_list.append(find_list[fi])
        
            for position in position_list:
                col = int((position[0] - v_matrix_region[0] - 15) / 51)  # 15 is left most offset

                # print(f'{part} of {skill_name} is detected at {position}, which is row{row}, col{col}')
                trinode_name_list[col].append(skill_name)
                trinode_skill[col][j] = 1
                if i == 0:  # bl, first skill
                    trinode_first[col][j] = 1
                    trinode_position[col] = [position[0] - v_matrix_region[0], position[1] - v_matrix_region[1]]

    for trinode in trinode_name_list:
        if len(trinode) == 2:
            print("Warning! Only 2 of skill is detected for a trinode, "
                  "please make sure all trinode is unlocked before scanning.")
        if len(trinode) > 3:
            print(rf"Warning! More than 3 skill is detected for a trinode, "
                  rf"please make sure all duplicate/unneeded skill icon at ./skill_icon/{job_name} are deleted manually before scanning.")
    scanned_ok_indices = [i for i in range(len(trinode_name_list)) if len(trinode_name_list[i]) == 3]
    trinode_name_list = [trinode_name_list[i] for i in scanned_ok_indices]
    trinode_position = [trinode_position[i] for i in scanned_ok_indices]
    trinode_skill = [trinode_skill[i] for i in scanned_ok_indices]
    trinode_first = [trinode_first[i] for i in scanned_ok_indices]

    img = Image.open(screenshot_name)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", 32)
    for i, position in enumerate(trinode_position):
        [x0, y0, x1, y1] = draw.textbbox(xy=(0, 0), text=f"{n_trinode_inlist + i}", font=font)
        w = x1 - x0
        # xy=(top, left) of text,
        # I want that "middle of text" align to "middle of trinode" icon for different digit text
        draw.text(xy=((position[0]+12)-(w/2), position[1]+12), text=f"{n_trinode_inlist + i}",
                  font=font, fill=(255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0))

    img.save(screenshot_name)
    return trinode_name_list, trinode_skill, trinode_first, screenshot_name, scanned_ok_indices


def get_skill_icon(my_job, skill_icon_page, scan_region):
    template = cv2.imread(r'./template_icon/left_square_bracket.png')
    h, w = template.shape[:-1]
    pyautogui.screenshot(f'SkillIconMatchingResult_{my_job}_{skill_icon_page}.png', region=scan_region)
    img = cv2.imread(f'SkillIconMatchingResult_{my_job}_{skill_icon_page}.png')
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)  # return indices that meet condition
    for i, pt in enumerate(zip(*loc[::-1])):  # Switch columns and rows
        left, top = pt[0] + offset[0], pt[1] + offset[1]
        icon = img[top: (top + 32), left: (left + 32)]

        # prevent duplicate icon
        duplicate = False
        for exist_icon in os.listdir(rf'./skill_icon/{my_job}'):
            if duplicate_images_detection(cv2.imread(rf'./skill_icon/{my_job}/{exist_icon}'), icon) >= threshold:
                duplicate = True
                break
        if not duplicate:
            cv2.imwrite(rf'./skill_icon/{my_job}/SkillIcon_{skill_icon_page}_{i}.png',
                        icon, (cv2.IMWRITE_PNG_COMPRESSION, 0))

    for i, pt in enumerate(zip(*loc[::-1])):  # Switch columns and rows
        left, top = pt[0] + offset[0], pt[1] + offset[1]
        # red box for left_square_bracket
        # cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
        # green box for skill_icon
        cv2.rectangle(img, (left, top), (left + 32, top + 32), (0, 255, 0), 2)

    screenshot_name = f'SkillIconMatchingResult_{my_job}_{skill_icon_page}.png'
    cv2.imwrite(screenshot_name, img)
    return len(loc[0]), screenshot_name  # return how many skill icon is detected


def update_skill_icon(my_job_path):
    # update skill_img_list after get_skill_icon
    skill_img_list = [rf"{my_job_path}/{img_name}" for img_name in listdir(my_job_path) if
                      isfile(rf"{my_job_path}/{img_name}")]
    n_skill = len(skill_img_list)

    # variable for locate_25node_at_once
    # cv2.imread(img) not support Unicode characters (chinese, 墨玄),
    # use cv2.imdecode(np.fromfile(img, dtype=np.uint8), cv2.IMREAD_UNCHANGED) instead
    bl_skill_img_list = [cv2.imread(img)
                         [bl_cor[1]: bl_cor[1] + bl_cor[3], bl_cor[0]:bl_cor[0] + bl_cor[2]]
                         for img in skill_img_list]
    tm_skill_img_list = [cv2.imread(img)
                         [tm_cor[1]: tm_cor[1] + tm_cor[3], tm_cor[0]:tm_cor[0] + tm_cor[2]]
                         for img in skill_img_list]
    br_skill_img_list = [cv2.imread(img)
                         [br_cor[1]: br_cor[1] + br_cor[3], br_cor[0]:br_cor[0] + br_cor[2]]
                         for img in skill_img_list]
    skill_name_list = [rf'{img.split("/")[-1].split(".")[0]}'
                       for img in skill_img_list]
    all_partial_skill_img_list = [bl_skill_img_list, tm_skill_img_list, br_skill_img_list]
    return skill_img_list, n_skill, bl_skill_img_list, tm_skill_img_list, br_skill_img_list, skill_name_list, all_partial_skill_img_list


class_group_list = ["warrior", "magician", "bowman", "thief", "pirate"]
job_dict = {
    # warrior
    '1623862925166.png': 'Mihile',
    '1623863170980.png': 'Dawn Warrior',
    '1623863311668.png': 'Demon Slayer',
    '1623863334997.png': 'Demon Avenger',
    '1623863478185.png': 'Blaster',
    '1623863594076.png': 'Zero',
    '1623863677248.png': 'Aran',
    '1623864046006.png': 'Kaiser',
    '1623864201695.png': 'Adele',
    '1623864522972.png': 'Hayato',
    '1654688398784.png': 'Hero',
    '1654688415659.png': 'Paladin',
    '1654688444144.png': 'Dark Knight',

    # magician
    '1623862952947.png': 'Blaze Wizard',
    '1623863453107.png': 'Battle Mage',
    '1623863567639.png': 'Beast Tamer',
    '1623863622826.png': 'Kinesis',
    '1623863692905.png': 'Luminous',
    '1623863715312.png': 'Evan',
    '1623864170710.png': 'Illium',
    '1623864486240.png': 'Kanna',
    '1641378894730.png': 'Lara',
    '1654688455738.png': 'Ice Lightning Mage',
    '1654688469035.png': 'Fire Poison Mage',
    '1654688484363.png': 'Bishop',

    # bowman
    '1623862499274.png': 'Pathfinder',
    '1623862975353.png': 'Wind Archer',
    '1623863269137.png': 'Wild Hunter',
    '1623863704280.png': 'Mercedes',
    '1624043465662.png': 'Kain',
    '1654688520082.png': 'Bowmaster',
    '1654688534207.png': 'Marksman',
    
    # thief
    '1623863129558.png': 'Night Walker',
    '1623863292684.png': 'Xenon',
    '1623863581139.png': 'Hoyoung',
    '1623863663123.png': 'Phantom',
    '1623864058147.png': 'Cadena',
    '1654688547411.png': 'Shadower',
    '1654688561098.png': 'Dual Blade',
    '1654688581020.png': 'Night Lord',
    # pirate
    '1623863047573.png': 'Thunder Breaker',
    '1623863467091.png': 'Mechanic',
    '1623863633498.png': 'Mo Xuan',
    '1623863731312.png': 'Shade',
    '1623864070960.png': 'Angelic Buster',
    '1623864185695.png': 'Ark',
    '1654688597021.png': 'Buccaneer',
    '1654688624458.png': 'Cannoneer',
    '1655747036270.png': 'Corsair'
}


class MainWindow_controller(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setup_control()

        self.skill_toggle_button_list = [self.ui.skill_toggleButton_1, self.ui.skill_toggleButton_2,
                                         self.ui.skill_toggleButton_3, self.ui.skill_toggleButton_4,
                                         self.ui.skill_toggleButton_5, self.ui.skill_toggleButton_6,
                                         self.ui.skill_toggleButton_7, self.ui.skill_toggleButton_8,
                                         self.ui.skill_toggleButton_9, self.ui.skill_toggleButton_10,
                                         self.ui.skill_toggleButton_11, self.ui.skill_toggleButton_12,
                                         self.ui.skill_toggleButton_13, self.ui.skill_toggleButton_14,
                                         self.ui.skill_toggleButton_15, self.ui.skill_toggleButton_16,
                                         self.ui.skill_toggleButton_17, self.ui.skill_toggleButton_18,
                                         self.ui.skill_toggleButton_19, self.ui.skill_toggleButton_20]

        self.job_name = ''
        self.job_dir = ''
        self.skill_img_list = []
        self.n_skill = 0
        self.bl_skill_img_list = []
        self.tm_skill_img_list = []
        self.br_skill_img_list = []
        self.skill_name_list = []
        self.all_partial_skill_img_list = []

        self.get_icon_page = 0  # skill_icon_generation

        self.trinode_skill = []
        self.trinode_first = []
        self.page = 0  # locate_11_at_once
        self.screenshot_name_list = []
        self.trinode_col = []

    def setup_control(self):
        self.ui.pushButton_b.clicked.connect(self.scan25_button)
        self.ui.pushButton_e.clicked.connect(self.get_combination)
        self.ui.pushButton_g.clicked.connect(self.get_icon_button)
        self.ui.pushButton_o.clicked.connect(self.open_directory)

        pixmap = QPixmap("./instruction_img/start_up.png").scaled(self.ui.display_label.size(), QtCore.Qt.KeepAspectRatio,
                                                                  QtCore.Qt.SmoothTransformation)
        self.ui.display_label.setPixmap(pixmap)

        for button, class_group in zip(self.ui.horizontalLayoutWidget.children()[1:], class_group_list):
            button.setIconSize(QtCore.QSize(button.width(), button.height()))
            # print(button.objectName())
            button.setIcon(QIcon(rf"./job_icon/class/{class_group}.webp"))
            button.clicked.connect(functools.partial(self.show_job_portrait, class_group))

        # self.ui.file_button.clicked.connect(self.open_file)
        # self.ui.dir_button.clicked.connect(self.open_folder)

    def show_job_portrait(self, class_group):
        job_img_list = os.listdir(rf'./job_icon/job/{class_group}')
        # print(job_img_list)
        for button in self.ui.horizontalLayoutWidget_2.children()[1:]:
            # button.setStyleSheet(rf"border-image : url()")  # clear icon
            button.setIcon(QIcon())
        for button, img in zip(self.ui.horizontalLayoutWidget_2.children()[1:], job_img_list):
            # print(button.objectName())
            # Method1: setStyleSheet : https://www.geeksforgeeks.org/pyqt5-how-to-adjust-the-image-inside-push-button/
            # button.setStyleSheet(rf"border-image : url('./job_icon/job/{class_group}/{img}')")

            # Method2: QPixmap.scaled
            # button.iconSize() , button.size(), QtCore.QSize(60, 170)
            # pixmap = QPixmap(rf'./job_icon/job/{class_group}/{img}').scaled(button.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            # button.setIcon(QIcon(pixmap))

            # Method3: setIconSize
            button.setIcon(QIcon(rf'./job_icon/job/{class_group}/{img}'))
            button.setIconSize(QtCore.QSize(100, 170))

            # https://stackoverflow.com/questions/21586643
            # reset button function
            try:
                button.clicked.disconnect()
            except Exception:
                pass
            button.clicked.connect(functools.partial(self.show_job_skill_icon, job_dict[img]))

    def show_job_skill_icon(self, job):
        self.job_name = job
        self.job_dir = rf"./skill_icon/{job}"
        # self.skill_img_list : image path
        self.skill_img_list, self.n_skill, self.bl_skill_img_list, self.tm_skill_img_list, self.br_skill_img_list, \
            self.skill_name_list, self.all_partial_skill_img_list = update_skill_icon(self.job_dir)

        for button in self.ui.gridLayoutWidget.children()[1:]:
            button.setIcon(QIcon())
        for button, icon in zip(self.skill_toggle_button_list, self.skill_img_list):
            # print(button.objectName())
            button.setIcon(QIcon(icon))

        print(f'{self.n_skill} skill icon file in {self.job_dir}')
        self.trinode_skill = []
        self.trinode_first = []
        self.page = 0
        self.screenshot_name_list = []
        self.trinode_col = []
        # self.get_icon_page = 0

        self.ui.skill_label.setText(f"# Skills : {self.n_skill}")
        self.ui.nodestone_label.setText(f"# Nodestones : {len(self.trinode_skill)}")

    def get_combination(self):
        n_trinode = len(self.trinode_skill)
        if n_trinode == 0:
            print("You have not scanned any Nodestone!")
            return

        required_skill = []
        required_skill_name_list = []
        for button, icon in zip(self.skill_toggle_button_list, self.skill_img_list):
            print(button.objectName(), icon)
            if button.isChecked():
                # print("checked")
                required_skill.append(self.skill_img_list.index(icon))
                required_skill_name_list.append(icon.split('/')[-1].split('.')[0])

        if len(required_skill) == 0:
            print("You have not selected any required skill!")
            return
        print(f'Your required skill [{len(required_skill_name_list)}] : {required_skill_name_list}')

        same_trinode_first_count = []  # W.R.T. each skill
        for j in range(self.n_skill):
            count = sum(row[j] for row in self.trinode_first)
            same_trinode_first_count.append(count)
        same_trinode_first_count_wrt_node = [same_trinode_first_count[self.trinode_first[i].index(1)] for i in range(len(self.trinode_first))]

        level_up_penalty_list = []
        for i in range(n_trinode):
            level_up_penalty = (n_trinode - same_trinode_first_count[self.trinode_first[i].index(1)]) / n_trinode
            # print(level_up_penalty)  # 0~1
            level_up_penalty_list.append(level_up_penalty)

        prob = pulp.LpProblem("trinode_combination", sense=pulp.LpMinimize)
        trinode_select_var = pulp.LpVariable.dicts('trinode_select', range(0, n_trinode), cat='Binary')
        prob += pulp.lpSum(trinode_select_var[i] * (1 + 0.1*level_up_penalty_list[i]) for i in range(n_trinode))  # objective function, 最小化選用的核心數
        for skill in required_skill:
            # 在所有選用的核心所強化的技能中，所有required_skill都需至少出現2次
            prob += pulp.lpSum(
                [trinode_select_var[trinode] * self.trinode_skill[trinode][skill] for trinode in range(n_trinode)]) >= 2
        for skill in range(self.n_skill):
            # 在所有選用的核心所強化的技能中，每個核心的第一個技能不能重複
            prob += pulp.lpSum(
                [trinode_select_var[trinode] * self.trinode_first[trinode][skill] for trinode in range(n_trinode)]) <= 1

        at_least_one_solution = False
        for i in range(3):
            prob.solve(pulp.PULP_CBC_CMD(msg=False))
            print(f"==========Result({i+1})==========")
            print("Solve status:", pulp.LpStatus[prob.status])  # 輸出求解狀態

            trinode_redundant_list = []
            if prob.status == pulp.LpStatusOptimal:
                sorted_variables = sorted(prob.variables(), key=lambda v: int(v.name.split('_')[-1]))
                selected = [i for i, var in enumerate(sorted_variables) if var.varValue == 1]
                selected_row = [self.trinode_skill[i] for i in selected]
                for j in range(self.n_skill):
                    if j in required_skill:
                        continue
                    else:
                        if sum(row[j] for row in selected_row) >= 1:
                            trinode_redundant_list.append(self.skill_img_list[j])
                result_image = result_image_generation(trinode_combination_number=i+1,
                                                       trinode_screenshot_list=self.screenshot_name_list,
                                                       trinode_selection_list=[var.varValue for var in sorted_variables],
                                                       trinode_redundant_list=trinode_redundant_list,
                                                       same_trinode_first_count_wrt_node=same_trinode_first_count_wrt_node,
                                                       trinode_col=self.trinode_col)

                if i == 0:
                    result_image_base = result_image
                    at_least_one_solution = True
                else:
                    result_image_base = concat_image_vertical(result_image_base, result_image)

                print("Minimal number of Nodestone needed = ", int(pulp.value(prob.objective)))  # 輸出最優解的目標函數值
                if pulp.value(prob.objective) == len(required_skill) * 2 / 3.0:
                    print("You got PERFECT Nodestone combination ! ")
                print("\nThe following Nodestones combination can meet your requirement with minimal number of Nodestone.")
                for v in prob.variables():
                    # print(v.name, "=", v.varValue)  # 輸出每個變數的最優值
                    if v.varValue == 1:
                        trinode_index = int(v.name.split('_')[-1])
                        skill_indices = [i for i, x in enumerate(self.trinode_skill[trinode_index]) if x == 1]
                        skill_name = []
                        same_trinode_first = 0
                        for skill_index in skill_indices:
                            if self.trinode_first[trinode_index][skill_index] == 1:
                                skill_name.append(f"【{self.skill_img_list[skill_index].split('/')[-1].split('.')[0]}】")
                                same_trinode_first = same_trinode_first_count[skill_index]
                            else:
                                skill_name.append(self.skill_img_list[skill_index].split('/')[-1].split('.')[0])
                        print(f'Nodestone {trinode_index} : {skill_name}, count = {same_trinode_first}')

                # get suboptimal solutions, add new constraint that would be violated by optimal solution
                previous_solution_indices = [i for i, var in enumerate(sorted_variables) if var.varValue == 1]
                print(previous_solution_indices)
                print([sorted_variables[i].name for i in previous_solution_indices])
                previous_solution_node_count = int(
                    sum([sorted_variables[i].varValue for i in previous_solution_indices]))

                prob += pulp.lpSum([trinode_select_var[i] for i in previous_solution_indices]) <= (
                            previous_solution_node_count - 1)
                # prob += (previous_solution_node_count + 1) <= pulp.lpSum(
                #     [trinode_select_var[i] for i in previous_solution_indices])

            else:
                print("None of Nodestone combination can meet your requirement !")

        if at_least_one_solution:
            result_image_name = f'Result_{self.job_name}.png'
            result_image_base.save(result_image_name)
            pixmap = QPixmap(result_image_name).scaled(self.ui.display_label.size(), QtCore.Qt.KeepAspectRatio,
                                                       QtCore.Qt.SmoothTransformation)
            self.ui.display_label.setPixmap(pixmap)

    def scan25_button(self):
        new_trinode_name_list, new_trinode_skill, new_trinode_first, screenshot_name, trinode_col \
            = locate_25node_at_once(skill_icon_path_list=self.skill_img_list,
                                    page=self.page,
                                    n_trinode_inlist=len(self.trinode_skill),
                                    job_name=self.job_name,
                                    all_partial_skill_img_list=self.all_partial_skill_img_list,
                                    skill_name_list=self.skill_name_list)
        if len(new_trinode_skill) != 0:
            self.trinode_skill.extend(new_trinode_skill)
            self.trinode_first.extend(new_trinode_first)
            self.screenshot_name_list.append(screenshot_name)
            self.trinode_col.extend([trinode_col])
            print(self.trinode_col)

            for trinode_name in new_trinode_name_list:
                print(trinode_name)
            self.page += 1
            sound_effect(1)
            pixmap = QPixmap(screenshot_name).scaled(self.ui.display_label.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.ui.display_label.setPixmap(pixmap)
            self.ui.nodestone_label.setText(f"# Nodestones : {len(self.trinode_skill)}")
        else:
            sound_effect(0)
            pixmap = QPixmap("./instruction_img/crafting_ui.png").scaled(self.ui.display_label.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.ui.display_label.setPixmap(pixmap)
            # self.ui.display_label.setStyleSheet(r"border-image : url(./instruction_img/crafting_ui.png)")
        print(rf'{len(new_trinode_skill)} Nodestone are detected.')

    def get_icon_button(self):
        pixmap = QPixmap("./instruction_img/move_cursor.png").scaled(self.ui.display_label.size(),
                                                                  QtCore.Qt.KeepAspectRatio,
                                                                  QtCore.Qt.SmoothTransformation)
        self.ui.display_label.setPixmap(pixmap)
        for retry in range(3):
            self.ui.pushButton_g.setText(f'Waiting...({3 - retry})')
            QtTest.QTest.qWait(1000)
        cursor_position = pyautogui.position()
        scan_region = [cursor_position[0] - 150, cursor_position[1], 350, 250]
        n_skill_icon, screenshot_name = get_skill_icon(my_job=self.job_name, skill_icon_page=self.get_icon_page, scan_region=scan_region)
        if n_skill_icon != 0:
            # update_skill_icon(self.job_dir)
            self.get_icon_page += 1
            sound_effect(1)
            pixmap = QPixmap(screenshot_name).scaled(self.ui.display_label.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.ui.display_label.setPixmap(pixmap)
            print(rf'{n_skill_icon} skill icon are detected, saved at {self.job_dir}.')

            self.show_job_skill_icon(job=self.job_name)

        else:
            sound_effect(0)
            print(rf'No skill icon are detected.')
            pixmap = QPixmap("./instruction_img/get_icon.png").scaled(self.ui.display_label.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.ui.display_label.setPixmap(pixmap)
            # self.ui.display_label.setStyleSheet(r"border-image : url(./instruction_img/get_icon.png)")

        self.ui.pushButton_g.setText("Generate skill icon")

    def open_directory(self):
        webbrowser.open(os.path.realpath(self.job_dir))
