import tkinter
from tkinter.messagebox import showinfo
import windnd

def drag(files):
    print(files)
    msg = '\n'.join((item.decode('gbk')for item in files))
    showinfo('wenjian',msg)

tk = tkinter.Tk()
windnd.hook_dropfiles(tk,func=drag)
tk.mainloop()
