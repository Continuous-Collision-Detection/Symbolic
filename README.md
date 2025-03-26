# Symbolic CCD

_Symbolic Continuous Collision Detection (CCD) using Mathematica._

## Contents

* `src`:
    * `roots_ee.wl`/`roots_vf.wl`: Mathematica sources for computing the CCD roots
    * `compare_toi.wl`: Utility for comparing TOI accuracy
* `scripts`: Python scripts we used to process our dataset
    * These scripts call the Mathematica code using the `wolframclient` package
* `hpc`: Scripts designed for an HPC environment where jobs can be dispatched to process queries

## Usage

The source files `roots_ee.wl` and `roots_vf.wl` each contains a `root` function that performs CCD using symbolic mathematics and returns a Boolean answer. Optionally, you can provide an `outfile` argument to save the symbolic expressions for the roots to a `.wxf` Mathematica file. 

The input data is an 8x6 matrix of integers where each row represents a vertex position and every two columns represent the x/y/z coordinates as a rational number (numerator and denominator pair). The order of the rows is:

* Edge-edge queries: `ea0_t0`, `ea1_t0`, `eb0_t0`, `eb1_t0`, `ea0_t1`, `ea1_t1`, `eb0_t1`, `eb1_t1` where `a` or `b` indicates which edge, `0` or `1` indicates the end-point of the edge, and `t0` or `t1` indicates the starting or ending positions of the edge.
* Vertex-face queries: `v_t0`, `f0_t0`, `f1_t0`, `f2_t0`, `v_t1`, `f0_t1`, `f1_t1`, `f2_t1` where `v` indicates the vertex, `f0`, `f1`, or `f2` indicates the face vertices, and `t0` or `t1` indicates the starting or ending positions of the vertex.

Each pair of columns (`1`/`2`, `3`/`4`, and `5`/`6`) comprise a single rational number for the `x`, `y`, and `z` coordinates of the vertex, respectively.
