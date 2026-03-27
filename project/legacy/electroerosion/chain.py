import matplotlib.pyplot

# from mpl_toolkits.mplot3d import Axes3D

from ikpy.chain import Chain
from ikpy.utils.geometry import from_transformation_matrix
from ikpy.link import OriginLink, URDFLink
from ikpy.urdf.URDF import get_urdf_parameters


"""my_chain = Chain(name='manipulator', 
    # active_links_mask=[0,1,1], 
    # active_links_mask=[0,1,1,1], 
    # active_links_mask=[0,1,1,1,1], 
    active_links_mask=[0,1,1,1,1,1,1,0], 
    links=[
        OriginLink(),
        URDFLink(
            name="j1",
            origin_translation=[0, 16, 171],
            origin_orientation=[0, 0, 0],
            rotation=[0, 0, 1],
        ),
        URDFLink(
            name="j2",
            origin_translation=[0, 55-16, 368-171],
            origin_orientation=[0, 0, 0],
            rotation=[1, 0, 0],
        ),
        URDFLink(
            name="j3",
            origin_translation=[0, 55-55, 610-368],
            origin_orientation=[0, 0, 0],
            rotation=[1, 0, 0],
        ),
        URDFLink(
            name="j4",
            origin_translation=[0, 137-55, 654-610],
            origin_orientation=[0, 0, 0],
            rotation=[0, 1, 0],
        ),
        URDFLink(
            name="j5",
            origin_translation=[0, 344-137, 648-654],
            origin_orientation=[0, 0, 0],
            rotation=[1, 0, 0],
        ),
        URDFLink(
            name="j6",
            origin_translation=[0, 339-344, 519-648],
            origin_orientation=[0, 0, 0],
            rotation=[0, 0, -1],
        ),
        # URDFLink(
        #     name="pen",
        #     origin_translation=[0, 0, -150],
        #     origin_orientation=[0, 0, 0],
        #     rotation=[0, 0, 1],
        # ),
        URDFLink(
            name="erosion",
            origin_translation=[0, 430-339, 277-519],
            origin_orientation=[0, 0, 0],
            joint_type='fixed',
        ),
    ]
)"""

my_chain = Chain.from_urdf_file("robot_6_axis.urdf", active_links_mask=[0,1,1,1,1,1,1,0])
#urdf_param = get_urdf_parameters("robot_6_axis.urdf", ["base_link, base_J1"])




if __name__ == '__main__':
    import numpy as np

    ax = matplotlib.pyplot.figure().add_subplot(111, projection='3d')

    pk = my_chain.forward_kinematics([0,0,0,0,0,0,0,0])
    print(pk)
    print(from_transformation_matrix(pk))

    ik = my_chain.inverse_kinematics([0,430,237])
    print([ round(np.degrees(x), 2) for x in ik])

    ik = my_chain.inverse_kinematics([0,430,230])
    print([ round(np.degrees(x), 2) for x in ik])

    ik = my_chain.inverse_kinematics([0,430,220])
    print([ round(np.degrees(x), 2) for x in ik])

    ik = my_chain.inverse_kinematics([0,430,210])
    print([ round(np.degrees(x), 2) for x in ik])

    ik = my_chain.inverse_kinematics([0,300,210])
    print([ round(np.degrees(x), 2) for x in ik])
