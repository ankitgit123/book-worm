# 📚 Book Worm

A full-stack e-commerce bookstore application where users can browse books, manage their wishlist and cart, purchase books, and manage their orders.

This project is being developed incrementally, starting with the core customer bookstore experience and expanding toward an enterprise-ready platform.

---

## 🚀 V1 — Current Release

V1 focuses on the complete customer-facing bookstore journey.

### Customer Features

- User registration
- User login and JWT authentication
- Browse book catalogue
- Browse books by category
- Browse publishers
- Search books
- View book details
- View tentative delivery date
- View related books
- Add books to wishlist
- Remove books from wishlist
- Add books to cart
- Update cart quantities
- Remove items from cart
- Clear cart
- Manage delivery addresses
- Set default address
- Checkout
- Gift points redemption
- Mock payment
- Order confirmation
- Order history
- Order details
- Buy Again
- Cancel order within 48 hours
- Submit book reviews
- Personalized recommendations

---

## 🏗️ Architecture

```text
┌───────────────────────────┐
│       React Frontend      │
│      TypeScript + Vite    │
└─────────────┬─────────────┘
              │
              │ REST / JSON
              ▼
┌───────────────────────────┐
│       FastAPI Backend     │
│       Python REST API     │
└─────────────┬─────────────┘
              │
              │ SQLAlchemy
              ▼
┌───────────────────────────┐
│          MySQL 8          │
└───────────────────────────┘