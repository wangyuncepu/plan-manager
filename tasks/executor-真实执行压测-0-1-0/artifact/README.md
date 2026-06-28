# calc — executor stress-test artifact

Self-contained demo built by PLA-011 to stress-test the executor loop
(Ralph iteration, iterations.log, checkpoint, crash recovery, velocity).

- `calc.py` — add / divide (ValueError on /0)
- `test_calc.py` — unittest, 3 cases

Run: `python3 -m unittest test_calc`
