from stock_admin import Blueprint

admin = Blueprint("admin", __name__, url_prefix='/admin/finance')
# CORS(admin, resources={r"/*": {"origins": "*"}})

from stock_admin.controller import admin_user
from stock_admin.controller import admin_role
from stock_admin.controller import admin_user_role
from stock_admin.controller import admin_menu_power
from stock_admin.controller import admin_role_menu_power
from stock_admin.controller import admin_menu



