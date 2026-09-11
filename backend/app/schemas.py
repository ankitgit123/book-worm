from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# AUTH
# ============================================================

class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str
    password: str = Field(min_length=6, max_length=100)


class LoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    gift_points_balance: int

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


# ============================================================
# AUTHOR
# ============================================================

class AuthorCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    bio: str | None = None
    photo_url: str | None = None


class AuthorResponse(BaseModel):
    id: int
    name: str
    bio: str | None
    photo_url: str | None

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# PUBLISHER
# ============================================================

class PublisherCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)


class PublisherResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# CATEGORY
# ============================================================

class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    slug: str = Field(min_length=2, max_length=120)


class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# BOOK
# ============================================================

class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None

    author_id: int
    publisher_id: int

    format: str = Field(min_length=1, max_length=50)
    language: str = Field(min_length=1, max_length=50)

    price: Decimal = Field(gt=0)

    cover_image_url: str | None = None

    delivery_date: date | None = None

    stock_quantity: int = Field(ge=0)

    category_ids: list[int] = Field(default_factory=list)


class BookUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    description: str | None = None

    author_id: int | None = None
    publisher_id: int | None = None

    format: str | None = None
    language: str | None = None

    price: Decimal | None = Field(
        default=None,
        gt=0,
    )

    cover_image_url: str | None = None

    delivery_date: date | None = None

    stock_quantity: int | None = Field(
        default=None,
        ge=0,
    )

    category_ids: list[int] | None = None


class BookSummaryResponse(BaseModel):
    id: int
    title: str
    price: Decimal
    cover_image_url: str | None
    average_rating: Decimal
    stock_quantity: int

    model_config = ConfigDict(from_attributes=True)


class BookResponse(BaseModel):
    id: int
    title: str
    description: str | None

    author: AuthorResponse
    publisher: PublisherResponse

    format: str
    language: str

    price: Decimal

    cover_image_url: str | None
    delivery_date: date | None

    stock_quantity: int
    sales_count: int
    average_rating: Decimal

    categories: list[CategoryResponse]

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# CART
# ============================================================

class CartItemCreate(BaseModel):
    book_id: int
    quantity: int = Field(gt=0)


class CartItemUpdate(BaseModel):
    quantity: int = Field(gt=0)


class CartItemResponse(BaseModel):
    id: int
    book: BookSummaryResponse
    quantity: int
    item_total: Decimal


class CartResponse(BaseModel):
    id: int
    items: list[CartItemResponse]
    subtotal: Decimal


# ============================================================
# WISHLIST
# ============================================================

class WishlistCreate(BaseModel):
    book_id: int


class WishlistResponse(BaseModel):
    id: int
    book: BookSummaryResponse
    created_at: datetime


# ============================================================
# ADDRESS
# ============================================================

class AddressCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    address_line1: str = Field(
        min_length=1,
        max_length=255,
    )

    address_line2: str | None = None

    city: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=1, max_length=100)

    postal_code: str = Field(
        min_length=1,
        max_length=20,
    )

    country: str = Field(
        min_length=1,
        max_length=100,
    )

    is_default: bool = False


class AddressUpdate(BaseModel):
    full_name: str | None = None

    address_line1: str | None = None
    address_line2: str | None = None

    city: str | None = None
    state: str | None = None

    postal_code: str | None = None
    country: str | None = None

    is_default: bool | None = None


class AddressResponse(BaseModel):
    id: int
    full_name: str

    address_line1: str
    address_line2: str | None

    city: str
    state: str
    postal_code: str
    country: str

    is_default: bool

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# ORDER
# ============================================================

class OrderCreate(BaseModel):
    address_id: int
    gift_points_used: int = Field(
        default=0,
        ge=0,
    )


class OrderItemResponse(BaseModel):
    id: int
    book_id: int
    book_title: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    method: str
    amount: Decimal
    status: str
    transaction_reference: str | None
    paid_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: int
    status: str

    subtotal: Decimal
    tax: Decimal
    delivery_charge: Decimal
    discount: Decimal
    gift_points_used: int
    total_amount: Decimal

    shipping_full_name: str

    shipping_address_line1: str
    shipping_address_line2: str | None

    shipping_city: str
    shipping_state: str
    shipping_postal_code: str
    shipping_country: str

    created_at: datetime
    cancelled_at: datetime | None

    items: list[OrderItemResponse]

    payment: PaymentResponse | None

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# REVIEW
# ============================================================

class ReviewCreate(BaseModel):
    rating: int = Field(
        ge=1,
        le=5,
    )

    comment: str | None = Field(
        default=None,
        max_length=2000,
    )


class ReviewUpdate(BaseModel):
    rating: int = Field(
        ge=1,
        le=5,
    )

    comment: str | None = Field(
        default=None,
        max_length=2000,
    )


class ReviewResponse(BaseModel):
    id: int
    user_id: int
    user_name: str

    book_id: int

    rating: int
    comment: str | None

    created_at: datetime
    updated_at: datetime


# ============================================================
# RECOMMENDATIONS
# ============================================================

class RecommendationResponse(BaseModel):
    reason: str
    books: list[BookSummaryResponse]


# ============================================================
# RELATED BOOKS
# ============================================================

class RelatedBooksResponse(BaseModel):
    book_id: int
    books: list[BookSummaryResponse]