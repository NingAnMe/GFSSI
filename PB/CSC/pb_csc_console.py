# coding: utf-8

from datetime import datetime
from posixpath import join as urljoin
import email
import imaplib
import logging
import os
import poplib
import socket
import sys
from dateutil.relativedelta import relativedelta


__author__ = 'wangpeng'

'''
FileName:     pb_csc_console.py
Description:  订购卫星数据
Author:       wangpeng
Date:         2015-08-21
version:      1.0.0.050821_beat
Input:        args1:开始时间  args2:结束时间  [YYYYMMDD-YYYYMMDD]
Output:       (^_^)
'''
'''
初始化日志
'''


def mail_date2date(mail_str_date):
    str_date = mail_str_date.split(',')[1].split('+')[0]
    fmt_datetime = datetime.strptime(
        str_date.strip(), '%d %b %Y %H:%M:%S')
    return fmt_datetime


def whoImportMe():
    return sys._getframe(2).f_code.co_filename  # .f_code.co_name


class LogServer:

    def __init__(self, logPath, loggerName=None):

        if logPath != '' and not os.path.isdir(logPath):
            os.makedirs(logPath)

        if loggerName is None:
            loggerName = whoImportMe()

        logFile = os.path.splitext(os.path.basename(loggerName))[0] + '.log'

        self.logger = logging.getLogger(loggerName)
        handler = logging.FileHandler(urljoin(logPath, logFile))
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        handler.setLevel(logging.INFO)

        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        self.logger.addHandler(ch)

    def error(self, msg):
        self.logger.error(msg)
        self.logger.handlers[0].flush()

    def info(self, msg):
        self.logger.info(msg)
        self.logger.handlers[0].flush()


'''
socket服务器
'''


class SocketServer(object):

    def __init__(self):
        self.ssdic = {}

    def __deinit__(self):
        for key in self.ssdic.keys():
            sserver = self.ssdic.get(key)
            if sserver:
                sserver.close()

    # 创建socket服务
    def createSocket(self, port):
        ret = False
        try:
            sserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # print socket.gethostname()
            # sserver.bind((socket.gethostname(), port))
            sserver.bind(('localhost', port))
            sserver.listen(5)
            self.ssdic[port] = sserver
            ret = True
        except Exception as e:
            print str(e)

        return ret

    # 关闭socket服务
    def closeSocket(self, port):
        sserver = self.ssdic.get(port)
        if sserver:
            try:
                sserver.close()
                self.ssdic.pop(port)
                sserver = None
            except Exception, e:
                print e


class MailServer_pop3(poplib.POP3):

    def __init__(self, host, ordernumber):

        poplib.POP3.__init__(self, host)
        self.ordernumber = ordernumber  # 订单号
        self.lines = []  # 邮件内容 (list)
        self.title = ''  # 邮件题目
        self.mailnumber = -1  # 邮件在邮箱中的编号

    def connect(self, user, password):
        try:
            #             print("Attempting APOP authentication")
            self.apop(user, password)
        except poplib.error_proto:
            #             print("Attempting standard authentication")
            try:
                self.user(user)
                self.pass_(password)
            except poplib.error_proto, e:
                print "Login failed:", e

    def findmail(self):
        infos = self.list()
        # df2=self.stat()
        if infos[1] is not None:
            mailNum = len(infos[1])
            for num in xrange(mailNum, 0, -1):
                number, octets = infos[1][num - 1].split(' ')
                # 获得邮件内容 (list of lines)
                lines = []
                try:
                    res = self.retr(number)
                    lines = res[1]
                except Exception, e:
                    print(str(e))
                    continue
                # 取得邮件题目
                mail = email.message_from_string('\n'.join(lines))
                title = mail['Subject']
#                log.info('mail tile:%s'%title)
#                log.info('sys.stdin.encoding:%s'%sys.stdin.encoding)
                if title is None:
                    return False

                title = unicode(title, 'UTF-8')
#                 print title, self.ordernumber
                # 比较邮件题目 (CLASS Order xxxxxxxx Processing Complete)
                if (u'Your Langley ASDC FTP Order <%s>' % self.ordernumber) in title:
                    self.title = title
                    self.mailnumber = number
                    self.lines = lines
#                     return True
                elif (u'CLASS Order %s Processing Complete' % self.ordernumber) in title:
                    self.title = title
                    self.mailnumber = number
                    self.lines = lines
#                     return True

                elif (u'CLASS Order %s Verification' % self.ordernumber) in title:
                    #                     self.title = title
                    #                     self.mailnumber = number
                    #                     self.lines = lines
                    self.dele(number)
#                     return False
        if len(self.title) > 0:
            return True
        else:
            return False

    def savemail(self, MAIL_SAVE_PATH, delete_after_save=False):
        #         print ('save the mail NO. %s' % (self.ordernumber))
        msg = email.message_from_string('\n'.join(self.lines))
        if not os.path.dirname(MAIL_SAVE_PATH):
            os.makedirs(os.path.dirname(MAIL_SAVE_PATH))

        # 在保存路径建立新文件
