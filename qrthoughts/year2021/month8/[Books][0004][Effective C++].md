---
type: Books
id: "0004"
title: "Effective C++"
created: "2021-08-05 15:40:21"
created_date: "2021-08-05"
published: "2021-08-10"
updated: "2021-08-15 22:45:28"
updated_date: "2021-08-15"
slug: "effective-c"
status: "published"
source:
  legacy_path: "qrthoughts/year2021/month8/[Books][0004][Effective C++].html"
  date_source:
    created: "html-comment"
    published: "index-data"
    updated: "html-comment"
migration:
  status: "draft"
  complexity: 1
---
# Effective C++

Acturally I collected the first 3 versions of this book. What I read is about the 2nd version on my cellphone. Acturally I have finished reading it for a couple of months, and almost forget the whole fifty-five ways introduced in the book. I just learned that it seemed is HOUJie who first translated it.


---


I just list some rules that I am not quite familiar with, or those that I think I need to pay attention to. And I decide to keep the 3rd version, so the number below is in 3rd version.


1) 07: Declare destructors virtual in polymorphic base classes. Remind myself to notice that when I write new class.


2) 49: Understand the behavior of the new-handler. I need to think what if the operator new fails if I allocate a huge memory.


3) Try to make the interface completed and small.


4) Avoid overload on pointer and value type, like string* and int.


5) 26: Postpone variable definitions as long as possible.


6) 31: Minimize compilation dependencies between files.


7) 34: Inheritance of interface and inheritance of implimentation.
