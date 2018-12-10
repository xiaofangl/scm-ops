#!/usr/bin/env python
# encoding: utf-8
# author: xiaofangliu
import os
import logging

from logging_conf import log_init

log_init()

logger = logging.getLogger(__file__)

if __name__ == '__main__':
    def os_execute_command(path, command):
        print(path, command)
        result = False
        if command != '' and path != '':
            try:
                os.chdir(path)
                command_result = os.popen(command)
                result = command_result.read()
                # print(result)
            except Exception as e:
                print(e)
                logger.error(e.__str__())
                _pwd = os.getcwd()
                logger.error(u'您的项目路径为 %s, 当前路径为 %s, 当前命令为 %s; '
                             '请确认 Git的执行路径是否正确。。。' % (
                                 path, _pwd, command))
                print(u'您的项目路径为 %s, 当前路径为 %s, 当前命令为 %s; '
                      '请确认 Git的执行路径是否正确。。。' % (
                          path, _pwd, command))

        else:
            logger.error(u'参数不能为空。。。')
            print(u'参数不能为空。。。')

        return result
    all_branch = 'git branch -a'
    all_branch_list = os_execute_command('/tmp/xiaofangl/.repo/manifests',
                                         all_branch)
    res = {}
    for one_branch in all_branch_list.split('\n'):
        if one_branch:
            print('++++' * 20)
            logger.debug("this branch is %s" % one_branch)
            if one_branch.split()[-1].split(')')[0]:
                print(one_branch, one_branch.split()[-1].split(')')[0])
                get_manifests = ("git log %s --pretty=oneline | "
                                 "grep 'Daily_build:save' | "
                                 "awk '{print $3}'" % (
                                     one_branch.split()[-1].split(')')[0]))
                os_execute_command('/tmp/xiaofangl/.repo/manifests',
                                   'git checkout %s' %
                                   one_branch.split()[-1].split(')')[0])

                _build = os_execute_command('/tmp/xiaofangl/.repo/manifests',
                                            get_manifests)
                if not _build:
                    logger.warning('this branch not daily_build ===>>> %s' %
                                   one_branch)
                else:
                    build_list = _build.split('\n')
                    logger.info('this branch have daily_build ===>>>'
                                ' %s; the manifest is %s' %
                                (one_branch, build_list[0]))
                res[one_branch.split()[-1].split(')')[0]] = _build
    print(res)
