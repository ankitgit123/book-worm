import type {
  Address,
  Book,
  Cart,
  Category,
  LoginRequest,
  Order,
  RecommendationResponse,
  RelatedBooksResponse,
  Review,
  TokenResponse,
  User,
  WishlistItem,
} from "./types";

const API_URL =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000";

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = localStorage.getItem(
    "book_worm_token"
  );

  const headers = new Headers(
    options.headers
  );

  headers.set(
    "Content-Type",
    "application/json"
  );

  if (token) {
    headers.set(
      "Authorization",
      `Bearer ${token}`
    );
  }

  const response = await fetch(
    `${API_URL}${endpoint}`,
    {
      ...options,
      headers,
    }
  );

  const contentType =
    response.headers.get("content-type");

  const data =
    contentType?.includes("application/json")
      ? await response.json()
      : null;

  if (!response.ok) {
    const message =
      data?.detail ||
      `Request failed with status ${response.status}`;

    throw new Error(message);
  }

  return data as T;
}


// ============================================================
// AUTH
// ============================================================

export async function register(
  name: string,
  email: string,
  password: string
): Promise<User> {
  return request<User>(
    "/auth/register",
    {
      method: "POST",
      body: JSON.stringify({
        name,
        email,
        password,
      }),
    }
  );
}


export async function login(
  email: string,
  password: string
): Promise<TokenResponse> {
  return request<TokenResponse>(
    "/auth/login",
    {
      method: "POST",
      body: JSON.stringify({
        email,
        password,
      }),
    }
  );
}


export async function getMe(): Promise<User> {
  return request<User>("/auth/me");
}


// ============================================================
// BOOKS
// ============================================================

export async function getBooks(
  params: {
    category_id?: number;
    language?: string;
    format?: string;
    search?: string;
  } = {}
): Promise<Book[]> {
  const searchParams =
    new URLSearchParams();

  if (params.category_id) {
    searchParams.set(
      "category_id",
      String(params.category_id)
    );
  }

  if (params.language) {
    searchParams.set(
      "language",
      params.language
    );
  }

  if (params.format) {
    searchParams.set(
      "format",
      params.format
    );
  }

  if (params.search) {
    searchParams.set(
      "search",
      params.search
    );
  }

  const query =
    searchParams.toString();

  return request<Book[]>(
    `/books${query ? `?${query}` : ""}`
  );
}


export async function getBook(
  bookId: number
): Promise<Book> {
  return request<Book>(
    `/books/${bookId}`
  );
}


// ============================================================
// CATEGORIES
// ============================================================

export async function getCategories(): Promise<
  Category[]
> {
  return request<Category[]>(
    "/categories"
  );
}


// ============================================================
// CART
// ============================================================

export async function getCart(): Promise<Cart> {
  return request<Cart>("/cart");
}


export async function addToCart(
  bookId: number,
  quantity = 1
): Promise<Cart> {
  return request<Cart>(
    "/cart/items",
    {
      method: "POST",
      body: JSON.stringify({
        book_id: bookId,
        quantity,
      }),
    }
  );
}


export async function updateCartItem(
  itemId: number,
  quantity: number
): Promise<Cart> {
  return request<Cart>(
    `/cart/items/${itemId}`,
    {
      method: "PUT",
      body: JSON.stringify({
        quantity,
      }),
    }
  );
}


export async function removeCartItem(
  itemId: number
): Promise<Cart> {
  return request<Cart>(
    `/cart/items/${itemId}`,
    {
      method: "DELETE",
    }
  );
}


// ============================================================
// WISHLIST
// ============================================================

export async function getWishlist(): Promise<
  WishlistItem[]
> {
  return request<WishlistItem[]>(
    "/wishlist"
  );
}


export async function addToWishlist(
  bookId: number
): Promise<WishlistItem> {
  return request<WishlistItem>(
    "/wishlist",
    {
      method: "POST",
      body: JSON.stringify({
        book_id: bookId,
      }),
    }
  );
}


export async function removeFromWishlist(
  bookId: number
): Promise<void> {
  await request(
    `/wishlist/${bookId}`,
    {
      method: "DELETE",
    }
  );
}


// ============================================================
// ADDRESSES
// ============================================================

export async function getAddresses(): Promise<
  Address[]
> {
  return request<Address[]>(
    "/addresses"
  );
}


export async function createAddress(
  data: Omit<Address, "id">
): Promise<Address> {
  return request<Address>(
    "/addresses",
    {
      method: "POST",
      body: JSON.stringify(data),
    }
  );
}


// ============================================================
// ORDERS
// ============================================================

export async function createOrder(
  addressId: number,
  giftPointsUsed: number
): Promise<Order> {
  return request<Order>(
    "/orders",
    {
      method: "POST",
      body: JSON.stringify({
        address_id: addressId,
        gift_points_used:
          giftPointsUsed,
      }),
    }
  );
}


export async function getOrders(): Promise<
  Order[]
> {
  return request<Order[]>(
    "/orders"
  );
}


export async function getOrder(
  orderId: number
): Promise<Order> {
  return request<Order>(
    `/orders/${orderId}`
  );
}


export async function cancelOrder(
  orderId: number
): Promise<Order> {
  return request<Order>(
    `/orders/${orderId}/cancel`,
    {
      method: "POST",
    }
  );
}


export async function buyAgain(
  orderId: number
): Promise<Cart> {
  return request<Cart>(
    `/orders/${orderId}/buy-again`,
    {
      method: "POST",
    }
  );
}


// ============================================================
// REVIEWS
// ============================================================

export async function getReviews(
  bookId: number
): Promise<Review[]> {
  return request<Review[]>(
    `/books/${bookId}/reviews`
  );
}


export async function createReview(
  bookId: number,
  rating: number,
  comment: string
): Promise<Review> {
  return request<Review>(
    `/books/${bookId}/reviews`,
    {
      method: "POST",
      body: JSON.stringify({
        rating,
        comment,
      }),
    }
  );
}


export async function updateReview(
  reviewId: number,
  rating: number,
  comment: string
): Promise<Review> {
  return request<Review>(
    `/reviews/${reviewId}`,
    {
      method: "PUT",
      body: JSON.stringify({
        rating,
        comment,
      }),
    }
  );
}


export async function deleteReview(
  reviewId: number
): Promise<void> {
  await request(
    `/reviews/${reviewId}`,
    {
      method: "DELETE",
    }
  );
}


// ============================================================
// RECOMMENDATIONS
// ============================================================

export async function getRecommendations(): Promise<
  RecommendationResponse
> {
  return request<RecommendationResponse>(
    "/recommendations"
  );
}


export async function getRelatedBooks(
  bookId: number
): Promise<RelatedBooksResponse> {
  return request<RelatedBooksResponse>(
    `/books/${bookId}/related`
  );
}