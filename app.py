import customtkinter as ctk
import sqlite3

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")

class App(ctk.CTk):
    database = "todo.db"

    def __init__(self):
        super().__init__()
        self.geometry("500x300")
        # self.resizable(False, False)
        self.title("TODO App")
        self.minsize(350,250)

        self.create_table()
        self.create_widgets()
        self.render_todo_list()

    def create_widgets(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)

        self.entry = ctk.CTkEntry(master=self, placeholder_text="Agregar tarea")
        self.entry.grid(column=0, row=0, padx=(30,0), pady=(30,0), sticky="nesw")

        self.btn = ctk.CTkButton(master=self, text="Agregar", width=100, command=self.add_todo)
        self.btn.grid(column=1, row=0, padx=(15,30), pady=(30,0))

        self.scrollable_frame = ctk.CTkScrollableFrame(master=self)
        self.scrollable_frame.grid(column=0, row=1, columnspan=2, padx=30, pady=30, sticky="nesw")
        self.scrollable_frame.columnconfigure(0, weight=1)
        self.scrollable_frame.columnconfigure(1, weight=0)

        self.bind("<Return>", lambda event:self.add_todo())

    def run_query(self, query, parameters=()):
        try:
            with sqlite3.connect(self.database) as connector:
                cursor = connector.cursor()
                result = cursor.execute(query, parameters)
                connector.commit()
            return result
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        except Exception as e:
            print(f"Exception in _query: {e}")

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS todo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            description TEXT NOT NULL,
            completed BOOLEAN NOT NULL
        )"""
        self.run_query(query)

    def add_todo(self):
        task = self.entry.get()
        if task:
            query = "INSERT INTO todo (description, completed) VALUES (?, ?)"
            self.run_query(query, (task, False))
            self.entry.delete(0, ctk.END)
            self.render_todo_list()

    def render_todo_list(self):
        query = "SELECT * FROM todo"
        data = self.run_query(query)

        # Limpiamos todos los elementos de la lista todo
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Renderizamos los nuevos elementos
        for i, row in enumerate(data):
            task_id = row[0] 
            completed = row[3]
            description = row[2]
            color = "#555555" if completed else "#FFFFFF"
            task = ctk.CTkCheckBox(master=self.scrollable_frame, text=description, text_color=color, command=self.completed_task(task_id, completed))
            task.grid(column=0, row=i, padx=20, pady=10, sticky="w")
            task.select() if completed else task.deselect()
            btn_delete = ctk.CTkButton(master=self.scrollable_frame, text="Eliminar", width=80, fg_color="#1A1A1A", hover_color="#A52222", command=self.delete_task(task_id))
            btn_delete.grid(column=1, row=i, padx=20, pady=10, sticky="e")
    
    def completed_task(self, task_id, completed):
        def _completed_task():
            query = "UPDATE todo SET completed = ? WHERE id = ?"
            self.run_query(query, (not completed, task_id))
            self.render_todo_list()
        return _completed_task
    
    def delete_task(self, task_id):
        def _delete_task():
            query = "DELETE FROM todo WHERE id = ?"
            self.run_query(query, (task_id, ))
            self.render_todo_list()
        return _delete_task

if __name__ == "__main__":
    app = App()
    app.mainloop()