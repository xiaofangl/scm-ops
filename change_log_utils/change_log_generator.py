#!/usr/bin/env python
# encoding: utf-8
# author: xiaofangliu


import difflib
import json
import logging

import click
import os
import re
from db_helpers import MysqlOperation
from logging_conf import log_init

log_init()

logger = logging.getLogger(__file__)


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


def read_file(file_name):
    try:
        file_desc = open(file_name, 'r')
        # 读取后按行分割
        text = file_desc.read().splitlines()
        file_desc.close()
        return text
    except IOError as error:
        print('Read input file Error: {0}'.format(error))
        logger.error('Read input file Error: {0}'.format(error))


def write_file(file_name, data):
    status = True
    try:
        with open(file_name, 'w+') as f_w:
            f_w.write(data)
    except IOError as e:
        logger.error(e.__str__())
        status = False
    return status


class OperationData(object):
    def __init__(self, **kwargs):
        if isinstance(kwargs, dict):
            self.workspace = kwargs.get('workspace', '')

            if not self.workspace:
                logger.error("workspace Can't be empty ")
                raise ImportError("workspace Can't be empty ")
            self.tmp_dir = '/tmp/ep_tools/change_log_utils/'
            self.branch_name = kwargs.get('branch_name', '')
            self.mode = kwargs.get('mode', '')
            self.result_to_file = kwargs.get('result_to_file', '')
            self.from_xml = kwargs.get('from_manifest', '')
            self.to_xml = kwargs.get('to_manifest', '')
            self.history_name_src = ''
            self.gerrit_morrir = kwargs.get('gerrit_mirror', '')
            self.db_settings_file = kwargs.get('db_settings_file', '')
            if not os.path.exists(self.db_settings_file):
                logger.error("can't find db_settings_file")
                raise ImportError("can't find db_settings_file")
            self.use_db = MysqlOperation(self.db_settings_file)
            if not os.path.exists(self.tmp_dir):
                os_execute_command('/tmp', ('mkdir -p %s' % self.tmp_dir))
            elif os.path.exists(
                    os.path.join(self.tmp_dir, 'manifest-diff-xml.txt')):
                os_execute_command('/tmp',
                                   'rm -fr /tmp/ep_tools/change_log_utils/'
                                   'manifest-diff-xml.txt')
                if os.path.exists(
                        os.path.join(self.tmp_dir, 'manifest-diff.txt')):
                    os_execute_command('/tmp',
                                       'rm -fr /tmp/ep_tools/'
                                       'change_log_utils/'
                                       'manifest-diff.txt')
        else:
            raise EOFError('init kwargs must a dictionary')

    # 初始化获得manifest
    @staticmethod
    def init_repo(**kwargs):
        if isinstance(kwargs, dict):

            repo_u = 'ssh://' + kwargs.get('user_gerrit', '') + '@' + \
                     kwargs.get('address_gerrit', '') + ':' + \
                     kwargs.get('port_gerrit', '') + \
                     kwargs.get('manifest_project', '')
            repo_b = kwargs.get('branch_name', '')
            repo_s = 'ssh://' + kwargs.get('user_gerrit', '') + '@' + \
                     kwargs.get('address_gerrit', '') + ':' + \
                     kwargs.get('port_gerrit', '') + \
                     kwargs.get('repo_url', '')
            repo_workspace = kwargs.get('workspace', '')

            if not repo_workspace:
                logger.error("workspace Can't be empty ")
                raise ImportError("workspace Can't be empty ")
            if not os.path.exists(repo_workspace):
                os_execute_command('/tmp', ('mkdir -p %s' % repo_workspace))

            if os.path.exists(os.path.join(repo_workspace, '.repo')):
                os_execute_command(repo_workspace,
                                   ('mv %s /tmp' % os.path.join
                                    (repo_workspace, '.repo')))
            repo_cmd = 'repo init -u %s -b %s --repo-url %s --no-repo-verify' \
                       % (repo_u, repo_b, repo_s)
            print(repo_cmd, repo_workspace)
            # logger.debug('%s==>>%s' % repo_cmd, repo_workspace)
            res = os_execute_command(repo_workspace, repo_cmd)
            return res
        else:
            logger.error('kwargs must a dictionary')
            raise EOFError('kwargs must a dictionary')

    # 第一步对比出manifest差异
    def compare_file(self, from_file=None, to_file=None):
        data = ''
        from_xml = ''
        to_xml = ''
        try:
            self.from_xml = from_file if not self.from_xml \
                else self.from_xml
            self.to_xml = to_file if not self.to_xml else self.to_xml

            if self.history_name_src:
                _history_name_src_list = self.history_name_src.split('\n')
                _path = os.path.join(self.workspace,
                                     '.repo/manifests')
                print(len(_history_name_src_list))
                for _one in _history_name_src_list:
                    # print('list' * 20)
                    # print(_one.split())
                    if len(_one) > 3:
                        one_tmp = _one.split()[-1]
                        # print(one_tmp)
                        if self.from_xml == one_tmp:
                            print('__==' * 20)
                            # print(self.from_xml, one_tmp)
                            _from = _one.split()[0] + ':' \
                                + _one.split()[-1]
                            _read_cmd = 'git show %s' % _from
                            _from_xml = os_execute_command(_path,
                                                           _read_cmd)
                            write_file('_from_xml', _from_xml)
                            from_xml = read_file('_from_xml')

                        if self.to_xml == one_tmp:
                            # print(self.from_xml, one_tmp)
                            _to = _one.split()[0] + ':' \
                                + _one.split()[-1]
                            _read_cmd = 'git show %s' % _to
                            _to_xml = os_execute_command(_path,
                                                         _read_cmd)
                            write_file('_from_xml', _to_xml)
                            to_xml = read_file('_from_xml')

                    else:
                        print("history mode, not self.history_name_src")
                        logger.warning('<<<===>>>> LOOK')
                        logger.warning("history mode, not "
                                       "self.history_name_src")
            print(len(from_xml), len(to_xml))
            data = difflib.Differ().compare(from_xml, to_xml)
            # print(str(data))
        except Exception as e:
            logger.error(e)
            logger.warning('%s<<<===>>>%s' % (self.from_xml, self.to_xml))
            print('%s<<<===>>>%s' % (self.from_xml, self.to_xml))
            print(e)

        print(20 * '---')
        data = '\n'.join(data)
        # print(data)
        if data:
            write_file(os.path.join(self.tmp_dir, 'manifest-diff-src.txt'),

                       data)
        else:
            logger.warning('%s ==>> %s not differences' % (self.from_xml,
                                                           self.to_xml))

            raise EOFError('%s ==>> %s not differences' % (self.from_xml,
                                                           self.to_xml))
        p = re.compile(r'^(?P<symbol>\-|\+|\?[^ ]).*')
        with open(os.path.join(self.tmp_dir, 'manifest-diff-src.txt'), 'r') \
                as f:
            while True:
                line = f.readline()
                if line:
                    c_line = p.match(line)
                    # print('c_line: ', c_line)
                    if c_line:
                        with open(
                                os.path.join(self.tmp_dir,
                                             'manifest-diff-xml.txt'),
                                'a') as f_w:
                            f_w.write(c_line.group() + '\n')
                else:
                    break
        add_list = []
        del_list = []
        with open(os.path.join(self.tmp_dir, 'manifest-diff-xml.txt'), 'r') \
                as f:
            while True:
                line = f.readline()
                if line:
                    # print(line)
                    a_p = re.compile(r'^(?P<symbol>\+|\?[^ ]).*')
                    d_p = re.compile(r'^(?P<symbol>\-|\?[^ ]).*')
                    add_line = a_p.match(line)
                    del_line = d_p.match(line)
                    pp = re.compile(
                        r'(?P<name>name=\S[A-Za-z0-9\S]{1,150}\S[^ ]) '
                        r'(?P<path>path=\S[A-Za-z0-9\S]{1,150}\S[^ ]) '
                        r'(?P<revision>revision=\S[A-Za-z0-9\S]{1,150}\S[^ ]) '
                        r'(?P<upstream>upstream=\S[A-Za-z0-9\S]{1,150}\S'
                        r'[^ |^\/\>\/\n ])')

                    if add_line:
                        _one = pp.search(add_line.group())
                        if _one:
                            _tmp = dict()
                            _tmp['name'] = _one.group('name').strip('name='). \
                                strip('"')
                            _tmp['path'] = _one.group('path').strip('path='). \
                                strip('"')
                            _tmp['revision'] = _one.group('revision'). \
                                strip('revision=').strip('"')
                            _tmp['upstream'] = _one.group('upstream'). \
                                strip('upstream=').strip('"')
                            add_list.append(_tmp)
                    elif del_line:
                        # print(del_line.group())
                        _ones = pp.search(del_line.group())
                        # print(_ones)
                        if _ones:
                            _tmp = dict()
                            _tmp['name'] = _ones.group(
                                'name').strip('name='). strip('"')
                            _tmp['path'] = _ones.group(
                                'path').strip('path='). strip('"')
                            _tmp['revision'] = _ones.group('revision'). \
                                strip('revision=').strip('"')
                            _tmp['upstream'] = _ones.group('upstream'). \
                                strip('upstream=').strip('"')
                            del_list.append(_tmp)

                else:
                    break
        print('add++ ', add_list, len(add_list))
        print(20 * '====')
        print('del-- ', del_list, len(del_list))

        add_name = []
        del_name = []
        project_status = []
        for i in add_list:
            add_name.append(i['name'])
        for j in del_list:
            del_name.append(j['name'])
        for i in add_name:
            if i not in del_name:
                a_line = 'A ' + i
                project_status.append(a_line)
            elif i in del_name:
                c_line = 'C ' + i
                project_status.append(c_line)
        for j in del_name:
            if j not in add_name:
                d_line = 'R ' + i
                project_status.append(d_line)
        first_list = []
        for i in project_status:
            print(i)
            if i.split(' ')[0].strip() == 'C':
                c_data = ''
                for j_time in del_list:
                    if i.split(' ')[1].strip() == j_time['name']:
                        c_data = i + ' ' + j_time['path'] + ' ' \
                            + j_time['revision'] + ' ' + j_time['upstream']
                        break
                for ii_time in add_list:
                    if i.split(' ')[1].strip() == ii_time['name']:
                        c_data = c_data + ' ' + ii_time['revision'] + ' ' \
                            + ii_time['upstream']
                        break
                first_list.append(c_data)
            elif i.split(' ')[0].strip() == 'A':
                for i_time in add_list:
                    if i.split(' ')[1].strip() == i_time['name']:
                        one_data = i + ' ' + i_time['path'] + ' ' + i_time[
                            'revision'] + ' ' + i_time['upstream']
                        first_list.append(one_data)
                        break
            elif i.split(' ')[0].strip() == 'R':
                for j_time in del_list:
                    if i.split(' ')[1].strip() == j_time['name']:
                        one_data = i + ' ' + j_time['path'] + ' ' + j_time[
                            'revision'] + ' ' + j_time['upstream']
                        first_list.append(one_data)
                        break
        print('rr' * 20)
        c = 0
        with open(os.path.join(self.tmp_dir, 'manifest-diff.txt'), 'a') as \
                f_f:
            f_f.write('\n'.join(first_list))
        for ii in first_list:
            print(c, ii)
            c = c + 1

        return first_list

    # 获取源manifest列表
    def get_differences_source_file(self, _branch_name=None):
        print(_branch_name)
        path = os.path.join(self.workspace, '.repo/manifests')
        self.branch_name = _branch_name if not \
            self.branch_name else self.branch_name
        print(self.branch_name)
        if not self.branch_name:
            logger.warning("mode history , can't find branch")
            logger.error("mode history , can't find branch ==>> %s"
                         % (self.branch_name))
            print("mode history , can't find branch ==>> %s"
                  % (self.branch_name))
        get_manifests = ("git log %s --pretty=oneline | "
                         "grep 'Daily_build:save' | awk '{print $3}'" % (
                             self.branch_name))
        # print(self.workspace)
        get_manifests_history = ("git log %s --pretty=oneline | "
                                 "grep 'Daily_build:save'" % (
                                     self.branch_name))
        os_execute_command(path, 'git checkout %s' % self.branch_name)
        os_execute_command(path, 'git pull')
        name_res = os_execute_command(path, get_manifests)
        self.history_name_src = os_execute_command(path,
                                                   get_manifests_history)
        if name_res:
            pass
        else:
            logger.error("can't find manifest file, please make sure this "
                         "workspace had .repo/manifests directory")
            raise Exception("can't find manifest file, please make sure this "
                            "workspace had .repo/manifests directory")
        return name_res

    # 获取并解析数据
    def generate_git_data(self, diff_manifest):
        if diff_manifest and isinstance(diff_manifest, list):
            diff_manifest = set(diff_manifest)
            total_dic = dict()
            for one_project in diff_manifest:
                logger.debug(one_project)
                obj_list = []
                if 'C' == one_project[0]:
                    one_project = one_project.split()
                    print(one_project)

                    p_active, p_name, p_path, p_old, from_branch, p_new, \
                        to_branch = one_project[0], \
                        one_project[1], \
                        one_project[2], \
                        one_project[3], \
                        one_project[4], \
                        one_project[5], \
                        one_project[6]
                    print(20 * '--')
                    print(p_active, p_name, p_path, p_old, from_branch, p_new,
                          to_branch)
                    name_exist = False
                    if p_name:
                        name_exist = self.use_db.query('project_name',
                                                       'compile_projectname',
                                                       p_name)
                        logger.info(
                            '%s ==>> %s' % (p_name, name_exist))
                    if p_name and not name_exist:
                        insert_data = dict()
                        insert_data['project_name'] = p_name
                        insert_data['is_app_hmi'] = False
                        logger.info(
                            '%s ==>> %s' % (p_name, insert_data))
                        self.use_db.insert('compile_projectname', insert_data)

                    git_scope_cmd = 'git log {0}..{1} --pretty=format:"%H"'. \
                        format(p_old, p_new)
                    if 'hmi/app' not in p_name:
                        path = os.path.join(self.gerrit_morrir,
                                            (p_name + '.git'))

                        git_scope = os_execute_command(path,
                                                       git_scope_cmd)
                        git_scope_list = git_scope.split('\n')
                        app_id = 0
                        for _line in git_scope_list:
                            print(_line)
                            one_commit_dict = {}

                            one_commit_dict['project'] = p_name
                            one_commit_dict['arg1'] = self.from_xml
                            one_commit_dict['arg2'] = self.to_xml
                            one_commit_dict['id'] = app_id
                            one_commit_dict[
                                'old_version'] = p_old.strip(
                                '\n')
                            one_commit_dict[
                                'new_version'] = p_new.strip(
                                '\n')
                            one_commit = 'git log %s -n1' % _line.strip(
                                '\n')
                            p_line = re.compile(r'^\s{4}(?P<query>\D+: .*).*')
                            p_commit_first = re.compile(
                                r'^(\[)(\D+)(:)(\D+)(\]) .*')
                            p_annotation = re.compile(r'^\n\n.*\n\n$',
                                                      flags=re.S)
                            # 一个version的所有commit hash

                            print('path: ', path)
                            one_commit_info = os_execute_command(path,
                                                                 one_commit)

                            if one_commit_info:
                                one_commit_info_list = one_commit_info.split(
                                    '\n')
                                c = 0
                                for line_i in one_commit_info_list:
                                    if one_commit_info_list.index(line_i) == 0:
                                        one_commit_dict['commit'] = \
                                            line_i.split()[
                                                1]
                                    elif one_commit_info_list.index(
                                            line_i) == 1:
                                        if 'Merge:' in line_i and 'Author' \
                                                not in line_i:
                                            one_commit_dict['Author'] = \
                                                one_commit_info_list[2].split(
                                                    ':')[
                                                    1].strip(' ')
                                            one_commit_dict['Date'] = \
                                                one_commit_info_list[3].split(
                                                    'Date:')[
                                                    1].strip(
                                                    ' ')
                                        elif 'Merge:' not in line_i and \
                                                'Author' in line_i:
                                            one_commit_dict['Author'] = \
                                                one_commit_info_list[1].split(
                                                    ':')[
                                                    1].strip(' ')
                                            one_commit_dict['Date'] = \
                                                one_commit_info_list[2].split(
                                                    'Date:')[
                                                    1].strip(
                                                    ' ')
                                    elif one_commit_info_list.index(
                                            line_i) == 4:
                                        fourth = line_i.strip()
                                        if len(fourth) > 0:
                                            one_commit_dict['title'] = fourth
                                        else:
                                            title = one_commit_info_list[
                                                5].strip()
                                            if title:
                                                one_commit_dict['title'] = \
                                                    title
                                            else:
                                                one_commit_dict[
                                                    'title'] = 'Merge'

                                    else:
                                        first_commit = p_commit_first.match(
                                            line_i)
                                        if first_commit:
                                            first_commit_group = \
                                                first_commit.group()
                                            print(first_commit_group)

                                        else:
                                            # print('else not first')
                                            annotation_text = \
                                                p_annotation.match(line_i)
                                            if annotation_text:
                                                # print('is annotation')
                                                annotation_text_group = \
                                                    annotation_text.group()
                                                # print(annotation_text_group)
                                                _annotation_text1 = \
                                                    annotation_text_group
                                                one_commit_dict[
                                                    'annotation'] = \
                                                    _annotation_text1.strip(
                                                        '\n\n')
                                            else:
                                                # print('keys...')
                                                key_line = p_line.match(line_i)
                                                if key_line:
                                                    key_line_group = \
                                                        key_line.group()
                                                    # print(key_line_group)
                                                    key_line_group_list = \
                                                        key_line_group.split(
                                                            ':')
                                                    one_commit_dict[
                                                        key_line_group_list[
                                                            0].strip()] = \
                                                        key_line_group_list[
                                                            1].strip()

                                    c = c + 1
                            else:
                                continue
                            print(one_commit_dict)
                            commit_id = one_commit_dict.get('commit', '')
                            start_manifest = one_commit_dict.get('arg1', '')
                            end_manifest = one_commit_dict.get('arg2', '')
                            commit_exist = False
                            print(commit_id)
                            if commit_id:
                                commit_exist = self.use_db.query_changelog(
                                    'commit', 'compile_changelog',
                                    start_manifest, end_manifest, commit_id)
                            print('commit_exist', commit_exist)
                            if commit_id and not commit_exist:
                                # use_db = MysqlOperation()
                                self.use_db.insert('compile_changelog',
                                                   one_commit_dict)
                            obj_list.append(one_commit_dict)
                            app_id = app_id + 1
                            print(10 * 'into_db')
                            logger.debug(str(one_commit_dict))

                    elif 'hmi/app' in p_name:
                        path = os.path.join(self.gerrit_morrir,
                                            (p_name + '.git'))

                        tmp_tag = os_execute_command(path, 'git tag')
                        if tmp_tag:
                            tag_list = tmp_tag.split('\n')
                            # print(type(tag_list), tag_list, tmp_tag)
                            p = re.compile(r'[0-9]{6}')
                            arg1 = p.findall(self.from_xml)
                            arg2 = p.findall(self.to_xml)
                            end_tag_name1 = ''
                            end_tag_name2 = ''
                            arg1_0 = arg1[0]
                            arg2_0 = arg2[0]
                            for i in tag_list:
                                if str(arg1_0) in i:
                                    end_tag_name1 = i.strip('\n')
                                elif str(arg2_0) in i:
                                    end_tag_name2 = i.strip('\n')

                            if not end_tag_name1 and end_tag_name2:
                                arg2_index = tag_list.index(end_tag_name2)
                                end_tag_name1 = tag_list[arg2_index - 1]
                            elif not end_tag_name2 and end_tag_name1:
                                arg1_index = tag_list.index(end_tag_name1)
                                end_tag_name2 = tag_list[arg1_index + 1]
                            elif not end_tag_name2 and not end_tag_name1:
                                print('没有 tag 提交吗？')
                                logger.info(u'没有 tag 提交吗？')
                            # print('tag' * 20)
                            # print(path, end_tag_name1, end_tag_name2)
                            diff_tag_cmd = 'git log {0}..{1} ' \
                                           '--pretty=format:"%H"' \
                                .format(
                                    end_tag_name1.strip('\n'),
                                    end_tag_name2.strip('\n'))
                            print(diff_tag_cmd)
                            diff_tag = os_execute_command(path, diff_tag_cmd)
                            print(10 * 'diff_tag')
                            # print(diff_tag.split('\n'))
                            # break
                            diff_tag = diff_tag.split('\n')
                            app_id = 0

                            # 一个项目名下的 版本1到版本2的所有commit
                            for tag_line in diff_tag:
                                one_commit_dict = {}

                                one_commit_dict['project'] = p_name

                                one_commit_dict['arg1'] = self.from_xml
                                one_commit_dict['arg2'] = self.to_xml
                                one_commit_dict['id'] = app_id
                                one_commit_dict[
                                    'old_version'] = end_tag_name1.strip(
                                    '\n')
                                one_commit_dict[
                                    'new_version'] = end_tag_name2.strip(
                                    '\n')
                                one_tag_commit = 'git log %s -n1' % \
                                                 tag_line.strip('\n')
                                # print(one_tag_commit)
                                p_line = re.compile(
                                    r'^\s{4}(?P<query>\D+: .*).*')
                                p_commit_first = re.compile(
                                    r'^(\[)(\D+)(:)(\D+)(\]) .*')
                                p_annotation = re.compile(r'^\n\n.*\n\n$',
                                                          flags=re.S)
                                # 一个version的所有commit hash

                                one_commit_info = os_execute_command(
                                    path, one_tag_commit)

                                if one_commit_info:
                                    # print(one_commit_info.split('\n'))
                                    one_commit_info_list = one_commit_info. \
                                        split('\n')
                                    c = 0
                                    for line_i in one_commit_info_list:
                                        if one_commit_info_list.index(
                                                line_i) == 0:
                                            one_commit_dict['commit'] = \
                                                line_i.split()[
                                                    1]
                                        elif one_commit_info_list.index(
                                                line_i) == 1:
                                            if 'Merge:' in line_i and \
                                                'Author' not in \
                                                    line_i:
                                                one_commit_dict['Author'] = \
                                                    one_commit_info_list[2]. \
                                                    split(':')[1].strip(' ')
                                                one_commit_dict['Date'] = \
                                                    one_commit_info_list[3]. \
                                                    split('Date:')[1].strip(
                                                        ' ')
                                            elif 'Merge:' not in line_i and \
                                                    'Author' in line_i:
                                                one_commit_dict['Author'] = \
                                                    one_commit_info_list[1]. \
                                                    split(':')[1].strip(' ')
                                                one_commit_dict['Date'] = \
                                                    one_commit_info_list[2]. \
                                                    split('Date:')[
                                                        1].strip(' ')
                                        elif one_commit_info_list.index(
                                                line_i) == 4:
                                            fourth = line_i.strip()
                                            if len(fourth) > 0:
                                                one_commit_dict['title'] = \
                                                    fourth
                                            else:
                                                title = one_commit_info_list[
                                                    5].strip()
                                                if title:
                                                    one_commit_dict['title'] \
                                                        = title
                                                else:
                                                    one_commit_dict[
                                                        'title'] = 'Merge'

                                        else:
                                            first_commit = \
                                                p_commit_first.match(line_i)
                                            if first_commit:
                                                first_commit_group = \
                                                    first_commit.group()
                                                print(first_commit_group)

                                            else:
                                                # print('else not first')
                                                annotation_text = \
                                                    p_annotation.match(line_i)
                                                if annotation_text:
                                                    # print('is annotation')
                                                    annotation_text_group = \
                                                        annotation_text.group()
                                                    one_commit_dict[
                                                        'annotation'] = \
                                                        annotation_text_group.\
                                                        strip('\n\n')
                                                else:
                                                    # print('keys...')
                                                    key_line = p_line.match(
                                                        line_i)
                                                    if key_line:
                                                        key_line_group = \
                                                            key_line.group()
                                                        # print(key_line_group)
                                                        line_group_list = \
                                                            key_line_group.\
                                                            split(':')
                                                        one_commit_dict[
                                                            line_group_list
                                                            [0].strip()] = \
                                                            line_group_list[
                                                                1].strip()

                                        c = c + 1

                                else:
                                    continue
                                print(one_commit_dict)

                                commit_id = one_commit_dict.get('commit', '')
                                start_manifest = one_commit_dict.get(
                                    'arg1', '')
                                end_manifest = one_commit_dict.get('arg2', '')
                                commit_exist = False
                                print(commit_id)
                                if commit_id:
                                    commit_exist = self.use_db.query_changelog(
                                        'commit', 'compile_changelog',
                                        start_manifest, end_manifest,
                                        commit_id)
                                print('commit_exist', commit_exist)

                                if commit_id and not commit_exist:
                                    # print('insert ??')
                                    self.use_db.insert('compile_changelog',
                                                       one_commit_dict)
                                obj_list.append(one_commit_dict)
                                app_id = app_id + 1
                                print(10 * 'into_db')
                                logger.debug(str(one_commit_dict))

                        else:
                            print('没有 tag 提交吗？')
                            logger.info(u'--没有 tag 提交吗？')
                            logger.error(p_name)
                    total_dic[p_name] = obj_list
                elif 'A' == one_project[0]:
                    one_project = one_project.split()
                    p_active, p_name, p_path, p_new, to_branch = \
                        one_project[0], \
                        one_project[1], \
                        one_project[2], \
                        one_project[3], \
                        one_project[4]

                    print(20 * '--')
                    print(p_active, p_name, p_path, p_new, to_branch)
                    name_exist = False
                    if p_name:
                        name_exist = self.use_db.query('project_name',
                                                       'compile_projectname',
                                                       p_name)
                        logger.info(
                            '%s ==>> %s' % (p_name, name_exist))
                    if p_name and not name_exist:
                        insert_data = dict()
                        insert_data['project_name'] = p_name
                        insert_data['is_app_hmi'] = False
                        logger.info(
                            '%s ==>> %s' % (p_name, insert_data))
                        self.use_db.insert('compile_projectname', insert_data)

                    git_commit = 'git log %s -n1' % p_new
                    if 'hmi/app' not in p_name:
                        path = os.path.join(self.gerrit_morrir,
                                            (p_name + '.git'))
                        res_commit = os_execute_command(path, git_commit)
                        if res_commit:
                            one_commit_dict = {}

                            one_commit_dict['project'] = p_name
                            one_commit_dict['arg1'] = self.from_xml
                            one_commit_dict['arg2'] = self.to_xml
                            one_commit_dict['id'] = 0
                            one_commit_dict[
                                'old_version'] = p_active.strip(
                                '\n')
                            one_commit_dict[
                                'new_version'] = p_new.strip(
                                '\n')

                            p_line = re.compile(r'^\s{4}(?P<query>\D+: .*).*')
                            p_commit_first = re.compile(
                                r'^(\[)(\D+)(:)(\D+)(\]) .*')
                            p_annotation = re.compile(r'^\n\n.*\n\n$',
                                                      flags=re.S)
                            one_commit_info_list = res_commit.split(
                                '\n')
                            for line_i in one_commit_info_list:
                                if one_commit_info_list.index(line_i) == 0:
                                    one_commit_dict['commit'] = \
                                        line_i.split()[
                                            1]
                                elif one_commit_info_list.index(
                                        line_i) == 1:
                                    if 'Merge:' in line_i and 'Author' \
                                            not in line_i:
                                        one_commit_dict['Author'] = \
                                            one_commit_info_list[2].split(
                                                ':')[
                                                1].strip(' ')
                                        one_commit_dict['Date'] = \
                                            one_commit_info_list[3].split(
                                                'Date:')[
                                                1].strip(
                                                ' ')
                                    elif 'Merge:' not in line_i \
                                            and 'Author' in line_i:
                                        one_commit_dict['Author'] = \
                                            one_commit_info_list[1].split(
                                                ':')[
                                                1].strip(' ')
                                        one_commit_dict['Date'] = \
                                            one_commit_info_list[2].split(
                                                'Date:')[
                                                1].strip(
                                                ' ')
                                elif one_commit_info_list.index(
                                        line_i) == 4:
                                    fourth = line_i.strip()
                                    if len(fourth) > 0:
                                        one_commit_dict['title'] = fourth
                                    else:
                                        title = one_commit_info_list[
                                            5].strip()
                                        if title:
                                            one_commit_dict['title'] = title
                                        else:
                                            one_commit_dict[
                                                'title'] = 'Merge'

                                else:
                                    first_commit = p_commit_first.match(
                                        line_i)
                                    if first_commit:
                                        first_commit_group = \
                                            first_commit.group()
                                        print(first_commit_group)

                                    else:
                                        # print('else not first')
                                        annotation_text = \
                                            p_annotation.match(line_i)
                                        if annotation_text:
                                            # print('is annotation')
                                            annotation_text_group = \
                                                annotation_text.group()
                                            # print(annotation_text_group)
                                            one_commit_dict[
                                                'annotation'] = \
                                                annotation_text_group.strip(
                                                    '\n\n')
                                        else:
                                            # print('keys...')
                                            key_line = p_line.match(line_i)
                                            if key_line:
                                                key_line_group = \
                                                    key_line.group()
                                                # print(key_line_group)
                                                key_line_group_list = \
                                                    key_line_group.split(
                                                        ':')
                                                # print(key_line_group_list)
                                                one_commit_dict[
                                                    key_line_group_list[
                                                        0].strip()] = \
                                                    key_line_group_list[
                                                        1].strip()

                            commit_id = one_commit_dict.get('commit', '')
                            start_manifest = one_commit_dict.get('arg1', '')
                            end_manifest = one_commit_dict.get('arg2', '')
                            commit_exist = False
                            print(commit_id)
                            if commit_id:
                                commit_exist = self.use_db.query_changelog(
                                    'commit', 'compile_changelog',
                                    start_manifest, end_manifest, commit_id)

                            if commit_id and not commit_exist:
                                self.use_db.insert('compile_changelog',
                                                   one_commit_dict)
                            obj_list.append(one_commit_dict)
                            print(10 * 'into_db')
                            logger.debug(str(one_commit_dict))
                        else:
                            print('没有 commit 提交吗？')
                            logger.info(u'--没有 commit 提交吗？')
                            logger.error(p_name)

                    elif 'hmi/app' in p_name:
                        path = os.path.join(self.gerrit_morrir,
                                            (p_name + '.git'))
                        tmp_tag = os_execute_command(path, git_commit)
                        if tmp_tag:
                            one_commit_info_list = tmp_tag.split('\n')
                            one_commit_dict = {}

                            one_commit_dict['project'] = p_name

                            one_commit_dict['arg1'] = self.from_xml
                            one_commit_dict['arg2'] = self.to_xml
                            one_commit_dict['id'] = 0
                            one_commit_dict[
                                'old_version'] = p_active.strip(
                                '\n')
                            one_commit_dict[
                                'new_version'] = p_new.strip(
                                '\n')
                            # print(one_tag_commit)
                            p_line = re.compile(
                                r'^\s{4}(?P<query>\D+: .*).*')
                            p_commit_first = re.compile(
                                r'^(\[)(\D+)(:)(\D+)(\]) .*')
                            p_annotation = re.compile(r'^\n\n.*\n\n$',
                                                      flags=re.S)

                            for line_i in one_commit_info_list:
                                if one_commit_info_list.index(
                                        line_i) == 0:
                                    one_commit_dict['commit'] = \
                                        line_i.split()[
                                            1]
                                elif one_commit_info_list.index(
                                        line_i) == 1:
                                    if 'Merge:' in line_i and 'Author' \
                                            not in line_i:
                                        one_commit_dict['Author'] = \
                                            one_commit_info_list[
                                                2].split(':')[1].strip(' ')
                                        one_commit_dict['Date'] = \
                                            one_commit_info_list[
                                                3].split('Date:')[1].strip(' ')
                                    elif 'Merge:' not in line_i \
                                            and 'Author' in line_i:
                                        one_commit_dict['Author'] = \
                                            one_commit_info_list[
                                                1].split(':')[1].strip(' ')
                                        one_commit_dict['Date'] = \
                                            one_commit_info_list[
                                                2].split('Date:')[1].strip(' ')
                                elif one_commit_info_list.index(
                                        line_i) == 4:
                                    fourth = line_i.strip()
                                    if len(fourth) > 0:
                                        one_commit_dict['title'] = fourth
                                    else:
                                        title = one_commit_info_list[5].strip()
                                        if title:
                                            one_commit_dict['title'] = title
                                        else:
                                            one_commit_dict[
                                                'title'] = 'Merge'

                                else:
                                    first_commit = p_commit_first.match(
                                        line_i)
                                    if first_commit:
                                        first_commit_group = \
                                            first_commit.group()
                                        print(first_commit_group)
                                    else:
                                        # print('else not first')
                                        annotation_text = \
                                            p_annotation.match(line_i)
                                        if annotation_text:
                                            # print('is annotation')
                                            annotation_text_group = \
                                                annotation_text.group()
                                            # print(annotation_text_group)
                                            one_commit_dict[
                                                'annotation'] = \
                                                annotation_text_group. \
                                                strip('\n\n')
                                        else:
                                            # print('keys...')
                                            key_line = p_line.match(line_i)
                                            if key_line:
                                                key_line_group = \
                                                    key_line.group()
                                                # print(key_line_group)
                                                key_line_group_list = \
                                                    key_line_group. \
                                                    split(':')
                                                one_commit_dict[
                                                    key_line_group_list[
                                                        0].strip()] = \
                                                    key_line_group_list[
                                                        1].strip()

                            commit_id = one_commit_dict.get('commit', '')
                            start_manifest = one_commit_dict.get('arg1', '')
                            end_manifest = one_commit_dict.get('arg2', '')
                            commit_exist = False
                            print(commit_id)
                            if commit_id:
                                commit_exist = self.use_db.query_changelog(
                                    'commit', 'compile_changelog',
                                    start_manifest, end_manifest, commit_id)

                            if commit_id and not commit_exist:
                                self.use_db.insert('compile_changelog',
                                                   one_commit_dict)
                            obj_list.append(one_commit_dict)
                            print(10 * 'into_db')
                            logger.debug(str(one_commit_dict))

                        else:
                            print('没有 tag 提交吗？')
                            logger.info(u'--没有 tag 提交吗？')
                            logger.error(p_name)
                    total_dic[p_name] = obj_list
                elif 'R' == one_project[0]:
                    one_project = one_project.split()
                    p_active, p_name, p_path, p_old, to_branch = \
                        one_project[0], \
                        one_project[1], \
                        one_project[2], \
                        one_project[3], \
                        one_project[4]

                    print(20 * '--')
                    print(p_active, p_name, p_path, p_old, to_branch)
                    name_exist = False
                    if p_name:
                        name_exist = self.use_db.query('project_name',
                                                       'compile_projectname',
                                                       p_name)
                        logger.info(
                            '%s ==>> %s' % (p_name, name_exist))
                    if p_name and not name_exist:
                        insert_data = dict()
                        insert_data['project_name'] = p_name
                        insert_data['is_app_hmi'] = False
                        logger.info(
                            '%s ==>> %s' % (p_name, insert_data))
                        self.use_db.insert('compile_projectname', insert_data)

                    git_commit = 'git log %s -n1' % p_old
                    if 'hmi/app' not in p_name:
                        path = os.path.join(self.gerrit_morrir,
                                            (p_name + '.git'))
                        res_commit = os_execute_command(path, git_commit)
                        if res_commit:
                            one_commit_dict = {}

                            one_commit_dict['project'] = p_name
                            one_commit_dict['arg1'] = self.from_xml
                            one_commit_dict['arg2'] = self.to_xml
                            one_commit_dict['id'] = 0
                            one_commit_dict[
                                'old_version'] = p_active.strip(
                                '\n')
                            one_commit_dict[
                                'new_version'] = p_old.strip(
                                '\n')

                            p_line = re.compile(r'^\s{4}(?P<query>\D+: .*).*')
                            p_commit_first = re.compile(
                                r'^(\[)(\D+)(:)(\D+)(\]) .*')
                            p_annotation = re.compile(r'^\n\n.*\n\n$',
                                                      flags=re.S)
                            one_commit_info_list = res_commit.split(
                                '\n')
                            for line_i in one_commit_info_list:
                                if one_commit_info_list.index(line_i) == 0:
                                    one_commit_dict['commit'] = \
                                        line_i.split()[
                                            1]
                                elif one_commit_info_list.index(
                                        line_i) == 1:
                                    if 'Merge:' in line_i and 'Author' \
                                            not in line_i:
                                        one_commit_dict['Author'] = \
                                            one_commit_info_list[2].split(
                                                ':')[
                                                1].strip(' ')
                                        one_commit_dict['Date'] = \
                                            one_commit_info_list[3].split(
                                                'Date:')[
                                                1].strip(
                                                ' ')
                                    elif 'Merge:' not in line_i \
                                            and 'Author' in line_i:
                                        one_commit_dict['Author'] = \
                                            one_commit_info_list[1].split(
                                                ':')[
                                                1].strip(' ')
                                        one_commit_dict['Date'] = \
                                            one_commit_info_list[2].split(
                                                'Date:')[
                                                1].strip(
                                                ' ')
                                elif one_commit_info_list.index(
                                        line_i) == 4:
                                    fourth = line_i.strip()
                                    if len(fourth) > 0:
                                        one_commit_dict['title'] = fourth
                                    else:
                                        title = one_commit_info_list[
                                            5].strip()
                                        if title:
                                            one_commit_dict['title'] = title
                                        else:
                                            one_commit_dict[
                                                'title'] = 'Merge'

                                else:
                                    first_commit = p_commit_first.match(
                                        line_i)
                                    if first_commit:
                                        first_commit_group = \
                                            first_commit.group()
                                        print(first_commit_group)
                                    else:
                                        # print('else not first')
                                        annotation_text = \
                                            p_annotation.match(line_i)
                                        if annotation_text:
                                            # print('is annotation')
                                            annotation_text_group = \
                                                annotation_text.group()
                                            # print(annotation_text_group)
                                            one_commit_dict[
                                                'annotation'] = \
                                                annotation_text_group.strip(
                                                    '\n\n')
                                        else:
                                            # print('keys...')
                                            key_line = p_line.match(line_i)
                                            if key_line:
                                                key_line_group = \
                                                    key_line.group()
                                                # print(key_line_group)
                                                key_line_group_list = \
                                                    key_line_group.split(
                                                        ':')
                                                # print(key_line_group_list)
                                                one_commit_dict[
                                                    key_line_group_list[
                                                        0].strip()] = \
                                                    key_line_group_list[
                                                        1].strip()

                            commit_id = one_commit_dict.get('commit', '')
                            start_manifest = one_commit_dict.get('arg1', '')
                            end_manifest = one_commit_dict.get('arg2', '')
                            commit_exist = False
                            print(commit_id)
                            if commit_id:
                                commit_exist = self.use_db.query_changelog(
                                    'commit', 'compile_changelog',
                                    start_manifest, end_manifest, commit_id)

                            if commit_id and not commit_exist:
                                self.use_db.insert('compile_changelog',
                                                   one_commit_dict)
                            obj_list.append(one_commit_dict)
                            print(10 * 'into_db')
                            logger.debug(str(one_commit_dict))
                        else:
                            print('没有 commit 提交吗？')
                            logger.info(u'--没有 commit 提交吗？')
                            logger.error(p_name)

                    elif 'hmi/app' in p_name:
                        path = os.path.join(self.gerrit_morrir,
                                            (p_name + '.git'))
                        tmp_tag = os_execute_command(path, git_commit)
                        if tmp_tag:
                            one_commit_info_list = tmp_tag.split('\n')
                            one_commit_dict = {}

                            one_commit_dict['project'] = p_name

                            one_commit_dict['arg1'] = self.from_xml
                            one_commit_dict['arg2'] = self.to_xml
                            one_commit_dict['id'] = 0
                            one_commit_dict[
                                'old_version'] = p_active.strip(
                                '\n')
                            one_commit_dict[
                                'new_version'] = p_old.strip(
                                '\n')
                            # print(one_tag_commit)
                            p_line = re.compile(
                                r'^\s{4}(?P<query>\D+: .*).*')
                            p_commit_first = re.compile(
                                r'^(\[)(\D+)(:)(\D+)(\]) .*')
                            p_annotation = re.compile(r'^\n\n.*\n\n$',
                                                      flags=re.S)

                            for line_i in one_commit_info_list:
                                if one_commit_info_list.index(
                                        line_i) == 0:
                                    one_commit_dict['commit'] = \
                                        line_i.split()[
                                            1]
                                elif one_commit_info_list.index(
                                        line_i) == 1:
                                    if 'Merge:' in line_i and 'Author' \
                                            not in line_i:
                                        one_commit_dict['Author'] = \
                                            one_commit_info_list[
                                                2].split(':')[1].strip(' ')
                                        one_commit_dict['Date'] = \
                                            one_commit_info_list[
                                                3].split('Date:')[1].strip(' ')
                                    elif 'Merge:' not in line_i \
                                            and 'Author' in line_i:
                                        try:
                                            one_commit_dict['Author'] = \
                                                one_commit_info_list[
                                                    1].split(':')[1].strip(' ')
                                        except Exception as e:
                                            print(e)
                                            logger.warning(
                                                one_commit_info_list[0])
                                            logger.warning(line_i)
                                            one_commit_dict['Author'] = \
                                                one_commit_info_list[1]
                                        one_commit_dict['Date'] = \
                                            one_commit_info_list[
                                                2].split('Date:')[1].strip(' ')

                                elif one_commit_info_list.index(
                                        line_i) == 4:
                                    fourth = line_i.strip()
                                    if len(fourth) > 0:
                                        one_commit_dict['title'] = \
                                            fourth
                                    else:
                                        title = one_commit_info_list[
                                            5].strip()
                                        if title:
                                            one_commit_dict['title'] = \
                                                title
                                        else:
                                            one_commit_dict[
                                                'title'] = 'Merge'

                                else:
                                    first_commit = p_commit_first.match(
                                        line_i)
                                    if first_commit:
                                        first_commit_group = \
                                            first_commit.group()
                                        print(first_commit_group)
                                    else:
                                        # print('else not first')
                                        annotation_text = \
                                            p_annotation.match(line_i)
                                        if annotation_text:
                                            # print('is annotation')
                                            annotation_text_group = \
                                                annotation_text.group()
                                            # print(annotation_text_group)
                                            one_commit_dict['annotation'] = \
                                                annotation_text_group.strip(
                                                    '\n\n')
                                        else:
                                            # print('keys...')
                                            key_line = p_line.match(line_i)

                                            if key_line:
                                                key_line_group = \
                                                    key_line.group()
                                                # print(key_line_group)
                                                key_line_group_list = \
                                                    key_line_group.split(':')
                                                one_commit_dict[
                                                    key_line_group_list[
                                                        0].strip()] = \
                                                    key_line_group_list[
                                                        1].strip()

                            commit_id = one_commit_dict.get('commit', '')
                            start_manifest = one_commit_dict.get('arg1', '')
                            end_manifest = one_commit_dict.get('arg2', '')
                            commit_exist = False
                            print(commit_id)
                            if commit_id:
                                commit_exist = self.use_db.query_changelog(
                                    'commit', 'compile_changelog',
                                    start_manifest, end_manifest, commit_id)
                            print('commit_exist', commit_exist)
                            if commit_id and not commit_exist:
                                self.use_db.insert('compile_changelog',
                                                   one_commit_dict)
                            obj_list.append(one_commit_dict)
                            print(10 * 'into_db')
                            logger.debug(str(one_commit_dict))

                        else:
                            print('没有 tag 提交吗？')
                            logger.info(u'--没有 tag 提交吗？')
                            logger.error(p_name)
                    total_dic[p_name] = obj_list
                else:
                    logger.warning('other ==>> %s' % one_project)
            if self.result_to_file:
                if not os.path.exists(self.result_to_file):
                    os_execute_command('/tmp',
                                       ('mkdir -p %s' % self.result_to_file))
                self.output_txt(self.result_to_file, total_dic)
        else:
            logger.error('not diff_manifest list')

    # 分组
    def packet_file(self, file_list, frequency):
        packet_file_list = []

        if file_list and isinstance(file_list, list) and \
                frequency != 1 and isinstance(frequency, int):
            a = 0
            p = re.compile(r'[0-9]{6}')

            for i in file_list:
                arg2 = i
                arg2_num = p.findall(arg2)
                if file_list.index(i) == len(file_list) - 1:
                    break
                else:
                    next_i_num = p.findall(
                        file_list[file_list.index(i) + 1])
                    if arg2_num != next_i_num:
                        arg1 = file_list[file_list.index(i) + 1]
                        # print(a)
                        # print('arg1:', arg1, 'arg2:', arg2)
                        if arg1 and arg2:
                            one_packet = arg1 + ' ' + arg2
                            if one_packet not in packet_file_list:
                                packet_file_list.append(one_packet)
                        else:
                            continue

                    else:
                        continue
                a = a + 1
        elif file_list and isinstance(file_list, list) and \
                frequency == 1 and isinstance(frequency, int):
            p = re.compile(r'[0-9]{6}')
            for i in file_list:
                arg2 = file_list[0]
                arg2_num = p.findall(arg2)
                next_i_num = p.findall(
                    file_list[file_list.index(i) + 1])
                if arg2_num != next_i_num:
                    arg1 = file_list[file_list.index(i) + 1]
                    one_packet = arg1 + ' ' + arg2
                    if one_packet not in packet_file_list:
                        packet_file_list.append(one_packet)
                    break
                else:
                    continue
        else:
            logger.error('must be import file source list')
            raise Exception('must be import file source list')

        return packet_file_list

    # generation 的主函数
    def get_change_log(self):
        if self.mode == 'daily':
            name_res = self.get_differences_source_file()
            if not name_res:
                self.use_db.close()
                logger.error('history mode not name resource data')
                raise Exception('history mode not name resource data')
            # do sth
            logger.debug(name_res.__str__())
            name_src_list = name_res.split('\n')
            # print(name_src_list)
            packet_file_list = self.packet_file(name_src_list, 1)
            print(packet_file_list)
            if len(packet_file_list) == 1:
                from_xml = packet_file_list[0].split()[0]
                to_xml = packet_file_list[0].split()[1]
            else:
                self.use_db.close()
                logger.error("mode daily , can't packet from/to manifest")
                raise Exception("mode daily , can't packet from/to manifest")
            diff_manifest = self.compare_file(from_xml, to_xml)
            self.generate_git_data(diff_manifest)
            # self.use_db.close()
        elif self.mode == 'history':
            _path = os.path.join(self.workspace, '.repo/manifests')

            all_branch_list = os_execute_command(_path, 'git branch -a')
            for one_branch in all_branch_list.split('\n'):
                if one_branch:
                    print('++++' * 20)
                    logger.debug("this branch is %s" % one_branch)
                    print(one_branch, one_branch.split()[-1].split(')')[0])
                    get_manifests = ("git log %s --pretty=oneline | "
                                     "grep 'Daily_build:save' | "
                                     "awk '{print $3}'" % (
                                         one_branch.split()[-1].split(')')[0]))
                    os_execute_command(_path, 'git checkout %s' %
                                       one_branch.split()[-1].split(')')[0])
                    os_execute_command(_path, 'git pull')
                    is_has_daily_build = os_execute_command(_path,
                                                            get_manifests)
                    if not is_has_daily_build:
                        logger.warning("mode history ,branch not daily build "
                                       "==>> %s"
                                       % (one_branch.split()[-1].split(')')[0])
                                       )
                        continue
                    name_res = self.get_differences_source_file(
                        one_branch.split()[-1].split(')')[0])
                    if not name_res:
                        self.use_db.close()
                        logger.error('history mode not name resource data')
                        raise Exception('history mode not name resource data')
                    # do sth
                    logger.debug(name_res.__str__())
                    name_src_list = name_res.split('\n')
                    # print(name_src_list)
                    packet_file_list = self.packet_file(name_src_list,
                                                        len(name_src_list))
                    print(20 * '====')
                    print(packet_file_list)
                    if packet_file_list:
                        for one_packet in packet_file_list:
                            if one_packet:
                                froms_xml = one_packet.split()[0]
                                tos_xml = one_packet.split()[1]
                                print(froms_xml, tos_xml)
                                if froms_xml == 'M01.D.A.B.180717-101.xml' and\
                                                tos_xml == \
                                                'M01.D.A.B.180730-102.xml':
                                    logger.info('M01.D.A.B.180730-102.xml '
                                                '===>>> Congratulations')
                                    print('M01.D.A.B.180730-102.xml'
                                          '===>>> Congratulations')
                                    break
                                else:
                                    diff_manifest = self.compare_file(
                                        froms_xml, tos_xml)
                                    self.generate_git_data(diff_manifest)
                                self.from_xml = None
                                self.to_xml = None
                    else:
                        self.use_db.close()
                        logger.error("mode history , can't packet "
                                     "from/to manifest")
                        raise Exception("mode history , can't packet "
                                        "from/to manifest")
                else:
                    logger.warning("mode history , can't find branch")
                    logger.warning("mode history , can't find branch ==>> ")
                    print("mode history , can't find branch ==>> ")

                self.branch_name = None
        elif self.mode == 'manual':
            print('this manual')
            if len(self.from_xml) == 0 or len(self.to_xml) == 0:
                self.use_db.close()
                logger.error('if choose manual mode, must had '
                             'from/to manifest parameter')
                raise ImportError('if choose manual mode, must had '
                                  'from/to manifest parameter')

            diff_manifest = self.compare_file()
            self.generate_git_data(diff_manifest)
            # self.use_db.close()
        else:
            self.use_db.close()
            logger.error('mode error, choose generation mode')
            raise EOFError('mode error, choose generation mode')

        self.use_db.close()

    # 写到文件
    def output_txt(self, filename, obj):
        arg1 = self.from_xml.split('-')[0]
        p = re.compile(r'[0-9]{6}')
        arg2 = p.findall(self.to_xml)
        name = arg1 + "-" + arg2[0] + '_changelog.txt'
        try:
            js_obj = json.dumps(obj)
        except Exception as e:
            logger.warning(e)
            js_obj = obj
        result = True
        try:
            with open(os.path.join(filename, name), 'a+') as f:
                f.write(js_obj)
        except IOError as e:
            logger.warning(e)
            result = False
        return result


