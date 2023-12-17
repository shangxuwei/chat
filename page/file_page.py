import tkinter as tk
from tkinter import ttk
import tkinter.messagebox

class FileGui(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("下载文件")  # 窗口名
        self.geometry('640x540+10+10')
        tableColumns = ['文件名','发送者','MD5']
        xscroll = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        xscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.table = ttk.Treeview(
            master=self,  # 父容器
            columns=tableColumns,  # 列标识符列表
            height=30,  # 表格显示的行数
            show='headings',  # 隐藏首列
            xscrollcommand=xscroll.set,  # x轴滚动条
        )
        xscroll.config(command=self.table.xview)


        self.table.heading(column="文件名", text="文件名", anchor=tk.W)
        self.table.heading(column='发送者', text='发送者', anchor=tk.W, )  # 定义表头
        self.table.heading(column='MD5', text='MD5', anchor=tk.W,)  # 定义表头

        self.table.pack(expand=1,fill=tk.BOTH)

    @staticmethod
    def download_confirm(file,md5):
        res = tkinter.messagebox.askokcancel('文件下载',f'是否下载文件{file}\nmd5:{md5}')
        return res
