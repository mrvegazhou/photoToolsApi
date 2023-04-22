# _*_ coding: utf-8 _*_
from photo_tools_app.model.app_feedback import AppFeedback as AppFeedbackModel
from photo_tools_app.exception.api_exception import FeedbackContentIsNull, FeedbackTypeIsNull
from photo_tools_app.service.app_imgs import AppImgsService


class AppFeedbackService(object):
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
                    res = AppImgsService.save_app_img_file_info(img, type='base64')
                    res_list.append({
                        'type': 1,
                        'tags': 'feedback',
                        'url': res
                    })
                imgs_ids = AppImgsService.save_app_imgs(res_list)
                imgs_ids_str = ','.join([str(img_id[0]) for img_id in imgs_ids])
                AppFeedbackModel.update_feedback_imgs(save_feedback_res, imgs_ids_str)
            return save_feedback_res
        else:
            return None







