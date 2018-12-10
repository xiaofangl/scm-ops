#!/usr/bin/env python
# encoding: utf-8
# author: xiaofangliu
import datetime
import logging
import click
# sys.path.insert(0, os.path.join(os.path.basename(__file__)))
import pymysql
import yaml
from logging_conf import log_init

log_init()
logger = logging.getLogger(__file__)


class MysqlOperation(object):
    def __init__(self, db_settings):
        print('setting ', db_settings)
        self.res = {'status': True}
        if '.yaml' in db_settings:
            with open(db_settings, 'r') as f:
                y = yaml.load(f)
                # print(y)
                if not y:
                    logger.error('please must sure db configure')
                    raise Exception('please must sure db configure')
                self.host = y['ep'].get('host', '')
                self.port = y['ep'].get('port', '')
                self.user = y['ep'].get('user', '')
                self.pawd = y['ep'].get('password', '')
                self.db = y['ep'].get('db', '')

        else:
            logger.error('the db setting must a yaml file %s' % db_settings)
            raise ImportError('the db setting must a yaml file')

        self.now = datetime.datetime.now()
        print('-----' * 20)
        # print('%s %s %s' % (self.host, self.db, self.user))
        logger.debug('%s %s %s' % (self.host, self.db, self.user))
        self.conn = pymysql.connect(host=self.host, user=self.user,
                                    password=self.pawd, db=self.db,
                                    port=self.port, sql_mode=' ')
        logger.info('conn ==>> ')
        self.cur = self.conn.cursor()
        logger.info('cur ==>> ')

    def query(self, field, table_name, conditions):
        status = True
        if isinstance(field, str) and isinstance(table_name, str):
            if table_name == 'ProjectName' or table_name == 'project_name' or \
                    table_name == 'compile_projectname':
                sql = """SELECT %s FROM `compile_projectname`
WHERE project_name=%s"""
                sql_parameters = [field, conditions]
            elif table_name == 'Changelog' or table_name == 'change_log' or \
                    table_name == 'compile_changelog':
                sql = """SELECT %s FROM `compile_changelog`
WHERE `commit`=%s"""
                sql_parameters = [field, conditions]
        else:
            raise ValueError("must be a valid value")

        print(sql)
        logger.debug(sql)
        # logger.debug(conditions)
        try:
            self.cur.execute(sql, sql_parameters)
            res = self.cur.fetchall()
            print(res, type(res))
            if res and isinstance(res, tuple):
                for row in res:
                    if conditions == row[0]:
                        print(conditions, True)
                        status = True
            else:
                status = False

        except Exception as e:
            print(e)
            logger.error('query ==>> ')
            logger.error(e)
        # finally:
        #     self.conn.close()
        logger.info('query status ==>> ')
        logger.info(status)
        return status

    def query_changelog(self, conditions, table_name, start_manifest,
                        end_manifest, commit_id):
        status = True
        if isinstance(conditions, str) and isinstance(table_name, str):

            if table_name == 'Changelog' or table_name == 'change_log' or \
                    table_name == 'compile_changelog':
                sql = """SELECT %s FROM `compile_changelog`
WHERE `commit`=%s and start_manifest=%s and end_manifest=%s"""
                sql_parameters = [conditions, commit_id, start_manifest,
                                  end_manifest]
        else:
            raise ValueError("must be a valid value")

        print(sql)
        print(sql_parameters)
        # logger.debug(sql)
        # logger.debug(conditions)
        try:
            self.cur.execute(sql, sql_parameters)
            res = self.cur.fetchall()
            print(res, type(res))
            if res and isinstance(res, tuple):
                for row in res:
                    if conditions == row[0]:
                        print(conditions, True)
                        status = True
            else:
                status = False

        except Exception as e:
            print(e)
            logger.error('query ==>> ')
            logger.error(e)
        # finally:
        #     self.conn.close()
        logger.info('query status ==>> ')
        logger.info(status)
        return status

    def insert(self, table_name, data):
        """

        :param table_name: 要插入的表名，支持 project_name，change_log，support_base
        :param data: 要插入的字段
        :return:
        """
        sql = ""
        sql_parameters = []
        if isinstance(table_name, str) and isinstance(data, dict):
            if table_name == 'ProjectName' or table_name == 'project_name' or \
                    table_name == 'compile_projectname':
                table_name = 'compile_projectname'
                project_name = data.get('project_name', '')
                is_app_hmi = data.get('is_app_hmi', '')
                description = data.get('description', '')
                is_app_hmi = False if not isinstance(is_app_hmi,
                                                     bool) else is_app_hmi

                sql = """insert into `compile_projectname` (project_name,
description, created) VALUES (%s, %s, %s)"""
                sql_parameters = [project_name, description, self.now]
            elif table_name == 'Changelog' or table_name == 'change_log' or \
                    table_name == 'compile_changelog':
                table_name = 'compile_changelog'
                project = data.get('project', '')
                start_manifest = data.get('arg1', '')
                end_manifest = data.get('arg2', '')

                start_version = data.get('old_version', '')
                end_version = data.get('new_version', '')

                title = data.get('title', '')
                author = data.get('Author', '')
                a_time = data.get('Date', '')
                # number = data.get('id', '')
                commit = data.get('commit', '')
                change_id = data.get('Change-Id', '')
                signed_off_by = data.get('Signed-off-by', '')
                annotation = data.get('annotation', '')

                issue_id = data.get('Issue-Id', '')
                root_cause = data.get('Root-Cause', '')
                bug_introduced_phase = data.get('Bug-Introduced-Phase', '')
                resolution_description = data.get('Resolution-Description', '')
                component = data.get('Component', '')
                # int(number) if not isinstance(number, int) else number
                print('time' * 20)
                print(a_time)
                try:
                    a_time = a_time.split(' +')[0].strip()
                except Exception as e:
                    a_time = a_time
                    logger.warning(e)
                logger.info('change_log_commit_source_time ==>> %s', a_time)
                try:
                    scr_time = datetime.datetime.strptime(a_time,
                                                          "%a %b %d %H:%M:%S "
                                                          "%Y")
                    time = scr_time.strftime('%Y-%m-%d %H:%M:%S')
                except Exception as e:
                    scr_time = datetime.datetime.utcfromtimestamp(0)
                    time = scr_time.strftime('%Y-%m-%d %H:%M:%S')
                    logger.warning(e)
                print(time)
                logger.info('change_log_commit_time ==>> %s', time)
                sql_s = """SELECT `id` FROM `compile_projectname` WHERE
project_name=%s"""
                sql_parameters_s = [project]
                project_id = 1
                self.cur.execute(sql_s, sql_parameters_s)
                res = self.cur.fetchall()
                logger.info('project_id ==>> ')
                # logger.info(res)
                print(res, type(res))
                if res and isinstance(res, tuple):
                    for row in res:
                        project_id = row[0]
                        break

                sql = """insert into `compile_changelog` (project_id,
start_manifest, end_manifest, start_version, end_version, title, author,\
 `time`, `commit`, change_id, signed_off_by, annotation, issue_id, root_cause,
 bug_introduced_phase, \
 resolution_description, component, created) VALUES (%s, %s, %s, %s, %s, %s, \
 %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                sql_parameters = [project_id, start_manifest, end_manifest,
                                  start_version, end_version, title, author,
                                  time, commit, change_id, signed_off_by,
                                  annotation, issue_id, root_cause,
                                  bug_introduced_phase, resolution_description,
                                  component, self.now]
                print(project_id, start_manifest, end_manifest, start_version,
                      end_version, title, author)
            elif table_name == 'SupportBase' or table_name == 'support_base' \
                    or table_name == 'compile_supportbase':
                table_name = 'compile_supportbase'
                start_manifest = data.get('old', '')
                end_manifest = data.get('new', '')
                near_old_version_mcu = data.get('near_old_version_mcu', '')
                near_old_version_ipc = data.get('near_old_version_ipc', '')
                near_new_version_mcu = data.get('near_new_version_mcu', '')
                near_new_version_ipc = data.get('near_new_version_ipc', '')
                near_new_version_android = data.get('near_new_version_android',
                                                    '')
                near_old_version_android = data.get('near_old_version_android',
                                                    '')
                sql = """insert into `compile_supportbase` (start_manifest,
end_manifest, near_old_version_mcu, near_old_version_ipc,\
 near_new_version_mcu, near_new_version_ipc, near_new_version_android,
 near_old_version_android, created) VALUES (%s, %s, %s, %s, %s, %s, %s,
 %s, %s)"""
                sql_parameters = [start_manifest, end_manifest,
                                  near_old_version_mcu,
                                  near_old_version_ipc,
                                  near_new_version_mcu,
                                  near_new_version_ipc,
                                  near_new_version_android,
                                  near_old_version_android,
                                  self.now
                                  ]

        else:
            logger.error("must be a valid value")
            raise ValueError("must be a valid value")
        print(20 * table_name)
        print(sql)
        # logger.debug(sql)
        # logger.debug(sql_parameters)
        logger.info('now ==>> ')
        # logger.info(self.now)
        try:
            result = self.cur.execute(sql, sql_parameters)
            insert_id = self.conn.insert_id()  # 插入成功后返回的id
            self.conn.commit()
            if result:
                print(u"插入成功", insert_id)
                insert_id = insert_id + 1
                logger.info('insert_id ===>>> insert success')
                # logger.info(insert_id)
                # logger.info('insert ===>>> ', result)
        except Exception as e:
            self.conn.rollback()
            logger.error('insert error ==>> insert faild')
            logger.error(e)
            print(e)
            # finally:
            #     self.conn.close()

    def delete(self):
        pass

    def close(self):
        self.cur.close()
        self.conn.close()
        logger.warning('this is close...')


@click.command()
@click.option("--db-settings-file",
              envvar="DB-SETTINGS-FILE",
              default="",
              type=str,
              help="Database settings information, Under the current code path"
                   " _conf_demo.yaml template."
                   "(e.g., --db-settings-file "
                   "'/etc/change_log_generation/db_config.yaml')")
@click.pass_context
def main(ctx, db_settings_file):
    click.echo(ctx)
    click.echo(db_settings_file)
    opera_db = MysqlOperation(db_settings_file)
    return opera_db


if __name__ == '__main__':
    res = main()
    print(res)
