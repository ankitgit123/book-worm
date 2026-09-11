from datetime import datetime, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import desc, func
from sqlalchemy.orm import Session, joinedload

from .database import get_db
from .models import (
    Address,
    Author,
    Book,
    BookCategory,
    Cart,
    CartItem,
    Category,
    Order,
    OrderItem,
    Payment,
    Publisher,
    Review,
    User,
    Wishlist,
)
from .schemas import (
    AddressCreate,
    AddressResponse,
    AddressUpdate,
    AuthorCreate,
    AuthorResponse,
    BookCreate,
    BookResponse,
    BookSummaryResponse,
    BookUpdate,
    CartItemCreate,
    CartItemResponse,
    CartItemUpdate,
    CartResponse,
    CategoryCreate,
    CategoryResponse,
    LoginRequest,
    OrderCreate,
    OrderItemResponse,
    OrderResponse,
    PaymentResponse,
    PublisherCreate,
    PublisherResponse,
    RecommendationResponse,
    RegisterRequest,
    RelatedBooksResponse,
    ReviewCreate,
    ReviewResponse,
    ReviewUpdate,
    TokenResponse,
    UserResponse,
    WishlistCreate,
    WishlistResponse,
)
from .services import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


router = APIRouter()

security = HTTPBearer()


# ============================================================
# AUTH
# ============================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials

    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = payload.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


