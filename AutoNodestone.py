from tkinter.filedialog import askopenfilename, askopenfilenames, askdirectory
from tkinter import Tk
import pyautogui
from os import system
from os import listdir
from os.path import isfile
import keyboard
import pulp
from playsound import playsound
import pickle
import cv2
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import numpy as np


# parameters for locate_25node_at_once
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


def locate_25node_at_once(skill_icon_path_list, page, n_trinode_inlist):
    query_icon_position = pyautogui.locateCenterOnScreen('./template_icon/query_icon.jpg', confidence=0.8)
    if query_icon_position is None:
        print('Unable to detect 25-core-per-page UI. Did you talk to V core master?')
        return [], [], []
    v_matrix_region = [query_icon_position[0] + 20, query_icon_position[1] - 470, 375, 405]
    scrennshot_name = rf'./V-matrix_{my_job}_{page}.jpg'
    pyautogui.screenshot(scrennshot_name, region=v_matrix_region)

    # [["skill_name"], ["skill_name"], ["skill_name"]......], record skill name
    trinode_name_list = [[] for _ in range(25)]
    # [[x, y], [x, y]......], record position of trinode's bl part
    trinode_position = [[] for _ in range(25)]
    # [[0,0,......], [0,0,......],......], one-hot code which records the 3 skills of this trinode
    trinode_skill = [[0 for _ in range(len(skill_icon_path_list))] for _ in range(25)]
    trinode_first = [[0 for _ in range(len(skill_icon_path_list))] for _ in range(25)]
    for i, (partial_skill_img_list, part) in enumerate(zip(all_partial_skill_img_list, part_list)):
        for j, (partial_img, skill_name) in enumerate(zip(partial_skill_img_list, skill_name_list)):
            # print(f'Detecting {part} of {skill_name} : ')
            position_list = pyautogui.locateAllOnScreen(partial_img,
                                                        region=v_matrix_region)  # (left, top, width, height) tuples
            for position in position_list:
                row = int((position[1] - v_matrix_region[1]) / 57)
                if (row % 2) == 0:
                    col = int((position[0] - v_matrix_region[0]) / 110)
                else:
                    col = int((position[0] - v_matrix_region[0] - 55) / 110)

                # print(f'{part} of {skill_name} is detected at {position}, which is row{row}, col{col}')
                index = trinode_index_connvert_table[row][col]
                trinode_name_list[index].append(skill_name)
                trinode_skill[index][j] = 1
                if i == 0:  # bl, first skill
                    trinode_first[index][j] = 1
                    trinode_position[index] = [position[0] - v_matrix_region[0], position[1] - v_matrix_region[1]]

    for trinode in trinode_name_list:
        if len(trinode) == 2:
            print("Warning! Only 2 of skill is detected for a trinode, "
                  "please make sure all trinode is unlocked before scanning.")
        if len(trinode) > 3:
            print(rf"Warning! More than 3 skill is detected for a trinode, "
                  rf"please make sure all duplicate/unneeded skill icon at {my_job_path} are deleted manually before scanning.")
    scanned_ok_indices = [i for i in range(len(trinode_name_list)) if len(trinode_name_list[i]) == 3]
    trinode_name_list = [trinode_name_list[i] for i in scanned_ok_indices]
    trinode_position = [trinode_position[i] for i in scanned_ok_indices]
    trinode_skill = [trinode_skill[i] for i in scanned_ok_indices]
    trinode_first = [trinode_first[i] for i in scanned_ok_indices]

    img = Image.open(scrennshot_name)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", 32)
    for i, position in enumerate(trinode_position):
        [x0, y0, x1, y1] = draw.textbbox(xy=(0, 0), text=f"{n_trinode_inlist + i}", font=font)
        w = x1 - x0
        # xy=(top, left) of text,
        # I want that "middle of text" align to "middle of trinode" icon for different digit text
        draw.text(xy=((position[0]+12)-(w/2), position[1]+10), text=f"{n_trinode_inlist + i}",
                  font=font, fill=(255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0))

    img.save(scrennshot_name)
    return trinode_name_list, trinode_skill, trinode_first


