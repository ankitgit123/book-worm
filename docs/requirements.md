# Book Worm — Software Requirements Specification

## 1. Project Overview

Book Worm is an online bookstore platform that allows customers
to browse books, view book details, add books to a shopping cart,
checkout, make a payment, and receive purchase confirmation.

The platform supports both guest users and registered users.

Registered users receive additional capabilities such as order
history, Buy Again, wishlist, recommendations, gift points,
saved addresses, and order cancellation.

---

# 2. User Types

## 2.1 Guest User

A guest user can:

- Access the bookstore home page
- Browse books
- Browse categories
- Search books
- Filter books
- Sort books
- View book details
- View related books
- View author information

A guest user must authenticate before completing a purchase.

## 2.2 Registered User

A registered user can:

- Login
- Logout
- Browse books
- Search books
- Filter books
- View book details
- Add books to cart
- Update cart quantities
- Remove books from cart
- Add/remove wishlist items
- View order history
- Buy Again
- Receive book recommendations
- Manage addresses
- Redeem gift points
- Checkout
- Make payment
- View purchase confirmation
- Cancel eligible orders

---

# 3. Functional Requirements

## FR-001 — User Registration

The system shall allow a new customer to create an account.

Required information:

- Name
- Email
- Password
- Confirm password

The system shall validate the submitted information.

---

## FR-002 — User Login

The system shall allow registered users to authenticate using
their email and password.

---

## FR-003 — User Logout

The system shall allow an authenticated user to logout.

---

## FR-004 — Home Page

The system shall provide a bookstore home page.

The home page shall display books organized into sections such as:

- Recommended for You
- Bestsellers
- New Launches

The supplied wireframe contains these catalogue/home sections. 


---

## FR-005 — Catalogue

The system shall provide a catalogue of books.

Users shall be able to:

- Browse all books
- Browse books by category
- Browse books by brand/publisher
- Search books
- Filter by language
- Filter by format
- Filter by price range
- Sort books

---

## FR-006 — Category Browsing

The system shall allow users to select a category.

Example categories:

- Romance
- Mystery
- Science Fiction
- Fantasy
- Historical
- Biography
- Self-help
- Memoir
- Travel
- Cooking
- Children's
- Young Adult
- Comics & Graphic Novels
- Poetry
- Drama
- Science
- Philosophy
- Religion
- Language Learning

---

## FR-007 — Book Details

The system shall provide a detail page for each book.

The page shall display:

- Book cover
- Title
- Author
- Description
- Publisher
- Format
- Language
- Categories
- Price
- Rating
- Sales information
- Tentative delivery date

The page shall also display:

- Related books
- Author information
- Reviews

---

## FR-008 — Related Books

The system shall display related books when a customer views
a book.

Related books may be determined using:

- Category
- Author
- Genre

---

## FR-009 — Shopping Cart

A registered user shall be able to add books to a shopping cart.

The cart shall allow the user to:

- Add a book
- Increase quantity
- Decrease quantity
- Remove a book
- View item price
- View quantity
- View subtotal
- View total

---

## FR-010 — Wishlist

A registered user shall be able to:

- Add a book to wishlist
- Remove a book from wishlist
- View wishlist
- Move a wishlist book to cart

---

## FR-011 — Order History

A registered user shall be able to view previous orders.

Each order shall contain:

- Order ID
- Order date
- Purchased books
- Quantities
- Price
- Total amount
- Payment status
- Order status
- Delivery information

---

## FR-012 — Buy Again

A registered user shall be able to select a previous order
and purchase the same books again.

The system shall add the previous order's books and quantities
to the user's current cart.

---

## FR-013 — Recommendations

The system shall recommend books based on the user's order history.

Recommendation inputs may include:

- Previously purchased books
- Previously purchased categories
- Previously purchased genres

---

## FR-014 — Gift Points

The system shall maintain gift/reward points for registered users.

Users shall be able to redeem eligible points during checkout.

The system shall prevent redemption of more points than the
user currently owns.

---

## FR-015 — Address Management

A registered user shall be able to:

- Add an address
- View saved addresses
- Select a saved address during checkout

Address information shall include:

- First name
- Last name
- Address
- Email
- City
- PIN
- Phone number
- State
- Country

---

## FR-016 — Checkout

The checkout page shall display:

- Cart items
- Quantities
- Prices
- Address
- Subtotal
- Tax
- Delivery charges
- Gift-point discount
- Final amount

The user shall be able to proceed to payment.

---

## FR-017 — Payment

The system shall support the following payment options:

- Credit Card
- Debit Card
- UPI
- Wallet

For the capstone implementation, payment can use a mock/simulated
payment provider.

---

## FR-018 — Payment Failure

If payment fails, the system shall:

- Display an error
- Keep the cart/order checkout information available
- Allow the user to retry payment

---

## FR-019 — Order Creation

After successful payment, the system shall create an order.

The order shall contain:

- Customer
- Order items
- Address
- Payment information
- Total amount
- Order status

---

## FR-020 — Purchase Confirmation

After successful purchase, the system shall display a confirmation
screen containing:

- Success message
- Order ID
- Purchased books
- Amount
- Delivery information
- Continue Shopping action

---

## FR-021 — Order Cancellation

A user shall be allowed to cancel an order within 48 hours of
order creation.

After 48 hours, cancellation shall not be allowed.

The cancellation rule is explicitly included in the capstone
customer journey. 