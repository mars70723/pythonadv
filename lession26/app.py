import os
 
import requests
import streamlit as st
from dotenv import load_dotenv
 
load_dotenv()
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
 
 
# ---------- Category API calls ----------
def get_categories():
    """GET /categories/ - fetch all categories."""
    r = requests.get(f"{API_URL}/categories/")
    r.raise_for_status()
    return r.json()
 
 
def create_category(name):
    """POST /categories/ - category name goes in the request body."""
    return requests.post(f"{API_URL}/categories/", json={"name": name})
 
 
def update_category(category_id, name):
    """PUT /categories/{category_id} - rename a category."""
    return requests.put(f"{API_URL}/categories/{category_id}", json={"name": name})
 
 
def delete_category(category_id):
    """DELETE /categories/{category_id} - remove a category."""
    return requests.delete(f"{API_URL}/categories/{category_id}")
 
 
# ---------- Recipe API calls ----------
def get_recipes():
    r = requests.get(f"{API_URL}/recipes/")
    r.raise_for_status()
    return r.json()
 
 
def create_recipe(data):
    return requests.post(f"{API_URL}/recipes/", json=data)
 
 
def update_recipe(recipe_id, data):
    return requests.put(f"{API_URL}/recipes/{recipe_id}", json=data)
 
 
def delete_recipe(recipe_id):
    return requests.delete(f"{API_URL}/recipes/{recipe_id}")
 
 
def show_result(resp, success_msg):
    if resp.ok:
        st.success(success_msg)
        st.rerun()
    else:
        try:
            detail = resp.json().get("detail", resp.text)
        except ValueError:
            detail = resp.text
        st.error(f"Error: {detail}")
 
 
# ---------- Pages ----------
def dashboard():
    st.header("📊 Dashboard")
    st.subheader("Recipes")
    recipes = get_recipes()
    if recipes:
        rows = [
            {
                "ID": r["id"],
                "Title": r["title"],
                "Category": r.get("category_name") or "-",
                "Ingredients": r["ingredients"],
                "Instructions": r["instructions"],
            }
            for r in recipes
        ]
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.info("No recipes yet.")
 
    st.subheader("Categories")
    cats = get_categories()
    if cats:
        rows = [{"ID": c["id"], "Name": c["name"]} for c in cats]
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.info("No categories yet.")
 
 
def manage_categories():
    st.header("🗂️ Manage Categories")
    cats = get_categories()
    tab_add, tab_edit, tab_del = st.tabs(["Add", "Edit", "Delete"])
 
    with tab_add:
        with st.form("add_cat", clear_on_submit=True):
            name = st.text_input("Category name")
            if st.form_submit_button("Create") :
                if name.strip():
                    show_result(create_category(name), "Category created!")
                else:
                    st.warning("Please enter a name.")
 
    options = {c["name"]: c["id"] for c in cats}
 
    with tab_edit:
        if options:
            chosen = st.selectbox("Category to edit", list(options), key="edit_cat_sel")
            new_name = st.text_input("New name", value=chosen, key=f"edit_cat_name_{chosen}")
            if st.button("Update category"):
                if new_name.strip():
                    show_result(update_category(options[chosen], new_name), "Category updated!")
                else:
                    st.warning("Name can't be empty.")
        else:
            st.info("No categories to edit.")
 
    with tab_del:
        if options:
            chosen = st.selectbox("Category to delete", list(options), key="del_cat_sel")
            st.caption("Recipes in this category will be kept but become uncategorised.")
            if st.button("Delete category", type="primary"):
                show_result(delete_category(options[chosen]), "Category deleted!")
        else:
            st.info("No categories to delete.")
 
 
def manage_recipes():
    st.header("🍲 Manage Recipes")
    cats = get_categories()
    cat_options = {"(none)": None, **{c["name"]: c["id"] for c in cats}}
    recipes = get_recipes()
    tab_add, tab_edit, tab_del = st.tabs(["Add", "Edit", "Delete"])
 
    with tab_add:
        with st.form("add_recipe", clear_on_submit=True):
            title = st.text_input("Title")
            cat = st.selectbox("Category", list(cat_options))
            ingredients = st.text_area("Ingredients")
            instructions = st.text_area("Instructions")
            if st.form_submit_button("Add recipe"):
                if title.strip() and ingredients.strip() and instructions.strip():
                    show_result(create_recipe({
                        "title": title, "ingredients": ingredients,
                        "instructions": instructions, "category_id": cat_options[cat],
                    }), "Recipe added!")
                else:
                    st.warning("Title, ingredients and instructions are required.")
 
    recipe_options = {f"{r['id']} - {r['title']}": r for r in recipes}
 
    with tab_edit:
        if recipe_options:
            label = st.selectbox("Recipe to edit", list(recipe_options), key="edit_rec_sel")
            r = recipe_options[label]
            k = f"_{r['id']}"
            title = st.text_input("Title", value=r["title"], key="t" + k)
            names = list(cat_options)
            current = r.get("category_name") or "(none)"
            idx = names.index(current) if current in names else 0
            cat = st.selectbox("Category", names, index=idx, key="c" + k)
            ingredients = st.text_area("Ingredients", value=r["ingredients"], key="i" + k)
            instructions = st.text_area("Instructions", value=r["instructions"], key="n" + k)
            if st.button("Update recipe"):
                show_result(update_recipe(r["id"], {
                    "title": title, "ingredients": ingredients,
                    "instructions": instructions, "category_id": cat_options[cat],
                }), "Recipe updated!")
        else:
            st.info("No recipes to edit.")
 
    with tab_del:
        if recipe_options:
            label = st.selectbox("Recipe to delete", list(recipe_options), key="del_rec_sel")
            if st.button("Delete recipe", type="primary"):
                show_result(delete_recipe(recipe_options[label]["id"]), "Recipe deleted!")
        else:
            st.info("No recipes to delete.")
 
 
# ---------- Main ----------
st.set_page_config(page_title="Online Recipe Book", page_icon="🍳", layout="wide")
st.title("🍳 Online Recipe Book")
 
page = st.sidebar.radio("Navigate", ["Dashboard", "Manage Recipes", "Manage Categories"])
 
try:
    {"Dashboard": dashboard,
     "Manage Recipes": manage_recipes,
     "Manage Categories": manage_categories}[page]()
except requests.exceptions.ConnectionError:
    st.error("Can't reach the backend. Start it with: uvicorn main:app --reload")