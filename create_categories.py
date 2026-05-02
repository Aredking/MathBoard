from app import create_app, db
from app.models import Category
from app.constants import DEFAULT_CATEGORIES
from app.utils import generate_slug

app = create_app()
with app.app_context():
    for name, slug, color, icon in DEFAULT_CATEGORIES:
        if not Category.query.filter_by(slug=slug).first():
            cat = Category(name=name, slug=slug, color=color, icon=icon)
            db.session.add(cat)
    db.session.commit()
    print("Категории добавлены!")