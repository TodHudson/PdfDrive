import tkinter.filedialog
import customtkinter
import os
import tkinter
import requests
import re
import wget

class ScrollableLabelButtonFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1, minsize=500)
        self.command = command
        self.label_list = []
        self.button_list = []
        self.remove_list = []
        self.query = []

    def add_item(self, item,query):
        label = customtkinter.CTkLabel(self, text=item, compound="left", padx=5, anchor="w", wraplength=500)
        button = customtkinter.CTkButton(self, text="Tải xuống", width=80, height=24)
        remove_btn = customtkinter.CTkButton(self,text="Xóa",command=lambda: self.remove_item(self,item), width=40, height=24)
        if self.command is not None:
            button.configure(command=lambda: self.command(query))
        label.grid(row=len(self.label_list), column=0, pady=(0, 10), sticky="w")
        button.grid(row=len(self.button_list), column=2, pady=(0, 10), padx=5)
        remove_btn.grid(row=len(self.remove_list), column=1, pady=(0, 10), padx=5)
        self.label_list.append(label)
        self.button_list.append(button)
        self.query.append(query)
        self.remove_list.append(remove_btn)

    def remove_item(self, item):
        for label, button in zip(self.label_list, self.button_list):
            if item == label.cget("text"):
                label.destroy()
                button.destroy()
                self.label_list.remove(label)
                self.button_list.remove(button)
                return
            
    def remove_all(self):
        for label, button in zip(self.label_list, self.button_list):
            label.destroy()
            button.destroy()
            self.label_list.remove(label)
            self.button_list.remove(button)
        return
    def on_error(self, path_query):
        for button, query in zip(self.button_list, self.query):
            if path_query == query:
                button.configure(text="Lỗi tải xuống", fg_color="red")
                return
            
    def on_success(self, path_query):
        for button, query in zip(self.button_list, self.query):
            if path_query == query:
                button.configure(text="Đã tải xong", fg_color="green")
                return
    def on_downloading(self, path_query):
        for button, query in zip(self.button_list, self.query):
            if path_query == query:
                button.configure(text="Đang tải xuống")
                return
            
def set_download_path():
    # Open the file dialog for selecting a directory
    selected_directory = tkinter.filedialog.askdirectory()
    link_path.configure(text=selected_directory)

def unique_items(input_list):
    seen = set()
    return [x for x in input_list if x not in seen and not seen.add(x)]

def Load_file():
    url = link.get()
    try:
        response = requests.get(url)
        if response.status_code == 200:
            content = response.text
            pattern = re.compile(r'href.*?-e.*?\.html', re.IGNORECASE)
            find_path_file = pattern.findall(content)
            list_path_file = unique_items(find_path_file)

            for path_file in list_path_file:
                path_query = path_file[6:]
                list_name = path_query.split('-')[:-1]
                list_name[0] = list_name[0][1:]
                name_of_book = ' '.join(list_name)
                scrollable_label_button_frame.add_item(name_of_book, path_query)
                # print(path_query)
        else:
            result_str.configure(text="website lỗi", text_color="red")
            scrollable_label_button_frame.remove_all()
    except:
        result_str.configure(text="Đường dẫn lỗi", text_color="red")
        scrollable_label_button_frame.remove_all()
            # print("fail")

def download_file(path_query=None):
    # url = link.get()
    # result_str.configure(text=url)
    # print(url)
    scrollable_label_button_frame.on_downloading(path_query)
    try:
        response = requests.get("https://www.pdfdrive.com" + path_query)
        # Check if the request was successful
        if response.status_code == 200:
            content = response.text
            pattern = re.compile(r'/ebook/preview.*?"', re.IGNORECASE) 
            matches = pattern.findall(content)
            # print(matches)
            matches = matches[0][15:-1].split('&')
            param_id = matches[0].split('=')[1]
            param_session = matches[1].split('=')[1]
            # print(matches)
            # print(param_id)
            # print(param_session)
            full_url_download = "https://www.pdfdrive.com/download.pdf?id=" + param_id + "&h=" + param_session +"&u=cache&ext=pdf"
            
            try:
                wget.download(url=full_url_download, out=link_path.cget('text'))
                scrollable_label_button_frame.on_success(path_query)
            except:
                scrollable_label_button_frame.on_error(path_query)
            # print(f"File downloaded and saved as {file_name}")
            
        else:
            print(f'Failed to download file: {response.status_code}')
    except:
        scrollable_label_button_frame.on_error(path_query)


def download_file_all():
    for query in scrollable_label_button_frame.query:
        download_file(query)
        # print(query)
    # pass
# =========================== Setting / Configuration ==========================
#System setting
customtkinter.set_appearance_mode("light")
customtkinter.set_default_color_theme("dark-blue")

#Our app frame
app = customtkinter.CTk()
# app.geometry("720x480")
app.title("PDFDrive Downloader")
app.resizable(width=True, height=True)
# app.grid_rowconfigure(0, weight=1)
# app.grid_columnconfigure(0, weight=1,minsize=600)
#Setup font
font = customtkinter.CTkFont(family="K2D", size=14)

# =================================================================================
# ======================================= UI Design ==========================================

#Create frame/container
frame_input = customtkinter.CTkFrame(app,fg_color='dark gray')
frame_input.pack(side="top", fill="both", expand=False, padx=10, pady=10)

download_all = customtkinter.CTkButton(app, text="Tải tất cả", command=download_file_all, font=font, width=80)
download_all.pack(padx=10, pady=5, anchor="e")

frame_download = customtkinter.CTkFrame(app, fg_color='light gray')
frame_download.pack(side="top", fill='both', expand=True, padx=10, pady=10)

frame_input_url = customtkinter.CTkFrame(frame_input, fg_color='white')
frame_input_url.place(x=0,y=0)
frame_input_url.pack(side="left", fill='both', expand=True, padx=10, pady=10)

frame_input_path = customtkinter.CTkFrame(frame_input, fg_color='white', width=80)
frame_input_path.place(x=400,y=0)
frame_input_path.pack(side="right", fill='both', expand=True, padx=10, pady=10)

#Adding UI Element
title = customtkinter.CTkLabel(frame_input_url, text="Nhập link search")
title.pack(padx=10, pady=10)

url_var = tkinter.StringVar()
link = customtkinter.CTkEntry(frame_input_url, width=400, height=40, textvariable=url_var)
link.pack()

result_str = customtkinter.CTkLabel(frame_input_url, text="")
result_str.pack()

download = customtkinter.CTkButton(frame_input_url, text="Load", command=Load_file, font=font)
# download.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)
download.pack(pady=10)

title_path = customtkinter.CTkLabel(frame_input_path, text="Đường dẫn tải xuống")
title_path.pack(padx=10, pady=10)

# Lấy đường dẫn thư mục người dùng hiện tại
user_profile = os.environ['USERPROFILE']
# Kết hợp với thư mục "Downloads"
downloads_folder = os.path.join(user_profile, 'Downloads')
link_path = customtkinter.CTkLabel(frame_input_path, text=downloads_folder)
link_path.pack(padx=5)

browser = customtkinter.CTkButton(frame_input_path, text="Browser", command=set_download_path, font=font)
browser.pack(pady=5)

result_path = customtkinter.CTkLabel(frame_input_path, text="")
result_path.pack()

scrollable_label_button_frame = ScrollableLabelButtonFrame(frame_download, width=600, command=download_file, corner_radius=0)
scrollable_label_button_frame.pack(side='top', fill='both', expand=True)
# for i in range(20):  # add items with images
#     scrollable_label_button_frame.add_item(f"image and item {i}")

# ================================================================================
#Run app
app.mainloop()