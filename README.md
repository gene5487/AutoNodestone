# AutoNodestone
Python program for MapleStory that help palyer find ideal combination of Nodestones.

- Uses [PyAutoGUI](https://pypi.org/project/PyAutoGUI/) to automatic identify Nodestone Skills.  
- Formulates the combination problem as an [integer linear programming (ILP)](https://en.wikipedia.org/wiki/Linear_programming) problem .
- Uses [PuLP](https://pypi.org/project/PuLP/) to solve ILP problem.



## 🔨Setup 
1. Download and install Python3.
2. Download and unzip AutoNodestone.
3. Inside your AutoNodestone directory, open a command prompt and run : 
```
pip install -r requirements.txt
```
>🙌Note :\
>For user's convenience, a standalone standalone executable (**AutoNodestone.exe**) is provided.\
>You can execute the program without setup envierment.\
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
>You may click desktop or other window to let MapleStroy lose focus, so that you can input to the program.

 
 
## 👀Demonstration
I have 10 Nodestones, \
I want to fully level 'Dragon Vein Absorption', 'Dragon Vein Eruption', 'Essence Sprinkle' using minimal slots.

![image](https://github.com/gene5487/AutoNodestone/blob/master/demonstration.gif)



## ❤Specil thnaks
- Source of skill icon image : [NodestoneBuilder repository](https://github.com/PhantasmicSky/NodestoneBuilder)
- Thank my classmates in NTUST for disscusing how to formulate the problem with me.
- Thank Prof. S.-Y. Fang. I learned ILP and some useful programing skills in the EDA course.
