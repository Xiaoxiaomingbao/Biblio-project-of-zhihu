# Biblio-project-of-zhihu

本项目用于连续下载知乎电子书网页，并将其制成epub格式。

第一步：利用Chrome插件SingleFile连续下载电子书网页（还有contents.html）至一个文件夹中，这一步可以利用程序continue_download_SingleFile v1.0.py，也可以手动进行。

第二步：以main.py为入口。从contents.html中提取目录，对其他HTML文件进行除冗（除去无用多余的代码）、base64编码转图片文件等操作。最终形成一个大文件夹（用书名命名）。

第三步：以set_opf.py为入口。添加epub必需的content.opf、toc.ncx等文件。

第四步：如果需要修改电子书的跳注链接，运行hetero_notes v2.0.py。

第五步：将大文件夹中的内容压缩为zip文件，修改扩展名为epub。

第六步：由于不同阅读器对epub格式标准的要求不同，最好再用Sigil对epub文件进行修正。主要是完善元数据和重置封面。

以上只是大致流程，欲知详情请参见我在telegram频道上发布的图文教程https://t.me/BiblioBiblioBiblio/84
