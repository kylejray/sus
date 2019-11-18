# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.2.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
from protocol_designer.protocol import Protocol, Compound_Protocol, sequential_protocol
from protocol_designer.potentials import Potential,blw,odv, duffing_2D
from protocol_designer.system import System
import numpy as np 

import matplotlib.pyplot as plt
plt.rcParams["animation.html"] = "jshtml"
from IPython.display import HTML

# If we want to actually calculate values of the potential and force, we need to put in some coordinates.

# N sets of coordinates are expected to be in an array with shape (N,D,2)
# where D is the dimensionality of our system, the 2 coordiantes determine position/velocity coordinates
N=20
coords_2D=np.random.random_sample((N,2,2))
coords_1D=np.random.random_sample((N,1,2))
coords_5D=np.random.random_sample((10,5,2))
#these will be used later
# -

# # Protocols

# +
#Let's jump in by importing some example protocols, we can talk about making them (and potentials) later.

# example_substages defines 4 simple substages (intances of the protocol class)
# to be used for testing purposes. It is a 12 parameter protocol,

import example_substages as ESS

erase_prot=ESS.CP

tilt=ESS.tilt
untilt=ESS.untilt
lower=ESS.lower
unlower=ESS.unlower

#all that protocols do is store some number of parameters as a function of time. they are very simple objects.
# -

# we can look at the signal a compound protocol generates over time:
erase_prot.show_params()

# by default it only shows the nontrivial parameters (the ones that are not constant)
# we can show all by using
erase_prot.show_params(which='all')

# this protocol has 12 parameters, but most of them are trivial
# you could also show any subset of parameters by specifying an explicit "which":
erase_prot.show_params(which=(1,2,7,9))

# +
#A compound protocol can give you the substage times

#if you want an array of the times:
protocol_times=erase_prot.times
print(protocol_times)


# if you want just the initial and final time of the whole protocol:
print('initial time:',erase_prot.t_i)
print('final time:',erase_prot.t_f)
# -

#if you just want a printout that tells you what each time corresponds to:
erase_prot.show_substage_times()

# +
#For a simple protocol, there are no substages:

#if we look at the protocol that is just one of the substages (called 'tilt') we can still use
#Protocol.t_i and Protocol.t_f to give initial and final times of the protocol:
print('inial time is:',tilt.t_i)
print('final time is:',tilt.t_f)
# -

# # Applying Protocols to Potentials using a System

# +
# The most important class here is the System class. It interpolates between whatever protocol/potential you create
# and gregs simulation architecture. also contains visualization methods

#Now we create the system that the protocol will apply to
#Systems take a protocol as an input, as well as a potential.

#ODV is a predefined potential, so lets just plop it in:
erase_sys=System(erase_prot,odv)

# -

# ### Oh no! An error. 
# ###### This is actually to be expected because the potential we put in needs 2 parameters to be defined but the protocol actually defined 12 different things. Thus, the assert error we get

# +
#When you define a system it will check if the protocol is compatilbe with the potential.

#you can check information on a potential object:
odv.info()

# -

#BLW is a predefined 2D potential (happens to be a 4 well system).
# it takes 12 parameters, and our erase protocol is a 12 parameter protocol,
# so this will work with the erasing protocol. technically any 12 parameter potential would be compatible though.
blw.info()

# +
#initialize our full system:

erase_sys=System(erase_prot,blw)
# -



# +
# Visualization tools
    
#animate the potential over time
#this is mostly a sanity check at this point to make sure it looks how you think.



# You can animate the protocol
ani=erase_sys.animate_protocol(mesh=40,surface=False);

#There is a workaround below make the animatio show in jupyter notebook,
#Normally you could just do plt.show() to show the animation. 
HTML(ani.to_jshtml(fps=5))

#you can save the animation by passing save=True into the argument of the .animate_lattice
#or just use ani.save etc... like a normal matplotlib animation object (this is probably preferable)

#animating the protocol is a bit slow, but I haven't worked on optimizing it at all because 
#it shouldnt affect simulation time. Its a diagnostic tool.
# -

#to see just a certain point in time use show_potential, surface determines if we see a wireframe or a contour plot.
erase_sys.show_potential(.6,surface=False)

# +
# you can pull out forces, the potential, or the energy given a set of coordiantes and a time 
potentials=erase_sys.get_potential(coords_2D,.7)
print('potentials for trials 11-15:',potentials[10:15])


# the output for forces is in the form (N,D): N sets of D forces
forces=erase_sys.get_external_force(coords_2D,.5)
print('forces for trial 4:{}'.format(forces[3]))
print('forces in the "y" direction for all trials 1-4:',forces[0:4,1])
# -

# # Creating new potentials and protocols

# ##### Lets say we want to make a new kind of potential, say a 2 dimensional potential that is an exponential well at (x,y)=0
#
# $$ V= - e^{-\frac{ax^2+by^2}{T}} $$
#
# ##### We have 3 parameters to deal with. All we need to do is make a function to give us the potential and the force

