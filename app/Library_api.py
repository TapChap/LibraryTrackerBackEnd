from flask import request, Blueprint

from book.Book_db import *
from client.Client_db import *

library_route = Blueprint("library_bp", __name__)

@library_route.route('/user/id/<int:client_id>/obtain', methods=['POST'])
def obtain_book(client_id):
    data = request.get_json()
    book_id = data.get("book_id")

    if not book_id:
        return {"message": "Missing book id"}, 400

    book, status_code = getBookById(book_id)
    if status_code == 404:
        return {"message": "Book not found"}, 404

    client, status_code = getClientByID(client_id)
    if status_code == 404:
        return {"message": "User not found"}, 404

    # Check if book is available
    if book.is_taken:
        return {"message": "Book not available"}, 400

    # Check if the client already has this book
    if book in client.held_books:
        return {"message": "Client already has this book"}, 400

    # Decrease quantity and add to client's held books
    book.available_count -= 1
    book.is_taken = book.available_count == 0  # Mark as taken if no copies left

    client.held_books.append(book)

    db.session.commit()

    return {
        "message": "book obtained by user",
        "book": book.toJson(),
        "user": client.toJson()
    }, 200

@library_route.route('/user/id/<int:client_id>/return', methods=['POST'])
def return_book(client_id):
    data = request.get_json()
    book_id = data.get("book_id")

    if not book_id:
        return {"message": "Missing book id"}, 400

    book, status_code = getBookById(book_id)
    if status_code == 404:
        return {"message": "Book not found"}, 404

    client, status_code = getClientByID(client_id)
    if status_code == 404:
        return {"message": "User not found"}, 404

    if book not in client.held_books:
        return {"message": "attempt to return book that isn't taken by user"}, 400

    book.available_count += 1
    book.is_taken = False

    client.held_books.remove(book)

    db.session.commit()

    return {
        "message": "book returned from user",
        "book": book.toJson(),
        "user": client.toJson()
    }, 200
