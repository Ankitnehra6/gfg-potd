# GfG problem of the day

Daily problem-of-the-day solutions from [GeeksforGeeks](https://www.geeksforgeeks.org/profile/ankitnehra20cse),
organised by difficulty. One commit per problem, named after the problem — so `git log` is a
record of what was actually solved.

```bash
./potd "Kadane's Algorithm" medium Solution.java   # file you already wrote
./potd "Trapping Rain Water" hard                  # opens an editor, then commits
```

The script refuses to commit a file containing nothing but comments. A daily commit that proves
nothing is worse than no commit.

---

## Current record

<!-- stats:start -->

<div align="center">

| Problems solved | Coding score | Institute rank | Longest streak |
|:---:|:---:|:---:|:---:|
| **524** | **1804** | **#4** | **24 days** |

</div>

68 problems-of-the-day solved · current streak 7 days · BML Munjal University (BMU) Gurgaon

[→ GeeksforGeeks profile](https://www.geeksforgeeks.org/profile/ankitnehra20cse)

<sub>Updated 13 Sep 2026 · refreshed daily by [stats.yml](.github/workflows/stats.yml)</sub>

<!-- stats:end -->

---

## Layout

```
solutions/
  hard/      medium/      easy/      basic/      school/
scripts/stats.py     reads the profile, rewrites the block above
.github/workflows/   refreshes it daily
```

`scripts/stats.py` needs no dependencies. GfG has no public stats API, but the profile page is
server-rendered and the numbers are already in the HTML payload before any JavaScript runs, so a
plain request is enough. It commits only when a number actually changed.
