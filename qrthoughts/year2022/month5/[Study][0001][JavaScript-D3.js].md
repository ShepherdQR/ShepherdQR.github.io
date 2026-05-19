---
type: Study
id: "0001"
title: "JavaScript-D3.js"
created: "2021-08-05 15:40:21"
created_date: "2021-08-05"
published: "2022-05-08"
updated: "2022-05-02 00:27:31"
updated_date: "2022-05-02"
slug: "javascript-d3-js"
status: "published"
source:
  legacy_path: "qrthoughts/year2022/month5/[Study][0001][JavaScript-D3.js].html"
  date_source:
    created: "html-comment"
    published: "index-data"
    updated: "html-comment"
migration:
  status: "draft"
  complexity: 4
---
# JavaScript-D3.js

可视化库。


---


学习。


<svg width = "400px" height = "20px">
        <!--  H 10, reach coordinate H10 -->
        <path d="M 10 10 H 390 V 19 H 10 L 10 10" /> 
    </svg>


Fig001, basic test. On 20220505_14:15, first picture using D3.


<svg width = "960" height = "300" id = "mainsvg" class = "svgs">
        <rect id="my_rect" 
      x="10" y="200" width="200" height="30" 
      stroke="black" fill="#69b3a2" stroke-width="1"
      />
    </svg>


<script>

    let mainsvg = d3.select("#mainsvg");

    let maingroup = mainsvg
        .append('g')
        .attr('transform', `translate(${100}, ${100})`);

        let circle = maingroup
        .append('circle')
        .attr('stroke', 'black')
        .attr('r', '66')
        .attr('fill', 'yellow');
    </script>
