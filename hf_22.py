import numpy as np
import collections
from scipy.special import comb
from scipy.special import factorial2
#from scipy.special import factorial12
from scipy.special import factorial
import copy 
from scipy.linalg import eigh
import argparse
from scipy import linalg
from scipy import special
import random

#loading things, parsing arguments
def parse_args():
    parser  = argparse.ArgumentParser(description="Input")
    parser.add_argument("-xyz", "--xyz", help="Xyz file. Default inp.xyz ", type=str, default="inp.xyz")
    parser.add_argument("-basis", "--basis", help="basis file. Default sto-3g.1.gbs ", type=str, default="sto-3g.1.gbs")
    args = parser.parse_args()
    return args
file_name = parse_args().xyz
basis_name = parse_args().basis

aolist = []
atomlist = []
#atomtype = []
aodict = collections.defaultdict(list)
atom_coords = []
def xyz_reader(file_name):
    print(file_name)
    file = open(file_name, 'r')
    number_of_atoms = 0
    atom_type = []

    for index, line in enumerate(file):
        if index == 0:
            try:
                number_of_atoms = line.split()[0]
            except:
                print("xyz file is wrong. have a number of atoms first")
        if index == 1:
            print("index is 1")
            continue
        if index != 0:
            atom = line.split()[0]
            print(atom)
            coords = [float(line.split()[1])*1.8897261339213, float(line.split()[2])*1.8897261339213, float(line.split()[3])*1.8897261339213]
            print(coords)
            atom_type.append(atom)
            #atomtype.append(atom)
            atom_coords.append(coords)
            atomlist.append((atom, coords))

            if atom in aodict:
                for ao in aodict[atom]:
                    print("basis", ao)
                    aonew = copy.copy(ao)
                    aonew.center = [coords[0],coords[1],coords[2]]
                    aolist.append(aonew)
    file.close()
    #print(atom_type, atom_coords)
    return number_of_atoms, atom_type, atom_coords




orbital_quantum_dict = {"S": (0, 0, 0), "Px": (1, 0, 0), "Py": (0, 1, 0), "Pz": (0, 0, 1), "Dx": (2, 0, 0),
                         "Dx": (2, 0, 0), "Dy": (0, 2, 0),"Dz": (0, 0, 2), "Dxy": (1, 1, 0),"Dyz": (0, 1, 1),
                         "Dxz": (1, 0, 1),}

atomic_charge_dict = {"H": 1, "C": 6, "N": 7, "O": 8, "He": 2, "Li": 3, "Be": 2, "B": 5, "F": 9, "Ne": 10}

