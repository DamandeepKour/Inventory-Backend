from sqlalchemy.orm import Session

from models.customer import Customer
from models.order import Order
from models.product import Product
from schemas.dashboard import DashboardResponse

LOW_STOCK_THRESHOLD = 5


def get_dashboard_stats(db: Session) -> DashboardResponse:
    total_products = db.query(Product).count()
    total_customers = db.query(Customer).count()
    total_orders = db.query(Order).count()
    low_stock_products = (
        db.query(Product).filter(Product.quantity <= LOW_STOCK_THRESHOLD).count()
    )

    return DashboardResponse(
        total_products=total_products,
        total_customers=total_customers,
        total_orders=total_orders,
        low_stock_products=low_stock_products,
    )
