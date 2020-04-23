# Tetris
A python 3.6 implementation of Tetris using tkinter

--FEATURES--
- Tracks your score and levels up for every 10 lines cleared
- Keeps track of your highscore in the session
- Speeds up the pieces based on your level
- Shows a preview of the next piece that will spawn in
- Hover feature allows you some extra time to move the piece around before it settles on high speeds (Default: On)
- Easyspin holds the piece in place while spinning (Default: Off)
- Kick feature allows the player to rotate pieces where there normally is not enough space by 'kicking' the piece away from the wall
- This implementation is accompanied by some sick tunes and sound effects!
- Shows toggleable guidelines for easier piece placement
- Pause the game whenever you need to take a break, and resume where you left off
- Select pieces completely random or pick from a bag of 7 without replacement

--FLAGS--
debug: Play with debug mode, which will print the board on the console after each move
random: The default mode picks pieces out of a bag of 7 without replacement, the random mode is truly random and a bit harder
nohover: Disable the hover feature
spin: Enable the easy spin feature, which holds the piece in place when rotating