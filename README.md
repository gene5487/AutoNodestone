# AutoNodestone
Python program for MapleStory that help palyer find ideal combination of [Nodestones](https://maplestory.nexon.net/micro-site/59387).

- Uses [PyAutoGUI](https://pypi.org/project/PyAutoGUI/) to automatic identify Nodestone Skills.
- Formulates the combination problem as an [Zero-one integer linear programming(0-1 ILP)](https://en.wikipedia.org/wiki/Integer_programming#Variants) problem.
- Uses [PuLP](https://pypi.org/project/PuLP/) to solve the 0-1 ILP problem.
- Uses [PyQt5](https://pypi.org/project/PyQt5/) as user interface.


## ✅Features
- Nodestone Skills identification is based on [Template Matching](https://docs.opencv.org/4.x/d4/dc6/tutorial_py_template_matching.html), \
which theoretically **supports all languages** (as long as all Maplestory server share same skill icon).
- Batch scan all the 11 Nodestones on V-martix UI at once without any manual input.
- Intuitive and convenience UI. (See [Usage](usage))


## 🔨Setup 
1. Download and install Python3.
2. Download and unzip AutoNodestone.
3. Inside your AutoNodestone directory, open a command prompt and run : 
```
pip install -r requirements.txt
```
>🙌Note :\
>For user's convenience, a standalone standalone executable (**AutoNodestone_PyQt_start.exe**) is provided.\
>You can execute the program without setting-up envierment.\
>This .exe file is created from python script (**AutoNodestone_PyQt_start.py**) using [PyInstaller](https://pypi.org/project/pyinstaller/).


## 🕹Usage
Inside your AutoNodestone directory, open a command prompt and run : 
```
python AutoNodestone_PyQt_start.py
```
OR\
Just doble click **AutoNodestone_PyQt_start.exe**
<br/>

<br/>
And then follow the instruction below :

 1. Select the job of your charater.

https://user-images.githubusercontent.com/58682521/190847875-cbe0f91c-385f-4805-84c9-2eff2a624af4.mp4

<br/>
<br/>

 2. *(Optional)* If yod find that the skill icons doesn't match the skill icons in-game :
  - Open the skill icon directory by clicking `Open directory` and delete those unneeded icons.
  - Generate skill icons from game by clicking `Generate skill icon`, the program will detect skill icons your screen and save to skill icon directory.

https://user-images.githubusercontent.com/58682521/190847883-f9d4871d-e10c-4321-a053-e35adc6042b1.mp4

<br/>
<br/>

 3. Scan Nodestones by clicking `Scan Nodestones` button.

https://user-images.githubusercontent.com/58682521/190847892-e79339c5-fca3-4f98-a58a-4be6c7ab9983.mp4

<br/>
<br/>

 4. Select your required skills in  `Skill selection` area.\ and get combination by clicking `Get combination`.

https://user-images.githubusercontent.com/58682521/190847901-8cc73b60-ec3b-4a0a-bdf2-2ae647388372.mp4

<br/>
<br/>


 5. Equip the Nodestones in the combination.

https://user-images.githubusercontent.com/58682521/190847908-64d81bcb-2711-4c6f-a9b6-28dcff94595c.mp4

<br/>
<br/>

## 📃Further information
Please refer to https://forum.gamer.com.tw/Co.php?bsn=07650&sn=6415998. (Written in Traditional Chinese)



## ❤Special thanks
- Source of skill icon image : [NodestoneBuilder repository](https://github.com/PhantasmicSky/NodestoneBuilder)
- Thank my classmates in NTUST for disscusing how to formulate the problem with me.
- Thank Prof. S.-Y. Fang. I learned ILP and some useful programing skills in the EDA course.
- Thank 星星(peggy7992) gave me helpful advise, which help me come up with batch identify method.
- Thank 煎熬(dcda5460170) gave me helpful advise, which give me the idea of `Generate skill` function and UI.
