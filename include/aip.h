/* Area of intersecting polygons
 * -----------------------------
 * Adapted from Norman Hardy's excellent implementation
 * http://www.cap-lore.com/MathPhys/IP/aip.c
 *
 * Computes the integral over the plane of the product of the winding numbers
 * of two polygons.
 *
 * Uses "Simulation of simplicity" to handle geometric degenericy.
 * See: Herbert Edelsbrunner and Ernst Peter
 *      Simulation of simplicity: a technique to cope with degenerate cases in geometric algorithms.
 *      ACM Trans. Graph. 9, 1 (January 1990), 66-104.
 *      DOI: 10.1145/77635.77639 
 *
 * Author: Nathan Clack <clackn@janelia.hhmi.org>
 * Date  : May 2009 
 *
 * Copyright 2010 Howard Hughes Medical Institute.
 * All rights reserved.
 * Use is subject to Janelia Farm Research Campus Software Copyright 1.1
 * license terms (http://license.janelia.org/license/jfrc_copyright_1_1.html).
 */
#ifndef H_AIP
#define H_AIP

#include <stdio.h>
typedef float real; // could be double.
#define C const
#define bigReal 1.E38f  // FLT_MAX, DBL_MAX if double above
#include <limits.h>

typedef struct _point {real x; real y;}                       point;
typedef struct _box   {point min; point max;}                 box;
typedef long long                                             hp;
typedef struct ipoint {long x; long y;}                       ipoint;
typedef struct rng    {long mn; long mx;}                     rng;
typedef struct vertex {ipoint ip; rng rx; rng ry; short in;}  vertex;

real inter(point * a, int na, point * b, int nb);

#endif // H_AIP