#         mail = open(os.path.join(MAIL_SAVE_PATH, self.title + '.eml'), 'w')
        mail = open(MAIL_SAVE_PATH, 'w')
        # 写入
        mail.write(msg.as_string(unixfrom=1))
        # 结束
        mail.write('\n')
        # 关闭文件
        mail.close()
        # 删除该邮件
        if delete_after_save:
            self.dele(self.mailnumber)


class MailServer_imap(imaplib.IMAP4):

    def __init__(self, host, ordernumber):

        imaplib.IMAP4.__init__(self, host)
        self.ordernumber = ordernumber  # 订单号
        self.lines = []  # 邮件内容 (list)
        self.title = ''  # 邮件题目
        self.mailnumber = -1  # 邮件在邮箱中的编号

    def connect(self, user, password):
        try:
            self.login(user, password)
        except Exception, e:
            print e

    def demail(self):
        # 删除该邮件
        try:
            self.store(self.mailnumber, '+FLAGS', '\\Deleted')
            self.expunge()
            print 'delelte mail %s' % self.mailnumber
        except Exception, e:
            print e

    def findmail(self):
        self.select()
        typ, data = self.search(None, 'ALL')
        assert(typ) == 'OK'
        numlist = [int(e) for e in data[0].split()]
        for number in sorted(numlist, reverse=False):
            print number
            typ, data1 = self.fetch(number, "(UID BODY[HEADER])")
#             typ, data1 = self.fetch(number, "(UID RFC822)")
            rawmail = data1[0][1]
            email_message = email.message_from_string(rawmail)
            title = email_message['Subject']
            print title
            if (u'Your Langley ASDC FTP Order <%s>' % self.ordernumber) in title:
                self.title = title
                self.mailnumber = number
                typ, data2 = self.fetch(number, "(UID BODY[TEXT])")
                self.lines = data2[0][1]
                return True
            elif (u'CLASS Order %s Processing Complete' % self.ordernumber) in title:
                self.title = title
                self.mailnumber = number
                typ, data2 = self.fetch(number, "(UID BODY[TEXT])")
                self.lines = data2[0][1]
                return True
            # yushuai  20181018修改： 邮件内会出现包含多个订单号的返回结果的情况
            elif ('%s' % self.ordernumber) in title and 'Verification' not in title:
                self.title = title
                self.mailnumber = number
                typ, data2 = self.fetch(number, "(UID BODY[TEXT])")
                self.lines = data2[0][1]
                return True

    def findspam(self):
        self.select()
        typ, data = self.search(None, 'ALL')
        assert(typ) == 'OK'
        for number in data[0].split():
            typ, data1 = self.fetch(number, "(UID BODY[HEADER])")
            rawmail = data1[0][1]
            email_message = email.message_from_string(rawmail)
            title = email_message['Subject']
            if 'Verification' in title:
                self.mailnumber = number
                self.demail()
            elif 'Cleanup Alert'in title:
                self.mailnumber = number
                self.demail()
            elif 'Expired' in title:
                self.mailnumber = number
                self.demail()

            # wangpeng add 2018-12-05 添加了清理邮件功能，7天之前的邮件自动删除
            fmt_datetime = mail_date2date(email_message['Date'])
            fmt_date_time_now = datetime.now() - relativedelta(days=5)

            if fmt_datetime < fmt_date_time_now:
                print fmt_datetime, fmt_date_time_now
                self.mailnumber = number
                self.demail()
            else:
                break

        return False

    def savemail(self, savefile):
        if not os.path.dirname(savefile):
            os.makedirs(os.path.dirname(savefile))
        # 在保存路径建立新文件
        # 多个订单在同一封邮件就用这个关键字分割；
        order_lines = self.lines.split(
            'NOTE: You must pick up your data within 96 hours of this notice.')
        mail = open(savefile, 'w')
        # 最后一个是thank you 丢弃
        for line in order_lines[:-1]:
            if 'CLASS has processed your order number %s' % self.ordernumber in line:
                # 写入
                mail.write(line + '\n')
        mail.close()


if __name__ == '__main__':
    #     Log = LogServer('D:/111.log')
    #     Log.info('testinfo')
    m = MailServer_imap('imap.exmail.qq.com', '3566799134')
#     m = MailServer_imap('imap.aliyun.cimap.aliyun.cnom', '123')
#     m = MailServer_imap('imap.kingweather.cn', '123')

    m.connect('FY3gsics@kingtansin.com', 'Kts123')
    # 清理7天之前的所有邮件
    m.findspam()
    if (m.findmail()):
        print '3'
        m.savemail('./3566799134.txt')

    m.close()
    m.logout()
