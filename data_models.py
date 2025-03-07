from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

class Author(db.Model):
    """
    Represents an author in the database.
    """

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    birth_date: Mapped[Date] = mapped_column(Date, nullable=False)
    date_of_death: Mapped[Date] = mapped_column(Date, nullable=True)
    books = relationship("Book", back_populates="author")

    def __repr__(self):
        return f"<Author(id={self.id}, name='{self.name}')>"

    def __str__(self):
        return f"{self.name} (Born: {self.birth_date})"


class Book(db.Model):
    """
    Represents a book in the database.
    """

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    isbn: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)  # ISBN should be unique
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    publication_year: Mapped[int] = mapped_column(Integer, nullable=False)  # Use Integer for year
    author_id: Mapped[int] = mapped_column(ForeignKey("author.id"), nullable=False)  # Foreign Key
    author = relationship("Author", back_populates="books")

    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}')>"

    def __str__(self):
        return f"{self.title} ({self.publication_year}) by {self.author.name}"