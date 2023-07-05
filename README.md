# simple-line-counter

A simple line counter that takes a directory or file as arg (or no arg for current directory) and gives a rough estimate of code, comments, mixed and blank lines. It's a rough estimate because it doesn't check whether a comment string is inside an actual string. For example, '#' will transform a line into mixed.
```
python main.py location
```