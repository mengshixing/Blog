# Blog #
  a blog website with python
   
## Depends ##   
  * Datebase:Mysql  
  * Python Packages:aiohttp(异步框架),jinja2(前端模板引擎),aiomysql(数据库驱动)  
  * frontend:bootstrap3.3.7,Font Awesome(字体图标框架)
 
## Structure ##  
  
    Blog/                    <-- 根目录
    +- backup/               <-- 备份目录
    +- conf/                 <-- 配置文件
    +- dist/                 <-- 打包目录
    +- www/                  <-- Web目录，存放.py文件
    |  +- static/            <-- 存放静态文件
    |  +- templates/         <-- 存放模板文件
    +- ios/                  <-- 存放iOS App工程
    +- LICENSE               <-- 代码LICENSE

## API ##
### 后端API包括：
> 获取日志：GET /blog/{id}  
> 创建日志：POST /api/updateblog 
> 修改日志：POST /api/updateblog/:blog_id  
> 删除日志：POST /api/blogs/:blog_id/delete  
> 获取评论：GET /api/comments  
> 创建评论：POST /api/blogs/:blog_id/comments  
> 删除评论：POST /api/comments/:comment_id/delete  
> 用户注册：POST /api/users  
> 用户登录：POST /api/authenticate 
### 管理页面包括：
> 评论列表页：GET /manage/comments  
> 日志列表页：GET /manage/blogs  
> 创建日志页：GET /create 
> 修改日志页：GET /manage/blogs/  
> 用户列表页：GET /manage/users  
### 用户浏览页面包括：
> 注册页：GET /register   
> 登录页：GET /signin   
> 注销页：GET /signout   
> 首页：GET /   
> 日志详情页：GET /blog/:blog_id      

## contact ##  
  programmer_msx@126.com