def basis_reader(file_name):
    print(file_name)
    basis = open(file_name, 'r')
    newatomtype = False
    contract_num = None
    origin = (0,0,0)
    orbitalType = None
    for line in basis:
        if line.strip() == "****":
            newatomtype = True
            linecount = 0
        if line.strip() == "H     0":
            newatomtype = True
            linecount = 1
            atomtype, _ = line.split()
        elif line.strip() != "****" and newatomtype == True:
            if linecount == 0:
                #print("line 0")
                atomtype, _ = line.split()
                linecount += 1
                #print(atomtype)
            elif linecount == 1:
                #print(line.split())
                orbitalType, contract_num, _ = line.split()
                contract_num = int(contract_num)
                if orbitalType == "S":
                    aos = Ao(origin, (0,0,0), contract_num)
                    aodict[atomtype].append(aos)
                elif orbitalType == "P":
                    aopx = Ao(origin,(1,0,0), contract_num)
                    aopy = Ao(origin,(0,1,0), contract_num)
                    aopz = Ao(origin,(0,0,1), contract_num)
                    aodict[atomtype].append(aopx)
                    aodict[atomtype].append(aopy)
                    aodict[atomtype].append(aopz)
                elif orbitalType == "D":
                    aodx2 = Ao(origin,(2,0,0), contract_num)
                    aody2 = Ao(origin,(0,2,0), contract_num)
                    aodz2 = Ao(origin,(0,0,2), contract_num)
                    aodxy = Ao(origin,(1,1,0), contract_num)
                    aodyz = Ao(origin,(0,1,1), contract_num)
                    aodzx = Ao(origin,(1,0,1), contract_num)
                    aodict[atomtype].append(aodx2)
                    aodict[atomtype].append(aody2)
                    aodict[atomtype].append(aodz2)
                    aodict[atomtype].append(aodxy)
                    aodict[atomtype].append(aodyz)
                    aodict[atomtype].append(aodzx)
                elif orbitalType == "SP":
                    aos = Ao(origin,(0,0,0), contract_num)
                    aodict[atomtype].append(aos)
                    aopx = Ao(origin,(1,0,0), contract_num)
                    aopy = Ao(origin,(0,1,0), contract_num)
                    aopz = Ao(origin,(0,0,1), contract_num)
                    aodict[atomtype].append(aopx)
                    aodict[atomtype].append(aopy)
                    aodict[atomtype].append(aopz)


                linecount += 1
                #print(orbitalType, contract_num)
            elif contract_num and 1 <linecount <= 1 + contract_num:
                if orbitalType == "S" or orbitalType == "P" or orbitalType == "D":
                    exponent, coeff = line.split()
                    
                    exponent = float(exponent.replace("D", "E", 1))
                    coeff = float(coeff.replace("D", "E", 1))
                    if orbitalType == "S":
                        aos.exponents[linecount - 2] = exponent
                        aos.coeffs[linecount - 2] = coeff

                    elif orbitalType == "P":
                        aopx.exponents[linecount - 2] = exponent
                        aopy.exponents[linecount - 2] = exponent
                        aopz.exponents[linecount - 2] = exponent
                        aopx.coeffs[linecount - 2] = coeff
                        aopy.coeffs[linecount - 2] = coeff
                        aopz.coeffs[linecount - 2] = coeff
                    elif orbitalType == "D":
                        aodx2.exponents[linecount - 2] = exponent
                        aody2.exponents[linecount - 2] = exponent
                        aodz2.exponents[linecount - 2] = exponent
                        aodxy.exponents[linecount - 2] = exponent
                        aodyz.exponents[linecount - 2] = exponent
                        aodzx.exponents[linecount - 2] = exponent
                        aodx2.coeffs[linecount - 2] = coeff
                        aody2.coeffs[linecount - 2] = coeff
                        aodz2.coeffs[linecount - 2] = coeff
                        aodxy.coeffs[linecount - 2] = coeff
                        aodyz.coeffs[linecount - 2] = coeff
                        aodzx.coeffs[linecount - 2] = coeff
                    #print(exponent, coeff)
                elif orbitalType == "SP":
                    exponent, coeffs, coeffp = line.split()
                    exponent = float(exponent.replace("D", "E", 1))
                    coeffs = float(coeffs.replace("D", "E", 1))
                    coeffp = float(coeffp.replace("D", "E", 1))
                    aos.exponents[linecount - 2] = exponent
                    aos.coeffs[linecount - 2] = coeffs
                    aopx.exponents[linecount - 2] = exponent
                    aopy.exponents[linecount - 2] = exponent
                    aopz.exponents[linecount - 2] = exponent
                    aopx.coeffs[linecount - 2] = coeffp
                    aopy.coeffs[linecount - 2] = coeffp
                    aopz.coeffs[linecount - 2] = coeffp
                    #print(exponent, coeffs, coeffp)
                if linecount < 1 + int(contract_num):
                    linecount += 1
                else:
                    linecount = 1
                
    #print(aodict)
        
# gaussians, orbitals

class Gprimitive:
    def __init__(self, angular, center, exponent):
        self.angular = angular
        self.center = center
        self.exponent = exponent
    def __call__(self, x):
        return (x - self.center)**self.angular*np.exp(-exponent*(x-self.center)**2) # ?brackets
    def __repr__(self):
        return str(self.center)+str(self.angular)+str(self.exponent)
    
class Ao:
    def __init__(self, center, angular, contract_num):
        self.center = center # the center of the atomic orbital
        self.exponents = [0 for i in range(contract_num)] #list of gaussian primitive exponents
        self.coeffs = [0 for i in range(contract_num)] #list of gaussian primivite coeffs
        self.angular = angular #angular momentum could be S, Px, Py, Pz, Dx2, Dy2, Dz2, Dxy, Dyz, Dzx, ... (0,0,0), (1,
    
    def __repr__(self):
        for key, value in orbital_quantum_dict.items():
            if value == self.angular:

                orbitaltype = key
        return orbitaltype + str(self.center) + str(self.exponents) + str(self.coeffs)
    
    def __call__(self, x, y, z):
        result = 0
        x0, y0, z0 = self.center
        l, m, n = self.angular # angular momenta in three dimensions
        for i in range(len(self.coeffs)):
            exponent = self.exponents[i]
            gprimitivex = Gprimitive(l, x0, exponent)
            gprimitivey = Gprimitive(m, y0, exponent)
            gprimitivez = Gprimitive(n, z0, exponent)
            result += self.coeffs[i]*gprimitivex(x)*gprimitivey(y)*gprimitivez(z)
        return result
    
