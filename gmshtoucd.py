#!/usr/bin/env python

"""
gmshtoucd - converts Gmsh mesh files into unstructured cell data format

Copyright (C) 2002-2010 Werner Scholz, Richard Boardman, Hans Fangohr

gmshtoucd is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2

gmshtoucd is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
for more details.

You should have received a copy of the GNU General Public License
along with magpar; if not, write to the Free Software Foundation,
Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

This program was designed for magpar, so results may
vary when used with other programs accepting AVS/UCD
as an input file format

This program is based on ngtoucd by Richard Boardman, Hans Fangohr.

"""

VERSION="0.1"

import os, string, sys, time

def readmesh(filename):
    """This will read the Gmsh mesh 'filename' and return
    points, tetrahedra and triangles"""

    # expected Gmsh msh file format:
    # http://www.geuz.org/gmsh/doc/texinfo/gmsh_10.html#SEC62
    
    f = open(filename, 'r')

    #################################################################
    #
    # read the first line to get the number of points
    #
    #################################################################

    thisline = f.readline()
    if thisline != "$MeshFormat\n" :
        bail("Unexpected input " + thisline)

    thisline = f.readline()
    segments  = string.split(thisline[:-1])
    # `.msh' file format, version 2.0
    if segments[0] != "2" and segments[0] != "2.1" and segments[0] != "2.2":
      bail("Unexpected input " + thisline)
    # file-type: ASCII format
    if int(segments[1])!=0 :
      bail("Unexpected input " + thisline)
    # data-size (ignored)

    thisline = f.readline()
    if thisline != "$EndMeshFormat\n" :
        bail("Unexpected input " + thisline)

    #################################################################
    #
    # read the points
    #
    #################################################################

    thisline = f.readline()
    if thisline != "$Nodes\n" :
        bail("Unexpected input " + thisline)
      
    thisline = f.readline()
    number_of_points = int(thisline)

    points = []

    for i in range(number_of_points):
        thisline  = f.readline()
        segments  = string.split(thisline[:-1])
        thispoint = list(map(lambda p: float(p), segments[1:4]))
        points.append(thispoint)

    thisline = f.readline()
    if thisline != "$EndNodes\n" :
        bail("Unexpected input " + thisline)
      
    #################################################################
    #
    # now read all the volume elements
    # first, ascertain the number of volume elements
    #
    #################################################################

    thisline = f.readline()
    if thisline != "$Elements\n" :
        bail("Unexpected input " + thisline)
      
    thisline             = f.readline()
    number_of_elements   = int(thisline)

    #################################################################
    #
    # then read and populate, keeping track
    # of the tetrahedra subdomain
    #
    #################################################################
    
    triangles           = []
    triangles_subdomain = []

    tetrahedra           = []
    tetrahedra_subdomain = []

    triangles_id=0
    tetrahedra_id=0

    for i in range(number_of_elements):
        thisline = f.readline()
        segments = string.split(thisline[:-1])
        tags = int(segments[2])

        # element type 2: 3 node triangle
        if int(segments[1]) == 2 :
            segments = string.split(thisline[:-1])
            if len(segments) != 6+tags:
                print "Found", len(segments), "elements, but expected ", 6+tags
                print segments
                raise "Oops", "File format error"

            triangles_subdomain.append(triangles_id)
            # similar adjustment for materials as with tetrahedra
            triangle = [list(map(lambda t : int(t)-1, segments[3+tags:5+tags])), int(segments[3])]
            triangles.append(triangle)
            triangles_id=triangles_id+1

        # element type 4: 4 node tetrahedron
        if int(segments[1]) == 4 :
            if len(segments) != 7+tags:
                print "Found", len(segments), "elements, but expected ", 7+tags
                print segments
                raise "Oops", "File format error"

            tetrahedra_subdomain.append(tetrahedra_id)

            # rpb, 17th March 2006 - updated to handle materials (note:
            # in Gmsh these are top-level objects [tlos])
            # original mapping was [a, b, c, d] (where a-d are points)
            # new mapping is [[a,b,c,d],m] (where m is a material ID)
            tetrahedron = [list(map(lambda t : int(t)-1, segments[3+tags:7+tags])), int(segments[3])]

            # Gmsh counts from 1 rather than from 0, hence int(t)-1

            tetrahedra.append(tetrahedron)
            tetrahedra_id=tetrahedra_id+1

    thisline = f.readline()
    if thisline != "$EndElements\n" :
        bail("Unexpected input " + thisline)
      
    #################################################################
    #
    # send back the read mesh
    #
    #################################################################
    
    return (points, tetrahedra, triangles, tetrahedra_subdomain, triangles_subdomain)

def bail(message="Sorry, I don't understand. Bailing out..."):
    """A 'get-out' clause"""
    print message
    sys.exit(1)

def initialise_file(file):
    """Attempt to remove the file first to avoid append issues"""
    try:
        os.remove(file)
    except:
        # no problem
        pass

def writeln(line, file):
    """One-shot file line append; this keeps the code terse"""
    f = open(file, 'a')
    f.write(line + '\n')
    f.close()

def stamp():
    """Format a time and a date for stdout feedback"""
    thistime = time.localtime()
    return "[%04d/%02d/%02d %02d:%02d:%02d] " % (thistime[0],
                                                 thistime[1],
                                                 thistime[2],
                                                 thistime[3],
                                                 thistime[4],
                                                 thistime[5])


