# This Project was fully vibe-coded, I just wanted this graph, and I thought many other people would also.

What this does, is it displays a graph of how much you've been training over the last year. It combines many different platforms. Mainly:
- Codeforces
- Atcoder
- DMOJ
- OJ.US
- Leetcode
- Orac2.info (niche)

To use this tool, simply replace the usernames at the bottom with your own. (lines 288 - 293).
Say your handle was tourist, you would replace it with:

```python
"cf": "tourist",
"atcoder": "tourist",
"dmoj": "tourist",
"ojuz": "tourist",
"leetcode": "",
"orac": False
```

To run it, download the appropriate python files with 
```
pip install matplotlib numpy pandas requests seaborn beautifulsoup4
```

And then simply run the file, and it should display the graph.
