算法组实体识别使用

从google code官网下载protobuf源码

$./configure --prefix=/usr/local/protobuf
$ make
$ make check
$ make install

到此步还没有安装完毕，在/etc/profile 或者用户目录 ~/.bash_profile
添加下面内容
####### add protobuf lib path ########
#(动态库搜索路径) 程序加载运行期间查找动态链接库时指定除了系统默认路径之外的其他路径
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/protobuf/lib/
#(静态库搜索路径) 程序编译期间查找动态链接库时指定查找共享库的路径
export LIBRARY_PATH=$LIBRARY_PATH:/usr/local/protobuf/lib/
#执行程序搜索路径
export PATH=$PATH:/usr/local/protobuf/bin/
#c程序头文件搜索路径
export C_INCLUDE_PATH=$C_INCLUDE_PATH:/usr/local/protobuf/include/
#c++程序头文件搜索路径
export CPLUS_INCLUDE_PATH=$CPLUS_INCLUDE_PATH:/usr/local/protobuf/include/
#pkg-config 路径
export PKG_CONFIG_PATH=/usr/local/protobuf/lib/pkgconfig/
######################################





继续安装protobuf的Python模块(如果不用python，可跳过这一步)
#cd ./python
#python setup.py build
#python setup.py test
#python setup.py install

5. 安装完成，验证Linux命令
#protoc –version
6. 验证Python模块是否被正确安装
#python
>>>import google.protobuf
如果没有报错，说明安装正常。

pip install grpcio
安装grpc模块


运行目录下 test_extract文件 若安装正确的话 可正常返回结果
Client received: {"ner_list":{"TIME":["2016年09月13日","05:00"],"ORGANIZATION":["招商银行股份有限公司","经银河基金管理有限公司","百度"]}}

