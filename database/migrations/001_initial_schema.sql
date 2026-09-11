CREATE DATABASE IF NOT EXISTS book_worm;

USE book_worm;


-- =========================================================
-- USERS
-- =========================================================

CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    gift_points_balance INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- =========================================================
-- AUTHORS
-- =========================================================

CREATE TABLE authors (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    bio TEXT,
    photo_url VARCHAR(500),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- =========================================================
-- PUBLISHERS
-- =========================================================

CREATE TABLE publishers (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- =========================================================
-- CATEGORIES
-- =========================================================

CREATE TABLE categories (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(120) NOT NULL UNIQUE
);


-- =========================================================
-- BOOKS
-- =========================================================

CREATE TABLE books (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    title VARCHAR(255) NOT NULL,

    description TEXT,

    author_id BIGINT NOT NULL,

    publisher_id BIGINT,

    format ENUM(
        'Paperback',
        'Hardcover',
        'eBook'
    ) NOT NULL,

    language VARCHAR(50) NOT NULL,

    price DECIMAL(10,2) NOT NULL DEFAULT 0,

    cover_image_url VARCHAR(500),

    delivery_date DATE,

    stock_quantity INT NOT NULL DEFAULT 0,

    sales_count INT NOT NULL DEFAULT 0,

    average_rating DECIMAL(2,1) NOT NULL DEFAULT 0,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (author_id)
        REFERENCES authors(id),

    FOREIGN KEY (publisher_id)
        REFERENCES publishers(id)
);


-- =========================================================
-- BOOK CATEGORIES
-- =========================================================

CREATE TABLE book_categories (
    book_id BIGINT NOT NULL,

    category_id BIGINT NOT NULL,

    PRIMARY KEY (book_id, category_id),

    FOREIGN KEY (book_id)
        REFERENCES books(id)
        ON DELETE CASCADE,

    FOREIGN KEY (category_id)
        REFERENCES categories(id)
        ON DELETE CASCADE
);


-- =========================================================
-- ADDRESSES
-- =========================================================

CREATE TABLE addresses (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    user_id BIGINT NOT NULL,

    first_name VARCHAR(100) NOT NULL,

    last_name VARCHAR(100) NOT NULL,

    address_line VARCHAR(255) NOT NULL,

    city VARCHAR(100) NOT NULL,

    state VARCHAR(100) NOT NULL,

    country VARCHAR(100) NOT NULL,

    postal_code VARCHAR(20) NOT NULL,

    phone VARCHAR(30) NOT NULL,

    email VARCHAR(255) NOT NULL,

    is_default BOOLEAN NOT NULL DEFAULT FALSE,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
);


-- =========================================================
-- CARTS
-- =========================================================

CREATE TABLE carts (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    user_id BIGINT NOT NULL UNIQUE,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);


-- =========================================================
-- CART ITEMS
-- =========================================================

CREATE TABLE cart_items (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    cart_id BIGINT NOT NULL,

    book_id BIGINT NOT NULL,

    quantity INT NOT NULL,

    UNIQUE (cart_id, book_id),

    FOREIGN KEY (cart_id)
        REFERENCES carts(id)
        ON DELETE CASCADE,

    FOREIGN KEY (book_id)
        REFERENCES books(id)
);


-- =========================================================
-- WISHLISTS
-- =========================================================

CREATE TABLE wishlists (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    user_id BIGINT NOT NULL,

    book_id BIGINT NOT NULL,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (user_id, book_id),

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    FOREIGN KEY (book_id)
        REFERENCES books(id)
);


-- =========================================================
-- ORDERS
-- =========================================================

CREATE TABLE orders (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    user_id BIGINT NOT NULL,

    status ENUM(
        'PENDING',
        'CONFIRMED',
        'COMPLETED',
        'CANCELLED'
    ) NOT NULL DEFAULT 'PENDING',

    subtotal DECIMAL(10,2) NOT NULL DEFAULT 0,

    tax DECIMAL(10,2) NOT NULL DEFAULT 0,

    delivery_charge DECIMAL(10,2) NOT NULL DEFAULT 0,

    discount DECIMAL(10,2) NOT NULL DEFAULT 0,

    gift_points_used INT NOT NULL DEFAULT 0,

    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0,

    shipping_first_name VARCHAR(100) NOT NULL,

    shipping_last_name VARCHAR(100) NOT NULL,

    shipping_address VARCHAR(255) NOT NULL,

    shipping_city VARCHAR(100) NOT NULL,

    shipping_state VARCHAR(100) NOT NULL,

    shipping_country VARCHAR(100) NOT NULL,

    shipping_postal_code VARCHAR(20) NOT NULL,

    shipping_phone VARCHAR(30) NOT NULL,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    cancelled_at DATETIME,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
);


-- =========================================================
-- ORDER ITEMS
-- =========================================================

CREATE TABLE order_items (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    order_id BIGINT NOT NULL,

    book_id BIGINT NOT NULL,

    quantity INT NOT NULL,

    unit_price DECIMAL(10,2) NOT NULL,

    total_price DECIMAL(10,2) NOT NULL,

    FOREIGN KEY (order_id)
        REFERENCES orders(id)
        ON DELETE CASCADE,

    FOREIGN KEY (book_id)
        REFERENCES books(id)
);


-- =========================================================
-- PAYMENTS
-- =========================================================

CREATE TABLE payments (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    order_id BIGINT NOT NULL UNIQUE,

    payment_method ENUM(
        'CREDIT_CARD',
        'DEBIT_CARD',
        'UPI',
        'WALLET'
    ) NOT NULL,

    amount DECIMAL(10,2) NOT NULL,

    status ENUM(
        'PENDING',
        'SUCCESS',
        'FAILED'
    ) NOT NULL DEFAULT 'PENDING',

    transaction_reference VARCHAR(255),

    paid_at DATETIME,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (order_id)
        REFERENCES orders(id)
);


-- =========================================================
-- REVIEWS
-- =========================================================

CREATE TABLE reviews (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    user_id BIGINT NOT NULL,

    book_id BIGINT NOT NULL,

    rating INT NOT NULL,

    comment TEXT,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (user_id, book_id),

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    FOREIGN KEY (book_id)
        REFERENCES books(id)
        ON DELETE CASCADE
);


-- =========================================================
-- INDEXES
-- =========================================================

CREATE INDEX idx_books_author
    ON books(author_id);

CREATE INDEX idx_books_publisher
    ON books(publisher_id);

CREATE INDEX idx_books_language
    ON books(language);

CREATE INDEX idx_books_format
    ON books(format);

CREATE INDEX idx_books_price
    ON books(price);

CREATE INDEX idx_books_active
    ON books(is_active);

CREATE INDEX idx_book_categories_category
    ON book_categories(category_id);

CREATE INDEX idx_addresses_user
    ON addresses(user_id);

CREATE INDEX idx_cart_items_book
    ON cart_items(book_id);

CREATE INDEX idx_wishlists_user
    ON wishlists(user_id);

CREATE INDEX idx_orders_user
    ON orders(user_id);

CREATE INDEX idx_orders_created_at
    ON orders(created_at);

CREATE INDEX idx_orders_status
    ON orders(status);

CREATE INDEX idx_order_items_order
    ON order_items(order_id);

CREATE INDEX idx_order_items_book
    ON order_items(book_id);

CREATE INDEX idx_reviews_book
    ON reviews(book_id);