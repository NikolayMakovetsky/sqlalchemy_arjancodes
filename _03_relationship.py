import hashlib

import sqlalchemy as sa
from sqlalchemy.orm import (
    Mapped,
    declarative_base,
    mapped_column,
    relationship,
    sessionmaker
)

db = sa.create_engine("sqlite:///:memory:", echo=True)
Session = sessionmaker(bind=db)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    # one to one
    auth: Mapped["UserAuth"] = relationship(
        "UserAuth", uselist=False, back_populates="user"
    )
    # one to many
    posts: Mapped[list["UserPost"]] = relationship(
        "UserPost", back_populates="user"
    )

    def __init__(self, username: str, email: str, password: str):
        super().__init__()
        self.auth = UserAuth(username=username, email=email)
        self.auth.set_password(password)

    def __repr__(self) -> str:
        return f"<User(username={self.auth.username}, email={self.auth.email})>"


class UserAuth(Base):
    __tablename__ = "user_auth"

    id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("users.id"), primary_key=True, index=True, unique=True)
    username: Mapped[str]
    email: Mapped[str] = mapped_column(index=True, unique=True)
    password_hash: Mapped[str]
    user: Mapped["User"] = relationship("User", back_populates="auth")

    def __init__(self, username: str, email: str):
        self.username = username
        self.email = email

    def set_password(self, password: str) -> None:
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, password: str) -> None:
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()

    def __repr__(self) -> str:
        return f"<UserAuth(username={self.username}, email={self.email})>"


class UserPost(Base):
    __tablename__ = "user_posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(sa.Integer, sa. ForeignKey("users.id"), nullable=False, index=True)
    content: Mapped[str]
    user: Mapped["User"] = relationship("User", back_populates="posts")

    def __repr__(self) -> str:
        return f"<UserPost(user={self.user}, content={self.content})>"


def main() -> None:
    Base.metadata.create_all(db)

    with Session.begin() as session:
        user = User(username="Elena", email="elen@mail.com", password="123")
        post = UserPost(content="Hello, I'm Elena!", user=user)
        session.add(user)
        session.add(post)

    with Session.begin() as session:
        user = session.query(User).first()
        print(user)
        print(user.auth)
        print(user.posts)

        print(f"Password check: {user.auth.check_password('123')}")
        print(f"Password check: {user.auth.check_password('wrongpassword')}")

        posts = session.query(UserPost).filter(UserPost.user == user).all()
        print(posts)


if __name__ == '__main__':
    main()
