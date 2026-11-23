---
title: "Code"
slug: "code"
date: 2026-11-23
author: "Paul G. de Jong"
type: page
status: publish
excerpt: "The open-source Python simulation code behind Orbital Ring Engineering: what the repository holds and how to run it."
---

## The simulation code

The numbers, tables and figures in *Orbital Ring Engineering, Volume I* come from Python code that anyone can download and run. The code is at [github.com/kjpaul/orbitalring](https://github.com/kjpaul/orbitalring), under the MIT license.

## What the repository holds

- `ring_altitude.py` holds the ring that every chapter uses: the 700 km altitude and the numbers that follow from it. Every other script reads it.
- `run_all.py` runs the cases behind the book and writes one log for each into a `runs` folder.
- The other scripts are grouped by subject: the levitation bearing, the linear induction motors that deploy the ring, the mass driver, the anchor lines, the space elevators, power, debris, radiation and the lunar ring.
- `README.md` lists each script beside the chapters it serves.

## How to run it

The code needs Python 3.10 or later. From the repository folder:

```
pip install -r requirements.txt
python run_all.py --list
python run_all.py
```

The first command installs the packages. The second prints the list of cases. The third runs them all, which takes about three hours on a laptop. To run only some of them, use `python run_all.py --only=name,name` with names from the list.

## Change the assumptions

The code is published so that the numbers can be checked. Change an assumption, run the case again, and see what happens to the result. If you find an error in the code or in the book, please report it on the [errata page](/errata/). Improvements to the code are welcome as pull requests on GitHub.

I also plan to publish the MathCAD worksheets behind the derivations.
