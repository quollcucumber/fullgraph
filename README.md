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
If you don't have a specific account on one of these, simply leave it blank.

To run it, download the appropriate python files with 
```
pip install matplotlib numpy pandas requests seaborn beautifulsoup4
```

And then simply run the file, and it should display the graph.

<h3> If you are in the group of like 10 people who actually have an orac2.info account: </h3>

(steps for firefox, I presume other browsers are similar)

1. Log into your orac acount
2. Go to https://orac2.info/hub/allsubs/1
3. Click f12/inspect(Q)
4. Go to the storage tab
5. Copy the value in SessionId, Value
6. Change line 15 to what is intuitive.
7. Run

If you've never used/even heard of orac2.info, you should make an account, it's got lots of amazing problems!

Here's my graph:
<img width="1593" height="375" alt="Screenshot from 2026-06-21 21-26-18" src="https://github.com/user-attachments/assets/0820109e-290a-411f-bf13-816e6a92b41e" />
