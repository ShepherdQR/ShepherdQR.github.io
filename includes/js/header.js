/*
 * @Author: Shepherd Qirong
 * @Date: 2022-10-06 21:41:23
 * @Github: https://github.com/ShepherdQR
 * @LastEditors: Shepherd Qirong
 * @LastEditTime: 2022-10-14 23:20:38
 * Copyright (c) 2019--20xx Shepherd Qirong. All rights reserved.
 */

function styleHeader(){
    (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
        (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
        m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
                            })(window,document,'script','//www.google-analytics.com/analytics.js','ga');
    ga('create', 'UA-45586344-1', 'shepherd.org');
    ga('send', 'pageview');
}

MathJax = {
    tex: {inlineMath: [['$', '$'], ['\\(', '\\)']]}
};

function supportMobile(){
    if (/mobile/i.test(navigator.userAgent) || /android/i.test(navigator.userAgent))
    {
        document.body.classList.add('mobile');
    }
}

function retrieveTitle(){
    var titleRawURI = location.href;
    var titleRaw = decodeURI(titleRawURI);
    var a = titleRaw.split('/')
    var curTittle = a[a.length - 1];
    //curTittle = curTittle.substring(0,curTittle.length-5);
    curTittle = curTittle.replace(".html", "");
    return curTittle;
}

function writeString(string){
    string = string.replace(/\r\n/g,"<br>")
    string = string.replace(/\n/g,"<br>");
    document.write(string);
}
