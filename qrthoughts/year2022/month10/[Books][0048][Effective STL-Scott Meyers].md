---
type: Books
id: "0048"
title: "Effective STL-Scott Meyers"
created: "2022-06-02 22:41:25"
created_date: "2022-06-02"
published: "2022-10-08"
updated: "2022-10-08 23:00:34"
updated_date: "2022-10-08"
slug: "effective-stl-scott-meyers"
status: "published"
source:
  legacy_path: "qrthoughts/year2022/month10/[Books][0048][Effective STL-Scott Meyers].html"
  date_source:
    created: "html-comment"
    published: "index-data"
    updated: "html-comment"
migration:
  status: "draft"
  complexity: 1
---
# Effective STL-Scott Meyers

50 Specific ways to improve your use of the standard template library.


---


连续内存容器，vector, string, deque; 基于节点的容器，在插入和删除时不会引起迭代器、指针、引用的失效。


判断式（返回bool的）一般是纯函数，没有状态。


for_each(vec.bagin(),vec.end(),mem_fun(&A::test));


//元素从data复制到d前端，每个增加42:
transform(data, data+number,
insert(d,d.begin()), bind2nd(plus < double >(), 42));


实践中，完全平衡树效率总体不如红黑树。


find算法用的是相等，find成员函数用的是等价。


greater < double > ::operator()是内联的，实例化sort时展开。


函数指针做参数会抑制内联。


不要写容易写，不容易读的代码。
