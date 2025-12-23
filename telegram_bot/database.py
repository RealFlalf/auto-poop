from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session
from models import Base, User, Score
from config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    return SessionLocal()

def get_user_by_telegram_id(db: Session, telegram_id: int):
    return db.query(User).filter(User.telegram_id == telegram_id).first()

def create_or_update_user(db: Session, telegram_id: int, username=None, first_name=None, last_name=None):
    user = get_user_by_telegram_id(db, telegram_id)
    if user:
        if username:
            user.username = username
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
    else:
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        db.add(user)
    db.commit()
    db.refresh(user)
    return user

def add_score(db: Session, telegram_id: int, points: int = 1):
    user = get_user_by_telegram_id(db, telegram_id)
    if user:
        score_entry = Score(user_id=user.id, points=points, timestamp=func.now())
        db.add(score_entry)
        db.commit()
        db.refresh(score_entry)
        return score_entry
    return None

def get_total_score(db: Session, telegram_id: int):
    user = get_user_by_telegram_id(db, telegram_id)
    if user:
        from sqlalchemy import func as sql_func
        result = db.query(sql_func.sum(Score.points)).filter(Score.user_id == user.id).scalar()
        return result or 0
    return 0

def get_top_users(db: Session, limit: int = 10):
    from sqlalchemy import func as sql_func
    subquery = db.query(
        Score.user_id,
        sql_func.sum(Score.points).label('total_score')
    ).group_by(Score.user_id).subquery()

    results = db.query(
        User.telegram_id,
        User.username,
        User.first_name,
        User.last_name,
        subquery.c.total_score
    ).join(subquery, User.id == subquery.c.user_id).order_by(subquery.c.total_score.desc()).limit(limit).all()

    return results

def clear_scores(db: Session):
    db.query(Score).delete()
    db.commit()

def get_user_scores_over_time(db: Session):
    from sqlalchemy import func as sql_func
    # Получить все очки с пользователями
    results = db.query(
        User.telegram_id,
        User.username,
        User.first_name,
        User.last_name,
        func.date(Score.timestamp).label('date'),
        Score.points
    ).join(Score, User.id == Score.user_id).order_by(User.telegram_id, func.date(Score.timestamp)).all()

    return results
