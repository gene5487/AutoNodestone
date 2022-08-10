# AutoNodestone
Python program for MapleStory that help palyer find ideal combination of [Nodestones](https://maplestory.nexon.net/micro-site/59387).

- Uses [PyAutoGUI](https://pypi.org/project/PyAutoGUI/) to automatic identify Nodestone Skills.
- Formulates the combination problem as an [Zero-one integer linear programming(0-1 ILP)](https://en.wikipedia.org/wiki/Integer_programming#Variants) problem.
- Uses [PuLP](https://pypi.org/project/PuLP/) to solve the 0-1 ILP problem.

## ✅Features
- Nodestone Skills identification is based on [Template Matching](https://docs.opencv.org/4.x/d4/dc6/tutorial_py_template_matching.html), \
which theoretically **supports all languages** (as long as all Maplestory server share same skill icon).
- Batch scan all the 25 Nodestones on V-martix UI at once.
- Generates screenshot with number label on each identified Nodestone, \
it helps user easily find out which Nodestone is in thier ideal combination. (See [Another demonstration](#another-demonstration))

## 🔨Setup 
1. Download and install Python3.
2. Download and unzip AutoNodestone.
3. Inside your AutoNodestone directory, open a command prompt and run : 
```
pip install -r requirements.txt
```
>🙌Note :\
>For user's convenience, a standalone standalone executable (**AutoNodestone.exe**) is provided.\
>You can execute the program without setting-up envierment.\
>This .exe file is created from python script (**AutoNodestone.py**) using [PyInstaller](https://pypi.org/project/pyinstaller/).



## 🕹Usage
Inside your AutoNodestone directory, open a command prompt and run : 
```
python AutoNodestone.py
```
OR\
Just doble click **AutoNodestone.exe**

>❗Note :\
>**Program can't read keyboard input when MapleStroy window is focused (i.e. when the last window you click in is MapleStroy).**\
>You may click desktop or other window to let MapleStroy lose focus, so that you can input to the program.\
>OR\
>Run CMD or **AutoNodestone.exe** as administrator should solve this problem.

 
 
## 👀Demonstration
I have 10 Nodestones, \
I want to fully level 'Dragon Vein Absorption', 'Dragon Vein Eruption', 'Essence Sprinkle' using minimal slots.\
\
<img src="https://github.com/gene5487/AutoNodestone/blob/master/demonstration.gif" width="800">



## 👀Another demonstration 
Batch scan & screenshot feature is shown.\
\
<img src="https://github.com/gene5487/AutoNodestone/blob/master/demonstration_batchscan.gif" width="800">




## 📃Further information
Please refer to https://forum.gamer.com.tw/Co.php?bsn=07650&sn=6415998. (Written in Traditional Chinese)



## ❤Special thanks
- Source of skill icon image : [NodestoneBuilder repository](https://github.com/PhantasmicSky/NodestoneBuilder)
- Thank my classmates in NTUST for disscusing how to formulate the problem with me.
- Thank Prof. S.-Y. Fang. I learned ILP and some useful programing skills in the EDA course.
- Thank 星星(peggy7992) gave me helpful advise, which help me come up with batch identify method.