@click.group()
@click.option("--workspace",
              envvar="JENKINS_JOB_WORKSPACE",
              default="",
              type=str,
              help="a working directory, necessary"
                   "(e.g., --workspace '/data/"
                   "daily_build_history_data/')")
@click.option("--branch-name",
              envvar="BRANCH-NAME",
              default="MASTER",
              help="branch of the repo"
                   "(e.g., --branch-name 'MASTER')")
@click.pass_context
def cli(ctx, workspace, branch_name):
    ctx.obj = dict()
    ctx.obj['workspace'] = workspace
    ctx.obj['branch_name'] = branch_name


@cli.command()
@click.option("--gerrit-user",
              envvar="USER-GERRIT",
              default="scm",
              help="username use connection gerrit"
                   "(e.g., --gerrit-user 'scm')")
@click.option("--branch-name",
              envvar="BRANCH-NAME",
              default="master",
              help="branch of the repo"
                   "(e.g., --branch-name 'xxx')")
@click.option("--gerrit-address",
              envvar="ADDRESS-GERRIT",
              default="gerrit.com",
              help="address use connection gerrit"
                   "(e.g., --gerrit-address 'gerritxxx.com')")
@click.option("--gerrit-port",
              envvar="PORT-GERRIT",
              default="2941",
              help="port use connection gerrit"
                   "(e.g., --gerrit-port '294xx')")