# +
from numpy import exp as exp

def exp_well_pot(x, y, params):
    a, b, T = params
    return(-exp(-(a*x**2+b*y**2)/T))
def exp_well_force(x, y, params):
    a, b, T = params
    dx= 2*a*x*exp(-(a*x**2+b*y**2)/T)/T
    dy= 2*a*y*exp(-(a*x**2+b*y**2)/T)/T
    return(-dx,-dy)
   


# +
# definine a new potential class takes a potential function and a force function as inputs.
# also you need to put in the number of parameters (3 here) and the number of dimensions (2 here)
exp_well=Potential(exp_well_pot,exp_well_force,3,2)  
# we can go ahead and look at it now by sending it through a System using Potential.trivial_protocol
# this just sets all parameters to 1 and the time window from 0 to 1

# the default parameters can be redefined when you instance a Potential class 
# by passing a list of the default parameters
# such as exp_well=Potential(exp_well_pot, exp_well_force, 3, 2, default_params=(3,8,.1))

trivial_system=System(exp_well.trivial_protocol(),exp_well)
# -

trivial_system.show_potential(.5,x_min=-1,x_max=1,y_min=-1,y_max=1)

# +
# Generally,  we want make our protocol that will operate on the potential. 
# This protocol will go from t=0 to t=.6
t=(0,.6)
#we'll a totally symmetric well (a=1,b=1,T=1) and end with a deformed well at the same T (a=.5,b=2,T=1) 
params=((1,.2),(1,3),(1,1))

#now, we make a protocol. WSP is short for well_stetch_protocol
WSP=Protocol(t,params)
# -

#Finally, we apply the well stretch protocol to the exp_well potential
well_stretch=System(WSP,exp_well)


# +
#and just to make sure it worked as expected, lets plot it:

well_stretch.show_potential(0)

#you can specify the window, if you want. The default is (0,1) though this might change to be an adaptive default
well_stretch.show_potential(.5,x_min=-1,x_max=1,y_min=-1,y_max=1)

# -

# # Editing Protocols

# +
#lets say we want to make a compound protocol that stretches the well and then unstretches it
#here we can call the reverse method of protocols, which reverses all parameters.

# it is functionally equivalent to  redefining the input params from ((a,b),(c,d),(e,f)) to ((b,a),(d,c),(f,e))

#first make a copy of the original protocol
WSP_rev=WSP.copy()
#then call the reverse method to reverse the parameters for the copy
WSP_rev.reverse()


# -

#note that the times will conflict if we try to concatenate onto the
#original protocol because they both operate between t=0 and t=.6
#we should get an error message if we try
SAR_prot=Compound_Protocol((WSP,WSP_rev))

# +
#so we need to time shift the second one to start at some point after t=.6
#use Protocol.time_shift for this:

print("WSP_rev initial time is:",WSP_rev.t_i,"WSP_rev final time is:",WSP_rev.t_f)

WSP_rev.time_shift(WSP.t_f)

print("WSP_rev initial time is:",WSP_rev.t_i,"WSP_rev final time is:",WSP_rev.t_f)
# -

#If we do this several times in a row, it will keep shifting the protocol times. 
print("WSP_rev initial time is:",WSP_rev.t_i,"WSP_rev final time is:",WSP_rev.t_f)
WSP_rev.time_shift(WSP.t_f)
print("initial time is:",WSP_rev.t_i,"final time is:",WSP_rev.t_f)

# +
#Lets make a compound protocol, to see what happens in this case. Note that we don't need to time order the substages,
#the class initialization will do that for us

SAR_prot=Compound_Protocol((WSP_rev,WSP))
SAR_prot.show_substage_times()

#its okay that there is some dead space between the protocol steps, the protocol assumes that to mean that we keep
#the parameters constant in the meantime.
# -

#now we can apply the compound protocol made of stretch and unstretch:
stretch_and_rev=System(SAR_prot,exp_well)

# +

# now we can see the whole protocol:
ani=stretch_and_rev.animate_protocol(surface=False,x_min=-1,x_max=1,y_min=-1,y_max=1)
HTML(ani.to_jshtml(fps=10))
#note that parameters are held fixed between the explicit substages to fill in the gaps

# +
# we can also edit protocols that we have already made with the Protocol.change_param method
# lets say we want the first parameter in our reverse process to actually go from .2 to 3 instead of back to 1

print(WSP_rev.params)
#we now call the change_param method, which takes in which parameters you want to change 
#and new initial and final values
WSP_rev.change_param(1,(.2,3))

print(WSP_rev.params)

# -

#now on top of this, what if we want to make the second stage of the protocol take longer
# we can use Protocol.time_stretch for that
print(WSP_rev.t_i,WSP_rev.t_f)
WSP_rev.time_stretch(3)
print(WSP_rev.t_i,WSP_rev.t_f)


# +
new_sys=System(Compound_Protocol((WSP,WSP_rev)), exp_well)

