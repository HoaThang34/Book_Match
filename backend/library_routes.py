from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from backend.extensions import db
from backend.library_service import get_book_content, get_book_by_id, get_categories, get_library
from backend.models import BookComment, User

library_bp = Blueprint("library", __name__, url_prefix="/api/library")


@library_bp.get("")
def list_books():
    category = request.args.get("category", "").strip()
    search = request.args.get("search", "").strip()
    books = get_library()
    if category:
        books = [b for b in books if b["category"]["slug"] == category]
    if search:
        q = search.lower()
        books = [b for b in books if q in b["title"].lower() or q in b["description"].lower()]
    return jsonify({"books": books, "total": len(books)})


@library_bp.get("/categories")
def list_categories():
    return jsonify({"categories": get_categories()})


@library_bp.get("/<int:book_id>")
def book_detail(book_id: int):
    book = get_book_by_id(book_id)
    if not book:
        return jsonify({"error": "Không tìm thấy sách."}), 404
    content = get_book_content(book_id)
    book = {k: v for k, v in book.items() if k != "file_path"}
    return jsonify({"book": book, "content": content or ""})


@library_bp.get("/<int:book_id>/comments")
def get_comments(book_id: int):
    if not get_book_by_id(book_id):
        return jsonify({"error": "Không tìm thấy sách."}), 404
    comments = (
        BookComment.query
        .filter_by(book_id=book_id)
        .order_by(BookComment.created_at.desc())
        .limit(50)
        .all()
    )
    return jsonify({"comments": [c.to_dict() for c in comments], "total": len(comments)})


@library_bp.post("/<int:book_id>/comments")
@jwt_required()
def post_comment(book_id: int):
    if not get_book_by_id(book_id):
        return jsonify({"error": "Không tìm thấy sách."}), 404
    data = request.get_json(silent=True) or {}
    content = (data.get("content") or "").strip()
    if not content:
        return jsonify({"error": "Nội dung bình luận không được để trống."}), 400
    if len(content) > 1000:
        return jsonify({"error": "Bình luận không được vượt quá 1000 ký tự."}), 400
    user_id = int(get_jwt_identity())
    comment = BookComment(
        book_id=book_id,
        user_id=user_id,
        content=content,
        created_at=datetime.now(timezone.utc),
    )
    db.session.add(comment)
    db.session.commit()
    return jsonify({"comment": comment.to_dict()}), 201