class Mo(object): #molecular orbital->linear combination of atomic orbitals
    def __init__(self, aolist, coeffs):
        self.aolist = aolist
        self.coeffs = coeffs
        
    def __repr__(self):
        return str(self.coeffs) + repr(self.aolist)
    
    def __call__(self, x, y, z):
        result = 0
        for i in range(len(self.aolist)):
            ao = aolist[i]
            result += self.coeffs[i]*ao(x, y, z)
        return result
    


###############################################################################
#####################################################################integrals, matrices
###############################################################################
# l, m and n are angular momenta in three respective dimensions here...lack of letters thing. its not a n quantum number



def angular_bullswitch(l):
    if l == 0 or l < 0:
        return 1
    else:
        return( (factorial2(2*l-1, exact=True, extend='zero'))**(0.5)   )
    
def Normalization(angular1, angular2, exponent1, exponent2):
    return (((2 * exponent1/np.pi)**0.75 )* ((2 * exponent2/np.pi)**0.75)) * ( ((4*exponent1)**(angular1/2)) / (angular_bullswitch(angular1)) ) * (((4*exponent2)**(angular2/2) )/ (angular_bullswitch(angular2)) )
    #N =1 ###without normalization

def E(l1, l2, t, center1, center2, exponent1, exponent2):#calculate the gaussian-hermite expansion coefficient using recurence
    sumexponent = exponent1 + exponent2
    newcenter = (exponent1 * center1 + exponent2 * center2) / (sumexponent)
    diffcenter = center1 - center2
    redexponent = exponent1 * exponent2 / (sumexponent)
    N = Normalization(l1, l2, exponent1, exponent2)
    #N = 1
    if t > l1 + l2:
        return 0
    if l1 < 0 or l2 < 0 or t < 0:
        return 0
    elif l1 == 0 and l2 == 0 and t == 0:

        return np.exp(-redexponent*diffcenter**2) *(N**(1/3))
    elif l1 > 0:
        return ( (1/(2*sumexponent))*E(l1-1, l2, t - 1,center1,center2,exponent1,exponent2)
                +(newcenter - center1)*E(l1-1,l2,t,center1,center2,exponent1,exponent2)
                +(t + 1)*E(l1-1,l2, t+1, center1,center2,exponent1,exponent2))
    elif l1 == 0:
        return ( (1/(2*sumexponent))*E(l1, l2-1, t - 1,center1,center2,exponent1,exponent2)
                +(newcenter - center2)*E(l1,l2-1,t,center1,center2,exponent1,exponent2)
                +(t + 1)*E(l1,l2-1, t+1, center1,center2,exponent1,exponent2))
    return 0

def S(m1, m2, center1, center2, exponent1, exponent2): #calculate overlap type integral
    
    return np.sqrt((np.pi/(exponent1 + exponent2)))*E(m1, m2, 0, center1, center2, exponent1, exponent2)

def T(m1, m2, center1, center2, exponent1, exponent2): #calculate kinetic type integral
    result = 0
    result += -2*exponent2*S(m1, m2 + 2, center1, center2, exponent1, exponent2)
    result += exponent2*(2*m2+1)*S(m1, m2, center1, center2, exponent1, exponent2)
    result += -1/2*m2*(m2-1)*S(m1, m2 - 2, center1, center2, exponent1, exponent2)
    return result
#
def boys(n, x):
    if x == 0:
        return 1/(2*n+1)
    if 2*x**(n+0.5) < 0.0000001:
        return 1/(2*n+1)
    else:
        return special.gammainc(n+0.5, x) * special.gamma(n+0.5) * (1/(2*x**(n+0.5)))
#one of these two are depracated   
def F(n, x): #calculate Boys function value by numerical integration
    if x < 1e-3:

        return 1/(2*n + 1)
    if n == 50:   #
        res1 = 1/(2*n + 1)
        #if x < 1e-7:
        #    return res1
        for k in range(1,11):
            res1 += (-x)**k/factorial(k)/(2*n+2*k+1)
        res2 = factorial2(2*n-1)/2**(n+1)*np.sqrt(np.pi/x**(2*n+1))
        result = min(res1, res2)
        return result
    return (2*x*F(n+1,x)+np.exp(-x))/(2*n+1)