@router.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db),
):
    existing_user = db.query(User).filter(
        User.email == data.email.lower()
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    user = User(
        name=data.name,
        email=data.email.lower(),
        password_hash=hash_password(data.password),
        gift_points_balance=0,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post(
    "/auth/login",
    response_model=TokenResponse,
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(
        User.email == data.email.lower()
    ).first()

    if not user or not verify_password(
        data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    token = create_access_token(
        {
            "user_id": user.id,
            "email": user.email,
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }


@router.get(
    "/auth/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


# ============================================================
# AUTHORS
# ============================================================

@router.post(
    "/authors",
    response_model=AuthorResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_author(
    data: AuthorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    author = Author(
        name=data.name,
        bio=data.bio,
        photo_url=data.photo_url,
    )

    db.add(author)
    db.commit()
    db.refresh(author)

    return author


@router.get(
    "/authors",
    response_model=list[AuthorResponse],
)
def get_authors(
    db: Session = Depends(get_db),
):
    return db.query(Author).order_by(
        Author.name.asc()
    ).all()


@router.get(
    "/authors/{author_id}",
    response_model=AuthorResponse,
)
def get_author(
    author_id: int,
    db: Session = Depends(get_db),
):
    author = db.query(Author).filter(
        Author.id == author_id
    ).first()

    if not author:
        raise HTTPException(
            status_code=404,
            detail="Author not found",
        )

    return author


# ============================================================
# PUBLISHERS
# ============================================================

@router.post(
    "/publishers",
    response_model=PublisherResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_publisher(
    data: PublisherCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = db.query(Publisher).filter(
        Publisher.name == data.name
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Publisher already exists",
        )

    publisher = Publisher(
        name=data.name,
    )

    db.add(publisher)
    db.commit()
    db.refresh(publisher)

    return publisher


@router.get(
    "/publishers",
    response_model=list[PublisherResponse],
)
def get_publishers(
    db: Session = Depends(get_db),
):
    return db.query(Publisher).order_by(
        Publisher.name.asc()
    ).all()


@router.get(
    "/publishers/{publisher_id}",
    response_model=PublisherResponse,
)
def get_publisher(
    publisher_id: int,
    db: Session = Depends(get_db),
):
    publisher = db.query(Publisher).filter(
        Publisher.id == publisher_id
    ).first()

    if not publisher:
        raise HTTPException(
            status_code=404,
            detail="Publisher not found",
        )

    return publisher


# ============================================================
# CATEGORIES
# ============================================================

@router.post(
    "/categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = db.query(Category).filter(
        (Category.name == data.name)
        | (Category.slug == data.slug)
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Category already exists",
        )

    category = Category(
        name=data.name,
        slug=data.slug,
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


@router.get(
    "/categories",
    response_model=list[CategoryResponse],
)
def get_categories(
    db: Session = Depends(get_db),
):
    return db.query(Category).order_by(
        Category.name.asc()
    ).all()


@router.get(
    "/categories/{category_id}",
    response_model=CategoryResponse,
)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
):
    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )

    return category


# ============================================================
# BOOK HELPERS
# ============================================================

def get_book_query(db: Session):
    return db.query(Book).options(
        joinedload(Book.author),
        joinedload(Book.publisher),
        joinedload(Book.book_categories)
        .joinedload(BookCategory.category),
    )


def get_book_or_404(
    book_id: int,
    db: Session,
):
    book = get_book_query(db).filter(
        Book.id == book_id
    ).first()

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found",
        )

    return book


# ============================================================
# BOOKS
# ============================================================

@router.post(
    "/books",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_book(
    data: BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    author = db.query(Author).filter(
        Author.id == data.author_id
    ).first()

    if not author:
        raise HTTPException(
            status_code=404,
            detail="Author not found",
        )

    publisher = db.query(Publisher).filter(
        Publisher.id == data.publisher_id
    ).first()

    if not publisher:
        raise HTTPException(
            status_code=404,
            detail="Publisher not found",
        )

    categories = []

    if data.category_ids:
        categories = db.query(Category).filter(
            Category.id.in_(data.category_ids)
        ).all()

        if len(categories) != len(set(data.category_ids)):
            raise HTTPException(
                status_code=400,
                detail="One or more categories not found",
            )

    book = Book(
        title=data.title,
        description=data.description,
        author_id=data.author_id,
        publisher_id=data.publisher_id,
        format=data.format,
        language=data.language,
        price=data.price,
        cover_image_url=data.cover_image_url,
        delivery_date=data.delivery_date,
        stock_quantity=data.stock_quantity,
        sales_count=0,
        average_rating=Decimal("0.00"),
        is_active=True,
    )

    db.add(book)
    db.flush()

    for category in categories:
        db.add(
            BookCategory(
                book_id=book.id,
                category_id=category.id,
            )
        )

    db.commit()

    return get_book_or_404(book.id, db)


@router.get(
    "/books",
    response_model=list[BookResponse],
)
def get_books(
    category_id: int | None = None,
    publisher_id: int | None = None,
    author_id: int | None = None,
    language: str | None = None,
    format: str | None = None,
    min_price: Decimal | None = Query(
        default=None,
        ge=0,
    ),
    max_price: Decimal | None = Query(
        default=None,
        ge=0,
    ),
    search: str | None = None,
    db: Session = Depends(get_db),
):
    query = get_book_query(db).filter(
        Book.is_active == True
    )

    if category_id:
        query = query.join(
            BookCategory,
            Book.id == BookCategory.book_id,
        ).filter(
            BookCategory.category_id == category_id
        )

    if publisher_id:
        query = query.filter(
            Book.publisher_id == publisher_id
        )

    if author_id:
        query = query.filter(
            Book.author_id == author_id
        )

    if language:
        query = query.filter(
            Book.language == language
        )

    if format:
        query = query.filter(
            Book.format == format
        )

    if min_price is not None:
        query = query.filter(
            Book.price >= min_price
        )

    if max_price is not None:
        query = query.filter(
            Book.price <= max_price
        )

    if search:
        query = query.filter(
            Book.title.ilike(f"%{search}%")
        )

    return query.order_by(
        Book.created_at.desc()
    ).all()


@router.get(
    "/books/{book_id}",
    response_model=BookResponse,
)
def get_book(
    book_id: int,
    db: Session = Depends(get_db),
):
    return get_book_or_404(book_id, db)


@router.put(
    "/books/{book_id}",
    response_model=BookResponse,
)
def update_book(
    book_id: int,
    data: BookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    book = get_book_or_404(book_id, db)

    update_data = data.model_dump(
        exclude_unset=True,
    )

    category_ids = update_data.pop(
        "category_ids",
        None,
    )

    for field, value in update_data.items():
        setattr(book, field, value)

    if category_ids is not None:
        db.query(BookCategory).filter(
            BookCategory.book_id == book.id
        ).delete(
            synchronize_session=False
        )

        categories = db.query(Category).filter(
            Category.id.in_(category_ids)
        ).all()

        if len(categories) != len(set(category_ids)):
            raise HTTPException(
                status_code=400,
                detail="One or more categories not found",
            )

        for category in categories:
            db.add(
                BookCategory(
                    book_id=book.id,
                    category_id=category.id,
                )
            )

    db.commit()

    return get_book_or_404(book.id, db)


@router.delete(
    "/books/{book_id}",
)
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    book = get_book_or_404(book_id, db)

    book.is_active = False

    db.commit()

    return {
        "message": "Book removed successfully"
    }


# ============================================================
# CART
# ============================================================

def get_or_create_cart(
    user_id: int,
    db: Session,
):
    cart = db.query(Cart).filter(
        Cart.user_id == user_id
    ).first()

    if not cart:
        cart = Cart(
            user_id=user_id,
        )

        db.add(cart)
        db.commit()
        db.refresh(cart)

    return cart


def build_cart_response(
    cart: Cart,
):
    items = []
    subtotal = Decimal("0.00")

    for item in cart.items:
        item_total = (
            item.book.price *
            item.quantity
        )

        subtotal += item_total

        items.append(
            CartItemResponse(
                id=item.id,
                book=item.book,
                quantity=item.quantity,
                item_total=item_total,
            )
        )

    return CartResponse(
        id=cart.id,
        items=items,
        subtotal=subtotal,
    )


@router.get(
    "/cart",
    response_model=CartResponse,
)
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cart = get_or_create_cart(
        current_user.id,
        db,
    )

    cart = db.query(Cart).options(
        joinedload(Cart.items)
        .joinedload(CartItem.book)
    ).filter(
        Cart.id == cart.id
    ).first()

    return build_cart_response(cart)


@router.post(
    "/cart/items",
    response_model=CartResponse,
)
def add_to_cart(
    data: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    book = db.query(Book).filter(
        Book.id == data.book_id,
        Book.is_active == True,
    ).first()

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found",
        )

    if data.quantity > book.stock_quantity:
        raise HTTPException(
            status_code=400,
            detail="Insufficient stock",
        )

    cart = get_or_create_cart(
        current_user.id,
        db,
    )

    item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.book_id == book.id,
    ).first()

    if item:
        new_quantity = (
            item.quantity +
            data.quantity
        )

        if new_quantity > book.stock_quantity:
            raise HTTPException(
                status_code=400,
                detail="Insufficient stock",
            )

        item.quantity = new_quantity

    else:
        item = CartItem(
            cart_id=cart.id,
            book_id=book.id,
            quantity=data.quantity,
        )

        db.add(item)

    db.commit()

    return get_cart(
        db=db,
        current_user=current_user,
    )


@router.put(
    "/cart/items/{item_id}",
    response_model=CartResponse,
)
def update_cart_item(
    item_id: int,
    data: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(CartItem).join(
        Cart
    ).filter(
        CartItem.id == item_id,
        Cart.user_id == current_user.id,
    ).first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found",
        )

    if data.quantity > item.book.stock_quantity:
        raise HTTPException(
            status_code=400,
            detail="Insufficient stock",
        )

    item.quantity = data.quantity

    db.commit()

    return get_cart(
        db=db,
        current_user=current_user,
    )


@router.delete(
    "/cart/items/{item_id}",
    response_model=CartResponse,
)
def remove_cart_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(CartItem).join(
        Cart
    ).filter(
        CartItem.id == item_id,
        Cart.user_id == current_user.id,
    ).first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found",
        )

    db.delete(item)
    db.commit()

    return get_cart(
        db=db,
        current_user=current_user,
    )


@router.delete(
    "/cart",
)
def clear_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cart = db.query(Cart).filter(
        Cart.user_id == current_user.id
    ).first()

    if cart:
        db.query(CartItem).filter(
            CartItem.cart_id == cart.id
        ).delete(
            synchronize_session=False
        )

        db.commit()

    return {
        "message": "Cart cleared successfully"
    }


# ============================================================
# WISHLIST
# ============================================================

@router.get(
    "/wishlist",
    response_model=list[WishlistResponse],
)
def get_wishlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Wishlist).options(
        joinedload(Wishlist.book)
    ).filter(
        Wishlist.user_id == current_user.id
    ).order_by(
        Wishlist.created_at.desc()
    ).all()


@router.post(
    "/wishlist",
    response_model=WishlistResponse,
)
def add_to_wishlist(
    data: WishlistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    book = db.query(Book).filter(
        Book.id == data.book_id,
        Book.is_active == True,
    ).first()

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found",
        )

    existing = db.query(Wishlist).filter(
        Wishlist.user_id == current_user.id,
        Wishlist.book_id == data.book_id,
    ).first()

    if existing:
        return existing

    wishlist = Wishlist(
        user_id=current_user.id,
        book_id=data.book_id,
    )

    db.add(wishlist)
    db.commit()
    db.refresh(wishlist)

    return db.query(Wishlist).options(
        joinedload(Wishlist.book)
    ).filter(
        Wishlist.id == wishlist.id
    ).first()


@router.delete(
    "/wishlist/{book_id}",
)
def remove_from_wishlist(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    wishlist = db.query(Wishlist).filter(
        Wishlist.user_id == current_user.id,
        Wishlist.book_id == book_id,
    ).first()

    if not wishlist:
        raise HTTPException(
            status_code=404,
            detail="Book is not in wishlist",
        )

    db.delete(wishlist)
    db.commit()

    return {
        "message": "Book removed from wishlist"
    }


@router.delete(
    "/wishlist",
)
def clear_wishlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db.query(Wishlist).filter(
        Wishlist.user_id == current_user.id
    ).delete(
        synchronize_session=False
    )

    db.commit()

    return {
        "message": "Wishlist cleared successfully"
    }


# ============================================================
# ADDRESSES
# ============================================================

def unset_default_addresses(
    user_id: int,
    db: Session,
):
    db.query(Address).filter(
        Address.user_id == user_id,
        Address.is_default == True,
    ).update(
        {
            Address.is_default: False
        },
        synchronize_session=False,
    )


@router.post(
    "/addresses",
    response_model=AddressResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_address(
    data: AddressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if data.is_default:
        unset_default_addresses(
            current_user.id,
            db,
        )

    address = Address(
        user_id=current_user.id,
        full_name=data.full_name,
        address_line1=data.address_line1,
        address_line2=data.address_line2,
        city=data.city,
        state=data.state,
        postal_code=data.postal_code,
        country=data.country,
        is_default=data.is_default,
    )

    db.add(address)
    db.commit()
    db.refresh(address)

    return address


@router.get(
    "/addresses",
    response_model=list[AddressResponse],
)
def get_addresses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Address).filter(
        Address.user_id == current_user.id
    ).order_by(
        Address.is_default.desc(),
        Address.created_at.desc(),
    ).all()


@router.get(
    "/addresses/{address_id}",
    response_model=AddressResponse,
)
def get_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id,
    ).first()

    if not address:
        raise HTTPException(
            status_code=404,
            detail="Address not found",
        )

    return address


@router.put(
    "/addresses/{address_id}",
    response_model=AddressResponse,
)
def update_address(
    address_id: int,
    data: AddressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id,
    ).first()

    if not address:
        raise HTTPException(
            status_code=404,
            detail="Address not found",
        )

    update_data = data.model_dump(
        exclude_unset=True,
    )

    if update_data.get("is_default") is True:
        unset_default_addresses(
            current_user.id,
            db,
        )

    for field, value in update_data.items():
        setattr(address, field, value)

    db.commit()
    db.refresh(address)

    return address


@router.post(
    "/addresses/{address_id}/default",
    response_model=AddressResponse,
)
def set_default_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id,
    ).first()

    if not address:
        raise HTTPException(
            status_code=404,
            detail="Address not found",
        )

    unset_default_addresses(
        current_user.id,
        db,
    )

    address.is_default = True

    db.commit()
    db.refresh(address)

    return address


@router.delete(
    "/addresses/{address_id}",
)
def delete_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id,
    ).first()

    if not address:
        raise HTTPException(
            status_code=404,
            detail="Address not found",
        )

    db.delete(address)
    db.commit()

    return {
        "message": "Address deleted successfully"
    }


# ============================================================
# ORDERS
# ============================================================

def build_order_response(
    order: Order,
):
    items = []

    for item in order.items:
        items.append(
            OrderItemResponse(
                id=item.id,
                book_id=item.book_id,
                book_title=item.book.title,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.total_price,
            )
        )

    return OrderResponse(
        id=order.id,
        status=order.status,
        subtotal=order.subtotal,
        tax=order.tax,
        delivery_charge=order.delivery_charge,
        discount=order.discount,
        gift_points_used=order.gift_points_used,
        total_amount=order.total_amount,
        shipping_full_name=order.shipping_full_name,
        shipping_address_line1=order.shipping_address_line1,
        shipping_address_line2=order.shipping_address_line2,
        shipping_city=order.shipping_city,
        shipping_state=order.shipping_state,
        shipping_postal_code=order.shipping_postal_code,
        shipping_country=order.shipping_country,
        created_at=order.created_at,
        cancelled_at=order.cancelled_at,
        items=items,
        payment=(
            PaymentResponse.model_validate(
                order.payment
            )
            if order.payment
            else None
        ),
    )


@router.post(
    "/orders",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order(
    data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cart = db.query(Cart).options(
        joinedload(Cart.items)
        .joinedload(CartItem.book)
    ).filter(
        Cart.user_id == current_user.id
    ).first()

    if not cart or not cart.items:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty",
        )

    address = db.query(Address).filter(
        Address.id == data.address_id,
        Address.user_id == current_user.id,
    ).first()

    if not address:
        raise HTTPException(
            status_code=404,
            detail="Address not found",
        )

    if data.gift_points_used > current_user.gift_points_balance:
        raise HTTPException(
            status_code=400,
            detail="Insufficient gift points",
        )

    subtotal = Decimal("0.00")

    for cart_item in cart.items:
        if not cart_item.book.is_active:
            raise HTTPException(
                status_code=400,
                detail=f"Book '{cart_item.book.title}' is unavailable",
            )

        if cart_item.quantity > cart_item.book.stock_quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for '{cart_item.book.title}'",
            )

        subtotal += (
            cart_item.book.price *
            cart_item.quantity
        )

    tax = (
        subtotal *
        Decimal("0.18")
    ).quantize(Decimal("0.01"))

    delivery_charge = (
        Decimal("40.00")
        if subtotal < Decimal("500.00")
        else Decimal("0.00")
    )

    discount = Decimal(
        data.gift_points_used
    )

    total_amount = (
        subtotal +
        tax +
        delivery_charge -
        discount
    )

    if total_amount < Decimal("0.00"):
        total_amount = Decimal("0.00")

    order = Order(
        user_id=current_user.id,
        status="CONFIRMED",
        subtotal=subtotal,
        tax=tax,
        delivery_charge=delivery_charge,
        discount=discount,
        gift_points_used=data.gift_points_used,
        total_amount=total_amount,
        shipping_full_name=address.full_name,
        shipping_address_line1=address.address_line1,
        shipping_address_line2=address.address_line2,
        shipping_city=address.city,
        shipping_state=address.state,
        shipping_postal_code=address.postal_code,
        shipping_country=address.country,
    )

    db.add(order)
    db.flush()

    for cart_item in cart.items:
        book = cart_item.book

        order_item = OrderItem(
            order_id=order.id,
            book_id=book.id,
            quantity=cart_item.quantity,
            unit_price=book.price,
            total_price=(
                book.price *
                cart_item.quantity
            ),
        )

        db.add(order_item)

        book.stock_quantity -= cart_item.quantity
        book.sales_count += cart_item.quantity

    if data.gift_points_used:
        current_user.gift_points_balance -= (
            data.gift_points_used
        )

    payment = Payment(
        order_id=order.id,
        method="MOCK",
        amount=total_amount,
        status="COMPLETED",
        transaction_reference=(
            f"MOCK-TXN-{order.id}"
        ),
        paid_at=datetime.utcnow(),
    )

    db.add(payment)

    db.query(CartItem).filter(
        CartItem.cart_id == cart.id
    ).delete(
        synchronize_session=False
    )

    db.commit()

    order = db.query(Order).options(
        joinedload(Order.items)
        .joinedload(OrderItem.book),
        joinedload(Order.payment),
    ).filter(
        Order.id == order.id
    ).first()

    return build_order_response(order)


@router.get(
    "/orders",
    response_model=list[OrderResponse],
)
def get_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    orders = db.query(Order).options(
        joinedload(Order.items)
        .joinedload(OrderItem.book),
        joinedload(Order.payment),
    ).filter(
        Order.user_id == current_user.id
    ).order_by(
        Order.created_at.desc()
    ).all()

    return [
        build_order_response(order)
        for order in orders
    ]


@router.get(
    "/orders/{order_id}",
    response_model=OrderResponse,
)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = db.query(Order).options(
        joinedload(Order.items)
        .joinedload(OrderItem.book),
        joinedload(Order.payment),
    ).filter(
        Order.id == order_id,
        Order.user_id == current_user.id,
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    return build_order_response(order)


# ============================================================
# CANCEL ORDER
# ============================================================

@router.post(
    "/orders/{order_id}/cancel",
    response_model=OrderResponse,
)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = db.query(Order).options(
        joinedload(Order.items)
        .joinedload(OrderItem.book),
        joinedload(Order.payment),
    ).filter(
        Order.id == order_id,
        Order.user_id == current_user.id,
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    if order.status == "CANCELLED":
        raise HTTPException(
            status_code=400,
            detail="Order is already cancelled",
        )

    if datetime.utcnow() > (
        order.created_at +
        timedelta(hours=48)
    ):
        raise HTTPException(
            status_code=400,
            detail="Order can only be cancelled within 48 hours",
        )

    if order.status not in (
        "CONFIRMED",
        "PROCESSING",
        "SHIPPED",
    ):
        raise HTTPException(
            status_code=400,
            detail="Order cannot be cancelled",
        )

    for item in order.items:
        item.book.stock_quantity += item.quantity

        item.book.sales_count = max(
            0,
            item.book.sales_count -
            item.quantity,
        )

    if order.gift_points_used:
        current_user.gift_points_balance += (
            order.gift_points_used
        )

    order.status = "CANCELLED"
    order.cancelled_at = datetime.utcnow()

    if order.payment:
        order.payment.status = "REFUND_PENDING"

    db.commit()

    order = db.query(Order).options(
        joinedload(Order.items)
        .joinedload(OrderItem.book),
        joinedload(Order.payment),
    ).filter(
        Order.id == order.id
    ).first()

    return build_order_response(order)


# ============================================================
# BUY AGAIN
# ============================================================

@router.post(
    "/orders/{order_id}/buy-again",
    response_model=CartResponse,
)
def buy_again(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = db.query(Order).options(
        joinedload(Order.items)
        .joinedload(OrderItem.book),
    ).filter(
        Order.id == order_id,
        Order.user_id == current_user.id,
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    cart = get_or_create_cart(
        current_user.id,
        db,
    )

    for order_item in order.items:
        book = order_item.book

        if not book.is_active:
            continue

        if book.stock_quantity <= 0:
            continue

        existing = db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.book_id == book.id,
        ).first()

        if existing:
            existing.quantity = min(
                existing.quantity +
                order_item.quantity,
                book.stock_quantity,
            )
        else:
            db.add(
                CartItem(
                    cart_id=cart.id,
                    book_id=book.id,
                    quantity=min(
                        order_item.quantity,
                        book.stock_quantity,
                    ),
                )
            )

    db.commit()

    return get_cart(
        db=db,
        current_user=current_user,
    )


# ============================================================
# REVIEWS
# ============================================================

def user_purchased_book(
    user_id: int,
    book_id: int,
    db: Session,
):
    return db.query(OrderItem).join(
        Order
    ).filter(
        Order.user_id == user_id,
        OrderItem.book_id == book_id,
        Order.status != "CANCELLED",
    ).first() is not None


def recalculate_book_rating(
    book_id: int,
    db: Session,
):
    result = db.query(
        func.avg(Review.rating)
    ).filter(
        Review.book_id == book_id
    ).scalar()

    book = db.query(Book).filter(
        Book.id == book_id
    ).first()

    if book:
        book.average_rating = (
            Decimal(str(round(float(result), 2)))
            if result is not None
            else Decimal("0.00")
        )


@router.post(
    "/books/{book_id}/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_review(
    book_id: int,
    data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    book = db.query(Book).filter(
        Book.id == book_id
    ).first()

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found",
        )

    purchased = user_purchased_book(
        current_user.id,
        book_id,
        db,
    )

    if not purchased:
        raise HTTPException(
            status_code=403,
            detail="You can review only books you have purchased",
        )

    existing = db.query(Review).filter(
        Review.user_id == current_user.id,
        Review.book_id == book_id,
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="You have already reviewed this book",
        )

    review = Review(
        user_id=current_user.id,
        book_id=book_id,
        rating=data.rating,
        comment=data.comment,
    )

    db.add(review)

    db.flush()

    recalculate_book_rating(
        book_id,
        db,
    )

    db.commit()
    db.refresh(review)

    return ReviewResponse(
        id=review.id,
        user_id=review.user_id,
        user_name=current_user.name,
        book_id=review.book_id,
        rating=review.rating,
        comment=review.comment,
        created_at=review.created_at,
        updated_at=review.updated_at,
    )


@router.get(
    "/books/{book_id}/reviews",
    response_model=list[ReviewResponse],
)
def get_book_reviews(
    book_id: int,
    db: Session = Depends(get_db),
):
    book = db.query(Book).filter(
        Book.id == book_id
    ).first()

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found",
        )

    reviews = db.query(Review).join(
        User
    ).filter(
        Review.book_id == book_id
    ).order_by(
        Review.created_at.desc()
    ).all()

    return [
        ReviewResponse(
            id=review.id,
            user_id=review.user_id,
            user_name=review.user.name,
            book_id=review.book_id,
            rating=review.rating,
            comment=review.comment,
            created_at=review.created_at,
            updated_at=review.updated_at,
        )
        for review in reviews
    ]


@router.put(
    "/reviews/{review_id}",
    response_model=ReviewResponse,
)
def update_review(
    review_id: int,
    data: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review = db.query(Review).filter(
        Review.id == review_id,
        Review.user_id == current_user.id,
    ).first()

    if not review:
        raise HTTPException(
            status_code=404,
            detail="Review not found",
        )

    review.rating = data.rating
    review.comment = data.comment
    review.updated_at = datetime.utcnow()

    recalculate_book_rating(
        review.book_id,
        db,
    )

    db.commit()
    db.refresh(review)

    return ReviewResponse(
        id=review.id,
        user_id=review.user_id,
        user_name=current_user.name,
        book_id=review.book_id,
        rating=review.rating,
        comment=review.comment,
        created_at=review.created_at,
        updated_at=review.updated_at,
    )


@router.delete(
    "/reviews/{review_id}",
)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review = db.query(Review).filter(
        Review.id == review_id,
        Review.user_id == current_user.id,
    ).first()

    if not review:
        raise HTTPException(
            status_code=404,
            detail="Review not found",
        )

    book_id = review.book_id

    db.delete(review)

    db.flush()

    recalculate_book_rating(
        book_id,
        db,
    )

    db.commit()

    return {
        "message": "Review deleted successfully"
    }


# ============================================================
# RELATED BOOKS
# ============================================================

@router.get(
    "/books/{book_id}/related",
    response_model=RelatedBooksResponse,
)
def get_related_books(
    book_id: int,
    limit: int = Query(
        default=6,
        ge=1,
        le=20,
    ),
    db: Session = Depends(get_db),
):
    book = db.query(Book).filter(
        Book.id == book_id
    ).first()

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found",
        )

    category_ids = db.query(
        BookCategory.category_id
    ).filter(
        BookCategory.book_id == book_id
    ).subquery()

    shared_category_count = func.count(
        BookCategory.category_id
    )

    related_books = db.query(Book).options(
        joinedload(Book.author),
        joinedload(Book.publisher),
        joinedload(Book.book_categories)
        .joinedload(BookCategory.category),
    ).join(
        BookCategory,
        Book.id == BookCategory.book_id,
    ).filter(
        BookCategory.category_id.in_(
            category_ids
        ),
        Book.id != book_id,
        Book.is_active == True,
    ).group_by(
        Book.id
    ).order_by(
        desc(shared_category_count),
        desc(Book.sales_count),
        desc(Book.average_rating),
    ).limit(
        limit
    ).all()

    return RelatedBooksResponse(
        book_id=book_id,
        books=related_books,
    )


# ============================================================
# RECOMMENDATIONS
# ============================================================

@router.get(
    "/recommendations",
    response_model=RecommendationResponse,
)
def get_recommendations(
    limit: int = Query(
        default=10,
        ge=1,
        le=20,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    purchased_book_ids_query = db.query(
        OrderItem.book_id
    ).join(
        Order
    ).filter(
        Order.user_id == current_user.id,
        Order.status != "CANCELLED",
    ).distinct()

    purchased_book_ids = [
        row[0]
        for row in purchased_book_ids_query.all()
    ]

    if not purchased_book_ids:
        books = db.query(Book).options(
            joinedload(Book.author),
            joinedload(Book.publisher),
            joinedload(Book.book_categories)
            .joinedload(BookCategory.category),
        ).filter(
            Book.is_active == True,
            Book.stock_quantity > 0,
        ).order_by(
            desc(Book.sales_count),
            desc(Book.average_rating),
        ).limit(
            limit
        ).all()

        return RecommendationResponse(
            reason="Popular books for you",
            books=books,
        )

    category_ids = db.query(
        BookCategory.category_id
    ).join(
        Book,
        Book.id == BookCategory.book_id,
    ).join(
        OrderItem,
        OrderItem.book_id == Book.id,
    ).join(
        Order,
        Order.id == OrderItem.order_id,
    ).filter(
        Order.user_id == current_user.id,
        Order.status != "CANCELLED",
    ).group_by(
        BookCategory.category_id
    ).order_by(
        desc(
            func.count(OrderItem.id)
        )
    ).limit(
        5
    ).all()

    category_ids = [
        row[0]
        for row in category_ids
    ]

    if not category_ids:
        books = db.query(Book).filter(
            Book.is_active == True,
            Book.stock_quantity > 0,
        ).order_by(
            desc(Book.sales_count),
            desc(Book.average_rating),
        ).limit(
            limit
        ).all()

        return RecommendationResponse(
            reason="Popular books for you",
            books=books,
        )

    recommendation_score = func.count(
        BookCategory.category_id
    )

    query = db.query(Book).options(
        joinedload(Book.author),
        joinedload(Book.publisher),
        joinedload(Book.book_categories)
        .joinedload(BookCategory.category),
    ).join(
        BookCategory,
        Book.id == BookCategory.book_id,
    ).filter(
        BookCategory.category_id.in_(category_ids),
        Book.is_active == True,
        Book.stock_quantity > 0,
    )

    if purchased_book_ids:
        query = query.filter(
            ~Book.id.in_(purchased_book_ids)
        )

    books = query.group_by(
        Book.id
    ).order_by(
        desc(recommendation_score),
        desc(Book.sales_count),
        desc(Book.average_rating),
    ).limit(
        limit
    ).all()

    return RecommendationResponse(
        reason="Recommended based on your order history",
        books=books,
    )