def info():
    """Output GPL details"""
    print """gmshtoucd, Copyright (C) 2002-2010
             Werner Scholz, Richard Boardman, Hans Fangohr
             gmshtoucd comes with ABSOLUTELY NO WARRANTY;
             for details see the file COPYING"""

def writeucd():
    """Call readmesh to read the Gmsh mesh, then convert and write the UCD mesh"""
    al = len(sys.argv)
    if al < 2 or al > 3 or sys.argv[1] == '--help' or sys.argv[1] == '-h':
        bail("Usage: " + sys.argv[0] + " gmsh.msh [ucdmesh.inp]")

    inputfile = sys.argv[1]

    if len(sys.argv) == 3:
        outputfile = sys.argv[2]
    else:
        outputfile = os.path.splitext(inputfile)[0] + ".inp"

    print
    print "About to read, check and process the gmsh file ", inputfile
    print "and then create the AVS/UCD mesh", outputfile
    print

    print stamp() + "Initialising file" + outputfile
    initialise_file(outputfile)
    print stamp() + "File " + outputfile + " initialised"

    print stamp() + "Attemping read of input " + inputfile
    (points, tetrahedra, triangles, tetrasub, trisub) = readmesh(inputfile)
    print stamp() + "Input file successfully read"

    print stamp() + "Points:     %d" % len(points)
    print stamp() + "Tetrahedra: %d [%d in subdomain]" % (len(tetrahedra), len(tetrasub))
    print stamp() + "Triangles:  %d [%d in subdomain]" % (len(triangles),  len(trisub))

    #################################################################
    #
    # the first line of a UCD file reads:
    # a b c d e
    #
    # where a is the number of nodes
    #       b is the number of cells
    #       c is the length of vector data associated with the nodes
    #       d is the length of vector data associated with the cells
    #       e is the length of vector data associated with the model
    #
    # example: 12 2 1 0 0
    #
    #################################################################

    # n.b. here the third integer indicates the number of placeholders
    
    print stamp() + "Creating descriptor [UCD]"
    writeln(str(len(points)) + " " + str(len(tetrahedra)) + " 3 0 0", outputfile)
    print stamp() + "UCD descriptor created"
    
    #################################################################
    #
    # then we have nodes in threespace, one line per node
    # n x y z
    # where n is the node ID -- integer (not necessarily sequential)
    #       x,y,z are the x, y and z coordinates
    #
    #################################################################

    print stamp() + "Now converting nodes"
    for i in range(len(points)):
        x, y, z = points[i][0], points[i][1], points[i][2]
        writeln(str(i+1) + " " + str(x) + " " + str(y) + " " + str(z), outputfile)
    print stamp() + "Nodes converted"

    #################################################################
    #
    # now the cells, one line/cell:
    #
    # c m t n1 n2 ... nn
    #
    # where c is the cell ID
    #       m is the material type (int, leave as 1 if we don't care)
    #       t is the cell type (prism|hex|pyr|tet|quad|tri|line|pt)
    #       n1...nn is a node ID list corresponding to cell vertices
    #
    #################################################################

    cellctr = 0

    print stamp() + "Converting tetrahedra"

    for tetra in tetrahedra:
        tet = tetra[0] # just the tetrahedron; tetra[1] is the material
        tetorder  = [0, 1, 2, 3]
        tetstring =  " " + str(tet[tetorder[0]]+1)
        tetstring += " " + str(tet[tetorder[1]]+1)
        tetstring += " " + str(tet[tetorder[2]]+1)
        tetstring += " " + str(tet[tetorder[3]]+1)
        writeln(str(cellctr+1) + " " + str(tetra[1]+1) + " tet" + tetstring, outputfile)
        cellctr   += 1

    print stamp() + "Tetrahedra converted"

    #################################################################
    #
    # uncomment the following section to convert triangles as well
    # - since magpar will ignore these, leave away for the time being
    #
    # print stamp() + "Converting triangles"
    #
    # cellctr = 0
    # for triang in triangles:
    #     tri = triang[0] # just the triangle; triang[1] is the material
    #     tristring = ""
    #     for node in tri:
    #         tristring += " " + str(node+1)
    #     writeln(str(cellctr+1) + " " + str(triang[1]) + " tri" + ts, outputfile)
    #
    # print stamp() + "Triangles converted"
    #
    #################################################################

    #################################################################
    #
    # for the data vector associated with the nodes:
    #
    # first line tells us into which components the vector is divided
    #
    #   example: vector of 5 floats could be 3 3 1 1
    #            node scalar could be 1 1
    #
    # next lines, for each data component, use a cs label/unit pair
    #
    #   example: temperature, kelvin
    #
    # subsequent lines, for each node, the vector of associated data
    # in this order
    #
    #   example: 1 10\n2 15\n3 12.4\n4 9
    #
    #################################################################

    print stamp() + "Initialising placeholders"

    writeln("3 1 1 1", outputfile)
    writeln("M_x, none", outputfile)
    writeln("M_y, none", outputfile)
    writeln("M_z, none", outputfile)
    
    #################################################################
    #
    # create some initial scalar values; here, generally
    # +x=1.0 +y=+z=0.01*x (everything else)="\epsilon"
    #
    #################################################################

    scalarstring =  " 1.0 0.0 0.0"

    for i in range(len(points)):
        writeln(str(i+1) + scalarstring, outputfile)

    print stamp() + "Placeholders inserted"

    # all done

    print stamp() + "All finished"


    
if __name__=="__main__":
    writeucd()