def R(t, u, v, n, p, x, y, z):
    if t < 0 or u < 0 or v < 0:
        return 0
    if t == 0 and u == 0 and v == 0:
        return (-2*p)**n*boys(n,p*(x**2+y**2+z**2)) #HERE use boys or F...
    if t > 0:
        return (t-1)*R(t-2,u,v,n+1,p,x,y,z)+x*R(t-1,u,v,n+1,p,x,y,z)
    if u > 0:
        return (u-1)*R(t,u-2,v,n+1,p,x,y,z)+y*R(t,u-1,v,n+1,p,x,y,z)
    if v > 0:
        return (v-1)*R(t,u,v-2,n+1,p,x,y,z)+z*R(t,u,v-1,n+1,p,x,y,z)
    


# l, m and n are angular momenta in three respective dimensions here...lack of letters thing. its not a n quantum number
def overlap(ao1, ao2): #calculate overlap matrix <psi|phi>
    #print(ao1)
    l1, m1, n1 = ao1.angular
    l2, m2, n2 = ao2.angular
    x1, y1, z1 = ao1.center
    x2, y2, z2 = ao2.center
    result = 0
    
    for i in range(len(ao1.coeffs)):
        for j in range(len(ao2.coeffs)):
            exponent1 = ao1.exponents[i]
            exponent2 = ao2.exponents[j]
            
            result += (ao1.coeffs[i]*ao2.coeffs[j]*
                    S(l1, l2, x1, x2, exponent1, exponent2)*
                    S(m1, m2, y1, y2, exponent1, exponent2)*
                    S(n1, n2, z1, z2, exponent1, exponent2))
    return result

def kinetic(ao1, ao2): #calculate kinetic integral <psi|-1/2*del^2|phi>
    l1, m1, n1 = ao1.angular
    l2, m2, n2 = ao2.angular
    x1, y1, z1 = ao1.center
    x2, y2, z2 = ao2.center
    result = 0
    for i in range(len(ao1.coeffs)):
        for j in range(len(ao2.coeffs)):
            exponent1 = ao1.exponents[i]
            exponent2 = ao2.exponents[j]

            #correctionforhavingonly1dimension = np.pi/(exponent1+exponent2)

            #N = Normalization(l1, l2, exponent1, exponent2)

            result += 0.5*ao1.coeffs[i]* ao2.coeffs[j]*( (exponent2*(4*(l2 + m2 + n2)+6))*S(l1, l2, x1, x2, exponent1,exponent2 )*S(m1, m2, y1, y2, exponent1,exponent2 )*S(n1, n2, z1, z2, exponent1,exponent2 )
            -4 * ((exponent2**2)* ( S(l1, l2+2, x1, x2, exponent1,exponent2 )*S(m1, m2, y1, y2, exponent1,exponent2 )* S(n1, n2, z1, z2, exponent1,exponent2 )+ S(m1, m2+2, y1, y2, exponent1,exponent2 )*S(l1, l2, x1, x2, exponent1,exponent2 )*S(n1, n2, z1, z2, exponent1,exponent2 ) +S(n1, n2+2, z1, z2, exponent1,exponent2 )*S(l1, l2, x1, x2, exponent1,exponent2 )*S(m1, m2, y1, y2, exponent1,exponent2 ) )) 
            -l2*(l2-1) * S(l1, l2-2, x1, x2, exponent1,exponent2)-m2*(m2-1) * S(m1, m2-2, y1, y2, exponent1,exponent2) -n2*(n2-1) * S(n1, n2-2, z1, z2, exponent1, exponent2)
            )
            
            """result += (ao1.coeffs[i]*ao2.coeffs[j]*
                    (T(l1,l2,x1,x2,exponent1,exponent2)*S(m1,m2,y1,y2,exponent1,exponent2)*S(n1,n2,z1,z2,exponent1,exponent2) +
                     S(l1,l2,x1,x2,exponent1,exponent2)*T(m1,m2,y1,y2,exponent1,exponent2)*S(n1,n2,z1,z2,exponent1,exponent2) +
                     S(l1,l2,x1,x2,exponent1,exponent2)*S(m1,m2,y1,y2,exponent1,exponent2)*T(n1,n2,z1,z2,exponent1,exponent2))
                   )"""
            #print("KINETIC", result)
    return result


