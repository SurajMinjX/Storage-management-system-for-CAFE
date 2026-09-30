import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

# Database connection establish kar rahe hain
connection = sqlite3.connect("storage.db")
cursor = connection.cursor()

# 5 clean columns wali table create kar rahe hain
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL
    )
"""
)
connection.commit()

# --- PRE-EXISTING SAMPLE PRODUCTS ---

cursor.execute("SELECT COUNT(*) FROM products")
if cursor.fetchone()[0] == 0:
  sample_products = [
      (1, "Basmati Rice", "Grains", 80.0, 50),
      (2, "Refined Oil", "Oil", 140.0, 15),
      (3, "Sugar", "Groceries", 45.0, 30),
      (4, "Toor Dal", pulses := "Pulses", 110.0, 20),
  ]
  cursor.executemany(
      "INSERT OR IGNORE INTO products VALUES (?, ?, ?, ?, ?)", sample_products
  )
  connection.commit()


# -------------------------------------------------------------
# 1. ADD PRODUCT WINDOW
# -------------------------------------------------------------
def open_add_window():
  add_win = tk.Toplevel(root)
  add_win.title("Add Product")
  add_win.geometry("350x350")
  add_win.config(bg="#f4f6f7")

  tk.Label(
      add_win,
      text="Add New Product",
      font=("Arial", 12, "bold"),
      bg="#f4f6f7",
      fg="#2c3e50",
  ).pack(pady=10)

  fields = [
      ("Product ID:", tk.Entry),
      ("Product Name:", tk.Entry),
      ("Category:", tk.Entry),
      ("Price:", tk.Entry),
      ("Quantity:", tk.Entry),
  ]
  entries = {}

  for label_text, widget_type in fields:
    tk.Label(
        add_win, text=label_text, bg="#f4f6f7", font=("Arial", 9, "bold")
    ).pack()
    entry = widget_type(add_win, width=25, font=("Arial", 10))
    entry.pack(pady=2)
    entries[label_text] = entry

  def save_product():
    try:
      p_id = int(entries["Product ID:"].get())
      p_name = entries["Product Name:"].get()
      cat = entries["Category:"].get()
      price = float(entries["Price:"].get())
      qty = int(entries["Quantity:"].get())

      if not p_name or not cat:
        raise ValueError("Fields cannot be empty")

      cursor.execute(
          "INSERT INTO products VALUES (?, ?, ?, ?, ?)",
          (p_id, p_name, cat, price, qty),
      )
      connection.commit()
      messagebox.showinfo("Success", "Product Added Successfully!")
      add_win.destroy()
    except ValueError as e:
      messagebox.showerror(
          "Error", f"Invalid input or empty fields! Details: {e}"
      )
    except sqlite3.IntegrityError:
      messagebox.showerror(
          "Error", "Product ID already exists! (Primary Key violation)"
      )
      connection.rollback()

  tk.Button(
      add_win,
      text="Save Product",
      bg="#27ae60",
      fg="white",
      font=("Arial", 10, "bold"),
      command=save_product,
  ).pack(pady=15)


# -------------------------------------------------------------
# 2. VIEW PRODUCTS WINDOW
# -------------------------------------------------------------
def open_view_window():
  view_win = tk.Toplevel(root)
  view_win.title("Inventory List")
  view_win.geometry("600x400")

  columns = ("ID", "Name", "Category", "Price", "Quantity")
  tree = ttk.Treeview(view_win, columns=columns, show="headings")

  for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100, anchor=tk.CENTER)

  cursor.execute("SELECT * FROM products")
  rows = cursor.fetchall()
  for row in rows:
    tree.insert("", tk.END, values=row)

  tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


# -------------------------------------------------------------
# 3. UPDATE PRODUCT WINDOW
# -------------------------------------------------------------
def open_update_window():
  up_win = tk.Toplevel(root)
  up_win.title("Update Product")
  up_win.geometry("300x250")
  up_win.config(bg="#f4f6f7")

  tk.Label(
      up_win,
      text="Update Price & Quantity",
      font=("Arial", 11, "bold"),
      bg="#f4f6f7",
  ).pack(pady=10)

  tk.Label(up_win, text="Product ID to Update:", bg="#f4f6f7").pack()
  e_id = tk.Entry(up_win, width=20)
  e_id.pack(pady=2)

  tk.Label(up_win, text="New Price:", bg="#f4f6f7").pack()
  e_price = tk.Entry(up_win, width=20)
  e_price.pack(pady=2)

  tk.Label(up_win, text="New Quantity:", bg="#f4f6f7").pack()
  e_qty = tk.Entry(up_win, width=20)
  e_qty.pack(pady=2)

  def update_db():
    try:
      p_id = int(e_id.get())
      new_p = float(e_price.get())
      new_q = int(e_qty.get())

      cursor.execute(
          "SELECT * FROM products WHERE product_id = ?", (p_id,)
      )
      if cursor.fetchone() is None:
        messagebox.showerror("Error", "Product ID not found!")
        return

      cursor.execute(
          "UPDATE products SET price = ?, quantity = ? WHERE product_id = ?",
          (new_p, new_q, p_id),
      )
      connection.commit()
      messagebox.showinfo("Success", "Product Updated Successfully!")
      up_win.destroy()
    except ValueError:
      messagebox.showerror("Error", "Please enter valid numeric values!")
      connection.rollback()

  tk.Button(
      up_win,
      text="Update",
      bg="#2980b9",
      fg="white",
      font=("Arial", 9, "bold"),
      command=update_db,
  ).pack(pady=15)


# -------------------------------------------------------------
# 4. DELETE PRODUCT WINDOW
# -------------------------------------------------------------

def open_delete_window():
  del_win = tk.Toplevel(root)
  del_win.title("Delete Product")
  del_win.geometry("280x180")
  del_win.config(bg="#f4f6f7")

  tk.Label(
      del_win,
      text="Delete Product by ID",
      font=("Arial", 11, "bold"),
      bg="#f4f6f7",
  ).pack(pady=10)

  tk.Label(del_win, text="Enter Product ID:", bg="#f4f6f7").pack()
  e_id = tk.Entry(del_win, width=20)
  e_id.pack(pady=5)

  def delete_db():
    try:
      p_id = int(e_id.get())
      cursor.execute(
          "SELECT * FROM products WHERE product_id = ?", (p_id,)
      )
      if cursor.fetchone() is None:
        messagebox.showerror("Error", "Product ID not found!")
        return

      cursor.execute("DELETE FROM products WHERE product_id = ?", (p_id,))
      connection.commit()
      messagebox.showinfo("Success", "Product Deleted Successfully!")
      del_win.destroy()
    except ValueError:
      messagebox.showerror("Error", "Please enter a valid numeric ID!")
      connection.rollback()

  tk.Button(
      del_win,
      text="Delete",
      bg="#c0392b",
      fg="white",
      font=("Arial", 9, "bold"),
      command=delete_db,
  ).pack(pady=10)


# -------------------------------------------------------------
# MAIN GUI DASHBOARD
# -------------------------------------------------------------

root = tk.Tk()
root.title("Storage Management System")
root.geometry("400x350")
root.config(bg="#ebdef0")

tk.Label(
    root,
    text="STORAGE MANAGEMENT SYSTEM",
    font=("Arial", 13, "bold"),
    bg="#ebdef0",
    fg="#512e5f",
).pack(pady=20)

btn_style = {
    "font": ("Arial", 10, "bold"),
    "width": 25,
    "fg": "white",
    "bd": 2,
}

tk.Button(
    root,
    text="1. Add Product",
    bg="#27ae60",
    command=open_add_window,
    **btn_style,
).pack(pady=8)
tk.Button(
    root,
    text="2. View Inventory",
    bg="#2980b9",
    command=open_view_window,
    **btn_style,
).pack(pady=8)
tk.Button(
    root,
    text="3. Update Product",
    bg="#d4ac0d",
    command=open_update_window,
    **btn_style,
).pack(pady=8)
tk.Button(
    root,
    text="4. Delete Product",
    bg="#c0392b",
    command=open_delete_window,
    **btn_style,
).pack(pady=8)
tk.Button(
    root,
    text="5. Exit",
    bg="#566573",
    command=root.destroy,
    **btn_style,
).pack(pady=8)

root.mainloop()