ani=new_sys.animate_protocol(surface=False,x_min=-1,x_max=1,y_min=-1,y_max=1)
HTML(ani.to_jshtml(fps=10))


# -

# # Higher Dimensional Potentials
#
# ###### while the package can handle higher dimensional potentials fine, I havent worked on the visualization part of them yet.
# ##### heres an example anyway...
# ##### 5 dimensional spherical containment with a hard edge :
#
# $$ V= 0 \quad\text{for} \quad \sqrt{x_i x^i} > r $$
# $$ V=V_0  \quad\text{for}\quad \sqrt{x_i x^i} < r$$
#
#
# ###### this wont be very useful for simulation because the force is zero everywhere, but its just for illustrative purposes anyway
#

# +
def five_d_sphere(x1, x2, x3, x4, x5, params):
    r,V0=params
    pos=x1,x2,x3,x4,x5
    distance=np.sqrt(np.sum(np.square(pos), axis=0))
    
    return  V0*(1-np.sign(distance-r))/2
    #return distance

def five_d_sphere_f(x1, x2, x3, x4, x5, params):
    r,V0 = params
    pos = x1,x2,x3,x4,x5
    
    return(0,0)

#note that the way it is set up makes really high dimensional potentials kind of annoying to write. 
#this can be changed if there is reason to.

fds=Potential(five_d_sphere,five_d_sphere_f,2,5)
fds_t=(0,1)
fds_p=((.5,1.8),(-1,0))
fds_sys=System(Protocol(fds_t,fds_p),fds)

# +
#when you call show_potential, we now take a 2-d slice of the potential, 
# sets all other coordinates to zero by default, and automatically chooses the first 2 coordinates

#below is a slice that shows what happens at 0=x2=x4=x5, and varying x1 and x3
# -

fds_sys.show_potential(.5,surface=True,x_min=-2,x_max=2,y_min=-2,y_max=2,axis1=1,axis2=3)

#we can also set the slice values
slice_val=(0,.6,0,.6,.2)
#here it will set x3=0, x4=.6, and x5=.2 while varying x1 and x2 (defaul axes)
fds_sys.show_potential(.5,surface=True,x_min=-2,x_max=2,y_min=-2,y_max=2,slice_values=slice_val)

# again, we can animate. default axis and slice is the same as show_potential
# mesh control the numbe of points we calcualte the potential at
ani = fds_sys.animate_protocol(surface=True, mesh=100, x_min=-2,x_max=2,y_min=-2,y_max=2, axis1=2, axis2=3)
HTML(ani.to_jshtml(fps=10))

# # Bonus practice
#
# #### ODV is also a build in potential for testing purposes, go ahead and try to apply a protocol to it to see if your familiar enough with the package

odv.info()

# +
#make a protocol

# +
#make a system
# -

# # Working With built-in potentials

#lets say we want to implement a simple kind of protocol where there are no discontinuities in parameters value
# we can use the function sequential_protocol for this.
from protocol_designer.protocol import sequential_protocol

# +
# as an example, lets apply Alec's version of the Szilard Engine. This operates on the Duffing_2D potential
from protocol_designer.potentials import duffing_2D

#out of the 7 possible parameters in this potential, 3 of them are held fixed at the default value for
#the potential (can be accessed with Potential.default_parameter, if its not defined the default will set all
# parameters to 0)
duffing_2D.default_params

# +
# in this version of szilards engine, we keep everything fixed except for the 3rd,4th,6th, and 7th parameters.
# it is a 12 step protocol, so there are 13 places we need to define the changin parameters

p3 = (-1, -1, -1, -1, -1, 0, 0, -1, -1, -1, -1, -1, -1)
p4 = (-1, 0, 0, -1, -1, -1, -1, -1, -1, 0, 0, -1, -1)
p6 = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0)
p7 = (0, 0, -1, -1, 0, -1, -1, 0, 0, 0, 0, 0, 0)

# we prepare a list of the which parameters will change, and also their values at each substage time
which=(3,4,6,7)
non_triv_param=(p3,p4,p6,p7)
# there are 12 steps
NS=12
#and 7 parameters
NP=7
# -

#then we create the Compound Protocol (note that default_params is optional, and defaults will be 0 without it)
szilard_prot_1 = sequential_protocol(NS, NP, which, non_triv_param, initial_params=duffing_2D.default_params )

szil_sys=System(szilard_prot_1, duffing_2D)
L=2
ani=szil_sys.animate_protocol(frames=50, surface=False,x_min=-L,x_max=L,y_min=-L,y_max=L)
HTML(ani.to_jshtml(fps=5))

# note that the function automatically makes NS substages of equal length between t=0 and t=1
# if you want to customize the times, then you can pass a list of length NS+1 to define
# the substage times:
t_list=(0,.5,.75,1,1.5,2,2.2,2.8,3,4,5,6,6.3)
szilard_prot_2 = sequential_protocol(NS, NP, which, non_triv_param, times=t_list, initial_params=duffing_2D.default_params)

szilard_prot_2.show_substage_times()