def oneelectron(ao1, centerC, ao2):
    l1, m1, n1 = ao1.angular
    l2, m2, n2 = ao2.angular
    a = l1 + m1 + n1
    b = l2 + m2 + n2
    c = a + b
    x1, y1, z1 = ao1.center
    x2, y2, z2 = ao2.center
    xc, yc, zc = centerC # coordinate of atom with charge Z
    result = 0
    for i in range(len(ao1.coeffs)):
        for j in range(len(ao2.coeffs)):
            exponent1 = ao1.exponents[i]
            exponent2 = ao2.exponents[j]
            p = exponent1 + exponent2
            xp = (exponent1*x1+exponent2*x2)/p
            yp = (exponent1*y1+exponent2*y2)/p
            zp = (exponent1*z1+exponent2*z2)/p
            xpc = xp - xc
            ypc = yp - yc
            zpc = zp - zc
            for t in range(c+1):
                for u in range(c+1):
                    for v in range(c+1):
                        result += (ao1.coeffs[i]*ao2.coeffs[j]*
                                2*np.pi/p*E(l1,l2,t,x1,x2,exponent1,exponent2)*
                                E(m1,m2,u,y1,y2,exponent1,exponent2)*
                                E(n1,n2,v,z1,z2,exponent1,exponent2)*
                                R(t,u,v,0,p,xpc,ypc,zpc))
    return result

def twoelectron(ao1, ao2, ao3, ao4):
    res = 0
    l1, m1, n1 = ao1.angular
    l2, m2, n2 = ao2.angular
    l3, m3, n3 = ao3.angular
    l4, m4, n4 = ao4.angular
    x1, y1, z1 = ao1.center
    x2, y2, z2 = ao2.center
    x3, y3, z3 = ao3.center
    x4, y4, z4 = ao4.center
    a = l1 + m1 + n1
    b = l2 + m2 + n2
    c = l3 + m3 + n3
    d = l4 + m4 + n4
    for i in range(len(ao1.coeffs)):
        for j in range(len(ao2.coeffs)):
            for k in range(len(ao3.coeffs)):
                for l in range(len(ao4.coeffs)):
                    exponent1 = ao1.exponents[i]
                    exponent2 = ao2.exponents[j]
                    exponent3 = ao3.exponents[k]
                    exponent4 = ao4.exponents[l]
                    p = (exponent1 + exponent2)
                    q = (exponent3 + exponent4)
                    alpha = p*q/(p + q)
                    xp = (x1*exponent1+x2*exponent2)/p
                    yp = (y1*exponent1+y2*exponent2)/p
                    zp = (z1*exponent1+z2*exponent2)/p
                    xq = (x3*exponent3+x4*exponent4)/q
                    yq = (y3*exponent3+y4*exponent4)/q
                    zq = (z3*exponent3+z4*exponent4)/q
                    xpq = xp - xq
                    ypq = yp - yq
                    zpq = zp - zq
                    for t in range(a + b + 1):
                        for u in range(a + b + 1):
                            for v in range(a + b + 1):
                                for tau in range(c + d + 1):
                                    for miu in range(c + d + 1):
                                        for phi in range(c + d + 1):
                                            res += (ao1.coeffs[i]*ao2.coeffs[j]*ao3.coeffs[k]*ao4.coeffs[l]*
                                                    2*np.pi**(5/2)/p/q/np.sqrt(p+q)*
                                                    E(l1, l2, t, x1, x2, exponent1, exponent2)*
                                                    E(m1, m2, u, y1, y2, exponent1, exponent2)*
                                                    E(n1, n2, v, z1, z2, exponent1, exponent2)*
                                                    E(l3, l4, tau, x3, x4, exponent3, exponent4)*
                                                    E(m3, m4, miu, y3, y4, exponent3, exponent4)*
                                                    E(n3, n4, phi, z3, z4, exponent3, exponent4)*
                                                    (-1)**(tau + miu + phi)*
                                                    R(t+tau, u+miu, v+phi, 0, alpha, xpq, ypq, zpq)
                                                    )
    
    return res



def coulombicAttraction(ao1, atomlist, ao2):
    res = 0
    for i in range(len(atomlist)):
        atomtype, centerC = atomlist[i]
        Z = atomic_charge_dict[atomtype]
        res += (-Z)*oneelectron(ao1, centerC, ao2)
    return res





