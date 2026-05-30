from flask import Blueprint, jsonify, request

from backend.library_service import get_book_content, get_book_by_id, get_categories, get_library

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
