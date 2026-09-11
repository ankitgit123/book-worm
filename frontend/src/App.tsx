import {
  useEffect,
  useState,
} from "react";

import {
  Link,
  Route,
  Routes,
  useNavigate,
  useParams,
} from "react-router-dom";

import {
  addToCart,
  addToWishlist,
  buyAgain,
  cancelOrder,
  createAddress,
  createOrder,
  createReview,
  getAddresses,
  getBook,
  getBooks,
  getCart,
  getCategories,
  getMe,
  getOrder,
  getOrders,
  getRecommendations,
  getRelatedBooks,
  getReviews,
  getWishlist,
  login,
  register,
  removeCartItem,
  removeFromWishlist,
  updateCartItem,
} from "./api";

import type {
  Address,
  Book,
  Cart,
  Category,
  Order,
  RecommendationResponse,
  RelatedBooksResponse,
  Review,
  User,
  WishlistItem,
} from "./types";


// ============================================================
// HELPERS
// ============================================================

function money(value: number) {
  return `₹${Number(value).toFixed(2)}`;
}


function isLoggedIn() {
  return Boolean(
    localStorage.getItem(
      "book_worm_token"
    )
  );
}


// ============================================================
// APP
// ============================================================

export default function App() {
  const [
    user,
    setUser,
  ] = useState<User | null>(null);

  const [
    cart,
    setCart,
  ] = useState<Cart | null>(null);

  const [
    wishlist,
    setWishlist,
  ] = useState<WishlistItem[]>([]);

  const [
    loadingUser,
    setLoadingUser,
  ] = useState(true);

  async function loadUserData() {
    if (!isLoggedIn()) {
      setLoadingUser(false);
      return;
    }

    try {
      const [
        currentUser,
        currentCart,
        currentWishlist,
      ] = await Promise.all([
        getMe(),
        getCart(),
        getWishlist(),
      ]);

      setUser(currentUser);
      setCart(currentCart);
      setWishlist(currentWishlist);
    } catch {
      localStorage.removeItem(
        "book_worm_token"
      );

      setUser(null);
    } finally {
      setLoadingUser(false);
    }
  }


  useEffect(() => {
    void loadUserData();
  }, []);


  async function refreshCart() {
    if (!isLoggedIn()) {
      return;
    }

    const updatedCart =
      await getCart();

    setCart(updatedCart);
  }


  async function handleLogout() {
    localStorage.removeItem(
      "book_worm_token"
    );

    setUser(null);
    setCart(null);
    setWishlist([]);

    window.location.href = "/";
  }


  if (loadingUser) {
    return (
      <div className="page-center">
        Loading Book Worm...
      </div>
    );
  }


  return (
    <div className="app">
      <Header
        user={user}
        cartCount={
          cart?.items.reduce(
            (total, item) =>
              total + item.quantity,
            0
          ) || 0
        }
        wishlistCount={
          wishlist.length
        }
        onLogout={handleLogout}
      />

      <main>
        <Routes>
          <Route
            path="/"
            element={
              <HomePage
                onAddToCart={async (
                  bookId
                ) => {
                  if (!user) {
                    window.location.href =
                      "/login";
                    return;
                  }

                  const updated =
                    await addToCart(
                      bookId
                    );

                  setCart(updated);
                }}
              />
            }
          />

          <Route
            path="/login"
            element={
              <LoginPage
                onLogin={async (
                  email,
                  password
                ) => {
                  const result =
                    await login(
                      email,
                      password
                    );

                  localStorage.setItem(
                    "book_worm_token",
                    result.access_token
                  );

                  await loadUserData();

                  window.location.href =
                    "/";
                }}
              />
            }
          />

          <Route
            path="/register"
            element={
              <RegisterPage
                onRegister={async (
                  name,
                  email,
                  password
                ) => {
                  await register(
                    name,
                    email,
                    password
                  );

                  const result =
                    await login(
                      email,
                      password
                    );

                  localStorage.setItem(
                    "book_worm_token",
                    result.access_token
                  );

                  await loadUserData();

                  window.location.href =
                    "/";
                }}
              />
            }
          />

          <Route
            path="/books"
            element={
              <CataloguePage
                onAddToCart={async (
                  bookId
                ) => {
                  if (!user) {
                    window.location.href =
                      "/login";
                    return;
                  }

                  const updated =
                    await addToCart(
                      bookId
                    );

                  setCart(updated);
                }}
                wishlist={wishlist}
                onWishlist={async (
                  bookId
                ) => {
                  if (!user) {
                    window.location.href =
                      "/login";
                    return;
                  }

                  const existing =
                    wishlist.find(
                      (item) =>
                        item.book.id ===
                        bookId
                    );

                  if (existing) {
                    await removeFromWishlist(
                      bookId
                    );

                    setWishlist(
                      wishlist.filter(
                        (item) =>
                          item.book.id !==
                          bookId
                      )
                    );
                  } else {
                    const item =
                      await addToWishlist(
                        bookId
                      );

                    setWishlist([
                      ...wishlist,
                      item,
                    ]);
                  }
                }}
              />
            }
          />

          <Route
            path="/books/:bookId"
            element={
              <BookDetailsPage
                user={user}
                wishlist={wishlist}
                onAddToCart={async (
                  bookId
                ) => {
                  if (!user) {
                    window.location.href =
                      "/login";
                    return;
                  }

                  const updated =
                    await addToCart(
                      bookId
                    );

                  setCart(updated);
                }}
                onWishlist={async (
                  bookId
                ) => {
                  if (!user) {
                    window.location.href =
                      "/login";
                    return;
                  }

                  const existing =
                    wishlist.find(
                      (item) =>
                        item.book.id ===
                        bookId
                    );

                  if (existing) {
                    await removeFromWishlist(
                      bookId
                    );

                    setWishlist(
                      wishlist.filter(
                        (item) =>
                          item.book.id !==
                          bookId
                      )
                    );
                  } else {
                    const item =
                      await addToWishlist(
                        bookId
                      );

                    setWishlist([
                      ...wishlist,
                      item,
                    ]);
                  }
                }}
              />
            }
          />

          <Route
            path="/cart"
            element={
              <CartPage
                cart={cart}
                onRefresh={refreshCart}
              />
            }
          />

          <Route
            path="/checkout"
            element={
              <CheckoutPage
                user={user}
                cart={cart}
                onOrderCreated={async () => {
                  await refreshCart();

                  const updatedUser =
                    await getMe();

                  setUser(
                    updatedUser
                  );
                }}
              />
            }
          />

          <Route
            path="/orders"
            element={
              <OrdersPage
                onBuyAgain={async (
                  orderId
                ) => {
                  const updated =
                    await buyAgain(
                      orderId
                    );

                  setCart(updated);

                  window.location.href =
                    "/cart";
                }}
                onCancel={async (
                  orderId
                ) => {
                  await cancelOrder(
                    orderId
                  );

                  window.location.reload();
                }}
              />
            }
          />

          <Route
            path="/orders/:orderId"
            element={
              <OrderDetailsPage />
            }
          />

          <Route
            path="/wishlist"
            element={
              <WishlistPage
                wishlist={wishlist}
                onRemove={async (
                  bookId
                ) => {
                  await removeFromWishlist(
                    bookId
                  );

                  setWishlist(
                    wishlist.filter(
                      (item) =>
                        item.book.id !==
                        bookId
                    )
                  );
                }}
              />
            }
          />

          <Route
            path="/recommendations"
            element={
              <RecommendationsPage />
            }
          />
        </Routes>
      </main>

      <Footer />
    </div>
  );
}


