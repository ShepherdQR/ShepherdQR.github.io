---
type: Books
id: "0002"
title: "图灵程序设计丛书"
created: "2022-06-02 22:41:25"
created_date: "2022-06-02"
published: "2021-08-08"
updated: "2023-03-18 15:13:24"
updated_date: "2023-03-18"
slug: "books-0002"
status: "published"
source:
  legacy_path: "qrthoughts/year2021/month8/[Books][0002][图灵程序设计丛书].html"
  date_source:
    created: "html-comment"
    published: "index-data"
    updated: "html-comment"
migration:
  status: "draft"
  complexity: 2
---
# 图灵程序设计丛书

图灵程序设计丛书


---


核心知识收集在latex中。这里罗列总体目录和心得。


---


- The Pragmatic Programmers


20210808整理完。Number 3 book of TURING serious. And the writer describes 75 problems.


---


The last several probles are interesting. We also learn that some websites offer public apis.


---


- The Principles of Programming


20210808整理完。

This is the second book of TURING serious. And the writer introduced 101 rules about programming.


---


Only write what is needed right now.
The connection in database, database config defination file, code source file, leads to the repeating codes problem. No good way to deal this. We can just put the consioning files together.
The abstraction has difficult levels, we need to seperate high level and lower levels.
[Seal] gather the relative elements(like data and functions).
The codes with close relationship should be gathered together as a module. Those modules that called each other frequently, should be rethinking whether the elements should be gathered into one module.
[Hide information] hide the internal state and functions of the module, prevent accessing to the internal elements from outside.
architecture techniques, abstract, seal, informationHide, package, the seperation of strage and implimentation, the seperation of interface and implimentation.
Strategy module offers parameters to the upper UI modules or the implimentation modules.
When the software goes wrong, it should immediately stop.
Write some codes that are used to generate coeds.
Build a prototype as soon as possible. Prototype shows the basic interface or UI and it must be throw and recode when the program is tested ok. While the key born of the software which we then immediately wtire, is the structure of the software, and its shape is the structure of the software.
Choose portability over efficiency.
A software turns the input into output, it works like a filter.
[Coupling] 1)Modules share the same resource files, or the same public data.
2)Module A using the public functions that defined in module B, the functions may contain parameters defined in module B.
3)Data coupling, only data transfer between difficult modules.

Idempotence. like function abs, no matter how many times we apply the function on the target, the output does not change. Like the Get in HTTP, no matter we get successfully or failed, we can just get again.

When we meet a problem, we repeat the problem to others, like our clothes, our cup or something, we clearly explain the problem, this helps us understand teh problem, its details and key point.
Thinking about the title, the paragraph subtitle, helps us effeciently understand the meaning of the paragraphs below.

Architecture follows the organization structure. We should design a good architecture.
The 80 percent need can be easily implemented, while 10 percent can be achieved, and 10 percent can hardly be  achieved.

Joshua tree principle: we ignore those things that we donnot know the name.
The second version of the software always contains too much useless functions. Feature Creep.

Donot reinvent wheels.

When we go farther, we must always keep in mind our origional purpose.


---


- 我的第一本算法书


20230318整理。


---


【数据结构】
链表、数组、栈、队列、哈希表、堆（上浮和下沉，用于实现priority queues）

二叉查找树：
1）左子树的值 R0;
L1 = R0,R1 = L0 mod R0；
一直到Lk, Rk,Rk = 0,Lk = gcd(L0， R0)

质数判断
1）根据定义枚举：计算A的平方根n，i:[2,n]，r[i] = A mod i;r[i]中有0表示有公因数，即不是质数。
2）费马测试：对于质数p，任意小于p的数c，有(c^p)mod(p) = c。测试A，随机找几个小于A的数，判断通过费马测试，大概率认为是质数。
3）存在满足费马测试的合数，称为Carmichael Numbers，绝对伪质数，如561.
4）AKS算法，多项式时间内进行质数测试。


PageRank
1）利用网页间的链接关系判断网页的价值。
2）A链接指向x个网页，x个网页评分A的权重；A被y个网页指向，A的评分等于来的各个网页的权重之和；为了解决循环链接，引入随机游走，即有a的概率跳到其他的节点，有1-a的概率沿着链接关系走。

汉诺塔问题:递归
1）移动方法F满足：F（n）=F（F（n-1))
