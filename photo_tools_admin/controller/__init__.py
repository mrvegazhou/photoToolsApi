from photo_tools_admin import Blueprint, CORS

admin = Blueprint("admin", __name__, url_prefix='/admin/sys')
CORS(admin, resources={r"/*": {"origins": "*"}})

from photo_tools_admin.controller import \
    admin_user, \
    admin_role, \
    admin_user_role, \
    admin_menu_power, \
    admin_role_menu_power, \
    admin_menu, \
    app_user, \
    app_imgs, \
    app_feedback, \
    app_search_log,\
    app_ad, \
    app_img_library

