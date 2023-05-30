from photo_tools_admin import Blueprint, CORS

admin = Blueprint("admin", __name__, url_prefix='/admin/sys')
CORS(admin, resources={r"/*": {"origins": "*"}})

from photo_tools_admin.controller import admin_user
from photo_tools_admin.controller import admin_role
from photo_tools_admin.controller import admin_user_role
from photo_tools_admin.controller import admin_menu_power
from photo_tools_admin.controller import admin_role_menu_power
from photo_tools_admin.controller import admin_menu
from photo_tools_admin.controller import app_user
from photo_tools_admin.controller import app_imgs
from photo_tools_admin.controller import app_feedback