// ============================================================
// HEADER
// ============================================================

function Header({
  user,
  cartCount,
  wishlistCount,
  onLogout,
}: {
  user: User | null;
  cartCount: number;
  wishlistCount: number;
  onLogout: () => void;
}) {
  return (
    <header className="header">
      <div className="header-inner">
        <Link
          to="/"
          className="logo"
        >
          📚 Book Worm
        </Link>

        <nav className="nav">
          <Link to="/books">
            Catalogue
          </Link>

          <Link to="/recommendations">
            Recommendations
          </Link>

          {user && (
            <>
              <Link to="/wishlist">
                Wishlist
                {wishlistCount > 0 && (
                  <span className="badge">
                    {wishlistCount}
                  </span>
                )}
              </Link>

              <Link to="/orders">
                Orders
              </Link>

              <Link to="/cart">
                Cart
                {cartCount > 0 && (
                  <span className="badge">
                    {cartCount}
                  </span>
                )}
              </Link>
            </>
          )}

          {user ? (
            <>
              <span className="user-name">
                {user.name}
              </span>

              <button
                className="link-button"
                onClick={onLogout}
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login">
                Login
              </Link>

              <Link
                to="/register"
                className="nav-button"
              >
                Register
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}


// ============================================================
// HOME
// ============================================================

function HomePage({
  onAddToCart,
}: {
  onAddToCart: (
    bookId: number
  ) => Promise<void>;
}) {
  const [
    books,
    setBooks,
  ] = useState<Book[]>([]);

  const [
    loading,
    setLoading,
  ] = useState(true);

  useEffect(() => {
    getBooks()
      .then(setBooks)
      .finally(() => setLoading(false));
  }, []);

  const featured =
    books.slice(0, 6);

  return (
    <>
      <section className="hero">
        <div className="hero-content">
          <span className="eyebrow">
            DISCOVER YOUR NEXT STORY
          </span>

          <h1>
            Books that stay
            <br />
            with you.
          </h1>

          <p>
            Discover books across
            programming, business,
            fiction and more.
          </p>

          <Link
            to="/books"
            className="primary-button"
          >
            Explore Catalogue
          </Link>
        </div>
      </section>

      <section className="section">
        <div className="section-heading">
          <div>
            <span className="eyebrow">
              BOOK WORM
            </span>

            <h2>
              Featured Books
            </h2>
          </div>

          <Link to="/books">
            View all →
          </Link>
        </div>

        {loading ? (
          <Loading />
        ) : (
          <div className="book-grid">
            {featured.map((book) => (
              <BookCard
                key={book.id}
                book={book}
                onAddToCart={
                  onAddToCart
                }
              />
            ))}
          </div>
        )}
      </section>
    </>
  );
}


// ============================================================
// CATALOGUE
// ============================================================

function CataloguePage({
  onAddToCart,
  wishlist,
  onWishlist,
}: {
  onAddToCart: (
    bookId: number
  ) => Promise<void>;

  wishlist: WishlistItem[];

  onWishlist: (
    bookId: number
  ) => Promise<void>;
}) {
  const [
    books,
    setBooks,
  ] = useState<Book[]>([]);

  const [
    categories,
    setCategories,
  ] = useState<Category[]>([]);

  const [
    search,
    setSearch,
  ] = useState("");

  const [
    categoryId,
    setCategoryId,
  ] = useState<number | undefined>();

  const [
    loading,
    setLoading,
  ] = useState(true);

  useEffect(() => {
    getCategories().then(
      setCategories
    );
  }, []);

  useEffect(() => {
    async function fetchBooks() {
      setLoading(true);

      try {
        const result = await getBooks({
          search: search || undefined,
          category_id: categoryId,
        });
        setBooks(result);
      } finally {
        setLoading(false);
      }
    }

    void fetchBooks();
  }, [search, categoryId]);

  return (
    <section className="section">
      <div className="page-title">
        <span className="eyebrow">
          SHOP
        </span>

        <h1>Catalogue</h1>

        <p>
          Browse our collection of
          books.
        </p>
      </div>

      <div className="catalogue-toolbar">
        <input
          value={search}
          onChange={(event) =>
            setSearch(
              event.target.value
            )
          }
          placeholder="Search books..."
        />

        <select
          value={
            categoryId ?? ""
          }
          onChange={(event) =>
            setCategoryId(
              event.target.value
                ? Number(
                    event.target.value
                  )
                : undefined
            )
          }
        >
          <option value="">
            All categories
          </option>

          {categories.map(
            (category) => (
              <option
                key={category.id}
                value={category.id}
              >
                {category.name}
              </option>
            )
          )}
        </select>
      </div>

      {loading ? (
        <Loading />
      ) : books.length === 0 ? (
        <EmptyState
          title="No books found"
          text="Try a different search."
        />
      ) : (
        <div className="book-grid">
          {books.map((book) => (
            <BookCard
              key={book.id}
              book={book}
              onAddToCart={
                onAddToCart
              }
              wishlistActive={wishlist.some(
                (item) =>
                  item.book.id ===
                  book.id
              )}
              onWishlist={
                onWishlist
              }
            />
          ))}
        </div>
      )}
    </section>
  );
}


// ============================================================
// BOOK CARD
// ============================================================

function BookCard({
  book,
  onAddToCart,
  wishlistActive = false,
  onWishlist,
}: {
  book: Book;
  onAddToCart: (
    bookId: number
  ) => Promise<void>;

  wishlistActive?: boolean;

  onWishlist?: (
    bookId: number
  ) => Promise<void>;
}) {
  const [
    adding,
    setAdding,
  ] = useState(false);

  async function handleAdd() {
    try {
      setAdding(true);

      await onAddToCart(
        book.id
      );
    } finally {
      setAdding(false);
    }
  }

  return (
    <article className="book-card">
      <Link
        to={`/books/${book.id}`}
        className="book-cover"
      >
        {book.cover_image_url ? (
          <img
            src={book.cover_image_url}
            alt={book.title}
          />
        ) : (
          <div className="cover-placeholder">
            📖
          </div>
        )}
      </Link>

      <div className="book-card-body">
        <div className="book-rating">
          ★{" "}
          {Number(
            book.average_rating
          ).toFixed(1)}
        </div>

        <Link
          to={`/books/${book.id}`}
          className="book-title"
        >
          {book.title}
        </Link>

        <p className="book-author">
          {book.author.name}
        </p>

        <div className="book-card-bottom">
          <strong>
            {money(book.price)}
          </strong>

          <div className="card-actions">
            {onWishlist && (
              <button
                className={`icon-button ${
                  wishlistActive
                    ? "active"
                    : ""
                }`}
                onClick={() =>
                  onWishlist(
                    book.id
                  )
                }
                title="Wishlist"
              >
                ♥
              </button>
            )}

            <button
              className="small-button"
              onClick={handleAdd}
              disabled={
                adding ||
                book.stock_quantity <=
                  0
              }
            >
              {book.stock_quantity <=
              0
                ? "Out of stock"
                : adding
                ? "Adding..."
                : "Add to cart"}
            </button>
          </div>
        </div>
      </div>
    </article>
  );
}


// ============================================================
// BOOK DETAILS
// ============================================================

function BookDetailsPage({
  user,
  wishlist,
  onAddToCart,
  onWishlist,
}: {
  user: User | null;

  wishlist: WishlistItem[];

  onAddToCart: (
    bookId: number
  ) => Promise<void>;

  onWishlist: (
    bookId: number
  ) => Promise<void>;
}) {
  const { bookId } =
    useParams();

  const [
    book,
    setBook,
  ] = useState<Book | null>(null);

  const [
    reviews,
    setReviews,
  ] = useState<Review[]>([]);

  const [
    related,
    setRelated,
  ] =
    useState<RelatedBooksResponse | null>(
      null
    );

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState("");

  const [
    rating,
    setRating,
  ] = useState(5);

  const [
    comment,
    setComment,
  ] = useState("");

  const navigate =
    useNavigate();

  useEffect(() => {
    const id = Number(
      bookId
    );

    if (!id) {
      return;
    }

    Promise.all([
      getBook(id),
      getReviews(id),
      getRelatedBooks(id),
    ])
      .then(
        ([
          bookData,
          reviewData,
          relatedData,
        ]) => {
          setBook(bookData);
          setReviews(
            reviewData
          );
          setRelated(
            relatedData
          );
        }
      )
      .catch((err) => {
        setError(
          err.message
        );
      })
      .finally(() => {
        setLoading(false);
      });
  }, [bookId]);

  if (loading) {
    return <Loading />;
  }

  if (error || !book) {
    return (
      <EmptyState
        title="Book not found"
        text={
          error ||
          "Unable to load this book."
        }
      />
    );
  }

  const wishlisted =
    wishlist.some(
      (item) =>
        item.book.id ===
        book.id
    );

  async function submitReview() {
    if (!book) return;

    if (!user) {
      navigate("/login");
      return;
    }

    try {
      const review =
        await createReview(
          book.id,
          rating,
          comment
        );

      setReviews([
        review,
        ...reviews,
      ]);

      setComment("");

      const updatedBook =
        await getBook(
          book.id
        );

      setBook(updatedBook);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to submit review"
      );
    }
  }

  return (
    <section className="section">
      <div className="product-layout">
        <div className="product-image">
          {book.cover_image_url ? (
            <img
              src={
                book.cover_image_url
              }
              alt={book.title}
            />
          ) : (
            <div className="large-cover-placeholder">
              📖
            </div>
          )}
        </div>

        <div className="product-info">
          <div className="book-rating large">
            ★{" "}
            {Number(
              book.average_rating
            ).toFixed(1)}
          </div>

          <h1>{book.title}</h1>

          <p className="product-author">
            By{" "}
            <strong>
              {book.author.name}
            </strong>
          </p>

          <p className="product-description">
            {book.description}
          </p>

          <div className="product-meta">
            <span>
              Publisher:{" "}
              {book.publisher.name}
            </span>

            <span>
              Format:{" "}
              {book.format}
            </span>

            <span>
              Language:{" "}
              {book.language}
            </span>
          </div>

          <div className="product-price">
            {money(book.price)}
          </div>

          {book.delivery_date && (
            <p className="delivery">
              Estimated delivery:{" "}
              {book.delivery_date}
            </p>
          )}

          <div className="product-actions">
            <button
              className="primary-button"
              onClick={() =>
                onAddToCart(
                  book.id
                )
              }
              disabled={
                book.stock_quantity <=
                0
              }
            >
              {book.stock_quantity <=
              0
                ? "Out of stock"
                : "Add to cart"}
            </button>

            <button
              className={`secondary-button ${
                wishlisted
                  ? "active"
                  : ""
              }`}
              onClick={() =>
                onWishlist(
                  book.id
                )
              }
            >
              {wishlisted
                ? "♥ Wishlisted"
                : "♡ Wishlist"}
            </button>
          </div>
        </div>
      </div>

      <div className="content-section">
        <div className="section-heading">
          <div>
            <span className="eyebrow">
              CUSTOMER FEEDBACK
            </span>

            <h2>Reviews</h2>
          </div>
        </div>

        {user && (
          <div className="review-form">
            <h3>
              Write a review
            </h3>

            <select
              value={rating}
              onChange={(event) =>
                setRating(
                  Number(
                    event.target.value
                  )
                )
              }
            >
              <option value="5">
                5 - Excellent
              </option>
              <option value="4">
                4 - Good
              </option>
              <option value="3">
                3 - Average
              </option>
              <option value="2">
                2 - Poor
              </option>
              <option value="1">
                1 - Bad
              </option>
            </select>

            <textarea
              value={comment}
              onChange={(event) =>
                setComment(
                  event.target.value
                )
              }
              placeholder="Share your experience..."
              rows={4}
            />

            <button
              className="primary-button"
              onClick={
                submitReview
              }
            >
              Submit Review
            </button>
          </div>
        )}

        {reviews.length === 0 ? (
          <p className="muted">
            No reviews yet.
          </p>
        ) : (
          <div className="reviews">
            {reviews.map(
              (review) => (
                <div
                  className="review"
                  key={review.id}
                >
                  <div className="review-header">
                    <strong>
                      {
                        review.user_name
                      }
                    </strong>

                    <span>
                      {"★".repeat(
                        review.rating
                      )}
                    </span>
                  </div>

                  <p>
                    {review.comment}
                  </p>
                </div>
              )
            )}
          </div>
        )}
      </div>

      {related &&
        related.books.length >
          0 && (
          <div className="content-section">
            <div className="section-heading">
              <h2>
                Related Books
              </h2>
            </div>

            <div className="book-grid">
              {related.books.map(
                (summary) => (
                  <Link
                    key={
                      summary.id
                    }
                    to={`/books/${summary.id}`}
                    className="book-card"
                  >
                    <div className="book-cover">
                      {summary.cover_image_url ? (
                        <img
                          src={
                            summary.cover_image_url
                          }
                          alt={
                            summary.title
                          }
                        />
                      ) : (
                        <div className="cover-placeholder">
                          📖
                        </div>
                      )}
                    </div>

                    <div className="book-card-body">
                      <div className="book-rating">
                        ★{" "}
                        {Number(
                          summary.average_rating
                        ).toFixed(1)}
                      </div>

                      <div className="book-title">
                        {
                          summary.title
                        }
                      </div>

                      <strong>
                        {money(
                          summary.price
                        )}
                      </strong>
                    </div>
                  </Link>
                )
              )}
            </div>
          </div>
        )}
    </section>
  );
}


// ============================================================
// CART
// ============================================================

function CartPage({
  cart,
  onRefresh,
}: {
  cart: Cart | null;

  onRefresh: () => Promise<void>;
}) {
  const navigate =
    useNavigate();

  if (!isLoggedIn()) {
    return (
      <EmptyState
        title="Please login"
        text="Login to view your cart."
        action={
          <Link
            to="/login"
            className="primary-button"
          >
            Login
          </Link>
        }
      />
    );
  }

  if (!cart) {
    return <Loading />;
  }

  async function changeQuantity(
    itemId: number,
    quantity: number
  ) {
    if (quantity < 1) {
      return;
    }

    await updateCartItem(
      itemId,
      quantity
    );

    await onRefresh();
  }

  async function remove(
    itemId: number
  ) {
    await removeCartItem(
      itemId
    );

    await onRefresh();
  }

  return (
    <section className="section narrow">
      <div className="page-title">
        <span className="eyebrow">
          YOUR BAG
        </span>

        <h1>Shopping Cart</h1>
      </div>

      {cart.items.length === 0 ? (
        <EmptyState
          title="Your cart is empty"
          text="Add some books to continue."
          action={
            <Link
              to="/books"
              className="primary-button"
            >
              Browse Books
            </Link>
          }
        />
      ) : (
        <>
          <div className="cart-list">
            {cart.items.map(
              (item) => (
                <div
                  className="cart-item"
                  key={item.id}
                >
                  <div className="cart-image">
                    {item.book
                      .cover_image_url ? (
                      <img
                        src={
                          item.book
                            .cover_image_url
                        }
                        alt={
                          item.book.title
                        }
                      />
                    ) : (
                      "📖"
                    )}
                  </div>

                  <div className="cart-details">
                    <Link
                      to={`/books/${item.book.id}`}
                    >
                      <h3>
                        {
                          item.book.title
                        }
                      </h3>
                    </Link>

                    <p>
                      {money(
                        item.book.price
                      )}
                    </p>

                    <div className="quantity">
                      <button
                        onClick={() =>
                          changeQuantity(
                            item.id,
                            item.quantity -
                              1
                          )
                        }
                        disabled={
                          item.quantity <=
                          1
                        }
                      >
                        −
                      </button>

                      <span>
                        {
                          item.quantity
                        }
                      </span>

                      <button
                        onClick={() =>
                          changeQuantity(
                            item.id,
                            item.quantity +
                              1
                          )
                        }
                      >
                        +
                      </button>
                    </div>
                  </div>

                  <div className="cart-total">
                    <strong>
                      {money(
                        item.item_total
                      )}
                    </strong>

                    <button
                      className="danger-button"
                      onClick={() =>
                        remove(
                          item.id
                        )
                      }
                    >
                      Remove
                    </button>
                  </div>
                </div>
              )
            )}
          </div>

          <div className="checkout-summary">
            <div>
              <span>
                Subtotal
              </span>

              <strong>
                {money(
                  cart.subtotal
                )}
              </strong>
            </div>

            <button
              className="primary-button full"
              onClick={() =>
                navigate(
                  "/checkout"
                )
              }
            >
              Proceed to Checkout
            </button>
          </div>
        </>
      )}
    </section>
  );
}


// ============================================================
// CHECKOUT
// ============================================================

function CheckoutPage({
  user,
  cart,
  onOrderCreated,
}: {
  user: User | null;
  cart: Cart | null;

  onOrderCreated: () => Promise<void>;
}) {
  const navigate =
    useNavigate();

  const [
    addresses,
    setAddresses,
  ] = useState<Address[]>([]);

  const [
    selectedAddress,
    setSelectedAddress,
  ] = useState<number | null>(
    null
  );

  const [
    giftPoints,
    setGiftPoints,
  ] = useState(0);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    purchasing,
    setPurchasing,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState("");

  const [
    showAddressForm,
    setShowAddressForm,
  ] = useState(false);

  const [
    addressForm,
    setAddressForm,
  ] = useState({
    full_name: "",
    phone: "",
    address_line1: "",
    address_line2: "",
    city: "",
    state: "",
    postal_code: "",
    country: "India",
    is_default: false,
  });

  useEffect(() => {
    if (!user) {
      navigate("/login");
      return;
    }

    getAddresses()
      .then((data) => {
        setAddresses(data);

        const defaultAddress =
          data.find(
            (address) =>
              address.is_default
          );

        if (defaultAddress) {
          setSelectedAddress(
            defaultAddress.id
          );
        }
      })
      .finally(() =>
        setLoading(false)
      );
  }, [user, navigate]);

  if (!user || loading) {
    return <Loading />;
  }

  if (!cart || cart.items.length === 0) {
    return (
      <EmptyState
        title="Your cart is empty"
        text="Add books before checkout."
        action={
          <Link
            to="/books"
            className="primary-button"
          >
            Browse Books
          </Link>
        }
      />
    );
  }

  async function addAddress() {
    try {
      const address =
        await createAddress(
          addressForm
        );

      setAddresses([
        ...addresses,
        address,
      ]);

      setSelectedAddress(
        address.id
      );

      setShowAddressForm(
        false
      );

      setAddressForm({
        full_name: "",
        phone: "",
        address_line1: "",
        address_line2: "",
        city: "",
        state: "",
        postal_code: "",
        country: "India",
        is_default: false,
      });
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to add address"
      );
    }
  }


  async function purchase() {
    if (!selectedAddress) {
      setError(
        "Please select a delivery address."
      );
      return;
    }

    try {
      setPurchasing(true);
      setError("");

      const order =
        await createOrder(
          selectedAddress,
          giftPoints
        );

      await onOrderCreated();

      navigate(
        `/orders/${order.id}`
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Purchase failed"
      );
    } finally {
      setPurchasing(false);
    }
  }

  const subtotal = Number(cart.subtotal);

  const tax = subtotal * 0.18;

  const delivery = subtotal < 500 ? 40 : 0;

  const discount = giftPoints;

  const total = Math.max(
    0,
    subtotal + tax + delivery - discount
  );

  return (
    <section className="section narrow">
      <div className="page-title">
        <span className="eyebrow">
          CHECKOUT
        </span>

        <h1>Complete Purchase</h1>
      </div>

      {error && (
        <div className="error">
          {error}
        </div>
      )}

      <div className="checkout-layout">
        <div>
          <div className="checkout-card">
            <div className="card-heading">
              <h2>
                Delivery Address
              </h2>

              <button
                className="text-button"
                onClick={() =>
                  setShowAddressForm(
                    !showAddressForm
                  )
                }
              >
                + Add address
              </button>
            </div>

            {addresses.length ===
              0 &&
              !showAddressForm && (
                <p className="muted">
                  No address saved.
                </p>
              )}

            <div className="address-list">
              {addresses.map(
                (address) => (
                  <label
                    className={`address-card ${
                      selectedAddress ===
                      address.id
                        ? "selected"
                        : ""
                    }`}
                    key={
                      address.id
                    }
                  >
                    <input
                      type="radio"
                      name="address"
                      checked={
                        selectedAddress ===
                        address.id
                      }
                      onChange={() =>
                        setSelectedAddress(
                          address.id
                        )
                      }
                    />

                    <div>
                      <strong>
                        {
                          address.full_name
                        }
                      </strong>

                      <p>
                        {
                          address.address_line1
                        }

                        {address.address_line2 &&
                          `, ${address.address_line2}`}
                      </p>

                      <p>
                        {
                          address.city
                        }
                        ,{" "}
                        {
                          address.state
                        }{" "}
                        {
                          address.postal_code
                        }
                      </p>

                      <p>
                        {
                          address.phone
                        }
                      </p>
                    </div>
                  </label>
                )
              )}
            </div>

            {showAddressForm && (
              <div className="form-grid">
                {Object.entries(
                  addressForm
                ).map(
                  ([
                    key,
                    value,
                  ]) => {
                    if (
                      key ===
                      "is_default"
                    ) {
                      return null;
                    }

                    return (
                      <input
                        key={key}
                        placeholder={key.replaceAll(
                          "_",
                          " "
                        )}
                        value={
                          value as string
                        }
                        onChange={(
                          event
                        ) =>
                          setAddressForm(
                            {
                              ...addressForm,
                              [key]:
                                event
                                  .target
                                  .value,
                            }
                          )
                        }
                      />
                    );
                  }
                )}

                <button
                  className="primary-button"
                  onClick={
                    addAddress
                  }
                >
                  Save Address
                </button>
              </div>
            )}
          </div>

          <div className="checkout-card">
            <h2>
              Gift Points
            </h2>

            <p className="muted">
              Available:
              {" "}
              {user.gift_points_balance}
              {" "}
              points
            </p>

            <input
              type="number"
              min="0"
              max={
                user.gift_points_balance
              }
              value={giftPoints}
              onChange={(event) =>
                setGiftPoints(
                  Math.min(
                    user.gift_points_balance,
                    Math.max(
                      0,
                      Number(
                        event.target
                          .value
                      )
                    )
                  )
                )
              }
            />

            <small>
              1 gift point =
              ₹1 discount
            </small>
          </div>

          <div className="checkout-card">
            <h2>
              Payment
            </h2>

            <div className="mock-payment">
              <div className="payment-icon">
                ✓
              </div>

              <div>
                <strong>
                  Demo Payment
                </strong>

                <p>
                  Payment gateway will
                  be integrated later.
                </p>
              </div>
            </div>
          </div>
        </div>

        <aside className="order-summary">
          <h2>
            Order Summary
          </h2>

          {cart.items.map(
            (item) => (
              <div
                className="summary-line"
                key={item.id}
              >
                <span>
                  {item.book.title}
                  {" "}
                  ×{" "}
                  {item.quantity}
                </span>

                <strong>
                  {money(
                    item.item_total
                  )}
                </strong>
              </div>
            )
          )}

          <hr />

          <div className="summary-line">
            <span>
              Subtotal
            </span>

            <span>
              {money(
                cart.subtotal
              )}
            </span>
          </div>

          <div className="summary-line">
            <span>
              Tax
            </span>

            <span>
              {money(tax)}
            </span>
          </div>

          <div className="summary-line">
            <span>
              Delivery
            </span>

            <span>
              {money(delivery)}
            </span>
          </div>

          {giftPoints > 0 && (
            <div className="summary-line discount">
              <span>
                Gift points
              </span>

              <span>
                -{money(discount)}
              </span>
            </div>
          )}

          <hr />

          <div className="summary-total">
            <span>
              Total
            </span>

            <strong>
              {money(total)}
            </strong>
          </div>

          <button
            className="primary-button full"
            onClick={purchase}
            disabled={
              purchasing ||
              !selectedAddress
            }
          >
            {purchasing
              ? "Processing..."
              : "Confirm Purchase"}
          </button>
        </aside>
      </div>
    </section>
  );
}


// ============================================================
// ORDERS
// ============================================================

function OrdersPage({
  onBuyAgain,
  onCancel,
}: {
  onBuyAgain: (
    orderId: number
  ) => Promise<void>;

  onCancel: (
    orderId: number
  ) => Promise<void>;
}) {
  const [
    orders,
    setOrders,
  ] = useState<Order[]>([]);

  const [
    loading,
    setLoading,
  ] = useState(true);

  useEffect(() => {
    if (!isLoggedIn()) {
      return;
    }

    getOrders()
      .then(setOrders)
      .finally(() => setLoading(false));
  }, []);

  if (!isLoggedIn()) {
    return (
      <EmptyState
        title="Please login"
        text="Login to view your orders."
        action={
          <Link
            to="/login"
            className="primary-button"
          >
            Login
          </Link>
        }
      />
    );
  }

  if (loading) {
    return <Loading />;
  }

  return (
    <section className="section narrow">
      <div className="page-title">
        <span className="eyebrow">
          ACCOUNT
        </span>

        <h1>My Orders</h1>
      </div>

      {orders.length === 0 ? (
        <EmptyState
          title="No orders yet"
          text="Your purchases will appear here."
        />
      ) : (
        <div className="orders">
          {orders.map(
            (order) => (
              <div
                className="order-card"
                key={order.id}
              >
                <div className="order-header">
                  <div>
                    <strong>
                      Order #
                      {order.id}
                    </strong>

                    <span>
                      {new Date(
                        order.created_at
                      ).toLocaleDateString()}
                    </span>
                  </div>

                  <span
                    className={`status ${order.status.toLowerCase()}`}
                  >
                    {order.status}
                  </span>
                </div>

                <div className="order-items">
                  {order.items.map(
                    (item) => (
                      <div
                        key={
                          item.id
                        }
                      >
                        <span>
                          {
                            item.book_title
                          }
                          {" "}
                          ×{" "}
                          {
                            item.quantity
                          }
                        </span>

                        <strong>
                          {money(
                            item.total_price
                          )}
                        </strong>
                      </div>
                    )
                  )}
                </div>

                <div className="order-footer">
                  <strong>
                    Total{" "}
                    {money(
                      order.total_amount
                    )}
                  </strong>

                  <div className="button-row">
                    <Link
                      to={`/orders/${order.id}`}
                      className="secondary-button"
                    >
                      View
                    </Link>

                    <button
                      className="secondary-button"
                      onClick={() =>
                        onBuyAgain(
                          order.id
                        )
                      }
                    >
                      Buy Again
                    </button>

                    {order.status !==
                      "CANCELLED" && (
                      <button
                        className="danger-button"
                        onClick={() =>
                          onCancel(
                            order.id
                          )
                        }
                      >
                        Cancel
                      </button>
                    )}
                  </div>
                </div>
              </div>
            )
          )}
        </div>
      )}
    </section>
  );
}


// ============================================================
// ORDER DETAILS
// ============================================================

function OrderDetailsPage() {
  const { orderId } =
    useParams();

  const [
    order,
    setOrder,
  ] = useState<Order | null>(null);

  const [
    loading,
    setLoading,
  ] = useState(true);

  useEffect(() => {
    getOrder(
      Number(orderId)
    )
      .then(setOrder)
      .finally(() => setLoading(false));
  }, [orderId]);

  if (loading) {
    return <Loading />;
  }

  if (!order) {
    return (
      <EmptyState
        title="Order not found"
        text="Unable to load the order."
      />
    );
  }

  return (
    <section className="section narrow">
      <div className="page-title">
        <span className="eyebrow">
          PURCHASE
        </span>

        <h1>
          Order #{order.id}
        </h1>

        <p>
          Thank you for your
          purchase.
        </p>
      </div>

      <div className="success-banner">
        <span>✓</span>

        <div>
          <strong>
            Purchase confirmed
          </strong>

          <p>
            Your order has been
            successfully placed.
          </p>
        </div>
      </div>

      <div className="order-card">
        <div className="order-header">
          <div>
            <strong>
              Status
            </strong>

            <span>
              {order.status}
            </span>
          </div>

          {order.payment && (
            <div>
              <strong>
                Payment
              </strong>

              <span>
                {
                  order.payment
                    .status
                }
              </span>
            </div>
          )}
        </div>

        <div className="order-items">
          {order.items.map(
            (item) => (
              <div
                key={item.id}
              >
                <span>
                  {item.book_title}
                  {" "}
                  ×{" "}
                  {item.quantity}
                </span>

                <strong>
                  {money(
                    item.total_price
                  )}
                </strong>
              </div>
            )
          )}
        </div>

        <div className="summary-box">
          <div>
            Subtotal
            <span>
              {money(
                order.subtotal
              )}
            </span>
          </div>

          <div>
            Tax
            <span>
              {money(
                order.tax
              )}
            </span>
          </div>

          <div>
            Delivery
            <span>
              {money(
                order.delivery_charge
              )}
            </span>
          </div>

          <div>
            Discount
            <span>
              -{money(
                order.discount
              )}
            </span>
          </div>

          <div className="total">
            Total
            <strong>
              {money(
                order.total_amount
              )}
            </strong>
          </div>
        </div>

        <div className="shipping">
          <h3>
            Delivery Address
          </h3>

          <p>
            {
              order.shipping_full_name
            }
          </p>

          <p>
            {
              order.shipping_address_line1
            }

            {order.shipping_address_line2 &&
              `, ${order.shipping_address_line2}`}
          </p>

          <p>
            {
              order.shipping_city
            }
            ,{" "}
            {
              order.shipping_state
            }{" "}
            {
              order.shipping_postal_code
            }
          </p>

          <p>
            {
              order.shipping_phone
            }
          </p>
        </div>
      </div>

      <div className="center-actions">
        <Link
          to="/orders"
          className="secondary-button"
        >
          Back to Orders
        </Link>

        <Link
          to="/books"
          className="primary-button"
        >
          Continue Shopping
        </Link>
      </div>
    </section>
  );
}


// ============================================================
// WISHLIST
// ============================================================

function WishlistPage({
  wishlist,
  onRemove,
}: {
  wishlist: WishlistItem[];

  onRemove: (
    bookId: number
  ) => Promise<void>;
}) {
  return (
    <section className="section">
      <div className="page-title">
        <span className="eyebrow">
          SAVED
        </span>

        <h1>Wishlist</h1>
      </div>

      {wishlist.length === 0 ? (
        <EmptyState
          title="Your wishlist is empty"
          text="Save books you want to read later."
          action={
            <Link
              to="/books"
              className="primary-button"
            >
              Browse Books
            </Link>
          }
        />
      ) : (
        <div className="book-grid">
          {wishlist.map(
            (item) => (
              <article
                className="book-card"
                key={item.id}
              >
                <Link
                  to={`/books/${item.book.id}`}
                  className="book-cover"
                >
                  {item.book
                    .cover_image_url ? (
                    <img
                      src={
                        item.book
                          .cover_image_url
                      }
                      alt={
                        item.book
                          .title
                      }
                    />
                  ) : (
                    <div className="cover-placeholder">
                      📖
                    </div>
                  )}
                </Link>

                <div className="book-card-body">
                  <div className="book-title">
                    {
                      item.book
                        .title
                    }
                  </div>

                  <strong>
                    {money(
                      item.book
                        .price
                    )}
                  </strong>

                  <button
                    className="danger-button"
                    onClick={() =>
                      onRemove(
                        item.book.id
                      )
                    }
                  >
                    Remove
                  </button>
                </div>
              </article>
            )
          )}
        </div>
      )}
    </section>
  );
}


// ============================================================
// RECOMMENDATIONS
// ============================================================

function RecommendationsPage() {
  const [
    data,
    setData,
  ] =
    useState<RecommendationResponse | null>(
      null
    );

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState("");

  useEffect(() => {
    async function fetchRecommendations() {
      if (!isLoggedIn()) {
        setLoading(false);
        return;
      }

      try {
        const result = await getRecommendations();
        setData(result);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    }

    void fetchRecommendations();
  }, []);

  if (!isLoggedIn()) {
    return (
      <EmptyState
        title="Login to see recommendations"
        text="We'll recommend books based on your purchases."
        action={
          <Link
            to="/login"
            className="primary-button"
          >
            Login
          </Link>
        }
      />
    );
  }

  if (loading) {
    return <Loading />;
  }

  return (
    <section className="section">
      <div className="page-title">
        <span className="eyebrow">
          FOR YOU
        </span>

        <h1>
          Recommended Books
        </h1>

        <p>
          {data?.reason ||
            "Books selected for you."}
        </p>
      </div>

      {error && (
        <div className="error">
          {error}
        </div>
      )}

      {!data ||
      data.books.length ===
        0 ? (
        <EmptyState
          title="No recommendations yet"
          text="Purchase some books and we'll recommend similar books."
        />
      ) : (
        <div className="book-grid">
          {data.books.map(
            (book) => (
              <Link
                key={book.id}
                to={`/books/${book.id}`}
                className="book-card"
              >
                <div className="book-cover">
                  {book.cover_image_url ? (
                    <img
                      src={
                        book.cover_image_url
                      }
                      alt={
                        book.title
                      }
                    />
                  ) : (
                    <div className="cover-placeholder">
                      📖
                    </div>
                  )}
                </div>

                <div className="book-card-body">
                  <div className="book-rating">
                    ★{" "}
                    {Number(
                      book.average_rating
                    ).toFixed(1)}
                  </div>

                  <div className="book-title">
                    {
                      book.title
                    }
                  </div>

                  <strong>
                    {money(
                      book.price
                    )}
                  </strong>
                </div>
              </Link>
            )
          )}
        </div>
      )}
    </section>
  );
}


// ============================================================
// LOGIN
// ============================================================

function LoginPage({
  onLogin,
}: {
  onLogin: (
    email: string,
    password: string
  ) => Promise<void>;
}) {
  const [
    email,
    setEmail,
  ] = useState("");

  const [
    password,
    setPassword,
  ] = useState("");

  const [
    error,
    setError,
  ] = useState("");

  const [
    loading,
    setLoading,
  ] = useState(false);

  async function submit(
    event: React.FormEvent
  ) {
    event.preventDefault();

    try {
      setLoading(true);
      setError("");

      await onLogin(
        email,
        password
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Login failed"
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthPage
      title="Welcome back"
      subtitle="Login to continue shopping."
    >
      <form
        className="auth-form"
        onSubmit={submit}
      >
        {error && (
          <div className="error">
            {error}
          </div>
        )}

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(event) =>
            setEmail(
              event.target.value
            )
          }
          required
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(event) =>
            setPassword(
              event.target.value
            )
          }
          required
        />

        <button
          className="primary-button full"
          disabled={loading}
        >
          {loading
            ? "Logging in..."
            : "Login"}
        </button>

        <p className="auth-footer">
          Don't have an account?{" "}
          <Link to="/register">
            Register
          </Link>
        </p>
      </form>
    </AuthPage>
  );
}


// ============================================================
// REGISTER
// ============================================================

function RegisterPage({
  onRegister,
}: {
  onRegister: (
    name: string,
    email: string,
    password: string
  ) => Promise<void>;
}) {
  const [
    name,
    setName,
  ] = useState("");

  const [
    email,
    setEmail,
  ] = useState("");

  const [
    password,
    setPassword,
  ] = useState("");

  const [
    error,
    setError,
  ] = useState("");

  const [
    loading,
    setLoading,
  ] = useState(false);

  async function submit(
    event: React.FormEvent
  ) {
    event.preventDefault();

    try {
      setLoading(true);
      setError("");

      await onRegister(
        name,
        email,
        password
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Registration failed"
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthPage
      title="Create your account"
      subtitle="Start your Book Worm journey."
    >
      <form
        className="auth-form"
        onSubmit={submit}
      >
        {error && (
          <div className="error">
            {error}
          </div>
        )}

        <input
          placeholder="Full name"
          value={name}
          onChange={(event) =>
            setName(
              event.target.value
            )
          }
          required
        />

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(event) =>
            setEmail(
              event.target.value
            )
          }
          required
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(event) =>
            setPassword(
              event.target.value
            )
          }
          minLength={6}
          required
        />

        <button
          className="primary-button full"
          disabled={loading}
        >
          {loading
            ? "Creating..."
            : "Create Account"}
        </button>

        <p className="auth-footer">
          Already have an account?{" "}
          <Link to="/login">
            Login
          </Link>
        </p>
      </form>
    </AuthPage>
  );
}


// ============================================================
// AUTH PAGE
// ============================================================

function AuthPage({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle: string;
  children: React.ReactNode;
}) {
  return (
    <section className="auth-page">
      <div className="auth-card">
        <div className="auth-logo">
          📚
        </div>

        <h1>{title}</h1>

        <p>{subtitle}</p>

        {children}
      </div>
    </section>
  );
}


// ============================================================
// FOOTER
// ============================================================

function Footer() {
  return (
    <footer className="footer">
      <div>
        <strong>
          📚 Book Worm
        </strong>

        <p>
          Discover your next
          favourite book.
        </p>
      </div>

      <div>
        <p>
          © 2026 Book Worm
        </p>
      </div>
    </footer>
  );
}


// ============================================================
// COMMON UI
// ============================================================

function Loading() {
  return (
    <div className="page-center">
      <div className="spinner" />
      <p>
        Loading...
      </p>
    </div>
  );
}


function EmptyState({
  title,
  text,
  action,
}: {
  title: string;
  text: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="empty-state">
      <div className="empty-icon">
        📚
      </div>

      <h2>{title}</h2>

      <p>{text}</p>

      {action}
    </div>
  );
}