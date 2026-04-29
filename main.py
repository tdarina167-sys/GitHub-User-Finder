import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import webbrowser
from datetime import datetime
import urllib.request
import urllib.error

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Путь к файлу с избранными
        self.favorites_file = "favorites.json"
        self.favorites = self.load_favorites()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Загрузка избранных при старте
        self.display_favorites()
    
    def create_widgets(self):
        """Создание всех виджетов интерфейса"""
        # Главный контейнер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка grid весов для масштабирования
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Заголовок
        title_label = ttk.Label(
            main_frame, 
            text="GitHub User Finder", 
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Фрейм для поиска
        search_frame = ttk.Frame(main_frame)
        search_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(0, weight=1)
        
        # Поле ввода
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(
            search_frame, 
            textvariable=self.search_var,
            font=('Arial', 11)
        )
        self.search_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        self.search_entry.bind('<Return>', lambda e: self.search_users())
        
        # Кнопка поиска
        search_button = ttk.Button(
            search_frame,
            text="Поиск",
            command=self.search_users
        )
        search_button.grid(row=0, column=1, padx=(0, 5))
        
        # Кнопка очистки
        clear_button = ttk.Button(
            search_frame,
            text="Очистить",
            command=self.clear_search
        )
        clear_button.grid(row=0, column=2)
        
        # Ноутбук для вкладок
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Вкладка результатов поиска
        self.search_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.search_frame, text="Результаты поиска")
        
        # Вкладка избранных
        self.favorites_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.favorites_frame, text="Избранное")
        
        # Настройка вкладок
        self.setup_search_tab()
        self.setup_favorites_tab()
        
        # Статус бар
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        status_bar = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=('Arial', 9)
        )
        status_bar.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def setup_search_tab(self):
        """Настройка вкладки поиска"""
        self.search_frame.columnconfigure(0, weight=1)
        self.search_frame.rowconfigure(0, weight=1)
        
        # Создаем фрейм для списка и скроллбаров
        list_frame = ttk.Frame(self.search_frame)
        list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Treeview для результатов поиска
        columns = ('username', 'profile_url')
        self.search_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            selectmode='browse'
        )
        
        # Определяем заголовки
        self.search_tree.heading('username', text='Имя пользователя')
        self.search_tree.heading('profile_url', text='URL профиля')
        
        # Определяем ширину колонок
        self.search_tree.column('username', width=200)
        self.search_tree.column('profile_url', width=400)
        
        # Добавляем скроллбары
        scrollbar_y = ttk.Scrollbar(
            list_frame,
            orient=tk.VERTICAL,
            command=self.search_tree.yview
        )
        scrollbar_x = ttk.Scrollbar(
            list_frame,
            orient=tk.HORIZONTAL,
            command=self.search_tree.xview
        )
        self.search_tree.configure(
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )
        
        # Размещаем элементы
        self.search_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Кнопки под списком
        buttons_frame = ttk.Frame(self.search_frame)
        buttons_frame.grid(row=1, column=0, pady=(10, 0))
        
        # Кнопка добавления в избранное
        add_favorite_button = ttk.Button(
            buttons_frame,
            text="Добавить в избранное",
            command=self.add_to_favorites
        )
        add_favorite_button.grid(row=0, column=0, padx=(0, 10))
        
        # Кнопка открытия профиля
        open_profile_button = ttk.Button(
            buttons_frame,
            text="Открыть профиль",
            command=lambda: self.open_profile(favorites=False)
        )
        open_profile_button.grid(row=0, column=1)
        
        # Привязываем двойной клик
        self.search_tree.bind('<Double-1>', lambda e: self.open_profile(favorites=False))
    
    def setup_favorites_tab(self):
        """Настройка вкладки избранных"""
        self.favorites_frame.columnconfigure(0, weight=1)
        self.favorites_frame.rowconfigure(0, weight=1)
        
        # Создаем фрейм для списка и скроллбаров
        list_frame = ttk.Frame(self.favorites_frame)
        list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Treeview для избранных
        columns = ('username', 'date_added')
        self.favorites_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            selectmode='browse'
        )
        
        # Определяем заголовки
        self.favorites_tree.heading('username', text='Имя пользователя')
        self.favorites_tree.heading('date_added', text='Дата добавления')
        
        # Определяем ширину колонок
        self.favorites_tree.column('username', width=200)
        self.favorites_tree.column('date_added', width=200)
        
        # Добавляем скроллбары
        scrollbar_y = ttk.Scrollbar(
            list_frame,
            orient=tk.VERTICAL,
            command=self.favorites_tree.yview
        )
        self.favorites_tree.configure(yscrollcommand=scrollbar_y.set)
        
        # Размещаем элементы
        self.favorites_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Кнопки под списком
        buttons_frame = ttk.Frame(self.favorites_frame)
        buttons_frame.grid(row=1, column=0, pady=(10, 0))
        
        # Кнопки для работы с избранным
        remove_button = ttk.Button(
            buttons_frame,
            text="Удалить из избранного",
            command=self.remove_from_favorites
        )
        remove_button.grid(row=0, column=0, padx=(0, 10))
        
        open_button = ttk.Button(
            buttons_frame,
            text="Открыть профиль",
            command=lambda: self.open_profile(favorites=True)
        )
        open_button.grid(row=0, column=1)
        
        # Привязываем двойной клик
        self.favorites_tree.bind('<Double-1>', lambda e: self.open_profile(favorites=True))
    
    def validate_input(self, username):
        """Проверка корректности ввода"""
        if not username or not username.strip():
            messagebox.showerror("Ошибка", "Поле поиска не должно быть пустым!")
            return False
        return True
    
    def make_api_request(self, url):
        """Выполнение HTTP запроса к GitHub API"""
        try:
            # Создаем запрос с заголовками
            req = urllib.request.Request(
                url,
                headers={
                    'Accept': 'application/vnd.github.v3+json',
                    'User-Agent': 'GitHub-User-Finder-App'
                }
            )
            
            # Выполняем запрос
            with urllib.request.urlopen(req, timeout=10) as response:
                data = response.read().decode('utf-8')
                return json.loads(data)
                
        except urllib.error.HTTPError as e:
            if e.code == 403:
                messagebox.showerror("Ошибка", 
                    "Достигнут лимит запросов к GitHub API.\n"
                    "Пожалуйста, подождите минуту и попробуйте снова.")
            elif e.code == 404:
                messagebox.showerror("Ошибка", "Запрашиваемый ресурс не найден.")
            else:
                messagebox.showerror("Ошибка", f"Ошибка HTTP: {e.code}")
            return None
            
        except urllib.error.URLError as e:
            messagebox.showerror("Ошибка", 
                "Не удалось подключиться к GitHub.\n"
                "Проверьте интернет-соединение.")
            return None
            
        except json.JSONDecodeError:
            messagebox.showerror("Ошибка", "Получен некорректный ответ от сервера.")
            return None
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Неизвестная ошибка: {str(e)}")
            return None
    
    def search_users(self):
        """Поиск пользователей GitHub"""
        username = self.search_var.get().strip()
        
        if not self.validate_input(username):
            return
        
        self.status_var.set(f"Поиск пользователя: {username}")
        self.root.update()
        
        # Формируем URL для поиска
        url = f"https://api.github.com/search/users?q={username}&per_page=30"
        
        # Выполняем запрос
        data = self.make_api_request(url)
        
        if data and 'items' in data:
            self.display_search_results(data['items'])
            self.status_var.set(f"Найдено пользователей: {len(data['items'])}")
        else:
            # Очищаем результаты при ошибке
            for item in self.search_tree.get_children():
                self.search_tree.delete(item)
            self.status_var.set("Ошибка поиска")
    
    def display_search_results(self, users):
        """Отображение результатов поиска"""
        # Очищаем предыдущие результаты
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
        
        # Добавляем новые результаты
        for user in users:
            self.search_tree.insert(
                '',
                'end',
                values=(user['login'], user['html_url'])
            )
    
    def add_to_favorites(self):
        """Добавление пользователя в избранное"""
        selected_item = self.search_tree.selection()
        
        if not selected_item:
            messagebox.showwarning("Предупреждение", 
                "Выберите пользователя для добавления в избранное")
            return
        
        # Получаем имя пользователя из выделенной строки
        item_values = self.search_tree.item(selected_item[0])['values']
        username = item_values[0]
        
        if username in self.favorites:
            messagebox.showinfo("Информация", 
                f"Пользователь '{username}' уже в избранном")
            return
        
        # Добавляем в избранное
        self.favorites[username] = {
            'date_added': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if self.save_favorites():
            self.display_favorites()
            self.status_var.set(f"Пользователь '{username}' добавлен в избранное")
    
    def remove_from_favorites(self):
        """Удаление пользователя из избранного"""
        selected_item = self.favorites_tree.selection()
        
        if not selected_item:
            messagebox.showwarning("Предупреждение", 
                "Выберите пользователя для удаления из избранного")
            return
        
        # Получаем имя пользователя из выделенной строки
        item_values = self.favorites_tree.item(selected_item[0])['values']
        username = item_values[0]
        
        # Запрашиваем подтверждение
        confirm = messagebox.askyesno("Подтверждение", 
            f"Вы уверены, что хотите удалить '{username}' из избранного?")
        
        if confirm and username in self.favorites:
            del self.favorites[username]
            if self.save_favorites():
                self.display_favorites()
                self.status_var.set(f"Пользователь '{username}' удален из избранного")
    
    def display_favorites(self):
        """Отображение избранных пользователей"""
        # Очищаем предыдущие записи
        for item in self.favorites_tree.get_children():
            self.favorites_tree.delete(item)
        
        # Добавляем избранных пользователей в алфавитном порядке
        for username in sorted(self.favorites.keys()):
            data = self.favorites[username]
            self.favorites_tree.insert(
                '',
                'end',
                values=(username, data.get('date_added', 'Неизвестно'))
            )
    
    def open_profile(self, favorites=False):
        """Открытие профиля пользователя в браузере"""
        if favorites:
            tree = self.favorites_tree
        else:
            tree = self.search_tree
        
        selected_item = tree.selection()
        
        if not selected_item:
            messagebox.showwarning("Предупреждение", 
                "Выберите пользователя для открытия профиля")
            return
        
        # Получаем имя пользователя
        item_values = tree.item(selected_item[0])['values']
        username = item_values[0]
        
        # Открываем профиль в браузере
        url = f"https://github.com/{username}"
        webbrowser.open(url)
        self.status_var.set(f"Открыт профиль: {username}")
    
    def clear_search(self):
        """Очистка поля поиска и результатов"""
        self.search_var.set("")
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
        self.status_var.set("Поиск очищен")
    
    def load_favorites(self):
        """Загрузка избранных из JSON файла"""
        if os.path.exists(self.favorites_file):
            try:
                with open(self.favorites_file, 'r', encoding='utf-8') as file:
                    return json.load(file)
            except json.JSONDecodeError:
                messagebox.showwarning("Предупреждение", 
                    "Файл избранных поврежден. Создан новый список.")
                return {}
            except Exception as e:
                messagebox.showerror("Ошибка", 
                    f"Ошибка загрузки избранных: {str(e)}")
                return {}
        return {}
    
    def save_favorites(self):
        """Сохранение избранных в JSON файл"""
        try:
            with open(self.favorites_file, 'w', encoding='utf-8') as file:
                json.dump(self.favorites, file, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", 
                f"Не удалось сохранить избранное: {str(e)}")
            return False

def main():
    """Главная функция запуска приложения"""
    root = tk.Tk()
    
    # Настройка заголовка и иконки (если есть)
    root.title("GitHub User Finder")
    
    # Попытка установить иконку (опционально)
    try:
        # Если у вас есть файл иконки, раскомментируйте следующую строку
        # root.iconbitmap('icon.ico')
        pass
    except:
        pass
    
    # Создание экземпляра приложения
    app = GitHubUserFinder(root)
    
    # Запуск главного цикла обработки событий
    root.mainloop()

if __name__ == "__main__":
    main()