basis_reader(basis_name)
xyz_reader(file_name)

###############################################
###############################################
###############################################
#matrices

total_charge = 0
for atom in atomlist:
    a = atom[0]
    total_charge += atomic_charge_dict[a]
print("total charge is", total_charge)


n = len(aolist)

Tmatrix = np.zeros((n,n))
Smatrix = np.zeros((n,n))

for i in range(n):
    for j in range(n):
        #print("AAA, one, two", aolist[i].center, aolist[j].center)
        Smatrix[i][j] = overlap(aolist[i], aolist[j])
        Tmatrix[i][j] = kinetic(aolist[i], aolist[j])


coulombAttractionMatrix = np.zeros((n,n))
for i in range(n):
    for j in range(n):
        coulombAttractionMatrix[i][j] = coulombicAttraction(aolist[i], atomlist, aolist[j])


#print(coulombAttractionMatrix)
import time, sys
from IPython.display import clear_output
def update_progress(progress):
    bar_length = 20
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
    if progress < 0:
        progress = 0
    if progress >= 1:
        progress = 1
    block = int(round(bar_length * progress))
    clear_output(wait = True)
    text = "Progress: [{0}] {1:.1f}%".format( "#" * block + "-" * (bar_length - block), progress * 100)
    print(text)

def nuclear_nuclear_rep(atom_coordinates, atomlist):
    natoms = len(atomlist)
    print(atomlist)
    V_nn = 0
    for a in range(natoms):
        atom1 = atomlist[a][0]
        za = atomic_charge_dict[atom1]
        for b in range(natoms):
            if b> a:
                atom2 = atomlist[b][0]
                zb = atomic_charge_dict[atom2]
                Rabx = atom_coordinates[a][0]-atom_coordinates[b][0]
                Raby = atom_coordinates[a][1]-atom_coordinates[b][1]
                Rabz = atom_coordinates[a][2]-atom_coordinates[b][2]
                Rab = (Rabx*Rabx + Raby*Raby + Rabz*Rabz)**(0.5)
                V_nn += za*zb/Rab
    return V_nn

def Cguesser(n):
    C = np.eye(n) #coeffcient matrix
    
    for basis in range(n):
        for basis2 in range(n):
            C[basis][basis2] = 1/n
    return C

coulombRepulsionTensor = np.zeros((n,n,n,n))
count = 0
for i in range(n):
    for j in range(n):
        for k in range(n):
            for l in range(n):
                #print(i, j, k, l)
                if coulombRepulsionTensor[k][k][i][i] != 0 and coulombRepulsionTensor[l][l][j][j] != 0 and (abs(coulombRepulsionTensor[k][k][i][i]))**(0.5) * (abs(coulombRepulsionTensor[l][l][j][j]))*(0.5) < 0.0000001:
                    coulombRepulsionTensor[i][j][k][l] = 0.000000001
                    print("simplifying due to schwarz inequalities")
                elif coulombRepulsionTensor[l][l][i][i] != 0 and coulombRepulsionTensor[k][k][j][j] != 0 and (abs(coulombRepulsionTensor[l][l][i][i]))**(0.5) * (abs(coulombRepulsionTensor[k][k][j][j]))**(0.5) < 0.0000001:
                    coulombRepulsionTensor[i][j][k][l] = 0.000000001
                    print("simplifying due to schwarz inequalities")
                elif coulombRepulsionTensor[i][j][i][j] != 0 and coulombRepulsionTensor[k][l][k][l] != 0 and (abs(coulombRepulsionTensor[i][j][i][j]))**(0.5) * (abs(coulombRepulsionTensor[k][l][k][l]))**(0.5) < 0.0000001:
                    coulombRepulsionTensor[i][j][k][l] = 0.000000001
                    print("simplifying due to schwarz inequalities")
                    
                else: #reusing 8 fold symmetry is much faster
                    if coulombRepulsionTensor[j][i][k][l] != 0: #not computed yet
                        coulombRepulsionTensor[i][j][k][l] = coulombRepulsionTensor[j][i][k][l]
                        print("reusing symmetry")
                    elif coulombRepulsionTensor[i][j][l][k] != 0:
                        coulombRepulsionTensor[i][j][k][l] = coulombRepulsionTensor[i][j][l][k]
                        print("reusing symmetry")
                    elif coulombRepulsionTensor[j][i][l][k] != 0:
                        coulombRepulsionTensor[i][j][k][l] = coulombRepulsionTensor[j][i][l][k]
                        print("reusing symmetry")
                    elif coulombRepulsionTensor[k][l][j][i] != 0:
                        coulombRepulsionTensor[i][j][k][l] = coulombRepulsionTensor[k][l][j][i]
                        print("reusing symmetry")
                    elif coulombRepulsionTensor[l][k][j][i] != 0:
                        coulombRepulsionTensor[i][j][k][l] = coulombRepulsionTensor[l][k][j][i]
                        print("reusing symmetry")
                    elif coulombRepulsionTensor[l][k][i][j] != 0:
                        coulombRepulsionTensor[i][j][k][l] = coulombRepulsionTensor[l][k][i][j]
                        print("reusing symmetry")
                    elif coulombRepulsionTensor[k][l][i][j] != 0:
                        coulombRepulsionTensor[i][j][k][l] = coulombRepulsionTensor[k][l][i][j]
                        print("reusing symmetry")

                    else:
                    
                
                        coulombRepulsionTensor[i][j][k][l] = twoelectron(aolist[i],aolist[j],aolist[k],aolist[l])
                        print("this integral is significant. Overlap1 ij, Overlap kl, [ij|kl]", Smatrix[i][j], Smatrix[k][l], coulombRepulsionTensor[i][j][k][l])
                count += 1
                update_progress(count / n**4)
                #print(Smatrix[i][j], Smatrix[k][l], coulombRepulsionTensor[i][j][k][l])
                
