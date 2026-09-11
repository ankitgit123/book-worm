export interface User {
  id: number;
  name: string;
  email: string;
  gift_points_balance: number;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface Author {
  id: number;
  name: string;
  bio: string | null;
  photo_url: string | null;
}

export interface Publisher {
  id: number;
  name: string;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
}

export interface BookSummary {
  id: number;
  title: string;
  price: number;
  cover_image_url: string | null;
  average_rating: number;
  stock_quantity: number;
}

export interface Book extends BookSummary {
  description: string | null;
  author: Author;
  publisher: Publisher;
  format: string;
  language: string;
  delivery_date: string | null;
  sales_count: number;
  categories: Category[];
}

export interface CartItem {
  id: number;
  book: BookSummary;
  quantity: number;
  item_total: number;
}

export interface Cart {
  id: number;
  items: CartItem[];
  subtotal: number;
}

export interface Address {
  id: number;
  full_name: string;
  phone: string;
  address_line1: string;
  address_line2: string | null;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  is_default: boolean;
}

export interface Payment {
  id: number;
  order_id: number;
  method: string;
  amount: number;
  status: string;
  transaction_reference: string | null;
  paid_at: string | null;
  created_at: string;
}

export interface OrderItem {
  id: number;
  book_id: number;
  book_title: string;
  quantity: number;
  unit_price: number;
  total_price: number;
}

export interface Order {
  id: number;
  status: string;
  subtotal: number;
  tax: number;
  delivery_charge: number;
  discount: number;
  gift_points_used: number;
  total_amount: number;

  shipping_full_name: string;
  shipping_phone: string;
  shipping_address_line1: string;
  shipping_address_line2: string | null;
  shipping_city: string;
  shipping_state: string;
  shipping_postal_code: string;
  shipping_country: string;

  created_at: string;
  cancelled_at: string | null;

  items: OrderItem[];
  payment: Payment | null;
}

export interface Review {
  id: number;
  user_id: number;
  user_name: string;
  book_id: number;
  rating: number;
  comment: string | null;
  created_at: string;
  updated_at: string;
}

export interface WishlistItem {
  id: number;
  book: BookSummary;
  created_at: string;
}

export interface RecommendationResponse {
  reason: string;
  books: BookSummary[];
}

export interface RelatedBooksResponse {
  book_id: number;
  books: BookSummary[];
}