def get_skill_icon(my_job, skill_icon_page, scan_region):
    template = cv2.imread(r'./template_icon/left_square_bracket.png')
    h, w = template.shape[:-1]
    pyautogui.screenshot(f'SkillIconMatchingResult_{my_job}_{skill_icon_page}.png', region=scan_region)
    img = cv2.imread(f'SkillIconMatchingResult_{my_job}_{skill_icon_page}.png')
    # img = cv2.imdecode(np.fromfile(f'SkillIconMatchingResult_{my_job}_{skill_icon_page}.png', dtype=np.uint8), cv2.IMREAD_UNCHANGED)
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)  # return indices that meet condition
    for i, pt in enumerate(zip(*loc[::-1])):  # Switch columns and rows
        left, top = pt[0] + offset[0], pt[1] + offset[1]
        cv2.imwrite(rf'./skill_icon/{my_job}/SkillIcon_{skill_icon_page}_{i}.png',
                    img[top: (top + 32), left: (left + 32)], (cv2.IMWRITE_PNG_COMPRESSION, 0))

    for i, pt in enumerate(zip(*loc[::-1])):  # Switch columns and rows
        left, top = pt[0] + offset[0], pt[1] + offset[1]
        # red box for skill_separation_line
        cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
        # green box for skill icon
        cv2.rectangle(img, (left, top), (left + 32, top + 32), (0, 255, 0), 2)

    cv2.imwrite(f'SkillIconMatchingResult_{my_job}_{skill_icon_page}.png', img)
    return len(loc[0])  # return how many skill icon is detected


