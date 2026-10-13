from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    ingredients = Column(Text, nullable=False)
    instructions = Column(Text, nullable=False)
    prep_time = Column(Integer, default=0)

    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=True
    )

    category = relationship("Category", backref="recipes")