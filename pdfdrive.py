import tkinter.filedialog
import customtkinter
import os
import tkinter
import requests
import re
import time
import multiprocessing
import threading

class ScrollableLabelButtonFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1, minsize=500)
        # self.thread_list = []
        self.label_list = []
        self.button_list = []
        self.remove_list = []
        self.query = []

    def add_item(self, item,query):
        label = customtkinter.CTkLabel(self, text=item, compound="left", padx=5, anchor="w", wraplength=500)
        button = customtkinter.CTkButton(self, text="Tải xuống", command=lambda: self.download_file(query), width=80, height=24)
        remove_btn = customtkinter.CTkButton(self,text="Xóa",command=lambda: self.remove_item(item), width=40, height=24)
        # if self.command is not None:
        #     button.configure(command=lambda: self.command(query))
        label.grid(row=len(self.label_list), column=0, pady=(0, 10), sticky="w")
        button.grid(row=len(self.button_list), column=2, pady=(0, 10), padx=5)
        remove_btn.grid(row=len(self.remove_list), column=1, pady=(0, 10), padx=5)
        self.label_list.append(label)
        self.button_list.append(button)
        self.query.append(query)
        self.remove_list.append(remove_btn)

    def remove_item(self, item):
        for label, button, remove_button, query in zip(self.label_list, self.button_list, self.remove_list, self.query):
            if item == label.cget("text"):
                label.destroy()
                button.destroy()
                remove_button.destroy()
                self.label_list.remove(label)
                self.button_list.remove(button)
                self.remove_list.remove(remove_button)
                self.query.remove(query)
                return
            
    def remove_all(self):
        for label, button, remove_button in zip(self.label_list, self.button_list, self.remove_list):
            label.destroy()
            button.destroy()
            remove_button.destroy() 
        
        self.label_list.clear()
        self.button_list.clear()
        self.remove_list.clear()
        self.query.clear()
        return
    def on_error(self, path_query):
        for button, query in zip(self.button_list, self.query):
            if path_query == query:
                button.configure(text="Lỗi tải xuống", fg_color="red")
                return
    def on_missing(self, path_query):
        for button, query in zip(self.button_list, self.query):
            if path_query == query:
                button.configure(text="File lỗi", fg_color="red")
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
    def on_check(self, path_query):
        for button, query in zip(self.button_list, self.query):
            if path_query == query:
                if button.cget('text') == "Đã tải xong":
                    return True
                
    def download_file(self,path_query=None):
        # url = link.get()
        # result_str.configure(text=url)
        # print(url)
        if(path_query == None):
            return
        if (self.on_check(path_query)):
            return
        
        self.on_downloading(path_query)
        download_path = link_path.cget('text')

        try:
            response = requests.get("https://www.pdfdrive.com" + path_query)
            # Check if the request was successful
            if response.status_code == 200:
                content = response.text
                pattern = re.compile(r'/ebook/preview.*?"', re.IGNORECASE) 
                matches = pattern.findall(content)
                if matches == []:
                    self.on_error(path_query)
                    return
                matches = matches[0][15:-1].split('&')
                param_id = matches[0].split('=')[1]
                param_session = matches[1].split('=')[1]
                # print(matches)
                # print(param_id)
                # print(param_session)
                full_url_download = "https://www.pdfdrive.com/download.pdf?id=" + param_id + "&h=" + param_session +"&u=cache&ext=pdf"
                thread_download = threading.Thread(target=download_singe_file, args=(download_path,full_url_download,path_query))
                # self.thread_list.append(thread_download)
                thread_download.start()
                # try:
                    # wget.download(url=full_url_download, out=link_path.cget('text'))
                    # local_filename = os.path.join(download_path, full_url_download.split('/')[-1])
                    # with requests.get(full_url_download, stream=True) as r:
                    #     r.raise_for_status()
                    #     with open(local_filename, 'wb') as f:
                    #         for chunk in r.iter_content(chunk_size=8192):
                    #             if chunk:  # filter out keep-alive new chunks
                    #                 f.write(chunk)
                    # print(f"Downloaded: {local_filename}")
                    
                #     self.on_success(path_query)
                # except Exception as e:
                #     print(e)
                #     self.on_error(path_query)
                # print(f"File downloaded and saved as {file_name}")
                
            else:
                print(f'Failed to download file: {response.status_code}')
        except Exception as e:
            print(e)
            self.on_error(path_query)
       
