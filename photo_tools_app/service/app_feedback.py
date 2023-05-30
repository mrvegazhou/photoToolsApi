# _*_ coding: utf-8 _*_
from photo_tools_app.model.app_feedback import AppFeedback as AppFeedbackModel
from photo_tools_app.exception.api_exception import FeedbackContentIsNull, FeedbackTypeIsNull, FeedbackReplyContentIsNull, FeedbackReplyReplyUserIsNull, FeedbackIdIsNull, FeedbackReplyToUserIsNull
from photo_tools_app.model.app_feedback_reply import AppFeedbackRelpy
from photo_tools_app.service.app_imgs import AppImgsService
from photo_tools_app.model.app_imgs import AppImgs as AppImgsModel
from photo_tools_app.model.app_user import AppUser as AppUserModel
from photo_tools_admin.model.admin_user import AdminUser as AdminUserModel


class AppFeedbackService(object):
    @staticmethod
    def get_feedback_list(page_num=1, content=None, contact=None, type=None, begin_date=None, end_date=None):
        feedback_list, total = AppFeedbackModel.get_feedback_list_by_page(page_num=page_num,  content=content, contact=contact, type=type, begin_date=begin_date, end_date=end_date)
        new_feedback_list = []
        for index, feedback in enumerate(feedback_list):
            new_feedback = dict(feedback)
            if feedback.imgs:
                imgs = feedback.imgs.split(',')
                imgs_list = AppImgsModel.get_app_imgs_by_ids(imgs)
                new_feedback['imgs'] = ','.join([img.url for img in imgs_list])
            if feedback.user_id:
                user_info = AppUserModel.get_userinfo_by_uuid(feedback.user_id)
                new_feedback.setdefault('user', user_info.username)
            new_feedback['type'] = AppFeedbackModel.get_type_str(feedback.type)
            # new_feedback['create_time'] = feedback.create_time.strftime("%Y-%m-%d %H:%M:%S")
            new_feedback_list.append(new_feedback)

        return new_feedback_list, total

    @staticmethod
    def del_feedback(uuid):
        AppFeedbackRelpy.del_feedback_reply(uuid)
        return AppFeedbackModel.del_feedback(uuid)

    @staticmethod
    def reply_feedback(feedback_id, content, to_user_id, reply_user_id):
        if not feedback_id:
            raise FeedbackIdIsNull()
        if not content:
            raise FeedbackReplyContentIsNull()
        if not reply_user_id:
            raise FeedbackReplyReplyUserIsNull()
        if not to_user_id:
            raise FeedbackReplyToUserIsNull()
        app_feedback_reply_model = AppFeedbackRelpy()
        app_feedback_reply_model.feedback_id = feedback_id
        app_feedback_reply_model.content = content
        app_feedback_reply_model.to_user_id = to_user_id
        app_feedback_reply_model.reply_user_id = reply_user_id
        return AppFeedbackRelpy.save_feedback_reply_info(app_feedback_reply_model)

    @staticmethod
    def save_feedback_info(info):
        feedback = AppFeedbackModel()
        if 'content' not in info or info['content'].strip()=='':
            raise FeedbackContentIsNull()
        if 'type' not in info or info['type'].strip()=='':
            raise FeedbackTypeIsNull()
        feedback.content = info['content'].strip()
        if info['type'].lower()=='suggest':
            feedback.type = 1
        elif info['type'].lower()=='bug':
            feedback.type = 2
        if 'contact' in info and info['contact'].strip()!='':
            feedback.contact = info['contact']
        if 'user_id' in info and info['user_id']:
            feedback.user_id = info['user_id']

        save_feedback_res = AppFeedbackModel.save_feedback_info(feedback)
        if save_feedback_res:
            if 'imgs' in info and len(info['imgs'])!=0:
                res_list = []
                for img in info['imgs']:
                    res, file_dir = AppImgsService.save_app_img_file_info(img, type='base64')
                    res_list.append({
                        'type': 1,
                        'tags': 'feedback',
                        'url': res,
                        'base_dir': file_dir
                    })
                imgs_ids = AppImgsService.save_app_imgs(res_list)
                imgs_ids_str = ','.join([str(img_id[0]) for img_id in imgs_ids])
                AppFeedbackModel.update_feedback_imgs(save_feedback_res, imgs_ids_str)
            return save_feedback_res
        else:
            return None

    @staticmethod
    def get_reply_feedback_list(feedback_id):
        reply_feedback_list = AppFeedbackRelpy.get_reply_feedback_list(feedback_id)
        if reply_feedback_list:
            user_ids = []
            for item in reply_feedback_list:
                user_ids.append(item.to_user_id)
                user_ids.append(item.reply_user_id)

            res_user_dict = {}

            admin_user_ids = set([uid for uid in user_ids if uid<=0])
            app_user_ids = list(set(user_ids).difference(admin_user_ids))

            user_list = AppUserModel.get_user_list_by_uuids(app_user_ids)
            for info in user_list:
                res_user_dict[info.uuid] = info.username

            if admin_user_ids:
                admin_user_list = AdminUserModel.get_admin_user_list_by_uuids([-admin_uid for admin_uid in admin_user_ids])
                for info in admin_user_list:
                    res_user_dict[-info.uuid] = info.username+'(管理员)'

            new_reply_feedback_list = []
            for index, reply in enumerate(reply_feedback_list):
                new_reply_feedback = dict(reply)
                new_reply_feedback["to_user"] = res_user_dict[new_reply_feedback['to_user_id']]
                new_reply_feedback["reply_user"] = res_user_dict[new_reply_feedback['reply_user_id']]
                new_reply_feedback_list.append(new_reply_feedback)

            return new_reply_feedback_list



    @staticmethod
    def test_sesson_tran():
        AppFeedbackRelpy.test_sesson_tran()








