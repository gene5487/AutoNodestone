# AutoNodestone
Python program for MapleStory that help palyer find ideal combination of [Nodestones](https://maplestory.nexon.net/micro-site/59387).

- Uses [PyAutoGUI](https://pypi.org/project/PyAutoGUI/) to automatic identify Nodestone Skills.
- Formulates the combination problem as an [Zero-one integer linear programming(0-1 ILP)](https://en.wikipedia.org/wiki/Integer_programming#Variants) problem.
- Uses [PuLP](https://pypi.org/project/PuLP/) to solve the 0-1 ILP problem.
- Uses [PyQt5](https://pypi.org/project/PyQt5/) to build user interface.
- Uses [PyInstaller](https://pypi.org/project/pyinstaller/) to create .exe file.


## ✅Features
- Nodestone Skills identification is based on [Template Matching](https://docs.opencv.org/4.x/d4/dc6/tutorial_py_template_matching.html), \
which theoretically **supports all languages** (as long as all Maplestory server share same skill icon).
- Batch scan all the 11 Nodestones on V-martix UI at once without any manual input.
- Intuitive and convenience UI. (See [Usage](https://github.com/gene5487/AutoNodestone/blob/master/README.md#usage))


## 🔨Setup 

>🙌Note :\
>For user's convenience, a executable (**AutoNodestone_PyQt_start.exe**) is provided.\
>You can execute the program without setting-up Python envierment.

1. Download and install Python3.
2. Download and unzip whole AutoNodestone folder.
3. Inside your AutoNodestone directory, open a command prompt and run : 
```
pip install -r requirements.txt
```


## 🕹Usage
1. 🛠 Set up your MapleStory resolution \
Make sure your MapleStory resolution is set to `1280x720` in windowed mode.
Otherwise, image recognition will not work properly.

2. 🚀 Launch the AutoNodestone GUI \
Inside your AutoNodestone directory, open a command prompt and run : 
```
python AutoNodestone_PyQt_start.py
```
OR\
Just doble click **AutoNodestone_PyQt_start.exe**

<br/>

3. 🎯 Follow the on-screen instructions

 I. Select the job of your charater.

https://user-images.githubusercontent.com/58682521/190847875-cbe0f91c-385f-4805-84c9-2eff2a624af4.mp4

<br/>
<br/>

 II. *(Optional)* If yod find that the skill icons doesn't match the skill icons in-game :
  - Open the skill icon directory by clicking `Open directory` and delete those unneeded icons.
  - Generate skill icons from game by clicking `Generate skill icon`, the program will detect skill icons your screen and save to skill icon directory.

https://user-images.githubusercontent.com/58682521/190847883-f9d4871d-e10c-4321-a053-e35adc6042b1.mp4

<br/>
<br/>

 III. Scan Nodestones by clicking `Scan Nodestones` button.

https://user-images.githubusercontent.com/58682521/190847892-e79339c5-fca3-4f98-a58a-4be6c7ab9983.mp4

<br/>
<br/>

 IV. Select your required skills in  `Skill selection` area, and get combination by clicking `Get combination`.

https://user-images.githubusercontent.com/58682521/190847901-8cc73b60-ec3b-4a0a-bdf2-2ae647388372.mp4

<br/>
<br/>


 V. Equip the Nodestones in the combination.

[123](https://user-images.githubusercontent.com/58682521/190847908-64d81bcb-2711-4c6f-a9b6-28dcff94595c.mp4)

<br/>
<br/>

## 🤔How program evaluate combination?
A *valid combination* must not violate the rules :

1. Nodes with the same main skills(skill that appear on first row) can not appear more than once.
2. Each required skills(selected by user) must appear at least twice.

**Program will find 3 different *valid combinations* with minimal number of Nodes.**
<br/>
<br/>

Because Nodes with the same main skill can be stacked and enhanced, if there are several *valid combinations* with same number of Nodes,\
**the combination with higher stack count will has higer priority**.

![stack count and priority example](https://user-images.githubusercontent.com/58682521/192094914-6e8d4ffd-91e3-4b6d-985a-9f5c0eec181c.PNG)



## 📃Further information
Please refer to https://forum.gamer.com.tw/Co.php?bsn=07650&sn=6415998. (Written in Traditional Chinese)



## ❤Special thanks
- Source of skill icon image : [NodestoneBuilder repository](https://github.com/PhantasmicSky/NodestoneBuilder)
- Thank my classmates in NTUST for disscusing how to formulate the problem with me.
- Thank Prof. S.-Y. Fang. I learned ILP and some useful programing skills in the EDA course.
- Thank 星星(peggy7992) gave me helpful advise, which help me come up with batch identify method.
- Thank 煎熬(dcda5460170) gave me helpful advise, which give me the idea of `Generate skill` function and UI.