@click.option("--manifest-project",
              envvar="MANIFEST-PROJECT",
              default="/platform/manifest",
              help="repo directory of the repo"
                   "(e.g., --manifest-project '/platform/manifest')")
@click.option("--repo-url",
              envvar="REPO-URL",
              default="/git-repo",
              help="repo repository location"
                   "(e.g., --repo-url '/git-repo')")
@click.pass_context
def init(ctx, branch_name, manifest_project, repo_url, gerrit_user,
         gerrit_address, gerrit_port):
    # click.echo(ctx.obj)
    click.echo(20 * '--')
    ctx.obj['user_gerrit'] = gerrit_user
    ctx.obj['address_gerrit'] = gerrit_address
    ctx.obj['port_gerrit'] = gerrit_port
    res = OperationData.init_repo(branch_name=branch_name,
                                  manifest_project=manifest_project,
                                  repo_url=repo_url,
                                  workspace=ctx.obj['workspace'],
                                  user_gerrit=ctx.obj['user_gerrit'],
                                  address_gerrit=ctx.obj['address_gerrit'],
                                  port_gerrit=ctx.obj['port_gerrit']
                                  )
    print(20 * 'init')
    print(res)
    return res


@cli.command()
@click.option("--repositories-base",
              envvar="REPOSITORIES-BASE",
              default="/data/git",
              help="repositories mirror mount base directory"
                   "(e.g., --gerrit-mirror '/data/git')")
