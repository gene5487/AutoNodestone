from tkinter.filedialog import askopenfilename, askopenfilenames, askdirectory
from tkinter import Tk
import pyautogui
from os import listdir
from os.path import isfile
import keyboard
import pulp
from playsound import playsound
import pickle


def sound_effect(sound_type):
    if sound_type == 0:
        playsound(rf'./sound/Maplestory-012.wav', block=False)
    elif sound_type == 1:
        playsound(rf'./sound/Maplestory-010.wav', block=False)


print("==========Stage 1 : Select your job==========")
root = Tk()
root.withdraw()
root.wm_attributes('-topmost', 1)
my_job_path = askdirectory(title='Select your job', initialdir=r'./skill_icon', parent=root)
skill_img_list = [rf"{my_job_path}/{img_name}" for img_name in listdir(my_job_path) if isfile(rf"{my_job_path}/{img_name}")]
print(skill_img_list)
print(f'You are {my_job_path.split("/")[-1]}')
n_skill = len(skill_img_list)
n_trinode = 0
trinode_skill = []
trinode_first = []
required_skill = []


print("==========Stage 2 : Input your Nodestone==========")
print("Put cursor on the Nodestone to show the 3 skill icon, let program scan through all Nodestone you have")
print("Press 'i' to scan the Nodestone currently on screen")
print("Press 's' to save scanned Nodestone to file")
print("Press 'l' to load scanned Nodestone from file")
print("Press 'e' to end this stage")
K = keyboard.read_key()
while K != 'e':
    if K == 's':
        with open(rf'./save/{my_job_path.split("/")[-1]}.pkl', 'wb') as save_file:
            pickle.dump([trinode_skill, trinode_first], save_file)
        print(rf'Save {n_trinode} Nodestone to ./save/{my_job_path.split("/")[-1]}.pkl')

    elif K == 'l':
        load_file_path = askopenfilename(filetypes=[('save file', '.pkl')], initialdir=r'./save')
        with open(load_file_path, 'rb') as load_file:
            new_trinode_skill, new_trinode_first = pickle.load(load_file)
        trinode_skill.extend(new_trinode_skill)
        trinode_first.extend(new_trinode_first)
        n_trinode += len(new_trinode_skill)
        print(rf'Load {len(new_trinode_skill)} Nodestone from {load_file_path}')

    elif K == 'i':
        recognition_count = 0
        skill_name = []
        skill_indices = []
        top_skill_y = 9999
        top_skill_index = -1
        for i, skill_icon in enumerate(skill_img_list):
            cursor_position = pyautogui.position()
            scan_region = [cursor_position[0]-10, cursor_position[1], 120, 210]
            pyautogui.screenshot('scan_region.png', region=scan_region)
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
            print(f"Trinode {n_trinode} : {skill_name}")
            sound_effect(1)
            new_trinode_first = [0] * n_skill
            new_trinode_skill = [0] * n_skill
            for index in skill_indices:
                new_trinode_skill[index] = 1
            new_trinode_first[top_skill_index] = 1
            trinode_first.append(new_trinode_first)
            trinode_skill.append(new_trinode_skill)
            # print(trinode_skill)
            # print(trinode_first)

            n_trinode += 1

        else:
            print("Unable to recognize Nodestone skill !")
            sound_effect(0)

    # print(trinode_skill)
    K = keyboard.read_key()


print("==========Stage 3 : Choose your required skill==========")
required_skill_name_list = askopenfilenames(filetypes=[('image files', '.png')], initialdir=my_job_path, parent=root)
for required_skill_name in required_skill_name_list:
    required_skill.append(skill_img_list.index(required_skill_name))
skill_name = []
for skill_index in required_skill:
    skill_name.append(skill_img_list[skill_index].split('/')[-1].split('.')[0])
print(f'Your required skill [{len(skill_name)}] : {skill_name}')


print("==========Stage 4 : Finding ideal combination==========")
prob = pulp.LpProblem("trinode_combination", sense=pulp.LpMinimize)
trinode_select_var = pulp.LpVariable.dicts('trinode_select', range(0, n_trinode), cat='Binary')
prob += pulp.lpSum(trinode_select_var)  # objective function, 最小化選用的核心數
for skill in required_skill:
    # 在所有選用的核心所強化的技能中，所有required_skill都需至少出現2次
    prob += pulp.lpSum([trinode_select_var[trinode]*trinode_skill[trinode][skill] for trinode in range(n_trinode)]) >= 2
for skill in range(n_skill):
    # 在所有選用的核心所強化的技能中，每個核心的第一個技能不能重複
    prob += pulp.lpSum([trinode_select_var[trinode]*trinode_first[trinode][skill] for trinode in range(n_trinode)]) <= 1
prob.solve()


print("==========Result==========")
print("Status:", pulp.LpStatus[prob.status])  # 輸出求解狀態


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

print("Minimal value of objective function (i.e. #Nodestone needed)= ", pulp.value(prob.objective))  # 輸出最優解的目標函數值
123