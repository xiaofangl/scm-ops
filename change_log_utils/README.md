### 20181116
#### import_history_daily_build.py
    * - 导入从20181009 -- 运行当天的commit数据；
    * - 执行方法 注意：
        * - 1）需要在workspace下运行， 也可手动指定workspace
        * - 2）如执行 write_history_data 命令则 必须 传入--daily-build-utilities 参数，此参数为 release——notes脚本的路径名称；当前版本使用 scm/manifest_tool 中的compare_file/下的filter_git 和find_desay
    ** **
(ep_tools) ┌─[liuxiaofang@ep_dev-4-60] - [/data/xiaofangl/workspase] - [2018-11-16 02:38:42]
└─[1] <> python /home/liuxiaofang/ep_tools/import_history_data/import_history_daily_build.py
Usage: import_history_daily_build.py [OPTIONS] COMMAND [ARGS]...

Options:
  --workspace TEXT              repo code download path
  --daily-build-utilities TEXT  change log tools deployment path
  --gerrit-url TEXT             gerrit server address
  --branch-name TEXT            repo branch
  --manifest-project TEXT       manifest address
  --git-repo TEXT               repo address
  --help                        Show this message and exit.

Commands:
  init_repo
  write_history_data
(ep_tools) ┌─[liuxiaofang@ep_dev-4-60] - [/data/xiaofangl/workspase] - [2018-11-16 02:38:50]
└─[0] <> python /home/liuxiaofang/ep_tools/import_history_data/import_history_daily_build.py --workspace '/data/xiaofangl/workspase' --daily-build-utilities '/home/liuxiaofang/old_tools' write_history_data


### 20181127
#### change_log_generator

** **
##### 1. 查看命令帮助文档
##### 2. 按代码目录下的_conf_dome.yaml 生成一个自己的DB配置文件；
********************************************************************************
(ep_tools) ┌─[liuxiaofang@ep_dev-4-60] - [~/ep_tools] - [2018-11-30 01:40:25]
└─[1] <> python change_log_utils/change_log_generator.py --help
/tmp/logs_ep_tools
Usage: change_log_generator.py [OPTIONS] COMMAND [ARGS]...

Options:
  --workspace TEXT       a working directory(e.g., --workspace
                         '/data/xiaofangl/daily_build_history_data/')
  --user-gerrit TEXT     username use connection gerrit(e.g., --user-gerrit
                         'chejscm')
  --address-gerrit TEXT  address use connection gerrit(e.g., --address-gerrit
                         'gerrit.it.chehejia.com')
  --port-gerrit TEXT     port use connection gerrit(e.g., --port-gerrit
                         '29418')
  --help                 Show this message and exit.

Commands:
  generate
  init

(ep_tools) ┌─[liuxiaofang@ep_dev-4-60] - [~/ep_tools] - [2018-11-30 01:41:26]
└─[0] <> python change_log_utils/change_log_generator.py generate --help
/tmp/logs_ep_tools
Usage: change_log_generator.py generate [OPTIONS]

Options:
  --repositories-base TEXT       repositories mirror mount base
                                 directory(e.g., --gerrit-mirror '/data/git')
  --mode [manual|daily|history]  choose generation mode(e.g., --mode 'manual')
  --from-manifest TEXT           if --mode choose manual; diff from
                                 manifest.xml, (e.g., --from-manifest
                                 'M01.CHJ.A81.SR3.181114-74.xml')
  --to-manifest TEXT             if --mode choose manual; diff to
                                 manifest.xml(e.g., --to-manifest
                                 'M01.CHJ.A81.SR3.181116-76.xml')
  --result-file-path TEXT        Has specified file memory to store results,
                                 save the file path; default generated to
                                 db(e.g., --result-file-path
                                 '/tmp/ep_tools/change_log_utils/')
  --db-settings-file TEXT        Database settings information, Under the
                                 current code path _conf_dome.yaml
                                 template.(e.g., --db-settings-file
                                 '/etc/change_log_generator/db_config.yaml')
  --help                         Show this message and exit.


(ep_tools) ┌─[liuxiaofang@ep_dev-4-60] - [~/ep_tools] - [2018-11-30 01:40:14]
└─[0] <> python change_log_utils/change_log_generator.py generate --mode daily --db-settings-file '/home/liuxiaofang/ep_tools/change_log_utils/_conf_dome.yaml'

2018-12-10

在主命令中增加版本参数；history支持多版本
(ep_tools) ┌─[liuxiaofang@ep_dev-4-60] - [~/ep_tools] - [2018-12-10 03:34:25]
└─[0] <> python change_log_utils/change_log_generator.py --workspace /tmp/xiaofangl generate --mode daily --result-file-path /tmp/xiaofangl --db-settings-file /tmp/xiaofangl/conf.yaml