def update_skill_icon(my_job_path):
    # update skill_img_list after get_skill_icon
    skill_img_list = [rf"{my_job_path}/{img_name}" for img_name in listdir(my_job_path) if
                      isfile(rf"{my_job_path}/{img_name}")]
    n_skill = len(skill_img_list)

    # variable for locate_25node_at_once
    # cv2.imread(img) not support Unicode characters (chinese, 墨玄),
    # use cv2.imdecode(np.fromfile(img, dtype=np.uint8), cv2.IMREAD_UNCHANGED) instead
    bl_skill_img_list = [cv2.imread(img)
                         [bl_cor[1]: bl_cor[1] + tm_cor[3], bl_cor[0]:bl_cor[0] + bl_cor[2]]
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


print("==========Stage 1 : Select your job==========")
root = Tk()
root.withdraw()
root.wm_attributes('-topmost', 1)
my_job_path = askdirectory(title='Select your job', initialdir=r'./skill_icon', parent=root)
my_job = my_job_path.split("/")[-1]
print(f'You are {my_job}')

skill_img_list, n_skill, bl_skill_img_list, tm_skill_img_list, br_skill_img_list, \
    skill_name_list, all_partial_skill_img_list = update_skill_icon(my_job_path)
print(f'{n_skill} skill icon file in {my_job_path}')

trinode_skill = []
trinode_first = []

part_list = ['bl', 'tm', 'br']
page = 0
skill_icon_page = 0

print("==========Stage 2 : Input your Nodestone==========")
print("Let program scan through all Nodestone you have\n")
print("Press 'g' to generate skill icon png file (Put cursor on the Nodestone to show the 3 skill icon)")
print("Press 'i' to scan the Nodestone currently on screen (Put cursor on the Nodestone to show the 3 skill icon)")
print("Press 'b' to scan whole V-matrix page (Talk to V core master, open the 25-core-per-page UI)")
print("Press 's' to save scanned Nodestone to file")
print("Press 'l' to load scanned Nodestone from file")
print("Press 'e' to end this stage\n")
K = keyboard.read_key()
while K != 'e':
    if K == 's':
        with open(rf'./save/{my_job_path.split("/")[-1]}.pkl', 'wb') as save_file:
            pickle.dump([trinode_skill, trinode_first], save_file)
        print(rf'Save {len(trinode_skill)} Nodestone to ./save/{my_job_path.split("/")[-1]}.pkl')

    elif K == 'l':
        load_file_path = askopenfilename(filetypes=[('save file', '.pkl')], initialdir=r'./save')
        with open(load_file_path, 'rb') as load_file:
            new_trinode_skill, new_trinode_first = pickle.load(load_file)
        trinode_skill.extend(new_trinode_skill)
        trinode_first.extend(new_trinode_first)
        print(rf'Load {len(new_trinode_skill)} Nodestone from {load_file_path}')

    elif K == 'i':
        recognition_count = 0
        skill_name = []
        skill_indices = []
        top_skill_y = 9999
        top_skill_index = -1
        for i, skill_icon in enumerate(skill_img_list):
            cursor_position = pyautogui.position()
            scan_region = [cursor_position[0] - 10, cursor_position[1], 120, 240]
            pyautogui.screenshot('scan_region.png', region=scan_region)
            # pyautogui.locateCenterOnScreen doesn't support chinese file name!
            position = pyautogui.locateCenterOnScreen(skill_icon, region=scan_region, confidence=0.8)
            if position is not None:
                skill_indices.append(i)
                recognition_count += 1
                if position[1] < top_skill_y:
                    top_skill_y = position[1]
                    top_skill_index = i

        if recognition_count == 3:
            for skill_index in skill_indices:
                if skill_index == top_skill_index:
                    skill_name.append(f"【{skill_img_list[skill_index].split('/')[-1].split('.')[0]}】")
                else:
                    skill_name.append(skill_img_list[skill_index].split('/')[-1].split('.')[0])
            print(f"Nodestone {len(trinode_skill)} : {skill_name}")
            sound_effect(1)
            new_trinode_first = [0] * n_skill
            new_trinode_skill = [0] * n_skill
            for index in skill_indices:
                new_trinode_skill[index] = 1
            new_trinode_first[top_skill_index] = 1
            trinode_first.append(new_trinode_first)
            trinode_skill.append(new_trinode_skill)

        else:
            print("Unable to recognize Nodestone skill !")
            sound_effect(0)

    elif K == 'b':
        new_trinode_name_list, new_trinode_skill, new_trinode_first \
            = locate_25node_at_once(skill_icon_path_list=skill_img_list, page=page, n_trinode_inlist=len(trinode_skill))
        if len(new_trinode_skill) != 0:
            trinode_skill.extend(new_trinode_skill)
            trinode_first.extend(new_trinode_first)

            for trinode_name in new_trinode_name_list:
                print(trinode_name)
            page += 1
            sound_effect(1)
        else:
            sound_effect(0)
        print(rf'{len(new_trinode_skill)} Nodestone are detected.')

    elif K == 'g':
        cursor_position = pyautogui.position()
        scan_region = [cursor_position[0] - 10, cursor_position[1], 120, 240]
        n_skill_icon = get_skill_icon(my_job=my_job, skill_icon_page=skill_icon_page, scan_region=scan_region)
        if n_skill_icon != 0:
            update_skill_icon(my_job_path)
            skill_icon_page += 1
            sound_effect(1)
        else:
            sound_effect(0)
        print(rf'{n_skill_icon} skill icon are detected, saved at {my_job_path}.')
        print(rf'Please delete duplicate/unneeded skill icon manually, and then restart the program.')

    K = keyboard.read_key()

while True:
    print("==========Stage 3 : Choose your required skill==========")
    required_skill = []
    required_skill_name_list = askopenfilenames(filetypes=[('image files', '.png')], initialdir=my_job_path, parent=root)
    for required_skill_name in required_skill_name_list:
        required_skill.append(skill_img_list.index(required_skill_name))
    skill_name = []
    for skill_index in required_skill:
        skill_name.append(skill_img_list[skill_index].split('/')[-1].split('.')[0])
    print(f'Your required skill [{len(skill_name)}] : {skill_name}')

    print("==========Stage 4 : Finding ideal combination==========")
    n_trinode = len(trinode_skill)
    prob = pulp.LpProblem("trinode_combination", sense=pulp.LpMinimize)
    trinode_select_var = pulp.LpVariable.dicts('trinode_select', range(0, n_trinode), cat='Binary')
    prob += pulp.lpSum(trinode_select_var)  # objective function, 最小化選用的核心數
    for skill in required_skill:
        # 在所有選用的核心所強化的技能中，所有required_skill都需至少出現2次
        prob += pulp.lpSum(
            [trinode_select_var[trinode] * trinode_skill[trinode][skill] for trinode in range(n_trinode)]) >= 2
    for skill in range(n_skill):
        # 在所有選用的核心所強化的技能中，每個核心的第一個技能不能重複
        prob += pulp.lpSum(
            [trinode_select_var[trinode] * trinode_first[trinode][skill] for trinode in range(n_trinode)]) <= 1
    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    print("==========Result==========")
    print("Solve status:", pulp.LpStatus[prob.status])  # 輸出求解狀態

    if prob.status == pulp.LpStatusOptimal:
        print("Minimal number of Nodestone needed = ", int(pulp.value(prob.objective)))  # 輸出最優解的目標函數值
        if pulp.value(prob.objective) == len(skill_name) * 2 / 3.0:
            print("You got PERFECT Nodestone combination ! ")

        print("\nThe following Nodestones combination can meet your requirement with minimal number of Nodestone.")
        for v in prob.variables():
            # print(v.name, "=", v.varValue)  # 輸出每個變數的最優值
            if v.varValue == 1:
                trinode_index = int(v.name.split('_')[-1])
                skill_indices = [i for i, x in enumerate(trinode_skill[trinode_index]) if x == 1]
                skill_name = []
                for skill_index in skill_indices:
                    if trinode_first[trinode_index][skill_index] == 1:
                        skill_name.append(f"【{skill_img_list[skill_index].split('/')[-1].split('.')[0]}】")
                    else:
                        skill_name.append(skill_img_list[skill_index].split('/')[-1].split('.')[0])
                print(f'Nodestone {trinode_index} : {skill_name}')

    else:
        print("None of Nodestone combination can meet your requirement !")

    print("\nPress 'r' to retry Stage 3~4")
    print("Press 'q' to end this program")

    while True:
        K = keyboard.read_key()
        if K == 'r' or K == 'q':
            break
    if K == 'q':
        break

system("pause")