@click.option("--mode",
              envvar="MODE",
              type=click.Choice(['manual', 'daily', 'history']),
              help="choose generation mode"
                   "(e.g., --mode 'manual')")
@click.option("--from-manifest",
              envvar="FROM-MANIFEST",
              default="",
              help="if --mode choose manual; diff from manifest.xml, "
                   "(e.g., --from-manifest 'ss1114-74.xml')")
@click.option("--to-manifest",
              envvar="TO-MANIFEST",
              default="",
              help="if --mode choose manual; diff to manifest.xml"
                   "(e.g., --to-manifest '181116-76.xml')")
@click.option("--result-file-path",
              envvar="RESULT-TO-FILE",
              default="",
              help="Has specified file memory to store results, "
                   "save the file path; default generated to db"
                   "(e.g., --result-file-path '/tmp/ep_tools/"
                   "change_log_utils/')")
@click.option("--db-settings-file",
              envvar="DB-SETTINGS-FILE",
              default="",
              type=str,
              help="Database settings information, Under the current code path"
                   " _conf_demo.yaml template."
                   "(e.g., --db-settings-file "
                   "'/etc/change_log_generator/db_config.yaml')")
@click.pass_context
def generate(ctx, repositories_base, mode, result_file_path,
             from_manifest, to_manifest, db_settings_file):
    click.echo(mode)
    _inst = OperationData(workspace=ctx.obj['workspace'],
                          branch_name=ctx.obj['branch_name'],
                          mode=mode,
                          result_to_file=result_file_path,
                          gerrit_mirror=repositories_base,
                          from_manifest=from_manifest,
                          to_manifest=to_manifest,
                          db_settings_file=db_settings_file)
    res = _inst.get_change_log()
    return res


if __name__ == '__main__':
    cli()
