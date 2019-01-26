# -*- coding: utf-8 -*-
# @Time    : 2018/8/1 11:16
from collections import OrderedDict
from datetime import datetime
class zd(object):

    def zdf(self):
        save = OrderedDict()
        find = OrderedDict()
        save["update_time"] = datetime.now()
        save["href_link"] = ""
        save['status'] =0
        save['status_two'] = 0
        find["href_link"] = ""
        return save,find