update_progress(1)
print("Coulombrepulsion", coulombRepulsionTensor)
print("Smatrix", Smatrix)
print("Tmatrix", Tmatrix)
print("coulombAttractionMatrix", coulombAttractionMatrix)

V_nn = nuclear_nuclear_rep(atom_coords, atomlist)
#print(V_nn)
norb = int(total_charge/2)
maxiter = 100

C = Cguesser(n)
#C = np.zeros((n, n))

print("C", C)
prev = float('inf')
tol = 1e-7
step = 0
for i in range(maxiter):
    step += 1
    print("SCF STEP", step)
    #start building Fock matrix
    JK = np.zeros((n,n))
    F = np.zeros((n,n)) 
    for j in range(n):
        for k in range(n):
            for l in range(n):
                for m in range(n):
                    #for o in range(norb):
                        JK[j][k] += (C[l][m]*
                                    (coulombRepulsionTensor[j][k][l][m]-
                                     0.5*coulombRepulsionTensor[j][m][l][k]
                                    ))
                        
    F = Tmatrix + coulombAttractionMatrix + JK #add kinetic integral and coulomb attraction integeral
    S = Smatrix #overlap matrix

    S_inverse = linalg.inv(S)
    S_inverse_sqrt = linalg.sqrtm(S_inverse)
    F_unitS = np.dot(S_inverse_sqrt, np.dot(F, S_inverse_sqrt))
    
    energy, C = eigh(F_unitS)
    mos = np.dot(S_inverse_sqrt, C)
    #print("mos, energy", mos, energy)
    nbasis_functions = mos.shape[0]
    density_matrix = np.zeros((nbasis_functions, nbasis_functions))
    occupation = 2.0 
    for i in range(nbasis_functions):
        for j in range(nbasis_functions):
            for oo in range(norb):
                C = mos[i, oo]
                Cdagger = mos[j, oo]
                density_matrix[i, j] += occupation * C * Cdagger
    C = density_matrix
    #print("Updated density matrix", C)

    nbasis_functions = density_matrix.shape[0]
    H_core = Tmatrix + coulombAttractionMatrix
    electronic_energy = 0 
    for k in range(nbasis_functions):
        for l in range(nbasis_functions):
            electronic_energy += C[k, l] * (H_core[k, l] + 0.5* JK[k, l])
    print("Electronic energy", electronic_energy)

    if abs(electronic_energy - prev) < tol:
        print('SCF Converged')
        break
    delta = electronic_energy - prev
    prev = electronic_energy
    print('EHF:'+str(electronic_energy)+" "+'prev:'+str(prev)+' '+'delta:'+str(delta))
print("Nuclear rep", V_nn)
print("Total",electronic_energy + V_nn)
print()



#print("SMATRIX", Smatrix)
#print("aolist", aolist)
#print("aodict", aodict)



