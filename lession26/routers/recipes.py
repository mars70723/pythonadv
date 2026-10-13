from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.recipe import Recipe
from models.category import Category
from pydantic import BaseModel
from typing import Optional

router = APIRouter(
    prefix="/recipes",
    tags=["Recipes"]
)


class RecipeCreate(BaseModel):
    title: str
    ingredients: str
    instructions: str
    prep_time: int = 0
    category_id: Optional[int] = None


@router.get("/")
def get_recipes(db: Session = Depends(get_db)):
    return db.query(Recipe).all()


@router.post("/")
def create_recipe(
    recipe: RecipeCreate,
    db: Session = Depends(get_db)
):
    if recipe.category_id is not None:
        category = db.query(Category).filter(
            Category.id == recipe.category_id
        ).first()

        if not category:
            raise HTTPException(
                status_code=404,
                detail="Category not found"
            )

    new_recipe = Recipe(**recipe.model_dump())

    db.add(new_recipe)
    db.commit()
    db.refresh(new_recipe)

    return new_recipe


@router.put("/{recipe_id}")
def update_recipe(
    recipe_id: int,
    recipe: RecipeCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(Recipe).filter(
        Recipe.id == recipe_id
    ).first()

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Recipe not found"
        )

    for key, value in recipe.model_dump().items():
        setattr(existing, key, value)

    db.commit()
    db.refresh(existing)

    return existing


@router.delete("/{recipe_id}")
def delete_recipe(
    recipe_id: int,
    db: Session = Depends(get_db)
):
    recipe = db.query(Recipe).filter(
        Recipe.id == recipe_id
    ).first()

    if not recipe:
        raise HTTPException(
            status_code=404,
            detail="Recipe not found"
        )

    db.delete(recipe)
    db.commit()

    return {"message": "Recipe deleted successfully"}