def download_singe_file(download_path,full_url_download, path_query):
    try:
        trim_path = path_query.split('.')[0][1:] + '.pdf'
        # print(trim_path)
        local_filename = download_path + '\\' + trim_path
        with requests.get(full_url_download, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
        if os.path.getsize(local_filename) == 14:
            scrollable_label_button_frame.on_missing(path_query)

        else:
            scrollable_label_button_frame.on_success(path_query)
    except Exception as e:
        print("Error Download Single File: ", e)
        scrollable_label_button_frame.on_error(path_query)

def set_download_path():
    # Open the file dialog for selecting a directory
    selected_directory = tkinter.filedialog.askdirectory()
    list_path = selected_directory.split("/")
    path_dir = '\\'.join(list_path)
    link_path.configure(text=path_dir)
    print(link_path.cget('text'))

def unique_items(input_list):
    seen = set()
    return [x for x in input_list if x not in seen and not seen.add(x)]

def Load_file_wrapper():
    thread = threading.Thread(target=Load_file)
    if thread.is_alive:
        thread.run()
    else:
        thread.start()

def Load_file():
    result_str.configure(text="Sách are loading", text_color="blue")
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
                # time.sleep(2)
                # print(path_query)
                result_str.configure(text="Đã load thành công", text_color="green")
        else:
            result_str.configure(text="website lỗi", text_color="red")
            scrollable_label_button_frame.remove_all()
    except:
        result_str.configure(text="Đường dẫn lỗi", text_color="red")
        scrollable_label_button_frame.remove_all()
            # print("fail")

def download_file_all():
    """Download multiple files in parallel."""
    # os.makedirs(download_path, exist_ok=True)
    # Create a pool of processes
    # list_thread = []
    # thread = None
    for query in scrollable_label_button_frame.query:
        scrollable_label_button_frame.download_file(query)
        # thread = scrollable_label_button_frame.download_file(query)
        # list_thread.append(thread)
    # for every_thread in list_thread:
        # every_thread.join()    
    # with multiprocessing.Pool() as pool:
    #     # Map the download_file function to the URL list
    #     pool.starmap(scrollable_label_button_frame.download_file, [query for query in scrollable_label_button_frame.query])
    # for query in scrollable_label_button_frame.query:
    #     download_file(query)
        # print(query)
    # pass

def remove_all_wrapper():
    scrollable_label_button_frame.remove_all()
# =========================== Setting / Configuration ==========================
#System setting
customtkinter.set_appearance_mode("light")
customtkinter.set_default_color_theme("dark-blue")

#Our app frame
app = customtkinter.CTk()
app.geometry("1024x768")
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

#Create frame to display button download all and remove all
frame_all = customtkinter.CTkFrame(app, fg_color='transparent')
frame_all.pack(side="top", fill='both', expand=False, padx=10, pady=10)

download_all = customtkinter.CTkButton(frame_all, text="Tải tất cả", command=download_file_all, font=font, width=80)
download_all.pack(side='right', padx=10, pady=5, anchor="e")

remove_all = customtkinter.CTkButton(frame_all, text="Xóa tất cả", command=remove_all_wrapper, font=font, hover_color='red', fg_color='dark red', text_color='white', width=80)
remove_all.pack(side='right', padx=10, pady=5, anchor="e")

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

load_file = customtkinter.CTkButton(frame_input_url, text="Load", command=Load_file_wrapper, font=font)
# download.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)
load_file.pack(pady=10)

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

scrollable_label_button_frame = ScrollableLabelButtonFrame(frame_download, width=600, corner_radius=0)
scrollable_label_button_frame.pack(side='top', fill='both', expand=True)
# for i in range(20):  # add items with images
#     scrollable_label_button_frame.add_item(f"image and item {i}")

# ================================================================================
#Run app
app.mainloop()
#https://www.pdfdrive.com/search?q=philosophy&pagecount=&pubyear=&searchin=&page=11
